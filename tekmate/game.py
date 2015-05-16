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
        if not item.obtainable:
            raise Item.NotObtainable
        item.parent_container = self.bag
        self.bag.append(item)

    def trigger_item_combination(self, item1, item2):
        item1.combine(item2)
        item2.combine(item1)

    def look_at(self, item1):
        if item1 in self.bag:
            return item1.get_inspect_message()
        return item1.get_look_at_message()


class Map(object):
    def __init__(self, name):
        self.name = name
        self.items = list()
        self.exits = dict()
        self.waypoints = list()
        self.background = None


class Waypoint(object):
    def __init__(self, name):
        self.neighbors = list()
        self.name = name
        self.pos = None
        self.is_spawn = False
        self.height = 32
        self.width = 32