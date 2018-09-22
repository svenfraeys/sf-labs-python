import math
import random
from PySide2 import QtGui, QtWidgets, QtCore
import sfwidgets.marchingsquares
import sfwidgets.quadtree


class MarchingQuadtreeCell(sfwidgets.marchingsquares.Cell):
    """customized cell for the marching squares
    """

    def __init__(self, mc, quad):
        super(MarchingQuadtreeCell, self).__init__(mc, 0, 0, quad.boundingbox)
        self.quad = quad
        self.mapper = {}

    def top(self):
        topquad = self.quad.top()
        if not topquad:
            return

        if topquad in self.mapper:
            return self.mapper[topquad]

        return None

    def left(self):
        quad = self.quad.left()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None

    def right(self):
        quad = self.quad.right()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None

    def bottom(self):
        quad = self.quad.bottom()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None

    def bottomleft(self):
        quad = self.quad.bottomleft()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None

    def bottomright(self):
        quad = self.quad.bottomright()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None

    def topleft(self):
        quad = self.quad.topleft()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None

    def topright(self):
        quad = self.quad.topright()
        if not quad:
            return

        if quad in self.mapper:
            return self.mapper[quad]

        return None


class MarchingQuadtreePainter(object):
    def __init__(self, painter, marchingquadtree):
        self.painter = painter
        self.marchingquadtree = marchingquadtree
        self.mcp = sfwidgets.marchingsquares.MarchingCellsPainter()

    def paint(self):
        sfwidgets.quadtree.paint_quad_tree(self.painter,
                                           self.marchingquadtree.quadtree)

        self.mcp.painter = self.painter
        for r in self.marchingquadtree.marching_squares.grid:
            for c in r:
                self.mcp.paint_cell(c)

        self.mcp.painter = None


class MarchingQuadtree(object):
    """marching squares quad tree
    """

    def __init__(self):
        self.__points = []
        self.marching_squares = sfwidgets.marchingsquares.MarchingSquares()
        self.quadtree = sfwidgets.quadtree.Quadtree()
        self.mapper = {}

    @property
    def rect(self):
        return self.marching_squares.rect

    @rect.setter
    def rect(self, value):
        self.marching_squares.rect = value
        self.quadtree.boundingbox = value

    @property
    def capacity(self):
        return self.quadtree.capacity

    @capacity.setter
    def capacity(self, value):
        self.quadtree.capacity = value

    @property
    def points(self):
        return self.__points

    @points.setter
    def points(self, value):
        self.__points = value
        self.marching_squares.points = value

    def calculate_grid(self):
        self.quadtree.reset()
        for p in self.points:
            self.quadtree.insert(p)

    def __quadtree_to_cells(self):
        """return the quadtree as cells
        """
        leafs = self.quadtree.leafs()
        print leafs

    def __quadtree_to_grid(self):
        leafs = self.quadtree.leafs()
        data = []

        for leaf in leafs:
            c = MarchingQuadtreeCell(self.marching_squares, leaf)
            c.mapper = self.mapper
            data.append(c)
            self.mapper[leaf] = c
        grid = [data]
        return grid

    def calculate_points(self):
        grid = self.__quadtree_to_grid()
        self.marching_squares.grid = grid
        self.marching_squares.calculate_points()


class MarchingQuadtreeDemoWidget(QtWidgets.QWidget):
    """marching squares demo
    """

    def __init__(self):
        super(MarchingQuadtreeDemoWidget, self).__init__()
        self.setWindowTitle("Marching Squares")
        self.points = []
        self.total_points = 200

        self.marching_squares = MarchingQuadtree()
        self._generate_points()
        self.mcp = sfwidgets.marchingsquares.MarchingCellsPainter()
        self.label = QtWidgets.QLabel(self)
        self.label.resize(150, 20)
        self.label.setStyleSheet("QLabel { background-color : white;}")
        self.label.move(QtCore.QPoint(10, 10))

    def _generate_points(self):
        self.points = []
        midpoint = QtGui.QVector2D(self.width() / 2, self.height() / 2)
        for i in range(self.total_points):
            progress = float(i) / float(self.total_points)
            x = random.random() * self.width()
            y = random.random() * self.height()
            v = QtGui.QVector2D(x, y)

            distance = v - midpoint
            add = (distance * -1) * (float(progress) ** 3)
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
        self.label.setText(
            " points: {}".format(len(self.points)))
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
            self.marching_squares.capacity /= 2
            self.start()
        if event.key() == QtCore.Qt.Key_Down:
            self.marching_squares.capacity *= 2
            self.start()

        if event.key() == QtCore.Qt.Key_Left:
            self.total_points /= 2
            self._generate_points()
            self.start()
        if event.key() == QtCore.Qt.Key_Right:
            self.total_points *= 2
            self._generate_points()
            self.start()

        if event.key() == QtCore.Qt.Key_H:
            self.mcp.show_grid = not self.mcp.show_grid
            self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        pcolor = 150
        pen = QtGui.QPen(QtGui.QColor(pcolor, pcolor, pcolor))
        painter.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(pcolor, pcolor, pcolor))
        painter.setBrush(brush)

        for point in self.points:
            painter.drawRect(point.x() - 1, point.y() - 1, 2, 2)

        brush = QtGui.QBrush()
        painter.setBrush(brush)
        self.mcp.painter = painter
        # self.mcp.mc = self.marching_squares
        self.mcp.paint_grid()
        self.mcp.painter = None

        p = MarchingQuadtreePainter(painter, self.marching_squares)
        p.paint()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    w = MarchingQuadtreeDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
