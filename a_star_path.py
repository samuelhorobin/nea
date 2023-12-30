import numpy as np
import heapq

def heuristic(node, goal):
    # Manhattan distance heuristic
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

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
    previous_nodes = {}

    heap = [(0, start)]  # Priority queue [(f_score, node)]
    while heap:
        _, current = heapq.heappop(heap)

        if current == end:
            path = []
            while current in previous_nodes:
                path.append(current)
                current = previous_nodes[current]
            path.append(start)
            return path[::-1]

        for neighbor in get_neighbors(grid, current):
            change = grid[neighbor] - grid[current]
            cost = max(change, 10)  # Cost is the change; if negative, set to 10

            tentative_dist = distances[current] + cost
            if tentative_dist < distances[neighbor]:
                distances[neighbor] = tentative_dist
                previous_nodes[neighbor] = current
                f_score = tentative_dist + heuristic(neighbor, end)
                heapq.heappush(heap, (f_score, neighbor))

    return None  # If there is no path from start to end

if __name__ == '__main__':
    # Your grid and node definitions remain the same
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
