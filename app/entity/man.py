from app.entity import Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface
from app.game import get_direction, dirs2
from app.input_manager import Button
from app.libraries.euclid import square_distance


class ManPart(Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface):

    def valid_move(self, entity):
        return False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_name = "man"
        self.name = kwargs['sprite_name']  # TODO RENAME
        self.load_sprites(self.sprite_name)
        self.can_move = True
        self.too_far = False
        self.head = self

    def update(self, dt):
        head_loc = self.head.path[0] if self.head.path else self.head.get_tile_pos()
        if self.path and square_distance(self.path[0], head_loc) > 2.1:
            self.cancel_movement()
            self.path = []
        self.update_physics(dt)
        self.move(dt)

    def get_sprite_state(self):
        return self.name

    def register_ant(self, ant):
        self.ant = ant

    def get_tile_pos(self):
        return self.tile_pos

    def get_sprite_name(self):
        return self.sprite_name


class ManHead(ManPart):
    offset_y = 1

    def __init__(self, **kwargs):
        super(ManHead, self).__init__(**kwargs)
        self.pieces = kwargs["pieces"]

    def update(self, dt):

        cancel_movement = False
        for piece in self.pieces:
            piece_loc = piece.path[0] if piece.path else piece.get_tile_pos()
            if self.path and square_distance(self.path[0], piece_loc) > 3:
                cancel_movement = True
        if cancel_movement:
            self.cancel_movement()
        super(ManHead, self).update(dt)
