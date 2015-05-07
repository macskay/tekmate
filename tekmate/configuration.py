# -*- encoding: utf-8 -*-
from glob import glob

from os.path import join, splitext
import pygame
from taz.game import Game

from tekmate.scenes import WorldScene


class PyGameInitializer(object):
    CAPTION = "Tek'ma'te"

    def __init__(self, configuration):
        self.configuration = configuration

    def initialize(self):
        pygame.init()
        self.set_up_display()
        self.set_up_mouse()
        self.load_global_images()

        return self.get_update_context(), self.get_render_context()

    def set_up_display(self):
        pygame.display.set_mode((self.configuration["display_width"], self.configuration["display_height"]))
        pygame.display.set_caption(self.CAPTION)

    def set_up_mouse(self):
        pygame.mouse.set_visible(True)

    def load_global_images(self):
        images = dict()
        base_path = join("assets", "global")
        for image_file in glob(join(base_path, "*.png")):
            name = splitext(image_file)
            surface = pygame.image.load(join(base_path, image_file)).convert()
            surface.set_colorkey((0, 128, 128))
            images[name[0]] = surface
        return images

    def get_render_context(self):
        render_context = {
            "flip": pygame.display.flip,
            "display": pygame.display.get_surface(),
            "images-global": self.load_global_images()
        }
        return render_context

    def get_update_context(self):
        update_context = {
            "clock": pygame.time.Clock(),
            "get_events": pygame.event.get
        }
        return update_context


class TekmateFactory(object):
    def __init__(self, pygame_initializer):
        self.pygame_initializer = pygame_initializer

    def create(self):
        update_context, render_context = self.pygame_initializer.initialize()
        game = Game(update_context, render_context)
        scene = WorldScene("world")
        game.register_new_scene(scene)
        game.push_scene_on_stack("world")
        return game
