# -*- encoding: utf-8 -*-
from unittest import TestCase, skip

from mock import patch, call, Mock
from pygame import Surface, display

from tekmate.ui import UI, PlayerUI, BagUI, NoteUI
from tekmate.game import Player
from tekmate.items import Note, IdCard


class UITestCase(TestCase):
    def test_when_image_not_found_raise_error(self):
        self.assertRaises(UI.ImageNotFound, UI.load_image, "player", "no_player.bmp")


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
        display.init()
        display.set_mode((1, 1))

    def test_can_create_player_ui(self):
        self.assertEquals(self.player_ui.get_position(), (0, 0))

    def test_when_initializing_player_ui_a_player_instance_is_created(self):
        self.assertIsNotNone(self.player_ui.player)

    def test_when_render_is_called_screen_should_get_cleared_and_image_is_drawn_to_surface(self):
        self.player_ui.render(Mock())

        expected_argument_for_fill = call((255, 255, 255))
        self.assertFillArgumentIs(expected_argument_for_fill)

        expected_argument_for_blit = call(self.player_ui.image, PlayerUI.PLAYER_IMAGE_OFFSET)
        self.assertBlitArgumentIs(expected_argument_for_blit)

    def assertFillArgumentIs(self, expected_argument_for_fill):
        returned_argument_list_for_fill = self.player_ui.surface.fill.call_args_list
        self.assertIn(expected_argument_for_fill, returned_argument_list_for_fill)

    def assertBlitArgumentIs(self, expected_args):
        returned_argument_list_for_blit = self.player_ui.surface.blit.call_args_list
        self.assertIn(expected_args, returned_argument_list_for_blit)

    def test_when_clicked_to_move_player_its_move_function_should_be_called(self):
        old_pos = self.player_ui.get_position()
        self.player_ui.move_player((300, 0), Surface((1920, 1080)))
        self.assertNotEqual(self.player_ui.get_position(), old_pos)

    def test_when_draw_bag_is_called_the_render_function_of_bag_should_be_called(self):
        mock_bag_ui = Mock()
        mock_display = Mock()
        self.player_ui.bag_ui = mock_bag_ui
        self.player_ui.draw_bag(mock_display)
        mock_bag_ui.render.assert_called_with(mock_display)

    def test_when_hide_bag_is_called_bag_visible_should_be_false(self):
        self.player_ui.hide_bag()
        self.assertFalse(self.player_ui.is_bag_visible())


    def test_add_item_adds_an_item_to_the_players_bag(self):
        self.player_ui.add_item(Mock())
        self.assertEqual(len(self.player_ui.player.bag), 1)


class BagUITestCase(TestCase):
    def setUp(self):
        self.bag_ui = BagUI()

    def create_mock_surface(self):
        mock_surface = Mock()
        self.bag_ui.surface = mock_surface
        return mock_surface

    def create_player_ui(self):
        player_ui = PlayerUI()
        player_ui.player.add_item(Note([]))
        player_ui.player.add_item(IdCard([]))
        return player_ui

    def test_can_create_bag_ui(self):
        self.assertIsInstance(self.bag_ui, BagUI)

    def test_when_created_surface_is_not_none(self):
        self.assertIsInstance(self.bag_ui.surface, Surface)

    def test_when_created_visible_is_false(self):
        self.assertFalse(self.bag_ui.visible)

    def test_when_render_and_visible_fill_with_green_color_should_be_called(self):
        mock_surface = self.create_mock_surface()
        self.bag_ui.show_bag(Player())
        self.bag_ui.render(mock_surface)
        mock_surface.fill.assert_called_with(BagUI.BACKGROUND_COLOR)

    def test_when_render_and_visible_player_bag_items_text_should_not_be_empty(self):
        player_ui = self.create_player_ui()
        mock_surface = self.create_mock_surface()
        self.bag_ui.show_bag(player_ui.player)
        self.bag_ui.render(mock_surface)
        self.assertNotEqual(self.bag_ui.items_text, 0)

    def test_is_text_empty_should_return_true_if_empty(self):
        self.assertTrue(self.bag_ui.is_text_item_empty())

    def test_when_hiding_back_visible_should_be_false_and_list_empty(self):
        self.bag_ui.visible = True
        self.bag_ui.hide_bag()
        self.assertFalse(self.bag_ui.visible)
        self.assertEqual(len(self.bag_ui.items_text), 0)




class NoteUITestCase(TestCase):
    def setUp(self):
        self.note_ui = NoteUI([])

    def test_can_create_tel_note_ui(self):
        self.assertIsNotNone(self.note_ui.item)

    def test_when_creating_note_and_ui_container_misses_raise_exception(self):
        with self.assertRaises(AssertionError):
            NoteUI(None)

    def test_when_creating_note_surface_is_not_none(self):
        self.assertIsNotNone(self.note_ui.surface)

    def test_when_creating_note_image_is_not_none(self):
        self.assertIsNotNone(self.note_ui.image)

    def test_when_rendering_image_is_blitted_to_surface_and_surface_to_display(self):
        mock_surface = Mock(spec=Surface)
        mock_image = Mock(spec=Surface)
        mock_display = Mock(spec=Surface)

        self.note_ui.surface = mock_surface
        self.note_ui.image = mock_image

        self.note_ui.render(mock_display)
        mock_surface.blit.assert_called_with(mock_image, (0, 0))
        mock_display.blit.assert_called_with(mock_surface, (300, 100))
