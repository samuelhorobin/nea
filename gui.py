import pygame
import settings

def display_game_stats(screen, font, elapsed_time, points, difficulty):
    minutes = int(elapsed_time / 60000)
    seconds = int((elapsed_time % 60000) / 1000)
    milliseconds = elapsed_time % 1000

    time_str = f"Time: {minutes:02}:{seconds:02}:{milliseconds:03}\n Points: {int(points)}\n Difficulty: {difficulty:.2f}"

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
    Level: {tower.level}\n\
    Health: {tower.health}/{tower.max_health}"
    
    text = font.render(stats_str , True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)  # Position the text in the upper right corner
    screen.blit(text, text_rect)

    return text_rect

def display_enemy_stats(screen, font, enemies, parent_rect = None):
    if enemies == None: return parent_rect
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
        Level: {enemy.level}\n\
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

def display_menu(screen, menu, pos, large_font, font):
    menu_texts = []
    menu_rects = []

    for key, value in menu.boolean_dict.items():
        if value:
            text = large_font.render(key, True, (255, 255, 255))
        else:
            text = font.render(key, True, (255, 255, 255))

        text_rect = text.get_rect()
        menu_texts.append(text)
        menu_rects.append(text_rect)

    menu_rects[0].topleft = pos

    for index in range(1, len(menu_rects)):
        menu_rects[index].topleft = (pos[0], menu_rects[index - 1].bottom + 10)

    for text, rect in zip(menu_texts, menu_rects):
        screen.blit(text, rect)

def render_gui(screen,
               large_font, font, small_font,
               tower_menu,
               paused, elapsed_time, Game_Data,
               selected_tower = None,
               selected_enemies = None):
    
    if paused:
        text = large_font.render("PAUSED" , True, (255, 255, 255))
        text_rect = text.get_rect()

        text_rect.midtop = (settings.resolution[0] // 2, 20)  # Position the text in the upper right corner
        screen.blit(text, text_rect)

    if selected_tower == []: selected_tower = None
    if selected_enemies == []: selected_enemies = None
    
    # top right gui
    bottom_rect = None
    for gui_function in [display_game_stats, display_tower_stats, display_enemy_stats]:
        if gui_function == display_game_stats:  bottom_rect = display_game_stats(screen, font, elapsed_time, Game_Data.points, Game_Data.difficulty)
        if gui_function == display_tower_stats: bottom_rect = display_tower_stats(screen, font, selected_tower, bottom_rect)
        if gui_function == display_enemy_stats: bottom_rect = display_enemy_stats(screen, font, selected_enemies, bottom_rect)

    # top left gui
    bottom_rect = None
    for gui_function in [display_personal_stats]:
        if gui_function == display_personal_stats: bottom_rect = display_personal_stats(screen, font, Game_Data.cash)

    
    # left gui
    display_menu(screen, tower_menu, (20, bottom_rect.bottom + 40), font, small_font)

def cursor_place_tower(screen, scale, offset,
                       cursor_xy, tower, small_font,
                       Game_Data, placeable):

    # A number between -6 and 6 that changes throughout the course of the frame
    frame_determinant = (Game_Data.count*3) % 120
    # A number that oscillates between 0 and 60
    resize_vector = frame_determinant if frame_determinant <= 60 else 120 - frame_determinant 
    # a number that oscillates between -3 and 3
    resize_vector = ((resize_vector // 10) - 3) / 2

    animation_adjustement = resize_vector 
    
    side_length = 10 if tower == "$800: Headquarters" else 5
    side_length += animation_adjustement

    rect = pygame.rect.Rect(((offset[0] - animation_adjustement / 2)*scale + cursor_xy[1]*5*scale, # x
                             (offset[1] - animation_adjustement / 2)*scale + cursor_xy[0]*5*scale), # y
                            (side_length*scale, side_length*scale))
    
    color = (255, 0, 0) if not placeable else (255, 255, 0)

    pygame.draw.rect(screen, color,
             rect,               # size
             border_radius=3) 

    if placeable:
        text = small_font.render(tower, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.bottomleft = (offset[0]*scale + cursor_xy[1]*5*scale,
                                offset[1]*scale + cursor_xy[0]*5*scale)  # Position the text in the upper right corner
        screen.blit(text, text_rect)