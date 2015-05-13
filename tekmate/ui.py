# -*- encoding: utf-8 -*-
import sys

import os
from os.path import abspath, split, join
import pygame
from tekmate.game import Player
from tekmate.items import Note


class UI(object):
    class ImageNotFound(Exception):
        pass

    @staticmethod
    def load_image(folder, name_of_file):
        try:
            return UI.try_loading_image(folder, name_of_file)
        except:
            raise UI.ImageNotFound

    @staticmethod
    def try_loading_image(folder, name_of_file):
        pth = abspath(split(__file__)[0])
        sys.path.append(abspath(join(pth, u"..")))
        fullname = os.path.join(pth, "..", "assets", folder, name_of_file+".png")
        return pygame.image.load(fullname)

    @staticmethod
    def is_new_pos_hiding_current_object_at_right_side(pos, width):
        return pos[0]+width > pygame.display.get_surface().get_width()

    @staticmethod
    def is_new_pos_hiding_current_object_at_left_side(pos, width):
        return pos[0]-width < 0

    @staticmethod
    def is_new_pos_hiding_current_object_at_bottom(pos, height):
        return pos[1]+height > pygame.display.get_surface().get_height()

    @staticmethod
    def new_pos_hides_menu_on_right_bottom_side(pos, width, height):
        return UI.is_new_pos_hiding_current_object_at_bottom(pos, height) and \
            UI.is_new_pos_hiding_current_object_at_right_side(pos, width)


class PlayerUI(pygame.sprite.Sprite):
    COLOR_KEY = (0, 128, 128)

    PLAYER_SUBSURFACE_SIZE = (50, 100)
    SCALING_FACTOR = 2.8

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.asset = UI.load_image("global", "player")
        self.image = self.set_image()
        self.rect = self.image.get_rect()
        self.bag_sprite_group = pygame.sprite.OrderedUpdates()

        self.bag_background = BagBackground()
        self.bag_sprite_group.add(self.bag_background)

        self.player = Player()

        self.bag_visible = False

    def set_image(self):
        image = self.asset.subsurface(pygame.Rect((0, 0), PlayerUI.PLAYER_SUBSURFACE_SIZE))
        image = pygame.transform.scale(image, self.get_image_proportions(image))
        image.set_colorkey(PlayerUI.COLOR_KEY)
        return image

    def get_image_proportions(self, image):
        return int(round(PlayerUI.SCALING_FACTOR * image.get_width())), \
            int(round(PlayerUI.SCALING_FACTOR * image.get_height()))

    def move(self, mouse_pos):
        self.rect.centerx = mouse_pos[0]
        if UI.is_new_pos_hiding_current_object_at_right_side(mouse_pos, self.rect.width):
            self.rect.right = mouse_pos[0]
        if UI.is_new_pos_hiding_current_object_at_left_side(mouse_pos, self.rect.width):
            self.rect.left = 0

    def add_item(self, item_ui):
        self.player.add_item(item_ui.item)
        item_ui.kill()
        self.bag_sprite_group.add(item_ui)

        item_ui.rect.topleft = (self.bag_background.rect.x+100, self.bag_background.rect.y+50)

    def is_bag_visible(self):
        return self.bag_visible


class ContextMenuUI(pygame.sprite.Sprite):
    class InvalidLayout(Exception):
        pass

    BACKGROUND_COLOR = (190, 190, 190)
    TEXT_COLOR = (50, 50, 50)
    CONTEXT_MENU_DEFAULT = ["Walk"]
    CONTEXT_MENU_ITEM = ["Look at", "Take", "Use"]
    CONTEXT_MENU_BAG_ITEM = ["Inspect", "Select"]

    MENU_ITEM_HEIGHT = 30
    MENU_ITEM_WIDTH = 100

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        pygame.font.init()
        self.surface = None
        self.current_layout = None
        self.font = pygame.font.SysFont("arial", 25)

        self.build_context_menu(ContextMenuUI.CONTEXT_MENU_DEFAULT)

        self.image = self.surface
        self.rect = self.image.get_rect()

    def build_context_menu(self, layout):
        self.current_layout = layout
        new_height = ContextMenuUI.MENU_ITEM_HEIGHT*len(layout)
        self.surface = pygame.Surface((ContextMenuUI.MENU_ITEM_WIDTH, new_height))
        self.fill_up_context_menu_with_text(layout)

    def fill_up_context_menu_with_text(self, layout):
        self.surface.fill(ContextMenuUI.BACKGROUND_COLOR)
        y = 0
        for item in layout:
            text = self.font.render(item, True, ContextMenuUI.TEXT_COLOR)
            self.surface.blit(text, (0, y))
            y += ContextMenuUI.MENU_ITEM_HEIGHT
        self.image = self.surface
        self.rect = self.image.get_rect()

    def open(self, pos):
        self.rect.topleft = pos

        width = ContextMenuUI.MENU_ITEM_WIDTH
        height = ContextMenuUI.MENU_ITEM_HEIGHT
        if UI.is_new_pos_hiding_current_object_at_bottom(pos, height):
            self.rect.bottomleft = pos
        if UI.is_new_pos_hiding_current_object_at_right_side(pos, width):
            self.rect.topright = pos
        if UI.new_pos_hides_menu_on_right_bottom_side(pos, width, height):
            self.rect.bottomright = pos

    def get_button_pressed(self, pos):
        y = self.rect.y+ContextMenuUI.MENU_ITEM_HEIGHT
        for elem in self.current_layout:
            if y > pos[1]:
                return elem
            y += ContextMenuUI.MENU_ITEM_HEIGHT
        else:
            raise ContextMenuUI.InvalidLayout

    def get_pos(self):
        return self.rect.topleft


class BagBackground(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = UI.load_image("global", "bag").convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(PlayerUI.COLOR_KEY)
        self.rect.center = (pygame.display.get_surface().get_width()//2, pygame.display.get_surface().get_height()//2)


class NoteUI(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = UI.load_image("items", "note")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()

        self.rect.topleft = (800, 100)

        self.item = Note([])

    def look_at(self):
        return self.item.get_look_at_message()

    def use(self):
        return self.item.get_use_message()

    def inspect(self):
        return self.item.get_inspect_message()

    def is_obtainable(self):
        return self.item.obtainable

    def is_usable(self):
        return self.item.usable
