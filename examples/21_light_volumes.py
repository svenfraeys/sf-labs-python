"""
base lightVolumes
"""
import math
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QPoint
from PySide2.QtGui import QVector2D, QPen, QColor, QPainterPath

DEBUG = False


class Line:
    def __init__(self, v0, v1):
        self.v0 = v0
        self.v1 = v1

    def paint(self, painter):
        painter.drawLine(self.v0.toPoint(), self.v1.toPoint())


class Ray:
    def __init__(self, pos, dir_):
        self.pos = pos
        self.dir = dir_
        self.length = 20

    def paint(self, painter):
        pen = QPen(QColor(255, 255, 255))
        painter.setPen(pen)
        painter.drawLine(self.pos.toPoint(),
                         (self.pos + self.dir * self.length).toPoint())
        if DEBUG:
            pen = QPen(QColor(50, 40, 230))
            painter.setPen(pen)
            painter.drawLine(self.pos.toPoint(),
                             (self.pos + self.dir * 20).toPoint())

            start = (self.pos - QVector2D(-2, -2)).toPoint()
            end = (self.pos - QVector2D(2, 2)).toPoint()
            r = QtCore.QRect(start, end)
            painter.fillRect(r, QtGui.QColor(255, 255, 255))


class VolumeLight:
    def __init__(self, light, lines):
        self.light = light
        self.lines = lines
        self.segments = 90
        self.rays = []

    @staticmethod
    def does_ray_intersect(ray, line):
        v0 = line.v0 - ray.pos
        v1 = line.v1 - ray.pos

        angle = math.atan2(ray.dir.y(), ray.dir.x())

        v0_angle = math.atan2(v0.y(), v0.x()) - angle
        v1_angle = math.atan2(v1.y(), v1.x()) - angle
        local_v0 = QVector2D(math.cos(v0_angle),
                             math.sin(v0_angle)) * v0.length()
        local_v1 = QVector2D(math.cos(v1_angle),
                             math.sin(v1_angle)) * v1.length()
        res = False

        # if the point is behind no hit
        if local_v0.x() < 0 and local_v1.x() < 0:
            return False

        # points need to cross the axis
        if local_v0.y() < 0 and local_v1.y() > 0:
            res = True

        if local_v0.y() > 0 and local_v1.y() < 0:
            res = True

        if not res:
            return None

        slope = VolumeLight.line_slope_x(local_v0, local_v1)

        intercept_x = local_v0.x() - slope * local_v0.y()
        intercept_y = local_v0.y() - slope * local_v0.x()
        if intercept_x <= 0:
            return None
        local_intersect_point = QVector2D(intercept_x, 0)

        new_angle = math.atan2(local_intersect_point.y(),
                               local_intersect_point.x()) + angle
        world_intersect = QVector2D(math.cos(new_angle), math.sin(
            new_angle)) * local_intersect_point.length()

        return world_intersect + ray.pos

    @staticmethod
    def line_slope_x(v1, p2):
        y = (p2.y() - v1.y())
        if y == 0:
            return 0
        return (p2.x() - v1.x()) / (p2.y() - v1.y())

    def calculate(self):
        self.rays = []
        cone_normal_top, cone_norma_bottom = self.light.cone_normals()
        angle_top = math.atan2(cone_normal_top.y(), cone_norma_bottom.x())
        angle_bottom = math.atan2(cone_norma_bottom.y(), cone_norma_bottom.x())

        # get angle between vectors
        total_angle = math.acos(QVector2D.dotProduct(cone_normal_top, cone_norma_bottom))
        part = total_angle / self.segments

        for i in range(self.segments):
            rad = math.atan2(self.light.dir.y(), self.light.dir.x())
            angle_i = rad - total_angle / 2.0 + (part * i)
            vector_i = QVector2D(math.cos(angle_i), math.sin(angle_i))
            ray_i = Ray(self.light.get_focal_point_worldspace(), vector_i)
            first_i = True
            self.rays.append(ray_i)

            for line in self.lines:
                intersect_v = self.does_ray_intersect(ray_i, line)

                if intersect_v:

                    length_i = (intersect_v - ray_i.pos).length()
                    if first_i:
                        ray_i.length = length_i
                        first_i = False
                    if length_i < ray_i.length:
                        ray_i.length = length_i


    def paint(self, painter):
        painther_path = QPainterPath()
        first = True
        top, bottom = self.light.get_top_bottom_worldspace()
        painther_path.moveTo(top.toPoint())
        for ray in self.rays:
            painther_path.lineTo((ray.pos + ray.dir * ray.length).toPoint())

        painther_path.lineTo(bottom.toPoint())
        painter.fillPath(painther_path, QColor(220,220,160))
        for ray in self.rays:
            if DEBUG:
                painter.setPen(QPen())
                ray.paint(painter)


