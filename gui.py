import pygame
import settings

def display_game_stats(screen, font, elapsed_time, points, difficulty):
    '''
    Displays game statistics on the screen.

    Parameters:
    - screen: Pygame screen surface
    - font: Pygame font for rendering text
    - elapsed_time: Elapsed time in milliseconds
    - points: Player's points
    - difficulty: Current game difficulty

    Returns:
    - Pygame Rect object representing the position of the displayed text
    '''

    # Calculate time components from milliseconds
    minutes = int(elapsed_time / 60000)
    seconds = int((elapsed_time % 60000) / 1000)
    milliseconds = elapsed_time % 1000

    # Format the time and game stats into a string
    time_str = f"Time: {minutes:02}:{seconds:02}:{milliseconds:03}\n Points: {int(points)}\n Difficulty: {difficulty:.2f}"

    # Render the text and position it in the upper right corner
    text = font.render(time_str, True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, 20)
    screen.blit(text, text_rect)

    return text_rect

def display_tower_stats(screen, font, tower, parent_rect=None):
    '''
    Displays tower statistics on the screen.

    Parameters:
    - screen: Pygame screen surface
    - font: Pygame font for rendering text
    - tower: Tower object with name, level, health, and max_health attributes
    - parent_rect: Pygame Rect object representing the position of the parent text block

    Returns:
    - Pygame Rect object representing the position of the displayed text
    '''

    # Exit early if no tower is selected
    if tower is None: return parent_rect
    # Determine vertical position based on previous text block
    y_displacement = parent_rect.bottom if parent_rect else 0
    
    # Format the tower stats into a string
    stats_str = f"\
    Selected tower:\n\
    Name: {tower.name}\n\
    Level: {tower.level}\n\
    Health: {tower.health}/{tower.max_health}"
    
    # Render and position the tower stats text
    text = font.render(stats_str, True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)
    screen.blit(text, text_rect)

    return text_rect

def display_enemy_stats(screen, font, enemies, parent_rect=None):
    '''
    Displays enemy statistics on the screen.

    Parameters:
    - screen: Pygame screen surface
    - font: Pygame font for rendering text
    - enemies: List of enemy objects with name, level, health, and max_health attributes
    - parent_rect: Pygame Rect object representing the position of the parent text block

    Returns:
    - Pygame Rect object representing the position of the displayed text
    '''

    # Exit early if no enemies are selected
    if enemies is None: return parent_rect
    # Determine vertical position based on previous text block
    y_displacement = parent_rect.bottom if parent_rect else 0

    # Render and position the "Selected enemies" header
    text_str = "Selected enemies:"
    text = font.render(text_str, True, (255, 255, 255))
    parent_rect = text_rect = text.get_rect()
    text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)
    screen.blit(text, text_rect)

    # Adjust vertical position for enemy stats
    y_displacement = parent_rect.bottom - 20 

    # Loop through and display stats for each selected enemy
    for enemy in enemies:
        stats_str = f"\
        Name: {enemy.name}\n\
        Level: {enemy.level}\n\
        Health: {enemy.health}/{enemy.max_health}"
    
        text = font.render(stats_str, True, (255, 255, 255))
        parent_rect = text_rect = text.get_rect()
        text_rect.topright = (settings.resolution[0] - 20, y_displacement + 20)
        screen.blit(text, text_rect)

        y_displacement = parent_rect.bottom

    return parent_rect

def display_personal_stats(screen, font, cash):
    '''
    Displays personal cash statistics on the screen.

    Parameters:
    - screen: Pygame screen surface
    - font: Pygame font for rendering text
    - cash: Current player's cash amount

    Returns:
    - Pygame Rect object representing the position of the displayed text
    '''

    # Format and display personal cash stats
    stats_str = f"Cash: {cash:.0f}"
    text = font.render(stats_str, True, (255, 255, 255))
    text_rect = text.get_rect()
    text_rect.topleft = (20, 20)
    screen.blit(text, text_rect)

    return text_rect

