import pygame as pg


class UI:
    def __init__(self, app) -> None:
        self.app = app
        self.screen = app.screen
        self.display = self.app.display
        self.rect = pg.Rect((0, 0), self.display.get_size())

    def _init_ui(self):
        pass

    def draw(self):
        self.screen.blit(self.display, (0, 0))
        pg.display.flip()

    def pg_event(self, event: pg.event.Event):
        pass

    @property
    def onscreenx(self):
        return self.rect.x + self.app.rect.x

    @property
    def onscreeny(self):
        return self.rect.y + self.app.rect.y


class GroupUI:
    def __init__(self, components):
        self.components = components

    def add(self, obj):
        self.components.append(obj)

    def add_lst(self, lst_objs):
        for obj in lst_objs:
            self.add(obj)

    def pg_event(self, event):
        for component in self.components:
            component.pg_event(event)

    def draw(self, surface):
        for component in self.components:
            component.draw(surface)


class SurfaceUI(pg.Surface):
    def __init__(self, rect, flags=0, surface=None):
        self.rect = pg.Rect(rect)
        super().__init__(self.rect.size, flags, surface)

    def set_surface(self, surface):
        if surface.get_size() != self.get_size():
            self.set_size(surface.get_size())
        self.blit(surface, (0, 0))

    def draw(self, surface):
        surface.blit(self, self.rect)

    def pg_event(self, event: pg.event.Event):
        pass

    def set_size(self, size):
        self.rect.size = size
        super().__init__(self.rect.size)

    def convert_alpha(self):
        super().__init__(self.rect.size, 0, super().convert_alpha())
        return self


SCROLL_VERTICAL = 1
SCROLL_HORIZONTAL = 2


class ScrollSurface(SurfaceUI):
    """Поле с прокруткой. Только для объектов с методом 'draw(surface)'"""

    def __init__(self, rect, scroll, background="black", single_step=15, scroll_type=SCROLL_VERTICAL,
                 bounds_checking=True):
        super().__init__(rect)
        self.convert_alpha()
        self.scroll_surface = SurfaceUI((scroll, self.rect.size))
        self.objects = []
        self.bounds_checking = bounds_checking
        self.background = background
        self.single_step = single_step
        self.scroll_type = scroll_type

    def mouse_scroll(self, dx, dy):
        self.scroll_surface.rect.x += dx
        self.scroll_surface.rect.y += dy
        # print("x", self.scroll_surface.rect.x, self.scroll_surface.rect.right, self.rect.w, self.scroll_surface.rect.w)
        if self.bounds_checking:
            if self.scroll_surface.rect.x > 0:
                self.scroll_surface.rect.x = 0
            if self.scroll_surface.rect.y > 0:
                self.scroll_surface.rect.y = 0
            if self.scroll_surface.rect.bottom < self.rect.h:
                self.scroll_surface.rect.bottom = self.rect.h
            if self.scroll_surface.rect.right < self.rect.w:
                self.scroll_surface.rect.right = self.rect.w

    def add_objects(self, objects):
        self.objects += objects
        for obj in objects:
            if obj.rect.right > self.rect.w:
                self.set_size((obj.rect.right + 5, self.rect.h))
            if obj.rect.bottom > self.rect.h:
                self.set_size((self.rect.w, obj.rect.bottom + 5))

    def draw(self, surface):
        self.scroll_surface.fill((0, 0, 0, 0))
        self.fill(self.background)
        for obj in self.objects:
            obj.draw(self.scroll_surface)
        self.blit(self.scroll_surface, self.scroll_surface.rect)
        surface.blit(self, self.rect)

    def pg_event(self, event: pg.event.Event):

        if event.type == pg.MOUSEBUTTONDOWN and event.button in (pg.BUTTON_WHEELDOWN, pg.BUTTON_WHEELUP):
            wheel_y = -1 if event.button == pg.BUTTON_WHEELDOWN else 1
            wheel_x = 0
            mouse_pos = tuple(event.pos)
            # if event.type == pg.MOUSEWHEEL:
            #     wheel_x, wheel_y = event.x, event.y
            #     mouse_pos = tuple(pg.mouse.get_pos())
            if self.rect.collidepoint(mouse_pos):
                if self.scroll_type & SCROLL_HORIZONTAL:
                    self.mouse_scroll(wheel_y * self.single_step, wheel_x * self.single_step)
                if self.scroll_type & SCROLL_VERTICAL:
                    self.mouse_scroll(wheel_x * self.single_step, wheel_y * self.single_step)
                return True
        if event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION):
            mouse_pos = tuple(event.pos)
            if self.rect.collidepoint(mouse_pos):
                event.pos = (mouse_pos[0] - self.scroll_surface.rect.x, mouse_pos[1] - self.scroll_surface.rect.y)
                for obj in self.objects:
                    obj.pg_event(event)
                event.pos = mouse_pos
                return True

    def scroll_to_bottom(self, vertical=True):
        if vertical:
            self.scroll_surface.rect.bottom = self.rect.h
        else:
            self.scroll_surface.rect.right = self.rect.w

    def scroll_to_top(self, vertical=True):
        if vertical:
            self.scroll_surface.rect.x = 0
        else:
            self.scroll_surface.rect.y = 0

    def set_size(self, size):
        self.scroll_surface.set_size(size)
        # if resize_rect:
        #     super(ScrollSurface, self).set_size(size)
