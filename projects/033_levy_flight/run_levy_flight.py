"""
base LevyFlight
"""
import random

import math
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect, QSize, QPoint
from PySide2.QtGui import QVector2D, QColor, QPainterPath


class LevyFlight(object):
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_RIGHT = 2
    MOVE_LEFT = 3

    def create_random_vector2d(self):
        a = random.random() * math.pi * 2
        return QVector2D(math.cos(a), math.sin(a))

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

    def get_next_pos(self):
        pos_copy = QVector2D(self.pos)
        v = self.create_random_vector2d()
        if random.random() < 0.01:
            pos_copy += v * random.randint(20, 40)
        else:
            pos_copy += v * random.randint(1, 5)
        return pos_copy

    def tick(self):
        """
        Tick the random walker to do something
        """

        while True:
            pos = self.get_next_pos()
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

    def paint(self, painter):
        chunk_x = float(self.rect.width()) / self.resolution.width()
        chunk_y = float(self.rect.height()) / self.resolution.height()

        painter_path = QPainterPath()
        for i, pos in enumerate(self.path):
            x = pos.x() * chunk_x
            y = pos.y() * chunk_y
            p = QPoint(x, y)
            if i == 0:
                painter_path.moveTo(p)
            else:
                painter_path.lineTo(p)

        painter.drawPath(painter_path)


class LevyFlightDemoWidget(QtWidgets.QWidget):
    """
    LevyFlight
    """

    def __init__(self):
        super(LevyFlightDemoWidget, self).__init__()
        self.setWindowTitle("LevyFlight")
        self.setCursor(QtCore.Qt.BlankCursor)
        self.is_paused = True
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.levy_flight = LevyFlight()

        self.levy_flight.rect = self.rect()
        self.levy_flight.resolution = QSize(300, 300)
        self.levy_flight.start_pos = QVector2D(
            self.levy_flight.resolution.width() / 2,
            self.levy_flight.resolution.height() / 2)

    def resizeEvent(self, event):
        self.levy_flight.rect = self.rect()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.is_paused = not self.is_paused
        if event.key() == QtCore.Qt.Key_Backspace:
            self.levy_flight.reset()
            self.update()

        if event.key() == QtCore.Qt.Key_Return:
            self.is_paused = False
            self.levy_flight.reset()
            self.update()

    def showEvent(self, event):
        self.levy_flight.setup()
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.levy_flight.paint(painter)

    def tick(self):
        if self.is_paused:
            return

        self.levy_flight.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = LevyFlightDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
