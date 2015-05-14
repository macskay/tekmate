# -*- encoding: utf-8 -*-
from functools import partial
from json import load
import os
from os.path import join, abspath, split
import sys


def load_item_data(name):
    pth = abspath(split(__file__)[0])
    sys.path.append(abspath(join(pth, u"..")))
    items_path = os.path.join(pth, "..", "assets", "global", "item_data.json")
    with open(items_path) as item_file:
        items_data = load(item_file)
    for item in items_data:
        if item == name:
            return items_data[item]


class Item(object):
    class NotUsable(Exception):
        pass

    class NotObtainable(Exception):
        pass

    class InvalidCombination(Exception):
        pass

    class ConditionNotMet(Exception):
        pass

    class InvalidInput(Exception):
        pass

    def __init__(self, parent_container):
        assert parent_container is not None
        parent_container.append(self)
        self.parent_container = parent_container
        self.usable = False
        self.obtainable = False
        self.looked_at = False
        self.name = "NAME"
        self.look_at_message = "LOOK_AT"
        self.inspect_message = "INSPECT"
        self.use_message = "USE"
        self.use_not_usable_message = "NOT_USABLE"
        self.unique_attributes = {}
        self.setup()
        self.fill_attributes()

    def setup(self):  # pragma: no cover
        pass

    def fill_attributes(self):
        actions = {
            "obtainable": lambda: partial(self.set_obtainable, value),
            "look_at": lambda: partial(self.set_look_at, value),
            "usable": lambda: partial(self.set_usable, value),
            "use": lambda: partial(self.set_use_message, value),
            "use_not_usable": lambda: partial(self.set_use_not_usable_message, value),
            "inspect": lambda: partial(self.set_inspect, value)
        }
        attributes = load_item_data(self.name)
        if attributes is not None:
            for key, value in attributes.items():
                if key in actions.keys():
                    actions[key]()()

    def set_obtainable(self, value):
        self.obtainable = value

    def set_look_at(self, value):
        self.look_at_message = value

    def set_usable(self, value):
        self.usable = value

    def set_inspect(self, value):
        self.inspect_message = value

    def set_use_message(self, value):
        self.use_message = value

    def set_use_not_usable_message(self, value):
        self.use_not_usable_message = value

    def combine(self, other):  # pragma: no cover
        pass

    def remove_from_parent_container(self):
        self.parent_container.remove(self)

    def move_to_container(self, new_container):
        new_container.append(self)
        self.remove_from_parent_container()
        self.parent_container = new_container

    def get_name(self):
        return self.name

    def get_look_at_message(self):
        self.looked_at = True
        return self.look_at_message

    def get_use_message(self):
        if not self.usable:
            return self.use_not_usable_message
        return self.use_message

    def get_inspect_message(self):
        return self.inspect_message

    def is_combination_possible(self, other):  # pragma: no cover
        pass

    def is_wrong_combination(self, other, name):
        if other.get_name() != name:
            return True
        return False

    def change_look_at_message(self, other, new_look_at_key):
        attributes = load_item_data(other.get_name())
        for key, value in attributes.items():
            if key == new_look_at_key:
                other.look_at_message = value


class Paperclip(Item):
    def setup(self):
        self.name = "Paperclip"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Door"):
            return False
        if not other.unique_attributes["combined_with_letter"]:
            return False
        return True

    def combine(self, other):
        self.remove_from_parent_container()
        key_item = next((item for item in other.parent_container if item.get_name() == "Key"))
        key_item.obtainable = True
        other.unique_attributes["combined_with_paperclip"] = True


class Key(Item):
    def setup(self):
        self.name = "Key"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Door"):
            return False
        return True

    def combine(self, other):
        other.usable = True
        self.remove_from_parent_container()


class IdCard(Item):
    class AccessDenied(Exception):
        pass

    def setup(self):
        self.unique_attributes["key_code"] = 0
        self.obtainable = True
        self.name = "ID-Card"

    def is_combination_possible(self, other):
        if self.has_insufficient_permissions(other):
            return False
        return True

    def combine(self, other):
        other.usable = True

    def has_insufficient_permissions(self, other):
        return other.unique_attributes["access_code"] != self.unique_attributes["key_code"]


class Door(Item):
    def setup(self):
        self.unique_attributes["access_code"] = 0
        self.unique_attributes["combined_with_letter"] = False
        self.name = "Door"


class CardReader(Item):
    def setup(self):
        self.name = "Card-Reader"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "ID-Card"):
            return False
        return True

    def combine(self, other):
        other.unique_attributes["key_code"] += 1


class Note(Item):
    def setup(self):
        self.obtainable = True
        self.name = "Note"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Symbols-Folder"):
            return False
        return True

    def combine(self, other):
        self.add_telephone_note_to_player_bag()
        self.remove_from_parent_container()

    def add_telephone_note_to_player_bag(self):
        player_bag = self.parent_container
        tel_note = TelephoneNote(player_bag)
        player_bag.append(tel_note)


class TelephoneNote(Item):
    def setup(self):
        self.name = "Telephone-Note"


class Telephone(Item):
    def setup(self):
        self.name = "Telephone"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Telephone-Note"):
            return False
        return True

    def combine(self, other):
        other.remove_from_parent_container()


class Letter(Item):
    def setup(self):
        self.obtainable = True
        self.name = "Letter"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Door"):
            return False
        if not other.looked_at:
            return False
        return True

    def combine(self, other):
        self.remove_from_parent_container()
        other.unique_attributes["combined_with_letter"] = True
        self.change_look_at_message(other, "look_at_after_letter")


class SymbolsFolder(Item):
    def setup(self):
        self.name = "Symbols-Folder"
