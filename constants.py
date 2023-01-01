import math

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
