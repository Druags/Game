import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic
from pytmx.util_pygame import load_pygame


class Level:
    def __init__(self):
        # получаем отображаемую поверхность
        self.display_surface = pygame.display.get_surface()

        # все спрайты
        self.all_sprites = CameraGroup()
        self.setup()
        self.overlay = Overlay(self.player)

    def setup(self):
        tmx_data = load_pygame('data/map.tmx')

        # дом
        for x, y, surf in tmx_data.get_layer_by_name('HouseFurnitureBottom').tiles():
            Generic((x*TILE_SIZE, y*TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        self.player = Player((640, 320), self.all_sprites)
        Generic(pos=(0, 0),
                surf=pygame.image.load('graphics/world/ground.png').convert_alpha(),
                groups=self.all_sprites,
                z=LAYERS['ground'])

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.overlay.display()
        self.all_sprites.update(dt)


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2
        for layer in LAYERS.values():
            for sprite in self.sprites():
                print(sprite)
                if sprite.z == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
