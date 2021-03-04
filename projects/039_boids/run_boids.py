"""

"""
import math
import random

from PySide2.QtCore import QTimer, QSize, QRect
from PySide2.QtGui import QPainter, QPen, QColor
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QFormLayout, QPushButton, QSpinBox, QDoubleSpinBox, \
    QCheckBox

TOTAL_BOIDS = 150
DEFAULT_MAX_SPEED = 9.0
DEFAULT_MAX_DISTANCE = 60.0
DEFAULT_EYE_SIGHT_ANGLE = 120.0
SEPARATION_DISTANCE = 20.0
PUSH_BACK_SPEED = 0.5
COHESION_STRENGTH = 0.01
SEPRATION_STRENGTH = 0.1
SEPARATION_VALUE = 1.0
COHESION_VALUE = 1.0
ALIGNMENT_VALUE = 1.0
BOID_SIZE = 5.0
DEBUG = False


class Rect:
    def __init__(self, x=0.0, y=0.0, width=0.0, height=0.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Vec2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return 'Vec2(x={!r}, y={!r})'.format(self.x, self.y)


class BoidsEnvironment:
    def __init__(self):
        self.is_running = True
        self.rect = Rect()
        self.max_speed = DEFAULT_MAX_SPEED
        self.boids = []
        self.neighbour_max_distance = DEFAULT_MAX_DISTANCE
        self.neighbour_max_distance2 = DEFAULT_MAX_DISTANCE * DEFAULT_MAX_DISTANCE


class Boid:
    def __init__(self):
        self.pos = Vec2()
        self.velocity = Vec2(0.0, 0.0)
        # self.steering = random.random() * 0.1

        self.debug = False
        self.eyesight = math.radians(DEFAULT_EYE_SIGHT_ANGLE)

        self.steering = 0.05
        self.separation_distance = SEPARATION_DISTANCE
        self.separation_distance2 = SEPARATION_DISTANCE * SEPARATION_DISTANCE

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


def len2_vec(vec):
    return vec.x * vec.x + vec.y * vec.y


def div_vec(vec, value):
    return Vec2(x=vec.x / value, y=vec.y / value)


def normalized_vec(vec):
    length = len_vec(vec)
    return Vec2(vec.x / length, vec.y / length)


def dot_vec(vec1, vec2):
    return vec1.x * vec2.x + vec1.y * vec2.y


def get_neighbours(environment, boid, angle=True):
    neighbours = []
    angle_neighbours = []
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
            neighbours.append(boid_i)

            if angle:
                # radians = math.acos(dot)
                # radians = math.atan2(dist_normalised.y, dist_normalised.x)
                if dot > 1.0:
                    dot = 1.0
                if dot < -1.0:
                    dot = 1.0

                current_angle = math.acos(dot)

                if abs(current_angle) > boid.eyesight:
                    continue

                angle_neighbours.append(boid_i)

    return neighbours, angle_neighbours


def _calc_separation_vec(boid, neighbours):
    separation_vec = Vec2()
    if neighbours:
        for neighbour in neighbours:
            diff = sub_vec2(neighbour.pos, boid.pos)
            if len2_vec(diff) < boid.separation_distance2:
                separation_vec = sub_vec2(separation_vec, diff)
        separation_vec = mul_vec2(separation_vec, SEPRATION_STRENGTH)
    return separation_vec


def _calc_alignment_vec(boid, neighbours):
    average_direction = Vec2()
    if neighbours:
        for neighbour in neighbours:
            average_direction = add_vec2(average_direction, neighbour.velocity)

        average_direction = div_vec(average_direction, len(neighbours))
        average_direction = div_vec(sub_vec2(average_direction, boid.velocity), 8.0)
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
        average_pos = mul_vec2(average_pos, COHESION_STRENGTH)
    return average_pos


def _limit_velocity(env, velocity):
    if len_vec(velocity) > env.max_speed:
        return mul_vec2(normalized_vec(velocity), env.max_speed)
    return Vec2(velocity.x, velocity.y)


def tick_boid(environment, boid):
    all_neighbours, neighbours = get_neighbours(environment, boid)

    # separation
    separation_vec = _calc_separation_vec(boid, all_neighbours)
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
    velocity = add_vec2(velocity, _bound_position(environment, boid))
    velocity = _limit_velocity(environment, velocity)

    boid.velocity = velocity

    boid.pos = add_vec2(boid.pos, velocity)

    # bound_v = _bound_position(environment, boid)
    # boid.velocity = bound_v


def _bound_position(env, boid):
    rect = env.rect
    xmin, xmax, ymin, ymax = rect.x, rect.x + rect.width, rect.y, rect.y + rect.height
    vec = Vec2()
    if boid.pos.x < xmin:
        vec.x = PUSH_BACK_SPEED
    elif boid.pos.x > xmax:
        vec.x = -PUSH_BACK_SPEED

    if boid.pos.y < ymin:
        vec.y = PUSH_BACK_SPEED
    elif boid.pos.y > ymax:
        vec.y = -PUSH_BACK_SPEED

    return vec


def tick_move_boids(environment, boid):
    pass
    # move
    # new_pos = add_vec2(boid.pos, boid.velocity)
    # bound_v = _bound_position(environment, boid)
    # boid.velocity = bound_v

    # new_pos.x = new_pos.x % environment.width
    # new_pos.y = new_pos.y % environment.height
    # boid.pos = new_pos


def tick_environment(environment):
    if environment.is_running:
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


def _draw_boid_debug_circle(painter, boid, value):
    painter.drawEllipse(boid.pos.x - value, boid.pos.y - value, value * 2.0,
                        value * 2.0)


def draw_boid(painter, environment, boid):
    size = BOID_SIZE
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
    # painter.drawLine(side_1.x, side_1.y, side_2.x, side_2.y)

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
        _draw_boid_debug_circle(painter, boid, max_dist)
        _draw_boid_debug_circle(painter, boid, boid.separation_distance)

        # draw detected neighbourds
        neighbours, angle_neighbours = get_neighbours(environment, boid)
        for neighbour in angle_neighbours:
            _draw_boid_debug_circle(painter, neighbour, 2)

        if angle_neighbours:
            separation_vec = _calc_separation_vec(boid, angle_neighbours)

            color = QColor()
            color.setRgb(200, 0, 200)
            pen.setColor(color)
            painter.setPen(pen)
            _draw_boid_debug_line(painter, boid, mul_vec2(separation_vec, 1))

            alignment_vec = _calc_alignment_vec(boid, angle_neighbours)
            color = QColor()
            color.setRgb(0, 200, 200)
            pen.setColor(color)
            painter.setPen(pen)
            _draw_boid_debug_line(painter, boid, mul_vec2(alignment_vec, 50))

            cohesion = _calc_cohesion(boid, angle_neighbours)
            color = QColor()
            color.setRgb(0, 120, 0)
            pen.setColor(color)
            painter.setPen(pen)
            _draw_boid_debug_line(painter, boid, mul_vec2(cohesion, 1))


def _make_boid(rect, speed):
    xmin, xmax, ymin, ymax = rect.x, rect.x + rect.width, rect.y, rect.y + rect.height
    boid = Boid()
    boid.pos.x = float(random.randint(xmin, xmax))
    boid.pos.y = float(random.randint(ymin, ymax))

    dir = Vec2((random.random() * 2.0) - 1.0, (random.random() * 2.0) - 1.0)
    boid.velocity = mul_vec2(normalized_vec(dir), speed)

    # boid.velocity = 0.5
    boid.debug = False
    return boid


def _make_environment(total, rect, max_speed, separation):
    env = BoidsEnvironment()
    env.rect = rect
    for i in range(total):
        boid = _make_boid(env.rect, max_speed)
        boid.debug = False
        boid.separation = separation

        env.boids.append(boid)
    if len(env.boids) > 1:
        env.boids[0].debug = DEBUG
        env.boids[0].pos = Vec2(env.rect.x + env.rect.width / 2.0, env.rect.y + env.rect.height / 2.0)
    return env


class BoidsWidget(QWidget):
    def __init__(self):
        super(BoidsWidget, self).__init__()
        self.setWindowTitle('Boids')
        self.environment = None

    def set_boids_environment(self, environment):
        self.environment = environment
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # painter.translate(QPointF(-25, -25))

        if self.environment:
            rect = QRect(self.environment.rect.x, self.environment.rect.y, self.environment.rect.width,
                         self.environment.rect.height)
            painter.drawRect(rect)

            for boid in self.environment.boids:
                draw_boid(painter, self.environment, boid)

    def sizeHint(self):
        return QSize(450, 450)

    def showEvent(self, event):
        self.update()


def _make_spinbox(default, min_value, max_value):
    spinbox = QSpinBox()
    spinbox.setMaximum(max_value)
    spinbox.setMinimum(min_value)
    spinbox.setValue(default)
    return spinbox


def _make_double_spinbox(default, min_value, max_value, single_step):
    spinbox = QDoubleSpinBox()

    spinbox.setSingleStep(single_step)
    spinbox.setMaximum(max_value)
    spinbox.setMinimum(min_value)
    spinbox.setValue(default)
    return spinbox


def _change_total(environment, new_total):
    total = len(environment.boids)
    if total == new_total:
        return environment
    elif total > new_total:
        environment.boids = environment.boids[:new_total]
    else:
        diff = new_total - total
        for i in range(diff):
            environment.boids.append(
                _make_boid(environment.rect, environment.max_speed))


class BoidsApp(QWidget):
    def __init__(self):
        super(BoidsApp, self).__init__()
        self.setWindowTitle('Boids')

        self._boids_environment = BoidsEnvironment()

        layout = QHBoxLayout()
        self._boids_widget = BoidsWidget()
        self._boids_widget.set_boids_environment(self._boids_environment)
        self._boids_widget.setMinimumWidth(550)
        self._form_layout = QFormLayout()

        self._is_running_checkbox = QCheckBox()
        self._is_running_checkbox.setChecked(True)
        self._is_running_checkbox.stateChanged.connect(self.__is_running_changed)

        self._tick_button = QPushButton()
        self._tick_button.setText('Tick')
        self._tick_button.clicked.connect(self.__do_tick)

        self._total_spinbox = _make_spinbox(TOTAL_BOIDS, 0, 9999)
        self._total_spinbox.valueChanged.connect(self.__total_changed)

        self._max_speed_spinbox = _make_double_spinbox(DEFAULT_MAX_SPEED, 0.0, 9999.0, 0.1)
        self._max_speed_spinbox.valueChanged.connect(self.__max_speed_changed)

        self._eyesight_radius_spinbox = _make_double_spinbox(DEFAULT_MAX_DISTANCE, 0.0, 9999.0, 0.5)
        self._eyesight_radius_spinbox.valueChanged.connect(self.__eyesight_radius_changed)

        self._eyesight_angle_spinbox = _make_double_spinbox(DEFAULT_EYE_SIGHT_ANGLE, 0.0, 360.0, 1.0)
        self._eyesight_angle_spinbox.valueChanged.connect(self.__eyesight_angle_changed)

        self._separation_distance_spinbox = _make_double_spinbox(SEPARATION_DISTANCE, 0.0, 9999.0, 1.0)
        self._separation_distance_spinbox.valueChanged.connect(self.__separation_distance_changed)

        self._separation_value_spinbox = _make_double_spinbox(SEPARATION_VALUE, 0.0, 1.0, 0.1)
        self._separation_value_spinbox.valueChanged.connect(self.__separation_value_changed)

        self._cohesion_value_spinbox = _make_double_spinbox(COHESION_VALUE, 0.0, 1.0, 0.1)
        self._cohesion_value_spinbox.valueChanged.connect(self.__cohesion_value_changed)

        self._alignment_value_spinbox = _make_double_spinbox(ALIGNMENT_VALUE, 0.0, 1.0, 0.1)
        self._alignment_value_spinbox.valueChanged.connect(self.__alignment_value_changed)

        self._generate_button = QPushButton()
        self._generate_button.setText('Generate')

        self._generate_button.clicked.connect(self._generate_environment)

        self._form_layout.addRow('Total Boids', self._total_spinbox)
        self._form_layout.addRow('Separation', self._separation_value_spinbox)
        self._form_layout.addRow('Cohesion', self._cohesion_value_spinbox)
        self._form_layout.addRow('Alignment', self._alignment_value_spinbox)

        self._form_layout.addRow('Max Speed', self._max_speed_spinbox)
        self._form_layout.addRow('Eyesight Radius', self._eyesight_radius_spinbox)
        self._form_layout.addRow('Eyesight Angle (degrees)', self._eyesight_angle_spinbox)
        self._form_layout.addRow('Separation Distance', self._separation_distance_spinbox)

        self._form_layout.addRow('Running', self._is_running_checkbox)
        self._form_layout.addWidget(self._generate_button)
        self._form_layout.addWidget(self._tick_button)

        layout.addWidget(self._boids_widget)
        layout.addLayout(self._form_layout)
        self.setLayout(layout)

        self.tick_timer = QTimer()
        self.tick_timer.setInterval(int(1000 / 24))
        self.tick_timer.timeout.connect(self._tick)
        self.tick_timer.start()

    def showEvent(self, event):
        self._generate_environment()

    def _tick(self):
        tick_environment(self._boids_environment)
        self._boids_widget.update()

    def __do_tick(self):
        is_running = self._boids_environment.is_running
        self._boids_environment.is_running = True
        tick_environment(self._boids_environment)
        self._boids_widget.update()
        self._boids_environment.is_running = is_running

    def __total_changed(self):
        total = self._total_spinbox.value()
        _change_total(self._boids_environment, total)

    def __cohesion_value_changed(self):
        value = self._cohesion_value_spinbox.value()
        for boid in self._boids_environment.boids:
            boid.cohesion = value

    def __alignment_value_changed(self):
        value = self._alignment_value_spinbox.value()
        for boid in self._boids_environment.boids:
            boid.alignment = value

    def __max_speed_changed(self):
        self._boids_environment.max_speed = self._max_speed_spinbox.value()

    def __eyesight_radius_changed(self):
        value = self._eyesight_radius_spinbox.value()
        self._boids_environment.neighbour_max_distance = value
        self._boids_environment.neighbour_max_distance2 = value * value

    def __is_running_changed(self):
        self._boids_environment.is_running = self._is_running_checkbox.isChecked()

    def __separation_distance_changed(self):
        value = self._separation_distance_spinbox.value()
        for boid in self._boids_environment.boids:
            boid.separation_distance = value
            boid.separation_distance2 = value * value

    def __separation_value_changed(self):
        value = self._separation_value_spinbox.value()
        for boid in self._boids_environment.boids:
            boid.separation = value

    def __eyesight_angle_changed(self):
        for boid in self._boids_environment.boids:
            boid.eyesight = math.radians(self._eyesight_angle_spinbox.value())

    def _generate_environment(self):
        max_speed = self._max_speed_spinbox.value()
        separation = self._separation_value_spinbox.value()
        environment = _make_environment(self._total_spinbox.value(), Rect(0.0, 0.0, 500.0, 500.0),
                                        max_speed, separation)
        environment.is_running = self._is_running_checkbox.isChecked()
        environment.max_speed = max_speed
        self._boids_environment = environment
        self._boids_widget.set_boids_environment(self._boids_environment)

    def sizeHint(self):
        return QSize(800, 550)


def main():
    app = QApplication()
    w = BoidsApp()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
