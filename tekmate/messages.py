# -*- encoding: utf-8 -*-
from os.path import join, abspath, split
import pygame
import sys


class MessageSystem(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.surface = pygame.Surface((pygame.display.get_surface().get_width(),
                                       pygame.display.get_surface().get_height())).convert()
        self.surface.set_colorkey((0, 0, 0))
        self.image = self.surface
        self.rect = self.image.get_rect()
        pth = abspath(split(__file__)[0])
        sys.path.append(abspath(join(pth, u"..")))
        self.font = pygame.font.Font(join(pth, "..", "assets", "global", "fonts", "RosesareFF0000.ttf"), 25)

    def display_text(self, message, actor):
        self.surface.fill((0, 0, 0))
        text = self.font.render(message, True, actor.TEXT_COLOR)
        rect_actor = actor.get_position()
        self.surface.blit(text, rect_actor.topleft)
