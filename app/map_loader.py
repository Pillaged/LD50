import logging
from collections import Iterable
from itertools import product

import pygame
from pygame import Rect
from pytmx import pytmx
from pytmx.util_pygame import handle_transformation, smart_convert

from app import prepare, asset_manager
from app.entity.controllable_ant import ControllableAnt, MainControllableAnt
from app.entity.man import ManPart, ManHead
from app.entity.win import Win
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

        self.left_hand = ManPart(position=(0, 0), sprite_name="lefthand")
        self.right_hand = ManPart(position=(0, 0), sprite_name="righthand")
        self.left_leg = ManPart(position=(0, 0), sprite_name="leftleg")
        self.right_leg = ManPart(position=(0, 0), sprite_name="rightleg")
        self.head = ManHead(position=(0, 0), sprite_name="head",
                            pieces=[self.left_hand, self.right_hand, self.right_leg, self.left_leg])
        self.left_hand.head = self.head
        self.right_hand.head = self.head
        self.left_leg.head = self.head
        self.right_leg.head = self.head

        self.left_hand_ant = ControllableAnt(position=(0, 0), control=(Button.LEFT_HAND, Button.ALL_BODY),
                                             part=self.left_hand)
        self.right_hand_ant = ControllableAnt(position=(0, 0), control=(Button.RIGHT_HAND, Button.ALL_BODY),
                                              part=self.right_hand)
        self.left_leg_ant = ControllableAnt(position=(0, 0), control=(Button.LEFT_FOOT, Button.ALL_BODY),
                                            part=self.left_leg)
        self.right_leg_ant = ControllableAnt(position=(0, 0), control=(Button.RIGHT_FOOT, Button.ALL_BODY),
                                             part=self.right_leg)
        self.head_ant = MainControllableAnt(position=(0, 0), control=(Button.HEAD, Button.ALL_BODY),
                                            part=self.head,
                                            pieces=[self.left_hand_ant, self.right_hand_ant, self.left_leg_ant,
                                                    self.right_leg_ant])
        for obj in data.objects:
            if obj.type and obj.type.lower().startswith("collision"):
                for tile_position, conds in self.region_tiles(obj, tile_size):
                    collision_map[tile_position] = conds if conds else None
            elif obj.type == "entity":
                e = self.load_entity(obj, tile_size)
                if e:
                    if isinstance(e, Iterable):
                        entities.extend(filter(bool, e))
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
        entities.extend((self.left_leg, self.right_hand, self.left_hand, self.right_leg, self.head, self.left_leg_ant,
                         self.right_hand_ant, self.left_hand_ant, self.right_leg_ant, self.head_ant))
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
                self.left_leg_ant.set_position((x, y))
            if name == "rightleg":
                self.right_leg_ant.set_position((x, y))

            if name == "lefthand":
                self.left_hand_ant.set_position((x, y))

            if name == "righthand":
                self.right_hand_ant.set_position((x, y))

            if name == "head":
                self.head_ant.set_position((x, y))

            if name == "hleftleg":
                self.left_leg.set_position((x, y))
            if name == "hrightleg":
                self.right_leg.set_position((x, y))

            if name == "hlefthand":
                self.left_hand.set_position((x, y))

            if name == "hrighthand":
                self.right_hand.set_position((x, y))

            if name == "hhead":
                self.head.set_position((x, y))

            if name == "win":
                return Win(position=(x, y), **dt)

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
