from time import sleep
from typing import List, Tuple
import math
import pygame as pg
from math import cos, sin
import pygame.display
from pygame import Vector3
from pygame.math import Vector2

delta_rotation = math.pi / 18

NUMPY_POINT = False

SHOW_EDGES = True
SHOW_POINTS = False
SHOW_POINTS |= SHOW_EDGES
SHOW_POLYGONS = True
SHOW_NORMALS = False
IGNOR_NORMAL = False
CUTTING_POLYGONS = 0
CUTTING_TYPE = 1

NORMAL_COF = 15
MIN_LIGHT = 35
MIN_LIGHT_ = 0.15

## изменяется при переходе к следующему состоянию сцены
## равен сумме
_tact_3d = 0  # Глобальный счетчик состояния расчета точек
phase_3d = 0
camera_3d = 0
count_camera = 1

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DEFAULT_COLOR_POINT = BLACK

TO_UNKNOWN = -1
TO_N = 0
TO_NW = 1
TO_W = 2
TO_EW = 3
TO_E = 4
TO_ES = 5
TO_S = 6
TO_NS = 7
TO_OFFSET = [
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1)
]

TACT_RESTART = 0
PHASE_OBJECT = 1  # фаза для перещета кординат точек объёков в обёкте
PHASE_MAP = 2  # фаза пересщета локальных кординат объёков в глобальные
PHASE_CAMERA = 3  # пересщет координат из глобальных в координаты камеры
PHASE_SCREEN = 4  # экранные координыты точки для текущей камеры просчитаны
PHASE_COUNT = 5

OBJECT_FLAG_MAP = 1  # в мировых координатах
OBJECT_FLAG_STATIC = 2  # не двигается
OBJECT_FLAG_MOVING = 4  # двигается
OBJECT_FLAG_DEPENDENT = 8  # зависим от родителя
OBJECT_FLAG_VISIBLE = 16  # объект можно увидеть на экране
OBJECT_FLAG_NOT_CALC_GLOBAL = 32  # расчитаны глобальные координаты

POINT_FLAG_NORMAL = 512  # это нормаль

POLYGON_FLAG_HAVENT_NORMAL = 0
POLYGON_FLAG_HAVE_NORMAL = 1
POLYGON_FLAG_COMMON_NORMAL = 2

PI2 = math.pi * 2

TO_UNKNOWN = -1
TO_N = 0
TO_NW = 1
TO_W = 2
TO_EW = 3
TO_E = 4
TO_ES = 5
TO_S = 6
TO_NS = 7
TO_OFFSET = [
    (0, -1),
    (1, -1),
    (1, 0),
    (1, 1),
    (0, 1),
    (-1, 1),
    (-1, 0),
    (-1, -1)
]

Rotation_0 = 0
Rotation_X = 1
Rotation_Y = 2
Rotation_Z = 3

MATRIX_CALC_MODE = 1


def vector_mod(vector, value):
    vector.x %= value
    vector.y %= value
    vector.z %= value
    return vector


def mul_matrix(a, b, c=None):
    s = 3
    if c is None:
        c = [[0] * s for i in range(3)]
    for i in range(s):
        for j in range(s):
            c[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j]
    return c


def crt_rotation_matrix(angle, rot_axis, c=None):
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return crt_rotation_matrix_pre(cos_a, sin_a, rot_axis, c=c)


def crt_rotation_matrix_pre(cos_a, sin_a, rot_axis, c=None):
    s = 3
    if c is None:
        c = [[0] * s for i in range(3)]
    else:
        for i in range(s):
            for j in range(s):
                c[i][j] = 0
    c[0][0] = c[1][1] = c[2][2] = 1
    if rot_axis == Rotation_0:
        return c
    # cos_a = math.cos(angle)
    # sin_a = math.sin(angle)
    if rot_axis == Rotation_X:
        c[1][1] = cos_a
        c[1][2] = -sin_a
        c[2][1] = sin_a
        c[2][2] = cos_a
    elif rot_axis == Rotation_Y:
        c[0][0] = cos_a
        c[0][2] = -sin_a
        c[2][0] = sin_a
        c[2][2] = cos_a
    elif rot_axis == Rotation_Z:
        c[0][0] = cos_a
        c[0][1] = -sin_a
        c[1][0] = sin_a
        c[1][1] = cos_a
    return c


def mul_vector_matrix(a, b, c=None):
    s = 3
    if c is None:
        c = [0] * s
    for j in range(s):
        c[j] = a[0] * b[0][j] + a[1] * b[1][j] + a[2] * b[2][j]
    return c


def scalar_mul_vectors(a, b):
    c = a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    return c


def sub_vectors(a, b, c=None):
    s = 3
    if c is None:
        c = [0] * s
    for j in range(s):
        c[j] = a[j] - b[j]
    return c


def sum_vectors(a, b, c=None):
    s = 3
    if c is None:
        c = [0] * s
    for j in range(s):
        c[j] = a[j] + b[j]
    return c


def vector_mul_vector(a, b, c=None):
    s = 3
    if c is None:
        c = [0] * 3
    a1, a2, a3 = a
    b1, b2, b3 = b
    # i = [(a2 * b3 - b2 * a3), 0, 0]
    # j = [0, (a1 * b3 - b1 * a3), 0]
    # k = [0, 0, (a1 * b2 - b1 * a2)]
    c[:] = [(a2 * b3 - b2 * a3), -(a1 * b3 - b1 * a3), (a1 * b2 - b1 * a2)]
    return c


