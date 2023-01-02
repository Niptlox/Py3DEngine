from logging import debug
from random import randint
from typing import List
import pygame as pg
import math

from ObjReader import open_file_obj
from settings import *
from Drawing import *

WINDOW_RECT = pg.Rect((-W_WIDTH, -W_HEIGHT), (W_WIDTH * 3, W_HEIGHT * 3))

pg.init()
pg.mouse.set_visible(False)
font = pg.font.SysFont("", 20)

screen = pg.display.set_mode(WINDOW_SIZE)
clock = pg.time.Clock()
screen.set_clip()


def get_color_of_light(color, light):
    return min(255, color[0] * light), min(255, color[1] * light), min(255, color[2] * light)


def get_center_points(vertexes):
    return sum(vertexes, Vector3.zero()) / len(vertexes)


class Vector3(pg.Vector3):
    @staticmethod
    def zero():
        return Vector3(0, 0, 0)


class Angle3(pg.Vector3):
    @staticmethod
    def zero():
        return Angle3(0, 0, 0)


class Object:
    def __init__(self, position: Vector3 = Vector3.zero(), rotation: Angle3 = Angle3.zero()):
        self.position = Vector3(position)
        self.rotation = Angle3(rotation)
        self.color = WHITE


class ObjectGroup(Object):
    def __init__(self, objects: List[Object]):
        if objects:
            pos = get_center_points(list(map(lambda x: x.position, objects)))
        else:
            pos = Vector3.zero()
        super(ObjectGroup, self).__init__(pos)
        self.objects = objects


class ObjectRotateGroup(ObjectGroup):
    def __init__(self, objects: List[Object], rotation: Angle3):
        super(ObjectRotateGroup, self).__init__(objects)
        self.rotation = Angle3(rotation)


class Point(Object):
    radius = 3

    def __init__(self, position, color=WHITE):
        super(Point, self).__init__(position)
        self.color = color

    def draw(self, surface, pos2d, light=1):
        pg.draw.circle(surface, get_color_of_light(self.color, light), pos2d, radius=self.radius, width=2)


class Points(Object):
    point_radius = 3

    def __init__(self, vertexes, color=WHITE):
        self.vertexes = [Vector3(vertex) for vertex in vertexes]
        if self.vertexes:
            pos = get_center_points(self.vertexes)
        else:
            pos = Vector3.zero()
        super(Points, self).__init__(pos)
        self.color = color

    def draw(self, surface, lst_pos2d_light):
        for pos2d_light in lst_pos2d_light:
            if pos2d_light:
                pg.draw.circle(surface, get_color_of_light(self.color, pos2d_light[1]), pos2d_light[0],
                               radius=self.point_radius, width=2)


class PolygonLines(Points):
    def __init__(self, vertexes, closed=True, color=WHITE, fill=False):
        super(PolygonLines, self).__init__(vertexes, color)
        self.closed = closed
        self.fill = fill

    def draw(self, surface, lst_pos2d_light):
        if self.fill and all(lst_pos2d_light):
            draw_poligon(surface, get_color_of_light(self.color, lst_pos2d_light[0][1]),
                         lst_pos2d_light[0][0], lst_pos2d_light[1][0],
                         lst_pos2d_light[2][0], lst_pos2d_light[3][0],
                         )
            # pg.draw.polygon(surface, get_color_of_light(self.color, lst_pos2d_light[0][1]),
            #                 list(map(lambda x: x[0], lst_pos2d_light)))
        else:
            first = None
            last = None
            for i in range(1, len(lst_pos2d_light)):
                if lst_pos2d_light[i - 1] and lst_pos2d_light[i]:
                    pg.draw.line(surface, get_color_of_light(self.color, lst_pos2d_light[i][1]),
                                 lst_pos2d_light[i - 1][0], lst_pos2d_light[i][0], width=2)
                    if self.closed:
                        if first is None:
                            first = lst_pos2d_light[i - 1]
                        last = lst_pos2d_light[i][0]
            if self.closed and first and last:
                pg.draw.line(surface, get_color_of_light(self.color, first[1]),
                             first[0], last, width=2)


