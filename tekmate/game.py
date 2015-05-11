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
            return item1.get_inspect_message()
        return item1.get_look_at_message()

    def use_item(self, item1):
        return item1.get_use_message()

    def move(self, mouse_pos, display):
        if self.is_mouse_pos_clicked_is_furthest_right(mouse_pos, display):
            new_x = display.get_width() - self.get_surface_width()
        else:
            difference = mouse_pos[0] - self.position[0]
            new_x = self.position[0] + difference
        self.position = new_x, self.position[1]

    def get_surface_proportions(self):
        return round(self.get_surface_width()), \
            round(self.get_surface_height())

    def is_mouse_pos_clicked_is_furthest_right(self, pos, display):
        return display.get_width() - pos[0] < self.get_surface_width()

    def get_surface_width(self):
        return self.SURFACE_WIDTH*self.SCALING_FACTOR

    def get_surface_height(self):
        return self.SCALING_FACTOR*self.SURFACE_HEIGHT
