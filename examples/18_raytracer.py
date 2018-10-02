"""ray tracer
"""
import numpy
import time
from PySide2 import QtWidgets, QtGui, QtCore

DEBUG = True


class AABB(object):
    def __init__(self, min_, max_):
        self.min = min_
        self.max = max_


class Triangle(object):
    def __init__(self, vertex0, vertex1, vertex2, normal=None):
        self.vertex0 = vertex0
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        if not normal:
            normal = QtGui.QVector3D()
        self.normal = normal

    def __mul__(self, other):
        v0 = other * QtGui.QVector4D(self.vertex0, 1).toVector3DAffine()
        v1 = other * QtGui.QVector4D(self.vertex1, 1).toVector3DAffine()
        v2 = other * QtGui.QVector4D(self.vertex2, 1).toVector3DAffine()
        return Triangle(v0, v1, v2, self.normal)


class PointLight(object):
    def __init__(self):
        self.matrix = QtGui.QMatrix4x4()
        self.color = QtGui.QVector3D(1, 1, 1)

    def position(self):
        return QtGui.QVector3D(self.matrix.column(3))


class Ray(object):
    def __init__(self):
        self.pos = QtGui.QMatrix4x4()
        self.direction = QtGui.QVector3D()


class Camera(object):
    def __init__(self):
        self.matrix = QtGui.QMatrix4x4()

        projection = QtGui.QMatrix4x4()
        projection.perspective(45.0, 1.0, 1, 1000)
        self.projection = projection.inverted()[0]

    def position(self):
        return QtGui.QVector3D(self.matrix.column(3))


class Geometry(object):
    def __init__(self):
        self.matrix = QtGui.QMatrix4x4()
        self.verts = []
        self.tris = []
        self.__aabb = None
        self.__aabb_worldspace = None
        self.object_color = QtGui.QVector3D(1, 1, 1)

    @property
    def aabb(self):
        return self.__aabb

    @aabb.setter
    def aabb(self, value):
        self.__aabb = value
        self.calculate()

    def calculate(self):
        min_ = QtGui.QVector3D()
        max_ = QtGui.QVector3D()

        for v in self.verts:
            v = RayTracer.multiply_matrix(v, self.matrix)
            if v.x() < min_.x():
                min_.setX(v.x())
            if v.y() < min_.y():
                min_.setY(v.y())
            if v.z() < min_.z():
                min_.setZ(v.z())

            if v.x() > max_.x():
                max_.setX(v.x())
            if v.y() > max_.y():
                max_.setY(v.y())
            if v.z() > max_.z():
                max_.setZ(v.z())
        self.__aabb_worldspace = AABB(min_, max_)

    @property
    def aabb_worldspace(self):
        """return world space bounding box
        """
        return self.__aabb_worldspace

    def position(self):
        return QtGui.QVector3D(self.matrix.column(3))


class Locator(object):
    def __init__(self):
        self.matrix = QtGui.QMatrix4x4()

    def position(self):
        return QtGui.QVector3D(self.matrix.column(3))


class Cube(Geometry):
    def __init__(self):
        # https://www.siggraph.org/education/materials/HyperGraph/modeling/polymesh/polymesh.htm
        super(Cube, self).__init__()
        p1 = [-1, -1, 1]
        p2 = [1, -1, 1]
        p3 = [1, 1, 1]
        p4 = [-1, 1, 1]
        p5 = [-1, 1, -1]
        p6 = [1, 1, -1]
        p7 = [-1, -1, -1]
        p8 = [1, -1, -1]

        cube_struct = [
            p1, p2, p3,
            p3, p4, p1,
            p5, p4, p3,
            p3, p6, p5,
            p3, p2, p8,
            p8, p6, p3,
            p5, p7, p1,
            p1, p4, p5,
            p6, p8, p7,
            p7, p5, p6
        ]

        for i in range(0, len(cube_struct), 3):
            p0 = cube_struct[i]
            p1 = cube_struct[i + 1]
            p2 = cube_struct[i + 2]

            p0 = QtGui.QVector3D(*p0)
            p1 = QtGui.QVector3D(*p1)
            p2 = QtGui.QVector3D(*p2)

            self.verts += [p0, p1, p2]
            n = RayTracer.calculate_normal(p0, p1, p2)
            t = Triangle(p0, p1, p2, n)
            self.tris.append(t)

        self.aabb = AABB(QtGui.QVector3D(-1, -1, -1), QtGui.QVector3D(1, 1, 1))


