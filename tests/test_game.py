# -*- encoding: utf-8 -*-
from unittest import TestCase

import pygame

try:  # pragma: no cover
    from unittest.mock import Mock, patch
except ImportError:  # pragma: no cover
    from mock import Mock, patch

from tekmate.game import Player, PyGameInitializer, TekmateFactory, WorldScene
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

    def test_when_moved_player_in_positive_x_position_should_be_hundred_zero(self):
        self.player.move_player((300, 150))
        self.assertEqual(self.player.position, (100, 0))

    def test_when_moved_player_in_negative_x_position_should_be_minus_hundred_zero(self):
        self.player.move_player((-100, 150))
        self.assertEqual(self.player.position, (-100, 0))

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


class PyGameInitializerTestCase(TestCase):
    def setUp(self):
        self.conf = {"display_width": 640, "display_height": 480}
        self.pygame_initializer = PyGameInitializer(self.conf)
        self.pygame_patcher = patch("tekmate.game.pygame", spec=True)
        self.pygame = self.pygame_patcher.start()
        self.uc, self.rc = self.pygame_initializer.initialize()

    def test_can_create_pygame_initializer(self):
        self.assertIsNotNone(self.pygame_initializer.configuration)

    def test_initialze_pygame_actually_initializes_pygame(self):
        self.pygame.init.assert_called_with()

    def test_initialize_pygame_sets_the_caption(self):
        self.pygame.display.set_caption.assert_called_with(PyGameInitializer.CAPTION)

    def test_initialize_pygame_sets_window_resoultion_correctly_from_conf(self):
        self.pygame.display.set_mode.assert_called_with((640, 480))

    def test_when_initialize_mouse_is_getting_configured_correctly(self):
        self.pygame.mouse.set_visible.assert_called_with(True)

    def test_update_context_should_have_a_clock(self):
        self.assertTrue(hasattr(self.uc["clock"], "tick"))

    def test_update_context_should_have_get_event_reference(self):
        self.assertIs(self.uc["get_events"], self.pygame.event.get)

    def test_render_context_should_have_flip_function(self):
        self.assertIs(self.rc["flip"], self.pygame.display.flip)

    def test_render_context_should_main_surface_reference(self):
        self.assertIs(self.rc["display"], self.pygame.display.get_surface())


class TekmateFactoryTestCase(TestCase):
    def setUp(self):
        mock_init = Mock(spec=PyGameInitializer)
        mock_scene = Mock(spec=WorldScene)
        mock_init.initialize.return_value = None, {}

        self.set_up_display()

        self.mock_init = mock_init
        self.mock_scene = mock_scene

    def set_up_display(self):
        pygame.display.init()
        pygame.display.set_mode((1, 1))

    def assertSceneRegistered(self, identifier, class_type):
        game = TekmateFactory(self.mock_init).create()
        scene = game.registered_scenes[identifier]
        self.assertIsInstance(scene, class_type)

    def test_create_should_initialize_pygame(self):
        game = TekmateFactory(self.mock_init).create()
        self.mock_init.initialize.assert_called_with()

    def test_create_should_add_world_scene_to_game(self):
        self.assertSceneRegistered("world", WorldScene)

    def test_create_should_push_world_scene_to_game(self):
        game = TekmateFactory(self.mock_init).create()
        self.assertEqual(game.get_name_of_top_scene(), "world")