TLISTS = (tuple, list)


def debug(param):
    pass


def create_matrix_rotate3(rotate3):
    # https://ru.wikipedia.org/wiki/%D0%9C%D0%B0%D1%82%D1%80%D0%B8%D1%86%D0%B0_%D0%BF%D0%BE%D0%B2%D0%BE%D1%80%D0%BE%D1%82%D0%B0
    # https://wikimedia.org/api/rest_v1/media/math/render/svg/ba4ec6507e4b6d47fb1e30e9e30734a18c02f157
    x, y, z = rotate3[0], rotate3[1], rotate3[2]
    sinx, siny, sinz = sin(x), sin(y), sin(z)
    cosx, cosy, cosz = cos(x), cos(y), cos(z)
    mat = [[cosy * cosz, -sinz * cosy, siny],
           [sinx * siny * cosz + sinz * cosx, -sinx * siny * sinz + cosx * cosz, -sinx * cosy],
           [sinx * sinz - siny * cosx * cosz, sinx * cosz + siny * sinz * cosx, cosx * cosy]]
    return mat


# if __name__ == '__main__':
#     p = PointN([1, 2, 3])
#     p3 = Point3((5, 59, 3))
#     p3.x = 1
#     print(p3.x)
#     vn1 = VectorN((1, 1, 2, 10))
#     vn2 = VectorN((1, 5, 2, 10))


# class Vector3(pg.Vector3):
#     @staticmethod
#     def zero():
#         return Vector3(0, 0, 0)


class MatrixRotation3:
    def __init__(self, rotation):
        self.matrix_calc_mode = MATRIX_CALC_MODE
        self._rotation = Vector3(rotation)
        # flags of calculated x, y, z
        self.calc_flag = [False, False, False]

        self._sinx, self._siny, self._sinz = 0, 0, 0
        self._cosx, self._cosy, self._cosz = 0, 0, 0
        self._matrix = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        self._matrixes = [None, None, None]
        self._mul1_0 = None

    def get_matrix(self):
        if self.matrix_calc_mode == 3:
            return self._matrix
        if not all(self.calc_flag):
            x, y, z = self._rotation.xyz
            if self.matrix_calc_mode == 1:
                if not self.calc_flag[0]:
                    self._sinx = sin(x)
                    self._cosx = cos(x)
                if not self.calc_flag[1]:
                    self._siny = sin(y)
                    self._cosy = cos(y)
                if not self.calc_flag[2]:
                    self._sinz = sin(z)
                    self._cosz = cos(z)
                self._matrix = [[self._cosy * self._cosz, -self._sinz * self._cosy, self._siny],
                                [self._sinx * self._siny * self._cosz + self._sinz * self._cosx,
                                 -self._sinx * self._siny * self._sinz + self._cosx * self._cosz,
                                 -self._sinx * self._cosy],
                                [self._sinx * self._sinz - self._siny * self._cosx * self._cosz,
                                 self._sinx * self._cosz + self._siny * self._sinz * self._cosx,
                                 self._cosx * self._cosy]]

            elif self.matrix_calc_mode == 2:
                if not self.calc_flag[0]:
                    self._matrixes[0] = crt_rotation_matrix(x, Rotation_X)
                if not self.calc_flag[1]:
                    self._matrixes[1] = crt_rotation_matrix(y, Rotation_Y)
                if not self.calc_flag[2]:
                    self._matrixes[2] = crt_rotation_matrix(z, Rotation_Z)
                if not self.calc_flag[0] or not self.calc_flag[1]:
                    self._mul1_0 = mul_matrix(self._matrixes[1], self._matrixes[0])
                if not all(self.calc_flag):
                    self._matrix = mul_matrix(self._matrixes[2], self._mul1_0)
        self.calc_flag = [True] * 3
        return self._matrix

    def set_rotation(self, rotation):
        if rotation.x != self._rotation.x:
            self.calc_flag[0] = False
        if rotation.y != self._rotation.y:
            self.calc_flag[1] = False
        if rotation.z != self._rotation.z:
            self.calc_flag[2] = False
        if self.matrix_calc_mode == 3:
            offset = Vector3(vector_mod(rotation, PI2)) - self._rotation
            if offset.x:
                m = crt_rotation_matrix(offset.x, Rotation_X)
                self._matrix = mul_matrix(self._matrix, m)
            if offset.y:
                m = crt_rotation_matrix(offset.y, Rotation_Y)
                self._matrix = mul_matrix(self._matrix, m)
            if offset.z:
                m = crt_rotation_matrix(offset.z, Rotation_Z)
                self._matrix = mul_matrix(self._matrix, m)
        self._rotation = vector_mod(rotation, PI2)

    @property
    def rotation(self):
        return self._rotation

    def length_squared(self):
        return self._rotation.length_squared()

    def __mul__(self, other):
        if isinstance(other, Vector3) or (isinstance(other, list) and len(other) == 3):
            # _ =
            if self.matrix_calc_mode in (1, 2, 3):
                return mul_vector_matrix(other, self.get_matrix())
            elif self.matrix_calc_mode == 0:
                return (other).rotate_z_rad(self._rotation.z).rotate_y_rad(self._rotation.y).rotate_x_rad(
                    self._rotation.x)
            # return mul_vector_matrix(mul_vector_matrix(mul_vector_matrix(other, self._matrixes[0]), self._matrixes[1]), self._matrixes[2])


