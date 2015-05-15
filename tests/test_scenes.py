# -*- encoding: utf-8 -*-
from unittest import TestCase
from tekmate.items import Door, Letter
from tekmate.ui import NoteUI, ContextMenuUI, DoorUI, LetterUI, PlayerUI, ItemUI

try:
    from unittest import Mock, patch
except ImportError:
    from mock import Mock, patch

import pygame
from taz.game import Game

from tekmate.scenes import WorldScene


class WorldSceneTestCase(TestCase):
    def setUp(self):
        self.game = Mock(spec=Game)
        self.scene = WorldScene("world")
        self.scene.game = self.game

    def create_context_menu_setup(self):
        self.scene.display = pygame.Surface((1, 1))
        self.scene.process_right_mouse_pressed((0, 0))
        self.scene.handle_opened_context_menu((10, 10))

    def mock_up_event(self, eventtype, eventkey=None, eventbutton=None):
        mock_event = Mock(spec=pygame.event.EventType)
        mock_event.type = eventtype
        mock_event.key = eventkey
        mock_event.button = eventbutton
        update_context = {
            "get_events": lambda: [mock_event]
        }
        render_context = {
            "player_ui": None
        }
        self.game.update_context = update_context
        self.game.render_context = render_context

    def create_mouse_mock(self, button_nr):
            class MockEvent:
                pos = (150, 200)
                button = button_nr
                type = pygame.MOUSEBUTTONDOWN
                pygame.key = None

            return MockEvent()

    def assertRaisesSystemExit(self):
        with self.assertRaises(SystemExit):
            self.scene.update()

    def test_should_exit_the_game_on_pygame_QUIT(self):
        self.mock_up_event(pygame.QUIT)
        self.assertRaisesSystemExit()

    def test_should_exit_game_on_escape_key(self):
        self.mock_up_event(pygame.KEYDOWN, eventkey=pygame.K_ESCAPE)
        self.assertRaisesSystemExit()

    def test_context_menu_not_none_by_default(self):
        self.assertIsNotNone(self.scene.context_menu)

    def test_world_space_sprite_group_not_none_by_default(self):
        self.assertIsNotNone(self.scene.default_group)

    def test_when_right_mouse_pressed_return_true(self):
        mock_event = self.create_mouse_mock(3)
        self.assertTrue(self.scene.is_right_mouse_pressed(mock_event))

    def test_when_left_mouse_pressed_return_true(self):
        mock_event = self.create_mouse_mock(1)
        self.assertTrue(self.scene.is_left_mouse_pressed(mock_event))

    def test_when_opening_context_menu_it_is_in_the_worlds_scene_group(self):
        self.scene.display = pygame.Surface((1, 1))
        self.scene.process_right_mouse_pressed((10, 10))
        self.assertIn(self.scene.context_menu, self.scene.context_group)

    def test_when_clicked_on_other_than_menu_close_menu(self):
        self.create_context_menu_setup()
        self.assertNotIn(self.scene.context_menu, self.scene.default_group)

    def test_when_sright_clicked_select_correct_context_menu(self):
        note = NoteUI()
        note.rect.topleft = (0, 0)
        self.scene.item_group.add(note)
        self.scene.select_correct_context_menu_list((10, 10))
        self.assertEqual(self.scene.context_menu.surface.get_height(), 90)

    def test_when_right_mouse_is_pressed_open_context_menu(self):
        mock_event = self.create_mouse_mock(3)
        self.scene.handle_input(mock_event)
        self.assertIn(self.scene.context_menu, self.scene.context_group)

    def test_when_left_mouse_is_pressed_somewhere_other_than_context_menu_close_context_menu(self):
        self.scene.process_right_mouse_pressed((100, 210))
        mock_event = self.create_mouse_mock(1)
        self.scene.handle_input(mock_event)
        self.assertNotIn(self.scene.context_menu, self.scene.default_group)

    def test_when_left_mouse_is_pressed_without_context_menu_open_move_player(self):
        pygame.display.set_mode((1920, 1080))
        mock_event = self.create_mouse_mock(1)
        self.scene.process_left_mouse_button_pressed(mock_event)
        self.assertEqual(self.scene.player_ui.rect.centerx, mock_event.pos[0])

    def test_when_use_item_is_called_return_use_message_of_item(self):
        self.scene.current_observed_item = NoteUI()
        self.assertEqual(self.scene.use_item(), "I can't use that!")

    def test_when_look_at_item_is_called_return_look_at_message_of_item(self):
        self.scene.current_observed_item = NoteUI()
        self.assertEqual(self.scene.look_at_item(), "This is a Note.")

    def test_when_take_item_is_called_item_gets_transferred_to_bag_and_killed_from_world_sprite_group(self):
        self.scene.current_observed_item = NoteUI()
        self.scene.take_item((10, 10))
        self.assertIn(self.scene.current_observed_item, self.scene.player_ui.bag_sprite_group)

    @patch("tekmate.scenes.WorldScene.get_button_pressed")
    def test_when_processing_a_command_the_respective_message_should_come_back(self, mock_get_button):
        self.scene.current_observed_item = NoteUI()
        self.scene.context_menu.bag_visible = True
        mock_get_button.return_value = "Look at"
        self.scene.process_button_command((1, 1))
        self.assertFalse(self.scene.is_context_menu_visible())

    def test_when_get_button_pressed_called_return_the_text_of_the_button(self):
        self.scene.set_context_menu(ContextMenuUI.CONTEXT_MENU_DEFAULT)
        self.scene.open_context_menu((100, 100))
        self.assertEqual(self.scene.get_button_pressed((1, 71)), "Walk")

    def test_when_combining_items_check_result(self):
        door = DoorUI()
        letter = LetterUI()
        player_ui = Mock()

        self.scene.current_selected_item = letter
        self.scene.current_observed_item = door
        self.scene.player_ui = player_ui
        self.scene.combine_items()
        player_ui.combine_items.assert_called_with(letter, door)

    @patch("tekmate.items.Item.get_name")
    def test_when_select_item_store_current_observerd_item_into_current_selected_item(self, mock_get_name):
        self.scene.current_observed_item = Mock()
        mock_get_name.return_value = "NAME"
        self.scene.select_item()
        self.assertEqual(self.scene.current_selected_item, self.scene.current_observed_item)


