import logging

from app import prepare
from app.entity import DrawInterface, EventInterface, UpdateInterface
from app.entity.controllable_ant import ControllableAnt, MainControllableAnt
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
        for e in self.entities:
            if isinstance(e, UpdateInterface):
                e.update(time_delta)

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
        for e in self.entities:
            if type(e) == MainControllableAnt:
                self.player = e
                return

    def add_entity(self, entity):
        entity.world = self
        self.entities.append(entity)

    def project(self, position):
        return position[0] * self.tile_size[0], position[1] * self.tile_size[1]

    def map_drawing(self, surface):
        world_surfaces = list()

        # get player coords to center map
        cx, cy = nearest(self.project(self.player.tile_pos))
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
        # if prepare.CONFIG.collision_map:
        #    self.debug_drawing(surface)

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
        # if tile in self.entity_map:
        #    for e in self.entity_map[tile]:
        #       # if isinstance(e, WallInterface) and not e.valid_move(entity):
        #            return False
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
