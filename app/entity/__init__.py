import os

from app import config
import app.libraries.pyganim as pyganim
from app.asset_manager import load_and_scale
from app.db import db
from app.libraries.euclid import Point3, Vector3, proj, tile_distance, trunc
from app.game import dirs2, dirs3, get_direction, butts2
from threading import Thread, Lock

class Entity:
    id: int = 0
    def __init__(self, **kwargs):
        pass
class Movable:
    wants_to_move = None
    wants_to_move_direction = None
    can_move = False


class UpdateInterface:
    def update(self, dt):
        pass


class EventInterface:
    def event(self, event):
        pass


class DrawInterface:
    offset_y = 0

    def get_sprites(self, layer):
        state = self.get_sprite_state()
        frame = self.sprite[state]
        if isinstance(frame, pyganim.PygAnimation):
            surface = frame.getCurrentFrame()
            frame.rate = self.get_play_rate(state)
            return [(surface, self.get_position(), layer)]
        return [(frame, self.get_position(), layer)]

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

    def get_position(self) -> tuple[float, float]:
        raise NotImplementedError

    def get_sprite_name(self):
        raise NotImplementedError


class WallInterface:
    def valid_move(self, entity):
        raise NotImplementedError


class TileCollisionInterface:
    def start_move_into(self, entity):
        raise NotImplementedError

    def end_move_into(self, entity):
        raise NotImplementedError

    def start_move_out(self, entity):
        raise NotImplementedError

    def end_move_out(self, entity):
        raise NotImplementedError

class ECS: 
    entities: dict[int, Entity] = dict()
    update: dict[int, UpdateInterface] = dict()
    draw: dict[int, DrawInterface] = dict()
    counter: int = 0 
    mutex: Lock = Lock()

    def __init__(self, **kwargs):
        pass

    def add_entity(self, entity: Entity):
        self.mutex.acquire()

        if entity.id != 0:
            raise Exception("entity already has ID assigned")

        entity.id = self.get_id()
        self.entities[entity.id] = entity

        if isinstance(entity, UpdateInterface):
            self.update[entity.id] = entity

        if isinstance(entity, DrawInterface):
            self.draw[entity.id] = entity

        self.mutex.release()


    def remove_entity(self, entity: Entity):
        self.mutex.acquire()
        id = entity.id
        self.entities.pop(id, None)
        self.update.pop(id, None)
        self.draw.pop(id, None)
        entity.id = 0
        self.mutex.release()

    def get_update(self) -> list[UpdateInterface]:
        self.mutex.acquire()
        i = list(self.update.values())
        self.mutex.release()
        return i

    def get_draw(self) -> list[DrawInterface]:
        self.mutex.acquire()
        i = list(self.draw.values())
        self.mutex.release()
        return i

    def get_id(self) -> int:
        self.counter += 1
        id = self.counter 
        return id