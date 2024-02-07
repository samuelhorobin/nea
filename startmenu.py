import pygame
import sys
import settings
import main

# Initialize Pygame
pygame.init()

# Define colors
BEIGE = (245, 245, 220)
BLACK = (0, 0, 0)

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Menu")

# Set up fonts
font = pygame.font.Font(None, 36)

# Define menu states
MAIN_MENU = 0
DIFFICULTY_MENU = 1
SETTINGS_MENU = 2

current_menu = MAIN_MENU
selected_difficulty = None
selected_resolution_index = 0

resolution = (1920, 1080)

# Common resolutions list
resolutions = [
    "800x600",
    "1024x768",
    "1280x720",
    "1366x768",
    "1440x900",
    "1600x900",
    "1680x1050",
    "1920x1080"
]

def resolution_string_to_tuple(resolution_string):
    width, height = map(int, resolution_string.split("x"))
    return (width, height)

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

running = True
while running:
    screen.fill(BEIGE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if current_menu == MAIN_MENU:
                if 200 < x < 600:
                    if 200 < y < 250:
                        current_menu = DIFFICULTY_MENU
                    elif 300 < y < 350:
                        current_menu = SETTINGS_MENU
                    elif 400 < y < 450:
                        pygame.quit()
                        sys.exit()
            elif current_menu == DIFFICULTY_MENU:
                if 200 < x < 600:
                    if 200 < y < 250:
                        selected_difficulty = "easy"
                        settings.update(selected_difficulty, resolution)
                        running = False
                    elif 300 < y < 350:
                        selected_difficulty = "medium"
                        settings.update(selected_difficulty, resolution)
                        running = False
                    elif 400 < y < 450:
                        selected_difficulty = "hard"
                        settings.update(selected_difficulty, resolution)
                        running = False
                    elif 500 < y < 550:
                        current_menu = MAIN_MENU
            elif current_menu == SETTINGS_MENU:
                if 200 < x < 600:
                    if 200 < y < 250:
                        selected_resolution_index = (selected_resolution_index + 1) % len(resolutions)
                        resolution = resolution_string_to_tuple(resolutions[selected_resolution_index])
                        settings.update(selected_difficulty, resolution)

                elif 400 < y < 450:
                    current_menu = MAIN_MENU

    if current_menu == MAIN_MENU:
        draw_text("Start", font, BLACK, WIDTH // 2, 225)
        draw_text("Settings", font, BLACK, WIDTH // 2, 325)
        draw_text("Exit", font, BLACK, WIDTH // 2, 425)
    elif current_menu == DIFFICULTY_MENU:
        draw_text("Easy", font, BLACK, WIDTH // 2, 225)
        draw_text("Medium", font, BLACK, WIDTH // 2, 325)
        draw_text("Hard", font, BLACK, WIDTH // 2, 425)
        draw_text("Back", font, BLACK, WIDTH // 2, 525)
    elif current_menu == SETTINGS_MENU:
        draw_text(f"Resolution: {resolutions[selected_resolution_index]}", font, BLACK, WIDTH // 2, 225)
        draw_text("Change Resolution by clicking resolution", font, BLACK, WIDTH // 2, 325)
        draw_text("Back", font, BLACK, WIDTH // 2, 425)

    pygame.display.flip()

if not running:
    main.main()
