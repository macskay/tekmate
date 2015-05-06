from unittest import TestCase
import pygame

from tekmate.ui import PlayerUI, ImageNotFound


class PlayerUITestCase(TestCase):
    def setUp(self):
        self.set_up_pygame_display()
        self.player_ui = PlayerUI()

    def set_up_pygame_display(self):
        pygame.display.init()
        pygame.display.set_mode((1, 1))

    def test_can_create_player_ui(self):
        self.assertEqual(self.player_ui.surface.get_colorkey(), (0, 128, 128, 255))

    def test_when_image_not_found_raise_error(self):
        self.assertRaises(ImageNotFound, self.player_ui.load_image, "player", "no_player.bmp")
