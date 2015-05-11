# -*- encoding: utf-8 -*-
import pygame
from taz.game import Scene, Game

from tekmate.ui import PlayerUI, NoteUI, ContextMenuUI


class WorldScene(Scene):
    def __init__(self, ident):
        super(WorldScene, self).__init__(ident)
        self.player_ui = None
        self.note_ui = None
        self.display = None
        self.context_menu = None

        self.world_container = []
        self.items_in_ui = []

    def initialize_scene(self):
        self.player_ui = PlayerUI()
        self.context_menu = ContextMenuUI()
        self.add_item_to_ui(NoteUI(self.world_container))

    def add_item_to_ui(self, item):
        self.items_in_ui.append(item)

    def update(self):  # pragma: no cover  (This is only because of all the branches, they will get tested eventually)
        for event in self.game.update_context["get_events"]():
            if event.type == pygame.QUIT or self.escape_key_pressed(event):
                raise Game.GameExitException
            elif self.left_mouse_button_pressed(event):
                self.handle_left_mouse_button(event.pos)
            elif self.right_mouse_button_pressed(event):
                self.open_context_menu(event.pos)
            elif self.i_pressed(event):
                self.handle_bag()

    def escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def left_mouse_button_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def handle_left_mouse_button(self, pos):
        if not self.context_menu.visible:
            self.move_player(pos, self.display)
            self.add_item_if_clicked_on(pos)
        else:
            self.interact_with_context_menu(pos)

    def move_player(self, mouse_pos, display):
        self.player_ui.move_player(mouse_pos, display)

    def add_item_if_clicked_on(self, pos):
        for item_ui in self.items_in_ui:
            if self.clicked_on(item_ui, pos):
                self.add_item_to_player(item_ui)

    def clicked_on(self, item, pos):
        return item.surface.get_rect(topleft=item.position).collidepoint(pos)

    def add_item_to_player(self, item_ui):
        self.player_ui.add_item(item_ui.item)
        self.items_in_ui.remove(item_ui)

    def interact_with_context_menu(self, pos):
        if self.clicked_on(self.context_menu, pos):
            menu_clicked = self.context_menu.interact_with_item(pos)
            self.player_ui.interact(menu_clicked)
        else:
            self.hide_context_menu()

    def hide_context_menu(self):
        self.context_menu.visible = False

    def right_mouse_button_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 3

    def open_context_menu(self, pos):
        self.change_context_menu_if_clicked_on_item(pos)
        self.show_context_menu(pos)

    def change_context_menu_if_clicked_on_item(self, pos):
        menu_style = ContextMenuUI.CONTEXT_MENU_DEFAULT
        for item_ui in self.items_in_ui:
            menu_style = self.change_context_menu_if_necessary(item_ui, pos)
        self.context_menu.create_menu(menu_style)

    def change_context_menu_if_necessary(self, item_ui, pos):
        menu_style = ContextMenuUI.CONTEXT_MENU_DEFAULT
        if self.clicked_on(item_ui, pos):
            menu_style = ContextMenuUI.CONTEXT_MENU_ITEM
        if self.is_bag_visible() and self.clicked_on(self.player_ui.bag_ui, pos):
            menu_style = ContextMenuUI.CONTEXT_MENU_BAG_ITEM
        return menu_style

    def is_bag_visible(self):
        return self.player_ui.is_bag_visible()

    def show_context_menu(self, pos):
        self.context_menu.show(pos, self.display)

    def i_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_i

    def handle_bag(self):
        self.open_close_bag()
        if self.is_context_menu_visible():
            self.hide_context_menu()

    def open_close_bag(self):
        if not self.is_bag_visible():
            self.show_bag()
        else:
            self.hide_bag()

    def show_bag(self):
        self.player_ui.show_bag()

    def hide_bag(self):
        self.player_ui.hide_bag()

    def is_context_menu_visible(self):
        return self.context_menu.visible

    def render(self):  # pragma: no cover
        self.display = self.game.render_context["display"]
        self.display.fill((0, 0, 0))

        self.render_items()
        self.render_player()
        self.render_bag()
        self.render_context_menu()

        pygame.display.flip()

    def render_items(self):
        for item in self.items_in_ui:
            item.render(self.display)

    def render_player(self):
        self.player_ui.render(self.display)

    def render_bag(self):
        if self.player_ui.is_bag_visible():
            self.player_ui.draw_bag(self.game.render_context["display"])
        else:   # pragma: no cover
            pass

    def render_context_menu(self):
        if self.is_context_menu_visible():
            self.context_menu.render(self.display)
        else:   # pragma: no cover
            pass

    def resume(self):  # pragma: no cover
        print("Resuming World")

    def pause(self):  # pragma: no cover
        print("Pausing World")

    def tear_down(self):  # pragma: no cover
        print("Tearing-Down World")
