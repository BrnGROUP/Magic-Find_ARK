"""
BRN Reroll Analyzer - Tela de Automação
Controles START/STOP, preview em tempo real, log de execução e texto OCR.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTextEdit, QSplitter, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QFont, QImage, QPixmap, QTextCursor
import cv2
import numpy as np

from core.analyzer import AnalyzerWorker


class AutomationPage(QWidget):
    """Página de controle da automação com preview e log em tempo real."""

    def __init__(self, config_manager, dashboard_page=None, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.dashboard = dashboard_page
        self.worker = None
        self.thread = None
        self.setup_ui()

    def setup_ui(self):
        """Constrói a interface de automação."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)

        # === HEADER ===
        header = QHBoxLayout()

        title_layout = QVBoxLayout()
        title = QLabel("Automação")
        title.setObjectName("title")
        title_layout.addWidget(title)
        subtitle = QLabel("Controle e monitoramento da automação de rerolls")
        subtitle.setObjectName("subtitle")
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()

        # Status indicator
        self.status_badge = QLabel("● PARADO")
        self.status_badge.setStyleSheet("""
            color: #e74c3c;
            font-weight: 700;
            font-size: 14px;
            padding: 8px 16px;
            background-color: #3f1e1e;
            border: 1px solid #e74c3c;
            border-radius: 20px;
        """)
        header.addWidget(self.status_badge, alignment=Qt.AlignRight | Qt.AlignTop)

        main_layout.addLayout(header)

        # === CONTROL BUTTONS ===
        controls_frame = QFrame()
        controls_frame.setObjectName("card")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(20, 16, 20, 16)
        controls_layout.setSpacing(16)

        self.btn_start = QPushButton("▶  INICIAR AUTOMAÇÃO")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_automation)
        controls_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹  PARAR")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_automation)
        controls_layout.addWidget(self.btn_stop)

        self.btn_pause = QPushButton("⏸  PAUSAR")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.pause_automation)
        controls_layout.addWidget(self.btn_pause)

        controls_layout.addStretch()

        # Info rápida
        info_label = QLabel("🛑 ESC = Parada de emergência")
        info_label.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: 600;")
        controls_layout.addWidget(info_label)

        main_layout.addWidget(controls_frame)

        # === CONTENT AREA (Splitter) ===
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # --- LEFT: Preview + OCR Text ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Preview da captura
        preview_frame = QFrame()
        preview_frame.setObjectName("card")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(16, 12, 16, 12)
        preview_layout.setSpacing(8)

        preview_header = QHBoxLayout()
        preview_title = QLabel("📸 Preview da Captura")
        preview_title.setObjectName("section_title")
        preview_header.addWidget(preview_title)

        self.preview_size_label = QLabel("")
        self.preview_size_label.setStyleSheet("color: #64748b; font-size: 11px;")
        preview_header.addWidget(self.preview_size_label, alignment=Qt.AlignRight)

        preview_layout.addLayout(preview_header)

        self.preview_label = QLabel("Aguardando captura...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(380, 260)
        self.preview_label.setStyleSheet("""
            background-color: #0f172a;
            border: 2px dashed #2a3a5c;
            border-radius: 8px;
            color: #64748b;
            font-size: 14px;
        """)
        preview_layout.addWidget(self.preview_label)

        left_layout.addWidget(preview_frame)

        # Texto OCR bruto
        ocr_frame = QFrame()
        ocr_frame.setObjectName("card")
        ocr_layout = QVBoxLayout(ocr_frame)
        ocr_layout.setContentsMargins(16, 12, 16, 12)
        ocr_layout.setSpacing(8)

        ocr_title = QLabel("🔤 Texto OCR Detectado")
        ocr_title.setObjectName("section_title")
        ocr_layout.addWidget(ocr_title)

        self.ocr_text_display = QTextEdit()
        self.ocr_text_display.setReadOnly(True)
        self.ocr_text_display.setMaximumHeight(120)
        self.ocr_text_display.setPlaceholderText("O texto extraído pelo OCR aparecerá aqui...")
        ocr_layout.addWidget(self.ocr_text_display)

        left_layout.addWidget(ocr_frame)

        splitter.addWidget(left_widget)

        # --- RIGHT: Log ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        log_frame = QFrame()
        log_frame.setObjectName("card")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(16, 12, 16, 12)
        log_layout.setSpacing(8)

        log_header = QHBoxLayout()
        log_title = QLabel("📋 Log de Execução")
        log_title.setObjectName("section_title")
        log_header.addWidget(log_title)

        btn_clear_log = QPushButton("🗑️")
        btn_clear_log.setObjectName("btn_icon")
        btn_clear_log.setToolTip("Limpar log")
        btn_clear_log.clicked.connect(self.clear_log)
        log_header.addWidget(btn_clear_log, alignment=Qt.AlignRight)

        log_layout.addLayout(log_header)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Cascadia Code", 11))
        log_layout.addWidget(self.log_display)

        right_layout.addWidget(log_frame)

        splitter.addWidget(right_widget)

        # Proporção 45/55
        splitter.setSizes([450, 550])

        main_layout.addWidget(splitter, stretch=1)

    # === AUTOMATION CONTROL ===

    def start_automation(self):
        """Inicia a automação em uma thread separada."""
        self.log_display.clear()
        self.append_log("⏳ Preparando automação...")
        self.append_log(f"   📍 Posição Reroll: {self.config.get_reroll_position()}")
        self.append_log(f"   🖱️ Posição Item (hover): {self.config.get_item_hover_position()}")
        self.append_log(f"   📐 Região captura: {self.config.get_capture_region()}")
        self.append_log(f"   ⏱️ Delay reroll: {self.config.get_click_delay()}s | Hover: {self.config.get_hover_delay()}s")
        self.append_log("")

        # Criar worker e thread
        self.thread = QThread()
        self.worker = AnalyzerWorker(self.config)
        self.worker.moveToThread(self.thread)

        # Conectar sinais
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self._on_finished)

        self.worker.status_changed.connect(self._on_status_changed)
        self.worker.magic_find_detected.connect(self._on_magic_find_detected)
        self.worker.best_value_updated.connect(self._on_best_value_updated)
        self.worker.reroll_count_updated.connect(self._on_reroll_count)
        self.worker.log_message.connect(self.append_log)
        self.worker.target_reached.connect(self._on_target_reached)
        self.worker.preview_updated.connect(self._update_preview)
        self.worker.ocr_text_updated.connect(self._update_ocr_text)
        self.worker.confidence_updated.connect(self._on_confidence)
        self.worker.elapsed_time_updated.connect(self._on_elapsed_time)
        self.worker.error_occurred.connect(self._on_error)

        # Atualizar botões
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_pause.setEnabled(True)

        # Iniciar
        self.thread.start()

    def stop_automation(self):
        """Para a automação."""
        if self.worker:
            self.worker.stop()
            self.append_log("🛑 Parando automação...")

    def pause_automation(self):
        """Pausa/retoma a automação."""
        if self.worker:
            self.worker.pause()
            if self.worker.is_paused():
                self.btn_pause.setText("▶  RETOMAR")
                self.append_log("⏸️ Automação pausada")
            else:
                self.btn_pause.setText("⏸  PAUSAR")
                self.append_log("▶️ Automação retomada")

    def _on_finished(self):
        """Callback quando a automação termina."""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸  PAUSAR")
        self._update_status_badge("PARADO", "#e74c3c", "#3f1e1e")

    def _on_status_changed(self, status):
        """Callback quando o status muda."""
        if self.dashboard:
            self.dashboard.update_status(status)
        
        if "Rodando" in status:
            self._update_status_badge("RODANDO", "#2ecc71", "#1e3f2e")
        elif "Pausado" in status:
            self._update_status_badge("PAUSADO", "#f39c12", "#3f3a1e")
        else:
            self._update_status_badge("PARADO", "#e74c3c", "#3f1e1e")

    def _on_magic_find_detected(self, value):
        """Callback quando Magic Find é detectado."""
        if self.dashboard:
            self.dashboard.update_last_magic_find(value)
            target = self.config.get_min_magic_find()
            self.dashboard.update_progress(value, target)
            self.dashboard.add_activity(f"🔍 Magic Find: {value:.1f}%")

    def _on_best_value_updated(self, value):
        """Callback quando melhor valor é atualizado."""
        if self.dashboard:
            self.dashboard.update_best_value(value)

    def _on_reroll_count(self, count):
        """Callback para contagem de rerolls."""
        if self.dashboard:
            self.dashboard.update_reroll_count(count)

    def _on_target_reached(self, value):
        """Callback quando a meta é atingida."""
        if self.dashboard:
            self.dashboard.add_activity(f"🔥 META ATINGIDA: {value:.1f}%!")

        # Notificação visual
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "🔥 Item Perfeito Encontrado!",
            f"Magic Find atingiu {value:.1f}%!\n\n"
            f"Meta: ≥ {self.config.get_min_magic_find()}%\n"
            f"A automação foi parada automaticamente.",
            QMessageBox.Ok
        )

    def _on_confidence(self, confidence):
        """Callback para confiança do OCR."""
        if self.dashboard:
            self.dashboard.update_confidence(confidence)

    def _on_elapsed_time(self, time_str):
        """Callback para tempo decorrido."""
        if self.dashboard:
            self.dashboard.update_elapsed_time(time_str)

    def _on_error(self, error_msg):
        """Callback para erros."""
        self.append_log(f"❌ ERRO: {error_msg}")

    def _update_preview(self, image):
        """Atualiza o preview da captura na interface."""
        try:
            if image is None:
                return

            h, w = image.shape[:2]
            ch = image.shape[2] if len(image.shape) == 3 else 1

            self.preview_size_label.setText(f"{w}×{h} px")

            if ch == 3:
                # BGR para RGB
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * w
                q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            else:
                bytes_per_line = w
                q_img = QImage(image.data, w, h, bytes_per_line, QImage.Format_Grayscale8)

            pixmap = QPixmap.fromImage(q_img)
            scaled = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)

        except Exception as e:
            print(f"[AutomationPage] Erro ao atualizar preview: {e}")

    def _update_ocr_text(self, text):
        """Atualiza o display de texto OCR."""
        self.ocr_text_display.setPlainText(text if text else "(nenhum texto detectado)")

    def _update_status_badge(self, text, color, bg_color):
        """Atualiza o badge de status."""
        self.status_badge.setText(f"● {text}")
        self.status_badge.setStyleSheet(f"""
            color: {color};
            font-weight: 700;
            font-size: 14px;
            padding: 8px 16px;
            background-color: {bg_color};
            border: 1px solid {color};
            border-radius: 20px;
        """)

    def append_log(self, message):
        """Adiciona uma mensagem ao log."""
        self.log_display.append(message)
        # Auto-scroll
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_display.setTextCursor(cursor)

    def clear_log(self):
        """Limpa o log."""
        self.log_display.clear()
