import itertools
import logging
from app.renderer import Renderer

import pygame

from app import prepare
from app.entity import DrawInterface, EventInterface, UpdateInterface, WallInterface
from app.entity.controllable_ant import ControllableAnt, MainControllableAnt
from app.entity.man import ManHead
from app.game import pairs
from app.libraries.euclid import nearest, trunc
from app.input_manager import Button
from app.state import State
import pyscroll

logger = logging.getLogger(__name__)


class WorldState(State):

    render : Renderer

    def __init__(self, client):
        super().__init__(client)

    def update(self, time_delta):
        super().update(time_delta)

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

        if event.button == Button.RESET and event.pressed:
            # TODO
            pass

    def startup(self, *args, **kwargs):
        super().startup(*args, **kwargs)

        self.screen = self.client.screen
        self.screen_rect = self.screen.get_rect()
        self.renderer = Renderer(tuple(prepare.SCREEN_SIZE))
        self.resolution = prepare.SCREEN_SIZE
        self.tile_size = prepare.TILE_SIZE

    def add_entity(self, entity):
        entity.world = self
        self.entities.append(entity)

    def project(self, position):
        return position[0] * self.tile_size[0], position[1] * self.tile_size[1]

    def map_drawing(self, surface):

        # get player coords to center map
        cx, cy = nearest(self.project(self.player[0].tile_pos))
        # cx, cy = 0, 0

        # offset center point for player sprite
        cx += prepare.TILE_SIZE[0] // 2
        cy += prepare.TILE_SIZE[1] // 2

        # center the map on center of player sprite
        # must center map before getting sprite coordinates
        self.current_map.renderer.center((cx, cy))

        # get list of surfaces to draw
        # TODO
        world_surfaces = list()
        for e in self.entities:
            if isinstance(e, DrawInterface):
                # list of (frame, pos, layer)
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
            # h = s.get_height()
            # if h > prepare.TILE_SIZE[1]:
            #     # offset for center and image height
            #     c = nearest((c[0], c[1] - h // 2))

            screen_surfaces.append((s, c, l))

        # draw the map and sprites
        self.rect = self.render.draw(surface, surface.get_rect(), screen_surfaces)

        # If we want to draw the collision map for debug purposes
        if False:  # prepare.CONFIG.collision_map:
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
