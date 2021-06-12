import pygame

from asset_manager import load_image

width, height = 600, 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("First Game!")

background_color = (255, 0, 255)  # RGB


def main():
    pygame.init()
    screen = pygame.display.get_surface()
    run = True
    img = load_image("assets/head.png")
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        screen.fill((0, 100, 0, 0))
        screen.blit(img, (0,0))
        pygame.display.update()
    pygame.quit()


if __name__ == '__main__':
    main()
