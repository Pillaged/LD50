from app.entity import Entity, DrawInterface


class ControllableAnt(Entity, DrawInterface):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sprite_name = "ant_small"
        self.load_sprites()

    def get_sprite_state(self):
        return "idle_animation"

    def get_tile_pos(self):
        return self.tile_pos

    def get_sprite_name(self):
        return self.sprite_name
