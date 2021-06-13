import logging

import pyscroll as pyscroll

from app import prepare
from app.input_manager import Button
from app.libraries.euclid import Vector2, Vector3

logger = logging.getLogger(__name__)

# direction => vector
dirs3 = {
    "up": Vector3(0, -1, 0),
    "down": Vector3(0, 1, 0),
    "left": Vector3(-1, 0, 0),
    "right": Vector3(1, 0, 0),
}
dirs2 = {
    "up": Vector2(0, -1),
    "down": Vector2(0, 1),
    "left": Vector2(-1, 0),
    "right": Vector2(1, 0),
}

butts2 = {
    Button.UP: Vector2(0, -1),
    Button.DOWN: Vector2(0, 1),
    Button.LEFT: Vector2(-1, 0),
    Button.RIGHT: Vector2(1, 0),
}

# 1 letter direction names
short_dirs2 = {d[0]: dirs2[d] for d in dirs2}

# complimentary directions
pairs = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left"
}

# what directions entities can face
facing = "front", "back", "left", "right"

facing_to_dirs = {
    "back": "up",
    "front": "down",
    "left": "left",
    "right": "right"
}


def get_direction(p1, p2):
    vals = ("up", -p2[1] + p1[1]), ("down", -p1[1] + p2[1]), ("right", p2[0] - p1[0]), ("left", p1[0] - p2[0])
    return max(vals, key=lambda x: x[1])[0]


class GameMap:
    def __init__(self, collision_map, entities, edges, data, filename):
        self.collision_map = collision_map
        self.entities = entities
        self.edges = edges
        self.renderer = None
        self.data = data
        self.size = data.width, data.height
        self.sprite_layer = 2
        self.filename = filename

    def initialize_renderer(self):
        visual_data = pyscroll.TiledMapData(self.data)
        clamp = (self.edges == "clamped")
        self.renderer = pyscroll.BufferedRenderer(visual_data, prepare.SCREEN_SIZE, clamp_camera=clamp, tall_sprites=2)
