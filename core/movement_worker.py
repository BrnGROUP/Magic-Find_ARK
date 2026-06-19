"""
BRN Reroll Analyzer - Módulo de Automação de Movimentação e Cliques
Simula o pressionamento cíclico de W/S e cliques do mouse em segundo plano.
"""

import time
import pyautogui
import keyboard
from PyQt5.QtCore import QObject, pyqtSignal


class MovementWorker(QObject):
    """
    Worker que executa o loop de movimentação W/S e socos em uma thread separada.
    """

    status_changed = pyqtSignal(str)       # Status: "Rodando", "Parado", etc.
    log_message = pyqtSignal(str)           # Mensagem de log para a UI
    finished = pyqtSignal()                 # Execução finalizada

    def __init__(self, config_manager):
        super().__init__()
        self.config = config_manager
        self._running = False
        self._paused = False

    def run(self):
        """Loop principal de movimentação e socos."""
        self._running = True
        self._paused = False

        # Configurações do gerenciador
        w_duration = self.config.get_movement_w_duration()
        s_duration = self.config.get_movement_s_duration()
        click_interval = self.config.get_movement_click_interval()
        click_enabled = self.config.is_movement_click_enabled()
        emergency_key = self.config.get("emergency_key", "esc")

        self.status_changed.emit("🟢 Rodando")
        self.log_message.emit("━━━ Automação de Movimentação Iniciada ━━━")
        self.log_message.emit(f"🚶‍♂️ Duração Frente (W): {w_duration}s")
        self.log_message.emit(f"🚶‍♂️ Duração Trás (S): {s_duration}s")
        self.log_message.emit(f"🥊 Cliques (Socos): {'Habilitado' if click_enabled else 'Desabilitado'}")
        if click_enabled:
            self.log_message.emit(f"⏱️ Intervalo do clique: {click_interval}s")
        self.log_message.emit(f"🛑 Tecla de emergência: {emergency_key.upper()}")
        self.log_message.emit("")

        # Garantir failsafe do PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.02

        try:
            while self._running:
                # Verificar tecla de emergência
                if keyboard.is_pressed(emergency_key):
                    self.log_message.emit("🛑 Tecla de emergência pressionada!")
                    break

                if self._paused:
                    self.status_changed.emit("⏸️ Pausado")
                    time.sleep(0.2)
                    continue

                self.status_changed.emit("🟢 Rodando")

                # === 1. MOVER PARA FRENTE (W) ===
                self.log_message.emit("🚶‍♂️ Movendo para frente (W)...")
                pyautogui.keyDown('w')
                
                start_w = time.time()
                last_click = 0
                
                while time.time() - start_w < w_duration and self._running:
                    # Verificar tecla de emergência no loop interno
                    if keyboard.is_pressed(emergency_key):
                        self._running = False
                        self.log_message.emit("🛑 Tecla de emergência pressionada!")
                        break

                    # Tratar pausa
                    if self._paused:
                        pyautogui.keyUp('w')
                        while self._paused and self._running:
                            if keyboard.is_pressed(emergency_key):
                                self._running = False
                                break
                            time.sleep(0.2)
                        if not self._running:
                            break
                        # Retomar movimentação W
                        pyautogui.keyDown('w')
                        # Reinicia tempo para completar o ciclo W
                        start_w = time.time()

                    # Executar clique/soco
                    if click_enabled:
                        now = time.time()
                        if now - last_click >= click_interval:
                            pyautogui.click()
                            last_click = now

                    time.sleep(0.05)

                pyautogui.keyUp('w')

                if not self._running:
                    break

                time.sleep(0.1)

                # === 2. MOVER PARA TRÁS (S) ===
                self.log_message.emit("🚶‍♂️ Movendo para trás (S)...")
                pyautogui.keyDown('s')
                
                start_s = time.time()
                last_click = 0
                
                while time.time() - start_s < s_duration and self._running:
                    # Verificar tecla de emergência no loop interno
                    if keyboard.is_pressed(emergency_key):
                        self._running = False
                        self.log_message.emit("🛑 Tecla de emergência pressionada!")
                        break

                    # Tratar pausa
                    if self._paused:
                        pyautogui.keyUp('s')
                        while self._paused and self._running:
                            if keyboard.is_pressed(emergency_key):
                                self._running = False
                                break
                            time.sleep(0.2)
                        if not self._running:
                            break
                        # Retomar movimentação S
                        pyautogui.keyDown('s')
                        start_s = time.time()

                    # Executar clique/soco
                    if click_enabled:
                        now = time.time()
                        if now - last_click >= click_interval:
                            pyautogui.click()
                            last_click = now

                    time.sleep(0.05)

                pyautogui.keyUp('s')

                # Pausa antes de reiniciar o loop
                time.sleep(0.1)

        except pyautogui.FailSafeException:
            self.log_message.emit("⚠️ PyAutoGUI FailSafe ativado! O mouse foi movido para o canto superior esquerdo da tela.")
        except Exception as e:
            self.log_message.emit(f"❌ Erro na automação: {e}")
        finally:
            # GARANTIR QUE AS TECLAS FÍSICAS NÃO FIQUEM PRESAS
            pyautogui.keyUp('w')
            pyautogui.keyUp('s')
            self._running = False
            self.status_changed.emit("🔴 Parado")
            self.log_message.emit("")
            self.log_message.emit("━━━ Automação de Movimentação Finalizada ━━━")
            self.finished.emit()

    def stop(self):
        """Para a execução do loop."""
        self._running = False

    def pause(self):
        """Pausa/retoma a execução."""
        self._paused = not self._paused

    def is_running(self):
        """Retorna se o loop está rodando."""
        return self._running

    def is_paused(self):
        """Retorna se o loop está pausado."""
        return self._paused
