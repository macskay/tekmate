# -*- encoding: utf-8 -*-


class Player(object):
    class NoSuchItem(Exception):
        pass

    def __init__(self):
        self.bag = []

    def add_item(self, item):
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