def find_intersection_plane(plane_normal: Vector3, plane_point: Vector3, vector_direction: Vector3, vector_point):
    """
    Эта функция находит точку пересечения плоскости и вектора.

    Args:
      plane_normal: вектор, перпендикулярный плоскости.
      plane_point: точка на плоскости.
      vector_direction: вектор направления вектора.
      vector_point: точка, из которой исходит вектор.

    Returns:
      Точка пересечения или None, если векторы параллельны.
    """
    # Проверка на параллельность
    pdv = plane_normal.dot(vector_direction)
    if pdv == 0:
        return None
    # Расстояние от точки на плоскости до плоскости
    d = plane_normal.dot(plane_point - vector_point)
    # Расстояние от точки на векторе до плоскости по направлению вектора
    t = d / pdv
    # Точка пересечения
    intersection_point = vector_point + t * vector_direction
    return intersection_point


def det2d(m):
    return m[0][0] * m[1][1] - m[0][1] * m[1][0]


def find_intersection_lines2d(line1_point1: Vector2, line1_point2: Vector2, line2_point1: Vector2,
                              line2_point2: Vector2) -> Vector2:
    """
    Эта функция находит точку пересечения двух 2D-линий.

    Args:
      line1_point1: Координаты первой точки первой линии (tuple).
      line1_point2: Координаты второй точки первой линии (tuple).
      line2_point1: Координаты первой точки второй линии (tuple).
      line2_point2: Координаты второй точки второй линии (tuple).

    Returns:
      Точка пересечения (tuple) или None, если линии не пересекаются.
    """
    A = (line2_point1[0] - line2_point2[0], line2_point2[1] - line2_point1[1])
    B = (line1_point1[0] - line1_point2[0], line1_point2[1] - line1_point1[1])
    C = (line2_point1[0] - line1_point1[0], line1_point1[1] - line2_point1[1])

    det_AB = det2d([A, B])
    det_AC = det2d([A, C])

    # Проверка на параллельность
    if det_AB == 0:
        return None
    # Расчет параметра t
    t = -det_AC / det_AB
    line1_direction = line1_point2 - line1_point1
    # line2_direction = line2_point2 - line2_point1
    # Вычисление точки пересечения
    intersection_point = Vector2(line1_point1[0] + t * line1_direction[0], line1_point1[1] + t * line1_direction[1])      
    return intersection_point


def create_normal(p0: Vector3, p1, p2):
    # print(p0, p1, p2, "====", (p1 - p0).cross(p2-p0))
    return (p1 - p0).cross(p2 - p0)


def get_color_of_light(color, light):
    return max(color[0] * MIN_LIGHT_, min(255, color[0] * light)), max(color[1] * MIN_LIGHT_,
                                                                       min(255, color[1] * light)), \
        max(color[2] * MIN_LIGHT_, min(255, color[2] * light))


DEF_LAMPS = [Vector3(-0.5, -1, -0.75).normalize()]


def get_light_of_lamps(surface_normal, lamps):
    if lamps:
        lamp_vectors = [lamp.vector for lamp in lamps]
    else:
        lamp_vectors = DEF_LAMPS
    light = sum([max(-surface_normal.dot(v), 0) for v in lamp_vectors])
    return light


def draw_point(camera, color, position2, r=2):
    pg.draw.circle(camera.surface, color, position2, r)


def draw_line(camera, color, position_1, position_2):
    pg.draw.line(camera.surface, color, position_1, position_2, 1)


def draw_polygon(camera, color, positions):
    if SHOW_POLYGONS:
        pg.draw.polygon(camera.surface, color, positions)
    if SHOW_EDGES:
        pg.draw.lines(camera.surface, color, True, positions)


iiiii = 0


class None3D:
    """Nononononon """

    def __init__(self, owner, position, flag=0):
        self._owner = None
        self.set_owner(owner)
        self._children = []
        self._local_position = position
        self.flag = int(flag)
        self._global_position = position

    @property
    def children(self):
        return self._children

    @property
    def owner(self):
        return self._owner

    def set_owner(self, owner):
        self._owner = None if isinstance(owner, Scene3D) else owner
        if self._owner:
            self._owner.__add_child(self)

    def __add_child(self, child_object):
        self.children.append(child_object)

    @property
    def local_position(self):
        return self._local_position

    @property
    def position(self):
        return self.global_position

    @property
    def global_position(self):
        # global iiiii
        # iiiii += 1
        # if isinstance(self, VertexPoint):
        #     print(iiiii, self, self._local_position, self.flag, (self._owner and
        #                                                     self._owner.flag), id(self.flag))
        # print(iiiii, 1, id(self.flag), self.flag, self)
        if self.flag & OBJECT_FLAG_MAP:
            return self._local_position
        if self._owner is None:
            return self._local_position
        # print(iiiii, 1, id(self.flag), self.flag)
        if self._owner.flag & OBJECT_FLAG_NOT_CALC_GLOBAL or self._owner.flag & OBJECT_FLAG_MOVING:
            # print(iiiii, 1, id(self.flag), self.flag)
            self._update_global_position()
        if self.flag & OBJECT_FLAG_NOT_CALC_GLOBAL:
            # print(iiiii, 1, id(self.flag), self.flag)
            self._update_global_position()
            # print(iiiii, 2, id(self.flag), self.flag)
            self.flag = self.flag - OBJECT_FLAG_NOT_CALC_GLOBAL
            # print(3, id(self.flag), self.flag)

        # print(self._owner, self._owner.flag & OBJECT_FLAG_NOT_CALC_GLOBAL)

        return self._global_position

    def _update_global_position(self):
        if self._owner.matrix_rotation.length_squared() == 0:
            self._global_position = self._owner.global_position + self._local_position
        else:
            self._global_position = (
                    self._owner.global_position + self._owner.get_matrix_rotation() * self._local_position)
        return self._global_position

    @position.setter
    def position(self, value: Vector3):
        # print("set", self, value)
        if self.flag & OBJECT_FLAG_MAP or self._owner is None:
            self._local_position = value
        else:
            self._local_position = value - self._owner.global_position
        self.flag |= OBJECT_FLAG_NOT_CALC_GLOBAL + OBJECT_FLAG_MOVING
        # for child in self._children:
        #     child.flag |= OBJECT_FLAG_NOT_CALC_GLOBAL


