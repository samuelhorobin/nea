import colorsys

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