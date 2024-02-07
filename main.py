# Import necessary libraries
import pygame
import numpy as np
import random
from collections import deque

# Import custom modules
import generate_terrain as gt
import generate_terrain as gtc
import settings
import tools
import sprites
import gui

# Define a class to store game data
class Game_Data:
    count = 1
    animation_count = 0
    cash = 240
    points = 1
    difficulty = 1

# Main game function
def main():
    # Initialize Pygame
    pygame.init()
    # Set up the game screen
    screen = pygame.display.set_mode(settings.resolution)

    # Set up fonts for GUI
    large_font = pygame.font.Font(None, 64)
    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)

    # Initialize variables for terrain generation
    seed = 0
    scale = 1
    offset = [0, 0]
    zoom_queue = deque()
    zoom_ticks = 15

    # Define tower menu items
    menu_item1, menu_item2, menu_item3, menu_item4 = "$20: Wall", "$120: Sniper", "$240: Producer", "$800: Headquarters"
    tower_menu = tools.ExclusiveBooleanList(menu_item1, menu_item2, menu_item3, menu_item4)

    # Set grid size based on selected difficulty
    if settings.selected_difficulty == "easy":
        size = 6
    elif settings.selected_difficulty == "medium":
        size = 5
    elif settings.selected_difficulty == "hard":
        size = 4

    # Generate terrain grid
    grid = gtc.generate_terrain(power=size, roughness=1, seed=5, smoothing_factor=1)

    # Initialize tower grid and other variables
    tower_grid = np.full_like(grid, fill_value=None, dtype=object)
    placeable = False

    # Create Pygame sprite groups for towers and enemies
    towers_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()

    # Set enemy cap for the game
    enemy_cap = 80

    # Get grid dimensions
    width, height = grid.shape

    # Initialize the headquarters tower at the center of the grid
    initial_tower = sprites.Headquarters(pos=(height // 2 - 1, width // 2 - 1),
                                         cells=grid,
                                         tower_grid=tower_grid)
    towers_group.add(initial_tower)

    # Initialize movement-related variables
    move_keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_RIGHT: False, pygame.K_LEFT: False,
                 pygame.K_w: False, pygame.K_s: False, pygame.K_d: False, pygame.K_a: False}
    move_speed = 5  # Adjust the movement speed as needed

    clock = pygame.time.Clock()

    # Initialize the first basic enemy
    enemy = sprites.Basic(Game_Data)
    enemy.spawn(grid, offset, scale)
    enemies_group.add(enemy)

    running = True
    paused = False
    alive = True

    while running:
        Game_Data.animation_count += 1
        if not paused:
            # Check if the player has lost
            hq_count = 0
            for tower in towers_group:
                if tower.name == "Headquarters":
                    hq_count += 1
            if hq_count == 0:
                alive = False
                paused = True
            else:
                # Update game data and income
                elapsed_time = pygame.time.get_ticks()
                Game_Data.count += 1
                Game_Data.points += 0.01 * (Game_Data.difficulty / (Game_Data.count / 600))
                Game_Data.difficulty += 0.00001
                base_income = Game_Data.difficulty * 0.01
                Game_Data.cash += base_income

                # Spawn enemies based on game difficulty
                if Game_Data.difficulty >= 1 and Game_Data.count % 360 == 0:
                    for _ in range(int(Game_Data.difficulty)):
                        if len(enemies_group.sprites()) < enemy_cap:
                            enemy = sprites.Basic(Game_Data)
                            enemy.spawn(grid, offset, scale)
                            enemies_group.add(enemy)

                if Game_Data.difficulty >= 3 and Game_Data.count % 400 == 0:
                    for _ in range(int(Game_Data.difficulty // 2)):
                        if len(enemies_group.sprites()) < enemy_cap:
                            enemy = sprites.Runner(Game_Data)
                            enemy.spawn(grid, offset, scale)
                            enemies_group.add(enemy)

                if Game_Data.difficulty >= 5 and Game_Data.count % 800 == 0:
                    for _ in range(int(Game_Data.difficulty // 4)):
                        if len(enemies_group.sprites()) < enemy_cap:
                            enemy = sprites.Giant(Game_Data)
                            enemy.spawn(grid, offset, scale)
                            enemies_group.add(enemy)

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Track key states
                if event.key in move_keys:
                    move_keys[event.key] = True

                # Zoom keys
                if event.key == pygame.K_i and scale >= 0.5 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks):
                        zoom_queue.append(-scale / 2 / zoom_ticks)
                if event.key == pygame.K_o and scale <= 8 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks):
                        zoom_queue.append(scale / zoom_ticks)

                # Misc keys
                if event.key == pygame.K_SPACE:
                    paused = not paused

                # Select towers
                if event.key == pygame.K_1:
                    tower_menu.select(menu_item1)
                if event.key == pygame.K_2:
                    tower_menu.select(menu_item2)
                if event.key == pygame.K_3:
                    tower_menu.select(menu_item3)
                if event.key == pygame.K_4:
                    tower_menu.select(menu_item4)

            elif event.type == pygame.KEYUP:
                if event.key in move_keys:
                    move_keys[event.key] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse wheel events for zooming
                if event.button == 4 and scale <= 8 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks):
                        zoom_queue.append(scale / zoom_ticks)
                elif event.button == 5 and scale >= 0.5 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks):
                        zoom_queue.append(-scale / 2 / zoom_ticks)

                # Handle tower placement
                if placeable and event.button == 1:
                    if tower == menu_item1 and Game_Data.cash >= 20:
                        placed_tower = sprites.Wall(pos=(cursor_xy[0], cursor_xy[1]),
                                                    cells=grid,
                                                    tower_grid=tower_grid)
                        towers_group.add(placed_tower)
                        Game_Data.cash -= 20
                    if tower == menu_item2 and Game_Data.cash >= 120:
                        placed_tower = sprites.Sniper(pos=(cursor_xy[0], cursor_xy[1]),
                                                      cells=grid,
                                                      tower_grid=tower_grid)
                        towers_group.add(placed_tower)
                        Game_Data.cash -= 120
                    if tower == menu_item3 and Game_Data.cash >= 240:
                        placed_tower = sprites.Producer(pos=(cursor_xy[0], cursor_xy[1]),
                                                        cells=grid,
                                                        tower_grid=tower_grid)
                        towers_group.add(placed_tower)
                        Game_Data.difficulty += 1
                        Game_Data.cash -= 240
                    if tower == menu_item4 and Game_Data.cash >= 800:
                        placed_tower = sprites.Headquarters(pos=(cursor_xy[0], cursor_xy[1]),
                                                            cells=grid,
                                                            tower_grid=tower_grid)
                        towers_group.add(placed_tower)
                        Game_Data.cash -= 800

        # Update continuous movement based on key states
        if move_keys[pygame.K_UP] or move_keys[pygame.K_w]:
            offset[1] += move_speed
        if move_keys[pygame.K_DOWN] or move_keys[pygame.K_s]:
            offset[1] -= move_speed
        if move_keys[pygame.K_RIGHT] or move_keys[pygame.K_d]:
            offset[0] -= move_speed
        if move_keys[pygame.K_LEFT] or move_keys[pygame.K_a]:
            offset[0] += move_speed

        # Apply any user-requested zoom adjustments
        if zoom_queue:
            delta_scale = zoom_queue.popleft()
            scale += delta_scale

            zoom_constant = 10

            if delta_scale < 0:
                offset[0] += zoom_constant / scale
                offset[1] += zoom_constant / scale
            elif delta_scale > 0:
                offset[0] -= zoom_constant / scale
                offset[1] -= zoom_constant / scale

        # Round the scale to improve display
        if not zoom_queue:
            scale = round(scale * 2) / 2

        # Fill the screen with black
        screen.fill((0, 0, 0))
        # Draw the terrain grid
        tools.draw_grid(screen, grid, scale, offset)

        # Update and draw towers and enemies
        towers_group.update(screen, scale, offset, small_font, enemies_group, Game_Data, paused)
        enemies_group.update(screen, grid, towers_group, tower_grid, enemies_group, scale, offset, paused)

        # Get cursor position and check for tower placement
        cursor_xy = tools.get_cursor_xy(grid, scale, offset, size=5)
        hovered_tower = None
        hovered_enemies = []
        for tower in towers_group:
            if tower.grid_pos == cursor_xy:
                hovered_tower = tower

        for enemy in enemies_group:
            if tuple(reversed(enemy.hitbox.topleft)) == cursor_xy:
                hovered_enemies.append(enemy)

        # Check tower placement validity and display cursor information
        placeable = False
        if cursor_xy and not tower_menu.none_true():
            tower = tower_menu.return_true()

            if tower != menu_item4:
                placeable = tools.can_fit(dimensions=(1, 1), pos=cursor_xy, tower_grid=tower_grid)
            elif tower == menu_item4:
                placeable = tools.can_fit(dimensions=(2, 2), pos=cursor_xy, tower_grid=tower_grid)

            # Check if player has enough cash for tower placement
            if tower == menu_item1 and Game_Data.cash < 20:
                placeable = False
            if tower == menu_item2 and Game_Data.cash < 120:
                placeable = False
            if tower == menu_item3 and Game_Data.cash < 240:
                placeable = False
            if tower == menu_item4 and Game_Data.cash < 800:
                placeable = False

            # Display cursor information
            gui.cursor_place_tower(screen, scale, offset, cursor_xy, tower, small_font, Game_Data, placeable)

        # Render GUI elements
        gui.render_gui(screen,
                       large_font, font, small_font,
                       tower_menu,
                       paused, alive, elapsed_time, Game_Data,
                       hovered_tower, hovered_enemies)

        # Update display
        pygame.display.update()
        # Limit frame rate to 60 FPS
        clock.tick(60)

    # Quit Pygame when the game loop ends
    pygame.quit()

# Run the main function if the script is executed directly
if __name__ == '__main__':
    main()
