# -*- encoding: utf-8 -*-
from unittest import TestCase

try:  # pragma: no cover
    from unittest.mock import Mock, patch
except ImportError:  # pragma: no cover
    from mock import Mock, patch

from pygame import Surface
from tekmate.game import Player
from tekmate.items import Item


class PlayerTestCase(TestCase):
    def setUp(self):
        self.player = Player()

        self.create_obtainable_item()
        self.create_usable_item()
        self.create_invalid_items()

    def create_obtainable_item(self):
        self.obtainable_item = Item([])
        self.obtainable_item.obtainable = True

    def create_usable_item(self):
        self.usable_item = Item([])
        self.usable_item.usable = True

    def create_invalid_items(self):
        self.not_usable_item = Item([])
        self.not_obtainable_item = Item([])

    def test_player_position_defaults_at_zero_zero(self):
        self.assertEqual(self.player.position, (0, 0))

    def test_when_position_to_move_is_right_of_player_move_player_right(self):
        self.player.position = (300, 0)
        mouse_pos = (500, 0)
        self.player.move(mouse_pos, Surface((1920, 1080)))
        self.assertEqual(self.player.position, mouse_pos)

    def test_when_position_to_move_is_left_of_player_move_player_left(self):
        self.player.position = (300, 0)
        mouse_pos = (100, 0)
        self.player.move(mouse_pos, Surface((1920, 1080)))
        self.assertEqual(self.player.position, mouse_pos)

    def test_when_clicked_to_move_right_and_x_pos_is_further_than_screen_width_minus_player_surface_width_force_x(self):
        mock_surface = Surface((640, 480))
        mouse_pos = (600, 0)

        self.player.move(mouse_pos, mock_surface)
        expected_x = int(mock_surface.get_width() - (self.player.SCALING_FACTOR*self.player.SURFACE_WIDTH))
        self.assertEqual(self.player.position, (expected_x, 0))

    def test_when_when_picking_up_not_obtainable_item_raise_exception_and_size_of_bag_should_be_one(self):
        self.assertRaises(Item.NotObtainable, self.player.add_item, self.not_obtainable_item)
        self.assertEqual(len(self.player.bag), 0)

    def test_when_picking_up_obtainable_item_size_of_bag_should_be_one(self):
        self.player.add_item(self.obtainable_item)
        self.assertEqual(len(self.player.bag), 1)

    def test_when_picking_up_obtainable_item_parent_container_should_be_changed_to_bag(self):
        self.player.add_item(self.obtainable_item)
        self.assertIs(self.obtainable_item.parent_container, self.player.bag)

    def test_when_using_not_usable_item_raise_exception(self):
        self.assertRaises(Item.NotUsable, self.player.use_item, self.not_usable_item)

    def test_when_using_usable_item_use_message_should_be_returned(self):
        self.assertEqual("Use Item", self.player.use_item(self.usable_item))

    def test_when_looked_at_item_in_room_look_at_message_should_be_returned(self):
        self.assertEqual("This is an Item", self.player.look_at(self.obtainable_item))

    def test_when_looked_at_item_in_bag_description_should_be_returned(self):
        self.player.add_item(self.obtainable_item)
        self.assertEqual("This is the Item-Description", self.player.look_at(self.obtainable_item))

    def test_when_trigger_item_combination_is_called_item_combine_functions_are_called(self):
        mock_item1 = Mock(spec=Item)
        mock_item2 = Mock(spec=Item)
        self.player.trigger_item_combination(mock_item1, mock_item2)
        mock_item1.combine.assert_called_with(mock_item2)
        mock_item2.combine.assert_called_with(mock_item1)

