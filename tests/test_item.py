# -*- encoding: utf-8 -*-
from unittest import TestCase
from mock import patch

from tekmate.game import Player
from tekmate.items import Item, Key, IdCard, Door, CardReader, Note, SymbolsFolder, TelephoneNote, \
    Telephone, Paperclip, Letter


class ItemTestCase(TestCase):
    def setUp(self):
        self.container = []
        self.item = Item(self.container)

    def test_can_create_item(self):
        self.assertEqual("Name", self.item.get_name())

    def test_when_created_item_should_be_inside_parent_container(self):
        self.assertIn(self.item, self.item.parent_container)

    def test_not_obtainable_by_default(self):
        self.assertFalse(self.item.obtainable)

    def test_not_usable_by_default(self):
        self.assertFalse(self.item.usable)

    def test_looked_at_door_variable_status(self):
        self.assertEqual(self.item.looked_at, False)
        self.item.looked_at = True
        self.assertEqual(self.item.looked_at, True)

    def test_when_player_use_unusable_item_raise_exception(self):
        self.item.usable = False
        self.assertRaises(Item.NotUsable, self.item.get_use_message)

    def test_when_parent_container_is_none_AssertionError_is_raised(self):
        with self.assertRaises(AssertionError):
            Item(None)

    def test_can_combine(self):
        item = self.item

        class MockItem(Item):
            def __init__(self, parent_container):
                super(MockItem, self).__init__(parent_container)
                self.called = False

            def combine(self, other):
                self.called = other is item

        mock_item = MockItem([])
        mock_item.combine(self.item)
        self.assertTrue(mock_item.called)

    def test_when_remove_from_container_parent_container_loses_item(self):
        self.item.remove_from_parent_container()
        self.assertNotIn(self.item, self.container)

    def test_when_add_to_container_container_should_change(self):
        container_new = []
        self.item.move_to_container(container_new)
        self.assertIn(self.item, container_new)
        self.assertNotIn(self.item, self.container)

    def test_when_looking_at_item_looked_at_must_be_true(self):
        self.item.get_look_at_message()
        self.assertTrue(self.item.looked_at)

    def test_when_inspecting_an_item_return_inspect_message(self):
        self.assertEqual(self.item.get_inspect_message(), "Inspect")

    @patch("tekmate.items.load_item_data")
    def test_when_filling_attributes_values_are_set_correctly(self, mock_item_load_data):
        mock_item_load_data.return_value = {u'use': u'USE',
                                            u'inspect': u'INSPECT',
                                            u'look_at': u'LOOK_AT',
                                            u'usable': u'USABLE',
                                            u'obtainable': u'OBTAINABLE'}
        self.item.fill_attributes()
        self.assertEqual(self.item.get_use_message(), "USE")
        self.assertEqual(self.item.inspect_message, "INSPECT")
        self.assertEqual(self.item.get_look_at_message(), "LOOK_AT")
        self.assertTrue(self.item.usable)
        self.assertTrue(self.item.obtainable)

        mock_item_load_data.return_value = {"false": "entry"}
        self.assertRaises(Item.InvalidInput, self.item.fill_attributes)


class PaperclipTestCase(TestCase):
    def setUp(self):
        self.container = []
        self.world_container = []
        self.paperclip = Paperclip(self.container)
        self.key = Key(self.world_container)
        self.door = Door(self.world_container)
        self.door.unique_attributes["combined_with_letter"] = True

    def test_can_create_paperclip(self):
        self.assertEqual("Paperclip", self.paperclip.get_name())

    def test_when_combined_with_other_than_door_raise_invalid_combination(self):
        obj = Item([])
        with self.assertRaises(Item.InvalidCombination):
            self.paperclip.combine(obj)

    def test_gets_consumed_when_combined_correctly_with_door(self):
        self.paperclip.combine(self.door)
        self.assertNotIn(self.paperclip, self.container)

    def test_when_combined_correctly_key_is_obtainable(self):
        self.paperclip.combine(self.door)
        self.assertTrue(self.key.obtainable)

    def test_when_combining_with_door_and_doors_combined_with_letter_is_false_raise_exception(self):
        self.door.unique_attributes["combined_with_letter"] = False
        self.assertRaises(Item.ConditionNotMet, self.paperclip.combine, self.door)

    def test_when_combined_with_door_correctly_set_combined_with_paperclip_True(self):
        self.paperclip.combine(self.door)
        self.assertTrue(self.door.unique_attributes["combined_with_paperclip"])


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
        self.assertRaises(Item.InvalidCombination, self.reader.combine, any_item)


class NoteTestCase(TestCase):
    def setUp(self):
        self.folder = SymbolsFolder([])
        self.player = Player()
        self.note = Note(self.player.bag)

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

    def test_can_create_telephone(self):
        self.assertEqual(self.telephone.get_name(), "Telephone")

    def test_when_combined_with_other_than_telephone_note_raise_exception(self):
        any_item = Item([])
        self.assertRaises(Item.InvalidCombination, self.telephone.combine, any_item)

    def test_when_combined_with_telephone_note_note_gets_consumed(self):
        self.telephone.combine(self.tel_note)
        self.assertNotIn(self.tel_note, self.player.bag)


class LetterTestCase(TestCase):
    def setUp(self):
        self.container = []
        self.letter = Letter(self.container)
        self.world_container = []
        self.key = Key(self.world_container)
        self.door = Door(self.world_container)

    def test_can_create_letter(self):
        self.assertEqual(self.letter.get_name(), "Letter")

    def test_when_letter_combined_other_than_door_raise_exception(self):
        any_item = Item([])
        self.assertRaises(Item.InvalidCombination, self.letter.combine, any_item)

    def test_gets_consumed_when_combined_correctly_with_door(self):
        self.door.looked_at = True
        self.letter.combine(self.door)
        self.assertNotIn(self.letter, self.container)

    def test_when_letter_combined_with_door_and_door_looked_at_is_false_raise_exception(self):
        self.assertRaises(Item.ConditionNotMet, self.letter.combine, self.door)

    def test_doors_combined_with_letter(self):
        self.assertFalse(self.door.unique_attributes["combined_with_letter"])
        self.door.looked_at = True
        self.letter.combine(self.door)
        self.assertTrue(self.door.unique_attributes["combined_with_letter"])


class KeyTestCase(TestCase):
    def setUp(self):
        self.container = []
        self.key = Key(self.container)
        self.door = Door([])

    def test_can_create_key(self):
        self.assertIsInstance(self.key, Key)

    def test_when_key_combined_other_than_door_raise_exception(self):
        any_item = Item([])
        self.assertRaises(Item.InvalidCombination, self.key.combine, any_item)

    def test_when_key_combined_with_door_and_door_not_usable_make_it_usable(self):
        self.key.combine(self.door)
        self.assertEqual(self.door.usable, True)

    def test_gets_consumed_when_combined_correctly_with_door(self):
        self.door.unique_attributes["combined_with_paperclip"] = True
        self.key.combine(self.door)
        self.assertNotIn(self.key, self.container)


class TelephoneNoteTestCase(TestCase):
    def setUp(self):
        self.tel_note = TelephoneNote([])

    def test_can_create_tel_note(self):
        self.assertEqual(self.tel_note.get_name(), "Telephone-Note")

    def test_get_look_at_message_should_be_telephone_note(self):
        self.assertEqual(self.tel_note.get_look_at_message(), "This is a Telephone-Note.")
