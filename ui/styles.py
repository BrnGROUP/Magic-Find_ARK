"""
BRN Reroll Analyzer - Sistema de Estilos (BRN UI Design System)
Define o tema visual completo da aplicação: dark theme premium.
"""


def get_stylesheet():
    """Retorna a stylesheet completa da aplicação no padrão BRN UI."""
    return """
    /* ================================================
       BRN UI DESIGN SYSTEM - DARK THEME PREMIUM
       Cores:
         Primário:   #2c3e50 (dark navy)
         Secundário: #3498db (blue accent)
         Destaque:   #e74c3c (red alert)
         Sucesso:    #2ecc71 (green)
         Fundo:      #1a1a2e → #16213e (gradient)
         Card:       #1e293b
         Texto:      #e2e8f0
       ================================================ */

    /* --- GLOBAL --- */
    QWidget {
        background-color: #1a1a2e;
        color: #e2e8f0;
        font-family: "Segoe UI", "Inter", "Arial", sans-serif;
        font-size: 13px;
    }

    QMainWindow {
        background-color: #1a1a2e;
    }

    /* --- SIDEBAR --- */
    QWidget#sidebar {
        background-color: #0f0f23;
        border-right: 1px solid #2a2a4a;
        min-width: 240px;
        max-width: 240px;
    }

    QWidget#sidebar QPushButton {
        background-color: transparent;
        color: #8892b0;
        border: none;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: left;
        font-size: 13px;
        font-weight: 500;
        margin: 2px 10px;
    }

    QWidget#sidebar QPushButton:hover {
        background-color: #1e293b;
        color: #e2e8f0;
    }

    QWidget#sidebar QPushButton:checked,
    QWidget#sidebar QPushButton[active="true"] {
        background-color: #3498db;
        color: #ffffff;
        font-weight: 600;
    }

    QWidget#sidebar QLabel#logo_label {
        color: #3498db;
        font-size: 18px;
        font-weight: 700;
        padding: 20px 16px 8px 16px;
        letter-spacing: 1px;
    }

    QWidget#sidebar QLabel#subtitle_label {
        color: #64748b;
        font-size: 10px;
        padding: 0px 16px 16px 16px;
        letter-spacing: 0.5px;
    }

    /* --- CARDS --- */
    QFrame#card {
        background-color: #1e293b;
        border: 1px solid #2a3a5c;
        border-radius: 12px;
        padding: 20px;
    }

    QFrame#card:hover {
        border-color: #3498db;
    }

    QFrame#card_stat {
        background-color: #1e293b;
        border: 1px solid #2a3a5c;
        border-radius: 12px;
        padding: 16px;
    }

    QFrame#card_highlight {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #1e3a5f, stop:1 #1e293b
        );
        border: 1px solid #3498db;
        border-radius: 12px;
        padding: 16px;
    }

    QFrame#card_success {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #1e3f2e, stop:1 #1e293b
        );
        border: 1px solid #2ecc71;
        border-radius: 12px;
        padding: 16px;
    }

    QFrame#card_danger {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:1,
            stop:0 #3f1e1e, stop:1 #1e293b
        );
        border: 1px solid #e74c3c;
        border-radius: 12px;
        padding: 16px;
    }

    /* --- LABELS --- */
    QLabel {
        background-color: transparent;
        color: #e2e8f0;
    }

    QLabel#title {
        font-size: 22px;
        font-weight: 700;
        color: #f1f5f9;
        letter-spacing: 0.5px;
    }

    QLabel#subtitle {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 400;
    }

    QLabel#card_title {
        font-size: 11px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    QLabel#card_value {
        font-size: 28px;
        font-weight: 700;
        color: #f1f5f9;
    }

    QLabel#card_value_blue {
        font-size: 28px;
        font-weight: 700;
        color: #3498db;
    }

    QLabel#card_value_green {
        font-size: 28px;
        font-weight: 700;
        color: #2ecc71;
    }

    QLabel#card_value_red {
        font-size: 28px;
        font-weight: 700;
        color: #e74c3c;
    }

    QLabel#card_value_gold {
        font-size: 28px;
        font-weight: 700;
        color: #f39c12;
    }

    QLabel#status_running {
        color: #2ecc71;
        font-weight: 600;
        font-size: 14px;
    }

    QLabel#status_stopped {
        color: #e74c3c;
        font-weight: 600;
        font-size: 14px;
    }

    QLabel#section_title {
        font-size: 16px;
        font-weight: 600;
        color: #e2e8f0;
        padding: 4px 0;
    }

    /* --- BUTTONS --- */
    QPushButton {
        background-color: #3498db;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        min-height: 20px;
    }

    QPushButton:hover {
        background-color: #2980b9;
    }

    QPushButton:pressed {
        background-color: #2471a3;
    }

    QPushButton:disabled {
        background-color: #2a3a5c;
        color: #64748b;
    }

    QPushButton#btn_start {
        background-color: #2ecc71;
        font-size: 16px;
        font-weight: 700;
        padding: 14px 32px;
        border-radius: 10px;
        min-width: 160px;
    }

    QPushButton#btn_start:hover {
        background-color: #27ae60;
    }

    QPushButton#btn_stop {
        background-color: #e74c3c;
        font-size: 16px;
        font-weight: 700;
        padding: 14px 32px;
        border-radius: 10px;
        min-width: 160px;
    }

    QPushButton#btn_stop:hover {
        background-color: #c0392b;
    }

    QPushButton#btn_pause {
        background-color: #f39c12;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 8px;
    }

    QPushButton#btn_pause:hover {
        background-color: #e67e22;
    }

    QPushButton#btn_secondary {
        background-color: #2a3a5c;
        color: #e2e8f0;
        border: 1px solid #3a4a6c;
    }

    QPushButton#btn_secondary:hover {
        background-color: #3a4a6c;
        border-color: #3498db;
    }

    QPushButton#btn_danger {
        background-color: #e74c3c;
    }

    QPushButton#btn_danger:hover {
        background-color: #c0392b;
    }

    QPushButton#btn_icon {
        background-color: transparent;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        padding: 8px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
    }

    QPushButton#btn_icon:hover {
        background-color: #1e293b;
        border-color: #3498db;
    }

    /* --- INPUTS --- */
    QLineEdit, QSpinBox, QDoubleSpinBox {
        background-color: #0f172a;
        color: #e2e8f0;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        selection-background-color: #3498db;
    }

    QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #3498db;
        outline: none;
    }

    QSpinBox::up-button, QDoubleSpinBox::up-button,
    QSpinBox::down-button, QDoubleSpinBox::down-button {
        background-color: #2a3a5c;
        border: none;
        border-radius: 4px;
        width: 20px;
    }

    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
        background-color: #3498db;
    }

    /* --- COMBO BOX --- */
    QComboBox {
        background-color: #0f172a;
        color: #e2e8f0;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 14px;
        min-height: 20px;
    }

    QComboBox:hover {
        border-color: #3498db;
    }

    QComboBox::drop-down {
        border: none;
        width: 30px;
    }

    QComboBox QAbstractItemView {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        selection-background-color: #3498db;
        padding: 4px;
    }

    /* --- TEXT EDIT (LOG) --- */
    QTextEdit {
        background-color: #0f172a;
        color: #a0e8b0;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        padding: 12px;
        font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
        font-size: 12px;
        selection-background-color: #3498db;
    }

    QPlainTextEdit {
        background-color: #0f172a;
        color: #a0e8b0;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        padding: 12px;
        font-family: "Cascadia Code", "Consolas", "Courier New", monospace;
        font-size: 12px;
    }

    /* --- TABLE --- */
    QTableWidget {
        background-color: #0f172a;
        color: #e2e8f0;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        gridline-color: #1e293b;
        selection-background-color: #2a3a5c;
        font-size: 13px;
    }

    QTableWidget::item {
        padding: 8px 12px;
        border-bottom: 1px solid #1e293b;
    }

    QTableWidget::item:selected {
        background-color: #2a3a5c;
        color: #3498db;
    }

    QHeaderView::section {
        background-color: #1e293b;
        color: #94a3b8;
        border: none;
        border-bottom: 2px solid #3498db;
        padding: 10px 12px;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* --- SCROLL BAR --- */
    QScrollBar:vertical {
        background-color: #0f172a;
        width: 8px;
        border-radius: 4px;
        margin: 0;
    }

    QScrollBar::handle:vertical {
        background-color: #2a3a5c;
        border-radius: 4px;
        min-height: 30px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #3498db;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }

    QScrollBar:horizontal {
        background-color: #0f172a;
        height: 8px;
        border-radius: 4px;
    }

    QScrollBar::handle:horizontal {
        background-color: #2a3a5c;
        border-radius: 4px;
        min-width: 30px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #3498db;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }

    /* --- PROGRESS BAR --- */
    QProgressBar {
        background-color: #0f172a;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        text-align: center;
        color: #e2e8f0;
        font-weight: 600;
        min-height: 24px;
    }

    QProgressBar::chunk {
        background-color: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 #3498db, stop:1 #2ecc71
        );
        border-radius: 7px;
    }

    /* --- GROUP BOX --- */
    QGroupBox {
        background-color: #1e293b;
        border: 1px solid #2a3a5c;
        border-radius: 10px;
        margin-top: 16px;
        padding: 20px 16px 16px 16px;
        font-weight: 600;
        font-size: 13px;
        color: #94a3b8;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 12px;
        color: #3498db;
        font-weight: 600;
    }

    /* --- TAB WIDGET --- */
    QTabWidget::pane {
        background-color: #1e293b;
        border: 1px solid #2a3a5c;
        border-radius: 8px;
        padding: 8px;
    }

    QTabBar::tab {
        background-color: #0f172a;
        color: #64748b;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 2px;
    }

    QTabBar::tab:selected {
        background-color: #1e293b;
        color: #3498db;
        font-weight: 600;
    }

    QTabBar::tab:hover:!selected {
        background-color: #1a2332;
        color: #e2e8f0;
    }

    /* --- TOOLTIP --- */
    QToolTip {
        background-color: #1e293b;
        color: #e2e8f0;
        border: 1px solid #3498db;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }

    /* --- SEPARATOR --- */
    QFrame#separator {
        background-color: #2a3a5c;
        max-height: 1px;
        min-height: 1px;
    }

    /* --- NOTIFICATION BAR --- */
    QFrame#notification_success {
        background-color: #1e3f2e;
        border: 1px solid #2ecc71;
        border-radius: 8px;
        padding: 12px 16px;
    }

    QFrame#notification_error {
        background-color: #3f1e1e;
        border: 1px solid #e74c3c;
        border-radius: 8px;
        padding: 12px 16px;
    }

    QFrame#notification_info {
        background-color: #1e2a3f;
        border: 1px solid #3498db;
        border-radius: 8px;
        padding: 12px 16px;
    }
    """
