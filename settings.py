import pygame

pygame.init()
infoObject = pygame.display.Info()

auto_resolution = True
resolution = (900, 700)
selected_difficulty = "easy"

if auto_resolution:
    resolution = (infoObject.current_w, infoObject.current_h)

def update(*args):
    global resolution, selected_difficulty
    resolution, selected_difficulty = args

