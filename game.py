import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("疯狂奶茶杯")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
PEACH = (255, 218, 185)
BROWN = (139, 90, 43)
CREAM = (255, 253, 208)
DARK_PINK = (219, 112, 147)

bg_color = (255, 218, 185)
game_bg_color = (240, 240, 240)
BUTTON_COLORS = {
    "normal": (255, 182, 193),
    "hover": (255, 105, 180),
    "press": (219, 112, 147),
}

cup_img = pygame.image.load("f:/code/BCI_gane/cup.webp").convert_alpha()
ingredient_img = pygame.image.load("f:/code/BCI_gane/小料.webp").convert_alpha()

cup_width = 100
cup_height = 120
cup_img = pygame.transform.scale(cup_img, (cup_width, cup_height))
ingredient_img = pygame.transform.scale(ingredient_img, (50, 50))

font_path = "C:/Windows/Fonts/simhei.ttf"
title_font = pygame.font.Font(font_path, 56)
button_font = pygame.font.Font(font_path, 32)


class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.bob_offset = 0
        self.bob_speed = 0
        self.bob_amplitude = 0

    def update(self, mouse_pos, mouse_pressed):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.pressed = mouse_pressed and self.hovered

        if self.hovered:
            self.bob_speed = 0.15
            self.bob_amplitude = 3
        else:
            self.bob_speed = 0
            self.bob_amplitude = 0
            self.bob_offset = 0

        if self.bob_amplitude > 0:
            self.bob_offset = (
                math.sin(pygame.time.get_ticks() * 0.005) * self.bob_amplitude
            )

    def draw(self, surface, y_offset=0):
        draw_rect = self.rect.copy()
        draw_rect.y += int(self.bob_offset) + y_offset

        color = (
            BUTTON_COLORS["press"]
            if self.pressed
            else (BUTTON_COLORS["hover"] if self.hovered else BUTTON_COLORS["normal"])
        )

        pygame.draw.rect(surface, BLACK, draw_rect.inflate(8, 8), border_radius=8)
        pygame.draw.rect(surface, color, draw_rect, border_radius=8)

        pygame.draw.rect(surface, CREAM, draw_rect.inflate(-8, -8), 3, border_radius=6)

        text_surf = button_font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self):
        if self.hovered and self.callback:
            self.callback()


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.size = random.randint(3, 8)
        self.color = random.choice([PINK, PEACH, CREAM])
        self.life = random.randint(30, 60)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(
                surface, self.color, (self.x, self.y, self.size, self.size)
            )


class Cup:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 120)
        self.image = cup_img
        self.bob_offset = 0

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.centerx = mouse_x
        self.rect.bottom = HEIGHT - 50
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 5

    def draw(self, surface):
        draw_rect = self.rect.copy()
        draw_rect.y += int(self.bob_offset)
        surface.blit(self.image, draw_rect)


