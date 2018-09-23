from PySide2 import QtGui, QtCore, QtWidgets
import random
import sfwidgets.treecolonization


def generate_points(rect, total):
    points = []
    for i in range(total):
        x = rect.topLeft().x() + random.random() * rect.width()
        y = rect.topLeft().y() + random.random() * rect.height()
        v = QtGui.QVector2D(x, y)
        points.append(v)
    return points


class TreeThread(QtCore.QThread):
    def __init__(self, tree):
        super(TreeThread, self).__init__()
        self.tree = tree

    def run(self):
        self.tree.generate()


class TreeColonizationDemoWidget(QtWidgets.QWidget):
    """demo
    """

    def __init__(self):
        super(TreeColonizationDemoWidget, self).__init__()
        self.total_points = 1000
        self.points = []
        self.direction = QtGui.QVector2D(0, -1)
        self.tree = sfwidgets.treecolonization.Tree(None, None, [])
        self.tree_thread = TreeThread(self.tree)
        self.setWindowTitle('Tree Colonization')

    def create(self):
        w_padding = self.width() * 0.2
        h_padding = self.height() * 0.1
        rect = QtCore.QRectF(w_padding, h_padding,
                             self.width() - w_padding * 2.0,
                             self.height() - self.height() * 0.4)
        self.points = generate_points(rect, self.total_points)
        pos = QtGui.QVector2D(self.width() / 2.0, self.height())

        self.tree = sfwidgets.treecolonization.Tree(pos, self.direction, self.points)
        self.tree.updated.connect(self._handle_update)
        self.tree_thread.tree = self.tree
        self.tree_thread.start()
        self.update()

    def _handle_update(self):
        self.update()

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        for p in self.points:
            painter.drawPoint(p.x(), p.y())
        p = QtGui.QPen()
        p.setWidth(2)
        painter.setPen(p)
        self.tree.paint(painter)

    def closeEvent(self, event):
        self.tree_thread.exit()

    def showEvent(self, e):
        self.create()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    w = TreeColonizationDemoWidget()
    w.show()
    app.exec_()
    # r = QtCore.QRectF(0, 0, 200, 200)
    # p = generate_points(r, 100)
    # pos = QtGui.QVector2D(100, 100)
    # Tree(pos, p)


if __name__ == '__main__':
    main()
