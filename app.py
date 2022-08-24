from logging import debug
from random import randint
from typing import List
import pygame as pg
import math

from settings import *
from Drawing import *

WINDOW_RECT = pg.Rect((-W_WIDTH, -W_HEIGHT), (W_WIDTH * 3, W_HEIGHT * 3))

pg.init()
pg.mouse.set_visible(False)
font = pg.font.SysFont("", 20)

screen = pg.display.set_mode(WINDOW_SIZE)
clock = pg.time.Clock()


def get_color_of_light(color, light):
    return min(255, color[0] * light), min(255, color[1] * light), min(255, color[2] * light)


def get_center_points(positions):
    return sum(positions, Vector3.zero()) / len(positions)


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
        self.position = position
        self.rotation = rotation
        self.color = WHITE


class ObjectGroup(Object):
    def __init__(self, objects: List[Object]):
        if objects:
            pos = get_center_points(list(map(lambda x: x.position, objects)))
        else:
            pos = Vector3.zero()
        super(ObjectGroup, self).__init__(pos)
        self.objects = objects


class Point(Object):
    radius = 3

    def __init__(self, position, color=WHITE):
        super(Point, self).__init__(position)
        self.color = color

    def draw(self, surface, pos2d, light=1):
        pg.draw.circle(surface, get_color_of_light(self.color, light), pos2d, radius=self.radius, width=2)


class Points(Object):
    point_radius = 3

    def __init__(self, positions, color=WHITE):
        if positions:
            pos = get_center_points(positions)
        else:
            pos = Vector3.zero()
        super(Points, self).__init__(pos)
        self.positions = positions
        self.color = color

    def draw(self, surface, lst_pos2d_light):
        for pos2d_light in lst_pos2d_light:
            if pos2d_light:
                pg.draw.circle(surface, get_color_of_light(self.color, pos2d_light[1]), pos2d_light[0],
                               radius=self.point_radius, width=2)


class PolygonLines(Points):
    def __init__(self, positions, closed=True, color=WHITE):
        super(PolygonLines, self).__init__(positions, color)
        self.closed = closed

    def draw(self, surface, lst_pos2d_light):
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
        ], color=color, closed=True)

    def draw(self, surface, lst_pos2d_light):
        if all(lst_pos2d_light):
            draw_poligon(surface, get_color_of_light(self.color, lst_pos2d_light[0][1]),
                         lst_pos2d_light[0][0], lst_pos2d_light[1][0],
                         lst_pos2d_light[2][0], lst_pos2d_light[3][0],
                         )
            # pg.draw.polygon(surface, get_color_of_light(self.color, lst_pos2d_light[0][1]),
            #                 list(map(lambda x: x[0], lst_pos2d_light)))
        else:
            super(WallFill, self).draw(surface, lst_pos2d_light)


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
            Line(position, Vector3(size, 0, 0), GREEN),
            Line(position, Vector3(0, size, 0), RED),
            Line(position, Vector3(0, 0, size), BLUE),
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
    def __init__(self, position, wight, height, color=WHITE):
        half_w = wight / 2
        super(WallCube, self).__init__([
            WallFill(position + Vector3(-half_w, half_w, 0), position + Vector3(half_w, half_w, 0), height, color),
            WallFill(position + Vector3(-half_w, -half_w, 0), position + Vector3(half_w, -half_w, 0), height, color),
            WallFill(position + Vector3(-half_w, half_w, 0), position + Vector3(-half_w, -half_w, 0), height, color),
            WallFill(position + Vector3(half_w, half_w, 0), position + Vector3(half_w, -half_w, 0), height, color),
        ])


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

        debug("focal_length", self.focal_length)

    def render(self, surface):
        w = self.player.world
        self.lst_render_objects = []
        for obj in w.objects:
            if obj is not self.player:
                self.render_object(surface, obj)
        self.lst_render_objects.sort(key=lambda x: x[1], reverse=True)
        for f in self.lst_render_objects:
            f[0]()

    def render_object(self, surface, obj):
        if isinstance(obj, ObjectGroup):
            for child in obj.objects:
                self.render_object(surface, child)
        if isinstance(obj, Points):
            lst_pos2d_light = [self.convert_to_2d(self.player.position, pos, get_light=True) for pos in obj.positions]
            dist = self.player.position.distance_squared_to(obj.position)
            self.lst_render_objects.append((lambda: obj.draw(surface, lst_pos2d_light), dist))
        if isinstance(obj, Point):
            res_pos_light = self.convert_to_2d(self.player.position, obj.position, get_light=True)
            if res_pos_light:
                dist = self.player.position.distance_squared_to(obj.position)
                self.lst_render_objects.append((lambda: obj.draw(surface, res_pos_light[0], res_pos_light[1]), dist))

    def convert_to_2d(self, my_pos: Vector3, obj_pos: Vector3, get_light=False):
        # obj_pos = obj_pos.rotate_z_rad(self.player.rotation.z)
        angle_z = self.player.rotation.z
        vec_to = (obj_pos - my_pos)
        vec_to.rotate_z_ip_rad(angle_z)
        vec_to.rotate_x_ip_rad(self.player.rotation.x)
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


