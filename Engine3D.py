import math
from typing import List

import pygame as pg

from Draw2D import *
from ObjReader import open_file_obj
from Vectors import *
from src import App
from constants import *

delta_rotation = math.pi / 18

NUMPY_POINT = False

SHOW_POINTS = True
SHOW_EDGES = True
SHOW_POLYGONS = True
SHOW_NORMALS = True

## изменяется при переходе к следующему состоянию сцены
## равен сумме
_tact_3d = 0  # Глобальный счетчик состояния расчета точек
phase_3d = 0
camera_3d = 0
count_camera = 1


def get_color_of_light(color, light):
    return max(0, min(255, color[0] * light)), max(0, min(255, color[1] * light)), max(0, min(255, color[2] * light))


def get_light_of_lamps(surface_normal, lamps):
    if lamps:
        lamp_vectors = [lamp.vector for lamp in lamps]
    else:
        lamp_vectors = Vector3(-0.5, -1, 0.75).normalize(), -Vector3(-0.5, -1, -0.75).normalize()
    light = sum([-surface_normal.dot(v) for v in lamp_vectors])
    return light


iiiii = 0


class None3D:
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
        position_from_camera = self.global_position - camera.global_position

        # vec_to = position_from_camera
        # vec_to.rotate_y_rad_ip(camera.rotation.y)
        # vec_to.rotate_x_rad_ip(camera.rotation.x)
        # vec_at_camera = vec_to

        vec_at_camera = camera.get_matrix_rotation() * position_from_camera
        self.dist_to_camera = dist = vec_at_camera[2]
        if dist == 0:
            dist = 1e-9
        x = camera.focus * vec_at_camera[0] / dist + camera.half_w
        y = camera.half_h - camera.focus * vec_at_camera[1] / dist
        self.position2d_on_camera = x, y
        # draw_point(camera, "green", self.position2d_on_camera)
        # self.tact_3d = self._owner.calc_point(camera, self)
        self.tact_3d = target_tact_3d
        if camera.surface_rect.collidepoint(self.position2d_on_camera) and dist > 0:
            self.flag |= OBJECT_FLAG_VISIBLE

    def show(self, camera, lamps, color="white"):
        draw_point(camera, color, self.position2d_on_camera)
        return self.position2d_on_camera


def init_points_from_lst(owner, points_lst, flag):
    return [VertexPoint(owner, Vector3(point), flag=flag) for point in points_lst]


class Object3d(None3D):
    def __init__(self, owner, position, points_lst, edges, faces=[], normals=[], rotation=(0, 0, 0), flag=0):
        super().__init__(owner, Vector3(position), flag)
        self._global_position = Vector3(position)
        self.matrix_rotation = MatrixRotation3(Vector3(rotation))
        self.flag |= OBJECT_FLAG_NOT_CALC_GLOBAL + OBJECT_FLAG_MOVING
        self.points: List[VertexPoint] = init_points_from_lst(self, points_lst, flag=self.flag & OBJECT_FLAG_MAP)
        self.max_radius2 = max(
            [(self.position - pnt.position).length_squared() for pnt in self.points]) if self.points else 0
        self.ext_points = []
        self.edges = edges
        self.faces = list(faces)
        self.normals = list(normals)
        if not faces:
            self.polygons = []
        elif isinstance(faces[0][0], int):
            self.polygons = [Polygon(self, [self.points[i] for i in face], normal=normal, flag=POLYGON_FLAG_HAVE_NORMAL)
                             for face, normal in zip(self.faces, self.normals)]
            print(self.faces, self.normals)
        elif len(faces[0][0]) == 3:
            self.polygons = [Polygon(self, [self.points[p[0]] for p in face], normal=self.normals[face[0][2]],
                                     flag=POLYGON_FLAG_HAVE_NORMAL) for face in self.faces]
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

    # SHOW_POINTS = False
    # SHOW_EDGES = False
    # SHOW_POLYGONS = True

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
                if SHOW_EDGES:
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


class FlatSurface3d(Surface3d):
    def __init__(self, owner, polygons=[], normal=None):
        super(FlatSurface3d, self).__init__(owner, polygons)
        if normal == None:
            normal = polygons[0].create_normal()
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


