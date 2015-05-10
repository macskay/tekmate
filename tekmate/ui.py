# -*- encoding: utf-8 -*-
import sys

import os
from os.path import abspath, split, join
import pygame

from tekmate.game import Player
from tekmate.items import TelephoneNote


class UI(object):
    class ImageNotFound(Exception):
        pass

    @staticmethod
    def load_image(folder, name_of_file):
        pth = abspath(split(__file__)[0])
        sys.path.append(abspath(join(pth, u"..")))
        fullname = os.path.join(pth, "..", "assets", folder, name_of_file)
        try:
            return pygame.image.load(fullname)
        except:
            raise UI.ImageNotFound


class PlayerUI(object):
    PLAYER_IMAGE_OFFSET = (-30, 0)

    def __init__(self):
        self.player = None
        self.global_images = None
        self.surface = None
        self.image = None

        self.player = Player()
        self.create_surface_and_image()
        self.bag_ui = BagUI()

    def render(self, display):
        self.surface.fill((255, 255, 255))
        self.surface.blit(self.image, PlayerUI.PLAYER_IMAGE_OFFSET)

        display.blit(self.surface, self.get_position())

    def create_surface_and_image(self):
        self.create_surface_with_factor()
        self.create_image_with_factor()

    def create_surface_with_factor(self):
        surface_proportions = self.player.get_surface_proportions()
        self.surface = pygame.Surface(surface_proportions)
        self.surface.convert()
        self.surface.set_colorkey((0, 128, 128))

    def create_image_with_factor(self):
        self.image = UI.load_image("player", "player.png")
        img_proportions = self.get_image_proportions()
        self.image = pygame.transform.scale(self.image, img_proportions)

    def get_position(self):
        return self.player.position

    def get_image_proportions(self):
        return int(round(Player.SCALING_FACTOR * self.image.get_width())), \
            int(round(Player.SCALING_FACTOR * self.image.get_height()))

    def move_player(self, mouse_pos, display):
        self.player.move(mouse_pos, display)

    def is_bag_visible(self):
        return self.bag_ui.visible

    def show_bag(self):
        self.bag_ui.show_bag(self.player)

    def draw_bag(self, display):
        self.bag_ui.render(display)

    def hide_bag(self):
        self.bag_ui.hide_bag()

    def add_item(self, item):
        self.player.add_item(item)


class BagUI(object):
    BACKGROUND_COLOR = (0, 51, 0)

    def __init__(self):
        pygame.font.init()
        self.visible = False
        self.surface = pygame.Surface((800, 500))
        self.items_text = []
        self.item_font = pygame.font.SysFont("comicsansms", 72)

    def show_bag(self, player):
        self.visible = True
        self.build_item_text(player.bag)

    def render(self, display):
        self.surface.fill(self.BACKGROUND_COLOR)
        y = 0
        for text in self.items_text:
            self.surface.blit(text, (0, y))
            y += 50
        display.blit(self.surface, (100, 100))

    def build_item_text(self, bag):
        for item in bag:
            item_text = self.item_font.render(item.get_name(), True, (0, 100, 0))
            self.items_text.append(item_text)

    def is_text_item_empty(self):
        return len(self.items_text) == 0

    def hide_bag(self):
        self.visible = False
        self.items_text = []


class NoteUI(object):
    def __init__(self, parent_container):
        assert parent_container is not None
        self.item = TelephoneNote(parent_container)
        self.surface = pygame.Surface((150, 200))
        self.image = UI.load_image("prolog", "letter.png")
        self.position = (300, 100)

    def render(self, display):
        self.surface.blit(self.image, (0, 0))
        display.blit(self.surface, self.position)
