import pygame
import numpy as np
from collections import deque
import random

import tools

#import path_finding
# import djikstras as path_finding
import a_star_path as path_finding

class Tower(pygame.sprite.Sprite):
    def __init__(self, pos, cells, tower_grid, dimensions = (1,1)):
        super().__init__()
        self.grid_pos = pos # row, col
        self.grid_row, self.grid_col = self.grid_pos
        self.dimensions = dimensions

        for i in range(0, self.dimensions[0]):
            for j in range(0, self.dimensions[1]):
                y = self.grid_row + i
                x = self.grid_col + j
                tower_grid[y, x] = self

        self.height = cells[pos]

    def update(self, screen, scale, offset, font, Game_Data, paused):
        self.draw(screen, scale, offset, font, Game_Data.animation_count)
        
    def hurt(self, damage, enemies, tower_grid):
        self.health -= damage
        if self.health <= 0:
            self.die(enemies, tower_grid)

    def die(self, enemies, tower_grid):
        for i in range(0, self.dimensions[0]):
                    for j in range(0, self.dimensions[1]):
                        y = self.grid_row + i
                        x = self.grid_col + j
                        tower_grid[y, x] = None       

        for enemy in enemies:
            if enemy.goal_queue:
                if enemy.goal_queue[-1] == self.grid_pos:
                    enemy.goal_queue.clear()
        self.kill()      
                    
class Bait(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid)
        self.name = "Bait"
        self.max_health = self.health = 10

    def draw(self, screen, scale, offset, font, animation_adjustment):
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
        
class Sniper(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid)
        self.name = "Sniper"
        self.max_health = self.health = 5

    def draw(self, screen, scale, offset, font, animation_adjustment):
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
        
class Producer(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid)
        self.name = "Producer"
        self.max_health = self.health = 10
        self.cooldown_timer = self.cash_cooldown = 60

    def draw(self, screen, scale, offset, font, animation_adjustment):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=200)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255),
            (offset[0]*scale + self.grid_col*5*scale - 0.5*scale, # x
             offset[1]*scale + self.grid_row*5*scale - 0.5*scale, # y
             6*scale, 6*scale),               # size
             border_radius=1)  

        flesh_rect = pygame.rect.Rect(offset[0]*scale + self.grid_col*5*scale, # x
                                      offset[1]*scale + self.grid_row*5*scale, # y
                                      5*scale, 5*scale)
        
        # Flesh
        pygame.draw.rect(screen, color,
                         flesh_rect,               # size
                         border_radius=0)          # border
        
        center = flesh_rect.center
        cog = pygame.rect.Rect(0, 0, 4*scale, 4*scale)

        # Create surfaces from cog rectangles
        cw_cog_surface = pygame.Surface((3*scale, 3*scale), pygame.SRCALPHA)
        pygame.draw.rect(cw_cog_surface, (255, animation_adjustment % 255, 255), cog)

        acw_cog_surface = pygame.Surface((3*scale, 3*scale), pygame.SRCALPHA)
        pygame.draw.rect(acw_cog_surface, (255, animation_adjustment % 255, 255), cog)

        # Rotate the cogs
        rotated_cw_cog = pygame.transform.rotate(cw_cog_surface, animation_adjustment % 180)
        rotated_acw_cog = pygame.transform.rotate(acw_cog_surface, -animation_adjustment % 180)

        # Get the new rects after rotation
        rotated_cw_cog_rect = rotated_cw_cog.get_rect(center=center)
        rotated_acw_cog_rect = rotated_acw_cog.get_rect(center=center)

        # Draw the rotated cogs onto the screen
        screen.blit(rotated_cw_cog, rotated_cw_cog_rect.topleft)
        screen.blit(rotated_acw_cog, rotated_acw_cog_rect.topleft)
    
    def update(self, screen, scale, offset, font, Game_Data, paused):
        self.draw(screen, scale, offset, font, Game_Data.animation_count)

        if self.cooldown_timer == self.cash_cooldown:
            self.cooldown_timer = 0
            Game_Data.cash += 1
        else:
            self.cooldown_timer += 1


        
class Wall(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid)
        self.name = "Wall"
        self.max_health = self.health = 10

    def draw(self, screen, scale, offset, font, animation_adjustment):
        color = (self.height, self.height, self.height)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255),
            (offset[0]*scale + self.grid_col*5*scale - 0.5*scale, # x
             offset[1]*scale + self.grid_row*5*scale - 0.5*scale, # y
             6*scale, 6*scale),               # size
             border_radius=0)  

        # Flesh
        pygame.draw.rect(screen, color,
            (offset[0]*scale + self.grid_col*5*scale, # x
             offset[1]*scale + self.grid_row*5*scale, # y
             5*scale, 5*scale),               # size
             border_radius=0)  
        
class Headquarters(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid, dimensions=(2,2))
        self.name = "Headquarters"
        self.max_health = self.health = 30

    def draw(self, screen, scale, offset, font, animation_adjustment):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=120)
        
        # Border
        pygame.draw.rect(screen, (255, 255, 255),
            (offset[0]*scale + self.grid_col*5*scale - 0.5*scale, # x
             offset[1]*scale + self.grid_row*5*scale - 0.5*scale, # y
             11*scale, 11*scale),               # size
             border_radius=5)  

        # Flesh
        pygame.draw.rect(screen, color,
            (offset[0]*scale + self.grid_col*5*scale, # x
             offset[1]*scale + self.grid_row*5*scale, # y
             10*scale, 10*scale),               # size
             border_radius=5)                       # border
        
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
        closest_pos = None
        shortest_distance = 9999

        for tower in towers:
            if tower.name == "Wall": pass
            else:
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
    
    def inflict_damage(self, towers, enemies, tower_grid):
        for tower in self.get_touching_towers(towers):
            tower.hurt(self.damage, enemies, tower_grid)

    def damage_update(self, towers, enemies, tower_grid):
        if self.damage_ticks >= self.damage_cooldown:
            self.damage_ticks = 0
            touching_towers = self.get_touching_towers(towers)
            self.inflict_damage(touching_towers, enemies, tower_grid)
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

    def update(self, screen, cells, towers, tower_grid,  enemies, scale, offset, paused):
        if not paused:
            self.determine_movement(cells, towers)
            self.damage_update(towers, enemies, tower_grid)
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
        # Flesh
        pygame.draw.rect(screen, color,
             rect,               # size
             border_radius=10) 
        
class Runner(Enemy):
    def __init__(self):
        super().__init__()
        self.name = "Runner"
        self.max_health = self.health = 1
        self.speed = 3

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=20)
        
        rect = pygame.rect.Rect((offset[0]*scale + (self.hitbox.x + 0.25)*5*scale, # x
                                 offset[1]*scale + (self.hitbox.y + 0.25)*5*scale), # y
                                (2.5*scale, 2.5*scale))
        # Flesh
        pygame.draw.rect(screen, color,
             rect,               # size
             border_radius=10) 

class Giant(Enemy):
    def __init__(self):
        super().__init__()
        self.name = "Giant"
        self.max_health = self.health = 20
        self.speed = 0.5

    def draw(self, screen, scale, offset):
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=10)
        
        rect = pygame.rect.Rect((offset[0]*scale + (self.hitbox.x - 0.5)*5*scale, # x
                                 offset[1]*scale + (self.hitbox.y - 0.5)*5*scale), # y
                                (10*scale, 10*scale))
        # Flesh
        pygame.draw.rect(screen, color,
             rect,               # size
             border_radius=10) 
