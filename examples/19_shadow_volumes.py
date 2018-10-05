import math
import random
from PySide2 import QtWidgets, QtGui, QtCore

DEBUG = False


def paint_line(painter, v0, v1):
    if DEBUG:
        painter.drawLine(v0.x(), v0.y(), v1.x(), v1.y())


def paint_vert(painter, v0):
    if DEBUG:
        painter.drawRect(v0.x() - 3, v0.y() - 3, 6, 6)


def fill_path(painter, verts, color):
    painter_path = QtGui.QPainterPath()
    first = True

    for v in verts:
        if first:
            painter_path.moveTo(v.toPoint())
            first = False
        else:
            painter_path.lineTo(v.toPoint())

    painter.fillPath(painter_path, color)


class VolumeRays:
    def __init__(self, light, geometry):
        self.light = light
        self.geometry = geometry
        self.debug_vectors = []

    def project_vector(self, light_v, rotate, v1):
        # translate
        local_v1 = v1 - light_v
        if DEBUG:
            self.debug_vectors.append(QtGui.QVector2D(local_v1))
        v1_rotation = math.atan2(local_v1.y(), local_v1.x())
        new_rotation = rotate - v1_rotation
        x = math.cos(new_rotation)
        y = math.sin(new_rotation)
        local_no_rotation_v1 = QtGui.QVector2D(x, y)
        local_no_rotation_v1.normalize()
        local_no_rotation_v1 *= local_v1.length()
        if DEBUG:
            self.debug_vectors.append(QtGui.QVector2D(local_no_rotation_v1))

        length_proj = QtGui.QVector2D.dotProduct(local_no_rotation_v1, QtGui.QVector2D(1, 0))
        length_project = local_no_rotation_v1.length() / length_proj
        local_no_rotation_v1.normalize()
        return local_no_rotation_v1 * length_project

    def get_min_max_v(self):
        direction = QtGui.QVector2D()
        for v in self.geometry.verts:
            direction += v - self.light.pos

        direction /= len(self.geometry.verts)
        direction.normalize()

        rotate = math.atan2(direction.y(), direction.x())

        max_r = 0
        min_r = 0
        min_v = None
        max_v = None

        for v in self.geometry.verts:
            p_v = self.project_vector(self.light.pos, rotate, v)

            if p_v.y() >= max_r:
                max_r = p_v.y()
                max_v = v
            if p_v.y() <= min_r:
                min_r = p_v.y()
                min_v = v

        return min_v, max_v

    def get_max_v(self):
        return self.geometry.verts[1]

    def paint(self, painter):
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 0)))
        self.debug_vectors = []
        min_v, max_v = self.get_min_max_v()

        for v in self.debug_vectors:
            paint_vert(painter, v)

        if min_v is None or max_v is None:
            return

        direction_min = min_v - self.light.pos
        direction_min.normalize()

        direction_max = max_v - self.light.pos
        direction_max.normalize()

        end_length = 500

        min_far = min_v + (direction_min * end_length)
        max_far = max_v + (direction_max * end_length)

        paint_vert(painter, min_far)
        paint_vert(painter, max_far)

        fill_path(painter, [min_v, min_far, max_far, max_v], QtGui.QColor(30,30,30))

        for v in self.geometry.verts:
            v0 = self.light.pos
            # paint_line(painter, v0, v)

        direction = QtGui.QVector2D()
        for v in self.geometry.verts:
            direction += v - self.light.pos

        direction.normalize()
        paint_line(painter, self.light.pos, self.light.pos + direction * 50)


class Light:
    def __init__(self):
        self.pos = QtGui.QVector2D()

    def set_xy(self, x, y):
        self.pos.setX(x)
        self.pos.setY(y)

    def paint(self, painter):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        painter.drawEllipse(self.pos.x() - 5, self.pos.y() - 5, 10,
                            10)


class Line:
    def __init__(self):
        self.v0 = QtGui.QVector2D()
        self.v1 = QtGui.QVector2D()

    def paint(self, painter):
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
        painter.drawLine(self.v0.x(), self.v0.y(), self.v1.x(), self.v1.y())

    @property
    def verts(self):
        return [self.v0, self.v1]


class Circle:
    def __init__(self):
        self.pos = QtGui.QVector2D()
        self.radius = 20
        self.segments = 20
        self.verts = []

    def generate_verts(self):
        self.verts = []
        chunk = (math.pi * 2.0) / self.segments
        for i in range(self.segments):
            r = i * chunk
            x = math.cos(r)
            y = math.sin(r)
            random_v = 0.5 + (random.random()) / 20.0
            v = self.pos + QtGui.QVector2D(x, y) * self.radius *random_v
            self.verts.append(v)

    def paint(self, painter):
        fill_path(painter, self.verts, QtGui.QColor())


class ShadowVolumesDemoWidget(QtWidgets.QWidget):
    """volume light demo
    """

    def __init__(self):
        super(ShadowVolumesDemoWidget, self).__init__()
        self.setWindowTitle('Shadow Volumes')
        self.resize(QtCore.QSize(300, 300))
        self.light = Light()
        self.light.set_xy(self.width() / 3, self.height() / 2)

        self.line = Line()
        self.line.v0.setX(self.width() / 2)
        self.line.v0.setY(self.height() / 3)

        self.line.v1.setX(self.width() / 2)
        self.line.v1.setY((self.height() / 3) * 2.0)

        # self.volume_rays = VolumeRays(self.light, self.circle)
        self.circles = []
        self.volume_rays = []
        for i in range(50):
            x = random.random() * self.width()
            y = random.random() * self.height()
            circle = Circle()
            circle.pos.setX(x)
            circle.pos.setY(y)
            circle.generate_verts()
            self.circles.append(circle)

            volume_ray = VolumeRays(self.light, circle)
            self.volume_rays.append(volume_ray)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor(50, 50, 50))

        for volume_ray in self.volume_rays:
            volume_ray.paint(painter)

        for circle in self.circles:
            circle.paint(painter)

        self.light.paint(painter)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        self.light.set_xy(event.pos().x(), event.pos().y())
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    w = ShadowVolumesDemoWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
