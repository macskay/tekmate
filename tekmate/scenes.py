# -*- encoding: utf-8 -*-
import operator
from os import path

import pygame
from taz.game import Scene, Game


class ImageNotFound(Exception):
    pass


class WorldScene(Scene):
    def initialize_scene(self):
        self.game.render_context["player_ui"] = PlayerUI()

    def update(self):
        for event in self.game.update_context["get_events"]():
            if event.type == pygame.QUIT or self.escape_key_pressed(event):
                raise Game.GameExitException
            elif self.left_mouse_button_pressed(event):
                print(event.button)
                player_ui = self.game.render_context["player_ui"]
                player_ui.move_player(0)
            else:
                pass

    def render(self):
        self.game.render_context["display"].fill((0, 0, 0))
        player_ui = self.game.render_context["player_ui"]
        player_ui.render()
        self.game.render_context["display"].blit(player_ui.surface, (player_ui.position, player_ui.position))
        pygame.display.flip()

    def resume(self):
        print("Resuming World")

    def pause(self):
        print("Pausing World")

    def tear_down(self):
        print("Tearing-Down World")

    def escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def left_mouse_button_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


class PlayerUI(object):
    SCALING_FACTOR = 2.8

    def __init__(self):
        self.surface, self.image = self.create_surface_and_image(PlayerUI.SCALING_FACTOR)
        self.surface.set_colorkey((0, 128, 128))
        self.position = (500, 50)

    def render(self):
        self.surface.fill((250, 250, 250))
        self.surface.blit(self.image, (0, 0))

    def move_player(self, direction):
        if direction == 0:
            self.position = (600, 50)

    def create_surface_and_image(self, factor):
        surface = self.create_surface_with_factor(factor)
        image = self.create_image_with_factor(factor)
        return surface, image

    def create_surface_with_factor(self, factor):
        surface_proportions = (round(factor * 50), round(factor * 100))
        surface = pygame.Surface(surface_proportions)
        surface.convert()
        return surface

    def create_image_with_factor(self, factor):
        image = self.load_image()
        img_proportions = (round(factor * image.get_width()), round(factor * image.get_height()))
        image = pygame.transform.scale(image, img_proportions)
        return image

    def load_image(self):
        fullname = path.join('..', 'assets', 'player', 'player.bmp')
        try:
            return pygame.image.load(fullname)
        except:
            raise ImageNotFound