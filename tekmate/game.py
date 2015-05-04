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
        return item1.get_look_message()

    def use_item(self, item1):
        return item1.get_use_message()


class Item(object):
    class NotUsable(Exception):
        pass

    class InvalidCombination(Exception):
        pass

    def __init__(self, parent_container):
        assert parent_container is not None
        self.usable = False
        self.obtainable = False
        self.parent_container = parent_container
        self.name = "Item"
        self.unique_attributes = {}
        self.setup()

    def setup(self):  # pragma: no cover
        pass

    def combine(self, other):
        self.combine_with(other)

    def combine_with(self, other):  # pragma: no cover
        pass

    def remove_from_parent_container(self):
        self.parent_container.remove(self)

    def get_name(self):
        return self.name

    def get_look_message(self):
        return "This is an Item"

    def get_use_message(self):
        if not self.usable:
            raise Item.NotUsable
        return "Use Item"

