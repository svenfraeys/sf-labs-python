import math
import random
from PySide2 import QtGui, QtWidgets, QtCore
import sfwidgets.marchingsquares


class MarchingSquaresDemoWidget(QtWidgets.QWidget):
    """marching squares demo
    """

    def __init__(self):
        super(MarchingSquaresDemoWidget, self).__init__()
        self.setWindowTitle("Marching Squares")
        self.points = []
        self.total_points = 200
        self.marching_squares = sfwidgets.marchingsquares.MarchingSquares()
        self.marching_squares.subdiv_x = 20
        self.marching_squares.subdiv_y = 20
        self._generate_points()
        self.mcp = sfwidgets.marchingsquares.MarchingCellsPainter()

    def _generate_points(self):
        self.points = []
        midpoint = QtGui.QVector2D(self.width() / 2, self.height() / 2)
        for i in range(self.total_points):
            progress = float(i) / float(self.total_points)
            x = random.random() * self.width()
            y = random.random() * self.height()
            v = QtGui.QVector2D(x, y)

            distance = v - midpoint
            add = (distance * -1) * (float(progress) * float(progress))
            v += add

            p = QtCore.QPointF(v.x() + math.sin(x) * 20.0, v.y())
            self.points.append(p)

    def showEvent(self, event):
        self.start()

    def start(self):
        self.marching_squares.rect = QtCore.QRectF(0, 0, self.width(),
                                                   self.height())
        self.marching_squares.points = self.points
        self.marching_squares.calculate_grid()
        self.marching_squares.calculate_points()
        self.update()

    def resizeEvent(self, event):
        self.marching_squares.rect = QtCore.QRectF(0, 0, self.width(),
                                                   self.height())
        self.marching_squares.calculate_grid()
        self.update()

    def mouseReleaseEvent(self, event):
        self._generate_points()
        self.start()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.marching_squares.subdiv_x += 2
            self.marching_squares.subdiv_y += 2
            self.start()
        if event.key() == QtCore.Qt.Key_Down:
            self.marching_squares.subdiv_x -= 2
            self.marching_squares.subdiv_y -= 2
            self.start()

        if event.key() == QtCore.Qt.Key_H:
            self.mcp.show_grid = not self.mcp.show_grid
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(20, 100, 220))
        painter.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(20, 100, 220))
        painter.setBrush(brush)

        for point in self.points:
            painter.drawRect(point.x() - 1, point.y() - 1, 2, 2)

        brush = QtGui.QBrush()
        painter.setBrush(brush)
        self.mcp.painter = painter
        self.mcp.mc = self.marching_squares
        self.mcp.paint_grid()
        self.mcp.painter = None


def main():
    app = QtWidgets.QApplication([])
    w = MarchingSquaresDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
