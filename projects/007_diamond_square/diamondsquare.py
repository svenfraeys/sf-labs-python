import random
from PySide2 import QtWidgets, QtGui, QtCore


def map_value(value, left_min, left_max, right_min, right_max):
    """map a value between a given min and max
    """
    left_span = left_max - left_min
    right_span = right_max - right_min

    normalized_value = (value - left_min) / left_span
    right_value = (normalized_value * right_span) + right_min
    return right_value


class DiamonSquare(object):
    def __init__(self, n):
        self.size = 2 ** n + 1
        self.lower = -0.1
        self.higher = 0.1
        self.lowest = 0.0
        self.highest = 0.0
        self.n = n
        self.grid = []
        self.create_grid()

    def create_grid(self):
        grid = []
        # make a black grid
        for x in range(self.size):
            line = []
            grid.append(line)
            for y in range(self.size):
                line.append(0.0)
        self.grid = grid

    def reset(self):
        self.lower = -0.1
        self.higher = 0.1
        self.lowest = 0.0
        self.highest = 0.0

    def set_n(self, n):
        self.reset()
        self.n = n
        self.size = 2 ** n + 1
        self.create_grid()

    def square_step(self, x, y, step_size):
        hstep = int(step_size / 2)
        grid = self.grid
        left = grid[x - hstep][y]
        right = grid[x + hstep][y]
        bottom = grid[x][y + hstep]
        top = grid[x][y - hstep]
        avg = (left + right + bottom + top) / 4.0
        r = random.uniform(self.lower, self.higher)
        grid[x][y] = avg + r
        if grid[x][y] < self.lowest:
            self.lowest = grid[x][y]
        if grid[x][y] > self.highest:
            self.highest = grid[x][y]

    def diamond_step(self, x, y, step_size):
        hstep = step_size / 2
        hstep =int(hstep)
        grid = self.grid
        # print "diamond", x, y
        # get the square
        tl = grid[x][y]
        tr = grid[x + step_size][y]
        bl = grid[x][y + step_size]
        br = grid[x + step_size][y + step_size]

        v = (tl + tr + bl + br) / 4.0
        r = random.uniform(self.lower, self.higher)

        dx = int(x + hstep)
        dy = int(y + hstep)
        grid[dx][dy] = r + v
        if grid[dx][dx] < self.lowest:
            self.lowest = grid[dx][dx]
        if grid[dx][dx] > self.highest:
            self.highest = grid[dx][dx]

    def generate(self):
        # fill corners
        grid = self.grid
        size = self.size
        grid[0][0] = 0.2
        grid[0][size - 1] = 0.1
        grid[-1][0] = 0.9
        grid[-1][size - 1] = 0.6

        step_size = int(size - 1)

        # print step_size

        while step_size > 1:
            hstep = int(step_size / 2)
            # diamond step

            for x in range(0, len(grid) - 1, int(step_size)):
                for y in range(0, len(grid[x]) - 1, int(step_size)):
                    self.diamond_step(x, y, int(step_size))

            even = True
            for x in range(0, int(len(grid) - 1), int(hstep)):
                y_start = 0 if even else hstep
                for y in range(int(y_start), int(len(grid[x]) - 1), int(hstep)):
                    self.square_step(x, y, step_size)
                even = not even
            step_size /= 2
            self.lower += 0.005
            self.higher -= 0.005


class DiamondSquareWidget(QtWidgets.QWidget):
    def __init__(self, n):
        super(DiamondSquareWidget, self).__init__()
        self.diamond_square = DiamonSquare(n)
        self.diamond_square.generate()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        w = float(self.width()) / float(self.diamond_square.size)
        h = float(self.height()) / float(self.diamond_square.size)

        for x in range(self.diamond_square.size):
            for y in range(self.diamond_square.size):
                value = self.diamond_square.grid[x][y]
                value = map_value(value, self.diamond_square.lowest,
                                  self.diamond_square.highest, 0, 255)
                c = QtGui.QColor(value, value, value)

                painter.setBrush(QtGui.QBrush(c))
                painter.setPen(QtGui.QPen(c))
                painter.drawRect(x * w, y * h, w, h)

    def sizeHint(self):
        return QtCore.QSize(300, 300)
