import pygame
import numpy as np
from collections import deque

import tools

class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, cells):
        super().__init__()

        self.pos = pos # row, col
        self.row, self.col = self.pos
        
        self.height = cells[pos]
        
        
class Bait(Tower):
    def __init__(self, pos, cells):
        super().__init__(pos, cells)

    def update(self, screen, scale, offset):
        self.draw(screen, scale, offset)

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=240)

        pygame.draw.rect(screen, color,
            (offset[0]*scale + self.col*5*scale, # x
             offset[1]*scale + self.row*5*scale, # y
             5*scale, 5*scale),               # size
             border_radius=2)                       # border
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.grid_pos = None
        self.height = None
        self.movement_queue = deque()

    def spawn(self, cells, offset, scale):
        rows, cols = cells.shape

        # Extracting the coordinates of the borders
        top_border = [(0, i) for i in range(1, cols - 1)]
        bottom_border = [(rows - 1, i) for i in range(1, cols - 1)]
        left_border = [(i, 0) for i in range(1, rows - 1)]
        right_border = [(i, cols - 1) for i in range(1, rows - 1)]

        # Combine borders into a list of coordinates without repeating corners
        border_coords = top_border + right_border[:-1] + bottom_border[::-1] + left_border[::-1][:-1]
        flattened_border_coords = [coord for coord in border_coords]
        random_index = np.random.choice(len(flattened_border_coords))

        self.grid_pos = flattened_border_coords[random_index]
        self.grid_row, self.grid_col = self.grid_pos

        self.pos = self.grid_pos
        self.row, self.col = self.grid_row, self.grid_col

        self.target_grid_row = self.grid_row
        self.target_grid_col = self.grid_col

        self.height = cells[self.grid_pos]

        self.hitbox = pygame.rect.Rect((offset[0]*scale + self.col*scale, # x
                                        offset[1]*scale + self.row*scale), # y
                                       (5, 5)) # size

    def go_to(self, neighbour, ticks):
        self.target_grid_row, self.target_grid_col = neighbour

        vector = (self.target_grid_row - self.grid_row) / ticks, \
                 (self.target_grid_col - self.grid_col) / ticks
        
        for tick in range(ticks): self.movement_queue.append(vector)

    def update(self, screen, scale, offset):

        self.hitbox = pygame.rect.Rect((offset[0]*scale + self.col*5*scale, # x
                                        offset[1]*scale + self.row*5*scale), # y
                                       (5*scale, 5*scale)) # size

        self.draw(screen, scale, offset)

        if self.movement_queue:
            movement = self.movement_queue.popleft()
            self.row += movement[0]
            self.col += movement[1]
        else:
            self.grid_row, self.grid_col = self.target_grid_row, self.target_grid_col
            self.hitbox = pygame.rect.Rect((offset[0]*scale + self.grid_col*5*scale, # x
                                            offset[1]*scale + self.grid_row*5*scale), # y
                                            (5*scale, 5*scale)) # size
            


    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=0)

        pygame.draw.rect(screen, color,
             self.hitbox,               # size
             border_radius=10)  


