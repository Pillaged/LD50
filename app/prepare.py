import os
import sys

import pygame

NATIVE_RESOLUTION = [960, 480]
SCREEN_SIZE = [960, 480]
TILE_SIZE = [32, 32]
SCALE = 1
LIBDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

BASEDIR = sys.path[0]
USER_GAME_DIR = os.path.join(os.path.expanduser("~"), ".antfive")

USER_GAME_ASSETS_DIR = os.path.join(USER_GAME_DIR, "../assets")

USER_GAME_DATA_DIR = os.path.join(USER_GAME_DIR, "data")

USER_GAME_SAVE_DIR = os.path.join(USER_GAME_DIR, "saves")

if not os.path.isdir(USER_GAME_DIR):
    os.makedirs(USER_GAME_DIR)


def init():
    pygame.init()
    pygame.display.set_caption("Five Ants")
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    pygame.display.set_mode(SCREEN_SIZE, flags)


def fetch(*args):
    """Fancy code to allow paths dynamically determine paths."""
    relative_path = os.path.join(*args)

    path = os.path.join(USER_GAME_DIR, relative_path)
    if os.path.exists(path):
        return path

    path = os.path.join(BASEDIR,"", relative_path)
    print(path)
    if os.path.exists(path):
        return path

    path = os.path.join(BASEDIR, relative_path)
    if os.path.exists(path):
        return path
    print(path)
    raise OSError(f"cannot load file {relative_path}")
