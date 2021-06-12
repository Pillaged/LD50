import pygame

from asset_manager import load_image
import os
import pytmx
import asset_manager

WIDTH, HEIGHT = 1920, 1600
BACKGROUND_COLOR = (255, 0, 255)  # RGB
TILE_MAP = "level1.tmx"
FPS = 60


def draw_window(window):
    window.fill(BACKGROUND_COLOR)
    pygame.display.update()


# def load_tile_map(tile_map):
#     global image, WIDTH, HEIGHT
#     asset_path = os.path.join(os.getcwd(), "Assets", tile_map)
#     print(asset_path)
#
#     tmxdata = pytmx.load_pygame(asset_path, pixelalpha=True)
#     WIDTH, HEIGHT = tmxdata.width * tmxdata.tilewidth, tmxdata.height * tmxdata.tileheight
#     ti = tmxdata.get_tile_image_by_gid
#     for layer in tmxdata.visible_layers:
#         if isinstance(layer, pytmx.TiledTileLayer):
#             for x, y, gid, in layer:
#                 tile = ti(gid)
#                 if tile:
#                     image = tmxdata.get_tile_image(x, y, layer)


def load_freeky_head():
    img = load_image("assets/head.png")
    screen = pygame.display.get_surface()
    screen.fill((0, 100, 0, 0))
    screen.blit(img, (0, 0))


def main():
    # tile_map_data = asset_manager.load_tile_map(os.path.join(os.getcwd(), "Assets", TILE_MAP))
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    tile_map_data = pytmx.load_pygame(os.path.join(os.getcwd(), "Assets", TILE_MAP))

    pygame.display.set_caption("First Game!")
    clock = pygame.time.Clock()
    pygame.init()
    run = True
    draw_window(window)

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        # load_freeky_head()
        for layer in tile_map_data.visible_layers:
            for x, y, gid, in layer:
                tile = tile_map_data.get_tile_image_by_gid(gid)
                if tile is not None:
                    window.blit(tile, (x * tile_map_data.tilewidth, y * tile_map_data.tileheight))
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
