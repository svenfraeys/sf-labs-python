import random
import time

from PySide2.QtCore import QRect
from PySide2.QtCore import QRectF
from PySide2.QtGui import QColor
from PySide2.QtGui import QVector2D


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
        self.debug = False
        self.player = Player()
        self.move_speed = 0.05
        self.prev_time = time.time()
        self.obstacles = []
        self.stopped = False
        self.total_ticks_alive = 0
        self.ticks_per_obstacle = 20
        self.obstacle_tick = 0

    def reset(self):
        self.obstacle_tick = 0
        self.obstacles = []
        self.player.pos = QVector2D()
        self.prev_time = time.time()
        self.stopped = False
        self.total_ticks_alive = 0

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
        y = self.player.pos.y() - self.move_speed
        if y < -1.0:
            y = -1.0
        self.player.pos.setY(y)

    def player_down(self):
        y = self.player.pos.y() + self.move_speed
        if y > 1.0:
            y = 1.0
        self.player.pos.setY(y)

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

        # self.distance_next_obstacle()
        self.total_ticks_alive += 1
        curr_time = time.time()
        diff = curr_time - self.prev_time

        self.obstacle_tick += 1

        if self.obstacle_tick >= self.ticks_per_obstacle:
            self.add_obstacle()
            self.obstacle_tick = 0

        if False and diff > 0.1:
            self.add_obstacle()
            self.prev_time = curr_time

        # move obstacles
        for obstalce in self.obstacles:
            obstalce.pos.setX(obstalce.pos.x() - 0.01)

        # check intersections
        for obstalce in self.obstacles:
            if self.player_intersects(obstalce):
                self.stopped = True

        if self.player.pos.y() < -0.95:
            self.stopped = True

        if self.player.pos.y() > 0.95:
            self.stopped = True

        # remove off screen obstacles
        for i in reversed(range(len(self.obstacles))):
            if self.obstacles[i].pos.x() < -1.0:
                self.obstacles.pop(i)


class RunnerPainter:
    def __init__(self, runner, rect):
        self.rect = rect
        self.runner = runner

    def pos_to_screen(self, pos):
        hwidth = self.rect.width() / 2.0
        hheight = self.rect.height() / 2.0
        x = self.rect.x() + hwidth + pos.x() * hwidth
        y = self.rect.y() + hheight + pos.y() * hheight
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

        painter.drawLine(pos.x(), pos.y(), pos.x() + 5, pos.y())
        painter.drawLine(pos.x(), pos.y(), pos.x() - 5, pos.y())
        painter.drawLine(pos.x(), pos.y(), pos.x(), pos.y() + 5)
        painter.drawLine(pos.x(), pos.y(), pos.x(), pos.y() - 5)

        rect = self.rect_to_screen(gameobject.rect)
        if isinstance(gameobject, Obstacle):
            if self.runner.is_obstacle_a_threat(gameobject):
                painter.fillRect(rect, QColor(200, 0, 0))
        painter.drawRect(rect)

        if self.runner.debug:
            txt = 'x: {} y: {}'.format(
                gameobject.pos.x(), gameobject.pos.y())
            painter.drawText(int(pos.x()), int(pos.y() - 10), txt)

    def paint_obstacles(self, painter):
        for obstacle in self.runner.obstacles:
            self.paint_gameobject(painter, obstacle)
