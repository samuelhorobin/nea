import pygame
import settings

def display_game_stats(screen, font, elapsed_time, points, difficulty):
    minutes = int(elapsed_time / 60000)
    seconds = int((elapsed_time % 60000) / 1000)
    milliseconds = elapsed_time % 1000

    time_str = f"\
    Time: {minutes:02}:{seconds:02}:{milliseconds:03}\n\
    Points: {int(points)}\n\
    Difficulty: {difficulty:.2f}\
        "

    text = font.render(time_str , True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, 20)  # Position the text in the upper right corner
    screen.blit(text, text_rect)

    return text_rect

def display_tower_stats(screen, font, tower, parent_rect = None):
    if tower == None: return parent_rect
    y_displacement = parent_rect.bottom if parent_rect else 0
    
    stats_str =f"\
    Selected tower:\n\
    Name: {tower.name}\n\
    Health: {tower.health}/{tower.max_health}"
    
    text = font.render(stats_str , True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)  # Position the text in the upper right corner
    screen.blit(text, text_rect)

    return text_rect

def display_enemy_stats(screen, font, enemies, parent_rect = None):
    if enemies == []: return parent_rect
    y_displacement = parent_rect.bottom if parent_rect else 0

    text_str = f"Selected enemies:"
    text = font.render(text_str , True, (255, 255, 255))
    parent_rect = text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)  # Position the text in the upper right corner
    screen.blit(text, text_rect)

    y_displacement = parent_rect.bottom - 20 

    for enemy in enemies:
        stats_str =f"\
        Name: {enemy.name}\n\
        Health: {enemy.health}/{enemy.max_health}"
    
        text = font.render(stats_str , True, (255, 255, 255))
        parent_rect = text_rect = text.get_rect()
        text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)  # Position the text in the upper right corner
        screen.blit(text, text_rect)

        y_displacement = parent_rect.bottom

    return parent_rect

def display_personal_stats(screen, font, cash):

    stats_str = f"\
    Cash: {cash:.0f}"

    text = font.render(stats_str , True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topleft = (20, 20)  # Position the text in the upper right corner
    screen.blit(text, text_rect)

    return text_rect

def render_gui(screen,
               font, elapsed_time, points, difficulty, cash,
               selected_tower = None,
               selected_enemies = None):
    
    # top right gui
    bottom_rect = None
    for gui_function in [display_game_stats, display_tower_stats, display_enemy_stats]:
        if gui_function == display_game_stats:       bottom_rect = display_game_stats(screen, font, elapsed_time, points, difficulty)
        if gui_function == display_tower_stats: bottom_rect = display_tower_stats(screen, font, selected_tower, bottom_rect)
        if gui_function == display_enemy_stats: bottom_rect = display_enemy_stats(screen, font, selected_enemies, bottom_rect)

    # top left gui
    bottom_rect = None
    for gui_function in [display_personal_stats]:
        if gui_function == display_personal_stats: bottom_rect = display_personal_stats(screen, font, cash)
        