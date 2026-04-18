"""
BRN Reroll Analyzer – Automação Inteligente para ARK Survival Evolved
=====================================================================

Aplicação desktop profissional para automação de rerolls no ARK.
Detecta automaticamente o valor de Magic Find via OCR e para quando 
a meta é atingida.

Autor: BRN GROUP
Versão: 1.0.0
"""

import sys
import os

# Adicionar o diretório raiz ao PYTHONPATH
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.main_window import MainWindow


def main():
    """Ponto de entrada principal da aplicação."""
    # Habilitar High DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    
    # Configurar fonte padrão
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Configurar nome da aplicação
    app.setApplicationName("BRN Reroll Analyzer")
    app.setOrganizationName("BRN GROUP")
    app.setApplicationVersion("1.0.0")

    # Criar e exibir janela principal
    window = MainWindow()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
