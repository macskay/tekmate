# -*- encoding: utf-8 -*-
from collections import namedtuple

from unittest import TestCase, skip
from unittest.mock import Mock

from tekmate.game import Player, Item, Needle


class ItemTestCase(TestCase):
    def setUp(self):
        self.container = []
        self.item = Item(self.container)
        self.container.append(self.item)

    def test_can_create_item(self):
        self.assertEqual("Item", self.item.get_name())

    def test_not_obtainable_by_default(self):
        self.assertFalse(self.item.obtainable)

    def test_when_parent_container_is_none_AssertionError_is_raised(self):
        with self.assertRaises(AssertionError):
            Item(None)

    def test_can_combine(self):
        item = self.item

        class MockItem(Item):
            def __init__(self):
                self.called = False

            def combine_with(self, other):
                self.called = other is item

        mock_item = MockItem()
        mock_item.combine(self.item)
        self.assertTrue(mock_item.called)

    def test_when_remove_from_container_parent_container_loses_item(self):
        self.item.remove_from_parent_container()
        self.assertNotIn(self.item, self.container)


class NeedleTestCase(TestCase):

    def setUp(self):
        self.container = []
        self.needle = Needle(self.container)
        self.container.append(self.needle)

    def create_mock_item(self, name):
        return namedtuple("MockItem", ["get_name", "obtainable"])(lambda: name, False)

    def test_can_create_needle(self):
        self.assertEqual("Needle", self.needle.get_name())

    def test_when_combined_with_not_a_lock_raise_invalid_combination(self):
        obj = self.create_mock_item("Pink")
        with self.assertRaises(Item.InvalidCombination):
            self.needle.combine(obj)

    def test_gets_consumed_when_combined_correctly(self):
        obj = self.create_mock_item("Lock")
        self.needle.combine(obj)
        self.assertNotIn(self.needle, self.container)

    def test_when_combined_correctly_key_is_obtainable(self):
        obj_lock = self.create_mock_item("Lock")
        obj_key = self.create_mock_item("Key")
        self.needle.combine(obj_lock)
        self.assertTrue(obj_key.obtainable)


class PlayerTestCase(TestCase):
    def setUp(self):
        self.player = Player()
        self.item1 = Item([])
        self.item2 = Item([])

    def test_if_player_can_add_item_to_bag(self):
        self.player.add_item(self.item1)
        self.assertEqual(len(self.player.bag), 1)

    def test_if_player_can_force_item_combination(self):
        mock_item1 = Mock(spec=Item)
        mock_item2 = Mock(spec=Item)
        self.player.trigger_item_combination(mock_item1, mock_item2)
        mock_item1.combine.assert_called_with(mock_item2)
        mock_item2.combine.assert_called_with(mock_item1)
