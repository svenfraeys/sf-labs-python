"""
base pathTraceBouncer
"""
import math
import random

import sys
from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtGui import QVector2D, QColor, QPen
from PySide2.QtCore import QRect, QPoint

DEBUG = False


class PathTracer:
    def __init__(self):
        self.debug_points = []
        self.rays = []
        self.bounce_rays = []
        self.lines = []
        self.max_bounces = 3
        self.scatter_per_bounce = 5
        self.all_rays = []

    @staticmethod
    def does_ray_intersect(ray, line):
        p0 = line.p0 - ray.pos
        p1 = line.p1 - ray.pos

        angle = math.atan2(ray.dir.y(), ray.dir.x())

        p0_angle = math.atan2(p0.y(), p0.x()) - angle
        p1_angle = math.atan2(p1.y(), p1.x()) - angle
        local_p0 = QVector2D(math.cos(p0_angle),
                             math.sin(p0_angle)) * p0.length()
        local_p1 = QVector2D(math.cos(p1_angle),
                             math.sin(p1_angle)) * p1.length()
        res = False

        # if the point is behind no hit
        if local_p0.x() < 0 and local_p1.x() < 0:
            return False

        # points need to cross the axis
        if local_p0.y() < 0 and local_p1.y() > 0:
            res = True

        if local_p0.y() > 0 and local_p1.y() < 0:
            res = True

        if not res:
            return None

        slope = PathTracer.line_slope_x(local_p0, local_p1)

        intercept_x = local_p0.x() - slope * local_p0.y()
        intercept_y = local_p0.y() - slope * local_p0.x()
        if intercept_x <= 0:
            return None
        local_intersect_point = QVector2D(intercept_x, 0)

        new_angle = math.atan2(local_intersect_point.y(),
                               local_intersect_point.x()) + angle
        world_intersect = QVector2D(math.cos(new_angle), math.sin(
            new_angle)) * local_intersect_point.length()

        return world_intersect + ray.pos

    @staticmethod
    def line_slope(p1, p2):
        x = (p2.x() - p1.x())
        if x == 0:
            return 0
        return (p2.y() - p1.y()) / (p2.x() - p1.x())

    @staticmethod
    def line_slope_x(p1, p2):
        y = (p2.y() - p1.y())
        if y == 0:
            return 0
        return (p2.x() - p1.x()) / (p2.y() - p1.y())

    def paint_ray_path(self, painter, ray, color):
        painter_path = QtGui.QPainterPath()
        painter_path.moveTo(ray.pos.toPoint())
        r = ray

        while r.parent:
            red = int(((color.red() / 255.0) * r.strength) * 255.0)
            green = int(((color.green() / 255.0) * r.strength) * 255.0)
            blue = int(((color.blue() / 255.0) * r.strength) * 255.0)

            painter.setPen(QPen(QtGui.QColor(red, green, blue)))
            painter.drawLine(r.pos.toPoint(), r.parent.pos.toPoint())
            painter_path.lineTo(r.parent.pos.toPoint())
            r = r.parent
            # painter.drawPath(painter_path)

    def paint(self, painter):
        for line in self.lines:
            line.paint(painter)

        # for ray in self.all_rays:
        #     ray.paint(painter)
        for r in self.all_rays:
            p = r.pos.toPoint()
            r = QRect(p + QPoint(-2, -2), p + QPoint(2, 2))
            if DEBUG:
                painter.fillRect(r, QColor(0, 0, 200))

        c = QtGui.QColor(250, 210, 20)
        for ray in self.all_rays:
            if not ray.children:
                painter.setPen(QtGui.QPen(c))
                self.paint_ray_path(painter, ray, c)

        if DEBUG:
            for point in self.debug_points:
                p = point.toPoint()
                r = QRect(p + QPoint(-2, -2), p + QPoint(2, 2))
                painter.fillRect(r, QColor(0, 0, 200))

        for ray in self.rays:
            ray.paint(painter)

    def reset(self):
        self.debug_points = []
        self.bounce_rays = []
        self.all_rays = []

    def reflect(self, point, normal):
        v = point - (normal * QVector2D.dotProduct(point, normal) * 2)
        v.normalize()
        return v

    def start(self):
        self.bounce_rays = []
        self.all_rays = []
        self.all_rays += self.rays

        # create the bounce rays
        for ray in self.rays:
            self.shoot_ray(ray)

        for i in range(self.max_bounces):
            bounce_rays = list(self.bounce_rays)
            self.bounce_rays = []
            for bounce_ray in bounce_rays:
                self.shoot_ray(bounce_ray)

    def shoot_ray(self, ray, ignore_line=None):
        intersecting_lines = []
        nearest_length = sys.float_info.max
        nearest_line = None
        nearest_point = None

        for line in self.lines:
            if line == ray.line:
                continue

            if line == ignore_line:
                continue
            intersect_point = self.does_ray_intersect(ray, line)
            if not intersect_point:
                continue

            l = (intersect_point - ray.pos).length()
            if l < nearest_length:
                nearest_length = l
                nearest_line = line
                nearest_point = intersect_point

            intersecting_lines.append(line)
            # self.debug_points.append(intersect_point)

        if not nearest_point:
            return

        if nearest_point:
            self.debug_points.append(nearest_point)

        angle = math.atan2(nearest_line.normal.y(), nearest_line.normal.x())
        roughness = math.pi / 8.0
        for i in range(self.scatter_per_bounce):
            new_strength = ray.strength - random.random() * 0.28
            if new_strength < 0:
                continue
            angle_random = roughness / 2.0 - (random.random() * roughness)
            new_angle = angle + angle_random
            new_normal = QVector2D(math.cos(new_angle), math.sin(new_angle))
            bounce_dir = self.reflect(ray.dir, new_normal)
            bounce_ray = Ray(nearest_point, bounce_dir)
            self.all_rays.append(bounce_ray)
            bounce_ray.parent = ray

            bounce_ray.strength = new_strength
            bounce_ray.line = nearest_line
            self.bounce_rays.append(bounce_ray)

        if not intersecting_lines:
            return


