import pygame
import numpy as np
from collections import deque
import random

import tools

#import path_finding
# import djikstras as path_finding
import a_star_path as path_finding

class Tower(pygame.sprite.Sprite):
    '''
    Class representing a tower in a tower defense game.
    '''

    def __init__(self, pos, cells, tower_grid, dimensions=(1, 1)):
        '''
        Constructor to initialize a Tower object.

        Parameters:
        - pos: Tuple containing the (row, col) grid position of the tower
        - cells: Dictionary or array representing the grid of cells
        - tower_grid: 2D NumPy array representing the tower grid
        - dimensions: Tuple containing the width and height dimensions of the tower (default is (1, 1))
        '''

        super().__init__()

        # Initialize attributes
        self.grid_pos = pos
        self.max_health = self.health = 5
        self.grid_row, self.grid_col = self.grid_pos
        self.dimensions = dimensions
        self.level = 1
        self.damage = 1

        # Set tower reference in the tower grid for each occupied cell
        for i in range(0, self.dimensions[0]):
            for j in range(0, self.dimensions[1]):
                y = self.grid_row + i
                x = self.grid_col + j
                tower_grid[y, x] = self

        # Set the height attribute based on the cell at the tower's position
        self.height = cells[pos]

    def update(self, screen, scale, offset, font, enemies, Game_Data, paused):
        '''
        Update method for the Tower object.

        Parameters:
        - screen: Pygame display surface
        - scale: Scaling factor for grid cell size
        - offset: Tuple containing the (x, y) offset of the grid
        - font: Pygame font object for displaying information
        - enemies: Pygame sprite group containing enemies
        - Game_Data: Instance of the game data class
        - paused: Boolean indicating whether the game is paused

        Returns:
        - None
        (Modifies the screen and other parameters during the update)
        '''

        self.draw(screen, scale, offset, font, Game_Data)

    def hurt(self, damage, enemies, tower_grid):
        '''
        Method to reduce the health of the tower when it is attacked.

        Parameters:
        - damage: Amount of damage to be inflicted on the tower
        - enemies: Pygame sprite group containing enemies
        - tower_grid: 2D NumPy array representing the tower grid

        Returns:
        - None
        (Modifies the tower's health and may trigger the die method)
        '''

        self.health -= damage
        if self.health <= 0:
            self.die(enemies, tower_grid)

    def get_closest_enemy(self, enemies, consider_height=False):
        '''
        Method to find the closest enemy to the tower.

        Parameters:
        - enemies: Pygame sprite group containing enemies
        - consider_height: Boolean indicating whether to consider the height difference

        Returns:
        - Closest enemy to the tower or None if there are no enemies
        '''

        if len(enemies.sprites()) == 0:
            return None

        closest_enemy = None
        shortest_distance = 9999

        for enemy in enemies:
            if enemy.name != "Wall" and enemy.grid_pos is not None:
                delta_height = enemy.height - self.height if consider_height else 0
                delta_x = enemy.grid_row - self.grid_row
                delta_y = enemy.grid_col - self.grid_col
                distance = (delta_height**2 + delta_x**2 + delta_y**2)**(1/2)

                if distance < shortest_distance:
                    shortest_distance = distance
                    closest_enemy = enemy

        return closest_enemy

    def die(self, enemies, tower_grid):
        '''
        Method to handle the tower's death.

        Parameters:
        - enemies: Pygame sprite group containing enemies
        - tower_grid: 2D NumPy array representing the tower grid

        Returns:
        - None
        (Modifies the tower grid, enemy goal queues, and may remove the tower sprite)
        '''

        # Remove tower reference from the tower grid for each occupied cell
        for i in range(0, self.dimensions[0]):
            for j in range(0, self.dimensions[1]):
                y = self.grid_row + i
                x = self.grid_col + j
                tower_grid[y, x] = None

        # Clear goal queues of enemies targeting the tower
        for enemy in enemies:
            if enemy.goal_queue:
                if enemy.goal_queue[-1] == self.grid_pos:
                    enemy.goal_queue.clear()

        # Remove the tower sprite
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
             border_radius=2)                 # border
        
    def update(self, screen, scale, offset, font, Game_Data, paused):
        self.draw(screen, scale, offset, font, Game_Data)
        
