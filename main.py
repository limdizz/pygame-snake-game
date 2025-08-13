import math
import random
import pygame

pygame.init()

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 87, 32)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
AQUA = (0, 255, 255)
PURPLE = (255, 0, 255)

# --- Screen Settings ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Game Settings ---
SNAKE_BLOCK = 10
INITIAL_SPEED = 5
MAX_HEARTS = 3

snake_speed = INITIAL_SPEED
hearts_remaining = MAX_HEARTS

# --- Button Settings ---
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 150, 200)
BUTTON_TEXT_COLOR = WHITE

# --- Graphics ---
heart_image = pygame.transform.scale(pygame.image.load("images/heart.png"), (25, 25))
snake_icon = pygame.image.load("images/snake.ico")

pygame.display.set_caption("Snake")
pygame.display.set_icon(snake_icon)

# --- Fonts ---
font_style = pygame.font.SysFont("TDAText", 15)
score_font = pygame.font.SysFont("TDAText", 25)
menu_font = pygame.font.SysFont("TDAText", 30)

# --- Audio: sounds ---
snake_start_sound = pygame.mixer.Sound('audio/snake_start.mp3')
snake_end_sound = pygame.mixer.Sound('audio/snake_end.mp3')
snake_hiss_ce_sound = pygame.mixer.Sound('audio/snake_hiss_ce.ogg')
snake_hiss_mh_sound = pygame.mixer.Sound('audio/snake_hiss_mh.ogg')

# --- Audio: music ---
music_ce = 'audio/music_ce.ogg'
music_mh = 'audio/music_mh.ogg'


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, surface):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)

        text_surf = menu_font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hovered:
            if self.action:
                snake_start_sound.play()
                self.action()


def draw_boundaries():
    pygame.draw.rect(screen, GREEN, [0, 0, SCREEN_WIDTH, SNAKE_BLOCK])  # Top
    pygame.draw.rect(screen, GREEN, [0, SCREEN_HEIGHT - SNAKE_BLOCK, SCREEN_WIDTH, SNAKE_BLOCK])  # Bottom
    pygame.draw.rect(screen, GREEN, [0, 0, SNAKE_BLOCK, SCREEN_HEIGHT])  # Left
    pygame.draw.rect(screen, GREEN, [SCREEN_WIDTH - SNAKE_BLOCK, 0, SNAKE_BLOCK, SCREEN_HEIGHT])  # Right


def draw_hearts():
    heart_spacing = 5
    total_width = hearts_remaining * (heart_image.get_width() + heart_spacing) - heart_spacing
    start_x = (SCREEN_WIDTH - total_width) // 2
    y_pos = SCREEN_HEIGHT - 50

    for i in range(hearts_remaining):
        screen.blit(heart_image, (start_x + i * (heart_image.get_width() + heart_spacing), y_pos))


def draw_snake(block_size, segments):
    for segment in segments:
        pygame.draw.rect(screen, WHITE, [segment[0], segment[1], block_size, block_size])


def load_high_score(mode):
    if mode == "M":
        record_file = "saves/highscore_mh.txt"
    else:
        record_file = "saves/highscore_ce.txt"

    try:
        with open(record_file) as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score, mode):
    if mode == "M":
        record_file = "saves/highscore_mh.txt"
    else:
        record_file = "saves/highscore_ce.txt"

    with open(record_file, "w") as file:
        file.write(str(score))


def display_current_score(score, lang):
    if lang == "ru":
        value = score_font.render("Счёт: " + str(score), True, WHITE)
        screen.blit(value, [25, 10])

    elif lang == "en":
        value = score_font.render("Your score: " + str(score), True, WHITE)
        screen.blit(value, [25, 10])


def display_high_score(high_score, lang):
    if lang == "ru":
        value = score_font.render("Рекорд: " + str(high_score), True, WHITE)
        screen.blit(value, [SCREEN_WIDTH - 220, 10])

    elif lang == "en":
        value = score_font.render("High score: " + str(high_score), True, WHITE)
        screen.blit(value, [SCREEN_WIDTH - 220, 10])


def show_message(text, font_size, color, x_offset=0, y_offset=0):
    if font_size == 15:
        message = font_style.render(text, True, color)
    elif font_size == 25:
        message = score_font.render(text, True, color)
    else:
        raise ValueError(f"Unsupported font size: {font_size}")

    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2 + x_offset, SCREEN_HEIGHT // 2 + y_offset))

    screen.blit(message, message_rect)


