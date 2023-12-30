import numpy as np
import cProfile

def get_neighbors(grid, node):
    rows, cols = grid.shape
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    neighbors = []

    for direction in directions:
        new_row, new_col = node[0] + direction[0], node[1] + direction[1]
        if 0 <= new_row < rows and 0 <= new_col < cols:
            neighbors.append((new_row, new_col))

    return neighbors

def path_find(grid, start, end):
    rows, cols = grid.shape

    distances = np.full_like(grid, np.inf, dtype=float)
    distances[start] = 0
    visited = set()
    previous_nodes = {}

    while True:
        min_dist = np.inf
        min_node = None

        for node in np.ndindex(grid.shape):
            if node not in visited and distances[node] < min_dist:
                min_dist = distances[node]
                min_node = node

        if min_node is None:
            break

        visited.add(min_node)

        if min_node == end:
            path = []
            while min_node in previous_nodes:
                path.append(min_node)
                min_node = previous_nodes[min_node]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(grid, min_node):
            change = grid[neighbor] - grid[min_node]
            cost = max(change, 10)  # Cost is the change; if negative, set to 1

            new_dist = distances[min_node] + cost
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous_nodes[neighbor] = min_node

    return None  # If there is no path from start to end

if __name__ == '__main__':
    grid = np.array([
        [90, 0,   0,  0,   5],
        [90, 90,  0,  90,  5],
        [5,  90,  0,  90,  5],
        [5,  90,  90, 90,  5],
        [5,  5,   5,   5,  5]
    ])

    start_node = (0, 0)
    end_node = (4, 4)
    path = path_find(grid, start_node, end_node)

    if path:
        for node in path:
            print(node)
