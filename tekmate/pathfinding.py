import math


class AStar(object):
    def __init__(self, nodes, start, destination):
        self.destination = destination
        self.start = start
        self.nodes = nodes
        self.closed_list = list()
        self.open_list = list()

        self.add_start_to_open_list()

    @staticmethod
    def calculate_euclidean_distance(a, b):
        euclidean_distance_exact = math.sqrt((a[0] - b[0]) * (a[0] - b[0]) +
                                             (a[1] - b[1]) * (a[1] - b[1]))
        return int(euclidean_distance_exact)

    def add_start_to_open_list(self):
        distance = self.calculate_euclidean_distance(self.start.pos, self.destination.pos)
        self.open_list.append((self.start, distance))

    def append_neighbors_to_list(self, node):
        for name, waypoint in node.neighbors.items():
            euclidean_neighbor_destination = self.calculate_euclidean_distance(waypoint.pos, self.destination.pos)
            if not self.is_in_list(self.closed_list, name) and not self.is_in_list(self.open_list, name):
                self.open_list.append((waypoint, euclidean_neighbor_destination))

    def is_in_list(self, node_list, name):
        for node in node_list:
            if node[0].name == name:
                return True
        else:
            return False

    def find_shortest_path(self):
        best_path = list()
        while not self.is_destination_only_node_in_open_list():
            node_with_shortest_path_to_destination = self.get_shortest_node()
            best_path.append(node_with_shortest_path_to_destination[0])
            self.append_neighbors_to_list(node_with_shortest_path_to_destination[0])

            self.open_list.remove(node_with_shortest_path_to_destination)
            self.closed_list.append(node_with_shortest_path_to_destination)
        best_path.append(self.destination)
        return best_path

    def is_destination_only_node_in_open_list(self):
        return self.get_shortest_node()[0] == self.destination

    def get_shortest_node(self):
        smallest_node = None, 999999
        for node in self.open_list:
            if node[1] < smallest_node[1]:  # pragma: no cover (implicit else, nothing happens when else is hit)
                smallest_node = node[0], node[1]
        return smallest_node