class Ingredient:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.image = ingredient_img
        self.active = True

    def update(self, speed):
        if self.active:
            self.rect.y += speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def show_menu():
    menu_running = True
    game_state = [None]

    title = "疯狂奶茶杯"

    def start_game_click():
        game_state[0] = "start_game"
        nonlocal menu_running
        menu_running = False

    def level_select_click():
        game_state[0] = "level_select"
        nonlocal menu_running
        menu_running = False

    def settings_click():
        game_state[0] = "settings"
        nonlocal menu_running
        menu_running = False

    buttons = [
        Button(WIDTH // 2 - 100, 250, 200, 60, "开始游戏", start_game_click),
        Button(WIDTH // 2 - 100, 330, 200, 60, "关卡选择", level_select_click),
        Button(WIDTH // 2 - 100, 410, 200, 60, "游戏设置", settings_click),
    ]

    particles = []
    last_spawn = pygame.time.get_ticks()

    clock = pygame.time.Clock()

    while menu_running:
        current_time = pygame.time.get_ticks()

        screen.fill(bg_color)

        for i in range(0, WIDTH, 40):
            for j in range(0, HEIGHT, 40):
                if (i // 40 + j // 40) % 2 == 0:
                    pygame.draw.rect(screen, (255, 232, 205), (i, j, 40, 40))

        if current_time - last_spawn > 100:
            particles.append(Particle(random.randint(50, WIDTH - 50), HEIGHT + 20))
            last_spawn = current_time

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0 or p.y > HEIGHT + 50:
                particles.remove(p)

        cup_bob = math.sin(current_time * 0.002) * 10
        cup_y_offset = 80 + int(cup_bob)
        screen.blit(cup_img, (WIDTH // 2 - 50, cup_y_offset))

        title_surf = title_font.render(title, True, BROWN)
        title_outline = title_font.render(title, True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 40))
        screen.blit(title_outline, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_surf, title_rect)

        for button in buttons:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()[0]
            button.update(mouse_pos, mouse_pressed)
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in buttons:
                        button.handle_click()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        pygame.display.flip()
        clock.tick(60)

    return game_state[0] if game_state[0] else "start_game"


def show_level_select():
    select_running = True

    font = pygame.font.Font(font_path, 32)
    title_surf = font.render("关卡选择", True, BROWN)

    back_button = Button(WIDTH // 2 - 60, 500, 120, 50, "返回", None)

    clock = pygame.time.Clock()

    while select_running:
        screen.fill(bg_color)

        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        back_button.update(mouse_pos, mouse_pressed)
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    back_button.handle_click()
                    select_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    select_running = False

        pygame.display.flip()
        clock.tick(60)

    return "menu"


def show_settings():
    settings_running = True

    font = pygame.font.Font(font_path, 32)
    title_surf = font.render("游戏设置", True, BROWN)

    back_button = Button(WIDTH // 2 - 60, 500, 120, 50, "返回", None)

    clock = pygame.time.Clock()

    while settings_running:
        screen.fill(bg_color)

        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 50))

        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        back_button.update(mouse_pos, mouse_pressed)
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    back_button.handle_click()
                    settings_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_running = False

        pygame.display.flip()
        clock.tick(60)

    return "menu"


def main():
    game_state = "menu"
    clock = pygame.time.Clock()
    running = True

    cup = Cup(WIDTH // 2, HEIGHT - 50)
    ingredients = []
    fall_speed = 3.0

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 2000)

    collected = 0

    buttons = [
        Button(WIDTH // 2 - 100, 250, 200, 60, "开始游戏", lambda: "start_game"),
        Button(WIDTH // 2 - 100, 330, 200, 60, "关卡选择", lambda: "level_select"),
        Button(WIDTH // 2 - 100, 410, 200, 60, "游戏设置", lambda: "settings"),
    ]

    while running:
        screen.fill(game_bg_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "menu":
                menu_result = show_menu()
                if menu_result == "quit":
                    running = False
                    game_state = "quit"
                elif menu_result == "level_select":
                    game_state = "level_select"
                elif menu_result == "settings":
                    game_state = "settings"

            elif game_state == "level_select":
                level_result = show_level_select()
                if level_result == "quit":
                    running = False
                    game_state = "quit"
                elif level_result == "menu":
                    game_state = "menu"

            elif game_state == "settings":
                settings_result = show_settings()
                if settings_result == "quit":
                    running = False
                    game_state = "quit"
                elif settings_result == "menu":
                    game_state = "menu"

            elif game_state == "game":
                if event.type == SPAWN_EVENT:
                    x = random.randint(50, WIDTH - 50)
                    ingredients.append(Ingredient(x, -50))
                elif event.type == pygame.MOUSEWHEEL:
                    fall_speed = max(1.0, min(10.0, fall_speed + event.y))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        fall_speed = min(10.0, fall_speed + 1.0)
                    elif event.key == pygame.K_DOWN:
                        fall_speed = max(1.0, fall_speed - 1.0)
                    elif event.key == pygame.K_ESCAPE:
                        game_state = "menu"

        if game_state == "game":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                fall_speed = min(10.0, fall_speed + 0.1)

            cup.update()

            for ing in ingredients[:]:
                ing.update(fall_speed)
                if ing.rect.colliderect(cup.rect):
                    collected += 1
                    ingredients.remove(ing)
                elif ing.rect.top > HEIGHT:
                    ingredients.remove(ing)

            cup.draw(screen)
            for ing in ingredients:
                ing.draw(screen)

            font = pygame.font.Font(font_path, 24)
            speed_text = font.render(f"下落速度: {fall_speed:.2f}", True, (50, 50, 50))
            score_text = font.render(f"已收集: {collected}", True, (50, 50, 50))
            screen.blit(speed_text, (10, 10))
            screen.blit(score_text, (10, 50))

        if game_state != "quit":
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
