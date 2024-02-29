import pygame
import numpy as np
import colorsys
import math
import os
import json

pygame.init()

class ExclusiveBooleanList:
    '''
    Class to manage a list of exclusive boolean values with selection and query functionalities.
    '''

    def __init__(self, *names):
        '''
        Constructor to initialize the ExclusiveBooleanList.

        Parameters:
        - *names: Variable number of names representing the boolean values to be managed.
        '''

        # Create a dictionary with boolean values initialized to False for each name
        self.boolean_dict = {name: False for name in names}

    def select(self, name):
        '''
        Method to select a specific boolean value while setting others to False.

        Parameters:
        - name: Name of the boolean value to be selected.

        Returns:
        - None
        '''

        if name in self.boolean_dict:
            if self.boolean_dict[name]:
                # If the selected value is already True, set all values to False
                self.boolean_dict = {key: False for key in self.boolean_dict}
            else:
                # If the selected value is False, set all values to False and set the selected value to True
                self.boolean_dict = {key: False for key in self.boolean_dict}
                self.boolean_dict[name] = True
        else:
            raise ValueError(f"Invalid name: {name}")

    def none_true(self):
        '''
        Method to check if none of the boolean values are True.

        Returns:
        - True if none of the boolean values are True, False otherwise.
        '''

        return all(not val for val in self.boolean_dict.values())
    
    def return_true(self):
        '''
        Method to return the name of the first True boolean value.

        Returns:
        - Name of the first True boolean value, or None if none are True.
        '''

        for (key, val) in self.boolean_dict.items():
            if val:
                return key
        return None

    def __str__(self):
        '''
        Method to return a string representation of the ExclusiveBooleanList.

        Returns:
        - String representation of the boolean dictionary.
        '''

        return str(self.boolean_dict)


def float_to_color(value):
    '''
    Function to convert a floating-point value to a color intensity within the range [0, 255].

    Parameters:
    - value: Floating-point value to be converted

    Returns:
    - Integer representing the color intensity within the range [0, 255]
    '''

    # Normalize the floating-point value to the range [0, 255]
    normalized_value = int((value + 1) * 127.5)

    # Ensure the result is within the valid range of [0, 255]
    return max(0, min(normalized_value, 255))


def change_hue(gray_color, new_hue):
    '''
    Function to change the hue of a gray color.

    Parameters:
    - gray_color: Integer representing the gray color value (0 to 255)
    - new_hue: New hue value in degrees (0 to 360)

    Returns:
    - Tuple containing the RGB color after changing the hue
    '''

    # Convert HSV to RGB, considering the input gray_color as the value component
    new_rgb = colorsys.hsv_to_rgb(new_hue / 360, 1, gray_color / 255)

    # Convert the resulting floating-point RGB values back to integers in the range [0, 255]
    return tuple(int(x * 255) for x in new_rgb)


def desaturate_color(color, amount):
    '''
    Function to desaturate an RGB color by a specified amount.

    Parameters:
    - color: Tuple representing the RGB color to be desaturated
    - amount: Integer value indicating the amount of desaturation (0 to 255)

    Returns:
    - Tuple containing the desaturated RGB color
    '''

    # Ensure the amount is within the valid range of 0 to 255
    amount = max(0, min(amount, 255))

    # Convert the RGB color to HLS color space
    r, g, b = color
    h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

    # Desaturate the color by adjusting its saturation
    new_s = max(0, s - (amount / 255.0))
    
    # Convert the color back to RGB
    new_r, new_g, new_b = colorsys.hls_to_rgb(h, l, new_s)

    # Convert back to integer RGB values
    new_r = int(new_r * 255)
    new_g = int(new_g * 255)
    new_b = int(new_b * 255)

    # Return the desaturated RGB color
    return new_r, new_g, new_b


