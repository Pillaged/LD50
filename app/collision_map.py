from PIL import Image
from enum import Enum

class CollisionMap:
    grid: list[list[int]]
    def __init__(self, filename: str):
        im = Image.open(filename)
        pixels = list(im.getdata())
        width, height = im.size
        
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]
        print(len(pixels))
        pass

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