class WallFill(PolygonLines):
    def __init__(self, position_1, position_2, height, color=WHITE):
        super(WallFill, self).__init__([
            position_1, position_2, position_2 + Vector3(0, 0, height),
                                    position_1 + Vector3(0, 0, height),
        ], color=color, closed=True, fill=True)


class FloorFill(WallFill):
    def __init__(self, position, size, color=WHITE, fill=True):
        super(WallFill, self).__init__([
            position, position + Vector3(size[0], 0, 0), position + Vector3(size[0], size[0], 0),
                      position + Vector3(0, size[1], 0),
        ], color=color, closed=True, fill=fill)


class Line(Points):
    width = 3

    def __init__(self, position_1: Vector3, position_2: Vector3, color=WHITE):
        super(Line, self).__init__([position_1, position_2], color)

    def draw(self, surface, lst_pos2d_light):
        # print(light)
        if all(lst_pos2d_light):
            pg.draw.line(surface, get_color_of_light(self.color, lst_pos2d_light[0][1]),
                         lst_pos2d_light[0][0], lst_pos2d_light[1][0], width=self.width)


class _Line(Object):
    width = 3

    def __init__(self, position_1: Vector3, position_2: Vector3, color=WHITE):
        super(_Line, self).__init__((position_1 + position_2) / 2)
        self.position_1 = position_1
        self.position_2 = position_2
        self.color = color

    def draw(self, surface, pos2d_1, pos2d_2, light=1):
        # print(light)
        pg.draw.line(surface, get_color_of_light(self.color, light), pos2d_1, pos2d_2, width=self.width)


class SystemCoord(ObjectGroup):
    def __init__(self, position, size: int):
        self.color = YELLOW
        super(SystemCoord, self).__init__([
            Line(position - Vector3(size, 0, 0), Vector3(size, 0, 0), GREEN),
            Line(position - Vector3(0, size, 0), Vector3(0, size, 0), RED),
            Line(position - Vector3(0, 0, size), Vector3(0, 0, size), BLUE),
            Point(position, self.color),

        ])


class Wall(ObjectGroup):
    def __init__(self, position_1, position_2, height, color=WHITE):
        super(Wall, self).__init__([
            Line(position_1, position_2, color),
            Line(position_1 + Vector3(0, 0, height), position_2 + Vector3(0, 0, height), color),
            Line(position_1, position_1 + Vector3(0, 0, height), color),
            Line(position_2, position_2 + Vector3(0, 0, height), color),
            Line(position_1, position_2 + Vector3(0, 0, height), color),
            Line(position_1 + Vector3(0, 0, height), position_2, color),
        ])


class WallCube(ObjectGroup):
    def __init__(self, position, width, height, color=WHITE):
        half_w = width / 2
        super(WallCube, self).__init__([
            WallFill(position + Vector3(-half_w, half_w, 0), position + Vector3(half_w, half_w, 0), height, color),
            WallFill(position + Vector3(-half_w, -half_w, 0), position + Vector3(half_w, -half_w, 0), height, color),
            WallFill(position + Vector3(-half_w, half_w, 0), position + Vector3(-half_w, -half_w, 0), height, color),
            WallFill(position + Vector3(half_w, half_w, 0), position + Vector3(half_w, -half_w, 0), height, color),
            FloorFill(position + Vector3(-half_w, -half_w, height), (width, width), color=color, fill=True),
            Point(position, color)
        ])


class PointsRotate(Points):
    def __init__(self, vertexes, rotation, color=WHITE):
        super(PointsRotate, self).__init__(vertexes, color)
        self.rotation = rotation

    def get_rotate_points(self):
        rot_points = []
        for point in self.vertexes:
            vec_point = point - self.position
            vec_point.rotate_x_rad_ip(self.rotation.x)
            vec_point.rotate_y_rad_ip(self.rotation.y)
            vec_point.rotate_z_rad_ip(self.rotation.z)
            rot_point = self.position + vec_point
            rot_points.append(rot_point)
        # print(self.rotation, rot_point)
        return rot_points


