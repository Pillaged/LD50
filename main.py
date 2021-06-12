import pygame

from asset_manager import load_image
import os
import pytmx

WIDTH, HEIGHT = 600, 400
BACKGROUND_COLOR = (255, 0, 255)  # RGB
TILE_MAP = "level1.tmx"
FPS = 60


def draw_window(window):
    window.fill(BACKGROUND_COLOR)
    pygame.display.update()


def load_tile_map(tile_map):
    global image, WIDTH, HEIGHT
    asset_path = os.path.join(os.getcwd(), "Assets", tile_map)
    print(asset_path)

    tmxdata = pytmx.load_pygame(asset_path, pixelalpha=True)
    WIDTH, HEIGHT = tmxdata.width * tmxdata.tilewidth, tmxdata.height * tmxdata.tileheight
    ti = tmxdata.get_tile_image_by_gid
    for layer in tmxdata.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid, in layer:
                tile = ti(gid)
                if tile:
                    image = tmxdata.get_tile_image(x, y, layer)


def main():
    # load_tile_map(TILE_MAP)
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("First Game!")
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.get_surface()
    run = True
    img = load_image("assets/head.png")
    draw_window(window)

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        screen.fill((0, 100, 0, 0))
        screen.blit(img, (0,0))
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
