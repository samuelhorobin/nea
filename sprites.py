import pygame
import numpy as np
from collections import deque
import random

import tools

#import path_finding
# import djikstras as path_finding
import a_star_path as path_finding

class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, cells):
        super().__init__()

        self.grid_pos = pos # row, col
        self.grid_row, self.grid_col = self.grid_pos
        
        self.height = cells[pos]

    def update(self, screen, scale, offset, paused):
        self.draw(screen, scale, offset)
        
    def hurt(self, damage, enemies):
        self.health -= damage
        if self.health <= 0:
            self.die(enemies)

    def die(self, enemies):
        for enemy in enemies:
            if enemy.goal_queue:
                if enemy.goal_queue[-1] == self.grid_pos:
                    enemy.goal_queue.clear()
        self.kill()      

        
class Bait(Tower):
    def __init__(self, pos, cells):
        super().__init__(pos, cells)
        self.name = "Bait"
        self.max_health = self.health = 10

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=240)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255),
            (offset[0]*scale + self.grid_col*5*scale - 0.5*scale, # x
             offset[1]*scale + self.grid_row*5*scale - 0.5*scale, # y
             6*scale, 6*scale),               # size
             border_radius=2)  

        # Flesh
        pygame.draw.rect(screen, color,
            (offset[0]*scale + self.grid_col*5*scale, # x
             offset[1]*scale + self.grid_row*5*scale, # y
             5*scale, 5*scale),               # size
             border_radius=2)                       # border
        
class Shooter(Tower):
    def __init__(self, pos, cells):
        super().__init__(pos, cells)
        self.name = "Shooter"
        self.max_health = self.health = 5

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=120)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255),
            (offset[0]*scale + self.grid_col*5*scale - 0.5*scale, # x
             offset[1]*scale + self.grid_row*5*scale - 0.5*scale, # y
             6*scale, 6*scale),               # size
             border_radius=1)  

        # Flesh
        pygame.draw.rect(screen, color,
            (offset[0]*scale + self.grid_col*5*scale, # x
             offset[1]*scale + self.grid_row*5*scale, # y
             5*scale, 5*scale),               # size
             border_radius=2)                       # border
        
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.grid_pos = None
        self.height = None
        
        self.speed = 1
        self.health = self.max_health = 1
        self.damage = 1
        self.damage_cooldown = self.damage_ticks = 60 
        self.name = "Enemy"
        
        self.movement_queue = deque()
        self.goal_queue = deque()

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

        self.hitbox = pygame.rect.Rect((self.grid_col, # x
                                        self.grid_row), # y
                                        (5, 5)) # size
        
    def get_closest_tower_pos(self, towers, consider_height = False):
        if len(towers.sprites()) == 0: return None
        shortest_distance = 9999

        for tower in towers:
            delta_height = tower.height - self.height if consider_height else 0
            delta_x = tower.grid_row - self.grid_row
            delta_y = tower.grid_col - self.grid_col
            distance = (delta_height**2 + delta_x**2 + delta_y**2)**(1/2)

            if distance < shortest_distance:
                shortest_distance = distance
                closest_pos = tower.grid_pos

        return closest_pos

    def get_touching_towers(self, towers):
        touching_towers = []
        for tower in towers:
            if tower.grid_pos == self.grid_pos:
                touching_towers.append(tower)
        return touching_towers
    
    def inflict_damage(self, towers, enemies):
        for tower in self.get_touching_towers(towers):
            tower.hurt(self.damage, enemies)

    def damage_update(self, towers, enemies):
        if self.damage_ticks >= self.damage_cooldown:
            self.damage_ticks = 0
            touching_towers = self.get_touching_towers(towers)
            self.inflict_damage(touching_towers, enemies)
        else:
            self.damage_ticks += 1


    def navigate_to(self, cells, goal):
        goals = path_finding.path_find(grid=cells,
                                       start=(self.grid_row, self.grid_col),
                                       end=goal)

        for goal in goals: self.goal_queue.append(goal)


    def go_to(self, cells, goal):
        self.target_grid_row, self.target_grid_col = goal

        delta_height = max(int(cells[goal]) - int(cells[self.grid_row, self.grid_col]), 10)

        ticks = int(delta_height * 1 / (2**(self.speed - 1)))

        vector = (self.target_grid_row - self.grid_row) / ticks, \
                 (self.target_grid_col - self.grid_col) / ticks
        
        for tick in range(ticks): self.movement_queue.append(vector)

    def update(self, screen, cells, towers, enemies, scale, offset, paused):
        if not paused:
            self.determine_movement(cells, towers)
            self.damage_update(towers, enemies)
        self.draw(screen, scale, offset)


    def determine_movement(self, cells, towers):
        self.hitbox = pygame.rect.Rect((self.grid_col, # x
                                            self.grid_row), # y
                                            (5, 5)) # size

        if self.movement_queue:
            movement = self.movement_queue.popleft()
            self.row += movement[0]
            self.col += movement[1]

        else:
            self.grid_row, self.grid_col = self.target_grid_row, self.target_grid_col
            self.grid_pos = self.grid_row, self.grid_col
            self.height = cells[self.grid_row, self.grid_col]
            

            self.hitbox = pygame.rect.Rect((self.grid_col, # x
                                            self.grid_row), # y
                                            (5, 5)) # size
            
            if self.goal_queue:
                self.go_to(cells, self.goal_queue.popleft())

            else:
                goal = self.get_closest_tower_pos(towers)
                if goal:
                    self.navigate_to(cells, goal)

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=0)

        pygame.draw.rect(screen, color,
             self.hitbox,               # size
             border_radius=10)  

class Basic(Enemy):
    def __init__(self):
        super().__init__()
        self.name = "Basic"
        self.max_health = self.health = 3

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=0)
        
        rect = pygame.rect.Rect((offset[0]*scale + self.hitbox.x*5*scale, # x
                                offset[1]*scale + self.hitbox.y*5*scale), # y
                                (5*scale, 5*scale))
        

        # # Border
        # pygame.draw.rect(screen, (0, 0, 0),
        #     (rect.x - 0.25*scale, # x
        #      rect.y - 0.25*scale, # y
        #      rect.width+(0.5*scale), rect.height+(0.5*scale)),               # size
        #      border_radius=10)  

        # Flesh
        pygame.draw.rect(screen, color,
             rect,               # size
             border_radius=10) 


    # def update(self, screen, cells, towers, scale, offset):
    #     self.determine_movement(cells, towers)
    #     self.damage_update(towers)
    #     self.draw(screen, scale, offset)
