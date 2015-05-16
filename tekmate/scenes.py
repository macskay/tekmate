# -*- encoding: utf-8 -*-
from functools import partial
import math
import pygame
from taz.game import Scene, Game
from tekmate.messages import MessageSystem

from tekmate.ui import ContextMenuUI, PlayerUI


class WorldScene(Scene):
    def __init__(self, ident):
        super(WorldScene, self).__init__(ident)
        self.display = None

        self.context_menu = ContextMenuUI()
        self.player_ui = PlayerUI()
        self.message_system = MessageSystem()

        self.waypoints = list()

        self.item_group = pygame.sprite.OrderedUpdates()
        self.default_group = pygame.sprite.OrderedUpdates()
        self.context_group = pygame.sprite.OrderedUpdates()
        self.display_text_group = pygame.sprite.GroupSingle()
        self.background_group = pygame.sprite.GroupSingle()
        self.animation_group = pygame.sprite.GroupSingle()

        self.current_observed_item = None
        self.current_selected_item = None

    def initialize(self):  # pragma: no cover
        self.display = self.game.render_context["display"]

        self.change_map(self.game.update_context["maps"]["example"])
        self.default_group.add(self.player_ui)

    def update(self):
        clock = self.game.update_context["clock"]
        delta = clock.tick(60)

        self.animation_group.update(delta)
        for event in self.game.update_context["get_events"]():
            self.handle_input(event)

    def handle_input(self, event):
        if event.type == pygame.QUIT or self.is_escape_key_pressed(event):
            raise Game.GameExitException
        elif self.is_right_mouse_pressed(event):
            self.process_right_mouse_pressed(event.pos)
        elif self.is_left_mouse_pressed(event):
            self.process_left_mouse_button_pressed(event)
        elif self.is_i_pressed(event):
            if not self.context_menu.alive():  # pragma: no cover (implicit else)
                self.handle_bag()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:  # pragma: no cover (just debugging)
            print(self.current_selected_item.item.get_name() + " is currently selected.")
        elif event.type == pygame.USEREVENT:  # pragma: no cover
            self.display_text_group.empty()
            pygame.time.set_timer(pygame.USEREVENT, 0)

    def is_escape_key_pressed(self, event):
        return event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE

    def is_right_mouse_pressed(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 3

    def process_right_mouse_pressed(self, pos):  # pragma: no cover
        if len(self.animation_group) > 0:
            self.animation_group.empty()
        clicked_in_bag_but_not_on_item = self.select_correct_context_menu_list(pos)
        if clicked_in_bag_but_not_on_item:
            self.close_context_menu()
        else:
            self.open_context_menu(pos)

    def select_correct_context_menu_list(self, pos):  # pragma: no cover
        self.set_context_menu(ContextMenuUI.CONTEXT_MENU_DEFAULT)
        if self.is_mouse_pos_inside_world_item(pos) and not self.is_bag_visible():
            self.set_world_item_context_menu()
        elif self.is_mouse_pos_inside_bag_item(pos):
            self.set_bag_item_world_context_menu()
        else:
            if self.is_bag_visible():    # pragma: no cover
                return True
        return False

    def is_mouse_pos_inside_world_item(self, pos):
        for item in self.item_group.sprites():
            if item.rect.collidepoint(pos):  # pragma: no cover (implicit else, nothing happening here)
                self.current_observed_item = item
                return True
        return False

    def is_bag_visible(self):
        return self.player_ui.is_bag_visible()

    def set_world_item_context_menu(self):  # pragma: no cover
        if self.current_selected_item is not None:
            self.set_context_menu(ContextMenuUI.CONTEXT_COMBINE_ITEM)
        else:
            self.set_context_menu(ContextMenuUI.CONTEXT_MENU_ITEM)

    def set_context_menu(self, layout):
        self.context_menu.build_context_menu(layout)

    def is_mouse_pos_inside_bag_item(self, pos):
        for item in self.player_ui.bag_sprite_group.sprites()[1:]:
            if item.rect.collidepoint(pos):  # pragma: no cover (implicit else, nothing happening here)
                self.current_observed_item = item
                return True
        return False

    def set_bag_item_world_context_menu(self):  # pragma: no cover
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
            if not self.is_bag_visible():  # pragma: no cover (implicit else)
                self.move_player(event.pos)

    def is_context_menu_visible(self):
        return self.context_menu.alive()

    def handle_opened_context_menu(self, mouse_pos):
        if self.is_context_menu_clicked_on(mouse_pos):     # pragma: no cover
            self.process_button_command(mouse_pos)
        else:
            self.close_context_menu()

    def is_context_menu_clicked_on(self, pos):
        return self.context_menu.rect.collidepoint(pos)

    def process_button_command(self, mouse_pos):   # pragma: no cover
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
        print(abs(self.player_ui.rect.left - self.current_observed_item.rect.left))
        if abs(self.player_ui.rect.left - self.current_observed_item.rect.left) < 100:
            callback()
        else:  # pragma: no cover
            self.move_player(self.current_observed_item.rect.center, callback)

    def move_player(self, pos, callback=None):
        closest_waypoint = self.find_closest_waypoint_to_destination(pos)
        self.print_closest_neighbors(closest_waypoint)
        self.start_animation(callback, pos)

    def find_closest_waypoint_to_destination(self, pos):
        closest_waypoint = None
        smallest_distance = 3000
        for waypoint in self.waypoints:
            distance = self.calculate_euclidean_distance(pos, waypoint)
            if distance < smallest_distance:
                smallest_distance = distance
                closest_waypoint = waypoint
        return closest_waypoint

    def print_closest_neighbors(self, closest_waypoint):
        print("Closed Waypoint: %s" % closest_waypoint.name)
        print("Closed Waypoint's neighbors: %s\n" % closest_waypoint.neighbors)
        for waypoint in self.waypoints:
            if waypoint.pos == self.player_ui.rect.bottomleft:
                print("My waypoint: %s" % waypoint.name)
                print("My neighbors: %s\n" % waypoint.neighbors)

    def start_animation(self, callback, pos):
        ani = self.player_ui.move(pos)
        if callback is not None:  # pragma: no cover
            ani.callback = lambda: callback()
        ani.start(self.player_ui.rect)
        self.animation_group.add(ani)

    def calculate_euclidean_distance(self, pos, waypoint):
        waypoint_center_x = waypoint.pos[0]+waypoint.width / 2
        waypoint_center_y = waypoint.pos[1]-waypoint.height / 2
        euclidean_distance = int(math.sqrt((pos[0]-waypoint_center_x)*(pos[0]-waypoint_center_x) +
                                           (pos[1]-waypoint_center_y)*(pos[1]-waypoint_center_y)))
        return euclidean_distance

    def take_item(self):  # pragma: no cover
        self.player_ui.add_item(self.current_observed_item)
        item_name = self.get_name_of_item()
        self.show_display_text("Alright, I think I'll take that %s with me!" % item_name)
        self.current_observed_item = None

    def combine_items(self):
        self.player_ui.combine_items(self.current_selected_item, self.current_observed_item)
        self.look_at_item()
        self.current_selected_item = None
        self.current_observed_item = None

    def look_at_item(self):
        self.show_display_text(self.current_observed_item.look_at())

    def use_item(self):  # pragma: no cover
        self.show_display_text(self.current_observed_item.use())

    def inspect_item(self):     # pragma: no cover
        return self.current_observed_item.inspect()

    def get_name_of_item(self):
        return self.current_observed_item.item.get_name()

    def select_item(self):
        self.current_selected_item = self.current_observed_item
        item_name = self.get_name_of_item()
        self.show_display_text("What should I do with this %s?" % item_name)

    def show_display_text(self, message):
        self.message_system.display_text(message, self.player_ui)
        self.message_system.add(self.display_text_group)
        pygame.time.set_timer(pygame.USEREVENT, 2000)

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

    def resume(self):  # pragma: no cover
        print("Resuming World")

    def pause(self):  # pragma: no cover
        print("Pausing World")

    def tear_down(self):  # pragma: no cover
        print("Tearing-Down World")

    def change_map(self, map_to_load):
        self.background_group.add(map_to_load.background)
        self.load_items(map_to_load)
        self.waypoints = map_to_load.waypoints
        self.find_spawn_for_player()

    def load_items(self, map_to_load):
        for item in map_to_load.items:
            self.item_group.add(item)

    def find_spawn_for_player(self):
        for waypoint in self.waypoints:
            if waypoint.is_spawn:
                self.set_player_start(waypoint)

    def set_player_start(self, waypoint):
        self.player_ui.rect.bottomleft = waypoint.pos



