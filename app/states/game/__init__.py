import itertools
import logging

import pygame

from app import prepare
from app.entity import DrawInterface, EventInterface, UpdateInterface
from app.entity.controllable_ant import ControllableAnt, MainControllableAnt
from app.entity.man import ManHead
from app.game import pairs
from app.libraries.euclid import nearest, trunc
from app.input_manager import Button
from app.map_loader import TMXMapLoader
from app.state import State

logger = logging.getLogger(__name__)


class WorldState(State):

    def __init__(self, client):
        super().__init__(client)

    def update(self, time_delta):
        super().update(time_delta)
        self.update_entity_map()
        for e in self.entities:
            if isinstance(e, UpdateInterface):
                e.update(time_delta)

    def update_entity_map(self):
        entity_map = dict()
        for e in self.entities:
            pos = nearest(e.world_pos)
            if pos in entity_map:
                entity_map[pos].append(e)
            else:
                entity_map[pos] = [e]
        self.entity_map = entity_map

    def draw(self, surface):
        self.screen = surface
        self.map_drawing(surface)

    def process_event(self, event):
        if event.button == Button.QUIT:
            self.client.done = True
            return None

        if event.button == Button.ESCAPE and event.pressed:
            self.client.done = True
            return None

        if event.button == Button.INTERACT and event.pressed:
            self.player = [self.player[1], self.player[0]]

        for e in self.entities:
            if isinstance(e, EventInterface):
                e.event(event)

    def startup(self, *args, **kwargs):
        super().startup(*args, **kwargs)

        self.screen = self.client.screen
        self.screen_rect = self.screen.get_rect()
        self.resolution = prepare.SCREEN_SIZE
        self.tile_size = prepare.TILE_SIZE

    def change_map(self, map_name):
        map_data = TMXMapLoader().load(map_name)

        self.current_map = map_data
        self.current_map.initialize_renderer()
        self.collision_map = map_data.collision_map
        self.map_size = map_data.size

        # The first coordinates that are out of bounds.
        self.invalid_x = (-1, self.map_size[0])
        self.invalid_y = (-1, self.map_size[1])

        self.entities = []
        for e in map_data.entities:
            self.add_entity(e)

        self.set_player()

    def set_player(self):
        self.player = []
        for e in self.entities:
            if type(e) == MainControllableAnt:
                self.player.append(e)

        for e in self.entities:
            if type(e) == ManHead:
                self.player.append(e)

    def add_entity(self, entity):
        entity.world = self
        self.entities.append(entity)

    def project(self, position):
        return position[0] * self.tile_size[0], position[1] * self.tile_size[1]

    def map_drawing(self, surface):
        world_surfaces = list()

        # get player coords to center map
        cx, cy = nearest(self.project(self.player[0].tile_pos))
        # cx, cy = 0, 0

        # offset center point for player sprite
        cx += prepare.TILE_SIZE[0] // 2
        cy += prepare.TILE_SIZE[1] // 2

        # center the map on center of player sprite
        # must center map before getting sprite coordinates
        self.current_map.renderer.center((cx, cy))
        for e in self.entities:
            if isinstance(e, DrawInterface):
                world_surfaces.extend(e.get_sprites(self.current_map.sprite_layer))

        # position the surfaces correctly
        # pyscroll expects surfaces in screen coords, so they are
        # converted from world to screen coords here
        screen_surfaces = list()
        for frame in world_surfaces:
            s, c, l = frame

            # project to pixel/screen coords
            c = self.get_pos_from_tilepos(c)

            # handle tall sprites
            h = s.get_height()
            if h > prepare.TILE_SIZE[1]:
                # offset for center and image height
                c = nearest((c[0], c[1] - h // 2))

            screen_surfaces.append((s, c, l))

        # draw the map and sprites
        self.rect = self.current_map.renderer.draw(surface, surface.get_rect(), screen_surfaces)

        # If we want to draw the collision map for debug purposes
        if True:  # prepare.CONFIG.collision_map:
            self.debug_drawing(surface)

    def debug_drawing(self, surface):
        from pygame.gfxdraw import box

        surface.lock()
        # We need to iterate over all collidable objects.  So, let's start
        # with the walls/collision boxes.
        box_iter = list(map(self._collision_box_to_pgrect, self.collision_map))
        # draw noc and wall collision tiles
        red = (255, 0, 0, 128)
        for item in box_iter:
            box(surface, item, red)

        # draw center lines to verify camera is correct
        w, h = surface.get_size()
        cx, cy = w // 2, h // 2
        pygame.draw.line(surface, (255, 50, 50), (cx, 0), (cx, h))
        pygame.draw.line(surface, (255, 50, 50), (0, cy), (w, cy))

        surface.unlock()

    def _collision_box_to_pgrect(self, box):
        """Returns a Rect (in screen-coords) version of a collision box (in world-coords).
        """

        # For readability
        x, y = self.get_pos_from_tilepos(box)
        tw, th = self.tile_size

        return pygame.Rect(x, y, tw, th)

    def get_pos_from_tilepos(self, tile_position):
        cx, cy = self.current_map.renderer.get_center_offset()
        px, py = self.project(tile_position)
        x = px + cx
        y = py + cy
        return x, y

    def valid_move(self, entity, tile):
        tile = (tile[0], tile[1])
        if tile not in self.get_exits(trunc(entity.tile_pos)):
            return False
        if tile in self.entity_map:
            for e in self.entity_map[tile]:
                # if isinstance(e, WallInterface) and not e.valid_move(entity):
                return False
        return True

    def get_exits(self, position, collision_map=None, skip_nodes=None):
        # get tile-level and npc/entity blockers
        if collision_map is None:
            collision_map = self.get_collision_map()

        if skip_nodes is None:
            skip_nodes = set()

        # if there are explicit way to exit this position use that information,
        # handles 'continue' and 'exits'
        tile_data = collision_map.get(position)
        if tile_data:
            exits = self.get_explicit_tile_exits(position, tile_data, skip_nodes)
        else:
            exits = None

        # get exits by checking surrounding tiles
        adjacent_tiles = list()
        for direction, neighbor in (
                ("down", (position[0], position[1] + 1)),
                ("right", (position[0] + 1, position[1])),
                ("up", (position[0], position[1] - 1)),
                ("left", (position[0] - 1, position[1])),
        ):
            # if exits are defined make sure the neighbor is present there
            if exits and not neighbor in exits:
                continue

            # check if the neighbor region is present in skipped nodes
            if neighbor in skip_nodes:
                continue

            # We only need to check the perimeter,
            # as there is no way to get further out of bounds
            if neighbor[0] in self.invalid_x or neighbor[1] in self.invalid_y:
                continue

            # test if this tile has special movement handling
            # NOTE: Do not refact. into a dict.get(xxxxx, None) style check
            # NOTE: None has special meaning in this check
            try:
                tile_data = collision_map[neighbor]
            except KeyError:
                pass
            else:
                # None means tile is blocked with no specific data

                if tile_data is None:
                    continue
                print(tile_data)
                try:
                    if pairs[direction] not in tile_data["enter"]:
                        continue
                except KeyError:
                    continue

            # no tile data, so assume it is free to move into
            adjacent_tiles.append(neighbor)

        return adjacent_tiles

    def get_collision_map(self):
        collision_dict = dict()
        collision_dict.update(self.collision_map)
        return collision_dict
