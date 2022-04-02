from contextlib import contextmanager
from itertools import groupby
from operator import itemgetter
import pygame
from pygame import Rect

class Renderer: 

    screen_center: tuple[int, int]
    view_rect: Rect 
    map_rect: Rect

    def __init__(self, screen_size:tuple[int, int], map_size: tuple[int, int]) -> None:
        self.view_rect = Rect(0, 0, screen_size[0], screen_size[1])
        self.map_rect = Rect(0, 0, map_size[0], map_size[1])
        self.screen_center = (screen_size[0]/2, screen_size[1])

    # surface is screen
    # rect is sub area of surface to draw on
    # to_draw is list of surfaces, screen positions, and z order to draw
    def draw(self, surface, rect, to_draw: list[tuple[pygame.Surface, tuple[float, float], int]]) -> None:
        with surface_clipping_context(surface, rect):
            self._clear_surface(surface, None)
            ox, oy = rect.left, rect.top

            def sprite_sort(i: tuple[pygame.Surface, tuple[float, float], int]):
                return i[2], i[1][1] + i[0].get_height()

            to_draw.sort(key=sprite_sort)
            for _, group in groupby(to_draw, itemgetter(2)):
                for i in group:   
                    x, y = i[1]         
                    surface.blit(i[0], (x - ox, y - oy))

    # sets the center of the screen
    def center(self, coords: tuple[int,int]):
        x, y = round(coords[0]), round(coords[1])
        self.view_rect.center = x, y

        # prevents camera from moving outside bounds
        self.view_rect.clamp_ip(self.map_rect)
        self.screen_center = self.view_rect.center

    
    def get_center_offset(self):    
        return (-self.view_rect.centerx + self._half_width,
                -self.view_rect.centery + self._half_height)
    
    def _clear_surface(self, surface :pygame.Surface, rect=None):
        surface.fill((0,0,0), rect)

@contextmanager
def surface_clipping_context(surface, clip):
    original = surface.get_clip()
    surface.set_clip(clip)
    yield
    surface.set_clip(original)