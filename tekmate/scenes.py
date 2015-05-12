# -*- encoding: utf-8 -*-
import pygame
from taz.game import Scene, Game

from tekmate.ui import ContextMenuUI, PlayerUI, NoteUI


class WorldScene(Scene):
    def __init__(self, ident):
        super(WorldScene, self).__init__(ident)
        self.display = None

        self.context_menu = ContextMenuUI()
        self.player_ui = PlayerUI()

        self.world_scene_sprite_group = pygame.sprite.OrderedUpdates()
        self.world_scene_sprite_group.add(self.player_ui)

        self.world_item_sprite_group = pygame.sprite.OrderedUpdates()

        self.current_observed_item = None

    def initialize(self):
        self.display = self.game.render_context["display"]

        # TODO: ADDING AN ITEM
        self.world_item_sprite_group.add(NoteUI())

    def update(self):
        for event in self.game.update_context["get_events"]():
            self.handle_input(event)

    def handle_input(self, event):
        if event.type == pygame.QUIT or self.is_escape_key_pressed(event):
            raise Game.GameExitException
        elif self.is_right_mouse_pressed(event):
            self.open_context_menu(event.pos)
        elif self.is_left_mouse_pressed(event):
            self.process_left_mouse_button_pressed(event)
        elif self.is_i_pressed(event):  # pragma: no cover (implicit else, which does nothing)
            self.handle_bag()

    def is_escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def is_right_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 3

    def open_context_menu(self, pos):
        self.select_correct_context_menu_list(pos)
        self.context_menu.open(pos)
        self.context_menu.add(self.world_scene_sprite_group)

    def select_correct_context_menu_list(self, pos):
        for item in self.world_item_sprite_group.sprites():
            if item.rect.collidepoint(pos):  # pragma: no cover (implicit else, nothing happening here)
                self.context_menu.build_context_menu(ContextMenuUI.CONTEXT_MENU_ITEM)
                self.current_observed_item = item
                break
        else:
            self.context_menu.build_context_menu(ContextMenuUI.CONTEXT_MENU_DEFAULT)

    def is_left_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def process_left_mouse_button_pressed(self, event):
        if self.context_menu.alive():
            self.handle_opened_context_menu(event.pos)
        else:
            self.move_player(event.pos)

    def handle_opened_context_menu(self, mouse_pos):
        if self.is_context_menu_clicked_on(mouse_pos):
            self.process_button_command(mouse_pos)
        else:
            self.close_context_menu()

    def is_context_menu_clicked_on(self, pos):
        return self.context_menu.rect.collidepoint(pos)

    def process_button_command(self, mouse_pos):
        item_pressed = self.get_button_pressed(mouse_pos)
        if item_pressed == "Walk":  # pragma: no cover (implicit else, which can never be called)
            self.move_player(mouse_pos)
        elif item_pressed == "Take":  # pragma: no cover
            self.take_item(mouse_pos)
        elif item_pressed == "Look at":  # pragma: no cover
            print(self.look_at_item())
        elif item_pressed == "Use":  # pragma: no cover
            print(self.use_item())
        self.close_context_menu()

    def move_player(self, pos):
        self.player_ui.move(pos)

    def take_item(self, mouse_pos):
        self.move_player(mouse_pos)
        self.player_ui.add_item(self.current_observed_item)

    def look_at_item(self):
        return self.current_observed_item.look_at()

    def use_item(self):
        return self.current_observed_item.use()

    def is_i_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_i

    def handle_bag(self):
        if not self.player_ui.is_bag_visible():
            self.player_ui.bag_visible = True
        else:
            self.player_ui.bag_visible = False

    def get_button_pressed(self, mouse_pos):
        return self.context_menu.get_button_pressed(mouse_pos)

    def close_context_menu(self):
        self.context_menu.remove(self.world_scene_sprite_group)
        self.current_observed_item = None

    def render(self):
        self.display.fill((0, 0, 0))

        self.world_item_sprite_group.draw(self.display)
        self.world_scene_sprite_group.draw(self.display)

        if self.player_ui.is_bag_visible():
            self.player_ui.bag_sprite_group.draw(self.display)

        pygame.display.flip()

    def resume(self):  # pragma: no cover
        print("Resuming World")

    def pause(self):  # pragma: no cover
        print("Pausing World")

    def tear_down(self):  # pragma: no cover
        print("Tearing-Down World")


