"""
dla diffusion limited aggregation
"""
import math
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect, QThread
from PySide2.QtGui import QVector2D, QPen, QBrush, QColor

MAX_WALKERS = 300
DEBUG = False


def create_random_vector2d():
    a = random.random() * math.pi * 2
    return QVector2D(math.cos(a), math.sin(a))


def length_square(a, b):
    diff = a - b
    return diff.x() * diff.x() + diff.y() * diff.y()


class Walker(object):
    def __init__(self, dla, x, y):

        self.dla = dla
        self.color = QColor()
        self.pos = QVector2D(x, y)
        self.radius = 10.0

    def next_pos(self):
        return self.pos + create_random_vector2d() * 5.0

    def walk(self):
        pos = self.next_pos()

        # if the next position is outside of the screen put it back in
        if pos.x() < self.dla.rect.x():
            pos.setX(self.dla.rect.width() - pos.x())
        elif pos.x() > self.dla.rect.width():
            pos.setX(pos.x() - self.dla.rect.width())

        if pos.y() < self.dla.rect.y():
            pos.setY(self.dla.rect.height() - pos.y())
        elif pos.y() > self.dla.rect.height():
            pos.setY(pos.y() - self.dla.rect.height())

        self.pos = pos

    def intersects(self, walker):
        # intersect checking avoiding square root
        length_sqr = length_square(self.pos, walker.pos)
        if length_sqr < self.radius * self.radius + walker.radius * walker.radius:
            return True
        else:
            return False


class DLA(object):
    def __init__(self):
        super(DLA, self).__init__()
        self.on_stick_func = None
        self.walker_radius = 8.0
        self.rect = QRect()
        self.walkers = []
        self.max_walkers = MAX_WALKERS
        self.walker = None
        self.finished = False
        self.walker_pen = QPen()
        self.walker_brush = QBrush(QColor())

    def get_progress(self):
        progress = (len(self.walkers) - 1) / float(self.max_walkers)
        return progress

    def reset(self):
        self.setup()

    def setup(self):
        self.walker = None
        w = Walker(self, self.rect.width() / 2, self.rect.height() / 2)
        w.radius = self.walker_radius
        w.color = QColor(200, 0, 0)

        self.walkers = [w]
        self.finished = False
        self.request_new_walker()

    def paint_walker(self, painter, w):
        painter.setPen(QPen(w.color))
        painter.setBrush(QBrush(w.color))
        painter.drawEllipse(math.floor(w.pos.x() - w.radius),
                            math.floor(w.pos.y() - w.radius),
                            math.ceil(w.radius * 2.0),
                            math.ceil(w.radius * 2.0))

    def paint(self, painter):
        for w in self.walkers:
            self.paint_walker(painter, w)

        if self.walker:
            self.paint_walker(painter, self.walker)

    def spawn_new_walker(self):
        side = random.randint(0, 3)
        rand_value = random.random() * self.rect.width()
        if side == 0:
            walker = Walker(self, rand_value, self.rect.y())
        elif side == 1:
            walker = Walker(self, rand_value, self.rect.height())
        elif side == 2:
            walker = Walker(self, self.rect.x(), rand_value)
        elif side == 3:
            walker = Walker(self, self.rect.width(), rand_value)
        else:
            raise RuntimeError('not a valid choice')

        progress = self.get_progress()
        walker.radius = (1.0 - self.get_progress()) * self.walker_radius
        walker.color = QColor((1.0 - progress) * 150, 0,
                              150 * progress)
        self.walker = walker

    def request_new_walker(self):
        if len(self.walkers) <= self.max_walkers:
            self.spawn_new_walker()
        else:
            self.finished = True
            self.walker = None

    def tick(self):
        if not self.walker:
            return

        self.walker.walk()
        sticks = False
        for w in self.walkers:
            if self.walker.intersects(w):
                sticks = True
                break

        if sticks:
            if self.on_stick_func:
                self.on_stick_func()
            self.walkers.append(self.walker)
            self.request_new_walker()


class DlaThread(QThread):
    on_progress = QtCore.Signal()

    def __init__(self, dla):
        super(DlaThread, self).__init__()
        self.dla = dla
        self.dla.on_stick_func = self.on_stick

    def on_stick(self):
        self.on_progress.emit()

    def run(self):
        while not self.dla.finished:
            self.dla.tick()


class DlaDemoWidget(QtWidgets.QWidget):
    """
    Dla
    """

    def __init__(self):
        super(DlaDemoWidget, self).__init__()
        self.setWindowTitle("DLA - Diffusion-Limited Aggregation")
        self.setCursor(QtCore.Qt.BlankCursor)
        self.dla = DLA()
        self.dla.on_stick_func = self.on_stick
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.dla_thread = DlaThread(self.dla)
        self.dla_thread.on_progress.connect(self.on_progress)
        self.jump_ticks = 0

    def on_progress(self):
        self.update()

    def on_stick(self):
        progress = (len(self.dla.walkers) - 1) / float(self.dla.max_walkers)
        progress *= 100.0
        print('{:0.2f} %'.format(progress))
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            pass

        if event.key() == QtCore.Qt.Key_Return:
            self.dla.reset()
            self.dla_thread.start()

    def resizeEvent(self, event):
        self.dla.rect = self.rect()

    def showEvent(self, event):
        self.dla.rect = self.rect()
        self.dla.setup()
        self.tick_timer.start()
        self.dla_thread.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QColor(120, 120, 120))
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.dla.paint(painter)

        if DEBUG:
            progress = self.dla.get_progress() * 100.0
            painter.setPen(QPen())
            painter.drawText(20, 20, '{:0.2f}%'.format(progress))

    def tick(self):
        pass

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = DlaDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
