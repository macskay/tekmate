# -*- encoding: utf-8 -*-
from unittest import TestCase, skip
from tekmate.game import Player

from tekmate.items import Item, Needle, Lock, Key, IdCard, Door, CardReader, Note, SymbolsFolder, TelephoneNote, \
    Telephone


class ItemTestCase(TestCase):
    def setUp(self):
        self.container = []
        self.item = Item(self.container)
        self.container.append(self.item)

    def test_can_create_item(self):
        self.assertEqual("Item", self.item.get_name())

    def test_not_obtainable_by_default(self):
        self.assertFalse(self.item.obtainable)

    def test_not_usable_by_default(self):
        self.assertFalse(self.item.usable)

    def test_when_parent_container_is_none_AssertionError_is_raised(self):
        with self.assertRaises(AssertionError):
            Item(None)

    @skip("TODO")
    def test_can_combine(self):
        item = self.item

        class MockItem(Item):
            def __init__(self, parent_container):
                super().__init__(parent_container)
                self.called = False

            def combine_with(self, other):
                self.called = other is item

        mock_item = MockItem([])
        mock_item.combine(self.item)
        self.assertTrue(mock_item.called)

    def test_when_remove_from_container_parent_container_loses_item(self):
        self.item.remove_from_parent_container()
        self.assertNotIn(self.item, self.container)


class NeedleTestCase(TestCase):

    def setUp(self):
        self.container = []
        self.world_container = []

        self.needle = Needle(self.container)
        self.key = Key(self.world_container)
        self.lock = Lock(self.world_container)

        self.append_items_to_respective_containers()

    def append_items_to_respective_containers(self):
        self.container.append(self.needle)
        self.world_container.append(self.key)
        self.world_container.append(self.lock)

    def test_can_create_needle(self):
        self.assertEqual("Needle", self.needle.get_name())

    def test_when_combined_with_not_a_lock_raise_invalid_combination(self):
        obj = Item([])
        with self.assertRaises(Item.InvalidCombination):
            self.needle.combine(obj)

    def test_gets_consumed_when_combined_correctly(self):
        self.needle.combine(self.lock)
        self.assertNotIn(self.needle, self.container)

    def test_when_combined_correctly_key_is_obtainable(self):
        self.needle.combine(self.lock)
        self.assertTrue(self.key.obtainable)


class IdCardTestCase(TestCase):
    def setUp(self):
        self.idcard = IdCard([])
        self.door = Door([])

    def test_can_create_id_card(self):
        self.assertEqual("ID-Card", self.idcard.get_name())

    def test_key_code_is_defaulted_at_zero(self):
        self.assertEqual(0, self.idcard.unique_attributes["key_code"])

    def test_id_card_can_open_door(self):
        self.idcard.combine(self.door)
        self.assertTrue(self.door.usable)

    def test_when_combined_with_door_and_insufficient_permissions_raise_Access_Denied(self):
        self.door.unique_attributes["access_code"] = 1
        self.assertRaises(IdCard.AccessDenied, self.idcard.combine, self.door)


class DoorTestCase(TestCase):
    def setUp(self):
        self.door = Door([])

    def test_can_create_door(self):
        self.assertEqual("Door", self.door.get_name())

    def test_access_code_is_defaulted_at_zero(self):
        self.assertEqual(0, self.door.unique_attributes["access_code"])


class CardReaderTestCase(TestCase):
    def setUp(self):
        self.reader = CardReader([])

    def test_can_create_card_reader(self):
        self.assertEqual("Card-Reader", self.reader.get_name())

    def test_when_combined_with_id_card_increase_key_code(self):
        idcard = IdCard([])
        self.reader.combine(idcard)
        self.assertEqual(idcard.unique_attributes["key_code"], 1)

    def test_when_combined_with_other_than_a_card_raise_exception(self):
        any_item = Item([])
        self.assertRaises(CardReader.NotAnIdCard, self.reader.combine, any_item)


class NoteTestCase(TestCase):
    def setUp(self):
        self.folder = SymbolsFolder([])
        self.player = Player()
        self.note = Note(self.player.bag)
        self.player.add_item(self.note)

    def test_can_create_note(self):
        self.assertEqual("Note", self.note.get_name())

    def test_when_combined_with_other_than_the_symbol_folder_raise_exception(self):
        any_item = Item([])
        self.assertRaises(Item.InvalidCombination, self.note.combine, any_item)

    def test_when_combined_with_symbol_folder_remove_note_from_player_bag(self):
        self.note.combine(self.folder)
        self.assertNotIn(self.note, self.player.bag)

    def test_when_combined_with_symbol_folder_note_telephone_should_be_added_to_player_bag(self):
        self.note.combine(self.folder)
        self.assertEqual(self.player.bag[0].get_name(), "Telephone-Note")


class TelephoneTestCase(TestCase):
    def setUp(self):
        self.telephone = Telephone([])
        self.setup_player_bag()

    def setup_player_bag(self):
        self.player = Player()
        self.tel_note = TelephoneNote(self.player.bag)
        self.player.add_item(self.tel_note)

    def test_can_create_telephone(self):
        self.assertEqual(self.telephone.get_name(), "Telephone")

    def test_when_combined_with_other_than_telephone_note_raise_exception(self):
        any_item = Item([])
        self.assertRaises(Item.InvalidCombination, self.telephone.combine, any_item)

    def test_when_combined_with_telephone_note_note_gets_consumed(self):
        self.telephone.combine(self.tel_note)
        self.assertNotIn(self.tel_note, self.player.bag)
