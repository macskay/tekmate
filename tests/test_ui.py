# -*- encoding: utf-8 -*-
from unittest import TestCase
import pygame

from tekmate.ui import UI, ContextMenuUI, PlayerUI


class UITestCase(TestCase):
    def test_when_image_not_found_raise_error(self):
        self.assertRaises(UI.ImageNotFound, UI.load_image, "player", "no_player.bmp")


class ContextMenuUITestCase(TestCase):
    def setUp(self):
        self.ui = ContextMenuUI()
        pygame.display.set_mode((1920, 1080))

    def test_surface_to_draw_not_none_by_default(self):
        self.assertIsNotNone(self.ui.surface)

    def test_image_not_none_by_default(self):
        self.assertIsNotNone(self.ui.image)

    def test_rect_not_none_by_default(self):
        self.assertIsNotNone(self.ui.rect)

    def test_font_not_none_by_default(self):
        self.assertIsNotNone(self.ui.font)

    def test_when_created_menu_is_filled_with_default_text(self):
        self.assertEqual(self.ui.surface.get_height(), 30)

    def test_when_build_called_with_layout_size_of_surface_changed(self):
        self.ui.build_context_menu(ContextMenuUI.CONTEXT_MENU_ITEM)
        self.assertEqual(self.ui.surface.get_height(), 90)

    def test_when_context_menu_open_and_button_pressed_get_name_of_item(self):
        self.assertEqual(self.ui.get_button_pressed((10, 10)), "Walk")

    def test_when_second_button_is_pressed_get_name_of_second_item(self):
        self.ui.build_context_menu(ContextMenuUI.CONTEXT_MENU_ITEM)
        self.assertEqual(self.ui.get_button_pressed((10, 50)), "Take")

    def test_when_get_button_pressed_is_passed_invalid_list_do_nothing(self):
        self.ui.current_layout = [1, 2]
        self.assertRaises(ContextMenuUI.InvalidLayout, self.ui.get_button_pressed, (1000, 1000))

    def test_when_opened_on_the_far_right_open_menu_top_right(self):
        pos = (1910, 10)
        self.ui.open(pos)
        self.assertEqual(self.ui.rect.topright, pos)

    def test_when_opened_on_the_far_bottom_right_open_menu_bottom_right(self):
        pos = (1910, 1070)
        self.ui.open(pos)
        self.assertEqual(self.ui.rect.bottomright, pos)

    def test_when_opened_on_the_far_bottom_open_menu_bottom_left(self):
        pos = (10, 1070)
        self.ui.open(pos)
        self.assertEqual(self.ui.rect.bottomleft, pos)

    def test_when_asked_for_the_pos_return_rects_topleft(self):
        self.assertEqual(self.ui.get_pos(), self.ui.rect.topleft)


class PlayerUITestCase(TestCase):
    def setUp(self):
        self.ui = PlayerUI()

    def test_can_create_player_ui(self):
        self.assertIsInstance(self.ui, pygame.sprite.Sprite)

    def test_image_not_none_by_default(self):
        self.assertIsNotNone(self.ui.image)

    def test_rect_not_none_by_default(self):
        self.assertIsNotNone(self.ui.rect)



