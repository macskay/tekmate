# -*- encoding: utf-8 -*-
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
        self.name = "Name"
        self.look_at_message = "Look at"
        self.inspect_message = "Inspect"
        self.use_message = "Use"
        self.use_not_usable_message = "Not Usable"
        self.unique_attributes = {}
        self.setup()
        self.fill_attributes()

    def setup(self):  # pragma: no cover
        pass

    def fill_attributes(self):
        attributes = load_item_data(self.name)
        if attributes is not None:
            for key, value in attributes.items():
                if key == "obtainable":
                    self.obtainable = True
                elif key == "look_at":
                    self.look_at_message = value
                elif key == "inspect":
                    self.inspect_message = value
                elif key == "usable":
                    self.usable = True
                elif key == "use":
                    self.use_message = value
                elif key == "use_not_usable":
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

    def change_look_at_message(self, other, new_look_at_key):
        attributes = load_item_data(other.get_name())
        for key, value in attributes.items():
            if key == new_look_at_key:
                other.look_at_message = value


class Paperclip(Item):
    def setup(self):
        self.name = "Paperclip"

    def combine(self, other):
        if other.get_name() != "Door":
            raise Item.InvalidCombination
        if not other.unique_attributes["combined_with_letter"]:
            raise Item.ConditionNotMet
        self.remove_from_parent_container()
        key_item = next((item for item in other.parent_container if item.get_name() == "Key"))
        key_item.obtainable = True
        other.unique_attributes["combined_with_paperclip"] = True


class Key(Item):
    def setup(self):
        self.name = "Key"

    def combine(self, other):
        if not other.get_name() == "Door":
            raise self.InvalidCombination
        other.usable = True
        self.remove_from_parent_container()


class IdCard(Item):
    class AccessDenied(Exception):
        pass

    def setup(self):
        self.unique_attributes["key_code"] = 0
        self.obtainable = True
        self.name = "ID-Card"

    def combine(self, other):
        if self.has_insufficient_permissions(other):
            raise IdCard.AccessDenied
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

    def combine(self, other):
        if other.get_name() != "ID-Card":
            raise Item.InvalidCombination
        other.unique_attributes["key_code"] += 1


class Note(Item):
    def setup(self):
        self.obtainable = True
        self.name = "Note"

    def combine(self, other):
        if other.get_name() != "Symbols-Folder":
            raise Item.InvalidCombination

        self.add_telephone_note_to_player_bag()
        self.remove_from_parent_container()

    def add_telephone_note_to_player_bag(self):
        player_bag = self.parent_container
        tel_note = self.create_telephone_note(player_bag)
        player_bag.append(tel_note)

    def create_telephone_note(self, player_bag):
        return TelephoneNote(player_bag)


class TelephoneNote(Item):
    def setup(self):
        self.name = "Telephone-Note"


class Telephone(Item):
    def setup(self):
        self.name = "Telephone"

    def combine(self, other):
        if other.get_name() != "Telephone-Note":
            raise Item.InvalidCombination
        other.remove_from_parent_container()


class Letter(Item):
    def setup(self):
        self.obtainable = True
        self.name = "Letter"

    def is_combination_possible(self, other):
        if other.get_name() != "Door":
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