class VertexPoint(None3D):
    # точка в объекте
    def __init__(self, owner, position, flag=0):
        if NUMPY_POINT:
            self.index = position
        else:
            position = Vector3(position)
        super().__init__(owner, position, flag)
        self.tact_3d = TACT_RESTART
        self.position2d_on_camera = (0, 0)
        self.dist_to_camera = -1

    def set_owner(self, owner):
        self._owner = owner

    # PHASE_OBJECT = 1  # фаза для перещета кординат точек объёков в обёкте
    # PHASE_MAP = 2  # фаза пересщета локальных кординат объёков в глобальные
    # PHASE_CAMERA = 3  # пересщет координат из глобальных в координаты камеры
    # PHASE_SCREEN = 4  # экранные координыты точки для текущей камеры просчитаны
    def calc(self, camera, target_tact_3d):
        if self.tact_3d >= target_tact_3d:
            "# Уже все просчитано"
            return
        if self.flag & OBJECT_FLAG_VISIBLE:
            self.flag ^= OBJECT_FLAG_VISIBLE
        self.position2d_on_camera, self.dist_to_camera, is_visible = camera.calc_point(self.global_position)
        # draw_point(camera, "green", self.position2d_on_camera)
        # self.tact_3d = self._owner.calc_point(camera, self)
        self.tact_3d = target_tact_3d
        if is_visible:
            self.flag |= OBJECT_FLAG_VISIBLE

    def show(self, camera, lamps, color="white"):
        self.calc(camera, _tact_3d + PHASE_SCREEN)
        draw_point(camera, color, self.position2d_on_camera)
        # print(self.position2d_on_camera)
        return self.position2d_on_camera


def init_points_from_lst(owner, points_lst, flag):
    return [VertexPoint(owner, Vector3(point), flag=flag) for point in points_lst]


class Object3d(None3D):
    def __init__(self, owner, position, points_lst=(), edges=(), faces=(), normals=(), rotation=(0, 0, 0), flag=0,
                 colors=[]):
        super().__init__(owner, Vector3(position), flag)
        self.color = WHITE
        self._global_position = Vector3(position)
        self.matrix_rotation = MatrixRotation3(Vector3(rotation))
        self.flag |= OBJECT_FLAG_NOT_CALC_GLOBAL + OBJECT_FLAG_MOVING
        self.points: List[VertexPoint] = init_points_from_lst(self, points_lst, flag=self.flag & OBJECT_FLAG_MAP)
        self.max_radius2 = max(
            [(self.position - pnt.position).length_squared() for pnt in self.points]) if self.points else 0
        self.ext_points = []
        self.edges = list(edges)
        self.faces = list(faces)
        self.normals = list(normals)

        if not faces:
            self.polygons = []
        elif isinstance(faces[0][0], int):
            # elif self.normals:
            self.polygons = [Polygon(self, [self.points[i] for i in face], normal=normal,
                                     flag=POLYGON_FLAG_HAVE_NORMAL, color=self.color)
                             for face, normal in zip(self.faces, self.normals)]
            # print(self.faces, self.normals)
        elif len(faces[0][0]) == 3:
            self.polygons = [Polygon(self, [self.points[p[0]] for p in face], normal=self.normals[face[0][2]],
                                     flag=POLYGON_FLAG_HAVE_NORMAL, color=self.color) for face in self.faces]
        if colors:
            for _color, poly in zip(colors, self.polygons):
                if _color:
                    poly.color = _color
        self.tact_3d = TACT_RESTART
        # : разобрать точки на внешние и внутрение

    def __copy__(self):
        points_lst = [pnt.local_position for pnt in self.points]
        return self.__class__(self.owner, self.position, points_lst, [], faces=self.faces, normals=self.normals,
                              rotation=self.rotation, flag=self.flag)

    @property
    def rotation(self):
        return self.matrix_rotation.rotation

    def set_rotation(self, rotation):
        self.matrix_rotation.set_rotation(rotation)
        self.flag |= OBJECT_FLAG_MOVING
        # for child in self._children:
        #     child.flag |= OBJECT_FLAG_NOT_CALC_GLOBAL
        # for child in self.points:
        #     child.flag |= OBJECT_FLAG_NOT_CALC_GLOBAL

    def get_matrix_rotation(self):
        return self.matrix_rotation

    def calc_point(self, camera, point: VertexPoint):
        pass

    def add_point(self, point: VertexPoint):
        self.points.append(point)

    def add_ext_point(self, point: VertexPoint):
        self.ext_points.append(point)

    def calc(self, camera, target_tact_3d):
        # print("calc", self)
        if self.tact_3d >= target_tact_3d:
            # Уже все просчитано
            return
        if self.flag & OBJECT_FLAG_VISIBLE:
            self.flag ^= OBJECT_FLAG_VISIBLE
        if camera.object_is_visible(self):
            self.flag |= OBJECT_FLAG_VISIBLE
            for point in self.points:
                point.calc(camera, target_tact_3d)
            for polygon in self.polygons:
                polygon.calc(camera)
        self.tact_3d = target_tact_3d
        if self.flag & OBJECT_FLAG_MOVING:
            self.flag -= OBJECT_FLAG_MOVING

    def show(self, camera, lamps):
        color = pg.color.Color(WHITE)
        self.calc(camera, _tact_3d + PHASE_SCREEN)
        if self.flag & OBJECT_FLAG_VISIBLE:
            if SHOW_POINTS:
                points2d = []
                for point in self.points:
                    if point.flag & OBJECT_FLAG_VISIBLE:
                        points2d.append(point.show(camera, lamps))
                        point.flag ^= OBJECT_FLAG_VISIBLE
                    else:
                        points2d.append(None)
                if SHOW_EDGES and not self.faces:
                    for pos_i1, pos_i2 in self.edges:
                        if points2d[pos_i1] and points2d[pos_i2]:
                            draw_line(camera, color, points2d[pos_i1], points2d[pos_i2])
            # if SHOW_POLYGONS:
            #     for polygon in self.polygons:
            #         polygon.show(camera, lamps)


