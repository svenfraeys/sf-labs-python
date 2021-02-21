import math
import random

from PySide2.QtCore import QTimer, QSize, QPointF
from PySide2.QtGui import QPainter, QPen, QColor
from PySide2.QtWidgets import QApplication, QWidget


class Vec2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Vec2(x={!r}, y={!r})'.format(self.x, self.y)


class Boid:
    def __init__(self):
        self.pos = Vec2()
        self.dir = Vec2(x=1, y=0)
        self.velocity = 0.5
        # self.steering = random.random() * 0.1

        self.separation = random.random() * 0.8
        self.alignment = 0.5 + random.random() * 0.5
        self.cohesion = random.random() * 0.5
        self.debug = False
        self.eyesight = math.radians(120)

        self.steering = 0.005

        # self.separation = 0.0
        # self.alignment = 1.0
        # self.cohesion = 0.0


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
    length = len_vec(vec)
    return Vec2(vec.x / length, vec.y / length)


def dot_vec(vec1, vec2):
    return vec1.x * vec2.x + vec1.y * vec2.y


class Environment:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.boids = []
        self.neighbour_max_distance = 100.0


def get_neighbours(environment, boid):
    neighbours = []
    for boid_i in environment.boids:
        if boid_i == boid:
            continue
        dist_vec = sub_vec2(boid_i.pos, boid.pos)
        distance = len_vec(dist_vec)
        if distance == 0.0:
            neighbours.append(boid_i)
        elif distance <= environment.neighbour_max_distance:
            dist_normalised = normalize_vec(dist_vec)
            dot = dot_vec(normalize_vec(boid.dir), dist_normalised)
            # radians = math.acos(dot)
            # radians = math.atan2(dist_normalised.y, dist_normalised.x)
            if dot > 1.0:
                dot = 1.0
            try:
                angle = math.acos(dot)
            except ValueError:
                angle = 0

            if boid.debug:
                pass

            if abs(angle) > boid.eyesight:
                continue

            neighbours.append(boid_i)

    return neighbours


def _calc_separation_vec(boid, neighbours):
    separation_vec = Vec2()
    for neighbour in neighbours:
        diff = sub_vec2(neighbour.pos, boid.pos)
        separation_vec = add_vec2(separation_vec, diff)

    separation_vec = mul_vec2(separation_vec, -1.0)
    separation_vec = normalize_vec(separation_vec)
    return separation_vec


def _calc_alignment_vec(boid, neighbours):
    average_direction = Vec2()
    for neighbour in neighbours:
        average_direction = add_vec2(average_direction, neighbour.dir)
    alignment_vec = normalize_vec(average_direction)
    return alignment_vec


def _calc_cohesion(boid, neighbours):
    average_pos = Vec2()
    for neighbour in neighbours:
        average_pos = add_vec2(average_pos, neighbour.pos)
    average_pos = div_vec(average_pos, len(neighbours))
    cohesion_vec = normalize_vec(sub_vec2(average_pos, boid.pos))
    return cohesion_vec


def tick_boid(environment, boid):
    neighbours = get_neighbours(environment, boid)

    # separation
    separation_vec = Vec2()

    if neighbours:
        separation_vec = _calc_separation_vec(boid, neighbours)

    separation_vec = mul_vec2(separation_vec, boid.separation)

    # alignment
    alignment_vec = Vec2()

    if neighbours:
        alignment_vec = _calc_alignment_vec(boid, neighbours)

    alignment_vec = mul_vec2(alignment_vec, boid.alignment)

    # cohesion
    cohesion_vec = Vec2()
    if neighbours:
        cohesion_vec = _calc_cohesion(boid, neighbours)

    cohesion_vec = mul_vec2(cohesion_vec, boid.cohesion)

    new_dir = Vec2()
    if neighbours:
        new_dir = add_vec2(new_dir, separation_vec)
        new_dir = add_vec2(new_dir, alignment_vec)
        new_dir = add_vec2(new_dir, cohesion_vec)
        new_dir = normalize_vec(new_dir)
    else:
        new_dir = boid.dir

    # boid.dir = new_dir

    dot = dot_vec(normalize_vec(boid.dir), new_dir)
    if dot > 1.0:
        dot = 1.0
    angle = math.acos(dot)

    # if angle > 180.0:
    #     print(math.degrees(angle))

    v = rotate(boid.dir, angle)
    angle = math.atan2(v.y, v.x)
    # print(angle)
    boid.dir = rotate(boid.dir, angle * boid.steering)

    # boid.dir = normalize_vec(
    #     add_vec2(boid.dir, mul_vec2(sub_vec2(boid.dir, new_dir), boid.steering))
    # )


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


def rotate(vec, angle):
    x = vec.x * math.cos(angle) - vec.y * math.sin(angle)
    y = vec.x * math.sin(angle) + vec.y * math.cos(angle)
    return Vec2(x=x, y=y)


def perpendicular_vec_clockwise(vec):
    return Vec2(x=vec.y, y=-vec.x)


