
from turtle import position
from app.entity import DrawInterface, Entity, UpdateInterface


class Dummy(Entity, DrawInterface, UpdateInterface):
    position: tuple[float, float]

    def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.sprite_name = "man"
            self.name = 'head' 
            self.load_sprites(self.sprite_name)
            self.position = (0,0)

    def update(self, dt):
        pass

    def get_sprite_state(self):
        return self.name

    def get_sprite_name(self):
        return self.sprite_name

    def get_position(self) -> tuple[float, float]:
        return self.position