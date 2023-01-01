import pygame as pg


def draw_point(camera, color, position2, r=2):
    pg.draw.circle(camera.surface, color, position2, r)


def draw_line(camera, color, position_1, position_2):
    pg.draw.line(camera.surface, color, position_1, position_2, 1)


def draw_polygon(camera, color, positions):
    pg.draw.polygon(camera.surface, color, positions)
