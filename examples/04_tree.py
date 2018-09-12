from PySide2 import QtWidgets, QtCore, QtGui
from sfwidgets.ltree import TreePainter, Vec2, TreeGenerator


class TreeDemoWidget(QtWidgets.QWidget):
    """lsystem widget
    """

    def __init__(self):
        super(TreeDemoWidget, self).__init__()
        self.setWindowTitle('Tree Demo')
        tree_generator = TreeGenerator()
        tree_generator.iterations = 9
        tree_generator.generate()

        self.tree_generator = tree_generator
        self.scale = Vec2(0.008, 0.008)

        roots_generator = TreeGenerator()
        roots_generator.iterations = 6
        roots_generator.generate()
        self.roots_generator = roots_generator

    def paintEvent(self, *args, **kwargs):
        painter = TreePainter(self, self.tree_generator)
        painter.painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.width = 5000.0
        painter.position = Vec2(self.width() / 2.0, self.height() - 20)
        painter.scale = self.scale
        painter.paint()

        root_painter = TreePainter(self, self.roots_generator)
        root_painter.position = Vec2(self.width() / 2.0, self.height() - 20)
        root_painter.direction = Vec2(0, 1)
        root_painter.scale = self.scale
        root_painter.width = 5000.0
        # root_painter.paint()

    def mousePressEvent(self, *args, **kwargs):
        # self.tree_generator.iterations += 1
        self.tree_generator.generate()

        self.update()


def main():
    app = QtWidgets.QApplication([])
    w = TreeDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