class SkeletonRotate(PointsRotate):
    def __init__(self, vertexes, edges, rotation, color=WHITE):
        self.edges = edges
        super(SkeletonRotate, self).__init__(vertexes, rotation, color)
        
    def draw(self, surface, lst_pos2d_light):
        i = 0
        for edge in self.edges:
            pos2d_light_1, pos2d_light_2 = lst_pos2d_light[edge[0]], lst_pos2d_light[edge[1]]
            color = self.color
            if pos2d_light_1 and pos2d_light_2:
                pg.draw.line(surface, get_color_of_light(color, pos2d_light_1[1]), pos2d_light_1[0],
                             pos2d_light_2[0],
                             width=2)


class WallCubeRotate(SkeletonRotate):
    def __init__(self, position, rotation, size, color=WHITE, rgb_lines=False):
        sx, sy, sz = size
        hx, hy, hz = size[0] // 2, size[1] // 2, size[2] // 2
        add_points = [Vector3(-hx, -hy, hz), Vector3(hx, -hy, hz), Vector3(hx, -hy, -hz), Vector3(-hx, -hy, -hz),
                      Vector3(-hx, hy, hz), Vector3(hx, hy, hz), Vector3(hx, hy, -hz), Vector3(-hx, hy, -hz), ]
        points = [position + add_point for add_point in add_points]
        edges = [(0, 1), (1, 2), (2, 3), (3, 0),
                      (4, 5), (5, 6), (6, 7), (7, 4),
                      (0, 4), (1, 5), (2, 6), (3, 7)]
        super(WallCubeRotate, self).__init__(points, edges, rotation, color)
        self.rgb_lines = rgb_lines

    def draw(self, surface, lst_pos2d_light):
        i = 0
        for edge in self.edges:
            pos2d_light_1, pos2d_light_2 = lst_pos2d_light[edge[0]], lst_pos2d_light[edge[1]]
            color = self.color
            if self.rgb_lines:
                if i in (0, 2, 4, 6):
                    color = GREEN  # x
                elif i in (1, 3, 5, 7):
                    color = BLUE  # z
                elif i in (8, 9, 10, 11):
                    color = RED  # y
            if pos2d_light_1 and pos2d_light_2:
                pg.draw.line(surface, get_color_of_light(color, pos2d_light_1[1]), pos2d_light_1[0],
                             pos2d_light_2[0],
                             width=2)
            i += 1
        # print(pos2d_light_1, pos2d_light_2)


