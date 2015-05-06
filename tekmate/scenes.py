# -*- encoding: utf-8 -*-
import pygame
from taz.game import Scene, Game
from tekmate.ui import PlayerUI


class WorldScene(Scene):
    def initialize_scene(self):
        self.game.render_context["player_ui"] = PlayerUI()

    def update(self):  # pragma: no cover  (This is only because of all the branches, they will get tested eventually)
        player_ui = self.game.render_context["player_ui"]
        for event in self.game.update_context["get_events"]():
            if event.type == pygame.QUIT or self.escape_key_pressed(event):
                raise Game.GameExitException
            elif self.left_mouse_button_pressed(event):
                player_ui.move_player(event.pos)
            else:
                pass

    def render(self):  # pragma: no cover
        self.game.render_context["display"].fill((0, 0, 0))
        player_ui = self.game.render_context["player_ui"]
        player_ui.render()
        self.game.render_context["display"].blit(player_ui.surface, (player_ui.position, player_ui.position))
        pygame.display.flip()

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