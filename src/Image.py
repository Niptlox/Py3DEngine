from src.common import *

BORDER_COLOR = "#1C1917"


def create_tile_image(color, bd=1, size=TILE_RECT, bd_color=BORDER_COLOR):
    img = pygame.Surface(size)
    img.fill(bd_color)
    pygame.draw.rect(img, color, ((bd, bd), (size[0] - bd * 2, size[0] - bd * 2)), border_radius=bd * 2)
    return img


def create_border(surface, bd=1, size=TILE_RECT, bd_color=BORDER_COLOR):
    pygame.draw.rect(surface, bd_color, ((0, 0), (size[0], size[1])), width=bd)
    return surface


COLORKEY = (0, 255, 0)


def load_imgs(path, count, size=TILE_RECT, colorkey=COLORKEY, alpha=None):
    return [load_img(path.format(i), size, colorkey, alpha) for i in range(count)]


def load_round_tool_imgs(path, count=4, colorkey=COLORKEY, alpha=None, rotate_imgs=True):
    cell_img = load_img(path.format(""), None, colorkey=colorkey)
    imgs = load_imgs(path, count, None, colorkey, alpha)
    if rotate_imgs:
        imgs = imgs + [pg.transform.rotate(im, -90 * i) for i in range(1, 4) for im in imgs]
    return cell_img, imgs