class Sniper(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid)
        self.name = "Sniper"
        self.max_health = self.health = 5
        self.shoot_cooldown = self.shoot_ticks = 18
        self.shooting = False
        self.target = None

    def draw(self, screen, scale, offset, font, Game_Data):
        posx, posy = offset[0]*scale + self.grid_col*5*scale, offset[1]*scale + self.grid_row*5*scale

        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=45)
        
        # Border
        pygame.draw.rect(screen, (255, 128, 128),
            (posx - 0.5*scale, # x
             posy - 0.5*scale, # y
             6*scale, 6*scale),               # size
             border_radius=1)  

        # Flesh
        flesh_rect = pygame.rect.Rect(posx, # x
                                      posy, # y
                                      5*scale, 5*scale)
    
        pygame.draw.rect(screen, color, flesh_rect, border_radius=2)                 # border

        hitbox_half_length = 2.5*scale
        turret_pivot_x, turret_pivot_y = posx + hitbox_half_length, posy + hitbox_half_length

        turret =  pygame.Surface((8*scale, 2*scale), pygame.SRCALPHA)
        turret.fill((128, 128, 128))

        nozzle =  pygame.Surface((1.2*scale, 3*scale), pygame.SRCALPHA)
        nozzle.fill((64, 64, 64))
        
        if self.target != None:
            target_centre = self.target.pos + pygame.Vector2(2.5 * scale, 2.5 * scale)

            angle = tools.get_angle_to_point(pygame.Vector2(posx, posy),
                                             target_centre)
            
            if self.shooting:
                pygame.draw.aaline(screen, (255, 0, 0), (turret_pivot_x, turret_pivot_y), (target_centre))
                self.shooting = False
        else:
            angle = 0
        
        screen.blit(*tools.rotate_image_around_pivot(image=turret,
                                                     pivot_point=(turret_pivot_x, turret_pivot_y),
                                                     distance_from_pivot=4*scale,
                                                     angle=angle))
        screen.blit(*tools.rotate_image_around_pivot(image=nozzle,
                                                     pivot_point=(turret_pivot_x, turret_pivot_y),
                                                     distance_from_pivot=8*scale,
                                                     angle=angle))
        
        pygame.draw.circle(screen, (64, 64, 64), (turret_pivot_x, turret_pivot_y), 2*scale)

    def add_level(self, Game_Data):
            self.max_health *= 2
            self.health = self.max_health

            self.damage *= 2
            
            if self.shoot_cooldown > 5:
                self.shoot_cooldown = int(self.shoot_cooldown*0.9)
            self.shoot_ticks = self.shoot_cooldown
        
    def update(self, screen, scale, offset, font, enemies, Game_Data, paused): 
        if not paused:
            if self.target == None:
                self.target = self.get_closest_enemy(enemies, consider_height=True)

            elif self.target != None:
                if self.shoot_ticks == self.shoot_cooldown:
                    self.shoot_ticks = 0
                    self.shoot()
                else:
                    self.shoot_ticks += 1
        self.draw(screen, scale, offset, font, Game_Data)   
        

    def shoot(self):
        self.shooting = True
        self.target.recieve_damage(damage=self.damage, tower=self)
        
