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


class WorldSceneSetupTestCase(TestCase):
    def setUp(self):
        pygame.display.init()
        pygame.display.set_mode((640, 480))
        self.world_scene = WorldScene("world")

    def test_when_mouse_button_is_pressed_function_should_return_true(self):
        class MockEvent:
            pos = (130, 200)
            button = 1
            type = pygame.MOUSEBUTTONDOWN
            pygame.key = None
        event = MockEvent()
        self.assertTrue(self.world_scene.left_mouse_button_pressed(event))
        self.assertFalse(self.world_scene.escape_key_pressed(event))

    def test_when_escape_key_pressed_function_should_return_true(self):
        class MockEvent:
            pos = None
            button = None
            type = pygame.KEYDOWN
            key = pygame.K_ESCAPE
        event = MockEvent()
        self.assertFalse(self.world_scene.left_mouse_button_pressed(event))
        self.assertTrue(self.world_scene.escape_key_pressed(event))