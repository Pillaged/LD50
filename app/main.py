import pygame

from app import prepare
from app.client import Client


def main():
    prepare.init()
    client = Client("Five Ants")
    client.auto_state_discovery()
    client.push_state("BackgroundState")
    client.push_state("MenuState")
    client.main()
    pygame.quit()
