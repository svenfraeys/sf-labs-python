"""maze solving
"""
import random

from PySide2.QtGui import QColor, QPainterPath, QPen

from maze import Maze

"""
base mazeSolver
"""
from PySide2 import QtGui, QtCore, QtWidgets


class MazeSolver:
    def __init__(self, maze, ):
        self.maze = maze
        self.start_slot = None
        self.end_slot = None
        self.solver_color = QColor(45, 45, 180)
        self.visited_slots = []
        self.stack = []
        self.next_slot = None

        self.path_pen = QPen(self.solver_color)
        self.path_pen.setWidth(2)

    def get_unvisited_neighbours(self, slot):
        unvisited_neighbours = []
        if not slot.right_wall:
            right = slot.right()
            if right and right not in self.visited_slots:
                unvisited_neighbours.append(right)
        if not slot.left_wall:
            left = slot.left()
            if left and left not in self.visited_slots:
                unvisited_neighbours.append(left)
        if not slot.top_wall:
            top = slot.top()
            if top and top not in self.visited_slots:
                unvisited_neighbours.append(top)
        if not slot.bottom_wall:
            bottom = slot.bottom()
            if bottom and bottom not in self.visited_slots:
                unvisited_neighbours.append(bottom)
        return unvisited_neighbours

    def reset(self):
        self.visited_slots = []
        self.stack = []
        self.next_slot = None

    def paint_slot(self, painter, slot, rect, size=0.8, color=None):
        chunk_x = rect.width() / float(self.maze.width)
        chunk_y = rect.height() / float(self.maze.height)

        x = slot.x * chunk_x
        y = slot.y * chunk_y
        w = chunk_x
        h = chunk_y
        topleft = 1.0 - size
        bottomright = 1.0 - topleft * 2
        painter.fillRect(x + w * topleft, y + h * topleft, w * bottomright,
                         h * bottomright, color or self.solver_color)

    def start(self):
        self.reset()
        self.solve_slot(self.start_slot)

    def solve_slot(self, slot):
        if slot == self.end_slot:
            self.visited_slots.append(slot)
            self.stack.append(slot)
            self.next_slot = None
            return True

        self.visited_slots.append(slot)

        unvisited_neighbours = self.get_unvisited_neighbours(slot)
        if unvisited_neighbours:
            # if the end is in our neighbours take that
            if self.end_slot in unvisited_neighbours:
                self.next_slot = self.end_slot
            else:
                # other wise take a radon neigbour
                random_neighbour_index = random.randint(0, len(
                    unvisited_neighbours) - 1)
                neighbour = unvisited_neighbours[random_neighbour_index]
                self.next_slot = neighbour

            self.stack.append(slot)

        else:
            if self.stack:
                s = self.stack.pop()
                self.next_slot = s
        return False

    def tick(self):
        if self.next_slot:
            result = self.solve_slot(self.next_slot)
            if result:
                pass

    def paint_stack(self, painter, rect):
        painterpath = QPainterPath()

        chunk_x = rect.width() / float(self.maze.width)
        chunk_y = rect.height() / float(self.maze.height)

        first = True
        for slot in self.stack:
            x = slot.x * chunk_x + chunk_x / 2.0
            y = slot.y * chunk_y + chunk_y / 2.0
            if first:
                painterpath.moveTo(x, y)
                first = False
            else:
                painterpath.lineTo(x, y)

            self.paint_slot(painter, slot, rect, size=0.3)

        painter.setPen(self.path_pen)
        painter.drawPath(painterpath)

    def paint(self, painter, rect):
        for slot in self.visited_slots:
            self.paint_slot(painter, slot, rect, size=0.3,
                            color=QColor(200, 200, 200))
        self.paint_slot(painter, self.start_slot, rect, size=0.8)
        self.paint_slot(painter, self.end_slot, rect, size=0.8)

        self.paint_stack(painter, rect)


class MazeSolverDemoWidget(QtWidgets.QWidget):
    """
    MazeSolver
    """

    def __init__(self):
        super(MazeSolverDemoWidget, self).__init__()
        self.setWindowTitle("MazeSolver")
        self.tick_timer = QtCore.QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.maze = Maze(20, 20)
        self.maze_solver = MazeSolver(self.maze)

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def showEvent(self, event):
        self.maze.generate(solve=True)
        self.maze_solver.start_slot = self.maze.slots[0]
        self.maze_solver.end_slot = self.maze.slots[-1]
        self.maze_solver.start()

        self.tick_timer.start()
        self.update()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.maze.paint(painter, self.rect())
        self.maze_solver.paint(painter, self.rect())

    def tick(self):
        self.maze_solver.tick()
        self.update()

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.maze.generate(solve=True)
            self.maze_solver.start_slot = self.maze.slots[0]
            self.maze_solver.end_slot = self.maze.slots[-1]
            self.maze_solver.start()
            self.update()

        if event.key() == QtCore.Qt.Key_Up:
            self.maze.width *= 2
            self.maze.height *= 2
            self.maze.generate(solve=True)
            self.maze_solver.start_slot = self.maze.slots[0]
            self.maze_solver.end_slot = self.maze.slots[-1]
            self.maze_solver.start()
            self.update()

        if event.key() == QtCore.Qt.Key_Down:
            self.maze.width = int(self.maze.width / 2)
            self.maze.height = int(self.maze.height / 2)
            self.maze.generate(solve=True)
            self.maze_solver.start_slot = self.maze.slots[0]
            self.maze_solver.end_slot = self.maze.slots[-1]
            self.maze_solver.start()
            self.update()


def main():
    app = QtWidgets.QApplication([])
    widget = MazeSolverDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
