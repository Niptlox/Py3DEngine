from src.Texture import *

DARK = "#27272A"
DEF_COLOR_SCHEME_BUT = ((WHITE, GRAY, DARK), (BLACK, BLACK, WHITE))


def openImagesButton(nameImg: str, colorkey=COLORKEY):
    path, extension = os.path.splitext(nameImg)
    imgUp = load_image(path + "_up" + extension, colorkey)
    imgIn = load_image(path + "_in" + extension, colorkey)
    imgDown = load_image(path + "_down" + extension, colorkey)
    return imgUp, imgIn, imgDown


def createImageButton(size, text="", bg=BLACK, font=TEXTFONT_BTN, text_color=WHITE, colorkey=COLORKEY):
    surf = get_texture_size(bg, size, colorkey=colorkey)

    texframe = font.render(text, True, text_color)
    texframe_rect = pygame.Rect((0, 0), texframe.get_size())
    # print("texframe_rect.center", texframe_rect, size)
    texframe_rect.center = size[0] // 2, size[1] // 2
    surf.blit(texframe, texframe_rect)
    return surf


def createImagesButton(size, text="", color_schema=DEF_COLOR_SCHEME_BUT, font=TEXTFONT_BTN, colorkey=COLORKEY):
    # print("color_schema", [(bg, colort) for bg, colort in zip(color_schema[0], color_schema[1])])
    imgs_but = [createImageButton(size, text, bg, font=font, text_color=colort, colorkey=colorkey)
                for bg, colort in zip(color_schema[0], color_schema[1])]
    return imgs_but


def createVSteckButtons(size, center_x, start_y, step, images_buttons, funcs, screen_position=(0, 0)):
    y = start_y
    x = center_x - size[0] // 2
    step += size[1]
    buts = []
    for images_button, func in zip(images_buttons, funcs):
        but = Button(func, ((x, y), size), *images_button, screenXY=(screen_position[0] + x, screen_position[1] + y))
        y += step
        buts.append(but)
    return buts


def createHSteckButtons(size, start_x, center_y, step, images_buttons, funcs, screen_position=(0, 0)):
    y = center_y - size[1] // 2
    x = start_x
    step += size[0]
    buts = []
    for images_button, func in zip(images_buttons, funcs):
        but = Button(func, ((x, y), size), *images_button, screenXY=(screen_position[0] + x, screen_position[1] + y))
        x += step
        buts.append(but)
    return buts


class Button(pygame.sprite.Sprite):
    def __init__(self, func, rect, imgUpB, imgInB=None, imgDownB=None, group=None, screenXY=None, disabled=False):
        """func, rect, imgUpB, imgInB=None, imgDownB=None, group=None, screenXY=None, disabled=False
        вызов func(button) - по пораметру передаёться кнопка"""
        # если рамеры == -1 то берётся размер кнопки
        self.func = func
        if group is not None:
            super().__init__(group)
        else:
            super().__init__()
        self.rect = rect = pygame.Rect(rect)
        xy = self.rect.x, self.rect.y
        if self.rect.w == -1 and self.rect.h == -1:
            size = None
        else:
            size = rect.size
        self.imgUpB = get_texture(imgUpB, colorkey=COLORKEY)
        self.image = self.imgUpB
        imgDownB = self.imgUpB if imgDownB is None else imgDownB
        imgInB = imgDownB if imgInB is None else imgInB
        self.imgDownB = get_texture(imgDownB, colorkey=COLORKEY)
        self.imgInB = get_texture(imgInB, colorkey=COLORKEY)
        self.disabled = disabled
        self.mauseInButton = False
        self.mauseDownButton = False
        if size is None:
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = xy
        else:
            self.rect = pygame.Rect(xy, size)
            self.imgUpB = pygame.transform.scale(self.imgUpB, self.rect.size)
            self.imgDownB = pygame.transform.scale(self.imgDownB, self.rect.size)
            self.imgInB = pygame.transform.scale(self.imgInB, self.rect.size)
        if not disabled:
            self.image = self.imgUpB
        else:
            self.image = self.imgDownB
        self.screenRect = self.rect if screenXY is None else pygame.Rect(screenXY, self.rect.size)
        # self.screenXY = screenXY

    def setXY(self, xy):
        x, y = xy
        ax, ay = x - self.rect.x, y - self.rect.y
        self.rect.move_ip(*xy)
        if self.rect is not self.screenRect:
            sx, sy = self.screenRect.x + ax, self.screenRect.y + ay
            self.screenRect.move_ip(sx, sy)

    def pg_event(self, event):
        if self.disabled:
            return
        but = 1
        if event.type == pygame.MOUSEBUTTONUP and event.button == but:
            if self.mauseDownButton:
                self.click()
            self.mauseDownButton = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == but:
            if self.screenRect.collidepoint(event.pos):
                self.mauseInButton = True
                self.mauseDownButton = True
        if event.type == pygame.MOUSEMOTION:
            if self.mauseInButton:
                if not self.screenRect.collidepoint(event.pos):
                    self.mauseInButton = False
                    self.mauseDownButton = False
            else:
                if self.screenRect.collidepoint(event.pos):
                    self.mauseInButton = True
        self.redraw()

    def update(self, *args) -> None:
        if args:
            event = args[0]
            self.pg_event(event)

    def click(self):
        if self.func:
            self.mauseInButton = False
            self.mauseDownButton = False
            self.redraw()
            self.func(self)
        else:
            print("Button down, but function not defined!!!")

    def inButton(self):
        if self.imgInB:
            self.image = self.imgInB

    def redraw(self):
        """update my image (not draw)"""
        if self.disabled:
            self.image = self.imgDownB
        elif self.mauseDownButton:
            self.image = self.imgDownB
        elif self.mauseInButton:
            self.image = self.imgInB
        else:
            self.image = self.imgUpB

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def set_disabled(self, dsb):
        self.disabled = dsb
        self.redraw()
