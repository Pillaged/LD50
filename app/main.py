import pygame

from app import prepare
from app.client import Client


def main():
    prepare.init()
    client = Client("Five Ants")
    client.auto_state_discovery()
    client.push_state("BackgroundState")
    instance = client.push_state("WorldState")
    instance.change_map("assets/antlevel1.tmx")
    client.main()
    pygame.quit()
