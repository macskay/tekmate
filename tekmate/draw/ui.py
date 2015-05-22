# -*- encoding: utf-8 -*-
from abc import abstractmethod, ABCMeta
import os
from os.path import abspath, join
from os.path import split
import sys

import pygame
from pygameanimation.animation import Animation

from tekmate.game import Player
from tekmate.items import Door, Letter, Paperclip, Key, LetterUnderDoor
from tekmate.pathfinding import AStar


class UI(object):
    class ImageNotFound(Exception):
        pass

    COLOR_KEY = (0, 128, 128)

    WALK_EVENT = pygame.USEREVENT+2
    CROUCH_EVENT = pygame.USEREVENT+3
    CROUCH_DELAY_EVENT = pygame.USEREVENT+4

    STOP_CROUCH_EVENT = pygame.USEREVENT+5

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
        return pygame.image.load(fullname).convert()

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
    PLAYER_SUBSURFACE_WIDTH = 50
    PLAYER_SUBSURFACE_HEIGHT = 90
    SCALING_FACTOR = 1.5

    TEXT_COLOR = (0, 153, 255)

    IDLE = (0, 0)
    WALK = (1, 0)
    CROUCH = (0, 1)

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.direction = 1
        self.asset = UI.load_image("global", "player")
        self.image = None
        self.set_image(PlayerUI.IDLE)
        self.rect = self.image.get_rect()
        self.bag_sprite_group = pygame.sprite.OrderedUpdates()

        self.bag_background = BagBackground()
        self.bag_sprite_group.add(self.bag_background)

        self.player = Player()

        self.bag_visible = False
        self.rect.move_ip(self.player.position)

        self.waypoints = None

        self.current_image_index = 0
        self.is_walking = False
        self.is_crouching = False
        self.is_waiting_for_crouch = False

    def set_image(self, action):
        surface_size = (PlayerUI.PLAYER_SUBSURFACE_WIDTH, PlayerUI.PLAYER_SUBSURFACE_HEIGHT)
        image = self.asset.subsurface(pygame.Rect(self.get_image_tile(action), surface_size))
        image = pygame.transform.scale(image, self.get_image_proportions(image))
        image.set_colorkey(UI.COLOR_KEY)
        if self.is_direction_left():
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def get_image_tile(self, action):
        return action[0]*PlayerUI.PLAYER_SUBSURFACE_WIDTH, action[1]*PlayerUI.PLAYER_SUBSURFACE_HEIGHT

    def get_image_proportions(self, image):
        return int(round(PlayerUI.SCALING_FACTOR * image.get_width())), \
            int(round(PlayerUI.SCALING_FACTOR * image.get_height()))

    def is_direction_left(self):
        return self.direction == -1

    def move(self, dest_pos):
        dest_x = dest_pos[0] - self.rect.width + self.rect.width
        dest_y = dest_pos[1] - self.rect.height
        ani = Animation(x=dest_x, y=dest_y, duration=750, round_values=True, transition='in_out_sine')
        return ani

    def add_item(self, item_ui, map_items):
        if self.player.add_item(item_ui.item):
            self.trigger_item_pick_up_animation(item_ui)
            self.hide_item_from_world_when_in_bag(item_ui)
            self.add_splitted_items_to_bag(item_ui) if self.item_has_to_be_split(item_ui) \
                else self.add_item_to_ui_bag(item_ui)
            map_items.remove(item_ui)
        return item_ui.item.get_add_message()

    def trigger_item_pick_up_animation(self, item_ui):
        if item_ui.get_name() == "LetterUnderDoor":
            pygame.time.set_timer(UI.CROUCH_EVENT, 100)
            pygame.time.set_timer(UI.STOP_CROUCH_EVENT, 400)

    def item_has_to_be_split(self, item_ui):
        return item_ui.item.is_split_needed

    def add_splitted_items_to_bag(self, item):
        new_items = self.split_up_item(item)

        self.loop_through_all_items_and_add_them(new_items)

    def loop_through_all_items_and_add_them(self, new_items):
        x = 100
        y = 50
        for item_ui in new_items:
            self.player.add_item(item_ui.item)
            self.bag_sprite_group.add(item_ui)
            item_ui.rect.topleft = (self.bag_background.rect.x + x, self.bag_background.rect.y + y)
            x += 100

    def hide_item_from_world_when_in_bag(self, item_ui):
        item_ui.kill()

    def add_item_to_ui_bag(self, item_ui):
        self.bag_sprite_group.add(item_ui)
        item_ui.rect.topleft = (self.bag_background.rect.x + 100, self.bag_background.rect.y + 50)

    def split_up_item(self, item_ui):
        return item_ui.split()

    def is_bag_visible(self):
        return self.bag_visible

    def combine_items(self, item_selected, item_observed):
        is_combination_possible, reason = item_selected.item.is_combination_possible(item_observed.item)
        if is_combination_possible:
            self.player.trigger_item_combination(item_selected.item, item_observed.item)
            item_selected.kill()

            if item_selected.is_animation_triggered:
                self.trigger_item_animation(item_selected)
        return reason

    def trigger_item_animation(self, item):
        if item.get_name() == "Letter":
            pygame.time.set_timer(UI.CROUCH_EVENT, 100)
            pygame.time.set_timer(UI.STOP_CROUCH_EVENT, 400)

    def get_position(self):
        return self.rect

    def find_shortest_path_to_destination(self, pos, direction):
        self.direction = direction
        start_node = self.get_start_node()
        end_node = self.get_closest_node_to_pos(pos)

        a_star = AStar(self.waypoints, start_node, end_node)
        best_path = a_star.find_shortest_path()
        return best_path

    def get_start_node(self):
        start_node = None
        for  waypoint in self.waypoints.values():
            if self.rect.bottomleft == waypoint.pos:
                start_node = waypoint
            else:
                # TODO: THIS NEEDS TO DIJKSTRA TO NOT WALK BACKWARDS
                start_node = self.get_closest_node_to_pos(self.rect.bottomleft)
        return start_node

    def get_closest_node_to_pos(self, pos):
        smallest_path = 999999
        smallest_node = None
        for  waypoint in self.waypoints.values():
            euclid = AStar.calculate_euclidean_distance(waypoint.pos, pos)
            if euclid < smallest_path:
                smallest_path = euclid
                smallest_node = waypoint
        return smallest_node

    def find_spawn(self):
        for waypoint in self.waypoints.values():
            if waypoint.is_spawn:
                self.set_player_start(waypoint)

    def set_player_start(self, waypoint):
        self.rect.bottomleft = waypoint.pos

    def animate_walk(self):
        self.is_walking = True
        self.current_image_index += 1
        if self.current_image_index >= 6:
            self.current_image_index = 0

    def animate_crouch(self):
        self.is_crouching = True
        self.current_image_index += 1
        if self.current_image_index >= 4:
            self.current_image_index = 0

    def update(self):
        new_image = PlayerUI.IDLE
        if self.is_walking:
            new_image = (PlayerUI.WALK[0]+self.current_image_index, PlayerUI.WALK[1])
        elif self.is_crouching:
            new_image = (PlayerUI.CROUCH[0]+self.current_image_index, PlayerUI.CROUCH[1])
        self.set_image(new_image)

    def reset_walk(self):
        self.is_walking = False
        self.set_image(PlayerUI.IDLE)

    def reset_crouch(self):
        self.is_crouching = False
        self.set_image(PlayerUI.IDLE)

    def face_target(self, target):
        if target.rect.left < self.rect.left:
            self.direction = -1
        else:
            self.direction = 1


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
        self.image.set_colorkey(UI.COLOR_KEY)
        self.rect.center = (
            pygame.display.get_surface().get_width() // 2, pygame.display.get_surface().get_height() // 2)


class ItemUI(pygame.sprite.Sprite):
    __metaclass__ = ABCMeta

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = None
        self.rect = None
        self.item = None
        self.is_animation_triggered = False
        self.setup()

    @abstractmethod
    def setup(self):
        pass

    def split(self):
        pass

    def post_animation_behavior(self):
        pass

    def look_at(self):
        return self.item.get_look_at_message()

    def use(self):
        return self.item.get_use_message()

    def inspect(self):
        return self.item.get_inspect_message()

    def get_add_message(self):
        return self.item.get_add_message()

    def is_obtainable(self):
        return self.item.obtainable

    def is_usable(self):
        return self.item.usable

    def get_name(self):
        return self.item.name

    def load_image(self, name):
        self.image = UI.load_image("items", name)
        self.image.set_colorkey(UI.COLOR_KEY)
        self.rect = self.image.get_rect()


class NoteUI(ItemUI):
    def setup(self):
        self.load_image("note")


class DoorUI(ItemUI):
    def setup(self):
        self.load_image("door")
        self.item = Door([])


class LetterUI(ItemUI):
    def setup(self):
        self.load_image("letter")
        self.item = Letter([])
        self.is_animation_triggered = True

    def change_to_letter_without_paperclip(self):
        self.load_image("letter_no_paperclip")

    def split(self):
        self.change_to_letter_without_paperclip()
        return PaperclipUI(), self


class PaperclipUI(ItemUI):
    def setup(self):
        self.load_image("paperclip")
        self.item = Paperclip([])
        self.is_animation_triggered = True


class KeyUI(ItemUI):
    def setup(self):
        self.load_image("key")
        self.item = Key([])


class LetterUnderDoorUI(ItemUI):
    def setup(self):
        self.load_image("letter_under_door")
        self.item = LetterUnderDoor([])

    def split(self):
        return [KeyUI()]


class BackgroundUI(pygame.sprite.Sprite):
    def __init__(self, background):
        pygame.sprite.Sprite.__init__(self)
        path = os.path.split(background.source)
        self.image = UI.load_image(path[0][3:], path[1][:-4])
        self.rect = self.image.get_rect()
