import pygame
import numpy as np
from collections import deque

import generate_terrain as gt
import generate_terrain as gtc
import settings
import tools
import sprites

def draw_grid(screen, cells, scale, offset):
    cursor_xy = get_cursor_xy(cells, scale, offset)

    for row, col in np.ndindex(cells.shape):
        color = tools.change_hue(gray_color=cells[row][col], 
                                 new_hue=145)
        size = 5

        if cursor_xy:
            if row == cursor_xy[0] or col == cursor_xy[1]:
                desaturate_val = 90
                color = tools.desaturate_color(color, desaturate_val)

        
        # Draw rectangles, using as background the screen value.
        pygame.draw.rect(screen, color,
                        (offset[0]*scale + col*size*scale, offset[1]*scale + row*size*scale,
                        size*scale, size*scale),
                        border_radius=1)

def get_cursor_xy(cells, scale, offset, size = 5):
    mouse_pos = pygame.mouse.get_pos()
    for row, col in np.ndindex(cells.shape):
        rect = pygame.rect.Rect(offset[0]*scale + col*size*scale, # x Pos
                                         offset[1]*scale + row*size*scale, # y Pos
                                         size*scale, size*scale)           # Size
        
        if rect.collidepoint(mouse_pos):
            return row, col



def main():    
    pygame.init()
    screen = pygame.display.set_mode(settings.resolution)

    seed = 0
    scale = 1
    offset = [0, 0]

    zoom_queue = deque()
    zoom_ticks = 15
    
    grid = gtc.generate_terrain(power=6)

    towers_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()

    initial_tower = sprites.Bait(pos=(20, 20), cells=grid)
    towers_group.add(initial_tower)

    for _ in range(10): 
        enemy = sprites.Enemy()
        enemy.spawn(grid, offset, scale)
        enemy.navigate_to(grid, (0,0))
        enemies_group.add(enemy)
  
    # Variables to track continuous movement
    move_keys = {pygame.K_UP: False, pygame.K_DOWN: False, pygame.K_RIGHT: False, pygame.K_LEFT: False,
                 pygame.K_w: False, pygame.K_s: False, pygame.K_d: False, pygame.K_a: False}
    move_speed = 5  # Adjust the movement speed as needed

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Track key states
            elif event.type == pygame.KEYDOWN:
                if event.key in move_keys: move_keys[event.key] = True

                if event.key == pygame.K_i and scale >= 0.5 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks): zoom_queue.append(-scale / 2 / zoom_ticks)
                if event.key == pygame.K_o and scale <= 8 and len(zoom_queue) == 0:
                    for _ in range(zoom_ticks): zoom_queue.append(scale / zoom_ticks)

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
            scale += zoom_queue.popleft()
        if not zoom_queue:
            scale = round(scale * 2) / 2

        screen.fill((0, 0, 0))  # Fill the screen with black
        draw_grid(screen, grid, scale, offset)

        towers_group.update(screen, scale, offset)
        enemies_group.update(screen, grid, scale, offset)

        # if pygame.time.get_ticks() % 1 == 0:
        #     enemy = sprites.Enemy()
        #     enemy.spawn(grid)
        #     enemies_group.add(enemy)

        pygame.display.update()
        clock.tick(60)  # Limit frame rate to 60 FPS

    pygame.quit()

if __name__ == '__main__':
    main()
