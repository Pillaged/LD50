import itertools
import logging
from telnetlib import EC
from app.entity.dummy import Dummy
from app.pathfinding import dijkstra
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

        if event.button == Button.MOUSE_LEFT and event.pressed:
            print(self.renderer.get_world_position(event.value))

    def startup(self, *args, **kwargs):
        super().startup(*args, **kwargs)
        self.renderer = Renderer(screen_size = prepare.SCREEN_SIZE, map_size=(1200,1200))
        self.ecs = ECS()

        self.collision_map = asset_manager.load_collision_map("collision_map_1.png")

        path = dijkstra((60,60), (340, 190), (32,32), self.collision_map.grid)
        self.path = path

        dummy = Dummy()
        dummy.position = (40,40)
        self.ecs.add_entity(dummy)

        self.renderer.center((0,0))


    def map_drawing(self, surface):
        # center the map on center of player sprite
        # must center map before getting sprite coordinates
        # self.renderer.center((100, 100))

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

        # demo pathfinding
        if True:
            ox, oy = self.renderer.view_rect.left, self.renderer.view_rect.top
            for point in self.path:
                x, y = -ox + point[0], -oy + point[1]
                pygame.draw.rect(surface, (0, 255, 0), (x,y,32,32))
                pygame.draw.rect(surface, (0, 0, 255), (x,y,2,2))

        # If we want to draw the collision map for debug purposes
        if True:  # prepare.CONFIG.collision_map:
            self.debug_drawing(surface)

    def debug_drawing(self, surface: pygame.Surface):
        ox, oy = self.renderer.view_rect.left, self.renderer.view_rect.top
        surface.blit(self.collision_map.image, (-ox, -oy))

        # draw center lines to verify camera is correct
        w, h = surface.get_size()
        cx, cy = w // 2, h // 2
        pygame.draw.line(surface, (255, 50, 50), (cx, 0), (cx, h))
        pygame.draw.line(surface, (255, 50, 50), (0, cy), (w, cy))

