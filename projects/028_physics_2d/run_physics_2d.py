"""
2D physics engine

# F = ma (Force = mass * acceleration)
"""
import time

import math
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QRect
from PySide2.QtGui import QVector2D


class Sphere:
    def __init__(self, engine):
        self.engine = engine
        self.static = False
        self.radius = 10.0
        self.pos = QVector2D()
        self.velocity = QVector2D()
        self.mass = 100.000

    def paint(self, painter):
        x = self.pos.x() - self.radius
        y = self.pos.y() - self.radius
        painter.drawEllipse(x, y, self.radius * 2.0,
                            self.radius * 2.0)

        end = self.pos + (self.velocity * self.mass)
        if self.engine.debug:
            painter.drawLine(self.pos.toPoint(), end.toPoint())

    def intersects_shpere(self, sphere):
        intersects = self.engine.circle_intersects(self.pos, self.radius,
                                                   sphere.pos, sphere.radius)
        return intersects

    def resolve_collision(self, sphere):
        diff = self.pos - sphere.pos

        depth = (self.radius + sphere.radius) - diff.length()
        # self.velocity *= -1
        diff.normalize()

        l = self.velocity.length()
        self.velocity = self.engine.reflect(self.velocity, diff)
        self.velocity.normalize()
        self.velocity *= l

        # resolve the target sphere
        lb = self.velocity.length()
        sphere.velocity = self.engine.reflect(sphere.velocity, diff * -1)
        sphere.velocity.normalize()
        sphere.velocity *= lb

        self.pos += self.velocity.normalized() * depth

    def intersects(self, object):
        if isinstance(object, Sphere):
            return self.intersects_shpere(object)

    def calculate_force(self):
        return QVector2D(0.0, self.mass * self.engine.gravity)

    def calculate_force_and_torque(self):
        pass

    def tick(self, dt=1.0):
        if self.static:
            return

        force = self.calculate_force()
        acceleration = QVector2D(force.x(), force.y())
        self.velocity.setX(self.velocity.x() + acceleration.x() * dt)
        self.velocity.setY(self.velocity.y() + acceleration.y() * dt)
        self.pos += self.velocity * dt

        for obj in self.engine.objects:
            if obj == self:
                continue

            if self.intersects(obj):
                self.resolve_collision(obj)


class Physics2D:
    def __init__(self):
        self.objects = []
        self.rect = QRect()
        self.debug = False

        self.gravity = 9.81
        self.last_time = time.time()

    def circle_intersects(self, p0, r0, p1, r2):
        distance = p0 - p1
        if distance.length() < (r0 + r2):
            return True
        else:
            return False

    @classmethod
    def line_intersects(cls, p0, p1, p2, p3):
        """does the lines intersect
        """
        return True

    @classmethod
    def box_intersects(cls, boxa, boxb):
        return False

    def add_sphere(self, radius=10.0):
        sphere = Sphere(self)
        self.objects.append(sphere)
        sphere.radius = radius
        sphere.pos.setX(self.rect.width() / 2.0)
        sphere.pos.setY(self.rect.height() / 2.0)
        return sphere

    def tick(self):
        current_time = time.time()

        dt = current_time - self.last_time

        for obj in self.objects:
            obj.tick(dt)
        self.last_time = current_time

    def reflect(self, point, normal):
        v = point - (normal * QVector2D.dotProduct(point, normal) * 2)
        v.normalize()
        return v


class Physics2DDemoWidget(QtWidgets.QWidget):
    """
    Physics2D
    """

    def __init__(self):
        super(Physics2DDemoWidget, self).__init__()
        self.setWindowTitle("Physics2D")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.engine = Physics2D()
        self.engine.rect = self.rect()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            print(self.engine.debug)
            self.engine.debug = not self.engine.debug

    def mousePressEvent(self, event):
        sphere = self.engine.add_sphere()
        sphere.pos.setX(self.width() / 2.0)
        sphere.pos.setY(self.height() / 2.0)

    def mouseMoveEvent(self, event):
        pass

    def showEvent(self, event):
        self.engine.rect = self.rect()
        sphere_a = self.engine.add_sphere()
        sphere_a.pos.setX(sphere_a.pos.x() + 5.0)

        segments = 30
        for i in range(segments):
            radians = math.pi / (segments / 2.0)
            x = math.cos(radians * i)
            y = math.sin(radians * i)
            pos = QVector2D(x, y)
            pos *= 20.0
            sphere_b = self.engine.add_sphere(radius=20.0)
            sphere_b.pos.setX(self.width() / 2.0 + x * 150)
            sphere_b.pos.setY(self.height() / 2.0 + y * 150)
            sphere_b.static = True

        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        for obj in self.engine.objects:
            obj.paint(painter)

    def tick(self):
        self.engine.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = Physics2DDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
