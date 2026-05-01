"""疯狂奶茶杯 - 第一周主程序
游戏入口文件，负责初始化 pygame、管理界面跳转（主菜单 -> 开始界面 -> 游戏）
"""

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
    """
    显示主菜单界面

    参数:
        screen: pygame 屏幕对象

    返回:
        用户选择结果："quit" / "start" / "difficulty" / "settings"
    """
    font = load_chinese_font(24)  # 副标题字号，修改此值可改变副标题/提示文字大小
    title_font = load_chinese_font(40)  # 按钮文字字号，修改此值可改变菜单按钮文字大小
    menu = MainMenu(screen, font, title_font)
    return menu.run()


def show_game_start(screen):
    """
    显示游戏开始界面（等待玩家确认开始）

    参数:
        screen: pygame 屏幕对象

    返回:
        "quit" / "back" / "start"
    """
    font = load_chinese_font(24)  # 副标题字号
    title_font = load_chinese_font(48)  # 标题字号，修改此值可改变开始界面标题大小
    start_screen = GameStartScreen(screen, font, title_font)
    return start_screen.run()


def run_game(screen, clock):
    """
    运行主游戏循环

    参数:
        screen: pygame 屏幕对象
        clock: pygame 时钟对象，用于控制帧率

    返回:
        "quit" / "menu"
    """
    font = load_chinese_font(36)  # 游戏中 HUD 文字字号（分数、模式、BCI 信息）
    hint_font = load_chinese_font(20)  # 底部提示文字字号

    # === 游戏对象初始化 ===
    cup = Cup()  # 玩家控制的杯子
    all_sprites = pygame.sprite.Group()  # 所有精灵组
    all_sprites.add(cup)

    ingredients = pygame.sprite.Group()  # 食材精灵组
    catch_effects = pygame.sprite.Group()  # 接住食材特效组
    particles = pygame.sprite.Group()  # 粒子特效组

    score_manager = ScoreManager()  # 分数/金钱管理器
    ingredient_manager = IngredientManager()  # 食材生成管理器

    # === BCI 脑电设备初始化 ===
    bci_reader = BCIDataReader()  # 脑电数据读取器（当前为模拟数据）
    bci_available = False  # 脑电设备是否可用

    # === 信号滤波器 ===
    dead_zone = DeadZoneFilter(
        threshold=5
    )  # 死区滤波器，threshold=5 表示忽略幅度 <5 的微小信号（防手抖）
    smooth_yaw = ExponentialSmoothing(
        alpha=0.3
    )  # 指数平滑滤波器，alpha=0.3 控制平滑程度（越大响应越快，越小越平滑）

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

    # 设置当前必接食材
    score_manager.set_required_ingredient("红茶")

    # === 游戏状态变量 ===
    running = True
    use_yaw_control = False  # 是否使用头动控制（False = 键盘控制）
    last_print_time = time.time()  # 用于控制终端输出频率

    print("=" * 50)
    print("疯狂奶茶杯 - 游戏开始")
    print("=" * 50)
    print("控制说明:")
    print("  方向键左/右: 移动杯子")
    print("  Y: 切换到头动控制模式（模拟）")
    print("  K: 切换回键盘控制模式")
    print("  ESC: 返回主菜单")
    print("=" * 50)

    # === 主游戏循环 ===
    while running:
        dt = clock.tick(60)  # 限制帧率为 60fps，返回上一帧到当前的毫秒数
        keys = pygame.key.get_pressed()  # 获取当前按下的所有键
        dt_sec = dt / 1000.0  # 将毫秒转换为秒，用于动画计算

        # === 事件处理 ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:  # Y 键：切换头动控制
                    use_yaw_control = True
                    cup.yaw_control = True
                    print("切换到头动控制模式 (模拟)")
                elif event.key == pygame.K_k:  # K 键：切换键盘控制
                    use_yaw_control = False
                    cup.yaw_control = False
                    print("切换到键盘控制模式")
                elif event.key == pygame.K_ESCAPE:  # ESC 键：返回主菜单
                    return "menu"

        # === 获取控制信号 ===
        if bci_available:
            # 真实 BCI 设备模式
            attention, raw_yaw = bci_reader.read_with_timeout()
        else:
            # 模拟数据模式（无设备时使用）
            t = time.time()
            attention = 50 + int(30 * ((t % 10) / 10))  # 模拟专注力 50~80 波动
            raw_yaw = 20 * ((t % 8) / 4 - 1)  # 模拟偏航角 -20~20 波动

            if int(t) % 5 == 0 and time.time() - last_print_time >= 4.9:
                print(f"[模拟] 专注力: {attention}, Yaw: {raw_yaw:.1f}")
                last_print_time = time.time()

        # === 信号处理 ===
        filtered_yaw = dead_zone.filter(raw_yaw)  # 死区滤波：去除微小抖动
        smoothed_yaw = smooth_yaw.smooth(filtered_yaw)  # 指数平滑：使运动更流畅

        # === 更新杯子位置 ===
        if use_yaw_control:
            cup.update(yaw=smoothed_yaw, dt=dt_sec)  # 头动控制模式
        else:
            cup.update(keys=keys, dt=dt_sec)  # 键盘控制模式

        # === 生成并更新食材 ===
        ingredient = ingredient_manager.update(required_types=["红茶"])
        if ingredient:
            ingredients.add(ingredient)

        ingredients.update()
        catch_effects.update(dt=dt_sec)
        particles.update(dt=dt_sec)

        # === 碰撞检测 ===
        hits = pygame.sprite.spritecollide(cup, ingredients, True)
        for hit in hits:
            effect = CatchEffect(hit, cup.rect)  # 创建接住特效
            catch_effects.add(effect)
            for _ in range(8):  # 生成 8 个粒子
                color = INGREDIENT_COLORS.get(hit.type, (255, 200, 0))
                particles.add(Particle(hit.rect.centerx, hit.rect.centery, color))
            cup.trigger_bounce()  # 触发杯子弹跳动画
            score_manager.score += 10
            print(f"接住 {hit.type}！分数: {score_manager.score}")

        # === 渲染画面 ===
        if has_background and background:
            screen.blit(background, (0, 0))  # 绘制背景图
        else:
            screen.fill((255, 255, 255))  # 白色背景（无图片时）

        all_sprites.draw(screen)  # 绘制杯子
        ingredients.draw(screen)  # 绘制食材
        catch_effects.draw(screen)  # 绘制接住特效
        particles.draw(screen)  # 绘制粒子特效

        # 绘制 HUD 信息
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
    """游戏主入口，管理界面循环跳转"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("疯狂奶茶杯 - 第1周")
    clock = pygame.time.Clock()

    while True:
        # 1. 显示主菜单
        result = show_menu(screen)

        if result == "quit":
            break
        elif result == "difficulty":
            print("难度设置 - 待实现")
        elif result == "settings":
            print("游戏设置 - 待实现")
        elif result == "start":
            # 2. 显示开始确认界面
            result2 = show_game_start(screen)
            if result2 == "quit":
                break
            elif result2 == "start":
                # 3. 进入主游戏
                game_result = run_game(screen, clock)
                if game_result == "quit":
                    break
                elif game_result == "menu":
                    continue

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
