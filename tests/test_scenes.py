# -*- encoding: utf-8 -*-
from unittest import TestCase

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
        self.scene.display = pygame.display.get_surface()
        self.scene.open_context_menu((0, 0))
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
                pos = (130, 200)
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
        self.assertIsNotNone(self.scene.world_scene_sprite_group)

    def test_when_right_mouse_pressed_return_true(self):
        mock_event = self.create_mouse_mock(3)
        self.assertTrue(self.scene.right_mouse_pressed(mock_event))

    def test_when_left_mouse_pressed_return_true(self):
        mock_event = self.create_mouse_mock(1)
        self.assertTrue(self.scene.left_mouse_pressed(mock_event))

    def test_when_opening_context_menu_it_is_in_the_worlds_scene_group(self):
        self.scene.display = pygame.display.get_surface()
        self.scene.open_context_menu((10, 10))
        self.assertIn(self.scene.context_menu, self.scene.world_scene_sprite_group)

    def test_when_clicked_on_other_than_menu_close_menu(self):
        self.create_context_menu_setup()
        self.assertNotIn(self.scene.context_menu, self.scene.world_scene_sprite_group)

    def test_when_clicked_on_a_button_get_item_pressed(self):
        self.create_context_menu_setup()

        mock_rect = Mock()
        self.scene.context_menu.rect = mock_rect
        mock_rect.y = 20
        mock_rect.collidepoint.return_value = True

        self.scene.handle_opened_context_menu((10, 10))
        self.assertEqual(self.scene.context_menu.get_button_pressed((10, 10)), "Walk")


class WorldSceneRenderTestCase(TestCase):
    def setUp(self):
        self.scene = WorldScene("world")
        self.scene.initialize_scene()

    @patch("pygame.sprite.Group.draw")
    def test_render_calls_world_scene_group_render(self, mock_draw):
        self.scene.game = Mock()
        self.scene.game.render_context = {"display": pygame.display.get_surface()}
        self.scene.render()
        mock_draw.assert_called_with(self.scene.display)