class RayTracer(object):
    def __init__(self):
        self.render_camera = Camera()
        self.objects = []
        self.render_resolution = QtCore.QSize()
        self.only_sample_nearest = True
        self.output_data = []
        self._screen_to_world_cache = {}
        self.fps = 0.00

    @staticmethod
    def multiply_matrix(v, matrix):
        return (matrix * QtGui.QVector4D(v, 1)).toVector3DAffine()

    def get_lights(self):
        lights = []
        for obj in self.objects:
            if isinstance(obj, PointLight):
                lights.append(obj)
        return lights

    def world_to_screen(self, v):
        mv = (self.render_camera.projection * self.render_camera.matrix)
        v4 = mv * QtGui.QVector4D(v, 1)
        return v4.toVector3DAffine()

    def screen_to_world(self, v):
        v4 = QtGui.QVector4D(v, 1)
        vp = self.render_camera.projection * self.render_camera.matrix
        return (vp.inverted()[0] * v4).toVector3DAffine()

    @staticmethod
    def calculate_normal(v0, v1, v2):
        edge1 = v1 - v0
        edge2 = v2 - v0
        return QtGui.QVector3D.crossProduct(edge1, edge2).normalized()

    def intersect_aabb(self, bbaa, ray):
        """check if a point intersects a bbaa
        """
        origin = [ray.pos.x(), ray.pos.y(), ray.pos.z()]
        dir_ = [ray.direction.x(), ray.direction.y(), ray.direction.z()]
        RIGHT = 0
        LEFT = 1
        MIDDLE = 2

        numdim = 3
        inside = True
        quadrant = [-1] * 3

        maxT = [0.0] * 3
        candidatePlane = [0.0] * 3
        minB = [bbaa.min.x(), bbaa.min.y(), bbaa.min.z()]
        maxB = [bbaa.max.x(), bbaa.max.y(), bbaa.max.z()]

        for i in range(numdim):
            if origin[i] < minB[i]:
                quadrant[i] = 1
                candidatePlane[i] = LEFT
                inside = False
            elif origin[i] > maxB[i]:
                quadrant[i] = RIGHT
                candidatePlane[i] = maxB[i]
                inside = False
            else:
                quadrant[i] = MIDDLE

        if inside:
            return QtGui.QVector3D(*origin)

        for i in range(numdim):
            if quadrant[i] != MIDDLE and dir_[i] != 0.0:
                maxT[i] = (candidatePlane[i] - origin[i]) / dir_[i]
            else:
                maxT[i] = -1.0

        which_plane = 0
        for i in range(numdim):
            if maxT[which_plane] < maxT[i]:
                which_plane = i

        if maxT[which_plane] < 0.0:
            return None

        coord = [0.0] * 3
        for i in range(numdim):
            if which_plane != i:
                coord[i] = origin[i] + maxT[which_plane] * dir_[i]
                if coord[i] < minB[i] or coord[i] > maxB[i]:
                    return None
            else:
                coord[i] = candidatePlane[i]
        return QtGui.QVector3D(*coord)

    def intersect_triangle(self, ray, triangle):
        # https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
        vertex0 = triangle.vertex0
        vertex1 = triangle.vertex1
        vertex2 = triangle.vertex2

        epsilon = 0.0000001
        edge1 = vertex1 - vertex0
        edge2 = vertex2 - vertex0
        h = QtGui.QVector3D.crossProduct(ray.direction, edge2)
        a = QtGui.QVector3D.dotProduct(edge1, h)

        if a > -epsilon and a < epsilon:
            return None
        f = 1 / a
        s = ray.pos - vertex0
        u = f * (QtGui.QVector3D.dotProduct(s, h))
        if u < 0.0 or u > 1.0:
            return None

        q = QtGui.QVector3D.crossProduct(s, edge1)
        v = f * QtGui.QVector3D.dotProduct(ray.direction, q)
        if v < 0.0 or u + v > 1.0:
            return None

        t = f * QtGui.QVector3D.dotProduct(edge2, q)
        if t > epsilon:
            intersection_point = ray.pos + ray.direction * t
            return intersection_point
        else:
            return None

    def render_tri(self, geometry, tri, pos):
        object_color = geometry.object_color

        ambient_diffuse = QtGui.QVector3D()

        lights = self.get_lights()
        for light in lights:
            ambient_strength = 0.2
            ambient = light.color * ambient_strength

            lightdir = (light.position() - pos).normalized()

            diff = max([QtGui.QVector3D.dotProduct(tri.normal, lightdir), 0.0])
            diffuse = diff * light.color
            ambient_diffuse += ambient + diffuse

        ambient_diffuse /= len(lights)
        color = ambient_diffuse * object_color

        color = QtGui.QColor(color.x() * 255,
                             color.y() * 255,
                             color.z() * 255)

        return color

    def screen_to_world_cache(self, x, y, z):
        key = "{}-{}-{}".format(x, y, z)
        if key in self._screen_to_world_cache:
            return self._screen_to_world_cache[key]

        pos = self.screen_to_world(QtGui.QVector3D(x, y, z))
        self._screen_to_world_cache[key] = pos
        return pos

    def render_pixel(self, screen_x, screen_y):
        far = self.screen_to_world_cache(screen_x, screen_y, -1)
        near = self.screen_to_world_cache(screen_x, screen_y, 1)

        direction = (far - near).normalized()
        ray = Ray()
        ray.direction = direction
        ray.pos = near
        hitting_tris = {}

        for obj in self.objects:
            if isinstance(obj, Geometry):
                if not self.intersect_aabb(obj.aabb_worldspace, ray):
                    continue
                for tri in obj.tris:
                    tri = tri * obj.matrix
                    pos = self.intersect_triangle(ray, tri)
                    if pos:
                        distance = (pos - ray.pos).length()
                        hitting_tris[distance] = (obj, tri, pos)

        keys = hitting_tris.keys()

        if keys:
            keys.sort()
            if self.only_sample_nearest:
                k = keys[0]
                geometry, tri, pos = hitting_tris[k]
                c = self.render_tri(geometry, tri, pos)
                return c
            else:
                c = None
                for k in reversed(keys):
                    geometry, tri, pos = hitting_tris[k]
                    c = self.render_tri(geometry, tri, pos)
                return c

        return QtGui.QColor(200, 200, 200)

    def render(self):
        start = time.time()
        width = self.render_resolution.width()
        height = self.render_resolution.height()
        step_width = 1.0 / float(width)
        step_height = 1.0 / float(height)
        half_step_width = step_width / 2.0
        half_step_height = step_height / 2.0
        output_image = []
        for y in range(height):
            row = []
            output_image.append(row)
            for x in range(width):
                screen_y = ((((
                                  step_height * y) + half_step_height) * 2.0) - 1.0) * -1
                screen_x = (((step_width * x) + half_step_width) * 2.0) - 1.0
                color = self.render_pixel(screen_x, screen_y)

                row.append(color)

        self.output_data = output_image
        self.fps = 1.0 / float(time.time() - start)