def pause_game():
    paused = True

    while paused:
        pygame.mixer.music.pause()

        pause_button = pygame.image.load('images/pause.png')
        pause_rect = pause_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_button, pause_rect)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    paused = False
                    pygame.mixer.music.unpause()

                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                paused = False
                pygame.mixer.music.unpause()

        clock.tick(15)


def create_menu(title_text, buttons, back_function=None):
    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BLACK)

        title = menu_font.render(title_text, True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        if back_function is None:
            author = font_style.render("2024-2025. Владислав Клименко (Limdizz).", True, WHITE)
            screen.blit(author, (SCREEN_WIDTH // 2 - author.get_width() // 2, SCREEN_HEIGHT - 50))

        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons:
                    button.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and back_function:
                    back_function()
                    return

                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

        pygame.display.update()
        clock.tick(15)


def run_main_menu(lang):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Начать игру", lambda: select_mode_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Настройки", lambda: run_settings_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Выйти из игры", lambda: exit_game())
        ]

        create_menu("Змейка", buttons)

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Start the Game", lambda: select_mode_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Settings", lambda: run_settings_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Exit to Desktop", lambda: exit_game())
        ]

        create_menu("Snake: The Game", buttons)


def select_mode_menu(lang):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Классический", lambda: run_game_loop("C", "ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Современный", lambda: run_game_loop("M", "ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Назад", lambda: run_main_menu("ru"))
        ]

        create_menu("Выберите режим игры", buttons, lambda: run_main_menu("ru"))

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Classic Easy", lambda: run_game_loop("C", "en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Modern Hard", lambda: run_game_loop("M", "en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Back", lambda: run_main_menu("en"))
        ]

        create_menu("Select the game mode", buttons, lambda: run_main_menu("en"))


def run_settings_menu(lang):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Разрешение", lambda: run_resolution_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Язык", lambda: run_language_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Назад", lambda: run_main_menu("ru"))
        ]

        create_menu("Настройки", buttons, lambda: run_main_menu("ru"))

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Resolution", lambda: run_resolution_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Language", lambda: run_language_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Back", lambda: run_main_menu("en"))
        ]

        create_menu("Settings", buttons, lambda: run_main_menu("en"))


def change_resolution(width, height, menu_callback):
    global SCREEN_HEIGHT, SCREEN_WIDTH, screen
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.update()
    clock.tick(15)
    menu_callback()


def run_resolution_menu(lang):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "640x480", lambda: change_resolution(640, 480, lambda: run_resolution_menu("ru"))),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "800x600", lambda: change_resolution(800, 600, lambda: run_resolution_menu("ru"))),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "1280x720", lambda: change_resolution(1280, 720, lambda: run_resolution_menu("ru"))),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 410, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Назад", lambda: run_settings_menu("ru"))
        ]

        create_menu("Разрешение", buttons, lambda: run_settings_menu("ru"))

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "640x480", lambda: change_resolution(640, 480, lambda: run_resolution_menu("en"))),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "800x600", lambda: change_resolution(800, 600, lambda: run_resolution_menu("en"))),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "1280x720", lambda: change_resolution(1280, 720, lambda: run_resolution_menu("en"))),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 410, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Back", lambda: run_settings_menu("en"))
        ]

        create_menu("Resolution", buttons, lambda: run_settings_menu("en"))


def run_language_menu(lang):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Русский", lambda: run_language_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "English", lambda: run_language_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Назад", lambda: run_settings_menu("ru"))
        ]

        create_menu("Язык", buttons, lambda: run_settings_menu("ru"))

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Русский", lambda: run_language_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "English", lambda: run_language_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Back", lambda: run_settings_menu("en"))
        ]

        create_menu("Language", buttons, lambda: run_settings_menu("en"))


def lose_game_menu(mode, lang):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Начать заново",
                   lambda: restart_game(mode, "ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT, "Выйти в меню",
                   lambda: run_main_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Выйти из игры", lambda: exit_game())
        ]

        create_menu("Вы проиграли", buttons)

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Restart",
                   lambda: restart_game(mode, "en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT, "Exit to Menu",
                   lambda: run_main_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Exit to Desktop", lambda: exit_game())
        ]

        create_menu("You lost", buttons)


