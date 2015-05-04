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


class Needle(Item):
    def get_name(self):
        return "Needle"

    def combine_with(self, other):
        if other.get_name() != "Lock":
            raise Item.InvalidCombination
        self.remove_from_parent_container()
        key_item = next((item for item in other.parent_container if item.get_name() == "Key"))
        key_item.obtainable = True


class Lock(Item):
    def get_name(self):
        return "Lock"


class Key(Item):
    def get_name(self):
        return "Key"


class IdCard(Item):
    class AccessDenied(Exception):
        pass

    def setup(self):
        self.unique_attributes["key_code"] = 0

    def get_name(self):
        return "ID-Card"

    def combine_with(self, other):
        if self.has_insufficient_permissions(other):
            raise IdCard.AccessDenied
        other.usable = True

    def has_insufficient_permissions(self, other):
        return other.unique_attributes["access_code"] != self.unique_attributes["key_code"]


class Door(Item):
    def setup(self):
        self.unique_attributes["access_code"] = 0

    def get_name(self):
        return "Door"


class CardReader(Item):
    class NotAnIdCard(Exception):
        pass

    def get_name(self):
        return "Card-Reader"

    def combine_with(self, other):
        if other.get_name() != "ID-Card":
            raise CardReader.NotAnIdCard
        other.unique_attributes["key_code"] += 1