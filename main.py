import pygame
import numpy as np
import random

from collections import deque


import generate_terrain as gt
import generate_terrain as gtc
import settings
import tools
import sprites
import gui

def main():    
    pygame.init()
    screen = pygame.display.set_mode(settings.resolution)

    large_font = pygame.font.Font(None, 64)
    font = pygame.font.Font(None, 32)

    seed = 0
    scale = 1
    offset = [0, 0]
    zoom_origin = [0, 0]
    zoom_queue = deque()
    zoom_ticks = 15

    count = 0
    cash = 0
    points = 1
    difficulty = 20

    grid = gtc.generate_terrain(power=6,
                                roughness=1,
                                seed=5,
                                smoothing_factor=1)

    towers_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()

    initial_tower1 = sprites.Bait(pos=(21, 20), cells=grid)
    towers_group.add(initial_tower1)

    initial_tower = sprites.Bait(pos=(25, 20), cells=grid)
    towers_group.add(initial_tower)

    initial_tower = sprites.Bait(pos=(11, 30), cells=grid)
    towers_group.add(initial_tower)

    initial_tower = sprites.Bait(pos=(1, 40), cells=grid)
    towers_group.add(initial_tower)

    initial_tower = sprites.Bait(pos=(8, 10), cells=grid)
    towers_group.add(initial_tower)
    
  
    # Variables to track continuous movement
    move_keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_RIGHT: False, pygame.K_LEFT: False,
                 pygame.K_w: False, pygame.K_s: False, pygame.K_d: False, pygame.K_a: False}
    move_speed = 5  # Adjust the movement speed as needed

    clock = pygame.time.Clock()

    enemy = sprites.Basic()
    enemy.spawn(grid, offset, scale)
    enemies_group.add(enemy)

    running = True
    paused = False

    while running:
        if not paused:
            elapsed_time = pygame.time.get_ticks()
            count += 1
            points += 0.01 * difficulty
            difficulty += 0.00001
            base_income = difficulty * 0.01
            cash += base_income

            if count % 360 == 0:
                for _ in range(int(difficulty)): 
                    enemy = sprites.Basic()
                    enemy.spawn(grid, offset, scale)
                    enemies_group.add(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Track key states
            elif event.type == pygame.KEYDOWN:
                if event.key in move_keys: move_keys[event.key] = True

                # Zoom keys
                if event.key == pygame.K_i and scale >= 0.5 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks): zoom_queue.append(-scale / 2 / zoom_ticks)
                if event.key == pygame.K_o and scale <= 8 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks): zoom_queue.append(scale / zoom_ticks)

                # Misc keys
                if event.key == pygame.K_SPACE:
                    paused = not paused

            elif event.type == pygame.KEYUP:
                if event.key in move_keys:
                    move_keys[event.key] = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and scale <= 8 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks): zoom_queue.append(scale / zoom_ticks)
                elif event.button == 5 and scale >= 0.5 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks): zoom_queue.append(-scale / 2 / zoom_ticks)

        # Update movement based on key states
        if move_keys[pygame.K_UP] or move_keys[pygame.K_w]:
            offset[1] += move_speed
        if move_keys[pygame.K_DOWN] or move_keys[pygame.K_s]:
            offset[1] -= move_speed
        if move_keys[pygame.K_RIGHT] or move_keys[pygame.K_d]:
            offset[0] -= move_speed
        if move_keys[pygame.K_LEFT] or move_keys[pygame.K_a]:
            offset[0] += move_speed

        # Apply any user requested zoom adjustments
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


        if not zoom_queue:
            scale = round(scale * 2) / 2

        screen.fill((0, 0, 0))  # Fill the screen with black
        tools.draw_grid(screen, grid, scale, offset)

        towers_group.update(screen, scale, offset, paused)
        enemies_group.update(screen, grid, towers_group, enemies_group, scale, offset, paused)

        cursor_xy = tools.get_cursor_xy(grid, scale, offset, size = 5)

        hovered_tower = None
        hovered_enemies = []
        for tower in towers_group:
            if tower.grid_pos == cursor_xy:
                hovered_tower = tower

        for enemy in enemies_group:
            if tuple(reversed(enemy.hitbox.topleft)) == cursor_xy:
                hovered_enemies.append(enemy)
                
        # gui.display_tower_stats(screen, font, tower, stats_rect)

        gui.render_gui(screen,
                       large_font, font,
                       paused, elapsed_time, points, difficulty, cash,
                       hovered_tower, hovered_enemies)

        pygame.display.update()
        clock.tick(60)  # Limit frame rate to 60 FPS

    pygame.quit()

if __name__ == '__main__':
    main()