class Surface3d(object):
    def __init__(self, owner, polygons=[]):
        self.owner = owner
        self.polygons = polygons
        self.tact_3d = TACT_RESTART


class Surface3dMonocolor(Surface3d):
    def __init__(self, owner, polygons=[], rgb=WHITE, alpha=255):
        super(Surface3dMonocolor, self).__init__(owner, polygons)
        self.rgb = rgb
        self.alpha = alpha


class Polygon:
    def __init__(self, owner, points: List[VertexPoint], flag=0, normal=(0, 0, 0), color=WHITE, cuttings=0):
        self.owner = owner
        self.color = color
        self.points = points
        self.points2d_on_camera = []
        self.flag = int(flag)
        self.cuttings = cuttings
        self._init_normal = Vector3(normal)
        if self._init_normal.length() > 0:
            self._init_normal.normalize_ip()

        self._center_point = VertexPoint(owner, self.get_center_position(), flag=OBJECT_FLAG_NOT_CALC_GLOBAL)

        self._init_normal_point = VertexPoint(owner, self._center_point.local_position + Vector3(normal) * NORMAL_COF,
                                              flag=OBJECT_FLAG_NOT_CALC_GLOBAL + POINT_FLAG_NORMAL)
        if flag & POLYGON_FLAG_HAVE_NORMAL:
            self.normal: Vector3 = self.update_normal()
        else:
            #  None
            self.normal: Vector3 = Vector3(0)

    def get_center_position(self):
        return sum([pnt.local_position for pnt in self.points], Vector3(0)) / len(self.points)

    def update_normal(self):
        self.normal = (self._init_normal_point.position - self._center_point.position).normalize()
        # self.normal = Vector3(self.owner.get_matrix_rotation() * self._init_normal)
        return self.normal

    def calc(self, camera):
        if self.flag & OBJECT_FLAG_VISIBLE:
            self.flag ^= OBJECT_FLAG_VISIBLE

        vis_points: List[VertexPoint] = [pnt for pnt in self.points if pnt.flag & OBJECT_FLAG_VISIBLE]
        if vis_points:
            vec = self._center_point.position - camera.position
            if self.owner.flag & OBJECT_FLAG_MOVING:
                self.update_normal()
            # print(self.normal, vec, vec.dot(self.normal))
            if vec.dot(self.normal) < 0 or IGNOR_NORMAL:
                if len(vis_points) == len(self.points):
                    self.flag |= OBJECT_FLAG_VISIBLE
                    camera.polygons.add(self)
                    self.points2d_on_camera = [pnt.position2d_on_camera for pnt in self.points]
                elif CUTTING_TYPE == 1:
                    self.points2d_on_camera = []
                    for i in range(len(self.points)):
                        p = self.points[i]
                        if p.flag & OBJECT_FLAG_VISIBLE:
                            self.points2d_on_camera.append(p.position2d_on_camera)
                        elif p.dist_to_camera > 0:
                            p2 = self.points[i - 1]
                            if p2.flag & OBJECT_FLAG_VISIBLE:
                                n_point = camera.cut_line2d(p2.position2d_on_camera, p.position2d_on_camera)
                                if n_point:
                                    self.points2d_on_camera.append(n_point)
                            p2 = self.points[(i + 1) % len(self.points)]
                            if p2.flag & OBJECT_FLAG_VISIBLE:
                                n_point = camera.cut_line2d(p2.position2d_on_camera, p.position2d_on_camera)
                                if n_point:
                                    self.points2d_on_camera.append(n_point)

                    if len(self.points2d_on_camera) >= 3:
                        self.flag |= OBJECT_FLAG_VISIBLE
                        camera.polygons.add(self)

                elif self.cuttings < CUTTING_POLYGONS and len(self.points) == 3:
                    if len(vis_points) == 2:
                        p1, p2 = vis_points
                        p3 = [pnt for pnt in self.points if not pnt.flag & OBJECT_FLAG_VISIBLE][0]
                        if p3.dist_to_camera < 0:
                            return
                    else:
                        p1 = vis_points[0]
                        p2, p3 = [pnt for pnt in self.points if not pnt.flag & OBJECT_FLAG_VISIBLE]
                        if p2.dist_to_camera < 0 or p3.dist_to_camera < 0:
                            return

                    p3_ = VertexPoint(p1.owner, p3.position + (p1.position - p3.position) / 2)
                    p3_.calc(camera, _tact_3d)
                    if not p3_.flag & OBJECT_FLAG_VISIBLE:
                        p3_ = VertexPoint(p2.owner, p3.position + (p2.position - p3.position) / 2)
                        p3_.calc(camera, _tact_3d)
                        Polygon(self.owner, [p3, p1, p3_], flag=self.flag, normal=self.normal,
                                color=self.color, cuttings=self.cuttings + 1).calc(camera)
                    else:
                        Polygon(self.owner, [p3, p2, p3_], flag=self.flag, normal=self.normal,
                                color=self.color, cuttings=self.cuttings + 1).calc(camera)

                    poly_1 = Polygon(self.owner, [p1, p2, p3_], flag=self.flag, normal=self.normal,
                                     color=self.color, cuttings=self.cuttings + 1)
                    poly_1.calc(camera)

    def show(self, camera, lamps):
        if self.flag & OBJECT_FLAG_VISIBLE:
            # self._center_point.calc(camera, _tact_3d + PHASE_SCREEN)
            light = get_light_of_lamps(self.normal, lamps)
            # z = self._center_point.dist_to_camera
            # if z > 0:
            #     light += 0.1
            #     light *= (10000 - z) / 10000
            # points2d = [pnt.position2d_on_camera for pnt in self.points]
            draw_polygon(camera, get_color_of_light(self.color, light), self.points2d_on_camera)
            if SHOW_NORMALS:
                self._init_normal_point.calc(camera, _tact_3d + PHASE_SCREEN)
                # self._init_normal_point.show(camera, lamps, color="green")

                self._center_point.show(camera, lamps, color="green")
                draw_line(camera, "red", self._center_point.position2d_on_camera,
                          self._init_normal_point.position2d_on_camera)


