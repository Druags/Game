import pygame
from settings import *
from random import randint, choice
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)


class Water(Generic):
    def __init__(self, pos, frames, groups):
        # анимация

        self.frames = frames
        self.frame_index = 0
        # настройка спрайта
        super().__init__(pos=pos,
                         surf=self.frames[self.frame_index],
                         groups=groups,
                         z=LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)


class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)

        # параметры дерева
        self.health = 5
        self.alive = True
        self.stump_path = f'../graphics/stumps/{"small" if name=="Small" else "large"}.png'
        self.stump_surf = pygame.image.load(self.stump_path)
        self.invul_timer = Timer(200)

        # яблоки
        self.apple_surface = pygame.image.load('../graphics/fruit/apple.png')
        self.apple_pos = APPLE_POS[name]
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

    def damage(self):
        # урон по дереву
        self.health -= 1

        if self.apple_sprites.sprites():
            random_apple = choice(self.apple_sprites.sprites())
            random_apple.kill()

    def check_death(self):
        if self.health <= 0:
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height*0.6)
            self.alive = False

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic((x, y), self.apple_surface, [self.apple_sprites, self.groups()[0]], LAYERS['fruit'])

    def update(self, dt):
        if self.alive:
            self.check_death()

