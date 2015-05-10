# -*- encoding: utf-8 -*-


class Item(object):
    class NotUsable(Exception):
        pass

    class NotObtainable(Exception):
        pass

    class InvalidCombination(Exception):
        pass

    class ConditionNotMet(Exception):
        pass

    def __init__(self, parent_container):
        assert parent_container is not None
        parent_container.append(self)
        self.usable = False
        self.obtainable = False
        self.parent_container = parent_container
        self.name = "Item"
        self.looked_at = False
        self.unique_attributes = {}
        self.setup()

    def setup(self):  # pragma: no cover
        pass

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
        return "This is an Item"

    def get_use_message(self):
        if not self.usable:
            raise Item.NotUsable
        return "Use Item"

    def get_description(self):
        return "This is the Item-Description"


class Paperclip(Item):
    def get_name(self):
        return "Paperclip"

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
    def get_name(self):
        return "Key"

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

    def get_name(self):
        return "ID-Card"

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

    def get_name(self):
        return "Door"


class CardReader(Item):
    class NotAnIdCard(Exception):
        pass

    def get_name(self):
        return "Card-Reader"

    def combine(self, other):
        if other.get_name() != "ID-Card":
            raise CardReader.NotAnIdCard
        other.unique_attributes["key_code"] += 1


class SymbolsFolder(Item):
    def get_name(self):
        return "Symbols-Folder"


class Note(Item):
    def setup(self):
        self.obtainable = True

    def get_name(self):
        return "Note"

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
        self.obtainable = True

    def get_name(self):
        return "Telephone-Note"

    def get_look_at_message(self):
        return "This is a Telephone Note"


class Telephone(Item):
    def get_name(self):
        return "Telephone"

    def combine(self, other):
        if other.get_name() != "Telephone-Note":
            raise Item.InvalidCombination
        other.remove_from_parent_container()


class Letter(Item):
    def setup(self):
        self.obtainable = True

    def get_name(self):
        return "Letter"

    def combine(self, other):
        if other.get_name() != "Door":
            raise Item.InvalidCombination
        if not other.looked_at:
            raise Item.ConditionNotMet
        self.remove_from_parent_container()
        other.unique_attributes["combined_with_letter"] = True

