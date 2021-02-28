import math
import random
from pstats import SortKey

from PySide2.QtCore import QTimer, QSize, QPointF, Qt
from PySide2.QtGui import QPainter, QPen, QColor
from PySide2.QtWidgets import QApplication, QWidget


class Vec2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Vec2(x={!r}, y={!r})'.format(self.x, self.y)


class Environment:
    def __init__(self):
        self.width = 500
        self.height = 500
        self.boids = []
        self.neighbour_max_distance = 200.0
        self.neighbour_max_distance2 = self.neighbour_max_distance * self.neighbour_max_distance


class Boid:
    def __init__(self):
        self.pos = Vec2()
        self.velocity = Vec2()
        # self.steering = random.random() * 0.1

        self.debug = False
        self.eyesight = math.radians(120)

        self.steering = 0.05

        self.separation = 1.0
        self.alignment = 1.0
        self.cohesion = 1.0


def add_vec2(vec1, vec2):
    return Vec2(x=vec1.x + vec2.x, y=vec1.y + vec2.y)


def sub_vec2(vec1, vec2):
    return Vec2(x=vec1.x - vec2.x, y=vec1.y - vec2.y)


def substract_vec2(vec1, vec2):
    vec1.x -= vec2.x
    vec1.y -= vec2.y


def mul_vec2(vec, value):
    return Vec2(x=vec.x * value, y=vec.y * value)


def len_vec(vec):
    return math.sqrt(vec.x * vec.x + vec.y * vec.y)


def div_vec(vec, value):
    return Vec2(x=vec.x / value, y=vec.y / value)


def normalized_vec(vec):
    length = len_vec(vec)
    return Vec2(vec.x / length, vec.y / length)


def dot_vec(vec1, vec2):
    return vec1.x * vec2.x + vec1.y * vec2.y


def get_neighbours(environment, boid):
    neighbours = []
    dist_vec = Vec2()
    for boid_i in environment.boids:
        if boid_i == boid:
            continue
        dist_vec.x = boid_i.pos.x
        dist_vec.y = boid_i.pos.y
        substract_vec2(dist_vec, boid.pos)
        # distance = len_vec(dist_vec)
        dist_dist = dist_vec.x * dist_vec.x + dist_vec.y * dist_vec.y
        if dist_dist == 0.0:
            neighbours.append(boid_i)
        elif dist_dist <= environment.neighbour_max_distance2:
            dist_normalised = normalized_vec(dist_vec)
            dot = dot_vec(boid.velocity, dist_normalised)
            # radians = math.acos(dot)
            # radians = math.atan2(dist_normalised.y, dist_normalised.x)
            if dot > 1.0:
                dot = 1.0
            if dot < -1.0:
                dot = 1.0

            angle = math.acos(dot)

            if abs(angle) > boid.eyesight:
                continue

            neighbours.append(boid_i)

    return neighbours


def _calc_separation_vec(boid, neighbours):
    separation_vec = Vec2()
    if neighbours:
        for neighbour in neighbours:
            diff = sub_vec2(neighbour.pos, boid.pos)
            separation_vec = sub_vec2(separation_vec, diff)

    return separation_vec


def _calc_alignment_vec(boid, neighbours):
    average_direction = Vec2()
    if neighbours:
        for neighbour in neighbours:
            average_direction = add_vec2(average_direction, neighbour.velocity)

        average_direction = div_vec(average_direction, len(neighbours))
        average_direction = div_vec(average_direction, 8)
    # alignment_vec = average_direction
    # alignment_vec = normalized_vec(alignment_vec)
    return average_direction


def _calc_cohesion(boid, neighbours):
    average_pos = Vec2()
    if neighbours:
        for neighbour in neighbours:
            average_pos = add_vec2(average_pos, neighbour.pos)
        average_pos = div_vec(average_pos, len(neighbours))
        average_pos = sub_vec2(average_pos, boid.pos)
        average_pos = div_vec(average_pos, 100.0)
    return average_pos


def _limit_velocity(velocity):
    if len_vec(velocity) > 0.5:
        return mul_vec2(normalized_vec(velocity), 0.5)
    return Vec2(velocity.x, velocity.y)


