import logging
from collections import Iterable
from itertools import product

import pygame
from pygame import Rect
from pytmx import pytmx
from pytmx.util_pygame import handle_transformation, smart_convert

from app import prepare, asset_manager
from app.entity.controllable_ant import ControllableAnt
from app.game import GameMap
from app.input_manager import Button

logger = logging.getLogger(__name__)


def round_to_divisible(x, base=16):
    return int(base * round(float(x) / base))


def snap_point(point, grid_size):
    return (round_to_divisible(point[0], grid_size[0]),
            round_to_divisible(point[1], grid_size[1]))


def snap_rect(rect, grid_size):
    left, top = snap_point(rect.topleft, grid_size)
    right, bottom = snap_point(rect.bottomright, grid_size)
    return Rect((left, top), (right - left, bottom - top))


def tiles_inside_rect(rect, grid_size):
    for y, x in product(
            range(rect.top, rect.bottom, grid_size[1]),
            range(rect.left, rect.right, grid_size[0]),
    ):
        yield x // grid_size[0], y // grid_size[1]


class TMXMapLoader:
    """ Maps are loaded from standard tmx files created from a map editor like Tiled.
    **Tiled:** http://www.mapeditor.org/
    """

    def load(self, filename):
        data = pytmx.TiledMap(
            filename, image_loader=scaled_image_loader, pixelalpha=True
        )
        tile_size = (data.tilewidth, data.tileheight)
        data.tilewidth, data.tileheight = prepare.TILE_SIZE
        edges = data.properties.get("edges")
        collision_map = dict()
        entities = list()

        for obj in data.objects:
            if obj.type and obj.type.lower().startswith("collision"):
                closed = getattr(obj, "closed", True)
                if closed:
                    for tile_position, conds in self.region_tiles(obj, tile_size):
                        collision_map[tile_position] = conds if conds else None
            elif obj.type == "entity":
                e = self.load_entity(obj, tile_size)
                if e:
                    if isinstance(e, Iterable):
                        entities.extend(e)
                    else:
                        entities.append(e)

            elif obj.type == "tile_entity":
                closed = getattr(obj, "closed", True)
                if closed:
                    for i, (tile_position, _) in enumerate(self.region_tiles(obj, tile_size)):
                        e = self.load_entity(obj, tile_size, i)
                        if e:
                            if isinstance(e, Iterable):
                                [x.set_position(tile_position) for x in e]
                                entities.extend(e)
                            else:
                                e.set_position(tile_position)
                                entities.append(e)

        return GameMap(
            collision_map, entities, edges, data, filename,
        )

    @staticmethod
    def region_tiles(region, grid_size):
        """ Converts rectangular region to individual
        tiles and returns any region tags with tile.
        :param region:
        :param grid_size:
        :return:
        """
        # TODO apply region tags
        rect = snap_rect(
            Rect(region.x, region.y, region.width, region.height), grid_size
        )
        for tile_position in tiles_inside_rect(rect, grid_size):
            yield tile_position, {}

    def load_entity(self, obj, tile_size, index=0):
        assert tile_size[0] == tile_size[1]
        x, y = snap_point((obj.x / tile_size[0], obj.y / tile_size[1]), (1, 1))
        w, h = int(obj.width / tile_size[0]), int(obj.height / tile_size[1])

        dt = {}

        for key, value in obj.properties.items():
            if key.startswith("*+"):
                dt[key[2:]] = str(int(value) + index)
                continue
            elif key.startswith("*"):
                dt[key[1:]] = value.split('-')[index]
                continue
            if key == "group":
                value = str(value)
            dt[key] = value

        def get_entity(name):
            if name == "leftleg":
                return ControllableAnt(position=(x, y), control=(Button.LEFT_FOOT, Button.ALL_BODY), **dt)
            if name == "rightleg":
                return ControllableAnt(position=(x, y), control=(Button.RIGHT_FOOT, Button.ALL_BODY), **dt)
            if name == "lefthand":
                return ControllableAnt(position=(x, y), control=(Button.LEFT_HAND, Button.ALL_BODY), **dt)
            if name == "righthand":
                return ControllableAnt(position=(x, y), control=(Button.RIGHT_HAND, Button.ALL_BODY), **dt)
            if name == "head":
                return ControllableAnt(position=(x, y), control=(Button.HEAD, Button.ALL_BODY), **dt)

        entities = []
        for name in obj.name.split(","):
            name = name.lower().strip()
            entities.append(get_entity(name))
        return entities


def scaled_image_loader(filename, colorkey, **kwargs):
    """ pytmx image loader for pygame

    Modified to load images at a scaled size

    :param filename:
    :param colorkey:
    :param kwargs:
    :return:
    """
    if colorkey:
        colorkey = pygame.Color("#{}".format(colorkey))

    pixelalpha = kwargs.get("pixelalpha", True)

    # load the tileset image
    try:
        image = pygame.image.load(filename)
    except:
        print("Image did not load correctly: {}".format(filename))
        return

    # scale the tileset image to match game scale
    scaled_size = scale_sequence(image.get_size())
    image = pygame.transform.scale(image, scaled_size)

    def load_image(rect=None, flags=None):
        if rect:
            # scale the rect to match the scaled image
            rect = Rect([i * prepare.SCALE for i in list(rect)])
            try:
                tile = image.subsurface(rect)
            except ValueError:
                logger.error("Tile bounds outside bounds of tileset image")
                raise
        else:
            tile = image.copy()

        if flags:
            tile = handle_transformation(tile, flags)

        tile = smart_convert(tile, colorkey, pixelalpha)
        return tile

    return load_image

def scale_sequence(sequence):
    """ Scale the thing

    :param sequence:
    :rtype: list
    """
    return [i * prepare.SCALE for i in sequence]