def perpendicular_vec_counter_clockwise(vec):
    return Vec2(x=-vec.y, y=vec.x)


def _draw_boid_debug_line(painter, boid, vec):
    dir_draw = add_vec2(boid.pos, vec)
    painter.drawLine(boid.pos.x, boid.pos.y, dir_draw.x, dir_draw.y)


def draw_boid(painter, environment, boid):
    size = 10.0
    half_size = size / 2.0
    end_point = add_vec2(boid.pos, mul_vec2(boid.dir, size * 1.5))
    # painter.drawEllipse(boid.pos.x - 10, boid.pos.y - 10, 20, 20)
    # painter.drawLine(boid.pos.x, boid.pos.y, end_point.x, end_point.y)

    side_1 = add_vec2(boid.pos, mul_vec2(perpendicular_vec_clockwise(boid.dir), half_size))
    side_2 = add_vec2(boid.pos, mul_vec2(perpendicular_vec_counter_clockwise(boid.dir), half_size))
    pen = QPen()
    color = QColor()
    if boid.debug:
        color.setRgb(200, 0, 0)
    else:
        color.setRgb(0, 0, 0)
    pen.setColor(color)
    painter.setPen(pen)
    painter.drawLine(side_2.x, side_2.y, end_point.x, end_point.y)
    painter.drawLine(side_1.x, side_1.y, end_point.x, end_point.y)
    painter.drawLine(side_1.x, side_1.y, side_2.x, side_2.y)

    if boid.debug:
        max_dist = environment.neighbour_max_distance
        pen.setColor(color)
        _draw_boid_debug_line(painter, boid, mul_vec2(boid.dir, max_dist))
        # draw direction
        sight_one = mul_vec2(rotate(boid.dir, boid.eyesight), max_dist)
        sight_two = mul_vec2(rotate(boid.dir, -boid.eyesight), max_dist)
        _draw_boid_debug_line(painter, boid, sight_one)
        _draw_boid_debug_line(painter, boid, sight_two)

        # draw range
        painter.drawEllipse(boid.pos.x - max_dist, boid.pos.y - max_dist, max_dist * 2.0,
                            max_dist * 2.0)

        # draw detected neighbourds
        neighbours = get_neighbours(environment, boid)
        for neighbour in neighbours:
            painter.drawEllipse(neighbour.pos.x - 2, neighbour.pos.y - 2, 4, 4)

        if neighbours:
            separation_vec = _calc_separation_vec(boid, neighbours)
            _draw_boid_debug_line(painter, boid, mul_vec2(separation_vec, 50))

            alignment_vec = _calc_alignment_vec(boid, neighbours)
            color = QColor()
            color.setRgb(0, 200, 200)
            pen.setColor(color)
            painter.setPen(pen)
            _draw_boid_debug_line(painter, boid, mul_vec2(alignment_vec, 50))

            cohesion = _calc_cohesion(boid, neighbours)
            color = QColor()
            color.setRgb(0, 120, 0)
            pen.setColor(color)
            painter.setPen(pen)
            _draw_boid_debug_line(painter, boid, mul_vec2(cohesion, 50))


class BoidsWidget(QWidget):
    def __init__(self):
        super(BoidsWidget, self).__init__()
        self.setWindowTitle('Boids')
        self.environment = self._make_environment()
        self.tick_timer = QTimer()
        self.tick_timer.setInterval(10)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start()

    def tick(self):
        tick_environment(self.environment)
        self.update()

    def _make_environment(self):
        env = Environment()
        for i in range(200):
            boid = Boid()
            boid.pos.x = random.randint(50, env.width - 100)
            boid.pos.y = random.randint(50, env.height - 100)

            dir = Vec2((random.random() * 2.0) - 1.0, (random.random() * 2.0) - 1.0)
            boid.dir = normalize_vec(dir)

            # boid.velocity = 0.5

            env.boids.append(boid)
        env.boids[0].debug = True
        env.boids[0].pos = Vec2(env.width / 2.0, env.height / 2.0)
        return env

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(QPointF(-25, -25))
        for boid in self.environment.boids:
            draw_boid(painter, self.environment, boid)

    def sizeHint(self):
        return QSize(450, 450)


def main():
    import cProfile
    p = cProfile.Profile()
    p.enable()
    app = QApplication()
    w = BoidsWidget()
    w.show()
    app.exec_()
    p.disable()
    p.print_stats()


def test_vec():
    vec1 = normalize_vec(Vec2(x=1.0, y=-1.0))
    vec2 = Vec2(x=1.0, y=0.0)
    diff = sub_vec2(vec1, vec2)
    angle = math.acos(dot_vec(vec1, vec2))
    print(angle)
    print(math.degrees(angle))

    print(rotate(Vec2(0.0, 1.0), math.radians(90)))

    print(dot_vec(Vec2(1.0, 0.0), Vec2(0.0, -1.0)))
    print(math.degrees(math.atan2(-1.0, 1.0)))


if __name__ == '__main__':
    main()
