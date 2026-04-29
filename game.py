import pygame
import random
import math
import os
from pathlib import Path

from button import Button
from colors import *
from cup import Cup
from ingredient import Ingredient

pygame.init()

# 设置窗口大小
WIDTH, HEIGHT = 1000, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("疯狂奶茶杯")

# 获取脚本所在目录并构建图片资源的相对路径
script_dir = Path(__file__).parent
resource_path = script_dir / "游戏资源" / "imgs"
menu_bg_img = pygame.image.load(resource_path / "奶茶店1.png").convert()
menu_bg = pygame.transform.scale(menu_bg_img, (WIDTH, HEIGHT))

game_bg_img = pygame.image.load(resource_path / "奶茶店2.png").convert()
game_bg = pygame.transform.scale(game_bg_img, (WIDTH, HEIGHT))

# 加载图片资源
cup_img = pygame.image.load(resource_path / "奶茶杯.png").convert_alpha()
ingredient_img = pygame.image.load(
    resource_path / "小料.webp"
).convert_alpha()

# 调整奶茶杯大小
cup_width = 60
cup_height = 80
cup_img = pygame.transform.scale(cup_img, (cup_width, cup_height))
ingredient_img = pygame.transform.scale(ingredient_img, (50, 50))

# 设置字体路径和大小
try:
    font_path = os.path.join("C:", "Windows", "Fonts", "simhei.ttf")
    if os.path.exists(font_path):
        title_font = pygame.font.Font(font_path, 56)
        button_font = pygame.font.Font(font_path, 32)
    else:
        # 如果黑体字体不存在，则使用默认字体
        title_font = pygame.font.Font(None, 56)
        button_font = pygame.font.Font(None, 32)
except:
    # 如果无法加载字体，则使用默认字体
    title_font = pygame.font.Font(None, 56)
    button_font = pygame.font.Font(None, 32)


def show_menu():
    menu_running = True
    game_state = [None]

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
        Button(80, 190, 180, 50, "开始游戏", start_game_click),
        Button(80, 270, 180, 50, "关卡选择", level_select_click),
        Button(80, 350, 180, 50, "游戏设置", settings_click),
    ]

    clock = pygame.time.Clock()

    while menu_running:
        screen.blit(menu_bg, (0, 0))

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

    font = pygame.font.Font(button_font.path if hasattr(button_font, 'path') else None, 32) if button_font else pygame.font.Font(None, 32)
    title_surf = font.render("关卡选择", True, BROWN)

    back_button = Button(WIDTH // 2 - 60, 380, 120, 50, "返回", None)

    clock = pygame.time.Clock()

    while select_running:
        screen.blit(menu_bg, (0, 0))

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

    font = pygame.font.Font(button_font.path if hasattr(button_font, 'path') else None, 32) if button_font else pygame.font.Font(None, 32)
    title_surf = font.render("游戏设置", True, BROWN)

    back_button = Button(WIDTH // 2 - 60, 380, 120, 50, "返回", None)

    clock = pygame.time.Clock()

    while settings_running:
        screen.blit(menu_bg, (0, 0))

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
    global screen
    game_state = "menu"
    clock = pygame.time.Clock()
    running = True

    cup = Cup(WIDTH // 2, HEIGHT - 50)
    # 设置奶茶杯图片
    cup.image = cup_img

    ingredients = []
    fall_speed = 3.0

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 2000)

    collected = 0

    while running:
        screen.blit(game_bg, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "menu":
                menu_result = show_menu()
                if menu_result == "quit":
                    running = False
                    game_state = "quit"
                elif menu_result == "start_game":
                    game_state = "game"
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
                    new_ingredient = Ingredient(x, -50)
                    new_ingredient.image = ingredient_img
                    ingredients.append(new_ingredient)
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

            font = pygame.font.Font(button_font.path if hasattr(button_font, 'path') else None, 24) if button_font else pygame.font.Font(None, 24)
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
