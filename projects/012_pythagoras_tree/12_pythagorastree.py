from PySide2 import QtGui, QtCore, QtWidgets
from pythagorstree import PythagorasTree, PythagorasTreePainter


class PythagorasTreeDemoWidget(QtWidgets.QWidget):
    """pythagoras tree
    """

    def __init__(self):
        super(PythagorasTreeDemoWidget, self).__init__()
        self.setWindowTitle('Pythagoras tree')
        self.tree = PythagorasTree()
        self.tree.n = 3
        self.tree.generate()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawText(20, 20, 'n={}'.format(self.tree.n))
        p = PythagorasTreePainter(self.width() / 2,
                                  self.height() - 20,
                                  self.tree, painter)
        p.paint()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.tree.n += 1
            self.tree.generate()
            self.update()
        if event.key() == QtCore.Qt.Key_Down:
            self.tree.n -= 1
            self.tree.generate()
            self.update()

    def sizeHint(self):
        return QtCore.QSize(200, 170)


def main():
    app = QtWidgets.QApplication([])
    w = PythagorasTreeDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
