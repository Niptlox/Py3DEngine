import math

from numba import njit
import pygame as pg

from settings import *


@njit(fastmath=True)
# Алгоритм DDA-линии https://grafika.me/node/63
def get_horizontal_pixels_of_line_dda(pos_1, pos_2, scale=2):
    lx = abs(pos_1[0] - pos_2[0])
    ly = abs(pos_1[1] - pos_2[1])
    length = max(lx, ly)
    if length == 0:
        return [pos_1]
    dx = (pos_2[0] - pos_1[0]) / length * scale
    dy = (pos_2[1] - pos_1[1]) / length * scale
    lst = []
    x, y = pos_1
    while length >= 0:
        lst.append((x, y))
        x += dx
        y += dy
        length -= scale
    return lst


@njit(fastmath=True)
# Алгоритм DDA-линии https://grafika.me/node/63
def get_line_dda(pos_1, pos_2, scale=2):
    lx = abs(pos_1[0] - pos_2[0])
    ly = abs(pos_1[1] - pos_2[1])
    length = max(lx, ly)
    if length == 0:
        return [pos_1]
    dx = (pos_2[0] - pos_1[0]) / length * scale
    dy = (pos_2[1] - pos_1[1]) / length * scale
    lst = []
    x, y = pos_1
    while length >= 0:
        lst.append((x, y))
        x += dx
        y += dy
        length -= scale
    return lst


@njit(fastmath=True)
def get_line_fill_poligon(pos11, pos12, pos21, pos22, scale=2):
    points_1 = get_line_dda(pos11, pos12, scale=scale)
    points_2 = get_line_dda(pos21, pos22, scale=scale)
    len_1 = len(points_1)
    len_2 = len(points_2)
    if len_1 > len_2:
        points_1, points_2 = points_2, points_1
        len_1, len_2 = len_2, len_1
        pos12 = pos22
    points = []
    for i in range(len_1):
        points.append(points_1[i])
        points.append(points_2[i])
    for i in range(len_1, len_2):
        points.append(pos12)
        points.append(points_2[i])

    return points


def draw_poligon(surface, color, pos11, pos12, pos21, pos22):
    w = 3
    points = get_line_fill_poligon(pos11, pos12, pos22, pos21, scale=w)
    pg.draw.lines(surface, color, False, points, width=w + 1)


def convert_to_2d(self, my_pos, obj_pos, get_light=False):
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