def display_menu(screen, menu, pos, large_font, font):
    '''
    Displays a menu on the screen.

    Parameters:
    - screen: Pygame screen surface
    - menu: Menu object with boolean_dict attribute
    - pos: Tuple representing the position of the menu
    - large_font: Pygame font for rendering large text
    - font: Pygame font for rendering text
    '''

    menu_texts = []
    menu_rects = []

    # Loop through menu items and render text for each, applying a different style if the item is selected
    for key, value in menu.boolean_dict.items():
        if value:
            text = large_font.render(key, True, (255, 255, 255))
        else:
            text = font.render(key, True, (255, 255, 255))

        text_rect = text.get_rect()
        menu_texts.append(text)
        menu_rects.append(text_rect)

    # Position the first menu item
    menu_rects[0].topleft = pos

    # Position remaining menu items below the first, with spacing
    for index in range(1, len(menu_rects)):
        menu_rects[index].topleft = (pos[0], menu_rects[index - 1].bottom + 10)

    # Display all menu items
    for text, rect in zip(menu_texts, menu_rects):
        screen.blit(text, rect)

def render_gui(screen,
               large_font, font, small_font,
               tower_menu,
               paused, alive, elapsed_time, Game_Data,
               selected_tower=None,
               selected_enemies=None):
    '''
    Renders the graphical user interface (GUI) on the screen.

    Parameters:
    - screen: Pygame screen surface
    - large_font: Pygame font for rendering large text
    - font: Pygame font for rendering text
    - small_font: Pygame font for rendering small text
    - tower_menu: Menu object representing the tower menu
    - paused: Boolean indicating whether the game is paused
    - alive: Boolean indicating whether the player is alive
    - elapsed_time: Elapsed time in milliseconds
    - Game_Data: Object containing game-related data (points, difficulty, cash, etc.)
    - selected_tower: Tower object representing the currently selected tower (default is None)
    - selected_enemies: List of enemy objects representing the currently selected enemies (default is None)
    '''

    # Display pause or death message if the game is paused or the player has died
    if paused or not alive:
        message = "PAUSED" if alive else "YOU DIED"
        text = large_font.render(message, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.midtop = (settings.resolution[0] // 2, 20)
        screen.blit(text, text_rect)

    # Normalize the selected tower and enemies lists
    if selected_tower == []: selected_tower = None
    if selected_enemies == []: selected_enemies = None
    
    # Display game, tower, and enemy stats in the top right
    bottom_rect = None
    for gui_function in [display_game_stats, display_tower_stats, display_enemy_stats]:
        if gui_function == display_game_stats:
            bottom_rect = display_game_stats(screen, font, elapsed_time, Game_Data.points, Game_Data.difficulty)
        elif gui_function == display_tower_stats:
            bottom_rect = display_tower_stats(screen, font, selected_tower, bottom_rect)
        elif gui_function == display_enemy_stats:
            bottom_rect = display_enemy_stats(screen, font, selected_enemies, bottom_rect)

    # Display personal stats in the top left
    bottom_rect = None
    for gui_function in [display_personal_stats]:
        if gui_function == display_personal_stats:
            bottom_rect = display_personal_stats(screen, font, Game_Data.cash)

    # Display the tower menu on the left
    display_menu(screen, tower_menu, (20, bottom_rect.bottom + 40), font, small_font)

def cursor_place_tower(screen, scale, offset,
                       cursor_xy, tower, small_font,
                       Game_Data, placeable):
    '''
    Visually assists with tower placement, indicating color and size adjustments based on the game state.

    Parameters:
    - screen: Pygame screen surface
    - scale: Scale factor for resizing elements
    - offset: Tuple representing the offset for placement adjustments
    - cursor_xy: Tuple representing the cursor position
    - tower: String representing the tower name
    - small_font: Pygame font for rendering small text
    - Game_Data: Object containing game-related data (count)
    - placeable: Boolean indicating whether tower placement is allowed

    Returns:
    - None
    '''

    # Visualize tower placement, adjusting color and size based on the game state
    frame_determinant = (Game_Data.count * 3) % 120
    resize_vector = frame_determinant if frame_determinant <= 60 else 120 - frame_determinant
    resize_vector = ((resize_vector // 10) - 3) / 2
    animation_adjustment = resize_vector
    
    side_length = 10 if tower == "$800: Headquarters" else 5
    side_length += animation_adjustment

    rect = pygame.rect.Rect(((offset[0] - animation_adjustment / 2) * scale + cursor_xy[1] * 5 * scale,
                             (offset[1] - animation_adjustment / 2) * scale + cursor_xy[0] * 5 * scale),
                            (side_length * scale, side_length * scale))
    
    color = (255, 0, 0) if not placeable else (255, 255, 0)

    pygame.draw.rect(screen, color, rect, border_radius=3)

    if placeable:
        text = small_font.render(tower, True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.bottomleft = (offset[0] * scale + cursor_xy[1] * 5 * scale,
                                offset[1] * scale + cursor_xy[0] * 5 * scale)
        screen.blit(text, text_rect)
