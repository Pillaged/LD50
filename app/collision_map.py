from PIL import Image
from enum import Enum

import pygame

class CollisionMap:
    image: pygame.Surface
    grid: list[list[int]]
    adjacency: dict[tuple[int,int], list[tuple[int,int]]]
    def __init__(self, filename: str):
        im = Image.open(filename)
        im = im.convert('RGB')
        width, height = im.size
        self.grid = [[Collision.INVALID]*height for _ in range(width)]
        for i in range(width):
            for j in range(height):
                self.grid[i][j] = get_collision(im.getpixel((i,j)))
        print(self.grid[59][60])
        print(im.getpixel((59,60)))
        self.image = pygame.image.load(filename)
    
    def pre_process(self):
        width, height = len(self.grid), len(self.grid[0])

        for i in range(width):
            for j in range(height):
                self.adjacency[(i,j)] = get_adjacent((i,j))
        

def get_collision(pixel: tuple[int, int, int]):
    if pixel == (0,0,0):
        return Collision.EMPTY
    elif pixel == (255,0,0):
        return Collision.WALL
    else:
        return Collision.INVALID

def get_adjacent(position: tuple[int,int]) -> tuple[tuple[int, int]]:
    x, y = position
    return (
        (x+1, y+1),
        (x+1, y+1),
        (x+1, y),
        (x+1, y-1),
        (x, y+1),
        (x, y-1),
        (x-1, y+1),
        (x-1, y),
        (x-1, y-1),


        # (x+2, y+1),
        # (x+2, y-1),
        # (x-2, y+1),
        # (x-2, y-1),

        # (x+1, y+2),
        # (x+1, y-2),
        # (x-1, y+2),
        # (x-1, y-2),
    )
            
class Collision(Enum):
    INVALID = -1
    EMPTY = 0
    WALL = 1