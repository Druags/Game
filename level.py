import pygame
from settings import *
from player import Player
from overlay import Overlay


class Level:
    def __init__(self):
        # получаем отображаемую поверхность
        self.display_surface = pygame.display.get_surface()

        # все спрайты
        self.all_sprites = pygame.sprite.Group()
        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        self.player = Player((640, 320), self.all_sprites)

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.draw(self.display_surface)
        self.overlay.display()
        self.all_sprites.update(dt)