class RayTracerWidget(QtWidgets.QWidget):
    """view for the raytracer
    """

    def __init__(self):
        super(RayTracerWidget, self).__init__()
        self.setWindowTitle('Raytracer')
        self.render = False

        self.ray_tracer = RayTracer()
        self.ray_tracer.render_resolution = QtCore.QSize(32, 32)
        self.ray_tracer.render_camera = Camera()
        self.ray_tracer.render_camera.matrix.lookAt(
            QtGui.QVector3D(1, 1, 0.8), QtGui.QVector3D(),
            QtGui.QVector3D(0, 1, 0))
        self.light = PointLight()
        self.light.matrix.translate(2, 2, 0)
        self.light.color = QtGui.QVector3D(1.0, 0.64, 0.18)
        self.ray_tracer.objects.append(self.light)

        self.light = PointLight()
        self.light.matrix.translate(2, -2, 2)
        self.light.color = QtGui.QVector3D(0.368, 156.0 / 255.0, 242.0 / 255.0)
        self.ray_tracer.objects.append(self.light)

        self.cube = Cube()
        self.cube.matrix.translate(0, 0, 0)
        self.ray_tracer.objects.append(self.cube)

        # self.ray_tracer.objects.append(Locator())

        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(1000.0 / 25.0))
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.render_timer = QtCore.QTimer()
        self.render_timer.setInterval(int(100.0 / 1.0))
        self.render_timer.timeout.connect(self.render_tick)
        self.render_timer.start()

        self.show_viewport = True

    def render_tick(self):
        if self.render:
            self.ray_tracer.render()

    def tick(self):
        self.cube.matrix.rotate(1, QtGui.QVector3D(0, 1, 0))
        self.cube.calculate()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_H:
            self.show_viewport = not self.show_viewport
            self.update()

        if event.key() == QtCore.Qt.Key_R:
            self.render = not self.render

        if event.key() == QtCore.Qt.Key_Up:
            self.ray_tracer.render_resolution *= 2
            self.ray_tracer.output_data = []

        if event.key() == QtCore.Qt.Key_Down:
            self.ray_tracer.render_resolution /= 2
            self.ray_tracer.output_data = []

    def device_to_world(self, pos, z):
        screen_v = self.device_to_screen(pos)
        screen_v.setZ(z)
        return self.ray_tracer.screen_to_world(screen_v)

    def device_to_screen(self, v):
        x = ((float(v.x()) / float(self.width())) * 2.0) - 1
        y = (((float(v.y()) / float(self.height())) * 2.0) - 1) * -1
        return QtGui.QVector3D(x, y, 0)

    def screen_to_device(self, v):
        x = ((v.x() + 1.0) / 2.0) * self.width()
        y = ((-v.y() + 1.0) / 2.0) * self.height()
        return QtCore.QPoint(x, y)

    def world_to_device(self, v):
        v_screen = self.ray_tracer.world_to_screen(v)
        v_device = self.screen_to_device(v_screen)
        return v_device

    def paint_line(self, painter, v_a, v_b):
        v_a = self.world_to_device(v_a)
        v_b = self.world_to_device(v_b)
        painter.drawLine(v_a.x(), v_a.y(), v_b.x(), v_b.y())

    def paint_pivot(self, painter, matrix):
        v = QtGui.QVector3D(matrix.column(3))
        x_v = self.multiply_matrix(QtGui.QVector3D(1, 0, 0), matrix)
        y_v = self.multiply_matrix(QtGui.QVector3D(0, 1, 0), matrix)
        z_v = self.multiply_matrix(QtGui.QVector3D(0, 0, 1), matrix)
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0)))

        self.paint_line(painter, v, x_v)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0)))
        self.paint_line(painter, v, y_v)
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 255)))
        self.paint_line(painter, v, z_v)

    def paint_vertex(self, painter, v):
        v_device = self.world_to_device(v)
        painter.fillRect(v_device.x() - 2, v_device.y() - 2, 4, 4,
                         QtGui.QColor(150, 150, 150))

    @staticmethod
    def multiply_matrix(v, matrix):
        return (matrix * QtGui.QVector4D(v, 1)).toVector3DAffine()

    def paint_triangle(self, painter, triangle, geometry):
        painter.setPen(QtGui.QPen(QtGui.QColor(20, 20, 20)))
        v0_device = self.world_to_device(triangle.vertex0)
        v1_device = self.world_to_device(triangle.vertex1)
        v2_device = self.world_to_device(triangle.vertex2)
        painter.drawLine(v0_device.x(), v0_device.y(), v1_device.x(),
                         v1_device.y())
        painter.drawLine(v1_device.x(), v1_device.y(), v2_device.x(),
                         v2_device.y())
        painter.drawLine(v2_device.x(), v2_device.y(), v0_device.x(),
                         v0_device.y())

        edge1 = triangle.vertex1 - triangle.vertex0
        edge2 = triangle.vertex2 - triangle.vertex0
        edge3 = triangle.vertex2 - triangle.vertex1
        normal_start = (
                           triangle.vertex0 + triangle.vertex1 + triangle.vertex2) / 3.0
        normal_end = normal_start + (
            self.multiply_matrix(triangle.normal / 5.0, geometry.matrix))
        # normal_end = normal_start
        # normal_start = triangle.vertex0 + (edge1 + edge2) / 2.0

        self.paint_vertex(painter, normal_start)
        self.paint_line(painter, normal_start, normal_end)

    def paint_geometry(self, painter, geometry):
        for t in geometry.tris:
            self.paint_triangle(painter, t * geometry.matrix, geometry)

        for v in geometry.verts:
            self.paint_vertex(painter,
                              self.multiply_matrix(v, geometry.matrix))

        self.paint_aabb(painter, geometry.aabb_worldspace)
        self.paint_pivot(painter, geometry.matrix)

    def paint_aabb(self, painter, aabb):
        p2_device = self.world_to_device(aabb.min)
        p1_device = self.world_to_device(aabb.max)

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 0, 255)))
        painter.drawLine(p1_device, p2_device)

    def paint_locator(self, painter, locator):
        self.paint_pivot(painter, locator.matrix)

    def paint_output_data(self, painter):
        width = self.ray_tracer.render_resolution.width()
        height = self.ray_tracer.render_resolution.height()
        pixel_width = 1.0 / float(width) * float(self.width())
        pixel_height = 1.0 / float(height) * float(self.height())
        for y in range(height):
            for x in range(width):
                try:
                    color = self.ray_tracer.output_data[y][x]
                except IndexError:
                    continue

                paint_x = x * pixel_width
                paint_y = y * pixel_height

                painter.fillRect(paint_x, paint_y, pixel_width + 1,
                                 pixel_height + 1,
                                 color)
                # painter.drawRect(paint_x, paint_y, pixel_width, pixel_height)

    def paint_light(self, painter, obj):
        position = QtGui.QVector3D(obj.matrix.column(3))
        pos_device = self.world_to_device(position)
        painter.drawEllipse(pos_device.x(), pos_device.y(), 20, 20)

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(),
                         QtGui.QColor(70, 70, 70))

        self.paint_output_data(painter)
        rays = self.ray_tracer.render_resolution.width() * self.ray_tracer.render_resolution.height()
        info = "Raytracer | {:.2f} fps | {} rays".format(self.ray_tracer.fps,
                                                         rays)
        painter.drawText(20, 20, info)
        if self.show_viewport:
            for obj in self.ray_tracer.objects:
                if isinstance(obj, Geometry):
                    self.paint_geometry(painter, obj)
                elif isinstance(obj, Locator):
                    self.paint_locator(painter, obj)
                elif isinstance(obj, PointLight):
                    self.paint_light(painter, obj)

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(300, 300)


def main():
    app = QtWidgets.QApplication([])
    w = RayTracerWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
