# -*- encoding: utf-8 -*-


class Player(object):
    class NoSuchItem(Exception):
        pass

    def __init__(self):
        self.bag = []

    def add_item(self, item):
        self.bag.append(item)

    def trigger_item_combination(self, item1, item2):
        item1.combine(item2)
        item2.combine(item1)


class Item(object):
    class InvalidCombination(Exception):
        pass

    def __init__(self, parent_container):
        assert parent_container is not None
        self.parent_container = parent_container
        self.obtainable = False

    def combine(self, other):
        self.combine_with(other)

    def combine_with(self, other):  # pragma: no cover
        pass

    def remove_from_parent_container(self):
        self.parent_container.remove(self)

    def get_name(self):
        return "Item"


class Needle(Item):
    def get_name(self):
        return "Needle"

    def combine_with(self, other):
        if other.get_name() != "Lock":
            raise Item.InvalidCombination
        self.remove_from_parent_container()


"""
class Lock(Item):
    pass


class Key(Item):
    pass
"""