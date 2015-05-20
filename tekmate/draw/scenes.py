# -*- encoding: utf-8 -*-
from functools import partial

import pygame

from taz.game import Scene, Game

from tekmate.draw.messages import MessageSystem
from tekmate.draw.ui import ContextMenuUI, PlayerUI, UI

import logging

logger = logging.getLogger()


class WorldScene(Scene):
    FPS_EVENT = pygame.USEREVENT + 0

    DISPLAY_TEXT_EVENT = pygame.USEREVENT + 1

    def __init__(self, ident):
        super(WorldScene, self).__init__(ident)
        self.display = None

        self.context_menu = ContextMenuUI()
        self.player_ui = PlayerUI()
        self.message_system = MessageSystem()

        self.item_group = pygame.sprite.OrderedUpdates()
        self.default_group = pygame.sprite.OrderedUpdates()
        self.context_group = pygame.sprite.OrderedUpdates()
        self.display_text_group = pygame.sprite.GroupSingle()
        self.background_group = pygame.sprite.GroupSingle()
        self.animation_group = pygame.sprite.GroupSingle()

        self.map_items = list()

        self.current_observed_item = None
        self.current_selected_item = None

        self.best_path = list()
        self.callback = None

        self.last_destination = (0, 0)

        self.is_wait_for_crouch = False

    def initialize(self):
        self.display = self.game.render_context["display"]
        pygame.time.set_timer(self.FPS_EVENT, 3000)

        self.change_map(self.game.update_context["maps"]["example"])
        self.default_group.add(self.player_ui)

    def update(self):
        clock = self.game.update_context["clock"]

        delta = clock.tick(1000)

        self.update_visible_items()

        self.animation_group.update(delta)
        self.stop_animation_if_needed()

        for event in self.game.update_context["get_events"]():
            self.handle_input(event)

        self.default_group.update()

    def stop_animation_if_needed(self):
        if self.player_ui.rect.bottomleft == self.last_destination:
            self.player_ui.reset_walk()
            pygame.time.set_timer(UI.WALK_EVENT, 0)
            self.last_destination = (0, 0)

    def handle_input(self, event):
        if event.type == pygame.QUIT or self.is_escape_key_pressed(event):
            raise Game.GameExitException
        elif self.is_right_mouse_pressed(event):
            self.process_right_mouse_pressed(event.pos)
        elif self.is_left_mouse_pressed(event):
            self.process_left_mouse_button_pressed(event)
        elif self.is_i_pressed(event):
            if not self.context_menu.alive():
                self.handle_bag()
        elif event.type == self.DISPLAY_TEXT_EVENT:
            self.display_text_group.empty()
            pygame.time.set_timer(self.DISPLAY_TEXT_EVENT, 0)
        elif event.type == UI.WALK_EVENT:
            self.player_ui.animate_walk()
        elif event.type == UI.CROUCH_EVENT:
            if self.player_ui.is_waiting_for_crouch:
                self.player_ui.is_waiting_for_crouch = False
                pygame.time.wait(1000)
            else:
                self.player_ui.animate_crouch()
        elif event.type == self.FPS_EVENT:
            logger.debug("FPS: %s" % self.game.update_context["clock"].get_fps())
        elif event.type == UI.STOP_CROUCH_EVENT:
            self.player_ui.reset_crouch()
            pygame.time.set_timer(UI.CROUCH_EVENT, 0)

    def is_escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def is_right_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 3

    def process_right_mouse_pressed(self, pos):
        if len(self.animation_group) > 0:
            self.animation_group.empty()
        clicked_in_bag_but_not_on_item = self.select_correct_context_menu_list(pos)
        if clicked_in_bag_but_not_on_item:
            self.close_context_menu()
        else:
            self.open_context_menu(pos)

    def select_correct_context_menu_list(self, pos):
        self.set_context_menu(ContextMenuUI.CONTEXT_MENU_DEFAULT)
        if self.is_mouse_pos_inside_world_item(pos) and not self.is_bag_visible():
            self.set_world_item_context_menu()
        elif self.is_mouse_pos_inside_bag_item(pos):
            self.set_bag_item_world_context_menu()
        else:
            if self.is_bag_visible():
                return True
        return False

    def is_mouse_pos_inside_world_item(self, pos):
        is_item_clicked = False
        for item in self.item_group.sprites():
            if item.rect.collidepoint(pos):
                self.current_observed_item = item
                is_item_clicked = True
        return is_item_clicked

    def is_bag_visible(self):
        return self.player_ui.is_bag_visible()

    def set_world_item_context_menu(self):
        if self.current_selected_item is not None:
            self.set_context_menu(ContextMenuUI.CONTEXT_COMBINE_ITEM)
        else:
            self.set_context_menu(ContextMenuUI.CONTEXT_MENU_ITEM)

    def set_context_menu(self, layout):
        self.context_menu.build_context_menu(layout)

    def is_mouse_pos_inside_bag_item(self, pos):
        for item in self.player_ui.bag_sprite_group.sprites()[1:]:
            if item.rect.collidepoint(pos):
                self.current_observed_item = item
                return True
        return False

    def set_bag_item_world_context_menu(self):
        self.set_context_menu(ContextMenuUI.CONTEXT_MENU_BAG_ITEM)

    def open_context_menu(self, pos):
        self.context_menu.open(pos)
        self.context_menu.add(self.context_group)

    def is_left_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def process_left_mouse_button_pressed(self, event):
        if self.is_context_menu_visible():
            self.handle_opened_context_menu(event.pos)
        else:
            if not self.is_bag_visible():
                self.move_player(event.pos)

    def is_context_menu_visible(self):
        return self.context_menu.alive()

    def handle_opened_context_menu(self, mouse_pos):
        if self.is_context_menu_clicked_on(mouse_pos):
            self.process_button_command(mouse_pos)
        else:
            self.close_context_menu()

    def is_context_menu_clicked_on(self, pos):
        return self.context_menu.rect.collidepoint(pos)

    def process_button_command(self, mouse_pos):
        actions = {
            "Walk": lambda: partial(self.move_player, mouse_pos),
            "Take": lambda: partial(self.walk_to_item_before_interacting, self.take_item),
            "Look at": lambda: partial(self.walk_to_item_before_interacting, self.look_at_item),
            "Use": lambda: partial(self.walk_to_item_before_interacting, self.use_item),
            "Inspect": lambda: partial(self.show_display_text, self.inspect_item()),
            "Select": lambda: partial(self.select_item),
            "Combine": lambda: partial(self.walk_to_item_before_interacting, self.combine_items)
        }
        item_pressed = self.get_button_pressed(mouse_pos)
        actions[item_pressed]()()
        self.close_context_menu()

    def get_button_pressed(self, mouse_pos):
        return self.context_menu.get_button_pressed(mouse_pos)

    def walk_to_item_before_interacting(self, callback):
        if self.is_target_in_range():
            self.face_target(self.current_observed_item)
            callback()
        else:
            self.move_player(self.current_observed_item.rect.center, callback)

    def is_target_in_range(self):
        return abs(self.player_ui.rect.left - self.current_observed_item.rect.left) < 100

    def face_target(self, target):
        self.player_ui.face_target(target)

    def move_player(self, pos, callback=None):
        direction = self.get_direction(pos)
        self.best_path = self.find_shortest_path_to_destination(pos, direction)
        self.callback = callback
        self.move_to_next_waypoint()

    def get_direction(self, pos):
        if pos[0] > self.player_ui.rect.left:
            return 1
        else:
            return -1

    def find_shortest_path_to_destination(self, pos, dir):
        return self.player_ui.find_shortest_path_to_destination(pos, dir)

    def move_to_next_waypoint(self):
        if len(self.best_path) > 1:
            self.trigger_next_animation()
        elif len(self.best_path) == 1:
            self.trigger_last_animation_and_execute_interaction()

    def trigger_next_animation(self):
        pos = self.best_path[0].pos
        self.best_path.pop(0)
        self.start_walk_animation(self.move_to_next_waypoint, pos)

    def trigger_last_animation_and_execute_interaction(self):
        pos = self.best_path[0].pos
        self.best_path.pop(0)
        self.start_walk_animation(self.callback, pos)
        self.last_destination = pos

    def start_walk_animation(self, callback, pos):
        ani = self.player_ui.move(pos)
        if callback is not None:
            ani.callback = lambda: callback()
        ani.start(self.player_ui.rect)
        self.animation_group.add(ani)
        pygame.time.set_timer(UI.WALK_EVENT, 100)

    def take_item(self):
        add_message = self.player_ui.add_item(self.current_observed_item, self.map_items)
        self.show_display_text(add_message)
        self.current_observed_item = None

    def combine_items(self):
        reason = self.player_ui.combine_items(self.current_selected_item,
                                              self.current_observed_item)
        self.show_display_text(reason)
        self.current_selected_item = None
        self.current_observed_item = None

    def look_at_item(self):
        self.show_display_text(self.current_observed_item.look_at())

    def use_item(self):
        self.show_display_text(self.current_observed_item.use())

    def inspect_item(self):
        return self.current_observed_item.inspect()

    def get_add_message_of_item(self):
        return self.current_observed_item.get_add_message()

    def select_item(self):
        self.current_selected_item = self.current_observed_item
        item_name = self.get_name_of_item()
        self.show_display_text("What should I do with this %s?" % item_name)

    def get_name_of_item(self):
        return self.current_observed_item.get_name()

    def show_display_text(self, message):
        self.message_system.display_text(message, self.player_ui)
        self.message_system.add(self.display_text_group)
        pygame.time.set_timer(self.DISPLAY_TEXT_EVENT, 2000)

    def is_i_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_i

    def handle_bag(self):
        if not self.is_bag_visible():
            self.player_ui.bag_visible = True
        else:
            self.player_ui.bag_visible = False

    def close_context_menu(self):
        self.context_menu.remove(self.context_group)

    def render(self):
        self.display.fill((0, 0, 0))

        self.background_group.draw(self.display)
        self.item_group.draw(self.display)

        self.default_group.draw(self.display)

        if self.is_bag_visible():
            self.player_ui.bag_sprite_group.draw(self.display)

        self.display_text_group.draw(self.display)
        self.context_group.draw(self.display)

        pygame.display.flip()

    def change_map(self, map_to_load):
        self.background_group.add(map_to_load.background)
        self.load_items(map_to_load)
        self.player_ui.waypoints = map_to_load.waypoints
        self.find_spawn_for_player()

    def load_items(self, map_to_load):
        self.map_items = map_to_load.items
        for item_ui in self.map_items:
            item_ui.item.parent_container = self.map_items

    def find_spawn_for_player(self):
        self.player_ui.find_spawn()

    def resume(self):
        print("Resuming World")

    def pause(self):
        print("Pausing World")

    def tear_down(self):
        print("Tearing-Down World")

    def update_visible_items(self):
        for item_ui in self.map_items:
            if item_ui.item.visible and item_ui not in self.item_group:
                self.item_group.add(item_ui)
