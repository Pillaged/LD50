from PIL import Image
from enum import Enum

class CollisionMap:
    grid: list[list[int]]
    def __init__(self, filename: str):
        im = Image.open(filename)
        im = im.convert('RGB')
        width, height = im.size
        self.grid = [[Collision.INVALID]*height for _ in range(width)]
        for i in range(width):
            for j in range(height):
                self.grid[i][j] = get_collision(im.getpixel((i,j)))

def get_collision(pixel: tuple[int, int, int]):
    if pixel == (255,255,255):
        return Collision.EMPTY
    elif pixel == (0,0,0):
        return Collision.WALL
    else:
        return Collision.INVALID
            
class Collision(Enum):
    INVALID = -1
    EMPTY = 0
    WALL = 1