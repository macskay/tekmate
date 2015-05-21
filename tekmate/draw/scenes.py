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

    STOP_DISPLAY_TEXT_EVENT = pygame.USEREVENT + 1

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

    def update(self):
        clock = self.game.update_context["clock"]
        delta = clock.tick(1000)

        self.update_visible_items()
        self.animation_group.update(delta)
        self.stop_animation_when_player_reached_destination()

        for event in self.game.update_context["get_events"]():
            self.handle_input(event)

        self.default_group.update()

    def update_visible_items(self):
        for item_ui in self.map_items:
            if item_ui.item.visible and item_ui not in self.item_group:
                self.item_group.add(item_ui)

    def stop_animation_when_player_reached_destination(self):
        if self.player_ui.rect.bottomleft == self.last_destination:
            self.player_ui.reset_walk()
            pygame.time.set_timer(UI.WALK_EVENT, 0)
            self.last_destination = (0, 0)

    def handle_input(self, event):
        self.handle_close_game_event(event)
        self.handle_mouse_button_pressed_event(event)
        self.handle_i_key_pressed_event(event)
        self.handle_ui_events(event)
        self.handle_logging_events(event)

    def handle_close_game_event(self, event):
        if event.type == pygame.QUIT or self.is_escape_key_pressed(event):
            raise Game.GameExitException

    def is_escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def handle_mouse_button_pressed_event(self, event):
        self.handle_mouse_left_event(event)
        self.handle_mouse_right_event(event)

    def handle_mouse_left_event(self, event):
        if self.is_left_mouse_pressed(event):
            self.process_left_mouse_button_pressed(event)

    def is_left_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def process_left_mouse_button_pressed(self, event):
        self.handle_opened_context_menu(event.pos) if self.is_context_menu_visible() else self.move_player(event.pos)

    def is_context_menu_visible(self):
        return self.context_menu.alive()

    def handle_opened_context_menu(self, mouse_pos):
        self.process_button_command(mouse_pos) if self.is_context_menu_clicked_on(mouse_pos) else self.close_context_menu()

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

    def move_player(self, pos, callback=None):
        if not self.is_bag_visible():
            direction = self.get_direction(pos)
            self.best_path = self.find_shortest_path_to_destination(pos, direction)
            self.callback = callback
            self.move_to_next_waypoint()

    def get_direction(self, pos):
        return 1 if pos[0] > self.player_ui.rect.left else -1

    def find_shortest_path_to_destination(self, pos, dir):
        return self.player_ui.find_shortest_path_to_destination(pos, dir)

    def move_to_next_waypoint(self):
        self.trigger_next_animation() if self.is_next_waypoint_not_last_waypoint() \
            else self.trigger_last_animation_and_execute_interaction()

    def trigger_next_animation(self):
        pos = self.best_path[0].pos
        self.best_path.pop(0)
        self.start_walk_animation(self.move_to_next_waypoint, pos)

    def is_next_waypoint_not_last_waypoint(self):
        return len(self.best_path) > 1

    def start_walk_animation(self, callback, pos):
        ani = self.player_ui.move(pos)
        if callback is not None:
            ani.callback = lambda: callback()
        ani.start(self.player_ui.rect)
        self.animation_group.add(ani)
        pygame.time.set_timer(UI.WALK_EVENT, 100)

    def trigger_last_animation_and_execute_interaction(self):
        pos = self.best_path[0].pos
        self.best_path.pop(0)
        self.start_walk_animation(self.callback, pos)
        self.last_destination = pos

    def walk_to_item_before_interacting(self, callback):
        if self.is_target_in_range():
            self.face_target(self.current_observed_item)
            callback()
        else:
            self.move_player(self.current_observed_item.rect.center, callback)

    def face_target(self, target):
        self.player_ui.face_target(target)

    def is_target_in_range(self):
        return abs(self.player_ui.rect.left - self.current_observed_item.rect.left) < 100

    def take_item(self):
        add_message = self.player_ui.add_item(self.current_observed_item, self.map_items)
        self.show_display_text(add_message)
        self.current_observed_item = None

    def show_display_text(self, message):
        self.message_system.display_text(message, self.player_ui)
        self.message_system.add(self.display_text_group)
        pygame.time.set_timer(self.STOP_DISPLAY_TEXT_EVENT, 2000)

    def look_at_item(self):
        self.show_display_text(self.current_observed_item.look_at())

    def use_item(self):
        self.show_display_text(self.current_observed_item.use())

    def inspect_item(self):
        return self.current_observed_item.inspect()

    def select_item(self):
        self.current_selected_item = self.current_observed_item
        item_name = self.get_name_of_item()
        self.show_display_text("What should I do with this %s?" % item_name)

    def get_name_of_item(self):
        return self.current_observed_item.get_name()

    def combine_items(self):
        reason = self.player_ui.combine_items(self.current_selected_item,
                                              self.current_observed_item)
        self.show_display_text(reason)
        self.current_selected_item = None
        self.current_observed_item = None

    def get_button_pressed(self, mouse_pos):
        return self.context_menu.get_button_pressed(mouse_pos)

    def close_context_menu(self):
        self.context_menu.remove(self.context_group)

    def is_bag_visible(self):
        return self.player_ui.is_bag_visible()

    def handle_mouse_right_event(self, event):
        if self.is_right_mouse_pressed(event):
            self.process_right_mouse_pressed(event.pos)

    def is_right_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 3

    def process_right_mouse_pressed(self, pos):
        if len(self.animation_group) > 0:
            self.animation_group.empty()
        clicked_in_bag_but_not_on_item = self.select_correct_context_menu_list(pos)
        self.close_context_menu() if clicked_in_bag_but_not_on_item else self.open_context_menu(pos)

    def select_correct_context_menu_list(self, pos):
        self.set_context_menu(ContextMenuUI.CONTEXT_MENU_DEFAULT)
        if self.is_mouse_pos_inside_world_item(pos) and not self.is_bag_visible():
            self.set_world_item_context_menu()
        elif self.is_mouse_pos_inside_bag_item(pos):
            self.set_bag_item_world_context_menu()
        else:
            self.handle_bag_open_right_click()
        return False

    def set_context_menu(self, layout):
        self.context_menu.build_context_menu(layout)

    def is_mouse_pos_inside_world_item(self, pos):
        is_item_clicked = False
        for item in self.item_group.sprites():
            if item.rect.collidepoint(pos):
                self.current_observed_item = item
                is_item_clicked = True
        return is_item_clicked

    def set_world_item_context_menu(self):
        self.set_context_menu(ContextMenuUI.CONTEXT_COMBINE_ITEM) if self.current_selected_item is not None \
            else self.set_context_menu(ContextMenuUI.CONTEXT_MENU_ITEM)

    def is_mouse_pos_inside_bag_item(self, pos):
        for item in self.player_ui.bag_sprite_group.sprites()[1:]:
            if item.rect.collidepoint(pos):
                self.current_observed_item = item
                return True
        return False

    def set_bag_item_world_context_menu(self):
        self.set_context_menu(ContextMenuUI.CONTEXT_MENU_BAG_ITEM)

    def handle_bag_open_right_click(self):
        return True if self.is_bag_visible() else False

    def open_context_menu(self, pos):
        self.context_menu.open(pos)
        self.context_menu.add(self.context_group)

    def handle_i_key_pressed_event(self, event):
        if self.is_i_pressed(event):
            if not self.context_menu.alive():
                self.handle_bag()

    def is_i_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_i

    def handle_bag(self):
        self.player_ui.bag_visible = True if not self.is_bag_visible() else False

    def render(self):
        self.display.fill((0, 0, 0))

        self.background_group.draw(self.display)
        self.item_group.draw(self.display)
        self.default_group.draw(self.display)
        self.render_bag()
        self.display_text_group.draw(self.display)
        self.context_group.draw(self.display)

        pygame.display.flip()

    def render_bag(self):
        if self.is_bag_visible():
            self.player_ui.bag_sprite_group.draw(self.display)

    def handle_ui_events(self, event):
        self.handle_walk_event(event)
        self.handle_crouch_event(event)
        self.handle_crouch_stop_event(event)
        self.handle_text_displaying_event(event)

    def handle_walk_event(self, event):
        if self.is_player_walking(event):
            self.player_ui.animate_walk()

    def is_player_walking(self, event):
        return event.type == UI.WALK_EVENT

    def handle_crouch_event(self, event):
        if self.is_player_crouching(event):
            self.handle_pickup_with_delay_event() if self.player_ui.is_waiting_for_crouch else \
                self.handle_put_down_without_delay_event()

    def is_player_crouching(self, event):
        return event.type == UI.CROUCH_EVENT

    def handle_pickup_with_delay_event(self):
        self.player_ui.is_waiting_for_crouch = False
        pygame.time.wait(1000)

    def handle_put_down_without_delay_event(self):
        self.player_ui.animate_crouch()

    def handle_crouch_stop_event(self, event):
        if event.type == UI.STOP_CROUCH_EVENT:
            self.reset_crouching_event()

    def reset_crouching_event(self):
        self.player_ui.reset_crouch()
        pygame.time.set_timer(UI.CROUCH_EVENT, 0)

    def handle_text_displaying_event(self, event):
        if self.is_text_displayed_long_enough(event):
            self.hide_displayed_text()

    def is_text_displayed_long_enough(self, event):
        return event.type == self.STOP_DISPLAY_TEXT_EVENT

    def hide_displayed_text(self):
        self.display_text_group.empty()
        pygame.time.set_timer(self.STOP_DISPLAY_TEXT_EVENT, 0)

    def handle_logging_events(self, event):
        if event.type == self.FPS_EVENT:
            logger.debug("FPS: %s" % self.game.update_context["clock"].get_fps())

    def resume(self):
        print("Resuming World")

    def pause(self):
        print("Pausing World")

    def tear_down(self):
        print("Tearing-Down World")