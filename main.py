import random
import pygame

pygame.init()

# COLORS
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 87, 32)
blue = (0, 0, 255)
yellow = (255, 255, 0)
aqua = (0, 255, 255)
purple = (255, 0, 255)

# SCREEN SETTINGS
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

snake_icon = pygame.image.load("images/snake.ico")
pygame.display.set_caption("Snake")
pygame.display.set_icon(snake_icon)

heart_image = pygame.image.load("images/heart.png")
heart_image = pygame.transform.scale(heart_image, (25, 25))
hearts_remaining = 3

# FONT SETTINGS
font_style = pygame.font.SysFont("TDAText", 15)
score_font = pygame.font.SysFont("TDAText", 25)

# SNAKE SETTINGS
snake_block = 10
snake_speed = 5

# SOUNDS
snake_start_sound = pygame.mixer.Sound('audio/snake_start.mp3')
snake_end_sound = pygame.mixer.Sound('audio/snake_end.mp3')
snake_hiss_ce_sound = pygame.mixer.Sound('audio/snake_hiss_ce.ogg')
snake_hiss_mh_sound = pygame.mixer.Sound('audio/snake_hiss_mh.ogg')

# MUSIC
music_ce = 'audio/music_ce.ogg'
music_mh = 'audio/music_mh.ogg'


def draw_boundaries():
    pygame.draw.rect(screen, green, [0, 0, screen_width, snake_block])  # Top
    pygame.draw.rect(screen, green, [0, screen_height - snake_block, screen_width, snake_block])  # Bottom
    pygame.draw.rect(screen, green, [0, 0, snake_block, screen_height])  # Left
    pygame.draw.rect(screen, green, [screen_width - snake_block, 0, snake_block, screen_height])  # Right


def draw_hearts():
    heart_spacing = 5
    total_width = hearts_remaining * (heart_image.get_width() + heart_spacing) - heart_spacing
    start_x = (screen_width - total_width) // 2
    y_pos = screen_height - 50

    for i in range(hearts_remaining):
        screen.blit(heart_image, (start_x + i * (heart_image.get_width() + heart_spacing), y_pos))


def draw_snake(block_size, segments):
    for segment in segments:
        pygame.draw.rect(screen, white, [segment[0], segment[1], block_size, block_size])


def load_high_score(mode):
    if mode == "M":
        record_file = "highscore_mh.txt"
    else:
        record_file = "highscore_ce.txt"

    try:
        with open(record_file) as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0


def save_high_score(score, mode):
    if mode == "M":
        record_file = "highscore_mh.txt"
    else:
        record_file = "highscore_ce.txt"

    with open(record_file, "w") as file:
        file.write(str(score))


def display_current_score(score):
    value = score_font.render("Your score: " + str(score), True, white)
    screen.blit(value, [25, 10])


def display_high_score(high_score):
    value = score_font.render("High score: " + str(high_score), True, white)
    screen.blit(value, [screen_width - 220, 10])


