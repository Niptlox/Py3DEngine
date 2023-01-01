import os
import sys

import pygame

printD = lambda *st, sep=" ", end="\n": print("DEBAG:", *st, sep=sep, end=end)

pygame.init()
pygame.font.init()

GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = pygame.color.Color("gray")

COLORKEY = GREEN

TEXTFONT = pygame.font.SysFont('Roboto', 32)
TEXTFONT_BTN = pygame.font.SysFont('Roboto', 40)
FPSFONT = pygame.font.SysFont('Roboto', 15)



def isColor(arg):
    if type(arg) is pygame.Color or (type(arg) in (tuple, list) and 3 <= len(arg) <= 4):
        return True
    return False


def vertical_gradient(size, startcolor, endcolor):
    """
    Draws a vertical linear gradient filling the entire surface. Returns a
    surface filled with the gradient (numeric is only 2-3 times faster).
    """
    height = size[1]
    bigSurf = pygame.Surface((1, height)).convert_alpha()
    dd = 1.0 / height
    sr, sg, sb, sa = startcolor
    er, eg, eb, ea = endcolor
    rm = (er - sr) * dd
    gm = (eg - sg) * dd
    bm = (eb - sb) * dd
    am = (ea - sa) * dd
    for y in range(height):
        bigSurf.set_at((0, y),
                       (int(sr + rm * y),
                        int(sg + gm * y),
                        int(sb + bm * y),
                        int(sa + am * y))
                       )
    return pygame.transform.scale(bigSurf, size)


def get_texture(texture, colorkey=None):
    if texture is None:
        return None
    if type(texture) is str and texture[0] != "#":
        return load_image(texture, colorkey)
    # if type(texture) is pygame.Color:
    #     return
    return texture


def get_texture_size(texture, size=None, colorkey=None):
    if texture is None:
        return None
    if type(texture) is str and texture[0] != "#":
        image = load_image(texture, colorkey)
        if size is not None:
            image = pygame.transform.scale(image, size)
            # image = image.convert_alpha()
        return image
    if type(texture) is not pygame.Surface and size is not None:
        surf = pygame.Surface(size)
        surf.fill(texture)
        texture = surf
    return texture


def load_image(name, colorkey=None):
    fullname = name  # os.path.join('data', name)
    # если файл не существует, то выходим
    # fullname = r"BetaIMG.png"
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        return None
        # sys.exit()

    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    # else:
    #   image = image.convert_alpha()
    return image


def load_animation(path, frame_durations, size=None, colorkey=COLORKEY):
    animation_name = path.split('/')[-1].split('\\')[-1]
    animation_frames = []
    n = 0
    # print("load_animation", path, animation_name)
    for count_frame in frame_durations:
        # animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '_' + str(n) + '.png'
        # player_animations/idle/idle_0.png
        animation_image = get_texture_size(img_loc, colorkey=colorkey, size=size)
        for i in range(count_frame):
            animation_frames.append(animation_image)
        n += 1
    return animation_frames


def rot_center(image, angle, x, y):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)

    return rotated_image, new_rect