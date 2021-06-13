from app.entity import Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface
from app.entity.man import ManHead
from app.game import get_direction, dirs2
from app.input_manager import Button


class Win(Entity, UpdateInterface):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clip = kwargs["clip"]
        self.cliptime = kwargs["cliptime"]
        self.level = kwargs["level"]

    def update(self, dt):
        for e in self.world.entities:
            if isinstance(e, ManHead):
                if self.get_tile_pos() == e.get_tile_pos():
                    self.world.next_level(self.clip, self.cliptime, self.level)

    def get_tile_pos(self):
        return self.tile_pos
