# -*- encoding: utf-8 -*-
from unittest import TestCase, skip

from mock import patch, call, Mock
import pygame

from tekmate.game import Player
from tekmate.ui import PlayerUserInterface


class PlayerUITestCase(TestCase):
    def setUp(self):
        self.transform_patcher = patch("tekmate.ui.pygame.transform")
        self.transform_patcher.start()
        self.surface_patcher = patch("tekmate.ui.pygame.Surface")
        self.surface = self.surface_patcher.start().return_value

        self.set_up_pygame_display()
        self.player_ui = PlayerUserInterface()

    def tearDown(self):
        self.surface_patcher.stop()
        self.transform_patcher.stop()

    def set_up_pygame_display(self):
        pygame.display.init()
        pygame.display.set_mode((1, 1))

    def test_can_create_player_ui(self):
        self.assertEquals(self.player_ui.get_position(), (0, 0))

    def test_when_initializing_player_ui_a_player_instance_is_created(self):
        self.assertIsInstance(self.player_ui.player, Player)

    def test_when_image_not_found_raise_error(self):
        self.assertRaises(PlayerUserInterface.ImageNotFound, self.player_ui.load_image, "player", "no_player.bmp")

    def test_when_render_is_called_screen_should_get_cleared_and_image_is_drawn_to_surface(self):
        self.player_ui.render()

        expected_argument_for_fill = call((255, 255, 255))
        self.assertFillArgumentIs(expected_argument_for_fill)

        expected_argument_for_blit = call(self.player_ui.image, (0, 0))
        self.assertBlitArgumentIs(expected_argument_for_blit)

    def test_when_drawn_player_to_display_expected_argument_should_be_display(self):
        mock_display = Mock()
        self.player_ui.draw_player_to_display(mock_display)
        mock_display.blit.assert_called_with(self.player_ui.surface, (0, 0))

    def assertBlitArgumentIs(self, expected_args):
        returned_argument_list_for_blit = self.player_ui.surface.blit.call_args_list
        self.assertIn(expected_args, returned_argument_list_for_blit)

    def assertFillArgumentIs(self, expected_argument_for_fill):
        returned_argument_list_for_fill = self.player_ui.surface.fill.call_args_list
        self.assertIn(expected_argument_for_fill, returned_argument_list_for_fill)
