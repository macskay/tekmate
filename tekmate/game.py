# -*- encoding: utf-8 -*-

from tekmate.items import Item


class Player(object):
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

    def move_player(self, mouse_pos):
        if mouse_pos[0] < self.position[0]:
            x = -100
        else:
            x = 100
        self.position = (self.position[0] + x, self.position[1])

class NPC(object):
    def __init__(self):
        self.position = (0, 0)
        self.default_response_message = "Hello, I'm an NPC"