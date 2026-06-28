"""
BRN Reroll Analyzer - Tela de Movimentação e Combate Cíclico
Controles de início/fim, configuração de tempo de W/S, clicks e log em tempo real.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QTextEdit, QDoubleSpinBox, QSpinBox, QComboBox, QGroupBox
)
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtGui import QFont, QTextCursor

from core.movement_worker import MovementWorker


class MovementPage(QWidget):
    """Página de controle para movimentação W/S e ataque contínuo no ARK."""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.worker = None
        self.thread = None
        self.setup_ui()
        
        # Inicializa o AutoClicker global
        from core.auto_clicker import AutoClicker
        self.autoclicker = AutoClicker(self.config)
        self.autoclicker.log_message.connect(self.append_log)
        
        self.load_settings()

    def setup_ui(self):
        """Constrói a interface da página de movimentação."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)

        # === HEADER ===
        header = QHBoxLayout()

        title_layout = QVBoxLayout()
        title = QLabel("Movimentação & Farm")
        title.setObjectName("title")
        title_layout.addWidget(title)
        subtitle = QLabel("Automação cíclica de movimento (Frente/Trás) e socos")
        subtitle.setObjectName("subtitle")
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()

        # Status badge
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

        # === CONFIGURATIONS CARD ===
        config_group = QGroupBox("⚙️ Configurações da Movimentação")
        config_layout = QGridLayout(config_group)
        config_layout.setSpacing(16)
        config_layout.setColumnStretch(1, 1)
        config_layout.setColumnStretch(3, 1)

        # Tempo W
        config_layout.addWidget(QLabel("Tempo Frente (W):"), 0, 0)
        self.w_duration_spin = QDoubleSpinBox()
        self.w_duration_spin.setRange(0.5, 60.0)
        self.w_duration_spin.setDecimals(1)
        self.w_duration_spin.setSuffix(" s")
        self.w_duration_spin.setSingleStep(0.5)
        self.w_duration_spin.valueChanged.connect(self.save_settings)
        config_layout.addWidget(self.w_duration_spin, 0, 1)

        # Tempo S
        config_layout.addWidget(QLabel("Tempo Trás (S):"), 0, 2)
        self.s_duration_spin = QDoubleSpinBox()
        self.s_duration_spin.setRange(0.5, 60.0)
        self.s_duration_spin.setDecimals(1)
        self.s_duration_spin.setSuffix(" s")
        self.s_duration_spin.setSingleStep(0.5)
        self.s_duration_spin.valueChanged.connect(self.save_settings)
        config_layout.addWidget(self.s_duration_spin, 0, 3)

        # Cliques (socos)
        config_layout.addWidget(QLabel("Desferir Socos (L-Click):"), 1, 0)
        self.click_enabled_combo = QComboBox()
        self.click_enabled_combo.addItems(["Ativado", "Desativado"])
        self.click_enabled_combo.currentIndexChanged.connect(self._on_click_toggle)
        self.click_enabled_combo.currentIndexChanged.connect(self.save_settings)
        config_layout.addWidget(self.click_enabled_combo, 1, 1)

        # Intervalo cliques
        self.click_interval_label = QLabel("Intervalo do Clique:")
        config_layout.addWidget(self.click_interval_label, 1, 2)
        self.click_interval_spin = QDoubleSpinBox()
        self.click_interval_spin.setRange(0.1, 10.0)
        self.click_interval_spin.setDecimals(2)
        self.click_interval_spin.setSuffix(" s")
        self.click_interval_spin.setSingleStep(0.1)
        self.click_interval_spin.valueChanged.connect(self.save_settings)
        config_layout.addWidget(self.click_interval_spin, 1, 3)

        main_layout.addWidget(config_group)

        # === AUTO-CLICKER CARD ===
        autoclick_group = QGroupBox("🔥 Auto-Clique Rápido (Burst Clicker)")
        autoclick_layout = QGridLayout(autoclick_group)
        autoclick_layout.setSpacing(16)
        autoclick_layout.setColumnStretch(1, 1)
        autoclick_layout.setColumnStretch(3, 1)

        # Cliques de Ativação
        autoclick_layout.addWidget(QLabel("Cliques de Ativação:"), 0, 0)
        self.autoclick_trigger_spin = QSpinBox()
        self.autoclick_trigger_spin.setRange(2, 50)
        self.autoclick_trigger_spin.setSuffix(" cliques")
        self.autoclick_trigger_spin.valueChanged.connect(self.save_settings)
        autoclick_layout.addWidget(self.autoclick_trigger_spin, 0, 1)

        # Janela de Tempo
        autoclick_layout.addWidget(QLabel("Janela de Tempo:"), 0, 2)
        self.autoclick_window_spin = QDoubleSpinBox()
        self.autoclick_window_spin.setRange(0.2, 10.0)
        self.autoclick_window_spin.setDecimals(1)
        self.autoclick_window_spin.setSuffix(" s")
        self.autoclick_window_spin.setSingleStep(0.2)
        self.autoclick_window_spin.valueChanged.connect(self.save_settings)
        autoclick_layout.addWidget(self.autoclick_window_spin, 0, 3)

        # Cliques Simulados
        autoclick_layout.addWidget(QLabel("Cliques Simulados:"), 1, 0)
        self.autoclick_burst_spin = QSpinBox()
        self.autoclick_burst_spin.setRange(10, 5000)
        self.autoclick_burst_spin.setSingleStep(50)
        self.autoclick_burst_spin.setSuffix(" cliques")
        self.autoclick_burst_spin.valueChanged.connect(self.save_settings)
        autoclick_layout.addWidget(self.autoclick_burst_spin, 1, 1)

        # Botão de Ativação
        self.btn_toggle_autoclick = QPushButton("▶  ATIVAR AUTO-CLIQUE")
        self.btn_toggle_autoclick.setObjectName("btn_secondary")
        self.btn_toggle_autoclick.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_autoclick.clicked.connect(self.toggle_autoclick)
        autoclick_layout.addWidget(self.btn_toggle_autoclick, 1, 2, 1, 2)

        main_layout.addWidget(autoclick_group)

        # === CONTROL BUTTONS ===
        controls_frame = QFrame()
        controls_frame.setObjectName("card")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(20, 16, 20, 16)
        controls_layout.setSpacing(16)

        self.btn_start = QPushButton("▶  INICIAR MOVIMENTAÇÃO")
        self.btn_start.setObjectName("btn_start")
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_movement)
        controls_layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏹  PARAR")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_stop.setCursor(Qt.PointingHandCursor)
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_movement)
        controls_layout.addWidget(self.btn_stop)

        self.btn_pause = QPushButton("⏸  PAUSAR")
        self.btn_pause.setObjectName("btn_pause")
        self.btn_pause.setCursor(Qt.PointingHandCursor)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self.pause_movement)
        controls_layout.addWidget(self.btn_pause)

        controls_layout.addStretch()

        # Tecla de pânico info
        emergency_key = self.config.get("emergency_key", "esc").upper()
        self.info_label = QLabel(f"🛑 {emergency_key} = Parada de emergência")
        self.info_label.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: 600;")
        controls_layout.addWidget(self.info_label)

        main_layout.addWidget(controls_frame)

        # === LOG AREA ===
        log_frame = QFrame()
        log_frame.setObjectName("card")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(16, 12, 16, 12)
        log_layout.setSpacing(8)

        log_header = QHBoxLayout()
        log_title = QLabel("📋 Log de Execução")
        log_title.setObjectName("section_title")
        log_header.addWidget(log_title)

        btn_clear = QPushButton("🗑️")
        btn_clear.setObjectName("btn_icon")
        btn_clear.setToolTip("Limpar log")
        btn_clear.clicked.connect(self.clear_log)
        log_header.addWidget(btn_clear, alignment=Qt.AlignRight)

        log_layout.addLayout(log_header)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Cascadia Code", 11))
        log_layout.addWidget(self.log_display)

        main_layout.addWidget(log_frame, stretch=1)

    # === LIFECYCLE / SETTINGS ===

    def load_settings(self):
        """Carrega as configurações salvas para os componentes da tela."""
        self.w_duration_spin.setValue(self.config.get_movement_w_duration())
        self.s_duration_spin.setValue(self.config.get_movement_s_duration())
        
        click_enabled = self.config.is_movement_click_enabled()
        self.click_enabled_combo.setCurrentIndex(0 if click_enabled else 1)
        self.click_interval_spin.setValue(self.config.get_movement_click_interval())
        
        # Auto-Clicker Settings
        self.autoclick_trigger_spin.setValue(self.config.get_autoclick_trigger_clicks())
        self.autoclick_burst_spin.setValue(self.config.get_autoclick_burst_clicks())
        self.autoclick_window_spin.setValue(self.config.get_autoclick_time_window())
        
        self._on_click_toggle()

    def save_settings(self):
        """Salva as configurações alteradas na UI para o ConfigManager."""
        self.config.set("movement_w_duration", self.w_duration_spin.value())
        self.config.set("movement_s_duration", self.s_duration_spin.value())
        self.config.set("movement_click_enabled", self.click_enabled_combo.currentIndex() == 0)
        self.config.set("movement_click_interval", self.click_interval_spin.value())
        
        # Auto-Clicker Settings
        self.config.set("autoclick_trigger_clicks", self.autoclick_trigger_spin.value())
        self.config.set("autoclick_burst_clicks", self.autoclick_burst_spin.value())
        self.config.set("autoclick_time_window", self.autoclick_window_spin.value())

    def _on_click_toggle(self):
        """Desabilita ou habilita o controle do delay do clique de acordo com a seleção."""
        enabled = self.click_enabled_combo.currentIndex() == 0
        self.click_interval_spin.setEnabled(enabled)
        self.click_interval_label.setEnabled(enabled)

    # === AUTOMATION CONTROL ===

    def start_movement(self):
        """Inicia a movimentação cíclica em uma thread dedicada."""
        self.log_display.clear()
        self.append_log("⏳ Preparando automação de movimentação...")
        
        # Salva o estado atual da tela antes de rodar
        self.save_settings()

        # Atualizar a tecla de emergência no label caso tenha mudado
        emergency_key = self.config.get("emergency_key", "esc").upper()
        self.info_label.setText(f"🛑 {emergency_key} = Parada de emergência")

        # Criar a thread e o worker
        self.thread = QThread()
        self.worker = MovementWorker(self.config)
        self.worker.moveToThread(self.thread)

        # Conectar os sinais
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self._on_finished)

        self.worker.status_changed.connect(self._on_status_changed)
        self.worker.log_message.connect(self.append_log)

        # Atualizar controles da UI
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_pause.setEnabled(True)
        self.w_duration_spin.setEnabled(False)
        self.s_duration_spin.setEnabled(False)
        self.click_enabled_combo.setEnabled(False)
        self.click_interval_spin.setEnabled(False)

        # Iniciar thread
        self.thread.start()

    def stop_movement(self):
        """Solicita a interrupção da automação."""
        if self.worker:
            self.worker.stop()
            self.append_log("🛑 Parando automação de movimentação...")

    def pause_movement(self):
        """Pausa ou retoma a automação."""
        if self.worker:
            self.worker.pause()
            if self.worker.is_paused():
                self.btn_pause.setText("▶  RETOMAR")
                self.append_log("⏸️ Movimentação pausada")
            else:
                self.btn_pause.setText("⏸  PAUSAR")
                self.append_log("▶️ Movimentação retomada")

    def _on_finished(self):
        """Executado quando a thread do worker é finalizada."""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("⏸  PAUSAR")
        
        self.w_duration_spin.setEnabled(True)
        self.s_duration_spin.setEnabled(True)
        self.click_enabled_combo.setEnabled(True)
        self._on_click_toggle() # restaura estado correto de habilitação do spin de clique
        
        self._update_status_badge("PARADO", "#e74c3c", "#3f1e1e")

    def _on_status_changed(self, status):
        """Callback acionado quando o status do worker muda."""
        if "Rodando" in status:
            self._update_status_badge("RODANDO", "#2ecc71", "#1e3f2e")
        elif "Pausado" in status:
            self._update_status_badge("PAUSADO", "#f39c12", "#3f3a1e")
        else:
            self._update_status_badge("PARADO", "#e74c3c", "#3f1e1e")

    def _update_status_badge(self, text, color, bg_color):
        """Atualiza a cor e o texto do indicador de status da página."""
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
        """Adiciona uma mensagem de texto ao console de logs com auto-scroll."""
        self.log_display.append(message)
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_display.setTextCursor(cursor)

    def clear_log(self):
        """Limpa as mensagens de log da tela."""
        self.log_display.clear()

    def toggle_autoclick(self):
        """Ativa ou desativa o monitoramento de cliques rápidos."""
        if self.autoclicker.is_active():
            self.autoclicker.stop()
            self.btn_toggle_autoclick.setText("▶  ATIVAR AUTO-CLIQUE")
            self.btn_toggle_autoclick.setObjectName("btn_secondary")
            
            # Forçar atualização visual do botão
            self.btn_toggle_autoclick.style().unpolish(self.btn_toggle_autoclick)
            self.btn_toggle_autoclick.style().polish(self.btn_toggle_autoclick)
            
            # Reabilitar inputs
            self.autoclick_trigger_spin.setEnabled(True)
            self.autoclick_burst_spin.setEnabled(True)
            self.autoclick_window_spin.setEnabled(True)
        else:
            self.save_settings()
            success = self.autoclicker.start()
            if success:
                self.btn_toggle_autoclick.setText("⏹  DESATIVAR AUTO-CLIQUE")
                self.btn_toggle_autoclick.setObjectName("btn_danger")
                
                # Forçar atualização visual do botão
                self.btn_toggle_autoclick.style().unpolish(self.btn_toggle_autoclick)
                self.btn_toggle_autoclick.style().polish(self.btn_toggle_autoclick)
                
                # Desabilitar inputs enquanto ativo
                self.autoclick_trigger_spin.setEnabled(False)
                self.autoclick_burst_spin.setEnabled(False)
                self.autoclick_window_spin.setEnabled(False)
