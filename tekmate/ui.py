# -*- encoding: utf-8 -*-
from os import path
import pygame


class ImageNotFound(Exception):
    pass


class PlayerUI(object):

    SCALING_FACTOR = 2.8

    def __init__(self):
        self.surface, self.image = self.create_surface_and_image(PlayerUI.SCALING_FACTOR)
        self.surface.set_colorkey((0, 128, 128))
        self.position = (500, 50)

    def render(self):  # pragma: no cover
        self.surface.fill((250, 250, 250))
        self.surface.blit(self.image, (0, 0))

    def create_surface_and_image(self, factor):
        surface = self.create_surface_with_factor(factor)
        image = self.create_image_with_factor(factor)
        return surface, image

    def create_surface_with_factor(self, factor):
        surface_proportions = (round(factor * 50), round(factor * 100))
        surface = pygame.Surface(surface_proportions)
        surface.convert()
        return surface

    def create_image_with_factor(self, factor):
        image = self.load_image("player", "player.bmp")
        img_proportions = (round(factor * image.get_width()), round(factor * image.get_height()))
        image = pygame.transform.scale(image, img_proportions)
        return image

    def load_image(self, folder, name_of_file):
        fullname = path.join('assets', folder, name_of_file)
        try:
            return pygame.image.load(fullname)
        except:
            raise ImageNotFound