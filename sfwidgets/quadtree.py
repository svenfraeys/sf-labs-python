"""
Quadtree
https://en.wikipedia.org/wiki/Quadtree
"""
import sys
import math
from PySide2 import QtCore


class Quadtree(object):
    """calculate quad tree
    """
    capacity = 1

    def __init__(self, boundingbox, parent=None):
        self.points = []
        self.depth = 0
        self.parent = parent
        self.north_west = None
        self.north_east = None
        self.south_west = None
        self.south_east = None
        self.boundingbox = boundingbox

    def top(self):
        if not self.parent:
            return None
        if self.parent.south_east == self:
            return self.parent.north_east
        if self.parent.south_west == self:
            return self.parent.north_west
        if self.parent.north_east == self:
            quad = self.parent.top()
            if quad:
                quad = quad.south_east if quad.south_east else quad
            return quad
        if self.parent.north_west == self:
            quad = self.parent.top()
            if quad:
                quad = quad.south_west if quad.south_west else quad
            return quad

    def bottom(self):
        if not self.parent:
            return None
        if self.parent.north_east == self:
            return self.parent.south_east
        if self.parent.north_west == self:
            return self.parent.south_west
        if self.parent.south_east == self:
            quad = self.parent.bottom()
            if quad:
                quad = quad.north_east if quad.north_east else quad
            return quad
        if self.parent.south_west == self:
            quad = self.parent.bottom()
            if quad:
                quad = quad.north_west if quad.north_west else quad
            return quad

    def left(self):
        if not self.parent:
            return None
        if self.parent.north_east == self:
            return self.parent.north_west
        if self.parent.south_east == self:
            return self.parent.south_west
        if self.parent.north_west == self:
            quad = self.parent.left()
            if quad:
                quad = quad.north_east if quad.north_east else quad
            return quad
        if self.parent.south_west == self:
            quad = self.parent.left()
            if quad:
                quad = quad.south_east if quad.south_east else quad
            return quad

    def right(self):
        if not self.parent:
            return None
        if self.parent.north_east == self:
            quad = self.parent.right()
            if quad:
                quad = quad.north_west if quad.north_west else quad
            return quad
        if self.parent.south_east == self:
            quad = self.parent.right()
            if quad:
                quad = quad.south_west if quad.south_west else quad
            return quad
        if self.parent.north_west == self:
            return self.parent.north_east
        if self.parent.south_west == self:
            return self.parent.south_east

    def nearest_quad(self, point):
        if not self.boundingbox.contains(point):
            return None
        if not self.north_west:
            return self

        # get nearest point
        res = self.north_west.nearest_quad(point)
        if res:
            return res
        res = self.north_east.nearest_quad(point)
        if res:
            return res

        res = self.south_east.nearest_quad(point)
        if res:
            return res

        res = self.south_west.nearest_quad(point)
        if res:
            return res

    def nearest_point(self, point):
        if not self.boundingbox.contains(point):
            return None

        # if we have no children check the points in ourselves
        if not self.north_west:
            x = point.x()
            y = point.y()
            lowest_length = sys.float_info.max
            lowest_point = None

            for p in self.points:
                lx = p.x() - x
                ly = p.y() - y
                length = math.sqrt(lx ** 2 + ly ** 2)
                if length < lowest_length:
                    lowest_length = length
                    lowest_point = point
            return lowest_point

        # get nearest point
        res = self.north_west.nearest_point(point)
        if res:
            return res
        res = self.north_east.nearest_point(point)
        if res:
            return res

        res = self.south_east.nearest_point(point)
        if res:
            return res

        res = self.south_west.nearest_point(point)
        if res:
            return res

    def subdivide(self):
        x = self.boundingbox.x()
        y = self.boundingbox.y()
        hwidth = self.boundingbox.width() / 2.0
        hheight = self.boundingbox.height() / 2.0

        self.north_west = Quadtree(QtCore.QRectF(x, y, hwidth, hheight), self)
        self.north_west.depth = self.depth + 1
        self.north_east = Quadtree(
            QtCore.QRectF(x + hwidth, y, hwidth, hheight), self)
        self.north_east.depth = self.depth + 1
        self.south_west = Quadtree(
            QtCore.QRectF(x, y + hheight, hwidth, hheight), self)
        self.south_west.depth = self.depth + 1
        self.south_east = Quadtree(
            QtCore.QRectF(x + hwidth, y + hheight, hwidth, hheight), self)
        self.south_east.depth = self.depth + 1

        for point in self.points:
            self.insert(point)
        self.points = []

    def insert(self, point):
        if not self.boundingbox.contains(point):
            return False

        if not self.north_west and len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if self.north_west is None:
            self.subdivide()

        if self.north_west.insert(point):
            return True
        if self.north_east.insert(point):
            return True
        if self.south_west.insert(point):
            return True
        if self.south_east.insert(point):
            return True

        return False


def paint_quad_tree(painter, quadtree):
    """draw the quad tree
    """
    painter.drawRect(quadtree.boundingbox)
    if quadtree.north_west:
        paint_quad_tree(painter, quadtree.north_west)
        paint_quad_tree(painter, quadtree.north_east)
        paint_quad_tree(painter, quadtree.south_west)
        paint_quad_tree(painter, quadtree.south_east)
