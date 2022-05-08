import math

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class QDMGraphicsScene(QGraphicsScene):
    itemSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()

    def __init__(self,scene, parent=None):
        super().__init__(parent)

        self.scene = scene
        # settings
        self.grid_size = 20
        self.grid_squares = 5

        self.color_background = QColor('#393939')
        self.color_light = QColor('#2f2f2f')
        self.color_dark = QColor('#292929')

        self._pen_light = QPen(self.color_light)
        self._pen_light.setWidth(1)

        self._pen_dark = QPen(self.color_dark)
        self._pen_dark.setWidth(2)

        #self.scene_width, self.scene_height = 64000, 64000


        self.setBackgroundBrush(self.color_background)

    # drag event wount be allowed until drag event is overridden
    def dragMoveEvent(self, event):
        pass

    def setGrScene(self,width,height):
        self.setSceneRect(-width // 2, -height // 2, width, height)


    def drawBackground(self, painter, rect, ):
        super().drawBackground(painter, rect)

        # create grid
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            if (x % (self.grid_size * self.grid_squares) != 0):
                lines_light.append(QLine(x, top, x, bottom))
            else:
                lines_dark.append(QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.grid_size):
            if (y % (self.grid_size * self.grid_squares) != 0):
                lines_light.append(QLine(left, y, right, y))
            else:
                lines_dark.append(QLine(left, y, right, y))

        # draw lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)
