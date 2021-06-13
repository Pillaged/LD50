from app.entity import Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface
from app.game import get_direction, dirs2
from app.input_manager import Button


class ManHand(Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_name = "man"
        self.name = kwargs['sprite_name'] #TODO RENAME
        self.load_sprites(self.sprite_name)
        self.can_move = True

    def get_sprite_state(self):
        return self.name

    def register_ant(self, ant):
        self.ant = ant


    def get_tile_pos(self):
        return self.tile_pos

    def get_sprite_name(self):
        return self.sprite_name

class ManHead(ManHand):
    pass