class Camera:
    fov_angle = 3.14159 / 3

    # fov_angle = 120

    def __init__(self, player, size):
        self.player = player
        self.size = size
        self.w, self.h = self.size
        self.half_w, self.half_h = self.w // 2, self.h // 2
        self.focal_length = self.half_w / math.tan(self.fov_angle / 2)
        self.lst_render_objects = []
        self.world_transform_calculated = False

        debug("focal_length", self.focal_length)

    def render(self, surface):
        if not self.player.camera_pos_calculated or 1:
            w = self.player.world
            self.lst_render_objects = []
            for obj in w.objects:
                if obj is not self.player:
                    self.render_object(surface, obj)
            self.lst_render_objects.sort(key=lambda x: x[1], reverse=True)
            self.player.camera_pos_calculated = True
        self.draw_sky(surface)
        for f in self.lst_render_objects:
            f[0]()

    def render_object(self, surface, obj):
        if isinstance(obj, ObjectGroup):
            for child in obj.objects:
                self.render_object(surface, child)
        elif isinstance(obj, PointsRotate):
            points = obj.get_rotate_points()
            lst_pos2d_light = [self.convert_to_2d(self.player.position, pos, get_light=True)
                               for pos in points]
            dist = self.player.position.distance_squared_to(obj.position)
            self.lst_render_objects.append((
                                           lambda lst_pos2d_light=lst_pos2d_light, dist=dist, surface=surface: obj.draw(
                                               surface, lst_pos2d_light), dist))
        elif isinstance(obj, Points):
            lst_pos2d_light = [self.convert_to_2d(self.player.position, pos, get_light=True) for pos in obj.vertexes]
            dist = self.player.position.distance_squared_to(obj.position)
            self.lst_render_objects.append((lambda: obj.draw(surface, lst_pos2d_light), dist))
        elif isinstance(obj, Point):
            res_pos_light = self.convert_to_2d(self.player.position, obj.position, get_light=True)
            if res_pos_light:
                dist = self.player.position.distance_squared_to(obj.position)
                self.lst_render_objects.append((lambda: obj.draw(surface, res_pos_light[0], res_pos_light[1]), dist))

    def convert_to_2d(self, my_pos: Vector3, obj_pos: Vector3, get_light=False):
        # obj_pos = obj_pos.rotate_z_rad(self.player.rotation.z)
        angle_z = self.player.rotation.z
        vec_to = (obj_pos - my_pos)
        vec_to.rotate_z_rad_ip(angle_z)
        vec_to.rotate_x_rad_ip(self.player.rotation.x)
        dist_y = vec_to.y
        # print(dist_y, self.focal_length)
        if dist_y <= 0:
            return

        x = self.focal_length * vec_to.x / dist_y + self.half_w
        y = self.half_h - self.focal_length * vec_to.z / dist_y
        if not WINDOW_RECT.collidepoint(x, y):
            return
        if get_light:
            light_dist = 800
            light = (light_dist - min(light_dist, dist_y)) / light_dist
            return (x, y), light
        return x, y

    def draw_sky(self, surface):
        y = self.half_h - math.tan(self.player.rotation.x) * self.focal_length
        # if y < 0:
        #     surface.fill()
        if y > self.h:
            surface.fill(color_sky)
        else:
            pg.draw.rect(surface, color_sky, (0, 0, self.w, y))
            # pg.draw.rect(surface, color_sky, (0, 0, self.w, y))


class World:
    def __init__(self, objects: list = []):
        self.objects = objects

    def add_object(self, obj):
        self.objects.append(obj)


class Player(Object):
    def __init__(self, position: Vector3, rotation: Angle3 = Angle3.zero(), mouse_control=False):
        super(Player, self).__init__(position, rotation)
        self.world: World = None
        self.speed = 0.5
        self.rot_speed = 0.001
        self.color = GREEN
        self.camera_pos_calculated = False
        self.mouse_control = mouse_control

    def set_world(self, p_world):
        self.world = p_world
        self.world.add_object(self)

    def update(self, elapsed_time):
        self.control_keys(elapsed_time)
        self.control_mouse(elapsed_time)

    def control_keys(self, elapsed_time):
        keys = pg.key.get_pressed()
        speed = self.speed * elapsed_time
        rot_speed = self.rot_speed * elapsed_time
        if keys[pg.K_q] or keys[pg.K_e] or keys[pg.K_LEFT] or keys[pg.K_RIGHT] or keys[pg.K_UP] or keys[pg.K_DOWN] or \
                keys[pg.K_w] or keys[pg.K_s] or keys[pg.K_a] or keys[pg.K_d]:
            self.camera_pos_calculated = False
        if keys[pg.K_q]:
            self.position.z -= speed
        if keys[pg.K_e]:
            self.position.z += speed
        if keys[pg.K_LEFT]:
            self.rotation.z -= rot_speed
        elif keys[pg.K_RIGHT]:
            self.rotation.z += rot_speed
        if keys[pg.K_UP]:
            self.rotation.x += rot_speed
        elif keys[pg.K_DOWN]:
            self.rotation.x -= rot_speed
        self.rotation.x = max(-1.45, min(1.45, self.rotation.x))
        vec_speed = Vector3(0, 0, 0)
        if keys[pg.K_w]:
            vec_speed = Vector3(math.sin(self.rotation.z), math.cos(self.rotation.z), 0)
        elif keys[pg.K_s]:
            vec_speed = Vector3(-math.sin(self.rotation.z), -math.cos(self.rotation.z), 0)
        if keys[pg.K_a]:
            vec_speed += Vector3(-math.cos(self.rotation.z), math.sin(self.rotation.z), 0)
        elif keys[pg.K_d]:
            vec_speed += Vector3(math.cos(self.rotation.z), -math.sin(self.rotation.z), 0)
        self.position += vec_speed * speed

    def control_mouse(self, elapsed_time):
        if pg.mouse.get_focused() and self.mouse_control:
            mouse_pos = pg.mouse.get_pos()
            new_mouse_pos = W_WIDTH // 2, W_HEIGHT // 2
            pg.draw.line(screen, RED, new_mouse_pos, mouse_pos)
            pg.mouse.set_pos(new_mouse_pos)
            rz = (mouse_pos[0] - new_mouse_pos[0]) / 100 * elapsed_time * MOUSE_SENSITIVITY
            rx = (mouse_pos[1] - new_mouse_pos[1]) / 100 * elapsed_time * MOUSE_SENSITIVITY
            # print(mouse_pos, rz, rx)
            if rz != 0 or rx != 0:
                self.camera_pos_calculated = False

            self.rotation.z += rz
            self.rotation.x += rx
            self.rotation.x = max(-1.45, min(1.45, self.rotation.x))


