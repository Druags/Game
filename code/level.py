import pygame
from settings import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Interaction, Particle
from transition import Transition
from pytmx.util_pygame import load_pygame
from support import *
from soil import SoilLayer
from sky import Rain, Sky
from random import randint


class Level:
    def __init__(self):

        # получаем отображаемую поверхность
        self.display_surface = pygame.display.get_surface()

        # все спрайты
        self.all_sprites = CameraGroup()
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()
        self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)

        # небо
        self.sky = Sky()
        self.rain = Rain(self.all_sprites)
        self.raining = True if randint(0, 10) > 3 else False
        self.soil_layer.raining = self.raining

        self.setup()
        self.overlay = Overlay(self.player)
        self.transition = Transition(self.reset, self.player)

    def setup(self):
        tmx_data = load_pygame('../data/map.tmx')

        # дом
        for layer in ['HouseFloor', 'HouseFurnitureBottom']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])

        for layer in ['HouseWalls', 'HouseFurnitureTop']:
            for x, y, surf in tmx_data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

        # изгородь
        for x, y, surf in tmx_data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), surf, [self.all_sprites, self.collision_sprites], LAYERS['main'])

        # вода
        water_frames = import_folder('../graphics/water')
        for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE), water_frames, self.all_sprites)

        # деревья
        for obj in tmx_data.get_layer_by_name('Trees'):
            Tree(pos=(obj.x, obj.y),
                 surf=obj.image,
                 groups=[self.all_sprites, self.collision_sprites, self.tree_sprites],
                 name=obj.name,
                 player_add=self.player_add
                 )

        # цветы
        for obj in tmx_data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image, [self.all_sprites, self.collision_sprites])

        for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), pygame.Surface((TILE_SIZE, TILE_SIZE)), self.collision_sprites)

        # взаимодействия игрока
        for obj in tmx_data.get_layer_by_name('Player'):
            if obj.name == 'Start':
                self.player = Player(pos=(obj.x, obj.y),
                                     group=self.all_sprites,
                                     collision_sprites=self.collision_sprites,
                                     tree_sprites=self.tree_sprites,
                                     interaction=self.interaction_sprites,
                                     soil_layer=self.soil_layer
                                     )
            if obj.name == 'Bed':
                Interaction(pos=(obj.x, obj.y),
                            size=(obj.width, obj.height),
                            groups=self.interaction_sprites,
                            name=obj.name
                            )

        Generic(
            pos=(0, 0),
            surf=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
            groups=self.all_sprites,
            z=LAYERS['ground'])

    def reset(self):
        self.soil_layer.update_plants()

        # почва
        self.soil_layer.remove_water()

        # дождь
        self.raining = True if randint(0, 10) > 3 else False
        self.soil_layer.raining = self.raining
        if self.raining:
            self.soil_layer.water_all()

        # яблоки на деревьях

        for tree in self.tree_sprites.sprites():
            if hasattr(tree, 'apple_sprites'):
                for apple in tree.apple_sprites.sprites():
                    apple.kill()
                tree.create_fruit()

        self.sky.start_color = [255, 255, 255]

    def player_add(self, item):
        self.player.item_inventory[item] += 1

    def plant_collision(self):
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player_add(plant.plant_type)
                    plant.kill()
                    Particle(plant.rect.topleft, plant.image, self.all_sprites, LAYERS['main'])
                    row = plant.rect.centerx // TILE_SIZE
                    col = plant.rect.centery // TILE_SIZE
                    self.soil_layer.grid[row][col].remove('P')

    def run(self, dt):
        self.display_surface.fill('black')
        self.all_sprites.custom_draw(self.player)
        self.all_sprites.update(dt)

        self.plant_collision()

        self.overlay.display()

        #  дождь
        if self.raining:
            self.rain.update()

        self.sky.display(dt)

        if self.player.sleep:
            self.transition.play()


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH / 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT / 2

        for layer in LAYERS.values():
            for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):

                if sprite.z == layer:

                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset
                    self.display_surface.blit(sprite.image, offset_rect)
                    if DEBUG:
                        if hasattr(sprite, 'hitbox'):
                            hitbox_rect = sprite.hitbox.copy()
                            hitbox_rect.center -= self.offset
                            pygame.draw.rect(self.display_surface, 'red', hitbox_rect, 5)
                            if sprite == player:
                                target_pos = offset_rect.center + PLAYER_TOOL_OFFSET[player.status.split('_')[0]]
                                pygame.draw.circle(self.display_surface, 'green', target_pos, 3)
