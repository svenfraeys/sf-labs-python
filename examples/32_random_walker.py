"""
base RandomWalker
"""
import random

import math
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect, QSize
from PySide2.QtGui import QVector2D, QColor


class RandomWalker(object):
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_RIGHT = 2
    MOVE_LEFT = 3

    def __init__(self):
        self.rect = QRect()
        self.path = []
        self.start_pos = QVector2D()
        self.pos = QVector2D()
        self.resolution = QSize()

        self.up_vector = QVector2D(0, -1)
        self.down_vector = QVector2D(0, 1)
        self.left_vector = QVector2D(-1, 0)
        self.right_vector = QVector2D(1, 0)

        self.head_color = QColor(250, 60, 50)
        self.tail_color = QColor(70, 70, 70)

    def reset(self):
        self.path = []
        self.pos = self.start_pos

    def setup(self):
        self.reset()

    def get_option(self):
        choice = random.randint(0, 3)
        pos_copy = QVector2D(self.pos)

        if choice == self.MOVE_UP:
            pos_copy += self.up_vector
        elif choice == self.MOVE_DOWN:
            pos_copy += self.down_vector
        elif choice == self.MOVE_LEFT:
            pos_copy += self.left_vector
        elif choice == self.MOVE_RIGHT:
            pos_copy += self.right_vector
        return pos_copy

    def tick(self):
        """
        Tick the random walker to do something
        """
        while True:
            pos = self.get_option()
            is_valid = True
            if pos.x() > self.resolution.width():
                is_valid = False
            elif pos.x() < 0:
                is_valid = False
            elif pos.y() > self.resolution.height():
                is_valid = False
            elif pos.y() < 0:
                is_valid = False

            if is_valid:
                self.path.append(pos)
                self.pos = pos
                break

    def paint_cell(self, painter, pos, color):
        chunk_x = float(self.rect.width()) / self.resolution.width()
        chunk_y = float(self.rect.height()) / self.resolution.height()
        x = pos.x() * chunk_x
        y = pos.y() * chunk_y
        painter.fillRect(x - chunk_x / 2, y - chunk_y - 2, math.ceil(chunk_x),
                         math.ceil(chunk_y),
                         color)

    def paint(self, painter):
        for p in self.path:
            self.paint_cell(painter, p, self.tail_color)

        self.paint_cell(painter, self.pos, self.head_color)


class RandomWalkerDemoWidget(QtWidgets.QWidget):
    """
    RandomWalker
    """

    def __init__(self):
        super(RandomWalkerDemoWidget, self).__init__()
        self.setWindowTitle("RandomWalker")
        self.setCursor(QtCore.Qt.BlankCursor)
        self.is_paused = True
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.random_walker = RandomWalker()

        self.random_walker.rect = self.rect()
        self.random_walker.resolution = QSize(50, 50)
        self.random_walker.start_pos = QVector2D(
            self.random_walker.resolution.width() / 2,
            self.random_walker.resolution.height() / 2)

    def resizeEvent(self, event):
        self.random_walker.rect = self.rect()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.is_paused = not self.is_paused
        if event.key() == QtCore.Qt.Key_Backspace:
            self.random_walker.reset()
            self.update()

        if event.key() == QtCore.Qt.Key_Return:
            self.is_paused = False
            self.random_walker.reset()
            self.update()

    def showEvent(self, event):
        self.random_walker.setup()
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.random_walker.paint(painter)

    def tick(self):
        if self.is_paused:
            return

        self.random_walker.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = RandomWalkerDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