class World:
    def __init__(self, objects: list = []):
        self.objects = objects

    def add_object(self, obj):
        self.objects.append(obj)


class Player(Object):
    def __init__(self, position: Vector3, rotation: Angle3 = Angle3.zero()):
        super(Player, self).__init__(position, rotation)
        self.world: World = None
        self.speed = 1
        self.rot_speed = math.pi / 100
        self.color = GREEN

    def set_world(self, p_world):
        self.world = p_world
        self.world.add_object(self)

    def update(self):
        self.control_keys()
        self.control_mouse()

    def control_keys(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_q]:
            self.position.z -= self.speed
        if keys[pg.K_e]:
            self.position.z += self.speed
        if keys[pg.K_LEFT]:
            self.rotation.z -= self.rot_speed
        elif keys[pg.K_RIGHT]:
            self.rotation.z += self.rot_speed
        vec_speed = Vector3(0, 0, 0)
        if keys[pg.K_w]:
            vec_speed = Vector3(math.sin(self.rotation.z), math.cos(self.rotation.z), 0) * self.speed
        elif keys[pg.K_s]:
            vec_speed = Vector3(-math.sin(self.rotation.z), -math.cos(self.rotation.z), 0) * self.speed
        if keys[pg.K_a]:
            vec_speed += Vector3(-math.cos(self.rotation.z), math.sin(self.rotation.z), 0) * self.speed
        elif keys[pg.K_d]:
            vec_speed += Vector3(math.cos(self.rotation.z), -math.sin(self.rotation.z), 0) * self.speed
        self.position += vec_speed

    def control_mouse(self):
        if pg.mouse.get_focused():
            mouse_pos = pg.mouse.get_pos()
            new_mouse_pos = W_WIDTH // 2, W_HEIGHT // 2
            pg.mouse.set_pos(new_mouse_pos)

            self.rotation.z += (mouse_pos[0] - new_mouse_pos[0]) / 100
            self.rotation.x += (mouse_pos[1] - new_mouse_pos[1]) / 100
            self.rotation.x = max(-1.6, min(1.6, self.rotation.x))


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


cnt = 20
lst = [WallCube(Vector3(randint(-4, 4) * 50, randint(-4, 4) * 50, -50), 50, 100) for i in range(cnt)]
# polygon = PolygonLines(list(map(lambda x: x.position, lst)))
world = World([SystemCoord(Vector3(0, 0, 0), 25),
               ] + lst)
player = Player(Vector3(-10, -500, 0))
player.set_world(world)

camera = Camera(player, WINDOW_SIZE)
mini_map = MiniMap((0, 200, 100, 100), 20, player)

running = True
while running:
    screen.fill("#000000")
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
    player.update()
    camera.render(screen)
    mini_map.draw(screen)
    screen.blit(font.render(f"{int(clock.get_fps())}fps", False, "#00FF00"), (5, 5))
    screen.blit(font.render(str(player.position), False, "#00FF00"), (5, 25))
    screen.blit(font.render(str(player.rotation), False, "#00FF00"), (5, 45))
    pg.display.flip()

    clock.tick()