class WorldSceneRenderTestCase(TestCase):
    def setUp(self):
        self.scene = WorldScene("world")

    @patch("pygame.sprite.OrderedUpdates.draw")
    def test_render_calls_world_scene_group_render(self, mock_draw):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.scene.game = Mock()
        self.scene.display = pygame.Surface((1, 1))
        self.scene.render()
        mock_draw.assert_called_with(self.scene.display)

    @patch("pygame.sprite.OrderedUpdates.draw")
    def test_render_calls_bag_to_call_if_visible(self, mock_draw):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.scene.game = Mock()
        self.scene.display = pygame.Surface((1, 1))
        self.scene.player_ui.bag_visible = True
        self.scene.render()
        mock_draw.assert_called_with(self.scene.display)


class WorldSceneUpdateTestCase(TestCase):
    def setUp(self):
        self.scene = WorldScene("world")

    def create_mouse_mock(self, button_nr):
        class MockEvent:
            pos = (150, 200)
            button = button_nr
            type = pygame.MOUSEBUTTONDOWN
            pygame.key = None

        return MockEvent()

    def create_key_event(self, key_id):
        class MockEvent:
            key = key_id
            type = pygame.KEYDOWN
            pygame.key = None

        return MockEvent()

    def test_render_calls_world_scene_group_update(self):
        self.scene.game = Mock()
        mock_event = self.create_mouse_mock(1)
        self.scene.game.update_context = {"get_events": lambda: [mock_event]}
        self.scene.update()
        self.assertEqual(self.scene.player_ui.rect.centerx, mock_event.pos[0])

    def test_when_i_pressed_handle_bag(self):
        self.scene.game = Mock()
        mock_event = self.create_key_event(pygame.K_i)
        self.scene.game.update_context = {"get_events": lambda: [mock_event]}
        self.scene.update()
        self.assertTrue(self.scene.player_ui.is_bag_visible())

    def test_when_i_pressed_close_bag_if_open(self):
        self.scene.game = Mock()
        mock_event = self.create_key_event(pygame.K_i)
        self.scene.game.update_context = {"get_events": lambda: [mock_event]}
        self.scene.player_ui.bag_visible = True
        self.scene.update()
        self.assertFalse(self.scene.player_ui.is_bag_visible())