class FlatSurface3d(Surface3d):
    def __init__(self, owner, polygons: List[Polygon] = [], normal=None):
        super(FlatSurface3d, self).__init__(owner, polygons)
        if normal == None:
            normal = polygons[0].update_normal()
        self.normal = normal

    def is_show(self):
        ##        point =
        return

    # def get_map_xyz(self):
    #
    #     return position

    # def get_screen_xy(self):
    #
    #     r_matrix = pg.struct_3d["rm"]
    #     o_xyz = pg.struct_3d["O"]
    #     x, y = xy
    #     z *= pg.scale
    #     v_xyz = sum_vectors(mul_vector_matrix((x, y, z), r_matrix), o_xyz)
    #     x, y, z = v_xyz
    #     K = self.focus / (self.focus + z)
    #     x, y = (int(x * K)+self.offset_x, int(y * K)+self.offset_x)
    #     if 0 <= x <= self.width and 0 <= y <= self.height:
    #         return (x, y)
    #     return None


def convert_faces_to_lines(faces):
    lines = set()
    for face in faces:
        lines.add(tuple(sorted((face[0], face[-1]))))
        lines |= {tuple(sorted((face[i], face[i + 1]))) for i in range(len(face) - 1)}

    return lines


def create_cube(owner, position, size, flag=0, color=WHITE):
    return create_box(owner, position, (size, size, size), flag, color=color)


def create_box(owner, position, size3, flag=0, color=WHITE, no_faces=False):
    hx, hy, hz = (Vector3(size3) / 2).xyz
    if flag & OBJECT_FLAG_MAP:
        x, y, z = Vector3(position).xyz
    else:
        x, y, z = 0, 0, 0
    points3 = [
        (x - hx, y + hy, z + hz),
        (x - hx, y + hy, z - hz),
        (x + hx, y + hy, z - hz),
        (x + hx, y + hy, z + hz),
        (x - hx, y - hy, z + hz),
        (x - hx, y - hy, z - hz),
        (x + hx, y - hy, z - hz),
        (x + hx, y - hy, z + hz),
        (x, y, z), ]

    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 2, 6, 5), (3, 2, 6, 7), (0, 3, 7, 4)]
    colors = [color] * len(faces)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (7, 6), (6, 5), (5, 4), (4, 7)]
    if no_faces:
        faces = []
    normals = [(0, 1, 0), (0, -1, 0), (-1, 0, 0), (0, 0, -1), (1, 0, 0), (0, 0, 1)]
    # faces = [(1, 2, 6, 5)]
    # normals = [(0, 0, -1)]

    return Object3d(owner, position, points3, edges, faces, normals, flag=flag, colors=colors)


def create_sys_coord(owner, position, length, width, colors=(RED, GREEN, BLUE)):
    obj = Object3d(owner, position)
    if isinstance(length, (float, int)):
        length = length, length, length
    box_x = create_box(obj, Vector3(length[0] / 2, 0, 0), Vector3(length[0], width, width), color=colors[0])
    box_y = create_box(obj, Vector3(0, length[1] / 2, 0), Vector3(width, length[1], width), color=colors[1])
    box_z = create_box(obj, Vector3(0, 0, length[2] / 2), Vector3(width, width, length[2]), color=colors[2])
    obj.x_length, obj.y_length, obj.z_length = length
    return obj


