import os
import sys

NATIVE_RESOLUTION = [320, 288]
SCREEN_SIZE = [320*4, 288*4]

LIBDIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

BASEDIR = sys.path[0]
USER_GAME_DIR = os.path.join(os.path.expanduser("~"), ".antfive")

# game data dir
USER_GAME_ASSETS_DIR = os.path.join(USER_GAME_DIR, "assets")

# game data dir
USER_GAME_DATA_DIR = os.path.join(USER_GAME_DIR, "data")

# game savegame dir
USER_GAME_SAVE_DIR = os.path.join(USER_GAME_DIR, "saves")

if not os.path.isdir(USER_GAME_DIR):
    os.makedirs(USER_GAME_DIR)


def fetch(*args):
    """Fancy code to allow paths dynamically determine paths."""
    relative_path = os.path.join(*args)

    path = os.path.join(USER_GAME_DIR, relative_path)
    if os.path.exists(path):
        return path

    path = os.path.join(BASEDIR, relative_path)
    if os.path.exists(path):
        return path

    raise OSError(f"cannot load file {relative_path}")


