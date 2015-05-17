# -*- encoding: utf-8 -*-
from abc import abstractmethod, ABCMeta
import os
from os.path import abspath, join
from os.path import split

import pygame
from pygameanimation.animation import Animation
import sys

from tekmate.game import Player
from tekmate.items import Note, Door, Letter
from tekmate.pathfinding import AStar


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
        fullname = os.path.join(pth, "..", "..", "assets", folder, name_of_file+".png")
        return pygame.image.load(fullname)

    @staticmethod
    def is_new_pos_hiding_current_object_at_right_side(pos, width):
        return pos[0] + width > pygame.display.get_surface().get_width()

    @staticmethod
    def is_new_pos_hiding_current_object_at_left_side(pos, width):
        return pos[0] - width < 0

    @staticmethod
    def is_new_pos_hiding_current_object_at_bottom(pos, height):
        return pos[1] + height > pygame.display.get_surface().get_height()

    @staticmethod
    def new_pos_hides_menu_on_right_bottom_side(pos, width, height):
        return UI.is_new_pos_hiding_current_object_at_bottom(pos, height) and \
            UI.is_new_pos_hiding_current_object_at_right_side(pos, width)


class PlayerUI(pygame.sprite.Sprite):
    COLOR_KEY = (0, 128, 128)

    PLAYER_SUBSURFACE_SIZE = (40, 90)
    SCALING_FACTOR = 1.5

    TEXT_COLOR = (0, 153, 255)

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
        self.rect.move_ip(self.player.position)

        self.waypoints = None

    def set_image(self):
        image = self.asset.subsurface(pygame.Rect((10, 0), PlayerUI.PLAYER_SUBSURFACE_SIZE))
        image = pygame.transform.scale(image, self.get_image_proportions(image))
        image.set_colorkey(PlayerUI.COLOR_KEY)
        return image

    def get_image_proportions(self, image):
        return int(round(PlayerUI.SCALING_FACTOR * image.get_width())), \
            int(round(PlayerUI.SCALING_FACTOR * image.get_height()))

    def move(self, dest_pos):
        dest_x = dest_pos[0] - self.rect.width + self.rect.width
        dest_y = dest_pos[1] - self.rect.height
        ani = Animation(x=dest_x, y=dest_y, duration=500, round_values=True, transition='out_sine')
        return ani

    def add_item(self, item_ui):  # pragma: no cover
        self.player.add_item(item_ui.item)
        item_ui.kill()
        self.bag_sprite_group.add(item_ui)

        item_ui.rect.topleft = (self.bag_background.rect.x + 100, self.bag_background.rect.y + 50)

    def is_bag_visible(self):
        return self.bag_visible

    def combine_items(self, item_selected, item_observed):
        if item_selected.item.is_combination_possible(item_observed.item):
            self.player.trigger_item_combination(item_selected.item, item_observed.item)
            item_selected.kill()

    def get_position(self):
        return self.rect

    def find_shortest_path_to_destination(self, pos):
        start_node = self.get_start_node()
        end_node = self.get_closest_node_to_pos(pos)

        a_star = AStar(self.waypoints, start_node, end_node)
        best_path = a_star.find_shortest_path()
        return best_path

    def get_start_node(self):
        start_node = None
        for name, waypoint in self.waypoints.items():
            if self.rect.bottomleft == waypoint.pos:
                start_node = waypoint
            else:
                start_node = self.get_closest_node_to_pos(
                    self.rect.bottomleft)  # TODO: THIS NEEDS TO DIJKSTRA TO NOT WALK BACKWARDS
        return start_node

    def get_closest_node_to_pos(self, pos):
        smallest_path = 999999
        smallest_node = None
        for name, waypoint in self.waypoints.items():
            euclid = AStar.calculate_euclidean_distance(waypoint.pos, pos)
            if euclid < smallest_path:
                smallest_path = euclid
                smallest_node = waypoint
        return smallest_node

    def find_spawn(self):
        for name, waypoint in self.waypoints.items():
            if waypoint.is_spawn:
                self.set_player_start(waypoint)

    def set_player_start(self, waypoint):
        self.rect.bottomleft = waypoint.pos


class ContextMenuUI(pygame.sprite.Sprite):
    class InvalidLayout(Exception):
        pass

    BACKGROUND_COLOR = (190, 190, 190)
    TEXT_COLOR = (50, 50, 50)
    CONTEXT_MENU_DEFAULT = ["Walk"]
    CONTEXT_MENU_ITEM = ["Look at", "Take", "Use"]
    CONTEXT_MENU_BAG_ITEM = ["Inspect", "Select"]
    CONTEXT_COMBINE_ITEM = ["Combine"]

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

    # noinspection PyArgumentList
    def build_context_menu(self, layout):
        self.current_layout = layout
        new_height = ContextMenuUI.MENU_ITEM_HEIGHT * len(layout)
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
        height = ContextMenuUI.MENU_ITEM_HEIGHT * len(self.current_layout)
        if UI.is_new_pos_hiding_current_object_at_bottom(pos, height):
            self.rect.bottomleft = pos
        if UI.is_new_pos_hiding_current_object_at_right_side(pos, width):
            self.rect.topright = pos
        if UI.new_pos_hides_menu_on_right_bottom_side(pos, width, height):
            self.rect.bottomright = pos

    def get_button_pressed(self, pos):
        y = self.rect.y + ContextMenuUI.MENU_ITEM_HEIGHT
        for elem in self.current_layout:
            if y > pos[1]:
                return elem
            y += ContextMenuUI.MENU_ITEM_HEIGHT
        raise ContextMenuUI.InvalidLayout

    def get_pos(self):
        return self.rect.topleft


class BagBackground(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = UI.load_image("global", "bag").convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(PlayerUI.COLOR_KEY)
        self.rect.center = (
            pygame.display.get_surface().get_width() // 2, pygame.display.get_surface().get_height() // 2)


class ItemUI(pygame.sprite.Sprite):
    __metaclass__ = ABCMeta

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = None
        self.item = None
        self.setup()

    @abstractmethod
    def setup(self):
        pass

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


class NoteUI(ItemUI):
    def setup(self):
        self.image = UI.load_image("items", "note")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.item = Note([])


class DoorUI(ItemUI):
    def setup(self):
        self.image = UI.load_image("items", "door")
        self.image = pygame.transform.scale(self.image, (64, 96))
        self.rect = self.image.get_rect()
        self.item = Door([])


class LetterUI(ItemUI):
    def setup(self):
        self.image = UI.load_image("items", "note")
        self.image = pygame.transform.scale(self.image, (32, 64))
        self.rect = self.image.get_rect()
        self.item = Letter([])


class BackgroundUI(pygame.sprite.Sprite):
    def __init__(self, background):
        pygame.sprite.Sprite.__init__(self)
        path = os.path.split(background.source)
        self.image = UI.load_image(path[0][3:], path[1][:-4])
        self.rect = self.image.get_rect()
