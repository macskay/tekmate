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
        context = {
            "get_events": lambda: [mock_event]
        }
        self.game.update_context = context

    def assertRaisesSystemExit(self):
        with self.assertRaises(SystemExit):
            self.scene.update()

    def test_should_exit_the_game_on_pygame_QUIT(self):
        self.mock_up_event(pygame.QUIT)
        self.assertRaisesSystemExit()

    def test_should_exit_game_on_escape_key(self):
        self.mock_up_event(pygame.KEYDOWN, pygame.K_ESCAPE)
        self.assertRaisesSystemExit()
