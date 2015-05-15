# -*- encoding: utf-8 -*-
from glob import glob

from os.path import join, splitext, abspath, split
import pygame
from pytmx.util_pygame import load_pygame
import sys
from taz.game import Game
from tekmate.game import Map

from tekmate.scenes import WorldScene
from tekmate.ui import DoorUI, LetterUI, BackgroundUI


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
            "get_events": pygame.event.get,
            "maps": MapLoader().map_dict
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


class MapLoader(object):
    def __init__(self):
        self.map_dict = dict()
        self.tmx_dict = dict()
        self.fill_tmx()
        self.create_maps()

    def fill_tmx(self):
        pth = abspath(split(__file__)[0])
        sys.path.append(abspath(join(pth, u"..")))
        self.tmx_dict["example"] = load_pygame(join(pth, "..", "assets", "maps", "example.tmx"))

    def create_maps(self):
        for key, value in self.tmx_dict.items():
            new_map = Map(key)
            self.load_objects(value, new_map)
            self.set_map_properties(value, new_map)
            self.map_dict[key] = new_map

    def load_objects(self, tmx, new_map):  # pragma: no cover
        for object_group in tmx.objectgroups:
            if object_group.name == "items":
                new_map.items = self.create_items(object_group)
            elif object_group.name == "waypoints":
                new_map.waypoints = self.create_waypoints(object_group)
            elif object_group.name == "exits":
                new_map.exits = self.create_exits(object_group)

    def create_items(self, items):  # pragma: no cover
        itemui_list = []
        for item in items:
            item_ui = None
            if item.name == "door":
                item_ui = DoorUI()
            elif item.name == "letter":
                item_ui = LetterUI()
            item_ui.rect.move_ip((item.x, item.y))
            itemui_list.append(item_ui)
        return itemui_list

    def create_waypoints(self, waypoints):
        wp_list = []
        for waypoint in waypoints:
            wp_list.append((waypoint.x, waypoint.y))
        return wp_list

    def create_exits(self, exits):
        exit_dict = dict()
        for exit in exits:
            exit_dict[(exit.x, exit.y)] = exit.name
        return exit_dict

    def set_map_properties(self, tmx, new_map):
        self.set_background(new_map, tmx)

    def set_background(self, new_map, tmx):
        background_layer = tmx.get_layer_by_name("background")
        new_map.background = BackgroundUI(background_layer)



