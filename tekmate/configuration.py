# -*- encoding: utf-8 -*-
from glob import glob
from os.path import join, splitext, abspath, split
import sys

import pygame
from pytmx.util_pygame import load_pygame
from taz.game import Game

from tekmate.game import Map, Waypoint
from tekmate.draw.scenes import WorldScene
from tekmate.draw.ui import DoorUI, LetterUI, BackgroundUI, LetterUnderDoorUI


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
            self.add_image_to_images_dict(image_file, images)
        return images

    def add_image_to_images_dict(self, image_file, images):
        surface = self.load_image_from_hard_drive(image_file)
        name = splitext(image_file)
        images[name[0]] = surface

    def load_image_from_hard_drive(self, image_file):
        surface = pygame.image.load(image_file).convert()
        surface.set_colorkey((0, 128, 128))
        return surface

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
    ITEM_TYPES = {
        "door": DoorUI,
        "letter": LetterUI,
        "letter_under_door": LetterUnderDoorUI
    }

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
            self.load_items(new_map, object_group)
            self.load_waypoints(new_map, object_group)
            self.load_exits(new_map, object_group)

    def load_items(self, new_map, object_group):
        if object_group.name == "items":
            new_map.items = self.create_items(object_group)
            new_map.set_items_parent_container()

    def create_items(self, items):  # pragma: no cover
        items_list = []
        for item in items:
            item_ui = self.create_item_object(item)
            items_list.append(item_ui)
        return items_list

    def create_item_object(self, item):
        item_ui = self.ITEM_TYPES[item.name]()
        item_ui.rect.move_ip((item.x, item.y))
        return item_ui

    def load_waypoints(self, new_map, object_group):
        if object_group.name == "waypoints":
            new_map.waypoints = self.create_waypoints(object_group)
            self.create_neighbors(new_map, object_group)

    def create_waypoints(self, waypoints):
        wp_list = dict()
        for waypoint in waypoints:
            wp = self.create_waypoint_object(waypoint)
            wp_list[waypoint.name] = wp
        return wp_list

    def create_waypoint_object(self, waypoint):
        wp = Waypoint(waypoint.name)
        wp.pos = (waypoint.x, waypoint.y + waypoint.height)
        return wp

    def create_neighbors(self, new_map, object_group):
        for waypoint_of_object_group in object_group:
            waypoint_object = self.get_waypoint_of_map(new_map, waypoint_of_object_group)
            self.setup_waypoint_properties(waypoint_object, waypoint_of_object_group, new_map)

    def setup_waypoint_properties(self, waypoint_object, waypoint_of_object_group, new_map):
        for wp_property in waypoint_of_object_group.properties:
            self.set_waypoint_as_spawn(waypoint_object, wp_property)
            self.add_neighbor_to_waypoint(waypoint_object, waypoint_of_object_group, wp_property, new_map)

    def get_waypoint_of_map(self, new_map, waypoint):
        return new_map.waypoints[waypoint.name]

    def set_waypoint_as_spawn(self, wp, wp_property):
        if wp_property == "spawn":
            wp.is_spawn = True

    def add_neighbor_to_waypoint(self, waypoint_object, waypoint_of_object_group, wp_property, new_map):
        if wp_property == "connect":
            neighbors_array = self.build_neighbors_array(waypoint_of_object_group)
            self.fill_up_neighbors_array_for_wp(neighbors_array, waypoint_object, new_map)

    def build_neighbors_array(self, waypoint):
        return waypoint.properties["connect"].split(", ")

    def fill_up_neighbors_array_for_wp(self, neighbors_array, waypoint_object, new_map):
        for neighbor in neighbors_array:
            waypoint_object.neighbors[neighbor] = new_map.waypoints[neighbor]

    def load_exits(self, new_map, object_group):
        if object_group.name == "exits":
            new_map.exits = self.create_exits(object_group)

    def create_exits(self, exits):
        exit_dict = dict()
        for exit_of_map in exits:
            exit_dict[(exit_of_map.x, exit_of_map.y)] = exit_of_map.name
        return exit_dict

    def set_map_properties(self, tmx, new_map):
        self.set_background(new_map, tmx)

    def set_background(self, new_map, tmx):
        background_layer = tmx.get_layer_by_name("background")
        new_map.background = BackgroundUI(background_layer)
