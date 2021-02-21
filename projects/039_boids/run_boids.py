import math
import random

from PySide2.QtCore import QTimer, QSize, QPointF
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QApplication, QWidget


class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Boid:
    def __init__(self):
        self.pos = Vec2()
        self.dir = Vec2(x=1, y=0)
        self.velocity = 0.5

        self.separation = random.random()
        self.alignment = random.random()
        self.cohesion = random.random()


def add_vec2(vec1, vec2):
    return Vec2(x=vec1.x + vec2.x, y=vec1.y + vec2.y)


def sub_vec2(vec1, vec2):
    return Vec2(x=vec1.x - vec2.x, y=vec1.y - vec2.y)


def mul_vec2(vec, value):
    return Vec2(x=vec.x * value, y=vec.y * value)


def len_vec(vec):
    return math.sqrt(vec.x * vec.x + vec.y * vec.y)


def div_vec(vec, value):
    return Vec2(x=vec.x / value, y=vec.y / value)


def normalize_vec(vec):
    d = 1.0 / len_vec(vec)
    return Vec2(vec.x * d, vec.y * d)


class Environment:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.boids = []
        self.neighbour_max_distance = 50.0


def get_neighbours(environment, boid):
    neighbours = []
    for boid_i in environment.boids:
        if boid_i == boid:
            continue

        distance = len_vec(sub_vec2(boid.pos, boid_i.pos))
        if distance < environment.neighbour_max_distance:
            neighbours.append(boid_i)

    return neighbours


def tick_boid(environment, boid):
    neighbours = get_neighbours(environment, boid)

    # separation
    separation_vec = Vec2()

    if neighbours:

        for neighbour in neighbours:
            diff = sub_vec2(neighbour.pos, boid.pos)
            separation_vec = add_vec2(separation_vec, diff)

        separation_vec = mul_vec2(separation_vec, -1.0)
        separation_vec = normalize_vec(separation_vec)

    separation_vec = mul_vec2(separation_vec, boid.separation)

    # alignment
    alignment_vec = Vec2()

    if neighbours:
        average_direction = Vec2()
        for neighbour in neighbours:
            average_direction = add_vec2(average_direction, neighbour.dir)
        alignment_vec = normalize_vec(average_direction)

    alignment_vec = mul_vec2(alignment_vec, boid.alignment)

    # cohesion
    cohesion_vec = Vec2()
    if neighbours:
        average_pos = Vec2()
        for neighbour in neighbours:
            average_pos = add_vec2(average_pos, neighbour.pos)
        average_pos = div_vec(average_pos, len(neighbours))
        cohesion_vec = normalize_vec(sub_vec2(boid.pos, average_pos))
        # boid.dir = cohesion_vec
    cohesion_vec = mul_vec2(cohesion_vec, boid.cohesion)

    new_dir = boid.dir
    new_dir = add_vec2(new_dir, separation_vec)
    new_dir = add_vec2(new_dir, alignment_vec)
    new_dir = add_vec2(new_dir, cohesion_vec)

    new_dir = normalize_vec(new_dir)

    # boid.dir = new_dir

    boid.dir = normalize_vec(
        add_vec2(boid.dir, mul_vec2(sub_vec2(boid.dir, new_dir), 0.02))
    )


def tick_move_boids(environment, boid):
    # move
    new_pos = add_vec2(boid.pos, mul_vec2(boid.dir, boid.velocity))
    new_pos.x = new_pos.x % environment.width
    new_pos.y = new_pos.y % environment.height
    boid.pos = new_pos


def tick_environment(environment):
    for boid in environment.boids:
        tick_boid(environment, boid)

    for boid in environment.boids:
        tick_move_boids(environment, boid)


def perpendicular_vec_clockwise(vec):
    return Vec2(x=vec.y, y=-vec.x)


def perpendicular_vec_counter_clockwise(vec):
    return Vec2(x=-vec.y, y=vec.x)


def draw_boid(painter, boid):
    size = 10.0
    half_size = size / 2.0
    end_point = add_vec2(boid.pos, mul_vec2(boid.dir, size * 1.5))
    # painter.drawEllipse(boid.pos.x - 10, boid.pos.y - 10, 20, 20)
    # painter.drawLine(boid.pos.x, boid.pos.y, end_point.x, end_point.y)

    side_1 = add_vec2(boid.pos, mul_vec2(perpendicular_vec_clockwise(boid.dir), half_size))
    side_2 = add_vec2(boid.pos, mul_vec2(perpendicular_vec_counter_clockwise(boid.dir), half_size))
    painter.drawLine(side_2.x, side_2.y, end_point.x, end_point.y)
    painter.drawLine(side_1.x, side_1.y, end_point.x, end_point.y)
    painter.drawLine(side_1.x, side_1.y, side_2.x, side_2.y)


class BoidsWidget(QWidget):
    def __init__(self):
        super(BoidsWidget, self).__init__()
        self.setWindowTitle('Boids')
        self.environment = self._make_environment()
        self.tick_timer = QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start()

    def tick(self):
        tick_environment(self.environment)
        self.update()

    def _make_environment(self):
        env = Environment()
        for i in range(50):
            boid = Boid()
            boid.pos.x = random.randint(0, env.width)
            boid.pos.y = random.randint(0, env.height)

            dir = Vec2((random.random() * 2.0) - 1.0, (random.random() * 2.0) - 1.0)
            boid.dir = normalize_vec(dir)

            boid.velocity = 0.5

            env.boids.append(boid)
        return env

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(QPointF(-25, -25))
        for boid in self.environment.boids:
            draw_boid(painter, boid)

    def sizeHint(self):
        return QSize(450, 450)


def main():
    app = QApplication()
    w = BoidsWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
