import pygame
import numpy as np

pygame.init()

class ExclusiveBooleanList:
    def __init__(self, names):
        self.boolean_dict = {name: False for name in names}

    def set_true(self, name):
        if name in self.boolean_dict:
            self.boolean_dict = {key: False for key in self.boolean_dict}
            self.boolean_dict[name] = True
        else:
            raise ValueError(f"Invalid name: {name}")

    def none_true(self):
        return all(not val for val in self.boolean_dict.values())

    def __str__(self):
        return str(self.boolean_dict)
    
def rgb_to_hls(r, g, b):
    c_max = max(r, g, b)
    c_min = min(r, g, b)
    
    # Calculate lightness
    l = (c_max + c_min) / 2.0

    # Calculate saturation
    if c_max == c_min:
        s = 0
    else:
        d = c_max - c_min
        s = d / (2 - c_max - c_min) if l > 0.5 else d / (c_max + c_min)

    # Calculate hue
    if c_max == r:
        h = (g - b) / d + (6 if g < b else 0) if d != 0 else 0
    elif c_max == g:
        h = (b - r) / d + 2 if d != 0 else 0
    else:
        h = (r - g) / d + 4 if d != 0 else 0
    h /= 6

    return h, l, s


def hls_to_rgb(h, l, s):
    if s == 0:
        return l, l, l
    else:
        if l < 0.5:
            q = l * (1 + s)
        else:
            q = l + s - l * s

        p = 2 * l - q
        new_r = hue_to_rgb(p, q, h + 1/3)
        new_g = hue_to_rgb(p, q, h)
        new_b = hue_to_rgb(p, q, h - 1/3)

        return new_r, new_g, new_b
    
def hue_to_rgb(p, q, t):
    if t < 0:
        t += 1
    if t > 1:
        t -= 1
    if t < 1/6:
        return p + (q - p) * 6 * t
    if t < 1/2:
        return q
    if t < 2/3:
        return p + (q - p) * (2/3 - t) * 6
    return p

def float_to_color(value):
    normalized_value = int((value + 1) * 127.5)
    return max(0, min(normalized_value, 255))

def change_hue(gray_color, new_hue):
    # Convert the gray color to RGB
    gray_normalized = gray_color / 255.0
    r, g, b = gray_normalized, gray_normalized, gray_normalized

    # Convert RGB to HLS
    h, l, s = rgb_to_hls(r, g, b)

    # Update hue
    h = new_hue / 360.0

    # Convert HLS back to RGB
    new_r, new_g, new_b = hls_to_rgb(h, l, s)

    # Convert back to integer RGB values
    new_r = int(new_r * 255)
    new_g = int(new_g * 255)
    new_b = int(new_b * 255)

    return new_r, new_g, new_b

def desaturate_color(color, amount):
    # Ensure the amount is within the valid range of 0 to 255
    amount = max(0, min(amount, 255))

    # Convert the RGB color to HLS color space manually
    r, g, b = color
    r_normalized, g_normalized, b_normalized = r / 255.0, g / 255.0, b / 255.0

    # Find the maximum and minimum values
    c_max = max(r_normalized, g_normalized, b_normalized)
    c_min = min(r_normalized, g_normalized, b_normalized)
    
    # Calculate lightness
    l = (c_max + c_min) / 2.0

    # Calculate saturation
    if c_max == c_min:
        s = 0
    else:
        d = c_max - c_min
        s = d / (2 - c_max - c_min) if l > 0.5 else d / (c_max + c_min)

    # Calculate hue
    if c_max == r_normalized:
        h = (g_normalized - b_normalized) / d + (6 if g_normalized < b_normalized else 0)
    elif c_max == g_normalized:
        h = (b_normalized - r_normalized) / d + 2
    else:
        h = (r_normalized - g_normalized) / d + 4
    h /= 6

    # Desaturate the color by adjusting its saturation
    new_s = max(0, s - (amount / 255.0))

    # Convert the color back to RGB manually
    if new_s == 0:
        new_r, new_g, new_b = l, l, l
    else:
        if l < 0.5:
            q = l * (1 + new_s)
        else:
            q = l + new_s - l * new_s

        p = 2 * l - q
        new_r = hue_to_rgb(p, q, h + 1/3)
        new_g = hue_to_rgb(p, q, h)
        new_b = hue_to_rgb(p, q, h - 1/3)

    # Convert back to integer RGB values
    new_r = int(new_r * 255)
    new_g = int(new_g * 255)
    new_b = int(new_b * 255)

    return new_r, new_g, new_b

def draw_grid(screen, cells, scale, offset):
    cursor_xy = get_cursor_xy(cells, scale, offset)

    for row, col in np.ndindex(cells.shape):
        color = change_hue(gray_color=cells[row][col], 
                                 new_hue=145)
        size = 5

        if cursor_xy:
            if row == cursor_xy[0] or col == cursor_xy[1]:
                desaturate_val = 90
                color = desaturate_color(color, desaturate_val)

        
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