# -*- encoding: utf-8 -*-
from unittest import TestCase

from mock import patch, Mock
import pygame

from tekmate.configuration import PyGameInitializer, TekmateFactory
from tekmate.scenes import WorldScene


class PyGameInitializerTestCase(TestCase):
    def setUp(self):
        self.conf = {"display_width": 640, "display_height": 480}
        self.pygame_initializer = PyGameInitializer(self.conf)
        self.pygame_patcher = patch("tekmate.configuration.pygame", spec=True)
        self.pygame = self.pygame_patcher.start()
        self.uc, self.rc = self.pygame_initializer.initialize()

    def test_can_create_pygame_initializer(self):
        self.assertIsNotNone(self.pygame_initializer.configuration)

    def test_initialze_pygame_actually_initializes_pygame(self):
        self.pygame.init.assert_called_with()

    def test_initialize_pygame_sets_the_caption(self):
        self.pygame.display.set_caption.assert_called_with(PyGameInitializer.CAPTION)

    def test_initialize_pygame_sets_window_resoultion_correctly_from_conf(self):
        self.pygame.display.set_mode.assert_called_with((640, 480))

    def test_initialize_pygame_loads_global_images(self):
        self.assertEqual(self.pygame_initializer.load_global_images(), self.rc["images-global"])

    def test_when_initialize_mouse_is_getting_configured_correctly(self):
        self.pygame.mouse.set_visible.assert_called_with(True)

    def test_update_context_should_have_a_clock(self):
        self.assertTrue(hasattr(self.uc["clock"], "tick"))

    def test_update_context_should_have_get_event_reference(self):
        self.assertIs(self.uc["get_events"], self.pygame.event.get)

    def test_render_context_should_have_flip_function(self):
        self.assertIs(self.rc["flip"], self.pygame.display.flip)

    def test_render_context_should_main_surface_reference(self):
        self.assertIs(self.rc["display"], self.pygame.display.get_surface())


class TekmateFactoryTestCase(TestCase):
    def setUp(self):
        mock_init = Mock(spec=PyGameInitializer)
        mock_scene = Mock(spec=WorldScene)
        mock_init.initialize.return_value = None, {}

        self.set_up_display()

        self.mock_init = mock_init
        self.mock_scene = mock_scene

    def set_up_display(self):
        pygame.display.init()
        pygame.display.set_mode((1, 1))

    def assertSceneRegistered(self, identifier, class_type):
        game = TekmateFactory(self.mock_init).create()
        scene = game.registered_scenes[identifier]
        self.assertIsInstance(scene, class_type)

    def test_create_should_initialize_pygame(self):
        TekmateFactory(self.mock_init).create()
        self.mock_init.initialize.assert_called_with()

    def test_create_should_add_world_scene_to_game(self):
        self.assertSceneRegistered("world", WorldScene)

    def test_create_should_push_world_scene_to_game(self):
        game = TekmateFactory(self.mock_init).create()
        self.assertEqual(game.get_name_of_top_scene(), "world")
