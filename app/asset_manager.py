import pygame
import logging

from pytmx import pytmx

import app.prepare as prepare
from pygame import mixer

logger = logging.getLogger(__name__)


def scale_surface(surface, factor):
    return pygame.transform.scale(
        surface, [int(i * factor) for i in surface.get_size()]
    )


def load_and_scale(filename):
    return scale_surface(load_image(filename), prepare.SCALE)


def transform_resource_filename(*filename):
    """ Appends the resource folder name to a filename
    :param filename: String
    :rtype: basestring
    """
    return prepare.fetch(*filename)


def load_image(filename):
    """ Load image from the resources folder
    """
    filename = transform_resource_filename(filename)
    return pygame.image.load(filename)


class DummySound:
    def play(self):
        pass


def load_audio(filename):
    """ Load sound from the resources folder
    """
    filename = transform_resource_filename(filename)
    try:
        return mixer.Sound(filename)
    except pygame.error as e:
        logger.error(e)
        logger.error('Unable to load sound: {}'.format(filename))
        return DummySound()


def load_tile_map(filename):
    """ Load tilemap from the resources folder
    """
    filename = transform_resource_filename(filename)
    data = pytmx.TiledMap(filename, pixelalpha=True)
    return data
