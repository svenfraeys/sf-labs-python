"""
base SnakeGame
"""
import random

from PySide2 import QtGui, QtCore, QtWidgets
from PySide2.QtCore import QTimer
from PySide2.QtGui import QPen, QColor, QVector2D


class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SnakeBody:
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent


class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.direction = QVector2D(1, 0)

    def go_left(self):
        if self.direction == QVector2D(1, 0):
            return
        self.direction = QVector2D(-1, 0)

    def go_right(self):
        if self.direction == QVector2D(-1, 0):
            return
        self.direction = QVector2D(1, 0)

    def go_up(self):
        if self.direction == QVector2D(0, 1):
            return
        self.direction = QVector2D(0, -1)

    def go_down(self):
        if self.direction == QVector2D(0, -1):
            return
        self.direction = QVector2D(0, 1)


class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []

    def generate(self):
        self.grid = [0.0] * self.width * self.height


class SnakeGame:
    def __init__(self):
        self.snake = Snake(10, 10)
        self.pauzed = False
        self.bodies = []
        self.last_body = None
        self.grid = Grid(20, 20)
        self.food = Food(12, 10)
        self.grid.generate()
        self.__width = None
        self.__height = None
        self.x_chunk = 0
        self.y_chunk = 0
        self.game_over = False

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, value):
        self.x_chunk = value / self.grid.width
        self.__width = value

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.y_chunk = value / self.grid.height
        self.__height = value

    def paint_grid(self, painter):
        painter.setPen(QPen(QColor(200, 200, 200)))

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                painter.drawRect(x * self.x_chunk, y * self.y_chunk,
                                 self.x_chunk, self.y_chunk)

    def paint_snake(self, painter):

        painter.fillRect(self.snake.x * self.x_chunk,
                         self.snake.y * self.y_chunk, self.x_chunk,
                         self.y_chunk, QColor())

    def paint_rect(self, painter, x, y, size):
        # 0.8
        diff = 1.0 - size
        diff_s = 1.0 - diff * 2
        painter.fillRect(x * self.x_chunk + self.x_chunk * diff,
                         y * self.y_chunk + self.y_chunk * diff,
                         self.x_chunk * diff_s, self.y_chunk * diff_s,
                         QColor())

    def paint_food(self, painter):
        painter.fillRect(self.food.x * self.x_chunk + self.x_chunk * 0.2,
                         self.food.y * self.y_chunk + self.y_chunk * 0.2,
                         self.x_chunk * 0.6, self.y_chunk * 0.6, QColor())

    def paint_bodies(self, painter):
        for body in self.bodies:
            self.paint_rect(painter, body.x, body.y, 0.9)

    def paint(self, painter):

        self.paint_grid(painter)
        self.paint_snake(painter)
        self.paint_food(painter)
        self.paint_bodies(painter)
        if self.game_over:
            painter.setPen(QPen(QColor()))

            text = "GAME OVER"
            painter.drawText(self.width / 2 - 35, self.height / 3, text)

    def add_new_part(self):
        body = SnakeBody(self.snake.x, self.snake.y,
                         self.last_body or self.snake)
        self.bodies.append(body)
        self.last_body = body

    def tick(self):
        if self.pauzed:
            return

        if self.game_over:
            return

        next_x = self.snake.x + self.snake.direction.x()
        next_y = self.snake.y + self.snake.direction.y()

        # if you go out of the grid it is game over
        if next_x > self.grid.width - 1 or next_x < 0:
            self.game_over = True
            return

        if next_y > self.grid.height - 1 or next_y < 0:
            self.game_over = True
            return

        for body in self.bodies:
            if body.x == next_x and body.y == next_y:
                self.game_over = True
                return

        # move the bodies to the parent
        for body in reversed(self.bodies):
            body.x = body.parent.x
            body.y = body.parent.y

        # move the snake head
        self.snake.x = next_x
        self.snake.y = next_y

        # snake eats the food add new part
        if self.snake.x == self.food.x and self.snake.y == self.food.y:
            self.food.x = random.randint(0, self.grid.width - 1)
            self.food.y = random.randint(0, self.grid.height - 1)

            self.add_new_part()

    def reset(self):
        self.bodies = []
        self.last_body = None
        self.snake.x = 10
        self.snake.y = 10

    def key_pressed(self, key):
        if self.game_over:
            self.reset()
            self.game_over = False
        if key == QtCore.Qt.Key_Left:
            self.snake.go_left()
        if key == QtCore.Qt.Key_Right:
            self.snake.go_right()
        if key == QtCore.Qt.Key_Up:
            self.snake.go_up()
        if key == QtCore.Qt.Key_Down:
            self.snake.go_down()

        if key == QtCore.Qt.Key_Escape:
            self.pauzed = not self.pauzed


class SnakeGameDemoWidget(QtWidgets.QWidget):
    """
    SnakeGame
    """

    def __init__(self):
        super(SnakeGameDemoWidget, self).__init__()
        self.resize(QtCore.QSize(300, 300))
        self.setWindowTitle("SnakeGame")
        self.snake_game = SnakeGame()
        self.snake_game.width = self.width()
        self.snake_game.height = self.height()
        self.tick_timer = QTimer()
        self.tick_timer.setInterval(100)
        self.tick_timer.timeout.connect(self.tick)

    def showEvent(self, event):
        self.tick_timer.start()

    def closeEvent(self, event):
        self.tick_timer.stop()

    def tick(self):
        self.snake_game.tick()
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.snake_game.paint(painter)

    def keyPressEvent(self, event):
        self.snake_game.key_pressed(event.key())

    def sizeHint(self):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    widget = SnakeGameDemoWidget()
    widget.show()
    app.exec_()


if __name__ == '__main__':
    main()
