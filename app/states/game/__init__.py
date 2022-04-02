import itertools
import logging
from telnetlib import EC
from app.entity.dummy import Dummy
from app.renderer import Renderer

import pygame

from app import asset_manager, prepare
from app.collision_map import CollisionMap 
from app.entity import ECS, DrawInterface, EventInterface, UpdateInterface, WallInterface
from app.entity.controllable_ant import ControllableAnt, MainControllableAnt
from app.entity.man import ManHead
from app.game import pairs
from app.libraries.euclid import nearest, trunc
from app.input_manager import Button
from app.state import State
import pyscroll

logger = logging.getLogger(__name__)


class WorldState(State):

    renderer : Renderer
    ecs : ECS
    collision_map: CollisionMap
    player : any

    def __init__(self, client):
        super().__init__(client)

    def update(self, time_delta):
        super().update(time_delta)

    def draw(self, surface):
        self.map_drawing(surface)

    def process_event(self, event):
        if event.button == Button.QUIT:
            self.client.done = True
            return None

        if event.button == Button.ESCAPE and event.pressed:
            self.client.done = True
            return None

        if event.button == Button.INTERACT and event.pressed:
            pass

        # TODO event entities
        # for e in self.entities:
        #     if isinstance(e, EventInterface):
        #         e.event(event)

        if event.button == Button.RESET and event.pressed:
            # TODO
            pass

    def startup(self, *args, **kwargs):
        super().startup(*args, **kwargs)
        self.renderer = Renderer(screen_size = prepare.SCREEN_SIZE, map_size=(1000,1000))
        self.ecs = ECS()

        self.collision_map = asset_manager.load_collision_map("collision_map_1.png")

        dummy = Dummy()
        self.ecs.add_entity(dummy)


    def map_drawing(self, surface):
        # center the map on center of player sprite
        # must center map before getting sprite coordinates
        self.renderer.center((100, 100))

        world_surfaces = list()
        for e in self.ecs.get_draw():
            world_surfaces.extend(e.get_sprites("0"))

        # position the surfaces correctly
        # converted from world to screen coords here
        screen_surfaces = list()
        for frame in world_surfaces:
            s, c, l = frame

            # handle tall sprites
            # h = s.get_height()
            # if h > prepare.TILE_SIZE[1]:
            #     # offset for center and image height
            #     c = nearest((c[0], c[1] - h // 2))

            screen_surfaces.append((s, c, l))

        # draw the map and sprites
        self.rect = self.renderer.draw(surface, surface.get_rect(), screen_surfaces)

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
