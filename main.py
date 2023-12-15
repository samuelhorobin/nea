import pygame
import numpy as np 

import generate_terrain as gt
import settings

def draw_grid(screen, cells, scale, offset):
    for row, col in np.ndindex(cells.shape):
        if cells[row][col] == 0: color = (0,   0,   0  )
        if cells[row][col] == 1: color = (255, 255, 255)
        if cells[row][col] == 2: color = (0,   255, 0  )
        size = 5
        
        # Draw rectangles, using as backgorund the screen value.
        pygame.draw.rect(screen, color,
                        (offset[0]*scale + col*size*scale, offset[1]*scale + row*size*scale,
                        size*scale, size*scale),
                        border_radius=1) 

def main():    
    pygame.init()
    screen = pygame.display.set_mode(settings.resolution)

    seed = 0
    scale = 1
    offset = [0, 0]
    grid = gt.generate_terrain()
  
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            # If key is pressed
            elif event.type == pygame.KEYDOWN:
                # Zoom
                if event.key == pygame.K_o:
                    if scale > 0.4: scale -= 0.2
                if event.key == pygame.K_i:
                    if scale < 3: scale += 0.2
                # Move
                if event.key == pygame.K_UP:
                    offset[1] -= 15
                if event.key == pygame.K_DOWN:
                    offset[1] += 15
                if event.key == pygame.K_RIGHT:
                    offset[0] += 15
                if event.key == pygame.K_LEFT:
                    offset[0] -= 15
                    
                

        pygame.draw.rect(screen, (0,0,0), (0, 0, settings.resolution[0], settings.resolution[1]))

        draw_grid(screen, grid, scale, offset)

        pygame.display.update()

if __name__ == '__main__':
    main()