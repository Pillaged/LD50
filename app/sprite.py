import pygame
from app.libraries.pyganim import PygAnimation as pyganim


class Sprite(pygame.sprite.DirtySprite):
    dirty = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visible = True
        self._rotation = 0
        self._image = None
        self._original_image = None
        self._width = 0
        self._height = 0
        self._needs_rescale = False
        self._needs_update = False

    def draw(self, surface, rect=None):
        """ Draw the sprite to the surface

        This operation does not scale the sprite, so it may exceed
        the size of the area passed.

        :param surface: Surface to be drawn on
        :param rect: Area to contain the sprite
        :return: Area of the surface that was modified
        :rtype: pygame.rect.Rect
        """
        # should draw to surface without generating a cached copy
        if rect is None:
            rect = surface.get_rect()
        return self._draw(surface, rect)

    def _draw(self, surface, rect):
        return surface.blit(self._image, rect)

    @property
    def image(self):
        # should always be a cached copy
        if self._needs_update:
            self.update_image()
            self._needs_update = False
            self._needs_rescale = False
        return self._image

    @image.setter
    def image(self, image):
        if image is None:
            self._original_image = None
            return

        if hasattr(self, 'rect'):
            self.rect.size = image.get_size()
        else:
            self.rect = image.get_rect()
        self._original_image = image
        self._needs_update = True

    def update_image(self):
        if self._needs_rescale:
            w = self.rect.width if self._width is None else self._width
            h = self.rect.height if self._height is None else self._height
            image = pyganim.scale(self._original_image, (w, h))
            center = self.rect.center
            self.rect.size = w, h
            self.rect.center = center
        else:
            image = self._original_image

        if self._rotation:
            image = pyganim.rotozoom(image, self._rotation, 1)
            rect = image.get_rect(center=self.rect.center)
            self.rect.size = rect.size
            self.rect.center = rect.center

        self._width, self._height = self.rect.size
        self._image = image

    # width and height are API that may not stay
    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        width = int(round(width, 0))
        if not width == self._width:
            self._width = width
            self._needs_rescale = True
            self._needs_update = True

    # width and height are API that may not stay
    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        height = int(round(height, 0))
        if not height == self._height:
            self._height = height
            self._needs_rescale = True
            self._needs_update = True

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        value = int(round(value, 0)) % 360
        if not value == self._rotation:
            self._rotation = value
            self._needs_update = True
