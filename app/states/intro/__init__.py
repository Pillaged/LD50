import os.path
import time

from pygame import mixer

import app.asset_manager
from app.entity import Entity, DrawInterface
from app.input_manager import Button
from app.state import State


class IntroState(State):
    def process_event(self, event):
        pass

    timer = 0

    def update(self, time_delta):
        self.animations.update(time_delta)
        self.timer -= time_delta*10
        if self.timer <= 0:
            instance = self.client.replace_state("WorldState")
            #instance.change_map(self.next_map)

    def draw(self, surface):
        surface.blit(self.splash.get_sprites(None)[0][0], (0, 0))

    def startup(self, **kwargs):
        pass

    def resume(self):
        pass

    def pause(self):
        pass

    def cleanup(self):
        pass

    def set_clip(self, clip_id, time, next_level):
        self.splash = SplashScreen(sprite_name=str(clip_id))
        self.timer = float(time)
        self.next_map = "assets/level" + str(next_level) + ".tmx"


class SplashScreen(Entity, DrawInterface):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_name = "clip"
        self.sprite_state = kwargs["sprite_name"]
        self.load_sprites()

    def get_sprite_state(self):
        return self.sprite_state

    def get_tile_pos(self):
        return self.tile_pos

    def get_sprite_name(self):
        return self.sprite_name
