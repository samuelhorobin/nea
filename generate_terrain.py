import numpy as np
import pygame
import tools

def generate_terrain(power=6, roughness=1, seed=1, smoothing_factor=1):
    '''
    Generates a terrain map using the diamond-square algorithm.

    Parameters:
    - power: Integer, the size of the terrain will be 2^power + 1.
    - roughness: Float, controls the roughness of the terrain.
    - seed: Integer, seed for random number generation.
    - smoothing_factor: Integer, number of times to apply terrain smoothing.

    Returns:
    - 2D NumPy array representing the generated terrain.
    '''

    size = 2**power + 1
    np.random.seed(seed)

    terrain = np.zeros((size, size), dtype=float)
    corners = [(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)]
    for corner in corners:
        terrain[corner] = np.random.uniform(0, 1)

    step = size - 1
    while step > 1:
        half = step // 2
        for y in range(0, size - 1, step):
            for x in range(0, size - 1, step):
                average = (
                    terrain[y, x]
                    + terrain[y + step, x]
                    + terrain[y, x + step]
                    + terrain[y + step, x + step]
                ) / 4.0
                terrain[y + half, x + half] = average + np.random.uniform(-roughness, roughness)

        for y in range(0, size - 1, step):
            for x in range(0, size - 1, step):
                left = terrain[y + half, x]
                right = terrain[y + half, x + step]
                top = terrain[y, x + half]
                bottom = terrain[y + step, x + half]

                terrain[y + half, x] = (terrain[y, x] + terrain[y + step, x] + top + left) / 4.0 + np.random.uniform(
                    -roughness, roughness
                )
                terrain[y + half, x + step] = (
                    terrain[y, x + step] + terrain[y + step, x + step] + top + right
                ) / 4.0 + np.random.uniform(-roughness, roughness)
                terrain[y, x + half] = (terrain[y, x] + terrain[y, x + step] + top + left) / 4.0 + np.random.uniform(
                    -roughness, roughness
                )
                terrain[y + step, x + half] = (
                    terrain[y + step, x] + terrain[y + step, x + step] + bottom + right
                ) / 4.0 + np.random.uniform(-roughness, roughness)
        step = half

    # Apply smoothing
    for _ in range(smoothing_factor):
        terrain = smooth_terrain(terrain)

    # Trim the sides
    terrain = terrain[1:-1, 1:-1]

    for row, col in np.ndindex(terrain.shape):
        terrain[row, col] = tools.float_to_color(terrain[row, col])

    return terrain

def smooth_terrain(terrain):
    '''
    Applies smoothing to the terrain.

    Parameters:
    - terrain: 2D NumPy array representing the terrain.

    Returns:
    - 2D NumPy array, the smoothed terrain.
    '''

    # Simple averaging smoothing function
    smoothed_terrain = terrain.copy()

    for row, col in np.ndindex(terrain.shape):
        smoothed_terrain[row, col] = np.sum(terrain[row - 1:row + 2, col-1:col+2]) / 9

    return smoothed_terrain

def visualize_terrain(terrain):
    '''
    Visualizes the terrain using Pygame.

    Parameters:
    - terrain: 2D NumPy array representing the terrain.
    '''

    pygame.init()

    size = terrain.shape[0]
    scale = 6  # Scale for visualization

    screen = pygame.display.set_mode((size * scale, size * scale))
    pygame.display.set_caption("Terrain Visualization")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        for y in range(size):
            for x in range(size):
                height = tools.change_hue(gray_color=tools.float_to_color(terrain[x, y]),
                                    new_hue=145)
                
                # Ensure color_index stays within the bounds of the colors list
                pygame.draw.rect(screen, (height), (x * scale, y * scale, scale, scale))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    terrain = generate_terrain(power=6, roughness=0.5, smoothing_factor=1)
    visualize_terrain(terrain)
