from unittest import TestCase
import pygame
from tekmate.configuration import MapLoader
from tekmate.pathfinding import AStar


class AStarTestCase(TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((0, 0))
        self.waypoints = self.create_waypoints()
        self.start = self.waypoints["waypoint_door"]
        self.destination = self.waypoints["waypoint_4"]
        self.a_star = AStar(self.waypoints, self.start, self.destination)

    def create_waypoints(self):
        map_loader = MapLoader().map_dict["example"]
        return map_loader.waypoints

    def test_when_creating_a_star_nodes_must_be_not_none(self):
        self.assertIsNotNone(self.a_star.nodes)
        self.assertIsNotNone(self.a_star.destination)

    def test_a_star_has_open_list(self):
        self.assertIsInstance(self.a_star.open_list, list)

    def test_a_star_has_closed_list(self):
        self.assertIsInstance(self.a_star.closed_list, list)

    def test_a_star_has_start_node_in_open_list_by_default(self):
        self.assertIn((self.start, 579), self.a_star.open_list)

    def test_calculate_euclidean_distance_returns_the_distance_between_a_and_b(self):
        a = (5, 5)
        b = (7, 2)
        self.assertEqual(self.a_star.calculate_euclidean_distance(a, b), 3)

    def test_append_neighbor_to_list_takes_neighbors_calculates_distance_to_dest_before_appending_to_open_list(self):
        euclidean = self.a_star.calculate_euclidean_distance(self.waypoints["waypoint_1"].pos, self.destination.pos)
        self.a_star.open_list[0] = (self.waypoints["waypoint_1"], euclidean)
        self.a_star.append_neighbors_to_list(self.waypoints["waypoint_1"])
        self.assertEqual(len(self.a_star.open_list), 4)

    def test_find_shortest_path_returns_the_shortet_path_from_a_to_b(self):
        best_path = self.a_star.find_shortest_path()
        self.assertEqual(len(best_path), 4)
