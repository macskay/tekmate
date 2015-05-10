# -*- encoding: utf-8 -*-
import pygame
from taz.game import Scene, Game

from tekmate.ui import PlayerUI, NoteUI
from tekmate.items import IdCard


class WorldScene(Scene):
    def __init__(self, ident):
        super(WorldScene, self).__init__(ident)
        self.player_ui = None
        self.note_ui = None
        self.display = None

        self.world_container = []
        self.items_in_ui = []

    def initialize_scene(self):
        self.player_ui = PlayerUI()
        self.add_item_to_ui(NoteUI(self.world_container))

    def update(self):  # pragma: no cover  (This is only because of all the branches, they will get tested eventually)
        for event in self.game.update_context["get_events"]():
            if event.type == pygame.QUIT or self.escape_key_pressed(event):
                raise Game.GameExitException
            elif self.left_mouse_button_pressed(event):
                self.move_player(event.pos, self.display)
                self.add_item_if_clicked_on(event.pos)
            elif self.i_pressed(event):
                self.handle_bag()

    def render(self):  # pragma: no cover
        self.display = self.game.render_context["display"]
        self.display.fill((0, 0, 0))

        self.render_items()
        self.render_player()

        if self.player_ui.is_bag_visible():
            self.draw_bag()

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

    def i_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_i

    def is_bag_visible(self):
        return self.player_ui.is_bag_visible()

    def show_bag(self):
        self.player_ui.show_bag()

    def draw_bag(self):
        self.player_ui.draw_bag(self.game.render_context["display"])

    def hide_bag(self):
        self.player_ui.hide_bag()

    def move_player(self, mouse_pos, display):
        self.player_ui.move_player(mouse_pos, display)

    def handle_bag(self):
        if not self.is_bag_visible():
            self.show_bag()
        else:
            self.hide_bag()

    def add_item_to_ui(self, item):
        self.items_in_ui.append(item)

    def render_items(self):
        for item in self.items_in_ui:
            item.render(self.display)

    def render_player(self):
        self.player_ui.render(self.display)
        pass

    def add_item_if_clicked_on(self, pos):
        for item_ui in self.items_in_ui:
            if self.is_clicked_on_item(item_ui, pos):
                self.add_item_to_player(item_ui.item)
                self.items_in_ui.remove(item_ui)

    def is_clicked_on_item(self, item, pos):
        return item.surface.get_rect(topleft=item.position).collidepoint(pos)

    def add_item_to_player(self, item):
        self.player_ui.add_item(item)
