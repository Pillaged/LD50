import os

from app import config
import app.libraries.pyganim as pyganim
from app.asset_manager import load_and_scale
from app.db import db
from app.libraries.euclid import Point3, Vector3, proj, tile_distance, trunc
from app.game import dirs2, dirs3, get_direction


class Entity:
    def __init__(self, **kwargs):
        self.type = None
        self.world = None

        # Physics
        self.position3 = Point3(0, 0, 0)
        self.velocity3 = Vector3(0, 0, 0)

        # Movement
        self.path = []
        self.path_origin = None
        self.final_move_dest = None
        self.facing = "down"
        self.move_rate = config.walk_rate

        if "slug" in kwargs:
            self.slug = kwargs["slug"]
        if "position" in kwargs:
            self.set_position(kwargs["position"])

    @property
    def tile_pos(self):
        return proj(self.position3)

    @property
    def world_pos(self):
        return proj(self.path[-1]) if self.moving and self.path else proj(self.tile_pos)

    # Physics
    def update_physics(self, td):
        self.position3 += self.velocity3 * td
        self.pos_update()

    def set_position(self, pos):
        self.position3.x = pos[0]
        self.position3.y = pos[1]

    def stop_moving(self):
        self.velocity3.x = 0
        self.velocity3.y = 0
        self.velocity3.z = 0

    @property
    def moving(self):
        return not self.velocity3 == (0, 0, 0)

    def move(self, dt):
        self.update_physics(dt)
        if self.path:
            if self.path_origin:
                # if path origin is set, then npc has started moving
                # from one tile to another.
                self.check_waypoint()
            else:
                # if path origin is not set, then a previous attempt to change
                # waypoints failed, so try again.
                self.next_waypoint()

        if not self.path:
            self.cancel_movement()

    def move_one_tile(self, direction):
        pos = self.path[0] if self.path else self.world_pos
        self.path.insert(0, trunc(pos + dirs2[direction]))

    def next_waypoint(self):
        target = self.path[-1]
        direction = get_direction(self.tile_pos, target) if self.tile_pos != target else self.facing
        self.facing = direction
        if self.world.valid_move(self, target):
            self.path_origin = tuple(self.tile_pos)
            self.velocity3 = self.move_rate * dirs3[direction]
            self.world.start_move_out(self, self.path_origin)
            self.world.start_move_into(self, target)
        else:
            # the target is blocked now
            self.stop_moving()

    def check_waypoint(self):
        """ Check if the waypoint is reached and sets new waypoint if so.
        :return: None
        """
        target = self.path[-1]
        expected = tile_distance(self.path_origin, target)
        traveled = tile_distance(self.tile_pos, self.path_origin)
        if traveled >= expected:
            self.set_position(target)
            self.path.pop()

            self.world.end_move_out(self, self.path_origin)
            self.world.end_move_into(self, target)

            self.path_origin = None
            if self.path:
                self.next_waypoint()

    def cancel_movement(self):
        """ Gracefully stop moving.  May cause issues with world triggers.
        :return:
        """
        if self.tile_pos == self.path_origin:
            self.abort_movement()
        elif self.path and self.moving:
            self.path = [self.path[-1]]
        else:
            self.stop_moving()
            self.cancel_path()

    def abort_movement(self):
        """ Stop moving, cancel paths, and reset tile position to center. May cause issues with world triggers.
        :return:
        """
        if self.path_origin is not None:
            self.set_position(self.path_origin)
        self.stop_moving()
        self.cancel_path()

    def cancel_path(self):
        self.path = []
        self.path_origin = None


class DrawInterface:
    def get_sprites(self, layer):
        state = self.get_sprite_state()
        frame = self.sprite[state]
        if isinstance(frame, pyganim.PygAnimation):
            surface = frame.getCurrentFrame()
            frame.rate = self.get_play_rate(state)
            return [(surface, self.get_tile_pos(), layer)]
        return [(frame, self.get_tile_pos(), layer)]

    def load_sprites(self, sprite_name=None):
        """ Load sprite graphics

        :return:
        """
        self.sprite = {}
        self.moveConductor = pyganim.PygConductor()

        sprite_name = sprite_name if sprite_name else self.get_sprite_name()
        data = db.lookup(sprite_name, table="sprite_data")
        for key, value in data["sprites"].items():
            file = value['file']
            if value["animation"]:
                num_frames = value['frames']
                frame_duration = value['frame_duration']
                files = ["{}.{}.png".format(file, str(i).rjust(3, '0')) for i in range(num_frames)]
                paths = [os.path.join("sprites", file) for file in files]
                frames = [(load_and_scale(path), frame_duration) for path in paths]
                self.sprite[key] = pyganim.PygAnimation(frames, loop=True)
                self.moveConductor.add(self.sprite[key])

            else:
                path = os.path.join("sprites", file + ".png")
                self.sprite[key] = load_and_scale(path)

        self.moveConductor.play()

    def get_play_rate(self, state):
        return 1.0

    def get_sprite_state(self):
        raise NotImplementedError

    def get_tile_pos(self):
        raise NotImplementedError

    def get_sprite_name(self):
        raise NotImplementedError
