import os

from pygame import mixer

from app.input_manager import Button
from app.state import State


class BackgroundState(State):

    def draw(self, surface):
        surface.fill((0, 0, 0, 0))

    def process_event(self, event):
        if event.button == Button.QUIT:
            self.client.done = True

        if event.button == Button.ESCAPE and event.pressed:
            self.client.done = True

    def startup(self, **kwargs):
        mixer.init()
        mixer.music.load(os.path.join("assets", "menu_music.wav"))
        mixer.music.set_volume(0.5)
        mixer.music.play(loops=-1)
