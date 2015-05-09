# -*- encoding: utf-8 -*-
from unittest import TestCase

try:
    from unittest import Mock
except ImportError:
    from mock import Mock

import pygame
from taz.game import Game

from tekmate.scenes import WorldScene


class WorldSceneUpdateTestCase(TestCase):
    def setUp(self):
        self.game = Mock(spec=Game)
        self.scene = WorldScene("world")
        self.scene.game = self.game

    def mock_up_event(self, eventtype, eventkey=None):
        mock_event = Mock(spec=pygame.event.EventType)
        mock_event.type = eventtype
        mock_event.key = eventkey
        update_context = {
            "get_events": lambda: [mock_event]
        }
        render_context = {
            "player_ui": None
        }
        self.game.update_context = update_context
        self.game.render_context = render_context

    def assertRaisesSystemExit(self):
        with self.assertRaises(SystemExit):
            self.scene.update()

    def test_should_exit_the_game_on_pygame_QUIT(self):
        self.mock_up_event(pygame.QUIT)
        self.assertRaisesSystemExit()

    def test_should_exit_game_on_escape_key(self):
        self.mock_up_event(pygame.KEYDOWN, pygame.K_ESCAPE)
        self.assertRaisesSystemExit()

    def test_when_pressed_i_bag_visible_true(self):
        self.mock_up_event(pygame.KEYDOWN, pygame.K_i)
        self.scene.initialize_scene()
        self.scene.player_ui.show_bag()
        self.assertTrue(self.scene.is_bag_visible())



class WorldSceneSetupTestCase(TestCase):
    def setUp(self):
        pygame.display.init()
        pygame.display.set_mode((640, 480))
        self.world_scene = WorldScene("world")

    def create_key_mock(self, key_pressed):
        class MockEvent:
            pos = None
            button = None
            type = pygame.KEYDOWN
            key = key_pressed
        return MockEvent()

    def create_mouse_mock(self):
        class MockEvent:
            pos = (130, 200)
            button = 1
            type = pygame.MOUSEBUTTONDOWN
            pygame.key = None
        return MockEvent()

    def test_when_mouse_button_is_pressed_function_should_return_true(self):
        event = self.create_mouse_mock()
        self.assertTrueTrueFalse(self.world_scene.left_mouse_button_pressed(event),
                                 self.world_scene.escape_key_pressed(event),
                                 self.world_scene.i_pressed(event))

    def test_when_escape_key_pressed_function_should_return_true(self):
        event = self.create_key_mock(pygame.K_ESCAPE)
        self.assertTrueTrueFalse(self.world_scene.escape_key_pressed(event),
                                 self.world_scene.left_mouse_button_pressed(event),
                                 self.world_scene.i_pressed(event))

    def test_when_i_key_pressed_draw_bag(self):
        event = self.create_key_mock(pygame.K_i)
        self.assertTrueTrueFalse(self.world_scene.i_pressed(event),
                                 self.world_scene.left_mouse_button_pressed(event),
                                 self.world_scene.escape_key_pressed(event))

    def assertTrueTrueFalse(self, evt1, evt2, evt3):
        self.assertTrue(evt1)
        self.assertFalse(evt2)
        self.assertFalse(evt3)

    def test_show_bag_should_make_bag_ui_visible(self):
        self.world_scene.initialize_scene()
        self.world_scene.show_bag()
        self.assertTrue(self.world_scene.is_bag_visible())

    def setup_mock_game(self):
        mock_game = Mock()
        mock_game.render_context = {"display": 0}
        self.world_scene.game = mock_game
        return mock_game

    def setup_mock_player_ui(self):
        mock_player_ui = Mock()
        self.world_scene.player_ui = mock_player_ui
        return mock_player_ui

    def test_draw_bag_should_call_player_uis_draw_bag(self):
        mock_player_ui = self.setup_mock_player_ui()
        mock_game = self.setup_mock_game()

        self.world_scene.draw_bag()
        mock_player_ui.draw_bag.assert_called_with(mock_game.render_context["display"])

    def test_hide_bag_should_make_bag_visible_false(self):
        self.world_scene.initialize_scene()
        self.world_scene.hide_bag()
        self.assertFalse(self.world_scene.is_bag_visible())
