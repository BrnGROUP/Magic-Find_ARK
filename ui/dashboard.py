"""
BRN Reroll Analyzer - Tela Dashboard
Exibe visão geral do sistema: status, estatísticas em cards, indicadores em tempo real.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QProgressBar, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont


class StatCard(QFrame):
    """Card de estatística individual com ícone, título e valor."""

    def __init__(self, icon, title, value="—", value_style="card_value", parent=None):
        super().__init__(parent)
        self.setObjectName("card_stat")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Header com ícone e título
        header = QHBoxLayout()
        header.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.addWidget(icon_label)
        header.addStretch()
        layout.addLayout(header)

        # Título
        self.title_label = QLabel(title)
        self.title_label.setObjectName("card_title")
        layout.addWidget(self.title_label)

        # Valor
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName(value_style)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        """Atualiza o valor exibido no card."""
        self.value_label.setText(str(value))

    def set_style(self, style_name):
        """Altera o estilo do valor."""
        self.value_label.setObjectName(style_name)
        self.value_label.setStyleSheet(self.value_label.styleSheet())


class DashboardPage(QWidget):
    """Página principal do Dashboard com estatísticas e status em tempo real."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Constrói a interface do dashboard."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(24)

        # === HEADER ===
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        title = QLabel("Dashboard")
        title.setObjectName("title")
        header_layout.addWidget(title)

        subtitle = QLabel("Visão geral da automação em tempo real")
        subtitle.setObjectName("subtitle")
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # === STATUS BAR ===
        self.status_frame = QFrame()
        self.status_frame.setObjectName("card_highlight")
        status_layout = QHBoxLayout(self.status_frame)
        status_layout.setContentsMargins(20, 12, 20, 12)

        status_icon = QLabel("⚡")
        status_icon.setFont(QFont("Segoe UI Emoji", 16))
        status_layout.addWidget(status_icon)

        self.status_label = QLabel("Parado")
        self.status_label.setObjectName("status_stopped")
        self.status_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        elapsed_title = QLabel("Tempo:")
        elapsed_title.setObjectName("card_title")
        status_layout.addWidget(elapsed_title)

        self.elapsed_label = QLabel("00:00:00")
        self.elapsed_label.setFont(QFont("Cascadia Code", 16, QFont.Bold))
        self.elapsed_label.setStyleSheet("color: #3498db;")
        status_layout.addWidget(self.elapsed_label)

        main_layout.addWidget(self.status_frame)

        # === STATISTICS CARDS GRID ===
        cards_grid = QGridLayout()
        cards_grid.setSpacing(16)

        # Card 1: Status da Automação
        self.card_status = StatCard(
            "🎮", "STATUS", "🔴 Parado", "card_value_red"
        )
        cards_grid.addWidget(self.card_status, 0, 0)

        # Card 2: Último Magic Find
        self.card_last_mf = StatCard(
            "🔍", "ÚLTIMO MAGIC FIND", "—", "card_value_blue"
        )
        cards_grid.addWidget(self.card_last_mf, 0, 1)

        # Card 3: Melhor Valor Encontrado
        self.card_best_mf = StatCard(
            "🏆", "MELHOR VALOR", "—", "card_value_gold"
        )
        self.card_best_mf.setObjectName("card_success")
        cards_grid.addWidget(self.card_best_mf, 0, 2)

        # Card 4: Total de Rerolls
        self.card_rerolls = StatCard(
            "🔄", "TOTAL REROLLS", "0", "card_value"
        )
        cards_grid.addWidget(self.card_rerolls, 1, 0)

        # Card 5: Confiança OCR
        self.card_confidence = StatCard(
            "🎯", "CONFIANÇA OCR", "—", "card_value_blue"
        )
        cards_grid.addWidget(self.card_confidence, 1, 1)

        # Card 6: Meta
        self.card_target = StatCard(
            "🎪", "META", "≥ 30%", "card_value_green"
        )
        cards_grid.addWidget(self.card_target, 1, 2)

        main_layout.addLayout(cards_grid)

        # === PROGRESS BAR ===
        progress_frame = QFrame()
        progress_frame.setObjectName("card")
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 16, 20, 16)
        progress_layout.setSpacing(12)

        prog_header = QHBoxLayout()
        prog_title = QLabel("Progresso para Meta")
        prog_title.setObjectName("section_title")
        prog_header.addWidget(prog_title)

        self.prog_percent = QLabel("0%")
        self.prog_percent.setStyleSheet("color: #3498db; font-weight: 700; font-size: 16px;")
        prog_header.addWidget(self.prog_percent, alignment=Qt.AlignRight)

        progress_layout.addLayout(prog_header)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)

        main_layout.addWidget(progress_frame)

        # === RECENT ACTIVITY ===
        activity_frame = QFrame()
        activity_frame.setObjectName("card")
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setContentsMargins(20, 16, 20, 16)
        activity_layout.setSpacing(8)

        act_title = QLabel("📋 Atividade Recente")
        act_title.setObjectName("section_title")
        activity_layout.addWidget(act_title)

        self.activity_labels = []
        for i in range(5):
            label = QLabel("—")
            label.setStyleSheet(
                "color: #64748b; font-size: 12px; padding: 4px 0; "
                "border-bottom: 1px solid #1a1a2e;"
            )
            activity_layout.addWidget(label)
            self.activity_labels.append(label)

        main_layout.addWidget(activity_frame)
        main_layout.addStretch()

    # --- Métodos de atualização ---

    def update_status(self, status_text):
        """Atualiza o status da automação."""
        self.status_label.setText(status_text)
        if "Rodando" in status_text:
            self.status_label.setObjectName("status_running")
            self.card_status.set_value("🟢 Rodando")
            self.status_frame.setObjectName("card_success")
        elif "Pausado" in status_text:
            self.card_status.set_value("⏸️ Pausado")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: 600; font-size: 14px;")
        else:
            self.status_label.setObjectName("status_stopped")
            self.card_status.set_value("🔴 Parado")
            self.status_frame.setObjectName("card_highlight")
        
        # Forçar re-aplicação de estilo
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_frame.style().unpolish(self.status_frame)
        self.status_frame.style().polish(self.status_frame)

    def update_last_magic_find(self, value):
        """Atualiza o último valor de Magic Find detectado."""
        self.card_last_mf.set_value(f"{value:.1f}%")

    def update_best_value(self, value):
        """Atualiza o melhor valor encontrado."""
        self.card_best_mf.set_value(f"{value:.1f}%")

    def update_reroll_count(self, count):
        """Atualiza o total de rerolls."""
        self.card_rerolls.set_value(str(count))

    def update_elapsed_time(self, time_str):
        """Atualiza o tempo decorrido."""
        self.elapsed_label.setText(time_str)

    def update_confidence(self, confidence):
        """Atualiza a confiança do OCR."""
        self.card_confidence.set_value(f"{confidence:.0f}%")

    def update_target(self, target_value):
        """Atualiza a meta exibida."""
        self.card_target.set_value(f"≥ {target_value:.0f}%")

    def update_progress(self, current_value, target_value):
        """Atualiza a barra de progresso."""
        if target_value > 0:
            percent = min(100, int((current_value / target_value) * 100))
        else:
            percent = 0
        self.progress_bar.setValue(percent)
        self.prog_percent.setText(f"{percent}%")

    def add_activity(self, message):
        """Adiciona uma mensagem à atividade recente (máximo 5)."""
        # Shift existing messages
        for i in range(len(self.activity_labels) - 1, 0, -1):
            self.activity_labels[i].setText(self.activity_labels[i-1].text())
        
        if self.activity_labels:
            self.activity_labels[0].setText(message)
            self.activity_labels[0].setStyleSheet(
                "color: #e2e8f0; font-size: 12px; padding: 4px 0; "
                "border-bottom: 1px solid #1a1a2e;"
            )
