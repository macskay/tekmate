# -*- encoding: utf-8 -*-
from os.path import join, abspath, split
import pygame
import sys


class MessageSystem(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.surface = None
        self.image = None
        self.rect = None
        pth = abspath(split(__file__)[0])
        sys.path.append(abspath(join(pth, u"..")))
        self.font = pygame.font.Font(join(pth, "..", "assets", "global", "fonts", "RosesareFF0000.ttf"), 20)

    def set_sprite_properties(self, height, o2, width):
        self.surface = pygame.Surface((width + o2, height + o2), pygame.SRCALPHA)
        self.surface.set_colorkey((0, 0, 0))
        self.image = self.surface
        self.rect = self.image.get_rect()

    def display_text(self, message, actor):
        text = self.font.render(message, False, actor.TEXT_COLOR)

        outline = self.font.render(message, False, (0, 0, 0))
        offset = 1
        o2 = offset*2
        width, height = text.get_size()
        self.set_sprite_properties(height, o2, width)

        for off in [(0, 0), (0, o2), (o2, 0), (o2, o2)]:
            self.surface.blit(outline, off)

        self.surface.blit(text, (offset, offset))

        self.rect.centerx = pygame.display.get_surface().get_width()/2
        self.rect.centery = 350