def draw_grid(screen, cells, scale, offset):
    '''
    Function to draw a grid on a Pygame screen based on a 2D array of cells.

    Parameters:
    - screen: Pygame display surface on which the grid will be drawn
    - cells: 2D NumPy array representing the grid with color values for each cell
    - scale: Scaling factor for grid cell size
    - offset: Tuple containing the (x, y) offset of the grid

    Returns:
    - None
    (Modifies the screen directly to draw the grid)
    '''

    # Get the row and column indices of the cursor position
    cursor_xy = get_cursor_xy(cells, scale, offset)

    # Iterate through each cell in the grid using NumPy ndindex
    for row, col in np.ndindex(cells.shape):
        # Change the hue of the cell's color based on its value
        color = change_hue(gray_color=cells[row][col], new_hue=145)
        size = 5

        # If the cursor is over a cell, desaturate its color by 90%
        if cursor_xy:
            if row == cursor_xy[0] or col == cursor_xy[1]:
                color = desaturate_color(color, 90)

        # Draw a rectangle representing the current grid cell on the Pygame screen
        pygame.draw.rect(screen, color,
                         (offset[0] * scale + col * size * scale, offset[1] * scale + row * size * scale,
                          size * scale, size * scale),
                         border_radius=1)


def get_cursor_xy(cells, scale, offset, size=5):
    '''
    Function to get the row and column indices of a 2D grid corresponding to the cursor position.

    Parameters:
    - cells: 2D NumPy array representing the grid
    - scale: Scaling factor for grid cell size
    - offset: Tuple containing the (x, y) offset of the grid
    - size: Size of each grid cell (default is 5)

    Returns:
    - Tuple containing the row and column indices of the cursor position in the grid
    - Returns None if the cursor is not over any grid cell
    '''

    # Get the current mouse position
    mouse_pos = pygame.mouse.get_pos()

    # Iterate through each cell in the grid using NumPy ndindex
    for row, col in np.ndindex(cells.shape):
        # Create a Rect object representing the current grid cell
        rect = pygame.rect.Rect(offset[0] * scale + col * size * scale,
                                offset[1] * scale + row * size * scale,
                                size * scale, size * scale)

        # Check if the mouse position is within the current grid cell
        if rect.collidepoint(mouse_pos):
            # Return the row and column indices of the cursor position
            return row, col

    # Return None if the cursor is not over any grid cell
    return None


def can_fit(dimensions, pos, tower_grid):
    '''
    Function to check if a tower of given dimensions can fit at a specified position on a tower grid

    Parameters:
    - dimensions: Tuple containing the width and height of the tower
    - pos: Tuple containing the row and column coordinates of the desired position on the tower grid
    - tower_grid: 2D NumPy array representing the tower grid where towers can be placed

    Returns:
    - True if the tower can fit at the specified position, False otherwise
    '''

    # Extract the row and column coordinates from the position
    grid_row, grid_col = pos
    
    # Extract the dimensions of the tower grid
    width, height = tower_grid.shape

    # Iterate through each cell in the tower's dimensions
    for i in range(0, dimensions[0]):
        for j in range(0, dimensions[1]):
            # Calculate the absolute coordinates of the current cell
            y = grid_row + i
            x = grid_col + j

            # Check if the cell is outside the bounds of the tower grid
            if y >= height or x >= width:
                return False

            # Check if the cell is already occupied by another tower
            if tower_grid[y, x] is not None:
                return False

    # If all cells are unoccupied and within bounds, the tower can fit
    return True

def calculate_angle(start_point, end_point):
    '''
    Function to calculate the angle in degrees between two points in a 2D space.

    Parameters:
    - start_point: Tuple containing the (x, y) coordinates of the starting point
    - end_point: Tuple containing the (x, y) coordinates of the ending point

    Returns:
    - Angle in degrees between the line connecting start_point and end_point and the x-axis
    '''

    # Calculate the differences in x and y coordinates
    delta_x = end_point[0] - start_point[0]
    delta_y = end_point[1] - start_point[1]

    # Calculate the angle in radians using the arctangent function
    angle_rad = math.atan2(delta_y, delta_x)

    # Convert the angle from radians to degrees
    angle_deg = math.degrees(angle_rad)

    # Return the calculated angle in degrees
    return angle_deg


