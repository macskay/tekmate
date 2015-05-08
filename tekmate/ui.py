# -*- encoding: utf-8 -*-
import sys

import os
from os.path import abspath, split, join
import pygame

from tekmate.game import Player


class PlayerUserInterface(object):
    class ImageNotFound(Exception):
        pass

    SCALING_FACTOR = 2.8

    def __init__(self):
        self.player = None
        self.global_images = None
        self.surface = None
        self.image = None
        self.create_surface_and_image(PlayerUserInterface.SCALING_FACTOR)
        self.player = Player()

    def render(self):
        self.surface.fill((255, 255, 255))
        self.surface.blit(self.image, (0, 0))

    def draw_player_to_display(self, display):
        display.blit(self.surface, self.get_position())

    def create_surface_and_image(self, factor):
        self.create_surface_with_factor(factor)
        self.create_image_with_factor(factor)

    def create_surface_with_factor(self, factor):
        surface_proportions = (round(factor * 50), round(factor * 100))
        self.surface = pygame.Surface(surface_proportions)
        self.surface.convert()
        self.surface.set_colorkey((0, 128, 128))

    def create_image_with_factor(self, factor):
        self.image = self.load_image("player", "player.png")
        img_proportions = (int(round(factor * self.image.get_width())), int(round(factor * self.image.get_height())))
        self.image = pygame.transform.scale(self.image, img_proportions)

    def load_image(self, folder, name_of_file):
        pth = abspath(split(__file__)[0])
        sys.path.append(abspath(join(pth, u"..")))
        fullname = os.path.join(pth, "..", "assets", folder, name_of_file)
        try:
            return pygame.image.load(fullname)
        except:
            raise PlayerUserInterface.ImageNotFound

    def get_position(self):
        return self.player.position