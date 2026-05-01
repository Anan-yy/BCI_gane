"""疯狂奶茶杯 - 第一周主程序
游戏入口文件，负责初始化 pygame、管理界面跳转（主菜单 -> 模式选择 -> 游戏）
"""

import pygame
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CHINESE_FONTS,
    IMAGES_DIR,
    ASSETS_DIR,
    INGREDIENT_COLORS,
    GAME_MODES,
    DEFAULT_GAME_MODE,
)
from game.sprites import Cup, Ingredient, CatchEffect, Particle
from game.ingredient_manager import IngredientManager
from data.score_manager import ScoreManager
from data.recipes import evaluate_recipe
from bci.data_reader import BCIDataReader
from bci.filter import DeadZoneFilter, ExponentialSmoothing, AttentionMappingCurve
from menu import MainMenu
import sys
import time
import os


def load_chinese_font(size=36):
    """
    加载支持中文的字体

    参数:
        size: 字体大小（像素），默认 36。修改此值可改变全局默认字号

    返回:
        pygame.font.Font 对象
    """
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
    """显示主菜单界面，返回 (result, mode)"""
    font = load_chinese_font(24)
    title_font = load_chinese_font(40)
    menu = MainMenu(screen, font, title_font)
    return menu.run()


def run_game(screen, clock, game_mode="regular"):
    """
    运行主游戏循环

    参数:
        screen: pygame 屏幕对象
        clock: pygame 时钟对象
        game_mode: 游戏模式（"regular" / "challenge" / "creative"）

    返回:
        "quit" / "menu"
    """
    mode_config = GAME_MODES.get(game_mode, GAME_MODES[DEFAULT_GAME_MODE])
    mode_name = mode_config["name"]
    has_required = mode_config["has_required"]
    free_combine = mode_config["free_combine"]

    font = load_chinese_font(36)
    hint_font = load_chinese_font(20)
    recipe_font = load_chinese_font(28)

    # === 游戏对象初始化 ===
    cup = Cup()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(cup)

    ingredients = pygame.sprite.Group()
    catch_effects = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    score_manager = ScoreManager()
    ingredient_manager = IngredientManager()
    ingredient_manager.spawn_interval = mode_config["spawn_interval"] / 1000.0

    # === BCI 脑电设备初始化 ===
    bci_reader = BCIDataReader()
    bci_available = False

    # === 信号滤波器 ===
    dead_zone = DeadZoneFilter(threshold=5)
    smooth_yaw = ExponentialSmoothing(alpha=0.3)

    # === 创意模式专注力映射 ===
    attention_curve = None
    if free_combine:
        attention_curve = AttentionMappingCurve()

    # === 背景图加载 ===
    background = None
    has_background = False
    try:
        bg_path = os.path.join(IMAGES_DIR, "奶茶店2.png")
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path).convert()
            background = pygame.transform.scale(
                background, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            has_background = True
    except Exception:
        pass

    # === 创意模式状态 ===
    creative_ingredients = []  # 记录已接住的食材
    recipe_result = None  # 配方评估结果

    # 设置必接食材（仅常规/挑战模式）
    if has_required:
        score_manager.set_required_ingredient("红茶")

    # === 游戏状态变量 ===
    running = True
    use_yaw_control = False
    last_print_time = time.time()

    # 根据模式设置下落速度
    from config import INGREDIENT_SPEED

    original_ingredient_speed = INGREDIENT_SPEED

    print("=" * 50)
    print(f"疯狂奶茶杯 - {mode_name}")
    print("=" * 50)
    if free_combine:
        print("创意模式规则：")
        print("  没有必接食材，自由搭配")
        print("  不同组合产生不同评分（黑暗→米其林）")
        print("  专注力越高，评分加成越大")
    else:
        print("控制说明:")
        print("  方向键左/右: 移动杯子")
        print("  Y: 头动模式 | K: 键盘模式 | ESC: 返回菜单")
    print("=" * 50)

    # === 主游戏循环 ===
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
                elif event.key == pygame.K_k:
                    use_yaw_control = False
                    cup.yaw_control = False
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

        # === 获取控制信号 ===
        if bci_available:
            attention, raw_yaw = bci_reader.read_with_timeout()
        else:
            t = time.time()
            attention = 50 + int(30 * ((t % 10) / 10))
            raw_yaw = 20 * ((t % 8) / 4 - 1)

            if int(t) % 5 == 0 and time.time() - last_print_time >= 4.9:
                print(f"[模拟] 专注力: {attention}, Yaw: {raw_yaw:.1f}")
                last_print_time = time.time()

        # === 信号处理 ===
        filtered_yaw = dead_zone.filter(raw_yaw)
        smoothed_yaw = smooth_yaw.smooth(filtered_yaw)

        # === 更新杯子位置 ===
        if use_yaw_control:
            cup.update(yaw=smoothed_yaw, dt=dt_sec)
        else:
            cup.update(keys=keys, dt=dt_sec)

        # === 生成并更新食材 ===
        required = ["红茶"] if has_required else None
        ingredient = ingredient_manager.update(required_types=required)
        if ingredient:
            ingredients.add(ingredient)

        ingredients.update()
        catch_effects.update(dt=dt_sec)
        particles.update(dt=dt_sec)

        # === 碰撞检测 ===
        hits = pygame.sprite.spritecollide(cup, ingredients, True)
        for hit in hits:
            effect = CatchEffect(hit, cup.rect)
            catch_effects.add(effect)
            for _ in range(8):
                color = INGREDIENT_COLORS.get(hit.type, (255, 200, 0))
                particles.add(Particle(hit.rect.centerx, hit.rect.centery, color))
            cup.trigger_bounce()

            if free_combine:
                # 创意模式：记录食材，不检查必接
                creative_ingredients.append(hit.type)
                score_manager.score += 10
                # 评估当前配方
                recipe_result = evaluate_recipe(creative_ingredients)
            else:
                score_manager.score += 10

            print(f"接住 {hit.type}！分数: {score_manager.score}")

        # === 渲染画面 ===
        if has_background and background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((255, 255, 255))

        all_sprites.draw(screen)
        ingredients.draw(screen)
        catch_effects.draw(screen)
        particles.draw(screen)

        # === 绘制 HUD ===
        score_text = font.render(f"分数: {score_manager.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # 模式名称
        mode_text = font.render(f"{mode_name}", True, (100, 50, 150))
        screen.blit(mode_text, (10, 50))

        # BCI/专注力信息
        if free_combine and attention_curve:
            multiplier = attention_curve.map_attention(attention)
            tier = attention_curve.get_rating_tier(attention)
            bci_text = font.render(
                f"专注力: {attention} ({tier} x{multiplier:.2f})", True, (100, 0, 0)
            )
        else:
            bci_text = font.render(
                f"专注力: {attention}  头动: {smoothed_yaw:.1f}", True, (100, 0, 0)
            )
        screen.blit(bci_text, (10, 90))

        # 创意模式配方显示
        if free_combine and recipe_result:
            recipe_name = recipe_result["recipe_name"]
            rating = recipe_result["rating"]
            total_score = recipe_result["total_score"]

            # 配方名称
            name_surf = recipe_font.render(
                f"{rating['emoji']} {recipe_name}", True, rating["color"]
            )
            screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, 10))

            # 评分等级
            grade_surf = recipe_font.render(
                f"评分: {rating['name']} ({total_score})", True, rating["color"]
            )
            screen.blit(
                grade_surf, (SCREEN_WIDTH // 2 - grade_surf.get_width() // 2, 45)
            )

            # 已接食材列表
            if creative_ingredients:
                ing_text = hint_font.render(
                    f"食材: {' + '.join(creative_ingredients)}", True, (80, 80, 80)
                )
                screen.blit(
                    ing_text, (SCREEN_WIDTH // 2 - ing_text.get_width() // 2, 80)
                )

        # 底部提示
        if free_combine:
            hint_text = "自由搭配，创造你的专属奶茶 | ESC 返回"
        else:
            hint_text = "方向键: 移动 | Y: 头动 | K: 键盘 | ESC: 返回"

        hint1 = hint_font.render(hint_text, True, (50, 50, 50))
        screen.blit(hint1, (10, SCREEN_HEIGHT - 40))

        pygame.display.flip()

    return "quit"


def main():
    """游戏主入口，管理界面循环跳转"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("疯狂奶茶杯 - 第1周")
    clock = pygame.time.Clock()

    while True:
        # 1. 显示主菜单（含模式选择）
        result, mode = show_menu(screen)

        if result == "quit":
            break
        elif result == "settings":
            print("游戏设置 - 待实现")
        elif result == "start":
            # 2. 进入主游戏
            game_result = run_game(screen, clock, game_mode=mode)
            if game_result == "quit":
                break
            elif game_result == "menu":
                continue

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
