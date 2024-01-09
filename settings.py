import pygame

pygame.init()
infoObject = pygame.display.Info()

auto_resolution = True
resolution = (900, 700)

if auto_resolution:
    resolution = (infoObject.current_w, infoObject.current_h)