def tick_boid(environment, boid):
    neighbours = get_neighbours(environment, boid)

    # separation
    separation_vec = _calc_separation_vec(boid, neighbours)
    separation_vec = mul_vec2(separation_vec, boid.separation)

    # alignment
    alignment_vec = _calc_alignment_vec(boid, neighbours)
    alignment_vec = mul_vec2(alignment_vec, boid.alignment)

    cohesion_vec = _calc_cohesion(boid, neighbours)
    cohesion_vec = mul_vec2(cohesion_vec, boid.cohesion)

    velocity = boid.velocity
    velocity = add_vec2(velocity, separation_vec)
    velocity = add_vec2(velocity, alignment_vec)
    velocity = add_vec2(velocity, cohesion_vec)
    velocity = _limit_velocity(velocity)
    boid.velocity = velocity

    boid.pos = add_vec2(boid.pos, velocity)
    # bound_v = _bound_position(environment, boid)
    # boid.velocity = bound_v


def _bound_position(env, boid):
    xmin, xmax, ymin, ymax = 0, env.width, 0, env.height
    vec = Vec2()
    if boid.pos.x < xmin:
        vec.x = 10
    elif boid.pos.x > xmax:
        vec.x = -10

    if boid.pos.y < ymin:
        vec.y = 10
    elif boid.pos.y > ymax:
        vec.y = -10

    return vec


def tick_move_boids(environment, boid):
    # move
    new_pos = add_vec2(boid.pos, boid.velocity)
    bound_v = _bound_position(environment, boid)
    boid.velocity = bound_v

    # new_pos.x = new_pos.x % environment.width
    # new_pos.y = new_pos.y % environment.height
    boid.pos = new_pos


def tick_environment(environment):
    for boid in environment.boids:
        tick_boid(environment, boid)


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
    if len_vec(boid.velocity) != 0:
        direction = normalized_vec(boid.velocity)
    else:
        direction = Vec2(1.0, 0.0)
    end_point = add_vec2(boid.pos, mul_vec2(direction, size * 1.5))
    # painter.drawEllipse(boid.pos.x - 10, boid.pos.y - 10, 20, 20)
    # painter.drawLine(boid.pos.x, boid.pos.y, end_point.x, end_point.y)

    side_1 = add_vec2(boid.pos, mul_vec2(perpendicular_vec_clockwise(direction), half_size))
    side_2 = add_vec2(boid.pos, mul_vec2(perpendicular_vec_counter_clockwise(direction), half_size))
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
        _draw_boid_debug_line(painter, boid, mul_vec2(direction, max_dist))
        # draw direction
        sight_one = mul_vec2(rotate(direction, boid.eyesight), max_dist)
        sight_two = mul_vec2(rotate(direction, -boid.eyesight), max_dist)
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
            _draw_boid_debug_line(painter, boid, mul_vec2(separation_vec, 1))

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
            _draw_boid_debug_line(painter, boid, mul_vec2(cohesion, 1))


class BoidsWidget(QWidget):
    def __init__(self):
        super(BoidsWidget, self).__init__()
        self.setWindowTitle('Boids')
        self.environment = self._make_environment()
        self.tick_timer = QTimer()
        self.tick_timer.setInterval(1)
        self.tick_timer.timeout.connect(self.tick)
        # self.tick_timer.start()
        self.setCursor(Qt.BlankCursor)

    def mousePressEvent(self, event):
        self.tick_timer.start()

    def tick(self):
        tick_environment(self.environment)
        self.update()

    def _make_environment(self):
        env = Environment()
        for i in range(80):
            boid = Boid()
            boid.pos.x = random.randint(50, env.width - 100)
            boid.pos.y = random.randint(50, env.height - 100)

            dir = Vec2((random.random() * 2.0) - 1.0, (random.random() * 2.0) - 1.0)
            boid.velocity = normalized_vec(dir)

            # boid.velocity = 0.5
            boid.debug = False

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
    sortby = SortKey.CUMULATIVE
    p = cProfile.Profile()
    # p.enable()
    app = QApplication()
    w = BoidsWidget()
    w.show()
    app.exec_()
    # p.disable()
    # p.print_stats(sort=sortby)


def test_vec():
    vec1 = normalized_vec(Vec2(x=1.0, y=-1.0))
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
