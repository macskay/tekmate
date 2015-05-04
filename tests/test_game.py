# -*- encoding: utf-8 -*-
from collections import namedtuple

from unittest import TestCase
from unittest.mock import Mock

from tekmate.game import Player, Item


class PlayerTestCase(TestCase):
    def setUp(self):
        self.player = Player()
        self.item1 = Item([])
        self.item2 = Item([])

    def test_when_item_is_added_size_of_bag_equals_one(self):
        self.player.add_item(self.item1)
        self.assertEqual(len(self.player.bag), 1)

    def test_if_player_can_force_item_combination(self):
        mock_item1 = Mock(spec=Item)
        mock_item2 = Mock(spec=Item)
        self.player.trigger_item_combination(mock_item1, mock_item2)
        mock_item1.combine.assert_called_with(mock_item2)
        mock_item2.combine.assert_called_with(mock_item1)

    def test_when_item_picked_up_parent_container_is_bag(self):
        self.player.add_item(self.item1)
        self.assertIs(self.item1.parent_container, self.player.bag)

    def test_when_used_and_not_usable_raise_exception(self):
        self.assertRaises(Item.NotUsable, self.player.use_item, self.item1)

    def test_when_used_and_usable_get_use_message(self):
        self.item1.usable = True
        self.assertEqual("Use Item", self.player.use_item(self.item1))

    def test_when_looked_at_get_look_message(self):
        self.assertEqual("This is an Item", self.player.look_at(self.item1))


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

