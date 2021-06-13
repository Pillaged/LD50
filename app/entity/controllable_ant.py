from copy import copy

from app.entity import Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface
from app.game import get_direction, dirs2
from app.input_manager import Button


class ControllableAnt(Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_name = "ant_small"
        self.control = kwargs['control']
        self.body = kwargs['part']
        self.load_sprites()
        self.can_move = True

    def get_sprite_state(self):
        return "idle_animation"

    def get_tile_pos(self):
        return self.tile_pos

    def get_sprite_name(self):
        return self.sprite_name

    def update(self, dt):
        if self.can_move and self.wants_to_move and not self.path and self.wants_to_move_direction:
            self.move_one_tile(self.wants_to_move_direction)
        self.update_physics(dt)
        self.move(dt)
        if self.moving:
            self.body.path = copy(self.path)
        self.wants_to_move = False
        self.wants_to_move_direction = False

    def event(self, event):
        if event.button in self.control:
            self.wants_to_move = True

        if event.button in [Button.RIGHT, Button.LEFT, Button.UP, Button.DOWN]:
            self.wants_to_move_direction = event.button


class MainControllableAnt(ControllableAnt):
    pass