def draw_line_with_length(screen, colour, start, end, length):
    '''
    Function to draw a line on a Pygame screen from a starting point to an end point with a specified length.

    Parameters:
    - screen: Pygame display surface on which the line will be drawn
    - colour: Tuple representing the RGB color of the line
    - start: Tuple containing the (x, y) coordinates of the starting point
    - end: Tuple containing the (x, y) coordinates of the original ending point
    - length: Desired length of the line

    Returns:
    - None
    (Modifies the screen directly to draw the line)
    '''

    # Calculate the direction vector from start to end
    direction_vector = [end[0] - start[0], end[1] - start[1]]

    # Calculate the length of the direction vector
    direction_length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)

    # Scale the direction vector to the desired length
    scaled_direction = [direction_vector[0] * length / direction_length, 
                        direction_vector[1] * length / direction_length]

    # Calculate the new end point based on the scaled direction vector
    new_end = (start[0] + scaled_direction[0], start[1] + scaled_direction[1])

    # Draw the line on the Pygame screen with a thickness of 5 pixels
    pygame.draw.line(screen, colour, start, new_end, 5)


def get_angle_to_point(reference_point: pygame.Vector2, point: pygame.Vector2) -> float:
    """
    Helper function to get the angle from a reference point to the mouse
    position. This could really be used to get the angle between any two vectors.
    Returns the results in radians, as opposed to pygame.Vector2.angle_to which gives the result in degrees
    """

    offset = point - reference_point
    return math.atan2(offset.y, offset.x)

def rotate_point_around_pivot_simple(pivot_point: pygame.Vector2, distance_from_pivot: float, angle: float) -> pygame.Vector2:
    """Basically just plots a point that is `distance_from_pivot` units away from the pivot point, at an angle of `angle`"""
    rotated_offset = pygame.Vector2(math.cos(angle), math.sin(angle)) * distance_from_pivot
    return pivot_point + rotated_offset

def rotate_image_around_pivot(image: pygame.Surface, pivot_point: pygame.Vector2, distance_from_pivot: pygame.Vector2, angle: float) -> tuple[pygame.Surface, pygame.Rect]:
    """
    Moves the image and rotates it such that the center tracks around the pivot point. Returns the image and a rect,
    which can be used directly with pygame.Surface.blit
    """
    new_img = pygame.transform.rotate(image, math.degrees(-angle))
    new_origin = rotate_point_around_pivot_simple(pivot_point, distance_from_pivot, angle)
    new_rect = new_img.get_rect(center=new_origin)

    return (new_img, new_rect)

def get_animation(spritesheetDir, animation, spritesheet_name="spritesheet", data_name="data", name=None):
    '''
    Function to extract animation frames from a spritesheet based on provided parameters
    '''
    # Get the absolute path of the current script's directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct paths for the spritesheet image and its associated JSON data
    sprite_png = os.path.join(root_dir, spritesheetDir, f"{spritesheet_name}.png")
    sprite_json = os.path.join(root_dir, spritesheetDir, f"{data_name}.json")

    # Open and read the JSON file containing spritesheet data
    with open(sprite_json, "r") as file:
        data = json.load(file)

        # Find the start and end frames for the specified animation tag
        for tag in data["meta"]["frameTags"]:
            if tag["name"] == animation:
                start = tag["from"]
                end = tag["to"]

        # If no specific name is provided, use the base name of the spritesheet directory
        if name is None:
            name = os.path.basename(spritesheetDir)

        # Extract frames data for the specified animation frames
        framesData = [data["frames"][f"{name} {i}.aseprite"] for i in range(start, end + 1)]

        # Initialize empty lists to store frames and load the spritesheet image
        frames = []
        spritesheet = pygame.image.load(sprite_png)

        # Iterate through frames data and extract individual frame surfaces
        for frame in framesData:
            # Extract frame position and size information
            x, y, w, h = [frame["frame"][i] for i in ["x", "y", "w", "h"]]
            
            # Create subsurface for the current frame and store it along with its duration
            frameSurface = spritesheet.subsurface(pygame.Rect(x, y, w, h))
            frames.append([frameSurface, frame["duration"]])

        # Return the list of frames for the specified animation
        return frames