class Line:
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        size = p1 - p0
        self.normal = QVector2D(size.y(), -size.x())
        self.normal.normalize()

    def paint(self, painter):
        pen = QPen(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawLine(self.p0.toPoint(), self.p1.toPoint())
        center = self.p0 + (self.p1 - self.p0) / 2

        painter.drawLine(center.toPoint(),
                         (center + self.normal * 5).toPoint())


class Ray:
    def __init__(self, pos, dir_):
        self.pos = pos
        self.dir = dir_
        self.__parent = None
        self.line = None
        self.children = []
        self.strength = 1.0

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        value.children.append(self)
        self.__parent = value

    def paint(self, painter):
        if DEBUG:
            pen = QPen(QColor(50, 40, 230))
            painter.setPen(pen)
            painter.drawLine(self.pos.toPoint(),
                             (self.pos + self.dir * 20).toPoint())

            start = (self.pos - QVector2D(-2, -2)).toPoint()
            end = (self.pos - QVector2D(2, 2)).toPoint()
            r = QtCore.QRect(start, end)
            painter.fillRect(r, QtGui.QColor(255, 255, 255))


class PathTraceBouncerDemoWidget(QtWidgets.QWidget):
    """
    PathTraceBouncer
    """

    def __init__(self):
        super(PathTraceBouncerDemoWidget, self).__init__()

        self.resize(QtCore.QSize(300, 300))
        self.current_mouse_button = None
        self.setWindowTitle("PathTraceBouncer")
        self.points = []
        self.ray = Ray(QVector2D(self.width() / 3, self.height() / 2),
                       QVector2D(0.5, 0.5).normalized())

        self.pathtracer = PathTracer()
        self.pathtracer.lines += self.create_circle(
            QVector2D(self.width() / 2, self.height() / 2), self.height() / 2,
            8)
        self.pathtracer.lines += self.create_circle(
            QVector2D(self.width() / 2, self.height() / 2), self.height() / 9,
            8)
        self.pathtracer.rays.append(self.ray)

    def create_circle(self, c, r, s):
        lines = []
        points = []
        pi2 = math.pi * 2
        for i in range(s):
            j = (pi2 / s) * i
            v = QVector2D(math.cos(j), math.sin(j))
            p = c + v * r
            points.append(p)

        for i in range(0, s - 1, 1):
            line = Line(points[i], points[i + 1])
            lines.append(line)
        lines.append(Line(points[-1], points[0]))
        return lines

    def mousePressEvent(self, event):
        self.current_mouse_button = event.button()

    def mouseReleaseEvent(self, event):
        self.current_mouse_button = event.button()

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_Up:
            self.pathtracer.max_bounces += 1
            if self.pathtracer.max_bounces > 5:
                self.pathtracer.max_bounces = 5
            self.pathtracer.reset()
            self.pathtracer.start()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.pathtracer.max_bounces -= 1
            if self.pathtracer.max_bounces < 0:
                self.pathtracer.max_bounces = 0
            self.pathtracer.reset()
            self.pathtracer.start()
            self.update()

        if event.key() == QtCore.Qt.Key_Right:
            self.pathtracer.scatter_per_bounce += 1
            if self.pathtracer.scatter_per_bounce > 6:
                self.pathtracer.scatter_per_bounce = 6
            self.pathtracer.reset()
            self.pathtracer.start()
            self.update()

        if event.key() == QtCore.Qt.Key_Left:
            self.pathtracer.scatter_per_bounce -= 1
            if self.pathtracer.scatter_per_bounce < 0:
                self.pathtracer.scatter_per_bounce = 0
            self.pathtracer.reset()
            self.pathtracer.start()
            self.update()

    def mouseMoveEvent(self, event):
        if self.current_mouse_button == QtCore.Qt.LeftButton:
            mouse_pos = event.pos()
            self.ray.pos = QVector2D(mouse_pos.x(), mouse_pos.y())
            self.pathtracer.reset()
            self.pathtracer.start()
            self.update()
        if self.current_mouse_button == QtCore.Qt.RightButton:
            mouse = QVector2D(event.pos().x(), event.pos().y())
            mouse_offset = mouse - self.ray.pos
            mouse_offset.normalize()
            self.ray.dir = mouse_offset
            self.pathtracer.reset()
            self.pathtracer.start()
            self.update()

    def showEvent(self, event):
        pass

    def paintEvent(self, event):
        self.points = []

        painter = QtGui.QPainter(self)

        painter.fillRect(self.rect(), QColor(80, 80, 80))

        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.pathtracer.paint(painter)

        txt = "max bounces: {} | scatter per bounce: {}".format(
            self.pathtracer.max_bounces, self.pathtracer.scatter_per_bounce)
        painter.fillRect(10, 10, 220, 15, QColor(150, 150, 150))
        painter.setPen(QPen())
        painter.drawText(20, 20, txt)

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = PathTraceBouncerDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