class Light:
    def __init__(self):
        self.pos = QVector2D()
        self.focal_point = -20
        self.dir = QVector2D()
        self.size = 20

    def get_top_bottom_worldspace(self):
        perpendicular = QVector2D(self.dir.y(), -self.dir.x())
        top = perpendicular * self.size / 2.0
        return self.pos + top, self.pos + top * -1

    def get_focal_point_worldspace(self):
        return QVector2D(self.pos + self.dir * self.focal_point)

    def paint_circle(self, painter, v, s):
        p = QVector2D(v - QVector2D(s / 2, s / 2)).toPoint()
        painter.drawEllipse(p.x(), p.y(), s, s)

    def cone_normals(self):
        top, bottom = self.get_top_bottom_worldspace()
        focal_point_world = self.get_focal_point_worldspace()

        top_dir = (top - focal_point_world)
        top_dir.normalize()

        bottom_dir = (bottom - focal_point_world)
        bottom_dir.normalize()
        return top_dir, bottom_dir

    def paint(self, painter):
        # center = self.pos.toPoint() - QPoint(self.size / 2, self.size / 2)
        focal_point_world = self.get_focal_point_worldspace()

        if DEBUG:
            painter.drawLine(self.pos.toPoint(),
                             self.pos.toPoint() + (self.dir * 15).toPoint())

            self.paint_circle(painter, focal_point_world, 5.0)
            self.paint_circle(painter, self.pos, 20)

        top, bottom = self.get_top_bottom_worldspace()
        if DEBUG:
            painter.drawLine(top.toPoint(), bottom.toPoint())

            painter.drawLine(focal_point_world.toPoint(), top.toPoint())
            painter.drawLine(focal_point_world.toPoint(), bottom.toPoint())

        path = QPainterPath()
        path.moveTo(top.toPoint())
        path.lineTo(bottom.toPoint())
        path.lineTo(focal_point_world.toPoint())

        painter.fillPath(path, QtGui.QColor(50, 50, 100))

        if DEBUG:
            top_dir, bottom_dir = self.cone_normals()
            top_dir *= 50
            end_top_cone = focal_point_world + top_dir
            bottom_dir *= 50
            end_bottom_cone = focal_point_world + bottom_dir

            painter.drawLine(focal_point_world.toPoint(), end_top_cone.toPoint())
            painter.drawLine(focal_point_world.toPoint(),
                             end_bottom_cone.toPoint())


class LightVolumesDemoWidget(QtWidgets.QWidget):
    """
    LightVolumes
    """

    def __init__(self):
        super(LightVolumesDemoWidget, self).__init__()
        self.resize(QtCore.QSize(300, 300))
        self.setWindowTitle("LightVolumes")
        self.current_mouse_button = None
        self.light = Light()
        self.light.dir = QVector2D(1, 0)
        self.light.pos.setX(self.width() / 3)
        self.light.pos.setY(self.height() / 2)

        self.lines = []

        for i in range(20):
            circle = self.create_circle(QVector2D(random.random() * self.width(), random.random() * self.height()), 10 + random.random() * 10, 16)
            self.lines += circle
        self.lines += self.create_window_rect()
        self.volumelight = VolumeLight(self.light, self.lines)
        self.volumelight.calculate()

    def create_window_rect(self):
        v0 = QVector2D(0, 0)
        v1 = QVector2D(self.width(), 0)
        v2 = QVector2D(0, self.height())
        v3 = QVector2D(self.width(), self.height())
        return [Line(v0, v1), Line(v0, v2), Line(v0, v1), Line(v1, v3), Line(v2, v3)]

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

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), QColor(30,30,30))

        self.volumelight.paint(painter)
        for line in self.lines:
            line.paint(painter)

        self.light.paint(painter)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def mousePressEvent(self, event):
        self.current_mouse_button = event.button()

    def mouseReleaseEvent(self, event):
        self.current_mouse_button = event.button()

    def mouseMoveEvent(self, event):
        if self.current_mouse_button == QtCore.Qt.LeftButton:
            mouse_pos = event.pos()
            self.light.pos = QVector2D(mouse_pos.x(), mouse_pos.y())
            self.volumelight.calculate()
            self.update()
        if self.current_mouse_button == QtCore.Qt.RightButton:
            mouse = QVector2D(event.pos().x(), event.pos().y())
            mouse_offset = mouse - self.light.pos
            mouse_offset.normalize()
            self.light.dir = mouse_offset
            self.volumelight.calculate()
            self.update()


def main():
    app = QtWidgets.QApplication([])
    widget = LightVolumesDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
