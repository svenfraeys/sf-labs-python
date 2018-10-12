"""
base Runner
"""
import random
import time
from PyQt5.QtGui import QVector2D
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect
from PySide2.QtCore import QRectF
from PySide2.QtGui import QColor


class GameObject:
    def __init__(self):
        self.size = 0.1
        self.pos = QVector2D(0.0, 0.0)

    @property
    def rect(self):
        hsize = self.size / 2.0
        return QRectF(self.pos.x() - hsize, self.pos.y() - hsize,
                      self.size, self.size)


class Player(GameObject):
    pass


class Obstacle(GameObject):
    pass


class Runner:
    def __init__(self):
        self.player = Player()
        self.move_speed = 0.05
        self.prev_time = time.time()
        self.obstacles = []
        self.stopped = False

    def is_obstacle_a_threat(self, obstacle):
        player_top = self.player.rect.top()
        player_bottom = self.player.rect.bottom()

        if obstacle.pos.x() < self.player.pos.x():
            return False

        if obstacle.rect.bottom() < player_top:
            return False

        if obstacle.rect.top() > player_bottom:
            return False

        return True

    def distance_next_obstacle(self):
        closest_obstacle = None
        closest_distance = 2000.0
        found = False
        for obstacle in self.obstacles:
            if self.is_obstacle_a_threat(obstacle):
                distance = obstacle.pos.x() - self.player.pos.x()
                if distance < closest_distance:
                    closest_distance = distance
                    closest_obstacle = obstacle
                    found = True

        if not found:
            return -1.0
        return 1.0 - closest_distance

    def player_up(self):
        self.player.pos.setY(self.player.pos.y() - self.move_speed)

    def player_down(self):
        self.player.pos.setY(self.player.pos.y() + self.move_speed)

    def add_obstacle(self):
        obstacle = Obstacle()
        obstacle.pos.setX(1)
        obstacle.pos.setY(-1.0 + random.random() * 2.0)
        self.obstacles.append(obstacle)

    def player_intersects(self, obstacle):
        if self.player.rect.intersects(obstacle.rect):
            return True
        else:
            return False

    def tick(self):
        if self.stopped:
            return

        print(self.distance_next_obstacle())

        # self.distance_next_obstacle()

        curr_time = time.time()
        diff = curr_time - self.prev_time

        if diff > 0.8:
            self.add_obstacle()
            self.prev_time = curr_time

        for obstalce in self.obstacles:
            obstalce.pos.setX(obstalce.pos.x() - 0.01)

        for obstalce in self.obstacles:
            if self.player_intersects(obstalce):
                self.stopped = True


class RunnerPainter:
    def __init__(self, runner, rect):
        self.rect = rect
        self.runner = runner

    def pos_to_screen(self, pos):
        hwidth = self.rect.width() / 2.0
        hheight = self.rect.height() / 2.0
        x = hwidth + pos.x() * hwidth
        y = hheight + pos.y() * hheight
        return QVector2D(x, y)

    def rect_to_screen(self, r):
        pos = self.pos_to_screen(QVector2D(r.x(), r.y()))
        w = (r.width() / 2.0) * self.rect.width()
        h = (r.height() / 2.0) * self.rect.height()
        return QRect(pos.x(), pos.y(), w, h)

    def paint(self, painter):
        r = self.runner.player.rect
        pos = self.pos_to_screen(self.runner.player.pos)
        pos = self.pos_to_screen(QVector2D(r.x(), r.y()))
        size = self.pos_to_screen(QVector2D(r.width(), r.height()))
        # painter.drawRect(pos.x(), pos.y(), 20, 20)
        self.paint_gameobject(painter, self.runner.player)
        self.paint_obstacles(painter)

    def paint_gameobject(self, painter, gameobject):
        screen_pos = self.pos_to_screen(gameobject.pos)
        r = gameobject.rect
        pos = self.pos_to_screen(gameobject.pos)
        # pos = self.pos_to_screen(QVector2D(r.x(), r.y()))
        # size = self.pos_to_screen(QVector2D(r.width(), r.height()))
        # painter.drawRect(pos.x(), pos.y(), (size).x(), (size).y())
        painter.drawLine(pos.x(), pos.y(), pos.x() + 5, pos.y())
        painter.drawLine(pos.x(), pos.y(), pos.x() - 5, pos.y())
        painter.drawLine(pos.x(), pos.y(), pos.x(), pos.y() + 5)
        painter.drawLine(pos.x(), pos.y(), pos.x(), pos.y() - 5)

        rect = self.rect_to_screen(gameobject.rect)
        if isinstance(gameobject, Obstacle):
            if self.runner.is_obstacle_a_threat(gameobject):
                painter.fillRect(rect, QColor(200, 0, 0))
        painter.drawRect(rect)

        txt = 'x: {} y: {}'.format(
            gameobject.pos.x(), gameobject.pos.y())
        painter.drawText(int(pos.x()), int(pos.y() - 10), txt)

    def paint_obstacles(self, painter):
        for obstacle in self.runner.obstacles:
            self.paint_gameobject(painter, obstacle)


class RunnerDemoWidget(QtWidgets.QWidget):
    """
    Runner
    """

    def __init__(self):
        super(RunnerDemoWidget, self).__init__()
        self.setWindowTitle("Runner")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(10)
        self.tick_timer.timeout.connect(self.tick)
        self.runner = Runner()
        self.runner_painter = RunnerPainter(self.runner, self.rect())

    def resizeEvent(self, event):
        self.runner_painter.rect = self.rect()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            pass

        if event.key() == QtCore.Qt.Key_Up:
            self.runner.player_up()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.runner.player_down()
            self.update()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def showEvent(self, event):
        self.runner_painter.rect = self.rect()
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.drawEllipse(0, 0, self.width(), self.height())
        self.runner_painter.paint(painter)

    def tick(self):
        self.runner.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = RunnerDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
