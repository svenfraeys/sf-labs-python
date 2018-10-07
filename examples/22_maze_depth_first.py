"""
base MazeDepthFirst
"""

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QTimer

from sfwidgets.mazedepthfirst import Maze


class MazeDepthFirstDemoWidget(QtWidgets.QWidget):
    """
    MazeDepthFirst
    """

    def __init__(self):
        super(MazeDepthFirstDemoWidget, self).__init__()
        self.setWindowTitle("MazeDepthFirst")
        self.maze = Maze(20, 20)
        self.maze.repaint = self.repaint
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    def tick(self):
        self.maze.tick()
        self.update()

    def mousePressEvent(self, *args, **kwargs):
        self.maze.generate()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.maze.pauze = not self.maze.pauze
            self.update()
        if event.key() == QtCore.Qt.Key_Up:
            self.maze.width *= 2
            self.maze.height *= 2
            self.maze.generate()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.maze.width = int(self.maze.width / 2)
            self.maze.height = int(self.maze.height / 2)
            self.maze.generate()
            self.update()

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        slot_x = x / float(self.width()) * self.maze.width
        slot_y = y / float(self.height()) * self.maze.height
        slot = self.maze.get_slot(int(slot_x), int(slot_y))

        print("""
        x: {} y: {}
        top: {}
        left: {}
        right: {}
        bottom: {}
        left {}
        right {}
        """.format(slot.x, slot.y, slot.top(), slot.left(), slot.right(),
                   slot.bottom(), slot.left_wall, slot.right_wall))

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.maze.paint(painter, self.rect())

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = MazeDepthFirstDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
