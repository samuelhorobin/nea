import pygame
import numpy as np
import colorsys

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
