import pygame
import numpy as np
import colorsys
import math

pygame.init()

class ExclusiveBooleanList:
    def __init__(self, *names):
        self.boolean_dict = {name: False for name in names}

    def select(self, name):
        if name in self.boolean_dict:
            if self.boolean_dict[name]:
                self.boolean_dict = {key: False for key in self.boolean_dict}
            else:
                self.boolean_dict = {key: False for key in self.boolean_dict}
                self.boolean_dict[name] = True
        else:
            raise ValueError(f"Invalid name: {name}")

    def none_true(self):
        return all(not val for val in self.boolean_dict.values())
    
    def return_true(self):
        for (key, val) in self.boolean_dict.items():
            if val == True:
                return key
        return None

    def __str__(self):
        return str(self.boolean_dict)

def float_to_color(value):
    normalized_value = int((value + 1) * 127.5)
    return max(0, min(normalized_value, 255))

def change_hue(gray_color, new_hue):
    new_rgb = colorsys.hsv_to_rgb(new_hue / 360, 1, gray_color / 255)
    return tuple(int(x * 255) for x in new_rgb)

def desaturate_color(color, amount):
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

    return new_r, new_g, new_b

def draw_grid(screen, cells, scale, offset):
    cursor_xy = get_cursor_xy(cells, scale, offset)

    for row, col in np.ndindex(cells.shape):
        color = change_hue(gray_color=cells[row][col], new_hue=145)
        size = 5

        if cursor_xy:
            if row == cursor_xy[0] or col == cursor_xy[1]:
                color = desaturate_color(color, 90)
            

        pygame.draw.rect(screen, color,
                         (offset[0] * scale + col * size * scale, offset[1] * scale + row * size * scale,
                          size * scale, size * scale),
                         border_radius=1)

def get_cursor_xy(cells, scale, offset, size=5):
    mouse_pos = pygame.mouse.get_pos()
    for row, col in np.ndindex(cells.shape):
        rect = pygame.rect.Rect(offset[0] * scale + col * size * scale,
                                offset[1] * scale + row * size * scale,
                                size * scale, size * scale)

        if rect.collidepoint(mouse_pos):
            return row, col
        
    return None

def can_fit(dimensions, pos, tower_grid):
    grid_row, grid_col = pos
    width, height = tower_grid.shape

    for i in range(0, dimensions[0]):
        for j in range(0, dimensions[1]):
            y = grid_row + i
            x = grid_col + j
            if y >= height: return False
            if x >= width: return False

            if tower_grid[y, x] is not None:
                return False
    return True

# def calculate_angle(start_point, end_point):
#     delta_x = end_point[0] - start_point[0]
#     delta_y = end_point[1] - start_point[1]
#     angle_rad = math.atan2(delta_y, delta_x)
#     angle_deg = math.degrees(angle_rad)
#     return angle_deg

# def draw_line_with_length(screen, colour, start, end, length):
#     # Calculate the direction vector
#     direction_vector = [end[0] - start[0], end[1] - start[1]]

#     # Calculate the length of the direction vector
#     direction_length = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)

#     # Scale the direction vector to the desired length
#     scaled_direction = [direction_vector[0] * length / direction_length, 
#                         direction_vector[1] * length / direction_length]

#     # Calculate the end point based on the scaled direction vector
#     new_end = (start[0] + scaled_direction[0], start[1] + scaled_direction[1])

#     # Draw the line
#     pygame.draw.line(screen, colour, start, new_end, 5)

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