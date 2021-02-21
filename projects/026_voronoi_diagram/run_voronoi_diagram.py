"""
base VoronoiDiagram
"""
import random

import math
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect
from PySide2.QtGui import QColor
from PySide2.QtGui import QPen
from PySide2.QtGui import QVector2D


class VoronoiDiagram:
    def __init__(self, width, height, total_points=20):
        self.width = width
        self.height = height
        self.total_points = total_points
        self.points = []
        self.colors = []
        self.rect = QRect()

    def generate(self):
        self.points = []
        self.colors = []
        for i in range(self.total_points):
            v = QVector2D(random.random(),
                          random.random())
            self.points.append(v)
            c = QColor(random.randint(0, 255), random.randint(0, 255),
                       random.randint(0, 255))
            self.colors.append(c)

    def get_closest_point(self, v):
        closest_length = 0
        is_first = True
        index = -1
        size_vector = QVector2D(self.width, self.height)

        for i, p in enumerate(self.points):
            length = (p * size_vector - v).length()
            if is_first:
                closest_length = length
                is_first = False
                index = i
                continue
            elif length < closest_length:
                closest_length = length
                index = i
        return index

    def paint(self, painter):

        chunk_x = float(self.rect.width()) / float(self.width)
        chunk_y = float(self.rect.height()) / float(self.height)
        size_vector = QVector2D(self.width, self.height)

        for y in range(self.height):
            for x in range(self.width):
                v = QVector2D(x, y)
                index = self.get_closest_point(v)
                c = self.colors[index]
                draw_x = math.floor(chunk_x * x)
                dray_y = math.floor(chunk_y * y)
                painter.setPen(QPen(c))
                painter.fillRect(draw_x, dray_y, math.ceil(chunk_x),
                                 math.ceil(chunk_y), c)

        painter.setPen(QPen(QColor(100, 100, 100)))
        for v in self.points:
            painter.drawRect(v.x() * size_vector.x() * chunk_x,
                             v.y() * size_vector.y() * chunk_y, 2, 2)


class VoronoiDiagramDemoWidget(QtWidgets.QWidget):
    """
    VoronoiDiagram
    """

    def __init__(self):
        super(VoronoiDiagramDemoWidget, self).__init__()
        self.setWindowTitle("VoronoiDiagram")

        self.voronoi = VoronoiDiagram(100, 100)

    def resizeEvent(self, event):
        self.voronoi.rect = self.rect()

    def showEvent(self, event):
        self.voronoi.rect = self.rect()
        self.voronoi.generate()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.voronoi.width *= 2
            self.voronoi.height *= 2
            self.update()
        if event.key() == QtCore.Qt.Key_Down:
            self.voronoi.width /= 2
            self.voronoi.height /= 2
            self.update()
        if event.key() == QtCore.Qt.Key_Left:
            self.voronoi.total_points /= 2
            self.voronoi.generate()
            self.update()
        if event.key() == QtCore.Qt.Key_Right:
            self.voronoi.total_points *= 2
            self.voronoi.generate()
            self.update()
        if event.key() == QtCore.Qt.Key_Space:
            self.voronoi.generate()
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.voronoi.paint(painter)

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = VoronoiDiagramDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
