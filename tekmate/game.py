# -*- encoding: utf-8 -*-
from tekmate.items import Item


class Player(object):
    SURFACE_WIDTH = 40
    SURFACE_HEIGHT = 100
    SCALING_FACTOR = 2.8

    class NoSuchItem(Exception):
        pass

    def __init__(self):
        self.position = (0, 0)
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

    def move(self, mouse_pos):
        difference = mouse_pos[0] - self.position[0]
        if abs(difference) < self.get_surface_proportions()[0]:
            return
        new_x = self.position[0] + difference
        self.position = new_x, self.position[1]

    def get_surface_proportions(self):
        return round(self.SCALING_FACTOR * self.SURFACE_WIDTH), \
            round(self.SCALING_FACTOR * self.SURFACE_HEIGHT)