class Producer(Tower):
    def __init__(self, pos, cells, tower_grid):
        super().__init__(pos, cells, tower_grid)
        self.name = "Producer"
        self.max_health = self.health = 10

    def draw(self, screen, scale, offset, font, Game_Data):
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
        pygame.draw.rect(cw_cog_surface, (255, Game_Data.count % 255, 255), cog)

        acw_cog_surface = pygame.Surface((3*scale, 3*scale), pygame.SRCALPHA)
        pygame.draw.rect(acw_cog_surface, (255, Game_Data.count % 255, 255), cog)

        # Rotate the cogs
        rotated_cw_cog = pygame.transform.rotate(cw_cog_surface, Game_Data.count % 180)
        rotated_acw_cog = pygame.transform.rotate(acw_cog_surface, -Game_Data.count % 180)

        # Get the new rects after rotation
        rotated_cw_cog_rect = rotated_cw_cog.get_rect(center=center)
        rotated_acw_cog_rect = rotated_acw_cog.get_rect(center=center)

        # Draw the rotated cogs onto the screen
        screen.blit(rotated_cw_cog, rotated_cw_cog_rect.topleft)
        screen.blit(rotated_acw_cog, rotated_acw_cog_rect.topleft)
    
    def update(self, screen, scale, offset, font, enemies, Game_Data, paused):
        self.draw(screen, scale, offset, font, Game_Data)
        if Game_Data.count % 255 == 0:
            Game_Data.cash += 120
            Game_Data.difficulty += 0.1

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
    '''
    Class representing an enemy in a tower defense game.
    '''

    def __init__(self, Game_Data, name="Enemy", speed=1, max_health=1, damage=1):
        '''
        Constructor to initialize an Enemy object.

        Parameters:
        - Game_Data: Instance of the game data class
        - name: String representing the name of the enemy (default is "Enemy")
        - speed: Float representing the movement speed of the enemy (default is 1)
        - max_health: Integer representing the maximum health of the enemy (default is 1)
        - damage: Integer representing the damage inflicted by the enemy (default is 1)
        '''

        super().__init__()

        # Initialize attributes
        self.grid_pos = None
        self.height = None
        self.level = 1 + Game_Data.difficulty // 2.151436  # Made it a weird decimal for variety
        self.speed = speed
        self.health = self.max_health = max_health * self.level
        self.damage = damage
        self.damage_cooldown = self.damage_ticks = 60
        self.name = name

        # Initialize movement and goal queues
        self.movement_queue = deque()
        self.goal_queue = deque()

    def spawn(self, cells, offset, scale):
        '''
        Method to spawn the enemy at a random position along the border of the grid.

        Parameters:
        - cells: 2D NumPy array representing the grid of cells
        - offset: Tuple containing the (x, y) offset of the grid
        - scale: Scaling factor for grid cell size

        Returns:
        - None
        (Modifies the enemy's attributes and position)
        '''

        rows, cols = cells.shape

        # Extract coordinates of the borders without repeating corners
        top_border = [(0, i) for i in range(1, cols - 1)]
        right_border = [(i, cols - 1) for i in range(1, rows - 1)]
        bottom_border = [(rows - 1, i) for i in range(1, cols - 1)]
        left_border = [(i, 0) for i in range(1, rows - 1)]

        # Combine borders into a list of coordinates
        border_coords = top_border + right_border[:-1] + bottom_border[::-1] + left_border[::-1][:-1]
        flattened_border_coords = [coord for coord in border_coords]

        # Choose a random position along the border
        random_index = np.random.choice(len(flattened_border_coords))
        self.grid_pos = flattened_border_coords[random_index]
        self.grid_row, self.grid_col = self.grid_pos

        # Set initial positions and attributes
        self.row, self.col = self.grid_row, self.grid_col
        self.target_grid_row, self.target_grid_col = self.grid_row, self.grid_col
        self.height = cells[self.grid_pos]

        # Set hitbox and position for drawing on the screen
        self.hitbox = pygame.rect.Rect((self.grid_col, self.grid_row), (5, 5))
        self.pos = pygame.Vector2(offset[0] * scale + self.hitbox.x * 5 * scale,
                                  offset[1] * scale + self.hitbox.y * 5 * scale)

    def get_closest_tower_pos(self, towers, consider_height=False):
        '''
        Method to find the closest tower's position to the enemy.

        Parameters:
        - towers: Pygame sprite group containing towers
        - consider_height: Boolean indicating whether to consider the height difference

        Returns:
        - Tuple containing the row and column indices of the closest tower's position
        '''

        if len(towers.sprites()) == 0:
            return None

        closest_pos = None
        shortest_distance = 9999

        for tower in towers:
            if tower.name == "Wallz":
                pass
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
        '''
        Method to find towers that the enemy is currently touching.

        Parameters:
        - towers: Pygame sprite group containing towers

        Returns:
        - List of tower objects that the enemy is currently touching
        '''

        touching_towers = []
        for tower in towers:
            if tower.grid_pos == self.grid_pos:
                touching_towers.append(tower)
        return touching_towers

    def inflict_damage(self, towers, enemies, tower_grid):
        '''
        Method to inflict damage on towers that the enemy is currently touching.

        Parameters:
        - towers: Pygame sprite group containing towers
        - enemies: Pygame sprite group containing enemies
        - tower_grid: 2D NumPy array representing the tower grid

        Returns:
        - None
        (Modifies the health of towers)
        '''

        for tower in self.get_touching_towers(towers):
            tower.hurt(self.damage, enemies, tower_grid)

    def recieve_damage(self, damage, tower):
        '''
        Method to receive damage from a tower.

        Parameters:
        - damage: Amount of damage to be received
        - tower: Tower object inflicting the damage

        Returns:
        - None
        (Modifies the enemy's health and may trigger the die method)
        '''

        self.health -= damage
        if self.health <= 0:
            self.die(tower)

    def die(self, tower):
        '''
        Method to handle the enemy's death.

        Parameters:
        - tower: Tower object that may be targeting the enemy

        Returns:
        - None
        (Modifies tower targets and removes the enemy sprite)
        '''

        if tower.name == "Sniper":
            tower.target = None
        self.kill()

    def damage_update(self, towers, enemies, tower_grid):
        '''
        Method to update the damage cooldown and inflict damage on nearby towers.

        Parameters:
        - towers: Pygame sprite group containing towers
        - enemies: Pygame sprite group containing enemies
        - tower_grid: 2D NumPy array representing the tower grid

        Returns:
        - None
        (Modifies the damage cooldown and may inflict damage on towers)
        '''

        if self.damage_ticks >= self.damage_cooldown:
            self.damage_ticks = 0
            touching_towers = self.get_touching_towers(towers)
            self.inflict_damage(touching_towers, enemies, tower_grid)
        else:
            self.damage_ticks += 1

    def navigate_to(self, cells, goal):
        '''
        Method to calculate and append the path to the goal in the goal queue.

        Parameters:
        - cells: 2D NumPy array representing the grid of cells
        - goal: Tuple containing the (row, col) indices of the goal

        Returns:
        - None
        (Modifies the goal queue)
        '''

        goals = path_finding.path_find(grid=cells,
                                       start=(self.grid_row, self.grid_col),
                                       end=goal)

        for goal in goals:
            self.goal_queue.append(goal)

    def go_to(self, cells, goal):
        '''
        Method to update the target position and movement queue for reaching the goal.

        Parameters:
        - cells: 2D NumPy array representing the grid of cells
        - goal: Tuple containing the (row, col) indices of the goal

        Returns:
        - None
        (Modifies the target position and movement queue)
        '''

        self.target_grid_row, self.target_grid_col = goal

        delta_height = max(int(cells[goal]) - int(cells[self.grid_row, self.grid_col]), 10)

        ticks = int(delta_height * 1 / (2**(self.speed - 1)))

        vector = ((self.target_grid_row - self.grid_row) / ticks,
                  (self.target_grid_col - self.grid_col) / ticks)

        for tick in range(ticks):
            self.movement_queue.append(vector)

    def update(self, screen, cells, towers, tower_grid, enemies, scale, offset, paused):
        '''
        Method to update the enemy's position, damage cooldown, and drawing.

        Parameters:
        - screen: Pygame display surface
        - cells: 2D NumPy array representing the grid of cells
        - towers: Pygame sprite group containing towers
        - tower_grid: 2D NumPy array representing the tower grid
        - enemies: Pygame sprite group containing enemies
        - scale: Scaling factor for grid cell size
        - offset: Tuple containing the (x, y) offset of the grid
        - paused: Boolean indicating whether the game is paused

        Returns:
        - None
        (Modifies the enemy's position, damage cooldown, and screen)
        '''

        if not paused:
            self.determine_movement(cells, towers)
            self.pos = pygame.Vector2(offset[0] * scale + self.hitbox.x * 5 * scale,
                                      offset[1] * scale + self.hitbox.y * 5 * scale)
            self.damage_update(towers, enemies, tower_grid)

        self.draw(screen, scale, offset)

    def determine_movement(self, cells, towers):
        '''
        Method to determine the enemy's movement based on the movement and goal queues.

        Parameters:
        - cells: 2D NumPy array representing the grid of cells
        - towers: Pygame sprite group containing towers

        Returns:
        - None
        (Modifies the enemy's position, hitbox, and may trigger goal navigation)
        '''

        self.hitbox = pygame.rect.Rect((self.grid_col, self.grid_row), (5, 5))

        if self.movement_queue:
            movement = self.movement_queue.popleft()
            self.row += movement[0]
            self.col += movement[1]

        else:
            self.grid_row, self.grid_col = self.target_grid_row, self.target_grid_col
            self.grid_pos = self.grid_row, self.grid_col
            self.height = cells[self.grid_row, self.grid_col]

            self.hitbox = pygame.rect.Rect((self.grid_col, self.grid_row), (5, 5))

            if self.goal_queue:
                self.go_to(cells, self.goal_queue.popleft())

            else:
                goal = self.get_closest_tower_pos(towers)
                if goal:
                    self.navigate_to(cells, goal)

    def draw(self, screen, scale, offset):
        '''
        Method to draw the enemy on the screen.

        Parameters:
        - screen: Pygame display surface
        - scale: Scaling factor for grid cell size
        - offset: Tuple containing the (x, y) offset of the grid

        Returns:
        - None
        (Modifies the screen)
        '''
        color = tools.change_hue(gray_color=self.height, 
                                 new_hue=0)

        pygame.draw.rect(screen, color,
             self.hitbox,               # size
             border_radius=10)  

class Basic(Enemy):
    def __init__(self, Game_Data):
        super().__init__(Game_Data, name="Basic", max_health=3)

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
    def __init__(self, Game_Data):
        super().__init__(Game_Data, name="Runner", max_health=1, speed=3)
        self.name = "Runner"
        self.max_health = self.health = 1
        self.level = 1
        self.speed = 1.5

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
    def __init__(self, Game_Data):
        super().__init__(Game_Data,
                         name="Giant",
                         max_health=20,
                         speed=0.25)

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
