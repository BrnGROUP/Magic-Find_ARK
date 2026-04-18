"""
BRN Reroll Analyzer - Tela de Configurações
Permite configurar coordenadas, região de captura, meta, modo de detecção e mais.

Funcionalidades:
- Captura visual de posição do mouse (overlay com crosshair)
- Seleção visual da região de captura (draw rectangle overlay)
- Posição do item para hover (tooltip do ARK)
- Configurações de delay e modo de detecção
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QLineEdit, QSpinBox, QDoubleSpinBox,
    QComboBox, QPushButton, QGroupBox, QMessageBox,
    QFileDialog, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from ui.region_selector import RegionSelector, PositionPicker


class SettingsPage(QWidget):
    """Página de configurações do sistema."""

    # Sinal emitido quando configurações são salvas
    settings_saved = pyqtSignal()

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self._region_selector = None
        self._position_picker = None
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Constrói a interface de configurações."""
        # Scroll area para caber em telas menores
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(18)

        # === HEADER ===
        title = QLabel("Configurações")
        title.setObjectName("title")
        main_layout.addWidget(title)

        subtitle = QLabel("Configure os parâmetros da automação — use os botões visuais para capturar posições e regiões")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        main_layout.addWidget(subtitle)

        # ═══════════════════════════════════════════════
        # GRUPO 1: POSIÇÃO DO BOTÃO REROLL
        # ═══════════════════════════════════════════════
        reroll_group = QGroupBox("📍 Etapa 1 — Posição do Botão Reroll")
        reroll_layout = QVBoxLayout(reroll_group)
        reroll_layout.setSpacing(10)

        reroll_desc = QLabel(
            "Clique no botão abaixo e depois clique diretamente no botão Reroll no jogo."
        )
        reroll_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        reroll_desc.setWordWrap(True)
        reroll_layout.addWidget(reroll_desc)

        # Coordenadas
        coords_row = QHBoxLayout()
        coords_row.setSpacing(16)

        coords_row.addWidget(QLabel("X:"))
        self.reroll_x_spin = QSpinBox()
        self.reroll_x_spin.setRange(0, 9999)
        self.reroll_x_spin.setSuffix(" px")
        coords_row.addWidget(self.reroll_x_spin)

        coords_row.addWidget(QLabel("Y:"))
        self.reroll_y_spin = QSpinBox()
        self.reroll_y_spin.setRange(0, 9999)
        self.reroll_y_spin.setSuffix(" px")
        coords_row.addWidget(self.reroll_y_spin)

        coords_row.addStretch()

        # Botão capturar
        self.btn_pick_reroll = QPushButton("🎯 Capturar no Jogo")
        self.btn_pick_reroll.setToolTip("Abre overlay e clique no botão Reroll")
        self.btn_pick_reroll.setCursor(Qt.PointingHandCursor)
        self.btn_pick_reroll.clicked.connect(self.pick_reroll_position)
        coords_row.addWidget(self.btn_pick_reroll)

        reroll_layout.addLayout(coords_row)

        # Status label
        self.reroll_status = QLabel("")
        self.reroll_status.setStyleSheet("color: #64748b; font-size: 11px;")
        reroll_layout.addWidget(self.reroll_status)

        main_layout.addWidget(reroll_group)

        # ═══════════════════════════════════════════════
        # GRUPO 2: POSIÇÃO DO ITEM (HOVER)
        # ═══════════════════════════════════════════════
        item_group = QGroupBox("🖱️ Etapa 2 — Posição do Item (Hover)")
        item_layout = QVBoxLayout(item_group)
        item_layout.setSpacing(10)

        item_desc = QLabel(
            "Após clicar no Reroll, o mouse precisa voltar ao item para que o tooltip com os atributos "
            "apareça. Clique no botão abaixo e depois clique em cima do item no inventário."
        )
        item_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        item_desc.setWordWrap(True)
        item_layout.addWidget(item_desc)

        item_coords = QHBoxLayout()
        item_coords.setSpacing(16)

        item_coords.addWidget(QLabel("X:"))
        self.item_x_spin = QSpinBox()
        self.item_x_spin.setRange(0, 9999)
        self.item_x_spin.setSuffix(" px")
        item_coords.addWidget(self.item_x_spin)

        item_coords.addWidget(QLabel("Y:"))
        self.item_y_spin = QSpinBox()
        self.item_y_spin.setRange(0, 9999)
        self.item_y_spin.setSuffix(" px")
        item_coords.addWidget(self.item_y_spin)

        item_coords.addStretch()

        self.btn_pick_item = QPushButton("🖱️ Capturar no Jogo")
        self.btn_pick_item.setToolTip("Abre overlay e clique no item do inventário")
        self.btn_pick_item.setCursor(Qt.PointingHandCursor)
        self.btn_pick_item.clicked.connect(self.pick_item_position)
        item_coords.addWidget(self.btn_pick_item)

        item_layout.addLayout(item_coords)

        self.item_status = QLabel("")
        self.item_status.setStyleSheet("color: #64748b; font-size: 11px;")
        item_layout.addWidget(self.item_status)

        main_layout.addWidget(item_group)

        # ═══════════════════════════════════════════════
        # GRUPO 3: REGIÃO DE CAPTURA DA TELA
        # ═══════════════════════════════════════════════
        capture_group = QGroupBox("📐 Etapa 3 — Região de Captura do Tooltip")
        capture_layout = QVBoxLayout(capture_group)
        capture_layout.setSpacing(10)

        capture_desc = QLabel(
            "Selecione a região da tela onde o tooltip do item aparece (com os atributos). "
            "Passe o mouse sobre o item no jogo primeiro para que o tooltip fique visível, "
            "depois clique no botão abaixo e desenhe um retângulo ao redor do tooltip."
        )
        capture_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        capture_desc.setWordWrap(True)
        capture_layout.addWidget(capture_desc)

        # Coordenadas da região
        region_row = QHBoxLayout()
        region_row.setSpacing(12)

        labels = ["X1:", "Y1:", "X2:", "Y2:"]
        self.capture_spins = []
        for label_text in labels:
            region_row.addWidget(QLabel(label_text))
            spin = QSpinBox()
            spin.setRange(0, 9999)
            spin.setSuffix(" px")
            region_row.addWidget(spin)
            self.capture_spins.append(spin)

        region_row.addStretch()
        capture_layout.addLayout(region_row)

        # Botão seletor visual
        btn_row = QHBoxLayout()

        self.btn_select_region = QPushButton("📐 Selecionar Região na Tela")
        self.btn_select_region.setToolTip("Abre overlay para desenhar um retângulo na tela")
        self.btn_select_region.setCursor(Qt.PointingHandCursor)
        self.btn_select_region.setMinimumHeight(38)
        self.btn_select_region.clicked.connect(self.select_capture_region)
        btn_row.addWidget(self.btn_select_region)

        btn_row.addStretch()
        capture_layout.addLayout(btn_row)

        self.region_status = QLabel("")
        self.region_status.setStyleSheet("color: #64748b; font-size: 11px;")
        capture_layout.addWidget(self.region_status)

        # Info box
        info_frame = QFrame()
        info_frame.setObjectName("notification_info")
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(12, 8, 12, 8)
        info_icon = QLabel("💡")
        info_icon.setFont(QFont("Segoe UI Emoji", 14))
        info_layout.addWidget(info_icon)
        info_text = QLabel(
            "Dica: Primeiro passe o mouse sobre o item no jogo para o tooltip aparecer, "
            "depois clique em 'Selecionar Região' e desenhe o retângulo cobrindo o tooltip inteiro."
        )
        info_text.setStyleSheet("color: #94a3b8; font-size: 11px;")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text, stretch=1)
        capture_layout.addWidget(info_frame)

        main_layout.addWidget(capture_group)

        # ═══════════════════════════════════════════════
        # GRUPO 4: PARÂMETROS DA AUTOMAÇÃO
        # ═══════════════════════════════════════════════
        params_group = QGroupBox("⚙️ Parâmetros da Automação")
        params_layout = QGridLayout(params_group)
        params_layout.setSpacing(12)
        params_layout.setColumnStretch(1, 1)
        params_layout.setColumnStretch(3, 1)

        # Meta de Magic Find
        params_layout.addWidget(QLabel("Meta Magic Find:"), 0, 0)
        self.min_mf_spin = QDoubleSpinBox()
        self.min_mf_spin.setRange(1.0, 100.0)
        self.min_mf_spin.setDecimals(1)
        self.min_mf_spin.setSuffix(" %")
        self.min_mf_spin.setSingleStep(5.0)
        params_layout.addWidget(self.min_mf_spin, 0, 1)

        # Delay entre cliques (pós-reroll)
        params_layout.addWidget(QLabel("Delay pós-reroll:"), 0, 2)
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.5, 30.0)
        self.delay_spin.setDecimals(1)
        self.delay_spin.setSuffix(" s")
        self.delay_spin.setSingleStep(0.5)
        self.delay_spin.setToolTip("Tempo de espera após clicar no Reroll (para o jogo processar)")
        params_layout.addWidget(self.delay_spin, 0, 3)

        # Delay do hover (tooltip)
        params_layout.addWidget(QLabel("Delay do hover:"), 1, 0)
        self.hover_delay_spin = QDoubleSpinBox()
        self.hover_delay_spin.setRange(0.3, 10.0)
        self.hover_delay_spin.setDecimals(1)
        self.hover_delay_spin.setSuffix(" s")
        self.hover_delay_spin.setSingleStep(0.5)
        self.hover_delay_spin.setToolTip("Tempo de espera após mover o mouse ao item (para o tooltip aparecer)")
        params_layout.addWidget(self.hover_delay_spin, 1, 1)

        # Modo de detecção
        params_layout.addWidget(QLabel("Modo de detecção:"), 1, 2)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["OCR (Tesseract)", "Reconhecimento por Imagem"])
        params_layout.addWidget(self.mode_combo, 1, 3)

        # Tecla de emergência
        params_layout.addWidget(QLabel("Tecla emergência:"), 2, 0)
        self.emergency_combo = QComboBox()
        self.emergency_combo.addItems(["ESC", "F12", "F10", "Pause"])
        params_layout.addWidget(self.emergency_combo, 2, 1)

        main_layout.addWidget(params_group)

        # ═══════════════════════════════════════════════
        # GRUPO 5: TESSERACT
        # ═══════════════════════════════════════════════
        tesseract_group = QGroupBox("🔧 Configuração do Tesseract OCR")
        tesseract_layout = QHBoxLayout(tesseract_group)
        tesseract_layout.setSpacing(12)

        tesseract_layout.addWidget(QLabel("Caminho:"))
        self.tesseract_path_input = QLineEdit()
        self.tesseract_path_input.setPlaceholderText("Ex: C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        tesseract_layout.addWidget(self.tesseract_path_input, stretch=1)

        btn_browse = QPushButton("📂")
        btn_browse.setObjectName("btn_icon")
        btn_browse.setToolTip("Procurar executável do Tesseract")
        btn_browse.clicked.connect(self.browse_tesseract)
        tesseract_layout.addWidget(btn_browse)

        main_layout.addWidget(tesseract_group)

        # === BOTÕES DE AÇÃO ===
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(12)

        self.btn_save = QPushButton("💾 Salvar Configurações")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_save.setMinimumHeight(40)
        actions_layout.addWidget(self.btn_save)

        self.btn_reset = QPushButton("🔄 Restaurar Padrão")
        self.btn_reset.setObjectName("btn_secondary")
        self.btn_reset.clicked.connect(self.reset_settings)
        actions_layout.addWidget(self.btn_reset)

        actions_layout.addStretch()

        main_layout.addLayout(actions_layout)
        main_layout.addStretch()

        scroll.setWidget(content)

        # Layout principal do widget
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll)

    # ═══════════════════════════════════════════════════
    # CAPTURA VISUAL DE POSIÇÕES E REGIÕES
    # ═══════════════════════════════════════════════════

    def pick_reroll_position(self):
        """Abre overlay para capturar posição do botão Reroll."""
        # Minimizar a janela principal para não atrapalhar
        parent_window = self.window()
        if parent_window:
            parent_window.showMinimized()

        QTimer.singleShot(500, self._open_reroll_picker)

    def _open_reroll_picker(self):
        """Abre o picker de posição do Reroll após delay."""
        self._position_picker = PositionPicker("Clique no botão REROLL do jogo")
        self._position_picker.position_selected.connect(self._on_reroll_position_selected)
        self._position_picker.selection_cancelled.connect(self._on_picker_cancelled)

    def _on_reroll_position_selected(self, x, y):
        """Callback quando posição do Reroll é capturada."""
        self.reroll_x_spin.setValue(x)
        self.reroll_y_spin.setValue(y)
        self.reroll_status.setText(f"✅ Posição capturada: ({x}, {y})")
        self.reroll_status.setStyleSheet("color: #2ecc71; font-size: 11px; font-weight: 600;")
        self._restore_window()

    def pick_item_position(self):
        """Abre overlay para capturar posição do item no inventário."""
        parent_window = self.window()
        if parent_window:
            parent_window.showMinimized()

        QTimer.singleShot(500, self._open_item_picker)

    def _open_item_picker(self):
        """Abre o picker de posição do item após delay."""
        self._position_picker = PositionPicker("Clique no ITEM do inventário (onde o mouse deve ficar para aparecer o tooltip)")
        self._position_picker.position_selected.connect(self._on_item_position_selected)
        self._position_picker.selection_cancelled.connect(self._on_picker_cancelled)

    def _on_item_position_selected(self, x, y):
        """Callback quando posição do item é capturada."""
        self.item_x_spin.setValue(x)
        self.item_y_spin.setValue(y)
        self.item_status.setText(f"✅ Posição capturada: ({x}, {y})")
        self.item_status.setStyleSheet("color: #2ecc71; font-size: 11px; font-weight: 600;")
        self._restore_window()

    def select_capture_region(self):
        """Abre overlay para selecionar região de captura."""
        parent_window = self.window()
        if parent_window:
            parent_window.showMinimized()

        QTimer.singleShot(500, self._open_region_selector)

    def _open_region_selector(self):
        """Abre o seletor de região após delay."""
        self._region_selector = RegionSelector()
        self._region_selector.region_selected.connect(self._on_region_selected)
        self._region_selector.selection_cancelled.connect(self._on_picker_cancelled)

    def _on_region_selected(self, x1, y1, x2, y2):
        """Callback quando região é selecionada."""
        self.capture_spins[0].setValue(x1)
        self.capture_spins[1].setValue(y1)
        self.capture_spins[2].setValue(x2)
        self.capture_spins[3].setValue(y2)
        
        width = x2 - x1
        height = y2 - y1
        self.region_status.setText(
            f"✅ Região capturada: ({x1}, {y1}) → ({x2}, {y2}) — {width}×{height} px"
        )
        self.region_status.setStyleSheet("color: #2ecc71; font-size: 11px; font-weight: 600;")
        self._restore_window()

    def _on_picker_cancelled(self):
        """Callback quando seleção é cancelada."""
        self._restore_window()

    def _restore_window(self):
        """Restaura a janela principal."""
        parent_window = self.window()
        if parent_window:
            parent_window.showNormal()
            parent_window.activateWindow()

    # ═══════════════════════════════════════════════════
    # LOAD / SAVE / RESET
    # ═══════════════════════════════════════════════════

    def load_settings(self):
        """Carrega configurações do ConfigManager para a interface."""
        rx, ry = self.config.get_reroll_position()
        self.reroll_x_spin.setValue(rx)
        self.reroll_y_spin.setValue(ry)

        ix, iy = self.config.get_item_hover_position()
        self.item_x_spin.setValue(ix)
        self.item_y_spin.setValue(iy)

        region = self.config.get_capture_region()
        for i, spin in enumerate(self.capture_spins):
            if i < len(region):
                spin.setValue(region[i])

        self.min_mf_spin.setValue(self.config.get_min_magic_find())
        self.delay_spin.setValue(self.config.get_click_delay())
        self.hover_delay_spin.setValue(self.config.get_hover_delay())

        mode = self.config.get_mode()
        self.mode_combo.setCurrentIndex(0 if mode == "ocr" else 1)

        emergency = self.config.get("emergency_key", "esc").upper()
        index = self.emergency_combo.findText(emergency)
        if index >= 0:
            self.emergency_combo.setCurrentIndex(index)

        self.tesseract_path_input.setText(self.config.get_tesseract_path())

    def save_settings(self):
        """Salva as configurações da interface no ConfigManager."""
        self.config.set("reroll_x", self.reroll_x_spin.value())
        self.config.set("reroll_y", self.reroll_y_spin.value())
        self.config.set("item_hover_x", self.item_x_spin.value())
        self.config.set("item_hover_y", self.item_y_spin.value())
        self.config.set("capture_region", [s.value() for s in self.capture_spins])
        self.config.set("min_magic_find", self.min_mf_spin.value())
        self.config.set("click_delay", self.delay_spin.value())
        self.config.set("hover_delay", self.hover_delay_spin.value())
        self.config.set("mode", "ocr" if self.mode_combo.currentIndex() == 0 else "image")
        self.config.set("emergency_key", self.emergency_combo.currentText().lower())
        self.config.set("tesseract_path", self.tesseract_path_input.text())
        self.config.save()

        self.settings_saved.emit()

        QMessageBox.information(
            self, "Sucesso",
            "✅ Configurações salvas com sucesso!",
            QMessageBox.Ok
        )

    def reset_settings(self):
        """Restaura configurações padrão."""
        reply = QMessageBox.question(
            self, "Confirmar",
            "Deseja restaurar todas as configurações para o padrão?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from core.config_manager import DEFAULT_CONFIG
            for key, value in DEFAULT_CONFIG.items():
                if key != "history":
                    self.config.set(key, value)
            self.load_settings()
            QMessageBox.information(self, "Sucesso", "Configurações restauradas!")

    def browse_tesseract(self):
        """Abre um diálogo para selecionar o executável do Tesseract."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Tesseract",
            "C:\\Program Files\\Tesseract-OCR",
            "Executáveis (*.exe)"
        )
        if path:
            self.tesseract_path_input.setText(path)
