"""
BRN Reroll Analyzer - Motor de Análise
Orquestra todo o ciclo de automação: clique → captura → OCR → análise → decisão.
"""

import time
import keyboard
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QThread

from core.clicker import Clicker
from core.screen_capture import ScreenCapture
from core.ocr_reader import OCRReader
from core.config_manager import ConfigManager


class AnalyzerWorker(QObject):
    """
    Worker que executa o loop de automação em uma thread separada.
    Emite sinais para atualizar a interface sem bloquear a UI.
    """

    # Sinais para comunicação com a interface
    status_changed = pyqtSignal(str)       # Status: "Rodando", "Parado", etc.
    magic_find_detected = pyqtSignal(float) # Valor de Magic Find detectado
    best_value_updated = pyqtSignal(float)  # Melhor valor encontrado
    reroll_count_updated = pyqtSignal(int)  # Total de rerolls
    log_message = pyqtSignal(str)           # Mensagem de log
    target_reached = pyqtSignal(float)      # Meta atingida! (valor)
    preview_updated = pyqtSignal(object)    # Imagem preview (numpy array)
    ocr_text_updated = pyqtSignal(str)      # Texto OCR bruto
    confidence_updated = pyqtSignal(float)  # Confiança do OCR
    elapsed_time_updated = pyqtSignal(str)  # Tempo decorrido formatado
    error_occurred = pyqtSignal(str)        # Erro ocorrido
    finished = pyqtSignal()                 # Execução finalizada

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self.clicker = Clicker()
        self.screen = ScreenCapture()
        self.ocr = OCRReader(self.config.get_tesseract_path())
        
        self._running = False
        self._paused = False
        self.best_value = 0.0
        self.start_time = None

    def run(self):
        """
        Loop principal de automação.
        
        Fluxo correto para ARK:
        1. Clicar no botão Reroll
        2. Aguardar o reroll processar
        3. Mover mouse para cima do item (tooltip aparece)
        4. Aguardar tooltip renderizar
        5. Capturar a região da tela
        6. Processar com OCR
        7. Verificar Magic Find
        """
        self._running = True
        self._paused = False
        self.best_value = 0.0
        self.clicker.reset_count()
        self.start_time = time.time()

        # Configurações
        reroll_x, reroll_y = self.config.get_reroll_position()
        item_x, item_y = self.config.get_item_hover_position()
        region = self.config.get_capture_region()
        min_mf = self.config.get_min_magic_find()
        delay = self.config.get_click_delay()
        hover_delay = self.config.get_hover_delay()
        mode = self.config.get_mode()

        self.status_changed.emit("🟢 Rodando")
        self.log_message.emit(f"━━━ Automação iniciada ━━━")
        self.log_message.emit(f"📍 Posição Reroll: ({reroll_x}, {reroll_y})")
        self.log_message.emit(f"🖱️ Posição Item (hover): ({item_x}, {item_y})")
        self.log_message.emit(f"📐 Região captura: {region}")
        self.log_message.emit(f"🎯 Meta Magic Find: ≥ {min_mf}%")
        self.log_message.emit(f"⏱️ Delay reroll: {delay}s | Delay hover: {hover_delay}s")
        self.log_message.emit(f"📖 Modo: {mode.upper()}")
        self.log_message.emit(f"🛑 Pressione ESC para parar")
        self.log_message.emit("")

        try:
            while self._running:
                # Verificar tecla de emergência
                if keyboard.is_pressed(self.config.get("emergency_key", "esc")):
                    self.log_message.emit("🛑 Tecla de emergência pressionada!")
                    break

                # Verificar se está pausado
                if self._paused:
                    self.status_changed.emit("⏸️ Pausado")
                    time.sleep(0.5)
                    continue

                # Atualizar tempo decorrido
                self._update_elapsed_time()

                # === PASSO 1: Clicar no botão Reroll ===
                self.log_message.emit(f"🔄 Reroll #{self.clicker.get_click_count() + 1}...")
                success = self.clicker.click_reroll(reroll_x, reroll_y)
                
                if not success:
                    self.log_message.emit("⚠️ Falha no clique - verificando segurança...")
                    break

                self.reroll_count_updated.emit(self.clicker.get_click_count())

                # === PASSO 2: Aguardar o reroll processar ===
                self.clicker.wait(delay)

                # === PASSO 3: Mover mouse para o item (exibir tooltip) ===
                self.log_message.emit(f"   🖱️ Movendo mouse ao item...")
                self.clicker.move_to(item_x, item_y)

                # === PASSO 4: Aguardar tooltip renderizar ===
                time.sleep(hover_delay)

                # === PASSO 5: Capturar tela ===
                image = self.screen.capture_region(region)
                if image is None:
                    self.log_message.emit("   ⚠️ Falha na captura de tela")
                    continue

                # Enviar preview para interface
                preview = self.screen.get_capture_preview(region)
                if preview is not None:
                    self.preview_updated.emit(preview)

                # === PASSO 6: Processar imagem com OCR (Pipeline com Fallbacks) ===
                
                # Tentativa 1: Com filtro de cores e PSM 6 (Bloco uniforme)
                processed = self.screen.preprocess_for_ocr(image, enhance_green=True)
                magic_find, raw_text, confidence = self.ocr.process_image(processed, psm=6)
                
                # Tentativa 2: Fallback Normal e PSM 3 (Automático)
                if magic_find <= 0:
                    self.log_message.emit("   🔍 Tentando leitura secundária (Normal + Automático)...")
                    processed_normal = self.screen.preprocess_for_ocr(image, enhance_green=False)
                    mf_fb, txt_fb, conf_fb = self.ocr.process_image(processed_normal, psm=3)
                    if mf_fb > 0:
                        magic_find, raw_text, confidence = mf_fb, txt_fb, conf_fb
                
                # Tentativa 3: Fallback Invertido e PSM 11 (Texto Esparso)
                if magic_find <= 0:
                    self.log_message.emit("   🔍 Tentando leitura terciária (Invertido + Texto Esparso)...")
                    processed_inv = self.screen.preprocess_for_ocr(image, enhance_green=False, invert=True)
                    mf_inv, txt_inv, conf_inv = self.ocr.process_image(processed_inv, psm=11)
                    if mf_inv > 0:
                        magic_find, raw_text, confidence = mf_inv, txt_inv, conf_inv

                self.ocr_text_updated.emit(raw_text)
                self.confidence_updated.emit(confidence)

                if magic_find > 0:
                    self.magic_find_detected.emit(magic_find)
                    self.log_message.emit(
                        f"   ✨ Magic Find: {magic_find}% "
                        f"(confiança: {confidence:.0f}%)"
                    )

                    # Registrar no histórico
                    self.config.add_history_entry(magic_find)

                    # Atualizar melhor valor
                    if magic_find > self.best_value:
                        self.best_value = magic_find
                        self.best_value_updated.emit(self.best_value)
                        self.log_message.emit(f"   🏆 Novo melhor valor: {self.best_value}%")

                    # === PASSO 8: Verificar se atingiu a meta ===
                    if magic_find >= min_mf:
                        self.log_message.emit("")
                        self.log_message.emit(f"🔥🔥🔥 META ATINGIDA! Magic Find: {magic_find}% 🔥🔥🔥")
                        self.log_message.emit(f"   Total de rerolls: {self.clicker.get_click_count()}")
                        self._update_elapsed_time()
                        self.target_reached.emit(magic_find)
                        break
                else:
                    self.log_message.emit(f"   ❌ Magic Find não detectado nesta tentativa")

        except Exception as e:
            self.error_occurred.emit(str(e))
            self.log_message.emit(f"❌ Erro: {e}")

        finally:
            self._running = False
            self.status_changed.emit("🔴 Parado")
            self.log_message.emit("")
            self.log_message.emit(f"━━━ Automação finalizada ━━━")
            self.log_message.emit(
                f"📊 Resumo: {self.clicker.get_click_count()} rerolls | "
                f"Melhor: {self.best_value}%"
            )
            self.finished.emit()

    def stop(self):
        """Para a automação."""
        self._running = False

    def pause(self):
        """Pausa/retoma a automação."""
        self._paused = not self._paused

    def is_running(self):
        """Retorna se a automação está rodando."""
        return self._running

    def is_paused(self):
        """Retorna se a automação está pausada."""
        return self._paused

    def _update_elapsed_time(self):
        """Atualiza o tempo decorrido."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.elapsed_time_updated.emit(formatted)
