import pygame as pg

# Colors =======

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Window settings ========
pg.init()
desktop_size = pg.display.get_desktop_sizes()[0]
print("desktop_size", desktop_size)
W_WIDTH, W_HEIGHT = 720, 480
W_WIDTH, W_HEIGHT = 1240, 720
HALF_W_WIDTH, HALF_W_HEIGHT = W_WIDTH // 2, W_HEIGHT // 2
# W_WIDTH, W_HEIGHT = desktop_size
WINDOW_SIZE = W_WIDTH, W_HEIGHT
WINDOW_RECT = pg.Rect((-W_WIDTH, -W_HEIGHT), (W_WIDTH * 3, W_HEIGHT * 3))

# App settings =======

FPS = 60
MOUSE_SENSITIVITY = 0.1

# CAMERA settings =====

color_floor = BLACK
color_sky = BLACK


