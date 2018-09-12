import math
import random

from PySide2 import QtGui, QtCore


class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y

    def __add__(self, other):
        result = self.copy()
        if isinstance(other, Vec2):
            result.x += other.x
            result.y += other.y
        else:
            result.x += other
            result.y += other
        return result

    def __mul__(self, other):
        result = self.copy()
        if isinstance(other, Vec2):
            result.x *= other.x
            result.y *= other.y
        else:
            result.x *= other
            result.y *= other
        return result

    def __sub__(self, other):
        result = self.copy()
        if isinstance(other, Vec2):
            result.x -= other.x
            result.y -= other.y
        else:
            result.x -= other
            result.y -= other
        return result

    def __div__(self, other):
        result = self.copy()
        if isinstance(other, Vec2):
            result.x /= other.x
            result.y /= other.y
        else:
            result.x /= other
            result.y /= other
        return result

    def copy(self):
        return Vec2(self.x, self.y)

    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length

    def inverse(self):
        self.x *= -1
        self.y *= -1

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def angle(self):
        vector = self.copy()
        vector.normalize()
        return math.atan2(vector.y, vector.x)

    def __repr__(self):
        return 'Vec2({}, {})'.format(self.x, self.y)

    def dot(self, value):
        angle_diff = value.angle() - self.angle()
        return self.length() * value.length() * math.cos(angle_diff)

    def perpendicular(self):
        return Vec2(self.y, -self.x)


class TreeGenerator(object):
    """tree generator
    """

    def __init__(self):
        self.iterations = 4
        self.structure = ''
        self.rules = {'1': '11', '0': '1[0]0'}

    def generate(self):

        axiom = '0'
        variables = ['0', '1']
        constants = ['[', ']']
        start = axiom

        for i in range(self.iterations):
            result = ''
            for v in start:
                if v in constants:
                    result += v
                elif v in variables and v in self.rules:
                    result += self.rules[v]

            start = result
        self.structure = start

    def depth(self):
        depth = 0

        for i in self.structure:
            if i == '1':
                depth += 1
            elif i == ']':
                return depth
        return depth


