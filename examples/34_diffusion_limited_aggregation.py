"""
dla diffusion limited aggregation
"""
import math
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect, QThread
from PySide2.QtGui import QVector2D, QPen, QBrush, QColor

MAX_ACTIVE_WALKERS = 80
MAX_STICKING_WALKER = 600
WALKER_RADIUS = 3.0
DEBUG = False
WALK_TROUGH_EDGES = False
WALK_SPEED = 3.0
PI2 = math.pi * 2.0


def create_random_vector2d():
    a = random.random() * PI2
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
        return self.pos + create_random_vector2d() * WALK_SPEED

    def walk(self):
        pos = self.next_pos()

        # if the next position is outside of the screen put it back in
        if pos.x() < self.dla.rect.x():
            if WALK_TROUGH_EDGES:
                pos.setX(self.dla.rect.width() - pos.x())
            else:
                pos.setX(0)
        elif pos.x() > self.dla.rect.width():
            if WALK_TROUGH_EDGES:
                pos.setX(pos.x() - self.dla.rect.width())
            else:
                pos.setX(self.dla.rect.width())

        if pos.y() < self.dla.rect.y():
            if WALK_TROUGH_EDGES:
                pos.setY(self.dla.rect.height() - pos.y())
            else:
                pos.setY(0)
        elif pos.y() > self.dla.rect.height():
            if WALK_TROUGH_EDGES:
                pos.setY(pos.y() - self.dla.rect.height())
            else:
                pos.setY(self.dla.rect.height())

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
        self.walker_radius = WALKER_RADIUS
        self.rect = QRect()
        self.sticking_walkers = []
        self.active_walkers = []
        self.max_active_walkers = MAX_ACTIVE_WALKERS
        self.max_sticking_walkers = MAX_STICKING_WALKER

        self.finished = False
        self.walker_pen = QPen()
        self.walker_brush = QBrush(QColor())
        self.active_walker_color = QColor(150, 150, 150)

    def get_progress(self):
        progress = (len(self.sticking_walkers) - 1) / float(
            self.max_sticking_walkers)
        return progress

    def reset(self):
        self.setup()

    def setup(self):
        w = Walker(self, self.rect.width() / 2, self.rect.height() / 2)
        w.radius = self.walker_radius
        w.color = QColor(200, 0, 0)

        self.sticking_walkers = [w]
        self.active_walkers = []

        for i in range(self.max_active_walkers):
            self.active_walkers.append(self.spawn_new_walker())

        self.finished = False
        self.request_new_walker()

    def paint_walker(self, painter, w, color=None):
        painter.setPen(QPen(color or w.color))
        painter.setBrush(QBrush(color or w.color))
        painter.drawEllipse(math.floor(w.pos.x() - w.radius),
                            math.floor(w.pos.y() - w.radius),
                            math.ceil(w.radius * 2.0),
                            math.ceil(w.radius * 2.0))

    def paint(self, painter):
        for w in self.active_walkers:
            self.paint_walker(painter, w, self.active_walker_color)
        for w in self.sticking_walkers:
            self.paint_walker(painter, w)

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
        walker.radius = self.walker_radius
        # walker.radius = (1.0 - self.get_progress()) * self.walker_radius
        walker.color = QColor((1.0 - progress) * 150, 0,
                              150 * progress)
        return walker

    def request_new_walker(self):
        if len(self.sticking_walkers) <= self.max_sticking_walkers:
            walker = self.spawn_new_walker()
            self.active_walkers.append(walker)

    def tick(self):
        if not self.active_walkers:
            return

        for w in self.active_walkers:
            w.walk()

        for active_walker in self.active_walkers:
            active_sticks = False
            for sticking_walker in self.sticking_walkers:
                if active_walker.intersects(sticking_walker):
                    active_sticks = True
                    break

            if active_sticks:
                if self.on_stick_func:
                    self.on_stick_func()
                self.sticking_walkers.append(active_walker)
                self.active_walkers.pop(
                    self.active_walkers.index(active_walker))

                self.request_new_walker()


class DlaThread(QThread):
    on_progress = QtCore.Signal()

    def __init__(self, dla):
        super(DlaThread, self).__init__()
        self.dla = dla
        self.dla.on_stick_func = self.on_stick

    def on_stick(self):
        pass
        # self.on_progress.emit()

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
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1000)
        self.tick_timer.timeout.connect(self.tick)
        self.dla_thread = DlaThread(self.dla)
        self.dla_thread.on_progress.connect(self.on_progress)
        self.jump_ticks = 0

    def on_progress(self):
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            if self.tick_timer.isActive():
                self.tick_timer.stop()
            else:
                self.tick_timer.start()

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
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = DlaDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