def open_file_obj(path, scale=1, _convert_faces_to_lines=False, ):
    if isinstance(scale, int):
        scale = (scale, scale, scale)
    with open(path, "r") as f:
        lines = f.readlines()

    vertexes = []
    faces = []
    normals = []
    normals_of_face = {}
    vertex_index_offset = 0
    i = 0
    for line in lines:
        i += 1
        if not line.replace(" ", "") or line[0] == "#":
            continue
        try:
            b = line.split()[0]
        except Exception as ex:
            b = None
            print(f"Warning line {i} open obj", line, ex)

        if b == "o":
            # object
            vertex_index_offset = len(vertexes)
        if b == "v":
            split = line.split()
            vertex = [float(split[i + 1]) * scale[i] for i in range(3)]
            vertexes.append(vertex)
        if b == "vn":
            split = line.split()
            normal = [float(split[i + 1]) for i in range(3)]
            normals.append(normal)
        if b == "f":
            face = []
            for st in line.split(" ")[1:]:
                try:
                    ar = list(map(lambda ii: int(ii) - 1 if ii else -1, st.split("/")))
                except:
                    print(line)
                if len(ar) == 1:
                    ar = [ar[0], None, None]
                if len(ar) == 2:
                    ar = [ar[0], None, ar[1]]
                face.append(ar)
            faces.append(face)
    if _convert_faces_to_lines:
        return vertexes, convert_faces_to_lines(faces), faces, normals
    return vertexes, faces, normals


def convert_faces_to_lines(faces):
    lines = set()
    for face in faces:
        lines.add(tuple(sorted((face[0], face[-1]))))
        lines |= {tuple(sorted((face[i], face[i + 1]))) for i in range(len(face) - 1)}

    return lines


def load_object_from_fileobj(owner, position, path, scale=1, flag=0, color=WHITE):
    vertexes, faces, normals = open_file_obj(path, scale, _convert_faces_to_lines=False)
    print(f"Load model: {path}, vertexes: {len(vertexes)}, faces: {len(faces)}, normals: {len(normals)}")
    edges = []
    colors = [color] * len(faces)
    obj = Object3d(owner, position, vertexes, edges, faces, normals, flag=flag, colors=colors)
    return obj


class Scene3D(object):
    def __init__(self):
        self.static: List[Object3d] = []
        self.lamps = []

    def add_static(self, obj: Object3d | List[Object3d], auto_add_children=True):
        if isinstance(obj, (list, tuple)):
            for obj_ in obj:
                self.add_static(obj_)
        else:
            self.static.append(obj)
            if auto_add_children and obj.children:
                for obj_ in obj.children:
                    self.add_static(obj_)

    def show(self, camera):
        for obj in self.static:
            obj.show(camera, self.lamps)


class CameraPolygons:
    def __init__(self, camera, scene):
        self.camera = camera
        self.scene = scene
        self.polygons: List[Tuple[Polygon, int]] = []

    def add(self, polygon: Polygon):
        max_dist = max([pnt.dist_to_camera for pnt in polygon.points + []])
        self.polygons.append((polygon, max_dist))

    def clear(self):
        self.polygons.clear()

    def show(self):
        self.polygons.sort(key=lambda x: x[1], reverse=True)
        for element in self.polygons:
            element[0].show(self.camera, self.scene.lamps)


class Camera(None3D):
    def __init__(self, owner, scene: Scene3D, surface: pg.Surface, position: Vector3, rotation: Vector3,
                 fov: float = math.pi / 3, background=BLACK):
        super().__init__(owner, Vector3(position), flag=0)
        self.surface = surface
        self.scene = scene
        self.background = background
        self.width, self.height = surface.get_size()
        self.surface_rect = pg.Rect(0, 0, self.width, self.height)
        self.half_w, self.half_h = self.width // 2, self.height // 2
        self.fov = fov
        self.focus = math.atan(self.fov / 2) * self.half_w
        print(self.focus)
        # init property enable
        self._active = True
        self._visible_distance = 15000
        self._visible_distance2 = self._visible_distance ** 2
        self.matrix_rotation = MatrixRotation3(rotation)
        self.matrix_rotation.matrix_calc_mode = 2
        self.polygons = CameraPolygons(self, self.scene)

    def cut_line3d(self, point_1, point_2):
        point = self.position
        rect_points = self.get_rect_points3d()
        rect_vectors = [p - point for p in rect_points]
        normal_top = rect_vectors[0].cross(rect_vectors[1])
        normal_left = rect_vectors[1].cross(rect_vectors[2])
        normal_bottom = rect_vectors[2].cross(rect_vectors[3])
        normal_right = rect_vectors[3].cross(rect_vectors[0])

    def cut_line2d(self, point_1, point_2):
        p1, p2 = Vector2(point_1), Vector2(point_2)
        sr = self.surface_rect
        rect_points = Vector2(sr.x, 0), Vector2(sr.w, 0), Vector2(sr.w, sr.h), Vector2(0, sr.h)
        for i in range(4):
            line = rect_points[i], rect_points[(i + 1) % 4]
            rpoint = find_intersection_lines2d(line[0], line[1], p1, p2)
            if rpoint is not None:
                return rpoint

    @property
    def rotation(self):
        return self.matrix_rotation.rotation

    def set_rotation(self, rotation):
        self.matrix_rotation.set_rotation(rotation)

    def get_matrix_rotation(self):
        return self.matrix_rotation

    def get_rect_points3d(self):
        rect_points = Vector3(-self.half_w, self.half_h, self.focus), Vector3(self.half_w, self.half_h, self.focus), \
            Vector3(self.half_w, -self.half_h, self.focus), Vector3(-self.half_w, -self.half_h, self.focus)
        m = self.get_matrix_rotation()
        return [m * p for p in rect_points]

    def calc_point(self, global_position) -> Tuple[Tuple[float, float], float, bool]:
        position_from_camera = global_position - self.global_position
        vec_at_camera = self.get_matrix_rotation() * position_from_camera
        dist = vec_at_camera[2]
        if dist == 0:
            dist = 1e-9
        x = self.focus * vec_at_camera[0] / dist + self.half_w
        y = self.half_h - self.focus * vec_at_camera[1] / dist
        is_visible = self.surface_rect.collidepoint((x, y)) and dist > 0
        return (x, y), dist, is_visible

    def object_is_visible(self, object3d: None3D):
        # TODO: Простая проверка виден ли объект на камере
        if isinstance(object3d, Object3d):
            return (
                    object3d.global_position - self.global_position).length_squared() <= self._visible_distance2 + object3d.max_radius2
        elif isinstance(object3d, VertexPoint):
            return (object3d.global_position - self.global_position).length_squared() <= self._visible_distance2

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self.set_active(value)

    def set_active(self, value=True):
        self._active = value
        # end active

    def show(self):
        if self.background:
            self.surface.fill(self.background)
        self.polygons.clear()
        self.scene.show(self)
        # if SHOW_POLYGONS:
        self.polygons.show()


