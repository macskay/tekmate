# -*- encoding: utf-8 -*-
from taz.game import Game
from tekmate.items import Item

import pygame
from tekmate.scenes import WorldScene


class Player(object):
    class NoSuchItem(Exception):
        pass

    def __init__(self):
        self.bag = []

    def add_item(self, item):
        if not item.obtainable:
            raise Item.NotObtainable
        item.parent_container = self.bag
        self.bag.append(item)

    def trigger_item_combination(self, item1, item2):
        item1.combine(item2)
        item2.combine(item1)

    def look_at(self, item1):
        if item1 in self.bag:
            return item1.get_description()
        return item1.get_look_at_message()

    def use_item(self, item1):
        return item1.get_use_message()


class PyGameInitializer(object):
    CAPTION = "Tek'ma'te"

    def __init__(self, configuration):
        self.configuration = configuration

    def initialize(self):
        pygame.init()
        self.set_up_display()
        self.set_up_mouse()

        return self.get_update_context(), self.get_render_context()

    def set_up_display(self):
        pygame.display.set_mode((self.configuration["display_width"], self.configuration["display_height"]))
        pygame.display.set_caption(self.CAPTION)

    def set_up_mouse(self):
        pygame.mouse.set_visible(True)

    def get_render_context(self):
        render_context = {
            "flip": pygame.display.flip,
            "display": pygame.display.get_surface()
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
