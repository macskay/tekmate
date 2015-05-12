# -*- encoding: utf-8 -*-
import pygame
from taz.game import Scene, Game

from tekmate.ui import ContextMenuUI


class WorldScene(Scene):
    def __init__(self, ident):
        super(WorldScene, self).__init__(ident)
        self.display = None

        self.context_menu = ContextMenuUI()
        self.world_scene_sprite_group = pygame.sprite.Group()

    def initialize_scene(self):
        pass

    def update(self):  # pragma: no cover
        for event in self.game.update_context["get_events"]():
            if event.type == pygame.QUIT or self.escape_key_pressed(event):
                raise Game.GameExitException
            elif self.right_mouse_pressed(event):
                self.open_context_menu(event.pos)
            elif self.left_mouse_pressed(event):
                self.handle_opened_context_menu(event.pos)

    def escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def right_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 3

    def left_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def open_context_menu(self, pos):
        self.context_menu.open(pos, self.display)
        self.context_menu.add(self.world_scene_sprite_group)

    def handle_opened_context_menu(self, pos):
        if self.context_menu.rect.collidepoint(pos):
            item_pressed = self.context_menu.get_button_pressed(pos)
        else:
            self.context_menu.remove(self.world_scene_sprite_group)

    def render(self):
        self.display = self.game.render_context["display"]
        self.display.fill((0, 0, 0))
        self.world_scene_sprite_group.draw(self.display)

        pygame.display.flip()

    def resume(self):  # pragma: no cover
        print("Resuming World")

    def pause(self):  # pragma: no cover
        print("Pausing World")

    def tear_down(self):  # pragma: no cover
        print("Tearing-Down World")
