import sys
from PySide2 import QtGui, QtCore


class Leaf(object):
    def __init__(self, pos):
        self.pos = pos
        self.reached = False


class Branch(object):
    def __init__(self, pos, direction, parent=None):
        self.parent = parent
        self.pos = pos
        if direction is None:
            direction = QtGui.QVector2D(0.0, -1.0)
        self.original_direction = QtGui.QVector2D(direction)
        self.direction = direction
        self.count = 0

    def reset(self):
        self.count = 0

    def paint(self, painter):
        if self.parent:
            painter.drawLine(int(self.parent.pos.x()), int(self.parent.pos.y()),
                             int(self.pos.x()),
                             int(self.pos.y()))

    def next_(self):
        new_pos = QtGui.QVector2D(self.pos + self.direction)
        new_dir = QtGui.QVector2D(self.direction)

        return Branch(new_pos, new_dir, self)


class Tree(QtCore.QObject):
    updated = QtCore.Signal()

    def __init__(self, pos, direction, points):
        super(Tree, self).__init__()
        self.leaves = [Leaf(p) for p in points]
        if direction:
            direction = QtGui.QVector2D(direction)
        self.root = Branch(pos, direction)
        self.branches = [self.root]
        self.active_branches = list(self.branches)
        self.max_dist = 10
        self.min_dist = 2
        self._grow_counter = 0

    def distance(self, p1, p2):
        diff = p1 - p2
        return diff.length()

    def send_update(self):

        self.updated.emit()

    def generate(self):
        branch_i = self.root
        found = False
        i = 0

        # draw the line upwards
        while not found:
            i += 1
            for leaf in self.leaves:
                distance = self.distance(leaf.pos, branch_i.pos)
                if distance < self.max_dist:
                    found = True

            if not found:
                branch_i = branch_i.next_()
                self.branches.append(branch_i)
                self.send_update()

        self.active_branches = [branch_i]
        while self.leaves:
            self.grow()

    def grow(self):
        self._grow_counter += 1
        # start attracting
        for leaf_i in self.leaves:
            closest_branch = None
            record = sys.float_info.max
            for branch_i in self.active_branches:
                distance = self.distance(leaf_i.pos, branch_i.pos)
                if distance < self.min_dist:
                    leaf_i.reached = True
                    closest_branch = None
                    continue

                if distance < record:
                    closest_branch = branch_i
                    record = distance

            if closest_branch:
                new_dir = leaf_i.pos - closest_branch.pos
                new_dir.normalize()
                new_length = 1.0
                closest_branch.direction += new_dir * new_length
                closest_branch.count += 1

        # cleanup reached leaves
        for i in reversed(range(len(self.leaves))):
            leaf = self.leaves[i]
            if leaf.reached:
                self.leaves.pop(i)

        # split the branches with a count
        for i in reversed(range(len(self.active_branches))):
            branch = self.active_branches[i]
            if branch.count > 0:
                branch.direction /= branch.count + 1
                branch_next = branch.next_()
                self.branches.append(branch_next)
                self.active_branches.append(branch_next)
                branch.reset()
            else:
                self.active_branches.pop(i)

        self.send_update()

    def paint(self, painter):
        for branch in self.branches:
            branch.paint(painter)

