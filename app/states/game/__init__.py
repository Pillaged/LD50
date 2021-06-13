import logging

from app import prepare
from app.entity import DrawInterface
from app.libraries.euclid import nearest
from app.input_manager import Button
from app.map_loader import TMXMapLoader
from app.state import State

logger = logging.getLogger(__name__)


class WorldState(State):

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

    def add_entity(self, entity):
        entity.world = self
        self.entities.append(entity)

    def project(self, position):
        return position[0] * self.tile_size[0], position[1] * self.tile_size[1]

    def map_drawing(self, surface):
        world_surfaces = list()

        # get player coords to center map
        # cx, cy = nearest(self.project(self.player.tile_pos))
        cx, cy = 500, 700

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
        # if prepare.CONFIG.collision_map:
        #    self.debug_drawing(surface)

    def get_pos_from_tilepos(self, tile_position):
        cx, cy = self.current_map.renderer.get_center_offset()
        px, py = self.project(tile_position)
        x = px + cx
        y = py + cy
        return x, y
