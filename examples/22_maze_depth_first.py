"""
base MazeDepthFirst
"""
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QTimer
from PySide2.QtGui import QColor, QPen


class Slot:
    def __init__(self, maze, x, y):
        self.maze = maze
        self.x = x
        self.y = y
        self.visited = False
        self.top_wall = True
        self.bottom_wall = True
        self.right_wall = True
        self.left_wall = True

    def left(self):
        return self.maze.get_slot(self.x - 1, self.y)

    def right(self):
        return self.maze.get_slot(self.x + 1, self.y)

    def top(self):
        return self.maze.get_slot(self.x, self.y - 1)

    def bottom(self):
        return self.maze.get_slot(self.x, self.y + 1)

    def __repr__(self):
        return 'Slot({}, {})'.format(self.x, self.y)


class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.repaint = None
        self.pauze = False
        self.slots = []
        self.stack = []
        self.unvisited_slot_color = QColor(20, 20, 20)
        self.visited_slot_color = QColor(240, 240, 240)
        self.foreground_color = QColor(120,120,120)
        self.background_color = QColor(50, 50, 50)
        self.next_slot = None

    def get_slot(self, x, y):
        if x < 0 or y < 0:
            return None
        if x >= self.width:
            return

        if y >= self.height:
            return

        index = self.width * y + x
        if index < 0:
            return None

        if index >= len(self.slots):
            return None

        return self.slots[index]

    def generate_grid(self):
        self.slots = []
        for y in range(self.height):
            for x in range(self.width):
                s = Slot(self, x, y)
                self.slots.append(s)

    def unvisited_neighbours(self, slot):
        top = slot.top()
        bottom = slot.bottom()
        left = slot.left()
        right = slot.right()

        unvisited_neigbours = []
        if top and not top.visited:
            unvisited_neigbours.append(top)
        if bottom and not bottom.visited:
            unvisited_neigbours.append(bottom)
        if left and not left.visited:
            unvisited_neigbours.append(left)
        if right and not right.visited:
            unvisited_neigbours.append(right)
        return unvisited_neigbours

    def pick_random_unvisited(self, slot):
        unvisited_neigbours = self.unvisited_neighbours(slot)
        rand_index = random.randint(0, len(unvisited_neigbours) - 1)
        return unvisited_neigbours[rand_index]

    def break_walls(self, slot0, slot1):
        if slot0.left() == slot1:
            slot0.left_wall = False
            slot1.right_wall = False
        if slot0.right() == slot1:
            slot0.right_wall = False
            slot1.left_wall = False
        if slot0.top() == slot1:
            slot0.top_wall = False
            slot1.bottom_wall = False
        if slot0.bottom() == slot1:
            slot0.bottom_wall = False
            slot1.top_wall = False

    def generate_maze(self, slot):
        if self.unvisited_neighbours(slot):
            self.stack.append(slot)
            rand_slot = self.pick_random_unvisited(slot)

            rand_slot.visited = True
            self.break_walls(slot, rand_slot)
            self.next_slot = rand_slot
        else:
            if self.stack:
                s = self.stack.pop()
                self.next_slot = s

    def generate(self):
        self.generate_grid()

        rand_x = random.randint(0, self.width - 1)
        rand_y = random.randint(0, self.height - 1)

        slot = self.slots[rand_y * self.height + rand_x]
        slot.visited = True

        self.generate_maze(slot)

    def tick(self):
        if self.pauze:
            return
        if self.next_slot:
            self.generate_maze(self.next_slot)

    def paint_slot(self, painter, slot, rect):
        chunk_x = rect.width() / float(self.width)
        chunk_y = rect.height() / float(self.height)

        x = slot.x * chunk_x
        y = slot.y * chunk_y
        w = chunk_x
        h = chunk_y
        if not slot.visited:
            painter.fillRect(x, y, w, h, self.background_color)
        else:
            painter.fillRect(x, y, w, h, self.visited_slot_color)
        if slot.visited:
            if slot.top_wall:
                painter.drawLine(x, y, x + w, y)
            if slot.bottom_wall:
                painter.drawLine(x, y + h, x + w, y + h)
            if slot.left_wall:
                painter.drawLine(x, y, x, y + h)
            if slot.right_wall:
                painter.drawLine(x + w, y, x + w, y + h)

    def paint(self, painter, rect):
        painter.fillRect(rect, self.background_color)
        pen = QPen()
        pen.setColor(self.foreground_color)
        pen.setWidth(2)
        painter.setPen(pen)

        for slot in self.slots:
            self.paint_slot(painter, slot, rect)


class MazeDepthFirstDemoWidget(QtWidgets.QWidget):
    """
    MazeDepthFirst
    """

    def __init__(self):
        super(MazeDepthFirstDemoWidget, self).__init__()
        self.setWindowTitle("MazeDepthFirst")
        self.maze = Maze(20, 20)
        self.maze.repaint = self.repaint
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.tick)
        self.timer.start()

    def tick(self):
        self.maze.tick()
        self.update()

    def mousePressEvent(self, *args, **kwargs):
        self.maze.generate()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.maze.pauze = not self.maze.pauze
            self.update()
        if event.key() == QtCore.Qt.Key_Up:
            self.maze.width *= 2
            self.maze.height *= 2
            self.maze.generate()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.maze.width = int(self.maze.width / 2)
            self.maze.height = int(self.maze.height / 2)
            self.maze.generate()
            self.update()

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        slot_x = x / float(self.width()) * self.maze.width
        slot_y = y / float(self.height()) * self.maze.height
        slot = self.maze.get_slot(int(slot_x), int(slot_y))

        print("""
        x: {} y: {}
        top: {}
        left: {}
        right: {}
        bottom: {}
        left {}
        right {}
        """.format(slot.x, slot.y, slot.top(), slot.left(), slot.right(), slot.bottom(), slot.left_wall, slot.right_wall))


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.maze.paint(painter, self.rect())

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = MazeDepthFirstDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