class TreePainter:
    """painting a tree
    """

    def __init__(self, widget, tree_generator):
        self.widget = widget
        self.tree_generator = tree_generator
        self.scale = Vec2(1.0, 1.0)
        self.position = Vec2(0.0, 0.0)
        self.direction = Vec2(0.0, -1.0)
        self.tree_generator = self.tree_generator
        self.pen = QtGui.QPen()


        self.painter = QtGui.QPainter(self.widget)
        self.painter.setPen(self.pen)

        self.width = 100.0

    def paint(self):
        turtle = Turtle(self.painter)
        turtle.direction = self.direction
        turtle.scale = self.scale
        turtle.offset = self.position
        depth = self.tree_generator.depth()
        width = 1.0
        paint_width = self.width
        length = 100.0 / (self.tree_generator.iterations / 10.0)
        paint_width = self.width / (self.tree_generator.iterations / 10.0)

        rotation = random.randrange(-9, 9) / 100.0

        draw_left_points = []
        draw_right_points = []
        bush_locations = []

        for k in self.tree_generator.structure:
            if k == '0':
                self.pen.setColor(QtGui.QColor(20, 160, 0))
                self.painter.setPen(self.pen)
                brush = QtGui.QBrush(QtGui.QColor(20, 160, 0))
                self.painter.setBrush(brush)
                a = turtle.position
                turtle.forward(length * 10.0)
                b = turtle.position
                chunk = b - a
                # turtle.draw_line(a, b)
                perp = chunk.perpendicular()
                perp.normalize()
                b = QtGui.QBrush(QtGui.QColor(20, 160, 0))
                b.setColor(QtGui.QColor(20, 160, 0))
                self.painter.setBrush(b)
                turtle.draw_circle(a, 20)
                bush_locations.append(a)
                # turtle.draw_line(a, a + perp * chunk.length())
                perp.inverse()
                # turtle.draw_line(a, a + perp * chunk.length())
            elif k == '1':
                width -= 1.0 / depth
                c = 150 - width * 150
                c = 0
                self.pen.setColor(QtGui.QColor(c, c, c))

                self.painter.setPen(self.pen)

                pos_a = turtle.position
                turtle.forward(length)
                turtle.rotate(rotation)
                pos_b = turtle.position
                chunk = pos_b - pos_a
                perp = chunk.perpendicular()
                perp.normalize()
                bottom_left = pos_a + (perp * paint_width * width)
                top_left = pos_b + (perp * paint_width * width)
                # turtle.draw_line(pos_a, bottom_left)
                perp_inv = perp.copy()
                perp_inv.inverse()
                bottom_right = pos_a + perp_inv * paint_width * width
                top_right = pos_b + perp_inv * paint_width * width
                # turtle.draw_line(bottom_left, bottom_right)

                polygon = [top_left, top_right, bottom_right, bottom_left]
                # turtle.draw_polygon(polygon, QtGui.QColor(c, c, c))

                if not draw_left_points and not draw_right_points:
                    draw_left_points.append(bottom_left)
                    draw_right_points.append(bottom_right)

                draw_left_points.append(top_left)
                draw_right_points.append(top_right)

            elif k == '[':
                turtle.push((width, length))
                length += 50.0
                angle = random.randrange(0, 40)
                turtle.rotate(angle)
                rotation = random.randrange(-9, 9) / 100.0
                draw_right_points.reverse()
                points = draw_left_points + draw_right_points
                turtle.draw_polygon(points, QtGui.QColor(200, 150, 0))
                draw_left_points = []
                draw_right_points = []
            elif k == ']':
                width, length = turtle.pop()
                angle = random.randrange(20, 70)
                turtle.rotate(-angle)
                rotation = random.randrange(-9, 9) / 100.0

                draw_left_points = []
                draw_right_points = []

        for bush_location in bush_locations:
            b = QtGui.QBrush(QtGui.QColor(20, 160, 0))
            b.setColor(QtGui.QColor(20, 160, 0))
            self.painter.setBrush(b)
            turtle.draw_circle(bush_location, 50)

class Turtle:
    """turtle drawing system
    """

    def __init__(self, painter):
        """qpainter to initialise
        """
        self.painter = painter
        self.offset = Vec2()
        self.stack = []
        self.position = Vec2()
        self.direction = Vec2(1.0, 0.0)
        self.scale = Vec2(1.0, 1.0)

    def push(self, data=None):
        self.stack.append(
            (self.position.copy(), self.direction.copy(), data))

    def pop(self):
        if self.stack:
            self.position, self.direction, data = self.stack.pop(-1)
            return data
        return None

    def draw_line(self, a, b):
        a = self.offset + a * self.scale.x
        b = self.offset + b * self.scale.y
        self.painter.drawLine(a.x, a.y, b.x, b.y)

    def draw_circle(self, a, radius):
        a = self.offset + a * self.scale.x
        self.painter.drawEllipse(a.x - radius / 2, a.y - radius / 2, radius, radius)

    def draw_polygon(self, points, color):
        polygon = QtGui.QPolygonF()
        painter_path = QtGui.QPainterPath()

        for i, v in enumerate(points):
            v = self.offset + v * self.scale.x

            if i == 0:
                painter_path.moveTo(v.x, v.y)
            else:
                painter_path.lineTo(v.x, v.y)
            polygon.append(QtCore.QPointF(v.x, v.y))

        # self.painter.drawPolygon(polygon)
        self.painter.fillPath(painter_path, color)

    def fill_path(self):
        self.painter.fillPath()

    def forward(self, value):
        prev_position = self.position
        self.position += self.direction * value
        # self.draw_line(prev_position, self.position)

    def rotate(self, degrees):
        theta = math.radians(degrees)
        cs = math.cos(theta)
        sn = math.sin(theta)

        x = self.direction.x * cs - self.direction.y * sn
        y = self.direction.x * sn + self.direction.y * cs
        self.direction = Vec2(x, y)
        # self.direction.normalize()
        return
