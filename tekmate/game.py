# -*- encoding: utf-8 -*-
from tekmate.items import Item


class Player(object):
    SURFACE_WIDTH = 40
    SURFACE_HEIGHT = 100
    SCALING_FACTOR = 2.8

    class NoSuchItem(Exception):
        pass

    def __init__(self):
        self.position = (0, 400)
        self.bag = []

    def add_item(self, item):
        return False if not item.obtainable else self.add_item_to_bag(item)

    def add_item_to_bag(self, item):
        item.parent_container = self.bag
        self.bag.append(item)

        return True

    def trigger_item_combination(self, item1, item2):
        item1.combine(item2)
        item2.combine(item1)

    def look_at(self, item1):
        return item1.get_look_at_message() if item1 not in self.bag else item1.get_inspect_message()


class Map(object):
    def __init__(self, name):
        self.name = name
        self.items = list()
        self.exits = dict()
        self.waypoints = dict()
        self.background = None

    def set_items_parent_container(self):
        for item_ui in self.items:
            item_ui.parent_container = self.items


class Waypoint(object):
    def __init__(self, name):
        self.neighbors = dict()
        self.name = name
        self.pos = None
        self.is_spawn = False
        self.height = 32
        self.width = 32