class Polygon:
    def __init__(self, owner, points: List[VertexPoint], flag=0, normal=(0, 0, 0)):
        self.owner = owner
        self.points = points
        self.flag = int(flag)
        self._init_normal = Vector3(normal)

        self._center_point = VertexPoint(owner, self.get_center_position(), flag=OBJECT_FLAG_NOT_CALC_GLOBAL)

        self._init_normal_point = VertexPoint(owner, self._center_point.local_position + Vector3(normal) * 5,
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
        if all(pnt.flag & OBJECT_FLAG_VISIBLE for pnt in self.points):
            # vec = self.points[0].position - camera.position
            vec = self._center_point.position - camera.position
            if self.owner.flag & OBJECT_FLAG_MOVING:
                self.update_normal()
            # print(self.normal, vec, vec.dot(self.normal))
            if vec.dot(self.normal) < 0:
                self.flag |= OBJECT_FLAG_VISIBLE
                camera.polygons.add(self)

    def show(self, camera, lamps):
        if self.flag & OBJECT_FLAG_VISIBLE and SHOW_POLYGONS:
            color = WHITE
            light = get_light_of_lamps(self.normal, lamps)
            points2d = [pnt.position2d_on_camera for pnt in self.points]
            draw_polygon(camera, get_color_of_light(color, light), points2d)
            if SHOW_NORMALS:
                self._init_normal_point.calc(camera, _tact_3d + PHASE_SCREEN)
                # self._init_normal_point.show(camera, lamps, color="green")
                self._center_point.calc(camera, _tact_3d + PHASE_SCREEN)
                self._center_point.show(camera, lamps, color="green")
                draw_line(camera, "red", self._center_point.position2d_on_camera,
                          self._init_normal_point.position2d_on_camera)


def convert_faces_to_lines(faces):
    lines = set()
    for face in faces:
        lines.add(tuple(sorted((face[0], face[-1]))))
        lines |= {tuple(sorted((face[i], face[i + 1]))) for i in range(len(face) - 1)}

    return lines


def create_cube(owner, position, size, flag=0):
    return create_box(owner, position, (size, size, size), flag)


def create_box(owner, position, size3, flag=0):
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
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),
             (7, 6), (6, 5), (5, 4), (4, 7), ]
    faces = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 2, 6, 5), (3, 2, 6, 7), (0, 3, 7, 4)]
    normals = [(0, 1, 0), (0, -1, 0), (-1, 0, 0), (0, 0, -1), (1, 0, 0), (0, 0, 1)]
    # faces = [(1, 2, 6, 5)]
    # normals = [(0, 0, -1)]
    edges = convert_faces_to_lines(faces)
    return Object3d(owner, position, points3, edges, faces, normals, flag=flag)


def load_object_from_fileobj(owner, position, path, scale=1, flag=0):
    vertexes, faces, normals = open_file_obj(path, scale, _convert_faces_to_lines=False)
    print(f"Load model: {path}, vertexes: {len(vertexes)}, faces: {len(faces)}, normals: {len(normals)}")
    obj = Object3d(owner, position, vertexes, [], faces, normals, flag=flag)
    return obj


class Scene3D(object):
    def __init__(self):
        self.static: List[Object3d] = []
        self.lamps = []

    def add_static(self, obj: Object3d):
        self.static.append(obj)

    def show(self, camera):
        for obj in self.static:
            obj.show(camera, self.lamps)


class CameraPolygons:
    def __init__(self, camera, scene):
        self.camera = camera
        self.scene = scene
        self.polygons = []

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
    def __init__(self, owner, scene, surface: pg.Surface, position: Vector3, rotation: Vector3,
                 fov: float = 3.14159 / 3, background=BLACK):
        super().__init__(owner, Vector3(position), flag=0)
        self.surface = surface
        self.scene = scene
        self.background = background
        self.width, self.height = surface.get_size()
        self.surface_rect = pg.Rect(0, 0, self.width, self.height)
        self.half_w, self.half_h = self.width // 2, self.height // 2
        self.fov = fov
        self.focus = self.half_w / math.tan(self.fov / 2)
        # init property enable
        self._active = True
        self._visible_distance = 500
        self._visible_distance2 = self._visible_distance ** 2
        self.matrix_rotation = MatrixRotation3(rotation)
        self.polygons = CameraPolygons(self, self.scene)

    @property
    def rotation(self):
        return self.matrix_rotation.rotation

    def set_rotation(self, rotation):
        self.matrix_rotation.set_rotation(rotation)

    def get_matrix_rotation(self):
        return self.matrix_rotation

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
        self.surface.fill(self.background)
        self.polygons.clear()
        self.scene.show(self)
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
        self.new_tact()


