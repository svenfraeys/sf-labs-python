import math
from PySide2 import QtWidgets, QtGui, QtCore


def calc_fractal_binary_tree(n):
    rules = {
        '1': '11',
        '0': '1[0]0'
    }
    return calc_lsystem('0', ['0', '1'], ['[', ']'], rules, n)


def paint_fractal_binary_tree(painter, value, size=10.0, angle=25):
    turtle = Turtle(painter)
    turtle.direction = Vec2(1.0, 0.0)
    for k in value:
        if k == '0':
            turtle.forward(size)
        elif k == '1':
            turtle.rotate(-angle)
        elif k == '[':
            turtle.push()
            turtle.rotate(angle)
        elif k == ']':
            turtle.pop()
            turtle.rotate(-angle)


def calc_fractal_plant(n):
    rules = {
        'X': 'F+[[X]-X]-F[-FX]+X',
        'F': 'FF'
    }
    return calc_lsystem('X', ['X', 'F'], ['+', '-', '[', ']'], rules, n)


def paint_fractal_plant(painter, value, size=10.0, angle=25):
    turtle = Turtle(painter)
    turtle.direction = Vec2(1.0, 0.0)
    for k in value:
        if k == 'F':
            turtle.forward(size)
        elif k == '-':
            turtle.rotate(-angle)
        elif k == '+':
            turtle.rotate(angle)
        elif k == '[':
            turtle.push()
        elif k == ']':
            turtle.pop()


def calc_dragon_curve(n):
    rules = {
        'X': 'X+YF+',
        'Y': '-FX-Y'
    }
    return calc_lsystem('FX', ['X', 'Y'], ['F', '+', '-'], rules, n)


def paint_dragon_curve(painter, value, size=10.0, angle=90.0):
    turtle = Turtle(painter)
    turtle.direction = Vec2(1.0, 0.0)
    for k in value:
        if k == 'F':
            turtle.forward(size)
        elif k == '+':
            turtle.rotate(angle)
        elif k == '-':
            turtle.rotate(-angle)


def calc_sierpinski_arrow_head_curve(n):
    rules = {
        'A': 'B-A-B',
        'B': 'A+B+A'
    }
    return calc_lsystem('A', ['A', 'B'], ['+', '-'], rules, n)


def paint_sierpinski_arrow_head_curve(painter, value, size=10.0, angle=60.0):
    turtle = Turtle(painter)
    turtle.direction = Vec2(1.0, 0.0)
    for k in value:
        if k == 'A':
            turtle.forward(size)
        elif k == 'B':
            turtle.forward(size)
        elif k == '+':
            turtle.rotate(angle)
        elif k == '-':
            turtle.rotate(-angle)


def calc_sierpinski_triangle(n):
    rules = {
        'F': 'F-G+F+G-F',
        'G': 'GG'
    }
    return calc_lsystem('F-G-G', ['F', 'G'], ['+', '-'], rules, n)


def paint_sierpinski_triangle(painter, value, size=10.0, angle=120.0):
    turtle = Turtle(painter)
    turtle.direction = Vec2(1.0, 0.0)
    for k in value:
        if k == 'F':
            turtle.forward(size)
        elif k == 'G':
            turtle.forward(size)
        elif k == '+':
            turtle.rotate(angle)
        elif k == '-':
            turtle.rotate(-angle)


def calc_koch_curve(n):
    return calc_lsystem('F', ['F'], ['+', '-'], {'F': 'F+F-F-F+F'}, n)


def paint_koch_curve(painter, value, size):
    turtle = Turtle(painter)
    turtle.direction = Vec2(1.0, 0.0)
    for k in value:
        if k == 'F':
            turtle.forward(1.0 * size)
        elif k == '+':
            turtle.rotate(-90)
        elif k == '-':
            turtle.rotate(90)


def calc_lsystem(axiom, variables, constants, rules, total):
    start = axiom

    for i in range(total):
        result = ''
        for v in start:
            if v in constants:
                result += v
            elif v in variables and v in rules:
                result += rules[v]

        start = result
    return start


def paint_fractal_binary_tree(painter, value, size=1.0):
    turtle = Turtle(painter)
    turtle.direction = Vec2(0.0, -1.0)
    for k in value:
        if k == '1':
            turtle.forward(1.0 * size)
        elif k == '0':
            turtle.forward(1.0 * size)
        elif k == '[':
            turtle.push()
            turtle.rotate(45.0)
        elif k == ']':
            turtle.pop()
            turtle.rotate(-45.0)


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

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __repr__(self):
        return 'Vec2({}, {})'.format(self.x, self.y)


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

    def push(self):
        self.stack.append((self.position.copy(), self.direction.copy()))

    def pop(self):
        if self.stack:
            self.position, self.direction = self.stack.pop(-1)

    def __draw_line(self, a, b):
        a = self.offset + a * self.scale.x
        b = self.offset + b * self.scale.y
        self.painter.drawLine(a.x, a.y, b.x, b.y)

    def forward(self, value):
        prev_position = self.position
        self.position += self.direction * value
        self.__draw_line(prev_position, self.position)

    def rotate(self, degrees):
        theta = math.radians(degrees)
        cs = math.cos(theta)
        sn = math.sin(theta)

        x = self.direction.x * cs - self.direction.y * sn
        y = self.direction.x * sn + self.direction.y * cs
        self.direction = Vec2(x, y)
        return


class LSystemWidget(QtWidgets.QWidget):
    """lsystem
    """

    def __init__(self):
        super(LSystemWidget, self).__init__()
        self.axiom = ''
        self.result = ''
        self.variables = []
        self.constants = []
        self.rules = {}
        self.iterations = 1
        self.scale = Vec2(1.0, 1.0)

    def calc_result(self):
        res = [i for i in
               calc_lsystem(self.axiom, self.variables, self.constants,
                            self.rules,
                            self.iterations)]

        self.result = res[-1]

    def paintEvent(self, event):
        super(LSystemWidget, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        turtle = Turtle(painter)
        turtle.direction = Vec2(0.0, -1.0)
        turtle.scale = self.scale
        turtle.offset = Vec2(self.width() / 2.0, self.height())

        for k in self.result:
            if k == '0':
                turtle.forward(20.0)
            elif k == '1':
                turtle.forward(20.0)
            elif k == '[':
                turtle.push()
                turtle.rotate(45.0)
            elif k == ']':
                turtle.pop()
                turtle.rotate(-45.0)

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize()


def main():
    app = QtWidgets.QApplication([])
    w = LSystemWidget()
    w.axiom = '0'
    w.variables = ['0', '1']
    w.constants = ['[', ']']
    w.rules = {'1': '11', '0': '1[0]0'}
    w.iterations = 4
    w.scale = Vec2(0.1, 0.1)
    w.calc_result()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
