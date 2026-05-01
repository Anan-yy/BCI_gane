"""疯狂奶茶杯 - 第一周主程序"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, CHINESE_FONTS, IMAGES_DIR, ASSETS_DIR
from game.sprites import Cup, Ingredient
from game.ingredient_manager import IngredientManager
from data.score_manager import ScoreManager
from bci.data_reader import BCIDataReader
from bci.filter import DeadZoneFilter, ExponentialSmoothing
import sys
import time
import os


def load_chinese_font(size=36):
    """加载支持中文的字体"""
    # 先尝试项目内的字体
    project_font = os.path.join(ASSETS_DIR, "fonts", "simhei.ttf")
    if os.path.exists(project_font):
        try:
            return pygame.font.Font(project_font, size)
        except:
            pass

    # 尝试系统字体
    try:
        return pygame.font.SysFont("simhei", size)
    except:
        pass

    # 最后使用pygame默认字体
    return pygame.font.Font(pygame.font.get_default_font(), size)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("疯狂奶茶杯 - 第1周")
    clock = pygame.time.Clock()

    # 初始化杯子
    cup = Cup()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(cup)

    # 食材组
    ingredients = pygame.sprite.Group()

    # 分数管理器
    score_manager = ScoreManager()

    # 食材管理器
    ingredient_manager = IngredientManager()

    # BCI数据读取器（模拟模式，无需真实设备）
    bci_reader = BCIDataReader()
    bci_available = False  # 设置为False使用纯模拟数据
    print("BCI设备: 模拟模式 (无真实设备)")

    # 滤波器
    dead_zone = DeadZoneFilter(threshold=5)
    smooth_yaw = ExponentialSmoothing(alpha=0.3)

    # 加载中文字体
    font = load_chinese_font(36)
    hint_font = load_chinese_font(20)
    print("使用中文字体显示")

    # 尝试加载背景图片
    background = None
    has_background = False
    try:
        bg_path = os.path.join(IMAGES_DIR, "奶茶店1.png")
        if os.path.exists(bg_path):
            background = pygame.image.load(bg_path).convert()
            background = pygame.transform.scale(
                background, (SCREEN_WIDTH, SCREEN_HEIGHT)
            )
            has_background = True
            print("已加载背景图片")
        else:
            print("未找到背景图片，使用纯色背景")
    except Exception as e:
        print(f"加载背景图片失败: {e}，使用纯色背景")

    # 设置必接食材（第一周只测试红茶）
    score_manager.set_required_ingredient("红茶")

    running = True
    use_yaw_control = False  # 按Y键切换到头动控制
    last_print_time = time.time()

    print("=" * 50)
    print("疯狂奶茶杯 - 第一周演示")
    print("=" * 50)
    print("控制说明:")
    print("  方向键左/右: 移动杯子")
    print("  Y: 切换到头动控制模式（模拟）")
    print("  K: 切换回键盘控制模式")
    print("  接住红茶 +10 分")
    print("=" * 50)

    while running:
        dt = clock.tick(60)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                    running = False

        # 读取BCI数据（模拟，无需真实设备）
        if bci_available:
            attention, raw_yaw = bci_reader.read_with_timeout()
        else:
            # 纯模拟：根据时间生成变化的数据，减少终端输出
            t = time.time()
            attention = 50 + int(30 * ((t % 10) / 10))  # 50-80循环
            raw_yaw = 20 * ((t % 8) / 4 - 1)  # -20到20循环

            # 每5秒打印一次数据，减少输出
            if int(t) % 5 == 0 and time.time() - last_print_time >= 4.9:
                print(f"[模拟] 专注力: {attention}, Yaw: {raw_yaw:.1f}")
                last_print_time = time.time()

        # 对Yaw进行滤波
        filtered_yaw = dead_zone.filter(raw_yaw)
        smoothed_yaw = smooth_yaw.smooth(filtered_yaw)

        # 更新杯子位置
        if use_yaw_control:
            cup.update(yaw=smoothed_yaw, dt=dt / 1000.0)
        else:
            cup.update(keys=keys, dt=dt / 1000.0)

        # 生成食材
        ingredient = ingredient_manager.update(required_types=["红茶"])
        if ingredient:
            ingredients.add(ingredient)

        # 更新食材位置
        ingredients.update()

        # 碰撞检测
        hits = pygame.sprite.spritecollide(cup, ingredients, False)
        for hit in hits:
            hit.kill()
            cup.trigger_bounce()
            score_manager.score += 10
            print(f"接住 {hit.type}！分数: {score_manager.score}")

        # 绘制
        if has_background and background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((255, 255, 255))

        all_sprites.draw(screen)
        ingredients.draw(screen)

        # 显示分数 - 中文显示
        score_text = font.render(f"分数: {score_manager.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # 显示控制模式
        mode_str = "头动控制" if use_yaw_control else "键盘控制"
        mode_text = font.render(f"模式: {mode_str}", True, (0, 100, 0))
        screen.blit(mode_text, (10, 50))

        # 显示BCI数据（模拟模式提示）
        bci_text = font.render(
            f"专注力: {attention}  头动: {smoothed_yaw:.1f}", True, (100, 0, 0)
        )
        screen.blit(bci_text, (10, 90))

        # 显示操作提示
        hint1 = hint_font.render(
            "方向键: 移动杯子 | Y: 头动模式 | K: 键盘模式", True, (50, 50, 50)
        )
        screen.blit(hint1, (10, SCREEN_HEIGHT - 60))
        hint2 = hint_font.render("接住红茶 +10分 | 无需BCI设备", True, (50, 50, 50))
        screen.blit(hint2, (10, SCREEN_HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
