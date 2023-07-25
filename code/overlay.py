import pygame
from settings import *


class Overlay:
    def __init__(self, player):
        # общие сведения
        self.display_surface = pygame.display.get_surface()
        self.player = player

        # импорты

        overlay_path = '../graphics/overlay/'
        self.tools_surface = {tool: pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in
                              player.tools}
        self.seeds_surface = {seed: pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in
                              player.seeds}

    def display(self):
        # инструменты
        tool_surf = self.tools_surface[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        # семена
        seed_surf = self.seeds_surface[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)