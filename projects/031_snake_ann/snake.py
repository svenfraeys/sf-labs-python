import random

from PySide2 import QtCore
from PySide2.QtCore import QRect
from PySide2.QtGui import QPen, QColor, QVector2D


class Food(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SnakeBody(object):
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent


class Snake(object):
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


class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = []

    def generate(self):
        self.grid = [0.0] * self.width * self.height


class SnakeGame(object):
    def __init__(self):
        self.rect = QRect()
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
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.snake_color = QColor()
        self.game_over_color = QColor(150, 150, 150)
        self.grid_color = QColor(200, 200, 200)
        self.game_over_grid_color = QColor(230, 230, 230)
        self.food_positions = []
        self.deterministic_food = True
        self.food_index = 0

    @property
    def width(self):
        return self.rect.width()

    @width.setter
    def width(self, value):
        self.x_chunk = float(value) / float(self.grid.width)
        self.__width = value

    @property
    def height(self):
        return self.__height

    @height.setter
    def height(self, value):
        self.y_chunk = value / self.grid.height
        self.__height = value

    def paint_grid(self, painter):
        color = self.grid_color
        if self.game_over:
            color = self.game_over_grid_color
        painter.setPen(QPen(color))

        for x in range(self.grid.width):
            for y in range(self.grid.height):
                painter.drawRect(x * self.x_chunk, y * self.y_chunk,
                                 self.x_chunk, self.y_chunk)

    def paint_snake(self, painter):
        color = self.snake_color
        if self.game_over:
            color = self.game_over_color
        painter.fillRect(self.snake.x * self.x_chunk,
                         self.snake.y * self.y_chunk, self.x_chunk,
                         self.y_chunk, color)

    def paint_rect(self, painter, x, y, size, color):
        # 0.8
        diff = 1.0 - size
        diff_s = 1.0 - diff * 2
        painter.fillRect(x * self.x_chunk + self.x_chunk * diff,
                         y * self.y_chunk + self.y_chunk * diff,
                         self.x_chunk * diff_s, self.y_chunk * diff_s,
                         color)

    def paint_food(self, painter):
        color = self.snake_color
        if self.game_over:
            color = self.game_over_color
        painter.fillRect(self.food.x * self.x_chunk + self.x_chunk * 0.2,
                         self.food.y * self.y_chunk + self.y_chunk * 0.2,
                         self.x_chunk * 0.6, self.y_chunk * 0.6, color)

    def paint_bodies(self, painter):
        color = self.snake_color
        if self.game_over:
            color = self.game_over_color

        for body in self.bodies:
            self.paint_rect(painter, body.x, body.y, 0.9, color)

    def paint(self, painter):

        self.paint_grid(painter)
        self.paint_snake(painter)
        self.paint_food(painter)
        self.paint_bodies(painter)

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
        
        if self.game_won:
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
            self.score += 1
            self.next_food()
            self.add_new_part()

    def next_food(self):
        if self.deterministic_food:
            if self.score == len(self.food_positions):
                self.game_won = True
                return
            self.food.x, self.food.y = self.food_positions[self.food_index]
            self.food_index += 1
        else:
            self.food.x = random.randint(0, self.grid.width - 1)
            self.food.y = random.randint(0, self.grid.height - 1)

    def setup(self):
        self.next_food()

    def reset(self):
        self.bodies = []
        self.score = 0
        self.last_body = None
        self.snake.x = 10
        self.snake.y = 10
        self.game_over = False
        self.game_won = False
        self.food_index = 0
        self.next_food()

    def key_pressed(self, key):
        if self.game_over or self.game_won:
            self.reset()
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