class Producer(object):
    """
    PHASE_OBJECT = 1
    PHASE_MAP = 2
    PHASE_CAMERA = 3
    PHASE_SCREEN = 4

    tact_3d = 0
    phase_3d = 0
    camera_3d = 0
    count_camera = 1
    """

    def __init__(self):
        self.cameras: List[Camera] = []
        self.count_camera = 0

    def add_camera(self, camera: Camera):
        self.cameras.append(camera)
        self.count_camera += 1

    def new_tact(self):
        global _tact_3d, phase_3d
        _tact_3d += PHASE_COUNT
        phase_3d = 0

    def show(self):
        for cam in self.cameras:
            if cam.active:
                cam.show()
            self.new_tact()  # todo: СДЕЛАТЬ ОТДЕЛЬНЫЙ ТАКТ ДЛЯ КАЖДОЙ КАМЕРЫ


def update_keys(obj, elapsed_time=100, speed=0.2, rot_speed=0.002, start_position=(0, 0, 0)):
    keys = pg.key.get_pressed()
    rx, ry, rz = 0, 0, 0
    ry = 1 if keys[pg.K_LEFT] else (-1 if keys[pg.K_RIGHT] else 0)
    rx = 1 if keys[pg.K_DOWN] else (-1 if keys[pg.K_UP] else 0)
    obj.set_rotation(obj.rotation + Vector3(rx, ry, rz) * rot_speed * elapsed_time)
    vec_speed = Vector3(0, 0, 0)
    ry = obj.rotation.y
    if keys[pg.K_w]:
        vec_speed = Vector3(-math.sin(ry), 0, math.cos(ry))
    elif keys[pg.K_s]:
        vec_speed = -Vector3(-math.sin(ry), 0, math.cos(ry))
    if keys[pg.K_a]:
        vec_speed += -Vector3(math.cos(ry), 0, math.sin(ry))
    elif keys[pg.K_d]:
        vec_speed += Vector3(math.cos(ry), 0, math.sin(ry))
    if keys[pg.K_q]:
        vec_speed += Vector3(0, -1, 0)
    if keys[pg.K_e]:
        vec_speed += Vector3(0, 1, 0)
    obj.position = obj.position + vec_speed * speed * elapsed_time
    if keys[pg.K_0]:
        obj.position = Vector3(start_position)
        obj.set_rotation(Vector3(0, 0, 0))


def clear_screen(screen):
    screen.fill("#000000")


def main():
    pygame.init()
    w, h = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pg.display.set_mode((w, h), flags=pg.RESIZABLE)
    running = True
    obj = load_object_from_fileobj(None, (0, 0, 15), "models/bedroom.obj", scale=1)
    # obj = create_cube(None, (0, 0, 0), 300)
    sys3d = create_sys_coord(None, Vector3(-30, 100, 15), (60, 34, 10), 1)
    scene3d = Scene3D()
    scene3d.add_static([obj, sys3d])
    camera = Camera(scene3d, scene3d, screen, (0, 0, 0), (0, 0, 0), background=(10, 10, 10))
    producer = Producer()
    producer.add_camera(camera)
    clock = pg.time.Clock()
    p1, p2 = Vector2(300, 900), Vector2(800, 900)
    p3 = Vector2(w // 2, h // 2)
    while running:
        p4 = Vector2(pg.mouse.get_pos())
        [exit() for event in pg.event.get(pg.QUIT)]
        # [camera.position.__add__(Vector3(0, 0, -1)) for event in pg.event.get(pg.KEYDOWN)]
        update_keys(camera, clock.tick(30))
        print(clock.get_fps())
        screen.fill(BLACK)
        # obj.set_rotation(obj.rotation + Vector3(0, 0.01, 0))
        producer.show()
        draw_line(camera, "red", p1, p2)
        draw_line(camera, "blue", p3, p4)
        p = find_intersection_lines2d(p1, p2, p3, p4)
        draw_point(camera, "green", p)
        pg.display.flip()

        # camera.focus -= 1
        # print(camera.position)


if __name__ == '__main__':
    main()
