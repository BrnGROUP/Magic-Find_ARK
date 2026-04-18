"""
BRN Reroll Analyzer - Tela de Histórico
Lista os melhores rolls encontrados com data/hora, exportação CSV e filtragem.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class HistoryPage(QWidget):
    """Página de histórico com tabela de resultados e exportação."""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.setup_ui()
        self.load_history()

    def setup_ui(self):
        """Constrói a interface do histórico."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(20)

        # === HEADER ===
        header = QHBoxLayout()

        title_layout = QVBoxLayout()
        title = QLabel("Histórico de Rolls")
        title.setObjectName("title")
        title_layout.addWidget(title)
        subtitle = QLabel("Registro de todos os valores de Magic Find detectados")
        subtitle.setObjectName("subtitle")
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)
        header.addStretch()

        main_layout.addLayout(header)

        # === STATS CARDS ===
        stats_frame = QFrame()
        stats_frame.setObjectName("card")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(20, 16, 20, 16)
        stats_layout.setSpacing(32)

        # Total rolls
        total_layout = QVBoxLayout()
        self.total_label_title = QLabel("TOTAL DE REGISTROS")
        self.total_label_title.setObjectName("card_title")
        total_layout.addWidget(self.total_label_title)
        self.total_label = QLabel("0")
        self.total_label.setStyleSheet("color: #3498db; font-size: 24px; font-weight: 700;")
        total_layout.addWidget(self.total_label)
        stats_layout.addLayout(total_layout)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet("color: #2a3a5c;")
        stats_layout.addWidget(sep1)

        # Best value
        best_layout = QVBoxLayout()
        self.best_label_title = QLabel("MELHOR VALOR")
        self.best_label_title.setObjectName("card_title")
        best_layout.addWidget(self.best_label_title)
        self.best_label = QLabel("—")
        self.best_label.setStyleSheet("color: #f39c12; font-size: 24px; font-weight: 700;")
        best_layout.addWidget(self.best_label)
        stats_layout.addLayout(best_layout)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #2a3a5c;")
        stats_layout.addWidget(sep2)

        # Average
        avg_layout = QVBoxLayout()
        self.avg_label_title = QLabel("MÉDIA")
        self.avg_label_title.setObjectName("card_title")
        avg_layout.addWidget(self.avg_label_title)
        self.avg_label = QLabel("—")
        self.avg_label.setStyleSheet("color: #2ecc71; font-size: 24px; font-weight: 700;")
        avg_layout.addWidget(self.avg_label)
        stats_layout.addLayout(avg_layout)

        stats_layout.addStretch()
        main_layout.addWidget(stats_frame)

        # === ACTION BUTTONS ===
        actions = QHBoxLayout()
        actions.setSpacing(12)

        btn_refresh = QPushButton("🔄 Atualizar")
        btn_refresh.setObjectName("btn_secondary")
        btn_refresh.clicked.connect(self.load_history)
        actions.addWidget(btn_refresh)

        btn_export = QPushButton("📥 Exportar CSV")
        btn_export.clicked.connect(self.export_csv)
        actions.addWidget(btn_export)

        btn_clear = QPushButton("🗑️ Limpar Histórico")
        btn_clear.setObjectName("btn_danger")
        btn_clear.clicked.connect(self.clear_history)
        actions.addWidget(btn_clear)

        actions.addStretch()
        main_layout.addLayout(actions)

        # === TABLE ===
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["#", "Data / Hora", "Magic Find (%)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 60)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        main_layout.addWidget(self.table, stretch=1)

    def load_history(self):
        """Carrega o histórico do ConfigManager para a tabela."""
        history = self.config.get_history()
        
        # Ordenar por valor decrescente (melhores primeiro)
        sorted_history = sorted(history, key=lambda x: x.get("value", 0), reverse=True)

        self.table.setRowCount(len(sorted_history))

        best_value = 0
        total_value = 0

        for row, entry in enumerate(sorted_history):
            value = entry.get("value", 0)
            timestamp = entry.get("timestamp", "—")

            # Coluna #
            idx_item = QTableWidgetItem(str(row + 1))
            idx_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, idx_item)

            # Coluna Data/Hora
            time_item = QTableWidgetItem(timestamp)
            time_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, time_item)

            # Coluna Magic Find
            value_item = QTableWidgetItem(f"{value:.1f}%")
            value_item.setTextAlignment(Qt.AlignCenter)
            
            # Colorir valores altos
            if value >= self.config.get_min_magic_find():
                value_item.setForeground(QColor("#2ecc71"))
                value_item.setFont(QFont("Segoe UI", 13, QFont.Bold))
            elif value >= self.config.get_min_magic_find() * 0.7:
                value_item.setForeground(QColor("#f39c12"))
            else:
                value_item.setForeground(QColor("#e2e8f0"))

            self.table.setItem(row, 2, value_item)

            # Stats
            if value > best_value:
                best_value = value
            total_value += value

        # Atualizar estatísticas
        count = len(sorted_history)
        self.total_label.setText(str(count))
        self.best_label.setText(f"{best_value:.1f}%" if count > 0 else "—")
        self.avg_label.setText(f"{total_value/count:.1f}%" if count > 0 else "—")

    def export_csv(self):
        """Exporta o histórico para um arquivo CSV."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exportar Histórico",
            "brn_historico.csv",
            "CSV (*.csv)"
        )
        if filepath:
            success = self.config.export_history_csv(filepath)
            if success:
                QMessageBox.information(
                    self, "Exportação",
                    f"✅ Histórico exportado com sucesso!\n\n{filepath}",
                    QMessageBox.Ok
                )
            else:
                QMessageBox.warning(
                    self, "Erro",
                    "❌ Erro ao exportar histórico.",
                    QMessageBox.Ok
                )

    def clear_history(self):
        """Limpa todo o histórico após confirmação."""
        reply = QMessageBox.question(
            self, "Confirmar",
            "⚠️ Deseja limpar todo o histórico?\nEsta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config.clear_history()
            self.load_history()
            QMessageBox.information(self, "Sucesso", "Histórico limpo!")
