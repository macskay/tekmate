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

    WRONG_COMBINATION = "I can't do that!"

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
        self.add_message = "ADD"
        self.add_not_obtainable_message = "NOT OBTAINABLE"
        self.unique_attributes = {}
        self.is_split_needed = False
        self.visible = True
        self.setup()
        self.fill_attributes()

    def setup(self):  # pragma: no cover
        pass

    def fill_attributes(self):
        value = ""
        actions = {
            "obtainable": lambda: partial(self.set_obtainable, value),
            "look_at": lambda: partial(self.set_look_at, value),
            "usable": lambda: partial(self.set_usable, value),
            "use": lambda: partial(self.set_use_message, value),
            "use_not_usable": lambda: partial(self.set_use_not_usable_message, value),
            "inspect": lambda: partial(self.set_inspect, value),
            "split_needed": lambda: partial(self.set_split_needed, value),
            "add": lambda: partial(self.set_add_message, value),
            "add_not_obtainable": lambda: partial(self.set_add_not_obtainable_message, value)
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

    def set_split_needed(self, value):
        self.is_split_needed = value

    def set_add_message(self, value):
        self.add_message = value

    def set_add_not_obtainable_message(self, value):
        self.add_not_obtainable_message = value

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

    def get_add_message(self):
        if not self.obtainable:
            return self.add_not_obtainable_message
        return self.add_message

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

    def get_combination_message(self, other, combination_error):
        attributes = load_item_data(other.get_name())
        for key, value in attributes.items():
            if key == combination_error:  # pragma: no cover (nothing happens when the key is not found)
                return value



class Paperclip(Item):
    def setup(self):
        self.name = "Paperclip"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Door"):
            return False, Item.WRONG_COMBINATION
        if not other.looked_at:
            return False, self.get_combination_message(other, "combination_paperclip_not_looked_at")
        if not other.unique_attributes["combined_with_letter"]:
            return False, self.get_combination_message(other, "combination_letter_not_under_door")
        return True, self.get_combination_message(self, "combinate")

    def combine(self, other):
        self.remove_from_parent_container()
        letter_under_door = next((item_ui for item_ui in other.parent_container if item_ui.get_name() == "LetterUnderDoor"))
        letter_under_door.item.obtainable = True

        other.unique_attributes["combined_with_paperclip"] = True
        self.change_look_at_message(other, "look_at_when_key_obtainable")

class Key(Item):
    def setup(self):
        self.name = "Key"
        self.visible = False

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Door"):
            return False, Item.WRONG_COMBINATION
        return True, self.get_combination_message(self, "combinate")

    def combine(self, other):
        other.usable = True
        self.remove_from_parent_container()

        self.change_look_at_message(other, "look_at_door_unlocked")



class IdCard(Item):
    class AccessDenied(Exception):
        pass

    def setup(self):
        self.unique_attributes["key_code"] = 0
        self.obtainable = True
        self.name = "ID-Card"

    def is_combination_possible(self, other):
        if self.has_insufficient_permissions(other):
            return False, Item.WRONG_COMBINATION
        return True, None

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
            return False, Item.WRONG_COMBINATION
        return True, None

    def combine(self, other):
        other.unique_attributes["key_code"] += 1


class Note(Item):
    def setup(self):
        self.obtainable = True
        self.name = "Note"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Symbols-Folder"):
            return False, Item.WRONG_COMBINATION
        return True, None

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
            return False, Item.WRONG_COMBINATION
        return True, None

    def combine(self, other):
        other.remove_from_parent_container()


class Letter(Item):
    def setup(self):
        self.name = "Letter"

    def is_combination_possible(self, other):
        if self.is_wrong_combination(other, "Door"):
            return False, Item.WRONG_COMBINATION
        if not other.looked_at:
            return False, self.get_combination_message(other, "combination_letter_not_looked_at")
        return True, self.get_combination_message(self, "combinate")

    def combine(self, other):
        self.remove_from_parent_container()
        other.unique_attributes["combined_with_letter"] = True
        letter_under_door = next((item_ui for item_ui in other.parent_container
                                  if item_ui.get_name() == "LetterUnderDoor"))

        letter_under_door.item.visible = True
        self.change_look_at_message(other, "look_at_after_letter")


class LetterUnderDoor(Item):
    def setup(self):
        self.visible = False
        self.name = "LetterUnderDoor"

class SymbolsFolder(Item):
    def setup(self):
        self.name = "Symbols-Folder"
