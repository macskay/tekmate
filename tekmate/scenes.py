# -*- encoding: utf-8 -*-
import pygame
from taz.game import Scene, Game


class WorldScene(Scene):
    def initialize_scene(self):  # pragma: no cover


    def update(self):  # pragma: no cover
        for event in self.game.update_context["get_events"]():
            if event.type == pygame.QUIT or self.escape_key_pressed(event):
                raise Game.GameExitException
            elif self.left_mouse_button_pressed(event):
                print(event.button)
            else:
                pass

    def render(self):  # pragma: no cover
        pass

    def resume(self):  # pragma: no cover
        print("Resuming World")

    def pause(self):  # pragma: no cover
        print("Pausing World")

    def tear_down(self):  # pragma: no cover
        print("Tearing-Down World")

    def escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def left_mouse_button_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


class PlayerUI(pygame.Surface):
    def __init__(self):
        pass
