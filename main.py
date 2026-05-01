"""疯狂奶茶杯 - 第一周主程序"""

import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CHINESE_FONTS,
    IMAGES_DIR,
    ASSETS_DIR,
    INGREDIENT_COLORS,
)
from game.sprites import Cup, Ingredient, CatchEffect, Particle
from game.ingredient_manager import IngredientManager
from data.score_manager import ScoreManager
from bci.data_reader import BCIDataReader
from bci.filter import DeadZoneFilter, ExponentialSmoothing
from menu import MainMenu
from game_start_screen import GameStartScreen
import sys
import time
import os


def load_chinese_font(size=36):
    """加载支持中文的字体"""
    project_font = os.path.join(ASSETS_DIR, "fonts", "ZCOOLKuaiLe-Regular.ttf")
    if os.path.exists(project_font):
        try:
            return pygame.font.Font(project_font, size)
        except:
            pass

    try:
        return pygame.font.SysFont("simhei", size)
    except:
        pass

    return pygame.font.Font(pygame.font.get_default_font(), size)


def show_menu(screen):
    font = load_chinese_font(24)
    title_font = load_chinese_font(40)
    menu = MainMenu(screen, font, title_font)
    return menu.run()


def show_game_start(screen):
    font = load_chinese_font(24)
    title_font = load_chinese_font(36)
    start_screen = GameStartScreen(screen, font, title_font)
    return start_screen.run()


def run_game(screen, clock):
    font = load_chinese_font(36)
    hint_font = load_chinese_font(20)

    cup = Cup()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(cup)

    ingredients = pygame.sprite.Group()
    catch_effects = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    score_manager = ScoreManager()
    ingredient_manager = IngredientManager()

    bci_reader = BCIDataReader()
    bci_available = False

    dead_zone = DeadZoneFilter(threshold=5)
    smooth_yaw = ExponentialSmoothing(alpha=0.3)

    background = None
    has_background = False
    try:
        # 游戏开始界面背景图
        bg_path = os.path.join(IMAGES_DIR, "奶茶店2.png")
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path).convert()
            background = pygame.transform.scale(
                background, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            has_background = True
    except Exception:
        pass

    score_manager.set_required_ingredient("红茶")

    running = True
    use_yaw_control = False
    last_print_time = time.time()

    print("=" * 50)
    print("疯狂奶茶杯 - 游戏开始")
    print("=" * 50)
    print("控制说明:")
    print("  方向键左/右: 移动杯子")
    print("  Y: 切换到头动控制模式（模拟）")
    print("  K: 切换回键盘控制模式")
    print("  ESC: 返回主菜单")
    print("=" * 50)

    while running:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()
        dt_sec = dt / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    use_yaw_control = True
                    cup.yaw_control = True
                    print("切换到头动控制模式 (模拟)")
                elif event.key == pygame.K_k:
                    use_yaw_control = False
                    cup.yaw_control = False
                    print("切换到键盘控制模式")
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

        if bci_available:
            attention, raw_yaw = bci_reader.read_with_timeout()
        else:
            t = time.time()
            attention = 50 + int(30 * ((t % 10) / 10))
            raw_yaw = 20 * ((t % 8) / 4 - 1)

            if int(t) % 5 == 0 and time.time() - last_print_time >= 4.9:
                print(f"[模拟] 专注力: {attention}, Yaw: {raw_yaw:.1f}")
                last_print_time = time.time()

        filtered_yaw = dead_zone.filter(raw_yaw)
        smoothed_yaw = smooth_yaw.smooth(filtered_yaw)

        if use_yaw_control:
            cup.update(yaw=smoothed_yaw, dt=dt_sec)
        else:
            cup.update(keys=keys, dt=dt_sec)

        ingredient = ingredient_manager.update(required_types=["红茶"])
        if ingredient:
            ingredients.add(ingredient)

        ingredients.update()
        catch_effects.update(dt=dt_sec)
        particles.update(dt=dt_sec)

        hits = pygame.sprite.spritecollide(cup, ingredients, True)
        for hit in hits:
            effect = CatchEffect(hit, cup.rect)
            catch_effects.add(effect)
            for _ in range(8):
                color = INGREDIENT_COLORS.get(hit.type, (255, 200, 0))
                particles.add(Particle(hit.rect.centerx, hit.rect.centery, color))
            cup.trigger_bounce()
            score_manager.score += 10
            print(f"接住 {hit.type}！分数: {score_manager.score}")

        if has_background and background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((255, 255, 255))

        all_sprites.draw(screen)
        ingredients.draw(screen)
        catch_effects.draw(screen)
        particles.draw(screen)

        score_text = font.render(f"分数: {score_manager.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        mode_str = "头动控制" if use_yaw_control else "键盘控制"
        mode_text = font.render(f"模式: {mode_str}", True, (0, 100, 0))
        screen.blit(mode_text, (10, 50))

        bci_text = font.render(
            f"专注力: {attention}  头动: {smoothed_yaw:.1f}", True, (100, 0, 0)
        )
        screen.blit(bci_text, (10, 90))

        hint1 = hint_font.render(
            "方向键: 移动杯子 | Y: 头动模式 | K: 键盘模式 | ESC: 返回菜单",
            True,
            (50, 50, 50),
        )
        screen.blit(hint1, (10, SCREEN_HEIGHT - 40))

        pygame.display.flip()

    return "quit"


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("疯狂奶茶杯 - 第1周")
    clock = pygame.time.Clock()

    while True:
        result = show_menu(screen)

        if result == "quit":
            break
        elif result == "difficulty":
            print("难度设置 - 待实现")
        elif result == "settings":
            print("游戏设置 - 待实现")
        elif result == "start":
            result2 = show_game_start(screen)
            if result2 == "quit":
                break
            elif result2 == "start":
                game_result = run_game(screen, clock)
                if game_result == "quit":
                    break
                elif game_result == "menu":
                    continue

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
