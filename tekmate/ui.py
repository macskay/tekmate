# -*- encoding: utf-8 -*-
import sys

import os
from os.path import abspath, split, join
import pygame


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

    def open(self, pos, display):
        self.rect.topleft = pos
        if self.new_pos_hides_menu_at_bottom(pos, display):
            self.rect.bottomleft = pos
        if self.new_pos_hides_menu_on_right_side(pos, display):
            self.rect.topright = pos
        if self.new_pos_hides_menu_on_right_bottom_side(pos, display):
            self.rect.bottomright = pos

    def new_pos_hides_menu_on_right_side(self, pos, display):
        return ContextMenuUI.MENU_ITEM_WIDTH > display.get_width()-pos[0]

    def new_pos_hides_menu_at_bottom(self, pos, display):
        return ContextMenuUI.MENU_ITEM_HEIGHT > display.get_height()-pos[1]

    def new_pos_hides_menu_on_right_bottom_side(self, pos, display):
        return self.new_pos_hides_menu_at_bottom(pos, display) and \
            self.new_pos_hides_menu_on_right_side(pos, display)

    def get_button_pressed(self, pos):
        y = self.rect.y+ContextMenuUI.MENU_ITEM_HEIGHT
        for elem in self.current_layout:
            if y > pos[1]:
                return elem
            y += ContextMenuUI.MENU_ITEM_HEIGHT
        else:
            raise ContextMenuUI.InvalidLayout
