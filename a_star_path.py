import numpy as np
import heapq

def heuristic(node, goal):
    '''
    Calculates the Manhattan distance heuristic between a node and the goal.

    Parameters:
    - node: A tuple (x, y) representing the current node's coordinates.
    - goal: A tuple (x, y) representing the goal node's coordinates.

    Returns:
    - The Manhattan distance heuristic as an integer.
    '''
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])

def get_neighbors(grid, node):
    '''
    Finds the neighbors of a given node in a grid.

    Parameters:
    - grid: The 2D numpy array representing the grid.
    - node: A tuple (x, y) representing the node's coordinates.

    Returns:
    - A list of tuples, each representing the coordinates of a neighbor.
    '''
    rows, cols = grid.shape
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Possible movements: up, down, left, right
    neighbors = []

    # Loop through each possible movement direction
    for direction in directions:
        new_row, new_col = node[0] + direction[0], node[1] + direction[1]
        # Check if the new position is within the grid boundaries
        if 0 <= new_row < rows and 0 <= new_col < cols:
            neighbors.append((new_row, new_col))

    return neighbors

def path_find(grid, start, end):
    '''
    Finds a path from a start node to an end node in a grid using A* algorithm.

    Parameters:
    - grid: The 2D numpy array representing the grid.
    - start: A tuple (x, y) representing the start node's coordinates.
    - end: A tuple (x, y) representing the end node's coordinates.

    Returns:
    - A list of tuples representing the path from start to end, or None if no path exists.
    '''
    rows, cols = grid.shape

    distances = np.full_like(grid, np.inf, dtype=float)  # Initialize all distances to infinity
    distances[start] = 0  # The distance to the start node is 0
    previous_nodes = {}

    heap = [(0, start)]  # Priority queue for nodes to explore, starting with the start node

    while heap:
        _, current = heapq.heappop(heap)  # Pop the node with the lowest f_score

        if current == end:
            # Reconstruct the path from end to start by following previous nodes
            path = []
            while current in previous_nodes:
                path.append(current)
                current = previous_nodes[current]
            path.append(start)  # Add the start node
            return path[::-1]  # Return the path in start to end order

        # Explore neighbors of the current node
        for neighbor in get_neighbors(grid, current):
            change = grid[neighbor] - grid[current]  # Calculate terrain change
            cost = max(change, 10)  # Cost is the terrain change; if negative, set to 10

            # Calculate tentative distance to neighbor
            tentative_dist = distances[current] + cost
            if tentative_dist < distances[neighbor]:  # Check if a new shorter path is found
                distances[neighbor] = tentative_dist
                previous_nodes[neighbor] = current
                f_score = tentative_dist + heuristic(neighbor, end)  # Total cost of path to this neighbor
                heapq.heappush(heap, (f_score, neighbor))  # Add neighbor to the priority queue

    return None  # Return None if there is no path from start to end

# Example usage
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
