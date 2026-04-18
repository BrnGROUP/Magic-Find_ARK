"""
BRN Reroll Analyzer - Seletor Visual de Região
Overlay transparente que permite ao usuário desenhar um retângulo na tela
para definir a região de captura.
"""

from PyQt5.QtWidgets import QWidget, QApplication, QLabel
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QCursor


class RegionSelector(QWidget):
    """
    Overlay transparente fullscreen que permite desenhar um retângulo.
    O usuário clica e arrasta para selecionar a região de captura.
    """

    # Sinal emitido quando a região é selecionada: (x1, y1, x2, y2)
    region_selected = pyqtSignal(int, int, int, int)
    selection_cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Configurar janela fullscreen transparente
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.CrossCursor)

        # Estado de desenho
        self._drawing = False
        self._start_point = QPoint()
        self._end_point = QPoint()
        self._current_rect = QRect()

        # Ocupar todas as telas
        screen = QApplication.primaryScreen()
        if screen:
            # Usar geometria virtual para cobrir múltiplas telas
            try:
                virtual = screen.virtualGeometry()
            except AttributeError:
                virtual = screen.geometry()
            self.setGeometry(virtual)
        
        self.showFullScreen()

    def paintEvent(self, event):
        """Desenha o overlay escuro com a região selecionada destacada."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fundo semi-transparente escuro
        overlay_color = QColor(0, 0, 0, 120)
        painter.fillRect(self.rect(), overlay_color)

        # Instruções no topo
        painter.setPen(QPen(QColor(255, 255, 255, 220)))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        painter.drawText(
            self.rect().adjusted(0, 40, 0, 0),
            Qt.AlignHCenter | Qt.AlignTop,
            "🎯 Clique e arraste para selecionar a região de captura"
        )
        
        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QPen(QColor(200, 200, 200, 180)))
        painter.drawText(
            self.rect().adjusted(0, 75, 0, 0),
            Qt.AlignHCenter | Qt.AlignTop,
            "Pressione ESC para cancelar"
        )

        # Desenhar retângulo selecionado
        if not self._current_rect.isNull() and self._current_rect.width() > 2:
            # Limpar a área selecionada (remover overlay escuro)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(self._current_rect, Qt.transparent)
            
            # Voltar ao modo normal
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # Borda da seleção
            pen = QPen(QColor(52, 152, 219), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self._current_rect)

            # Cantos destacados
            corner_size = 12
            corner_pen = QPen(QColor(46, 204, 113), 3)
            painter.setPen(corner_pen)
            r = self._current_rect
            
            # Canto superior esquerdo
            painter.drawLine(r.topLeft(), r.topLeft() + QPoint(corner_size, 0))
            painter.drawLine(r.topLeft(), r.topLeft() + QPoint(0, corner_size))
            # Canto superior direito
            painter.drawLine(r.topRight(), r.topRight() + QPoint(-corner_size, 0))
            painter.drawLine(r.topRight(), r.topRight() + QPoint(0, corner_size))
            # Canto inferior esquerdo
            painter.drawLine(r.bottomLeft(), r.bottomLeft() + QPoint(corner_size, 0))
            painter.drawLine(r.bottomLeft(), r.bottomLeft() + QPoint(0, -corner_size))
            # Canto inferior direito
            painter.drawLine(r.bottomRight(), r.bottomRight() + QPoint(-corner_size, 0))
            painter.drawLine(r.bottomRight(), r.bottomRight() + QPoint(0, -corner_size))

            # Dimensões
            width = abs(self._current_rect.width())
            height = abs(self._current_rect.height())
            size_text = f"{width} × {height} px"
            
            painter.setPen(QPen(QColor(255, 255, 255, 220)))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            
            # Posição do texto de dimensões (abaixo do retângulo)
            text_x = self._current_rect.center().x() - 50
            text_y = self._current_rect.bottom() + 25
            
            # Fundo do texto
            text_rect = QRect(text_x - 8, text_y - 14, 116, 24)
            painter.fillRect(text_rect, QColor(30, 41, 59, 200))
            painter.drawText(text_rect, Qt.AlignCenter, size_text)

            # Coordenadas
            coord_text = f"({r.left()}, {r.top()}) → ({r.right()}, {r.bottom()})"
            painter.setFont(QFont("Segoe UI", 10))
            painter.setPen(QPen(QColor(148, 163, 184, 200)))
            coord_rect = QRect(text_x - 30, text_y + 12, 176, 20)
            painter.drawText(coord_rect, Qt.AlignCenter, coord_text)

        painter.end()

    def mousePressEvent(self, event):
        """Início da seleção."""
        if event.button() == Qt.LeftButton:
            self._drawing = True
            self._start_point = event.globalPos()
            self._end_point = event.globalPos()
            self._current_rect = QRect()

    def mouseMoveEvent(self, event):
        """Atualiza o retângulo durante o arrasto."""
        if self._drawing:
            self._end_point = event.globalPos()
            self._current_rect = QRect(self._start_point, self._end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        """Finaliza a seleção."""
        if event.button() == Qt.LeftButton and self._drawing:
            self._drawing = False
            self._end_point = event.globalPos()
            self._current_rect = QRect(self._start_point, self._end_point).normalized()
            
            # Só aceitar se a região for grande o suficiente
            if self._current_rect.width() > 10 and self._current_rect.height() > 10:
                x1 = self._current_rect.left()
                y1 = self._current_rect.top()
                x2 = self._current_rect.right()
                y2 = self._current_rect.bottom()
                
                self.region_selected.emit(x1, y1, x2, y2)
                self.close()
            else:
                self.update()

    def keyPressEvent(self, event):
        """ESC cancela a seleção."""
        if event.key() == Qt.Key_Escape:
            self.selection_cancelled.emit()
            self.close()


class PositionPicker(QWidget):
    """
    Overlay para capturar posição do mouse com contagem regressiva.
    Mostra a posição em tempo real e confirma com clique.
    """

    position_selected = pyqtSignal(int, int)
    selection_cancelled = pyqtSignal()

    def __init__(self, label_text="Clique na posição desejada", parent=None):
        super().__init__(parent)
        self.label_text = label_text

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.CrossCursor)

        screen = QApplication.primaryScreen()
        if screen:
            try:
                virtual = screen.virtualGeometry()
            except AttributeError:
                virtual = screen.geometry()
            self.setGeometry(virtual)

        self._mouse_pos = QPoint()
        self.setMouseTracking(True)
        self.showFullScreen()

    def paintEvent(self, event):
        """Desenha o overlay com crosshair."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fundo semi-transparente (mais leve)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 60))

        # Instruções
        painter.setPen(QPen(QColor(255, 255, 255, 240)))
        painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
        
        # Fundo da instrução
        text_bg = QRect(self.width() // 2 - 250, 30, 500, 70)
        painter.fillRect(text_bg, QColor(15, 23, 42, 220))
        painter.drawText(text_bg, Qt.AlignCenter, f"🎯 {self.label_text}")
        
        painter.setFont(QFont("Segoe UI", 11))
        painter.setPen(QPen(QColor(200, 200, 200, 200)))
        esc_rect = QRect(self.width() // 2 - 100, 85, 200, 25)
        painter.drawText(esc_rect, Qt.AlignCenter, "ESC para cancelar")

        # Crosshair no mouse
        if not self._mouse_pos.isNull():
            mx, my = self._mouse_pos.x(), self._mouse_pos.y()
            
            # Linhas cruzadas
            cross_pen = QPen(QColor(52, 152, 219, 180), 1, Qt.DashLine)
            painter.setPen(cross_pen)
            painter.drawLine(mx, 0, mx, self.height())
            painter.drawLine(0, my, self.width(), my)

            # Círculo central
            painter.setPen(QPen(QColor(46, 204, 113), 2))
            painter.drawEllipse(QPoint(mx, my), 15, 15)
            painter.drawEllipse(QPoint(mx, my), 3, 3)

            # Coordenadas perto do cursor
            coord_text = f"({mx}, {my})"
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.setPen(QPen(QColor(255, 255, 255, 240)))
            
            label_rect = QRect(mx + 20, my + 20, 120, 28)
            painter.fillRect(label_rect, QColor(15, 23, 42, 220))
            painter.drawText(label_rect, Qt.AlignCenter, coord_text)

        painter.end()

    def mouseMoveEvent(self, event):
        """Rastreia posição do mouse."""
        self._mouse_pos = event.globalPos()
        self.update()

    def mousePressEvent(self, event):
        """Confirma a posição com clique."""
        if event.button() == Qt.LeftButton:
            pos = event.globalPos()
            self.position_selected.emit(pos.x(), pos.y())
            self.close()

    def keyPressEvent(self, event):
        """ESC cancela."""
        if event.key() == Qt.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
