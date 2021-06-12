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
