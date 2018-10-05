"""ray tracer
"""
import cProfile, pstats, StringIO

import numpy as np
import time

import sys
from PySide2 import QtWidgets, QtGui, QtCore

DEBUG = True

PROFILE = False
DIMENSIONS = [0, 1, 2]

RIGHT = 0
LEFT = 1
MIDDLE = 2
EPSILON = 0.0000001


def profile_it(func):
    def wrapped(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()  # start profiling
        res = func(*args, **kwargs)
        pr.disable()  # end profiling
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        return res
    return wrapped


class BoundingBox(object):
    def __init__(self, min_, max_):
        self.min = min_
        self.max = max_


class DataPoint(object):
    def __init__(self, pos=None, geometry=None, tri=None, world_tri=None):
        self.pos = pos
        self.geometry = geometry
        self.tri = tri
        self.world_tri = world_tri


class Triangle(object):
    def __init__(self, geometry, vertex0, vertex1, vertex2, normal=None):
        self.vertex0 = vertex0
        self.vertex1 = vertex1
        self.vertex2 = vertex2
        self.geometry = geometry
        self.world_v0 = None
        self.world_v1 = None
        self.world_v2 = None
        if not normal:
            normal = QtGui.QVector3D()
        self.normal = normal

    def calculate_world(self):
        self.world_v0 = self.geometry.matrix * QtGui.QVector4D(self.vertex0,
                                                               1).toVector3DAffine()
        self.world_v1 = self.geometry.matrix * QtGui.QVector4D(self.vertex1,
                                                               1).toVector3DAffine()
        self.world_v2 = self.geometry.matrix * QtGui.QVector4D(self.vertex2,
                                                               1).toVector3DAffine()

    def __mul__(self, other):
        v0 = other * QtGui.QVector4D(self.vertex0, 1).toVector3DAffine()
        v1 = other * QtGui.QVector4D(self.vertex1, 1).toVector3DAffine()
        v2 = other * QtGui.QVector4D(self.vertex2, 1).toVector3DAffine()
        return Triangle(self.geometry, v0, v1, v2, self.normal)


class PointLight(object):
    def __init__(self):
        self.__matrix = QtGui.QMatrix4x4()
        self.color = np.array([1, 1, 1])
        self.name = "pointLight"
        self.position = None

    @property
    def matrix(self):
        return self.__matrix

    @matrix.setter
    def matrix(self, value):
        self.__matrix = value
        self.position = QtGui.QVector3D(value.column(3))

    def get_position(self):
        return self.position

    def translate(self, x, y, z):
        self.__matrix.translate(x, y, z)
        self.position = QtGui.QVector3D(self.__matrix.column(3))


class Ray(object):
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction


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
        self.name = ""
        self.matrix = QtGui.QMatrix4x4()
        self.verts = []
        self.tris = []
        self.__boundingbox = None
        self.__boundingbox_worldspace = None
        self.object_color = QtGui.QVector3D(1, 1, 1)

    @property
    def boundingbox(self):
        return self.__boundingbox

    @boundingbox.setter
    def boundingbox(self, value):
        self.__boundingbox = value
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
        self.__boundingbox_worldspace = BoundingBox(min_, max_)

        for tri in self.tris:
            tri.calculate_world()


    @property
    def boundingbox_worldspace(self):
        """return world space bounding box
        """
        return self.__boundingbox_worldspace

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
            t = Triangle(self, p0, p1, p2, n)
            t.calculate_world()
            self.tris.append(t)

        self.boundingbox = BoundingBox(QtGui.QVector3D(-1, -1, -1),
                                       QtGui.QVector3D(1, 1, 1))


class RayTracer(object):
    def __init__(self):
        self.is_rendering = False
        self.render_camera = Camera()
        self.objects = []
        self.__geometries = []
        self.__lights = []

        self.__render_resolution = QtCore.QSize()
        self.only_sample_nearest = True
        self.__output_data = []
        self._screen_to_world_cache = {}
        self.fps = 0.00
        self.vp = QtGui.QMatrix4x4()
        self.vp_inverted = QtGui.QMatrix4x4()
        self.rays = []
        self.enabled_shadows = True
        self.enabled_reflections = True
        self.__total_lights = 0

    def remove_matrix_translation(self, matrix):
        matrix = QtGui.QMatrix4x4(matrix)
        v = QtGui.QVector3D(matrix.column(3))
        matrix.translate(v)
        return matrix

    @property
    def render_resolution(self):
        return self.__render_resolution

    @render_resolution.setter
    def render_resolution(self, value):
        self.__render_resolution = value

    @staticmethod
    def multiply_matrix(v, matrix):
        return (matrix * QtGui.QVector4D(v, 1)).toVector3DAffine()

    def get_lights(self):
        return self.__lights

    def setup_output_data(self):
        self.__output_data = np.zeros((self.render_resolution.width(),
                                       self.render_resolution.height(), 3))

    def calculate_matrices(self):
        self.vp = (self.render_camera.projection * self.render_camera.matrix)
        self.vp_inverted = self.vp.inverted()[0]

    def world_to_screen(self, v):
        v4 = self.vp * QtGui.QVector4D(v, 1)
        return v4.toVector3DAffine()

    def screen_to_world(self, v):
        v4 = QtGui.QVector4D(v, 1)
        return (self.vp_inverted * v4).toVector3DAffine()

    @staticmethod
    def calculate_normal(v0, v1, v2):
        edge1 = v1 - v0
        edge2 = v2 - v0
        return QtGui.QVector3D.crossProduct(edge1, edge2).normalized()

    def intersect_boundingbox(self, bbaa, ray):
        """check if a point intersects a bbaa
        """
        origin = [ray.pos.x(), ray.pos.y(), ray.pos.z()]

        inside = True
        quadrant = [-1, -1, -1]

        candidatePlane = [0.0, 0.0, 0.0]
        minB = [bbaa.min.x(), bbaa.min.y(), bbaa.min.z()]
        maxB = [bbaa.max.x(), bbaa.max.y(), bbaa.max.z()]

        for i in DIMENSIONS:
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

        if inside is True:
            return QtGui.QVector3D(*origin)

        maxT = [0.0, 0.0, 0.0]
        dir_ = [ray.direction.x(), ray.direction.y(), ray.direction.z()]

        for i in DIMENSIONS:
            if quadrant[i] != MIDDLE and dir_[i] != 0.0:
                maxT[i] = (candidatePlane[i] - origin[i]) / dir_[i]
            else:
                maxT[i] = -1.0

        which_plane = 0
        for i in DIMENSIONS:
            if maxT[which_plane] < maxT[i]:
                which_plane = i

        if maxT[which_plane] < 0.0:
            return None

        coord = [0.0, 0.0, 0.0]
        for i in DIMENSIONS:
            if which_plane != i:
                coord[i] = origin[i] + maxT[which_plane] * dir_[i]
                if coord[i] < minB[i] or coord[i] > maxB[i]:
                    return None
            else:
                coord[i] = candidatePlane[i]
        return QtGui.QVector3D(*coord)

    def intersect_triangle(self, ray, triangle):
        # https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
        vertex0 = triangle.world_v0
        vertex1 = triangle.world_v1
        vertex2 = triangle.world_v2

        edge1 = vertex1 - vertex0
        edge2 = vertex2 - vertex0
        h = QtGui.QVector3D.crossProduct(ray.direction, edge2)
        a = QtGui.QVector3D.dotProduct(edge1, h)

        if -EPSILON < a < EPSILON:
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
        if t > EPSILON:
            intersection_point = ray.pos + ray.direction * t
            return intersection_point
        else:
            return None

    def nparray_to_vector3D(self, array):
        return QtGui.QVector3D(array[0], array[1], array[2])

    def reflect_vector(self, vector, normal):
        dot = QtGui.QVector3D.dotProduct(vector, normal)
        return vector - (normal * 2 * dot)

        r = -vector - (-dot) * normal
        return vector + 2 * r
        return -2 * (
            QtGui.QVector3D.dotProduct(vector, normal) * normal) + vector
        return ((2 * QtGui.QVector3D.dotProduct(vector,
                                                normal)) * normal) - vector
        return vector - (
            2 * QtGui.QVector3D.dotProduct(vector, normal) * normal)

    def render_tri(self, geometry, tri, pos, color, ray, reflections=True):
        object_color = geometry.object_color

        ambient_diffuse = QtGui.QVector3D()

        for light in self.__lights:
            ambient_strength = 0.2
            ambient = light.color * ambient_strength

            lightdir = (light.position - pos).normalized()

            # diff = max(QtGui.QVector3D.dotProduct(tri.normal, lightdir), 0.0)
            dot = QtGui.QVector3D.dotProduct(tri.normal, lightdir)
            diff = dot if dot > 0 else 0.0

            # shadows

            light_ray = (light.position - pos)
            light_ray.normalized()
            shadow_ray = Ray(pos, light_ray)
            intersected_data = self.intersected_geometry(shadow_ray,
                                                         ignore_geo=[
                                                             geometry])
            if intersected_data:
                # v = intersected_pos - pos
                # v.normalize()
                diff /= 2

            diffuse = diff * light.color
            ambient_diffuse += ambient + diffuse

        if reflections is True:
            normal = self.calculate_normal(tri.world_v0,
                                           tri.world_v1,
                                           tri.world_v2)
            refl_direction = self.reflect_vector(ray.direction.normalized(),
                                                 normal)

            reflection_ray = Ray(pos, refl_direction)

            refl_data = self.intersected_geometries(reflection_ray,
                                                    ignore_tri=[tri],
                                                    ignore_geo=[geometry])

            refl_data = self.get_nearest_data_point(reflection_ray.pos,
                                                    refl_data)

            if refl_data:
                refl_color = [0.0, 0.0, 0.0]
                screen_pos = self.world_to_screen(refl_data.pos)
                relf_ray = self.screen_to_ray(screen_pos)

                self.render_tri(refl_data.geometry, refl_data.tri,
                                refl_data.pos, refl_color, relf_ray,
                                reflections=False)
                relf_c = QtGui.QVector3D(refl_color[0], refl_color[1],
                                         refl_color[2])
                object_color = QtGui.QVector3D(object_color)
                object_color += relf_c
                self.clamp_color_vector(object_color)

        ambient_diffuse /= self.__total_lights
        color_out = ambient_diffuse * object_color
        color[0] = color_out.x()
        color[1] = color_out.y()
        color[2] = color_out.z()

    def clamp_color_vector(self, v):
        v.setX(v.x() if v.x() < 1.0 else 1.0)
        v.setY(v.y() if v.y() < 1.0 else 1.0)
        v.setZ(v.z() if v.z() < 1.0 else 1.0)

    def screen_to_world_cache(self, x, y, z):
        key = "{}-{}-{}".format(x, y, z)
        if key in self._screen_to_world_cache:
            return self._screen_to_world_cache[key]

        pos = self.screen_to_world(QtGui.QVector3D(x, y, z))
        self._screen_to_world_cache[key] = pos
        return pos

    def intersected_geometry(self, ray, ignore_geo=None, ignore_tri=None):
        res = self.intersected_geometries(ray, ignore_geo=ignore_geo,
                                          ignore_tri=ignore_tri, first=True)
        if res:
            return res[0]
        else:
            return None

    def intersected_geometries(self, ray, ignore_geo=None, ignore_tri=None,
                               first=False):
        data_list = []
        for obj in self.__geometries:
            if ignore_geo and obj in ignore_geo:
                continue

            if not self.intersect_boundingbox(obj.boundingbox_worldspace,
                                              ray):
                continue

            for tri in obj.tris:
                if ignore_tri and tri in ignore_tri:
                    continue
                # put the triangle in world space
                pos = self.intersect_triangle(ray, tri)
                if pos:
                    data = DataPoint(pos=pos, tri=tri, geometry=obj)
                    data_list.append(data)
                    if first is True:
                        return data_list
        return data_list

    def render_pixel(self, ray, color):
        hitting_tris = {}
        hit_geo = False
        for obj in self.__geometries:
            if not self.intersect_boundingbox(obj.boundingbox_worldspace,
                                              ray):
                continue
            for tri in obj.tris:
                pos = self.intersect_triangle(ray, tri)
                if pos:
                    hit_geo = True
                    distance = (pos - ray.pos).length()
                    hitting_tris[distance] = (obj, tri, pos)
        if not hit_geo:
            color[0] = 0.3
            color[1] = 0.3
            color[2] = 0.3
            return


        keys = hitting_tris.keys()

        k = keys[0]
        geometry, tri, pos = hitting_tris[k]
        self.render_tri(geometry, tri, pos, color, ray)
        return

    def screen_to_ray(self, screen_pos):
        far = self.screen_to_world(QtGui.QVector3D(screen_pos.x(), screen_pos.y(), -1))
        near = self.screen_to_world(QtGui.QVector3D(screen_pos.x(), screen_pos.y(), 1))
        direction = (far - near).normalized()
        ray = Ray(near, direction)
        return ray

    def calculate_rays(self):
        width = self.render_resolution.width()
        height = self.render_resolution.height()
        step_width = 1.0 / float(width)
        step_height = 1.0 / float(height)
        half_step_width = step_width / 2.0
        half_step_height = step_height / 2.0
        rays = []
        for y in range(height):
            row = []
            rays.append(row)
            for x in range(width):
                screen_y = ((((
                                  step_height * y) + half_step_height) * 2.0) - 1.0) * -1
                screen_x = (((step_width * x) + half_step_width) * 2.0) - 1.0
                ray = self.screen_to_ray(QtGui.QVector2D(screen_x, screen_y))
                row.append(ray)
        self.rays = rays

    def start(self):
        # index objects
        self.__geometries = []
        for obj in self.objects:
            if isinstance(obj, Geometry):
                self.__geometries.append(obj)
            elif isinstance(obj, PointLight):
                self.__lights.append(obj)

        self.__total_lights = len(self.__lights)

    def render(self):

        self.is_rendering = True
        start = time.time()

        # calculate world tris
        for obj in self.__geometries:
            for tri in obj.tris:
                tri.calculate_world()

        for y, col in enumerate(self.__output_data):
            for x, color in enumerate(col):
                ray = self.rays[y][x]
                self.render_pixel(ray, color)

        output_image = []
        for x in self.__output_data:
            row = []
            output_image.append(row)

            for color in x:
                r = color[0] * 255
                r = r if r < 255 else 255
                g = color[1] * 255
                g = g if g < 255 else 255
                b = color[2] * 255
                b = b if b < 255 else 255
                c = QtGui.QColor(r, g, b)
                row.append(c)

        # self.output_data = output_image
        self.fps = 1.0 / float(time.time() - start)
        self.is_rendering = False

    @property
    def output_data(self):
        return self.__output_data

    def get_nearest_data_point(self, p, data_points):
        nearest_distance = sys.float_info.max
        nearest_data_point = None
        for data_point in data_points:
            distance = (data_point.pos - p).length()
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_data_point = data_point
        return nearest_data_point


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
        eye = QtGui.QVector3D(2, 5, 0.8)
        eye = QtGui.QVector3D(2, 2, 0.8)

        self.ray_tracer.render_camera.matrix.lookAt(
            eye, QtGui.QVector3D(),
            QtGui.QVector3D(0, 1, 0))
        self.light = PointLight()
        self.light.name = "p1"
        self.light.translate(2, 2, -2)
        self.light.color = QtGui.QVector3D(1.0, 0.64, 0.18)
        self.ray_tracer.objects.append(self.light)

        self.light = PointLight()
        self.light.name = "p2"
        self.light.translate(-2, 5, 0)
        self.light.color = QtGui.QVector3D(0.368, 156.0 / 255.0, 242.0 / 255.0)
        self.ray_tracer.objects.append(self.light)

        self.cube = Cube()
        self.cube.object_color = QtGui.QVector3D(0.2, 0.8, 0.3)
        self.cube.name = "center"
        self.cube.matrix.translate(0, 0, 0)
        self.ray_tracer.objects.append(self.cube)

        self.cube2 = Cube()
        self.cube2.name = "floor"
        self.cube2.matrix.scale(6.0, 0.2, 6.0)
        self.cube2.matrix.translate(0, -3.0, 0)
        self.cube2.object_color = QtGui.QVector3D(0.8, 0.3, 0.2)
        self.cube2.calculate()
        self.ray_tracer.objects.append(self.cube2)

        self.ray_tracer.calculate_matrices()
        self.ray_tracer.calculate_rays()
        self.ray_tracer.setup_output_data()

        # self.ray_tracer.objects.append(Locator())

        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(1000.0 / 25.0))
        self.timer.timeout.connect(self.tick)
        self.timer.start()

        self.show_viewport = True
        self.rays_to_paints = []

    def tick(self):
        if self.render:
            self.ray_tracer.render()

        self.cube.matrix.rotate(1, QtGui.QVector3D(0, 1, 0))
        self.cube.calculate()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Backspace:
            self.ray_tracer.setup_output_data()
            self.update()
        if event.key() == QtCore.Qt.Key_H:
            self.show_viewport = not self.show_viewport
            self.update()

        if event.key() == QtCore.Qt.Key_S:
            self.ray_tracer.enabled_shadows = not self.ray_tracer.enabled_shadows
            self.update()

        if event.key() == QtCore.Qt.Key_R:
            self.ray_tracer.enabled_reflections = not self.ray_tracer.enabled_reflections
            self.update()

        if event.key() == QtCore.Qt.Key_Space:
            self.render = not self.render
            if self.render:
                self.ray_tracer.start()

        if event.key() == QtCore.Qt.Key_Up:
            self.ray_tracer.render_resolution *= 2
            self.ray_tracer.setup_output_data()
            self.ray_tracer.calculate_rays()

        if event.key() == QtCore.Qt.Key_Down:
            self.ray_tracer.render_resolution /= 2
            self.ray_tracer.setup_output_data()
            self.ray_tracer.calculate_rays()

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
        v0_device = self.world_to_device(triangle.world_v0)
        v1_device = self.world_to_device(triangle.world_v1)
        v2_device = self.world_to_device(triangle.world_v2)
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
            self.paint_triangle(painter, t, geometry)

        for v in geometry.verts:
            self.paint_vertex(painter,
                              self.multiply_matrix(v, geometry.matrix))

        self.paint_boundingbox(painter, geometry.boundingbox_worldspace)
        self.paint_pivot(painter, geometry.matrix)

    def paint_boundingbox(self, painter, boundingbox):
        p2_device = self.world_to_device(boundingbox.min)
        p1_device = self.world_to_device(boundingbox.max)

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
                                 QtGui.QColor(color[0] * 255, color[1] * 255,
                                              color[2] * 255))
                # painter.drawRect(paint_x, paint_y, pixel_width, pixel_height)

    def paint_light(self, painter, obj):
        position = QtGui.QVector3D(obj.matrix.column(3))
        pos_device = self.world_to_device(position)
        painter.drawEllipse(pos_device.x(), pos_device.y(), 20, 20)
        painter.drawText(pos_device.x(), pos_device.y() - 15, str(obj.name))

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        painter.fillRect(0, 0, self.width(), self.height(),
                         QtGui.QColor(70, 70, 70))

        self.paint_output_data(painter)
        rays = self.ray_tracer.render_resolution.width() * self.ray_tracer.render_resolution.height()
        info = "Raytracer | {:.2f} fps | {} rays".format(self.ray_tracer.fps,
                                                         rays)

        painter.drawText(20, 20, info)
        info = "Rendering: {} | Shadows: {} | Reflections {}".format(
            self.render, self.ray_tracer.enabled_shadows,
            self.ray_tracer.enabled_reflections)
        painter.drawText(20, 40, info)
        if self.show_viewport:
            for obj in self.ray_tracer.objects:
                if isinstance(obj, Geometry):
                    self.paint_geometry(painter, obj)
                elif isinstance(obj, Locator):
                    self.paint_locator(painter, obj)
                elif isinstance(obj, PointLight):
                    self.paint_light(painter, obj)

            for ray in self.rays_to_paints:
                self.paint_ray(painter, ray, 20)

    def paint_ray(self, painter, ray, length=1.0):
        self.paint_line(painter, ray.pos, ray.pos + ray.direction * length)

    def sizeHint(self, *args, **kwargs):
        return QtCore.QSize(300, 300)

    def mousePressEvent(self, event):
        self.rays_to_paints = []
        screen_pos = self.device_to_screen(event.pos())
        ray = self.ray_tracer.screen_to_ray(screen_pos)
        self.rays_to_paints.append(ray)
        data = self.ray_tracer.intersected_geometries(ray)
        data = self.ray_tracer.get_nearest_data_point(ray.pos, data)

        if data:
            normal = self.ray_tracer.calculate_normal(data.tri.world_v0,
                                                      data.tri.world_v1,
                                                      data.tri.world_v2)
            print "-"
            print ray.direction
            print data.geometry.name

            # print normal
            refl_direction = self.ray_tracer.reflect_vector(
                ray.direction.normalized(), normal)
            print refl_direction
            # print refl_direction.normalized()
            refl_ray = Ray(QtGui.QVector3D(data.pos), refl_direction)
            self.rays_to_paints.append(refl_ray)

            refl_data = self.ray_tracer.intersected_geometry(refl_ray)
            if refl_data:
                print "reflection"
                print refl_data


def main():
    app = QtWidgets.QApplication([])
    w = RayTracerWidget()
    w.show()
    app.exec_()


if __name__ == '__main__':
    main()