class MiniMap:
    def __init__(self, rect, scale, player):
        self.rect = pg.Rect(rect)
        self.size = self.rect.size
        self.half_width, self.half_height = self.rect.w // 2, self.rect.h // 2
        self.half_size_vector = pg.Vector2(self.half_width, self.half_height)
        self.scale = scale
        self.player = player
        self.surface = pg.Surface(self.rect.size)

    def draw(self, surface):
        self.surface.fill("#AAAAAA")
        p_pos = pg.Vector2(self.player.position.xy)
        for obj in self.player.world.objects:
            pos = (pg.Vector2(obj.position.xy) - p_pos) / self.scale
            # print(obj, p_pos, obj.position, (pg.Vector2(obj.position.xy) - p_pos))
            pg.draw.circle(self.surface, obj.color, (pos.x + self.half_width, self.half_height - pos.y), radius=1)
        pos_2 = self.half_width + math.sin(self.player.rotation.z) * 25, \
                self.half_height - math.cos(self.player.rotation.z) * 25
        pg.draw.line(self.surface, GREEN, self.half_size_vector, pos_2)
        surface.blit(self.surface, self.rect)


def main():
    cnt = 20
    lst = [WallCube(Vector3(randint(-4, 4) * 50, randint(-4, 4) * 50, 0), 50, 100) for i in range(cnt)]
    # polygon = PolygonLines(list(map(lambda x: x.position, lst)))
    # cube = WallCubeRotate(Vector3(0, 0, 0), Angle3(math.pi / 4, math.pi / 4, math.pi / 4), (50, 30, 10), rgb_lines=True)
    sceleton = SkeletonRotate(*open_file_obj("monkey1.obj", 7, _convert_faces_to_lines=True), rotation=Angle3(math.pi / 2, 0, 0))
    world = World([SystemCoord(Vector3(0, 0, 0), 0), sceleton])
    player = Player(Vector3(-00, -32, 2), rotation=Angle3(0.0, 0, 0), mouse_control=False)
    player.set_world(world)

    camera = Camera(player, WINDOW_SIZE)
    mini_map = MiniMap((0, 200, 100, 100), 20, player)
    rotating = False
    running = True
    while running:
        elapsed_time = clock.tick(FPS)

        screen.fill("#000000")
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                rotating = not rotating


        camera.render(screen)
        player.update(elapsed_time)
        # mini_map.draw(screen)
        screen.blit(font.render(f"{int(clock.get_fps())}fps", False, "#00FF00"), (5, 5))
        screen.blit(font.render(str(player.position), False, "#00FF00"), (5, 25))
        screen.blit(font.render(str(player.rotation), False, "#00FF00"), (5, 45))
        pg.display.flip()
        if rotating:
            sceleton.rotation.x += math.pi / 400
            # sceleton.rotation.y -= math.pi / 300
            sceleton.rotation.z += math.pi / 400


if __name__ == '__main__':
    main()
