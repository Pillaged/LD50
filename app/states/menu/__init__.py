import os.path
import time

from pygame import mixer

import app.asset_manager
from app.entity import Entity, DrawInterface
from app.input_manager import Button
from app.state import State


class MenuState(State):
    def process_event(self, event):
        if event.button == Button.QUIT or (event.button == Button.ESCAPE and event.pressed):
            self.client.done = True
            menu_shutdown_music = app.asset_manager.load_audio(os.path.join("assets", "menu_shutdown.mp3"))
            mixer.music.stop()
            menu_shutdown_music.play()
            time.sleep()
            return

        if event.button == Button.INTERACT:
            menu_music = app.asset_manager.load_audio(os.path.join("assets", "menu_click.mp3"))
            menu_music.play()
            time.sleep(.7)
            instance = self.client.replace_state("IntroState")
            instance.set_clip("1", 13.1, 1)

    def update(self, time_delta):  # this is for updating objects, updating keystrokes, whateva
        self.animations.update(time_delta)

    def draw(self, surface):  # draw shit on surface after startup, main loop will render this automatically
        surface.blit(self.splash.get_sprites(None)[0][0], (0, 0))

    def startup(self, **kwargs):  # when it's pushed for the first time, initializes things
        self.splash = SplashScreen()

    def resume(self):
        pass

    def pause(self):
        pass

    def cleanup(self):
        pass


class SplashScreen(Entity, DrawInterface):
    position = (0,0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprite_name = "splash"
        self.load_sprites()

    def get_sprite_state(self):
        return "idle"

    def register_ant(self, ant):
        self.ant = ant

    def get_position(self) -> tuple[float, float]:
        return self.position

    def get_sprite_name(self):
        return self.sprite_name
