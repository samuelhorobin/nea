import numpy as np
import heapq  # Import heapq for priority queue operations

def get_neighbors(grid, node):
    """
    Get all valid neighbors of a given node within the grid.
    
    Parameters:
    - grid: The 2D numpy array representing the grid.
    - node: A tuple (row, col) representing the current node.
    
    Returns:
    - A list of tuples, where each tuple is a valid neighboring node.
    """
    rows, cols = grid.shape
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # Possible movement directions
    neighbors = []

    for direction in directions:
        new_row, new_col = node[0] + direction[0], node[1] + direction[1]
        if 0 <= new_row < rows and 0 <= new_col < cols:  # Ensure within grid bounds
            neighbors.append((new_row, new_col))

    return neighbors

def path_find(grid, start, end):
    """
    Find the shortest path from start to end node in a grid, considering terrain cost.
    
    Parameters:
    - grid: 2D numpy array representing the grid with terrain costs.
    - start: Starting node as a tuple (row, col).
    - end: Ending node as a tuple (row, col).
    
    Returns:
    - A list of nodes (as tuples) representing the shortest path, including start and end.
    """
    rows, cols = grid.shape

    distances = np.full_like(grid, np.inf, dtype=float)  # Initialize distances to infinity
    distances[start] = 0  # Distance from start to itself is 0
    visited = set()  # Track visited nodes to avoid reprocessing
    previous_nodes = {}  # Map each node to its predecessor on the shortest path

    # Priority queue to store nodes by their current known shortest distance
    pq = []
    heapq.heappush(pq, (0, start))  # Start node with distance 0

    while pq:
        current_dist, current_node = heapq.heappop(pq)  # Node with the smallest distance

        if current_node in visited:
            continue  # Skip nodes that have been visited
        visited.add(current_node)

        if current_node == end:
            # Path found, reconstruct it from end to start using previous_nodes
            path = []
            while current_node in previous_nodes:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.append(start)
            return path[::-1]  # Return reversed path, from start to end

        # Explore neighbors
        for neighbor in get_neighbors(grid, current_node):
            if neighbor in visited:
                continue  # Skip already visited neighbors

            # Calculate new distance to neighbor considering the terrain cost
            change = grid[neighbor] - grid[current_node]
            cost = max(change, 10)  # Cost is the change; if negative, set to 10
            new_dist = distances[current_node] + cost

            # Update neighbor's distance and path if a shorter path is found
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))  # Re-add neighbor with new distance

    return None  # If no path is found

if __name__ == '__main__':
    # Example grid (terrain costs) and start/end nodes
    grid = np.array([
        [90, 0,   0,  0,   5],
        [90, 90,  0,  90,  5],
        [5,  90,  0,  90,  5],
        [5,  90,  90, 90,  5],
        [5,  5,   5,   5,  5]
    ])
    start_node = (0, 0)
    end_node = (4, 4)

    # Find and print the shortest path
    path = path_find(grid, start_node, end_node)
    if path:
        print("Shortest Path:")
        for node in path:
            print(node)
    else:
        print("No path found.")