def clear_screen(screen):
    screen.fill("#000000")


class AppScene3D(App.Scene):
    def __init__(self, app) -> None:
        super().__init__(app)
        self.tact = 0

        self.screen.fill(BLACK)
        self.scene3d = Scene3D()
        # self.obj = load_object_from_fileobj(self.scene3d, (0, 0, 0), "models/GAMUNCUL1.obj", scale=8)
        # self.obj = load_object_from_fileobj(self.scene3d, (0, 0, 0), "models/controllerVR.obj", scale=5)
        self.obj = load_object_from_fileobj(self.scene3d, (0, 10, 0), "models/bedroom.obj", scale=8)
        # self.obj = Object3d(self.scene3d, (0, 0, 0), [], [], [])

        # self.obj2 = Object3d(self.scene3d, (0, 0, 0), [(0, 0, 0), (0, 10, 0)], [], [])
        # self.obj2 = load_object_from_fileobj(self.scene3d, (0, 0, 0), "models/monkey1.obj", scale=8)
        self.obj2 = create_cube(None, (0, 1, 0), 10)
        # self.scene3d.add_static(self.obj2)
        # self.scene3d.add_static(obj)
        self.scene3d.add_static(self.obj)
        self.camera = Camera(self.scene3d, self.scene3d, self.screen, (0, 0, -50), (0, 0, 0), background=(10, 10, 10))
        self.producer = Producer()
        self.producer.add_camera(self.camera)
        self.rot_flag = 0

    def pg_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_f:
                self.rot_flag ^= 1
            if event.key == pg.K_c:
                obj = self.obj.__copy__()
                self.scene3d.add_static(obj)

    def update_keys(self):
        keys = pg.key.get_pressed()
        speed = 0.1 * self.elapsed_time
        rot_speed = 0.001 * self.elapsed_time
        camera = self.camera
        # поворот объекта
        rx, ry, rz = 0, 0, 0
        if keys[pg.K_LEFT]:
            ry = -1
        elif keys[pg.K_RIGHT]:
            ry = 1
        if keys[pg.K_UP]:
            rx = 1
        elif keys[pg.K_DOWN]:
            rx = -1
        camera.set_rotation(camera.rotation + Vector3(rx, ry, rz) * rot_speed)
        vec_speed = Vector3(0, 0, 0)
        # смещение
        ry = camera.rotation.y
        if keys[pg.K_w]:
            vec_speed = Vector3(math.sin(ry), 0, math.cos(ry))
        elif keys[pg.K_s]:
            vec_speed = Vector3(-math.sin(ry), 0, -math.cos(ry))
        if keys[pg.K_a]:
            vec_speed += Vector3(-math.cos(ry), 0, math.sin(ry))
        elif keys[pg.K_d]:
            vec_speed += Vector3(math.cos(ry), 0, -math.sin(ry))
        if keys[pg.K_q]:
            vec_speed += Vector3(0, -1, 0)
        if keys[pg.K_e]:
            vec_speed += Vector3(0, 1, 0)
        camera.position = camera.position + vec_speed * speed

    def update(self):
        pg.display.set_caption(f"Cnt: {len(self.scene3d.static)};fps: {int(self.clock.get_fps())}")
        rot_speed = 0.001 * self.elapsed_time
        if self.rot_flag:
            self.obj2.set_rotation(self.obj2.rotation + Vector3(rot_speed, 0, rot_speed))
            self.obj.set_rotation(self.obj.rotation + Vector3(rot_speed, 0, 0))
            # point = Object3d(self.scene3d, self.obj.points[1].position, [(0, 0, 0)], [], [])
            # self.scene3d.add_static(point)
            # for pos in self.obj2.points:
            #     point = Object3d(self.scene3d, pos.position, [(0, 0, 0)], [], [])
            #     self.scene3d.add_static(point)

        self.producer.show()
        pg.display.flip()
        self.update_keys()


def main():
    FPS = 600
    width, height = 2560, 1440
    pg.init()
    screen = pg.display.set_mode((width, height), flags=pg.RESIZABLE)
    app = App.App(screen, fps=FPS)
    app.set_scene(AppScene3D(app))
    app.main()


if __name__ == '__main__':
    main()