def show_message(text, font_size, color, x_offset=0, y_offset=0):
    if font_size == 15:
        message = font_style.render(text, True, color)
    elif font_size == 25:
        message = score_font.render(text, True, color)
    else:
        raise ValueError(f"Unsupported font size: {font_size}")

    message_rect = message.get_rect(center=(screen_width // 2 + x_offset, screen_height // 2 + y_offset))

    screen.blit(message, message_rect)


def pause_game():
    paused = True

    while paused:
        pygame.mixer.music.pause()

        pause_button = pygame.image.load('images/pause.png')
        pause_rect = pause_button.get_rect(center=(screen_width // 2, screen_height // 2))
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


def run_main_menu():
    intro = True

    while intro:
        screen.fill(black)
        show_message("Press C for classic easy mode or M for modern hard mode", 15, white)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    snake_start_sound.play()
                    pygame.mixer.music.load(music_ce)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    run_game_loop("C")

                elif event.key == pygame.K_m:
                    snake_start_sound.play()
                    pygame.mixer.music.load(music_mh)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    run_game_loop("M")

                elif event.key == pygame.K_q:
                    pygame.quit()
                    quit()


def run_game_loop(mode):
    game_over = False
    game_close = False
    new_high_score = False
    border_counter = 0
    growth_step = 1

    snake_list = []
    length_of_snake = 1
    x1 = screen_width / 2
    y1 = screen_height / 2
    x1_change = 0
    y1_change = 0
    global snake_speed, hearts_remaining

    food_x = round(random.randrange(40, screen_width - 40) / 10.0) * 10.0
    food_y = round(random.randrange(40, screen_height - 40) / 10.0) * 10.0
    color_list = [white, red, green, blue, aqua, purple, yellow]

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
            screen.fill(black)
            show_message("You lost! Press R to restart, M to exit to main menu or Q to quit", 15, red)

            pygame.mixer.music.stop()

            display_current_score(length_of_snake - 1)
            display_high_score(high_score)

            if new_high_score:
                screen.fill(black)
                show_message("Press R to restart, M to exit to main menu or Q to quit", 15, white, y_offset=80)
                show_message("NEW HIGH SCORE!", 25, red, -10, -40)
                show_message('Score: ' + str(high_score), 25, red, -10, 20)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False

                    # After a restart, the speed counter is reset
                    if event.key == pygame.K_r:
                        snake_speed = 5
                        hearts_remaining = 3
                        run_game_loop(mode)

                    if event.key == pygame.K_m:
                        snake_speed = 5
                        hearts_remaining = 3
                        run_main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            # The snake can be controlled both by the arrows and by using the WASD and numpad keys
            if event.type == pygame.KEYDOWN:
                if ((event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_KP4)
                        and x1_change != snake_block):
                    x1_change = -snake_block
                    y1_change = 0

                if ((event.key == pygame.K_RIGHT or event.key == pygame.K_d or event.key == pygame.K_KP6)
                        and x1_change != -snake_block):
                    x1_change = snake_block
                    y1_change = 0

                if ((event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_KP8)
                        and y1_change != snake_block):
                    x1_change = 0
                    y1_change = -snake_block

                if ((event.key == pygame.K_DOWN or event.key == pygame.K_s or event.key == pygame.K_KP2)
                        and y1_change != -snake_block):
                    x1_change = 0
                    y1_change = snake_block

                if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    pause_game()

                if event.key == pygame.K_q:
                    pygame.quit()
                    quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pause_game()

        if x1 >= screen_width:
            x1 = 0
        elif x1 < 0:
            x1 = screen_width - snake_block

        if y1 >= screen_height:
            y1 = 0
        elif y1 < 0:
            y1 = screen_height - snake_block

        x1 += x1_change
        y1 += y1_change

        if mode == "C":
            screen.fill(black)
            draw_hearts()

            # In this mode you cannot cross the border more than 3 times
            if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
                border_counter += 1
                hearts_remaining -= 1

                if hearts_remaining <= 0 or border_counter >= 3:
                    game_close = True
                    snake_end_sound.play()

            pygame.draw.circle(
                screen,
                white,
                (food_x + snake_block // 2, food_y + snake_block // 2),
                snake_block // 2)
        else:
            bg = pygame.image.load("images/grass.jpg")
            screen.blit(bg, (0, 0))
            draw_boundaries()

            if x1 >= screen_width or x1 < 0 or y1 >= screen_height or y1 < 0:
                game_close = True
                snake_end_sound.play()

            pygame.draw.circle(
                screen,
                random.choice(color_list),
                (food_x + snake_block // 2, food_y + snake_block // 2),
                snake_block // 1.5
            )

        snake_head = [x1, y1]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True
                snake_end_sound.play()

        draw_snake(snake_block, snake_list)
        display_current_score(length_of_snake - 1)
        display_high_score(high_score)

        if x1 == food_x and y1 == food_y:
            food_x = round(random.randrange(60, screen_width - 60) / 10.0) * 10.0
            food_y = round(random.randrange(60, screen_height - 60) / 10.0) * 10.0

            length_of_snake += growth_step

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

        current_score = length_of_snake - 1
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
    run_main_menu()
