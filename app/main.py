import pygame

from app.client import Client

width, height = 600, 500
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("First Game!")

background_color = (255, 0, 255)  # RGB


def main():
    pygame.init()
    client = Client("Five Ants")
    client.auto_state_discovery()
    client.push_state("BackgroundState")
    client.main()
    pygame.quit()
