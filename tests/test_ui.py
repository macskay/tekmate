from unittest import TestCase
from mock import Mock, patch
import pygame

from tekmate.ui import PlayerUI, ImageNotFound


class PlayerUITestCase(TestCase):

    def setUp(self):
        self.transform_patcher = patch("tekmate.ui.pygame.transform")
        self.transform_patcher.start()
        self.surface_patcher = patch("tekmate.ui.pygame.Surface")
        self.surface = self.surface_patcher.start().return_value
        self.set_up_pygame_display()
        self.player_ui = PlayerUI()

    def tearDown(self):
        self.surface_patcher.stop()
        self.transform_patcher.stop()

    def set_up_pygame_display(self):
        pygame.display.init()
        pygame.display.set_mode((1, 1))

    def test_can_create_player_ui(self):
        self.assertEqual(self.player_ui.surface.get_colorkey(), (0, 128, 128, 255))

    def test_when_image_not_found_raise_error(self):
        self.assertRaises(ImageNotFound, self.player_ui.load_image, "player", "no_player.bmp")

    def test_when_render_is_called_screen_should_get_cleared_and_image_is_drawn_to_surface(self):
        mock_player_ui = Mock(PlayerUI)
        mock_player_ui.surface = self.surface
        mock_player_ui.render()

        self.surface.fill.assert_called_with((250, 250, 250))
        self.surface.blit.assert_called_with(mock_player_ui.image, (0, 0))