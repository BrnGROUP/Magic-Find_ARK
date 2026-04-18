"""
BRN Reroll Analyzer - Janela Principal
Janela principal com sidebar de navegação e área de conteúdo dinâmica.
"""

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame,
    QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from ui.styles import get_stylesheet
from ui.dashboard import DashboardPage
from ui.settings import SettingsPage
from ui.automation import AutomationPage
from ui.history import HistoryPage
from core.config_manager import ConfigManager


class MainWindow(QMainWindow):
    """Janela principal do BRN Reroll Analyzer."""

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.setWindowTitle("BRN Reroll Analyzer – ARK Survival Evolved")
        self.setMinimumSize(1000, 680)
        self.resize(1280, 800)
        
        # Aplicar stylesheet
        self.setStyleSheet(get_stylesheet())

        self.setup_ui()
        self.show()

    def setup_ui(self):
        """Constrói a interface principal com sidebar e área de conteúdo."""
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === SIDEBAR ===
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(16, 24, 16, 8)
        logo_layout.setSpacing(2)

        logo_label = QLabel("⚡ BRN REROLL")
        logo_label.setObjectName("logo_label")
        logo_layout.addWidget(logo_label)

        subtitle_label = QLabel("Reroll Automation Tool")
        subtitle_label.setObjectName("subtitle_label")
        logo_layout.addWidget(subtitle_label)

        sidebar_layout.addWidget(logo_container)

        # Separator
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        sidebar_layout.addWidget(sep)

        # Spacer
        sidebar_layout.addSpacing(12)

        # Menu buttons
        self.nav_buttons = []

        nav_items = [
            ("📊", "Dashboard"),
            ("🤖", "Automação"),
            ("⚙️", "Configurações"),
            ("📋", "Histórico"),
        ]

        for icon, text in nav_items:
            btn = QPushButton(f"  {icon}   {text}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("Segoe UI", 12))
            btn.clicked.connect(lambda checked, t=text: self._navigate(t))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # Footer do sidebar
        footer_container = QWidget()
        footer_layout = QVBoxLayout(footer_container)
        footer_layout.setContentsMargins(16, 8, 16, 16)
        footer_layout.setSpacing(4)

        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.HLine)
        footer_layout.addWidget(sep2)

        footer_layout.addSpacing(8)

        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #475569; font-size: 11px;")
        version_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(version_label)

        credit_label = QLabel("by BRN GROUP")
        credit_label.setStyleSheet("color: #3498db; font-size: 10px; font-weight: 600;")
        credit_label.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(credit_label)

        sidebar_layout.addWidget(footer_container)

        main_layout.addWidget(sidebar)

        # === CONTENT AREA ===
        self.stack = QStackedWidget()

        # Criar páginas
        self.dashboard_page = DashboardPage()
        self.automation_page = AutomationPage(self.config, self.dashboard_page)
        self.settings_page = SettingsPage(self.config)
        self.history_page = HistoryPage(self.config)

        # Conectar sinais
        self.settings_page.settings_saved.connect(self._on_settings_saved)

        # Adicionar páginas ao stack
        self.stack.addWidget(self.dashboard_page)    # 0
        self.stack.addWidget(self.automation_page)    # 1
        self.stack.addWidget(self.settings_page)      # 2
        self.stack.addWidget(self.history_page)       # 3

        main_layout.addWidget(self.stack, stretch=1)

        # Selecionar Dashboard por padrão
        self._navigate("Dashboard")

    def _navigate(self, page_name):
        """Navega para a página selecionada."""
        page_map = {
            "Dashboard": 0,
            "Automação": 1,
            "Configurações": 2,
            "Histórico": 3,
        }

        index = page_map.get(page_name, 0)
        self.stack.setCurrentIndex(index)

        # Atualizar botões
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # Atualizar dados quando navegar para histórico
        if page_name == "Histórico":
            self.history_page.load_history()

        # Atualizar meta no dashboard quando navegar
        if page_name == "Dashboard":
            self.dashboard_page.update_target(self.config.get_min_magic_find())

    def _on_settings_saved(self):
        """Callback quando configurações são salvas."""
        self.dashboard_page.update_target(self.config.get_min_magic_find())

    def closeEvent(self, event):
        """Garantir que a automação pare ao fechar a janela."""
        if (self.automation_page.worker 
                and self.automation_page.worker.is_running()):
            self.automation_page.stop_automation()
            # Aguardar thread finalizar
            if self.automation_page.thread:
                self.automation_page.thread.quit()
                self.automation_page.thread.wait(3000)
        event.accept()
