from PySide2 import QtGui, QtCore, QtWidgets
import math


class Branch(object):
    def __init__(self):
        self.size = 10
        self.angle = 45
        self.left = None
        self.right = None

    def split(self):
        self.left = Branch()
        self.left.size = self.size / 2.0

        self.right = Branch()
        self.right.size = self.size / 2.0


class PythagorasTree(object):
    def __init__(self):
        self.n = 1
        self.size = 30
        self.degrees = 45
        self.branch = None

    def leafs_iter(self, branch):
        if not branch.left:
            return [branch]

        leafs = []
        leafs += self.leafs_iter(branch.left)
        leafs += self.leafs_iter(branch.right)
        return leafs

    def generate(self):
        self.branch = Branch()
        self.branch.size = self.size
        self.branch.degrees = self.degrees

        branch_i = self.branch
        for i in range(self.n - 1):
            leafs = self.leafs_iter(branch_i)
            for leaf in leafs:
                leaf.split()


class PythagorasTreePainter(object):
    def __init__(self, x, y, tree, painter=None):
        self.x = x
        self.y = y
        self.tree = tree
        self.degrees = 12
        self.painter = painter

    def paint_line(self, x1, y1, x2, y2):
        y1 = self.y + y1 * -1.0
        x1 = self.x + x1

        y2 = self.y + y2 * -1.0
        x2 = self.x + x2
        self.painter.drawLine(x1, y1, x2, y2)

    def rotate_vec2(self, v, degrees):
        rads = math.radians(degrees)

        angle = math.atan2(v.y(), v.x())
        new_angle = rads + angle
        x = math.cos(new_angle)
        y = math.sin(new_angle)

        v2 = QtGui.QVector2D(x, y)
        v2.normalize()

        return v2

    def paint_square(self, p1, p2, p3, p4):
        objectpos = QtGui.QVector2D(self.x, self.y)
        p1 = QtGui.QVector2D(p1)
        p2 = QtGui.QVector2D(p2)
        p3 = QtGui.QVector2D(p3)
        p4 = QtGui.QVector2D(p4)
        p1.setY(p1.y() * -1)
        p2.setY(p2.y() * -1)
        p3.setY(p3.y() * -1)
        p4.setY(p4.y() * -1)

        p1 = p1 + objectpos
        p2 = p2 + objectpos
        p3 = p3 + objectpos
        p4 = p4 + objectpos

        p = QtGui.QPainterPath()
        p.moveTo(p1.x(), p1.y())
        p.lineTo(p2.x(), p2.y())
        p.lineTo(p3.x(), p3.y())
        p.lineTo(p4.x(), p4.y())
        self.painter.fillPath(p, QtGui.QColor())
        self.painter.drawPath(p)

    def paint_branch(self, pos, direction, branch):
        # self.paint_square(0, 0, branch.size)
        hs = branch.size / 2.0
        size = direction.normalized() * branch.size
        end = pos + size
        # self.paint_line(pos.x(), pos.y(), end.x(), end.y())

        n = self.rotate_vec2(direction, 90)
        p1 = pos + n * hs
        p2 = pos - n * hs
        p3 = end - n * hs
        p4 = end + n * hs
        self.paint_square(p1, p2, p3, p4)

        c = branch.size
        angle = branch.angle
        length = math.cos(math.radians(angle)) * c

        av = end - p4
        cv = self.rotate_vec2(av, branch.angle).normalized() * hs
        top_point = cv.normalized() * length
        cv = p4 + top_point / 2.0

        av = end - p3
        cv2 = self.rotate_vec2(av, -branch.angle).normalized() * hs
        top_point = cv2.normalized() * length
        cv2 = p3 + top_point / 2.0

        left_dir = self.rotate_vec2(direction, -branch.angle)
        right_dir = self.rotate_vec2(direction, branch.angle)

        if branch.left:
            branch.left.size = length
            self.paint_branch(cv2, left_dir, branch.left)
            # self.paint_square(-20, branch.size, branch.size)
        if branch.right:
            branch.right.size = length
            self.paint_branch(cv, right_dir, branch.right)
            # self.paint_square(20, branch.size, branch.size)

    def paint(self):
        self.paint_branch(QtGui.QVector2D(), QtGui.QVector2D(0, 1),
                          self.tree.branch)

