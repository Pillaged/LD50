import os

from app import config
import app.libraries.pyganim as pyganim
from app.asset_manager import load_and_scale
from app.db import db
from app.libraries.euclid import Point3, Vector3, proj, tile_distance, trunc
from app.game import dirs2, dirs3, get_direction, butts2

class base_enemy(Entity, DrawInterface, UpdateInterface, EventInterface, Movable, WallInterface):

    def __init__(self, start_pos, end_pos, direction, mov_spd, gun_spd, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sprite_name = "bad_guy"
        self.name = kwargs['sprite_name']
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.mov_spd = mov_spd
        self.gun_spd = gun_spd
        self.cur_pos = self.start_pos
        self.direction = direction # -> list of len 2 containing positive 1 or neg 1. x,y.

    def move(self):
        change = []
        for i in range(len(self.direction)):
            self.cur_pos[i](self.direction[i]*self.mov_spd)
        
        
