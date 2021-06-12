import pygame

width, height = 600, 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("First Game!")

background_color = (255, 0, 255)  # RGB


def main():
    pygame.init()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        window.fill()
    pygame.quit()


if __name__ == '__main__':
    main()