def new_high_score_menu(mode, score=0, lang="ru"):
    if lang == "ru":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Начать заново",
                   lambda: restart_game(mode, "ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT, "Выйти в меню",
                   lambda: run_main_menu("ru")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Выйти из игры", lambda: exit_game())
        ]

        create_menu(f"Новый рекорд: {score}", buttons)

    elif lang == "en":
        buttons = [
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 200, BUTTON_WIDTH, BUTTON_HEIGHT, "Restart",
                   lambda: restart_game(mode, "en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 270, BUTTON_WIDTH, BUTTON_HEIGHT, "Exit to Menu",
                   lambda: run_main_menu("en")),
            Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 340, BUTTON_WIDTH, BUTTON_HEIGHT,
                   "Exit to Desktop", lambda: exit_game())
        ]

        create_menu(f"New High Score: {score}", buttons)


def restart_game(mode, lang="ru"):
    global snake_speed, hearts_remaining

    snake_speed = INITIAL_SPEED
    hearts_remaining = MAX_HEARTS

    if lang == "ru":
        run_game_loop(mode, "ru")
    elif lang == "en":
        run_game_loop(mode, "en")


def exit_game():
    pygame.quit()
    quit()


def run_game_loop(mode, lang="ru"):
    game_over = False
    game_close = False
    new_high_score = False
    border_counter = 0
    growth_step = 1

    snake_list = []
    length_of_snake = 1
    x1 = SCREEN_WIDTH / 2
    y1 = SCREEN_HEIGHT / 2
    x1_change = 0
    y1_change = 0
    global snake_speed, hearts_remaining

    food_x = round(random.randrange(40, SCREEN_WIDTH - 40) / 10.0) * 10.0
    food_y = round(random.randrange(40, SCREEN_HEIGHT - 40) / 10.0) * 10.0
    color_list = [WHITE, RED, GREEN, BLUE, AQUA, PURPLE, YELLOW]

    bonus_ball_counter = 0
    bonus_active = False
    bonus_x = None
    bonus_y = None
    bonus_threshold = 5
    bonus_radius = int(SNAKE_BLOCK * 1.25)

    current_score = 0
    high_score = load_high_score(mode)

    if mode == "C":
        pygame.mixer.music.load(music_ce)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.load(music_mh)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    while not game_over:
        while game_close:
            screen.fill(BLACK)

            pygame.mixer.music.stop()

            if new_high_score:
                screen.fill(BLACK)

                if mode == "C" and lang == "en":
                    new_high_score_menu("C", high_score, "en")
                elif mode == "C" and lang == "ru":
                    new_high_score_menu("C", high_score, "ru")

                if mode == "M" and lang == "en":
                    new_high_score_menu("M", high_score, "en")
                elif mode == "M" and lang == "ru":
                    new_high_score_menu("M", high_score, "ru")

            else:
                if mode == "C" and lang == "en":
                    lose_game_menu("C", "en")
                elif mode == "C" and lang == "ru":
                    lose_game_menu("C", "ru")

                if mode == "M" and lang == "en":
                    lose_game_menu("M", "en")
                elif mode == "M" and lang == "ru":
                    lose_game_menu("M", "ru")

            display_current_score(current_score, "ru")
            display_high_score(high_score, "ru")

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            # The snake can be controlled both by the arrows and by using the WASD and numpad keys
            if event.type == pygame.KEYDOWN:
                if ((event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_KP4)
                        and x1_change != SNAKE_BLOCK):
                    x1_change = -SNAKE_BLOCK
                    y1_change = 0

                if ((event.key == pygame.K_RIGHT or event.key == pygame.K_d or event.key == pygame.K_KP6)
                        and x1_change != -SNAKE_BLOCK):
                    x1_change = SNAKE_BLOCK
                    y1_change = 0

                if ((event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_KP8)
                        and y1_change != SNAKE_BLOCK):
                    x1_change = 0
                    y1_change = -SNAKE_BLOCK

                if ((event.key == pygame.K_DOWN or event.key == pygame.K_s or event.key == pygame.K_KP2)
                        and y1_change != -SNAKE_BLOCK):
                    x1_change = 0
                    y1_change = SNAKE_BLOCK

                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    pause_game()

                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pause_game()

        if x1 >= SCREEN_WIDTH:
            x1 = 0
        elif x1 < 0:
            x1 = SCREEN_WIDTH - SNAKE_BLOCK

        if y1 >= SCREEN_HEIGHT:
            y1 = 0
        elif y1 < 0:
            y1 = SCREEN_HEIGHT - SNAKE_BLOCK

        x1 += x1_change
        y1 += y1_change

        if mode == "C":
            screen.fill(BLACK)
            draw_hearts()

            # In this mode you cannot cross the border more than 3 times
            if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
                border_counter += 1
                hearts_remaining -= 1

                if hearts_remaining <= 0 or border_counter >= 3:
                    game_close = True
                    snake_end_sound.play()

            pygame.draw.circle(
                screen,
                WHITE,
                (food_x + SNAKE_BLOCK // 2, food_y + SNAKE_BLOCK // 2),
                SNAKE_BLOCK // 2)

            if bonus_active:
                pygame.draw.circle(
                    screen,
                    random.choice(color_list),
                    (int(bonus_x + SNAKE_BLOCK // 2), int(bonus_y + SNAKE_BLOCK // 2)),
                    bonus_radius
                )
        else:
            bg = pygame.image.load("images/grass.jpg")
            screen.blit(bg, (0, 0))
            draw_boundaries()

            if x1 >= SCREEN_WIDTH or x1 < 0 or y1 >= SCREEN_HEIGHT or y1 < 0:
                game_close = True
                snake_end_sound.play()

            pygame.draw.circle(
                screen,
                random.choice(color_list),
                (food_x + SNAKE_BLOCK // 2, food_y + SNAKE_BLOCK // 2),
                SNAKE_BLOCK // 1.5
            )

            if bonus_active:
                size = bonus_radius * 2
                points = [
                    (bonus_x, bonus_y + size // 2),
                    (bonus_x + size // 2, bonus_y),
                    (bonus_x + size, bonus_y + size // 2),
                    (bonus_x + size // 2, bonus_y + size)
                ]
                pygame.draw.polygon(screen, random.choice(color_list), points)

        snake_head = [x1, y1]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True
                snake_end_sound.play()

        draw_snake(SNAKE_BLOCK, snake_list)

        if lang == "ru":
            display_current_score(current_score, "ru")
            display_high_score(high_score, "ru")
        elif lang == "en":
            display_current_score(current_score, "en")
            display_high_score(high_score, "en")

        if x1 == food_x and y1 == food_y:
            food_x = round(random.randrange(60, SCREEN_WIDTH - 60) / 10.0) * 10.0
            food_y = round(random.randrange(60, SCREEN_HEIGHT - 60) / 10.0) * 10.0

            length_of_snake += growth_step
            current_score += growth_step
            bonus_ball_counter += 1

            if bonus_ball_counter >= bonus_threshold and not bonus_active:
                bonus_x = round(random.randrange(60, SCREEN_WIDTH - 60) / 10.0) * 10.0
                bonus_y = round(random.randrange(60, SCREEN_HEIGHT - 60) / 10.0) * 10.0
                bonus_active = True
                bonus_ball_counter = 0

            if mode == "M":
                # In this mode the score counter increases in an arithmetic progression
                growth_step += 2
                snake_hiss_mh_sound.play()

            if mode == "C":
                snake_hiss_ce_sound.play()

            # The snake speed increases with every eaten food
            if snake_speed < 60 and mode == "C":
                snake_speed += 0.75
            elif snake_speed < 600 and mode == "M":
                snake_speed += 2

        if bonus_active:
            bonus_center_x = bonus_x + bonus_radius
            bonus_center_y = bonus_y + bonus_radius

            snake_center_x = x1 + SNAKE_BLOCK // 2
            snake_center_y = y1 + SNAKE_BLOCK // 2

            distance = math.hypot(snake_center_x - bonus_center_x, snake_center_y - bonus_center_y)

            if distance < bonus_radius + SNAKE_BLOCK // 2:
                bonus_active = False

                if mode == "C":
                    bonus_reduction_ce = 3
                    length_of_snake = max(1, length_of_snake - bonus_reduction_ce)
                    del snake_list[:min(bonus_reduction_ce, len(snake_list))]

                elif mode == "M":
                    new_length = max(1, length_of_snake // 2)
                    bonus_reduction_mh = length_of_snake - new_length
                    length_of_snake = new_length
                    del snake_list[:min(bonus_reduction_mh, len(snake_list))]

        if current_score > high_score:
            high_score = current_score
            save_high_score(high_score, mode)
            new_high_score = True

        pygame.display.update()
        clock.tick(snake_speed)

    pygame.quit()
    quit()


if __name__ == "__main__":
    clock = pygame.time.Clock()
    run_main_menu("ru")
