import random

import math
from PySide2 import QtWidgets, QtCore, QtGui
import quadtree


class QuadTreeDemoWidget(QtWidgets.QWidget):
    def __init__(self):
        super(QuadTreeDemoWidget, self).__init__()
        self.setWindowTitle('Quadtree')
        self.total_points = 800
        self.selected_quad = None
        self.points = []
        layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("points")
        self.label.setStyleSheet("QLabel { background-color : white;}")
        self.setLayout(layout)
        self.quadtree = quadtree.Quadtree(QtCore.QRectF())
        quadtree.Quadtree.capacity = 200
        layout.addWidget(self.label)
        layout.addStretch()

        self.update_label()

    def generate_points(self):
        self.points = []
        midpoint = QtGui.QVector2D(self.width() / 2, self.height() / 2)
        for i in range(int(self.total_points)):
            progress = float(i) / float(self.total_points)
            x = random.random() * self.width()
            y = random.random() * self.height()
            v = QtGui.QVector2D(x, y)

            distance = v - midpoint
            add = (distance * -1) * (float(progress) * float(progress))
            v += add

            p = QtCore.QPointF(v.x() + math.sin(x) * 20.0, v.y())
            self.points.append(p)

    def generate_quadtree(self):
        self.quadtree = quadtree.Quadtree(
            QtCore.QRectF(0, 0, self.width(), self.height()))
        for p in self.points:
            self.quadtree.insert(p)

    def update_label(self):
        self.label.setText(
            "points: {} | capacity: {}".format(
                self.total_points, quadtree.Quadtree.capacity))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(20, 100, 220))
        painter.setPen(pen)
        brush = QtGui.QBrush(QtGui.QColor(20, 100, 220))
        painter.setBrush(brush)

        for point in self.points:
            painter.drawRect(point.x() - 1, point.y() - 1, 2, 2)

        pen = QtGui.QPen(QtGui.QColor(10, 50, 110))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(QtGui.QBrush())

        if self.quadtree:
            quadtree.paint_quad_tree(painter, self.quadtree)

        if self.selected_quad:
            p = QtGui.QPen()
            p.setWidth(3)
            painter.setPen(p)
            painter.setBrush(QtGui.QBrush())
            painter.drawRect(self.selected_quad.boundingbox)
            l = self.selected_quad.left()
            if l:
                painter.drawRect(l.boundingbox)
            r = self.selected_quad.right()
            if r:
                painter.drawRect(r.boundingbox)

            b = self.selected_quad.bottom()
            if b:
                painter.drawRect(b.boundingbox)

            t = self.selected_quad.top()
            if t:
                painter.drawRect(t.boundingbox)

            p = QtGui.QPen(QtGui.QColor(200, 0, 0))
            p.setWidth(2)
            painter.setPen(p)

            tl = self.selected_quad.topleft()
            if tl:
                painter.drawRect(tl.boundingbox)

            tr = self.selected_quad.topright()
            if tr:
                painter.drawRect(tr.boundingbox)

            bl = self.selected_quad.bottomleft()
            if bl:
                painter.drawRect(bl.boundingbox)

            br = self.selected_quad.bottomright()
            if br:
                painter.drawRect(br.boundingbox)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def showEvent(self, event):
        self.generate_points()
        self.generate_quadtree()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.selected_quad = self.quadtree.nearest_quad(event.pos())
            self.update()
            # self.total_points *= 2
        if event.button() == QtCore.Qt.RightButton:
            self.selected_quad = None
            self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Right:
            self.selected_quad = None
            self.total_points *= 2
            self.generate_points()
            self.generate_quadtree()
            self.update_label()
            self.update()
        if event.key() == QtCore.Qt.Key_Left:
            self.selected_quad = None
            self.total_points /= 2
            self.generate_points()
            self.generate_quadtree()
            self.update_label()
            self.update()
        if event.key() == QtCore.Qt.Key_Up:
            self.selected_quad = None
            quadtree.Quadtree.capacity *= 2
            self.generate_quadtree()
            self.update()
            self.update_label()
        if event.key() == QtCore.Qt.Key_Down:
            self.selected_quad = None
            res = quadtree.Quadtree.capacity / 2
            if res > 0:
                quadtree.Quadtree.capacity = res
            self.generate_quadtree()
            self.update()
            self.update_label()


def main():
    app = QtWidgets.QApplication([])
    w = QuadTreeDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
