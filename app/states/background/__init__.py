from app.state import State


class BackgroundState(State):

    def draw(self, surface):
        surface.fill((0, 0, 0, 0))
