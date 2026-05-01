"""疯狂奶茶杯 - 第一周主程序
游戏入口文件，负责初始化 pygame、管理界面跳转（主菜单 -> 模式选择 -> 游戏）
"""

import pygame
import math
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CHINESE_FONTS,
    IMAGES_DIR,
    ASSETS_DIR,
    INGREDIENT_COLORS,
    GAME_MODES,
    DEFAULT_GAME_MODE,
    FOCUS_TEAPOT_IMG,
    BACKGROUND_IMG,
    GAME_DURATION,
)
from game.sprites import Cup, Ingredient, CatchEffect, Particle, MissEffect
from game.ingredient_manager import IngredientManager
from data.score_manager import ScoreManager
from data.recipes import evaluate_recipe
from bci.data_reader import BCIDataReader
from bci.filter import DeadZoneFilter, ExponentialSmoothing, AttentionMappingCurve
from menu import MainMenu, GameSettingsScreen
from menu.screens.bci_settings import BCISettingsScreen
from menu.splash import SplashScreen
from menu.transition import StartTransition
from menu.summary import SummaryScreen
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


class FocusTeapotUI:
    """专注力茶壶 UI - 液面高度代表专注力数值（0-100）"""

    def __init__(self, image_path=None, x=10, y=90, width=100, height=120):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.focus_value = 0
        self._liquid_color = (144, 238, 144)
        self._teapot_img = None

        if image_path and os.path.exists(image_path):
            try:
                self._teapot_img = pygame.image.load(image_path).convert_alpha()
                self._teapot_img = pygame.transform.scale(
                    self._teapot_img, (self.width, self.height)
                )
            except:
                pass

    def update(self, value):
        """更新专注力数值并计算当前液体颜色"""
        self.focus_value = max(0, min(100, value))
        t = self.focus_value / 100.0
        r = int(144 + (255 - 144) * t)
        g = int(238 + (215 - 238) * t)
        b = int(144 + (0 - 144) * t)
        self._liquid_color = (r, g, b)

    def draw(self, screen):
        """绘制茶壶 UI"""
        if self._teapot_img:
            screen.blit(self._teapot_img, (self.x, self.y))
        else:
            self._draw_fallback(screen)

    def _draw_fallback(self, screen):
        """无图片时的备用绘制方案"""
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2
        body_r = self.width * 0.38

        # 1. 壶把手 (右侧)
        handle_rect = pygame.Rect(
            cx + body_r - 5, cy - body_r * 0.6, self.width * 0.35, body_r * 1.2
        )
        pygame.draw.rect(screen, (139, 69, 19), handle_rect, 6, border_radius=10)

        # 2. 壶嘴 (左侧)
        spout_pts = [
            (cx - body_r + 5, cy - body_r * 0.2),
            (cx - body_r - self.width * 0.35, cy - body_r * 0.8),
            (cx - body_r - self.width * 0.25, cy - body_r * 0.6),
            (cx - body_r + 5, cy + body_r * 0.4),
        ]
        pygame.draw.polygon(screen, (139, 69, 19), spout_pts, 6)

        # 3. 壶身轮廓 & 液体裁剪区域
        body_rect = pygame.Rect(cx - body_r, cy - body_r, body_r * 2, body_r * 2)

        # 4. 液体 (裁剪在壶身内)
        liquid_h = body_rect.height * (self.focus_value / 100.0)
        if liquid_h > 0:
            liquid_rect = pygame.Rect(
                body_rect.x,
                body_rect.y + body_rect.height - liquid_h,
                body_rect.width,
                liquid_h,
            )
            # 绘制液体背景
            clip_surf = pygame.Surface(
                (body_rect.width, body_rect.height), pygame.SRCALPHA
            )
            pygame.draw.ellipse(
                clip_surf, (255, 255, 255), (0, 0, body_rect.width, body_rect.height)
            )
            pygame.draw.rect(
                clip_surf,
                self._liquid_color,
                (0, body_rect.height - liquid_h, body_rect.width, liquid_h),
            )

            # 液面高光
            if liquid_h > 4:
                pygame.draw.line(
                    clip_surf,
                    (255, 255, 255),
                    (4, body_rect.height - liquid_h + 2),
                    (body_rect.width - 4, body_rect.height - liquid_h + 2),
                    2,
                )

            screen.blit(clip_surf, (body_rect.x, body_rect.y))

        # 5. 壶身边框 & 背景 (半透明壶身效果)
        glass_surf = pygame.Surface(
            (body_rect.width, body_rect.height), pygame.SRCALPHA
        )
        pygame.draw.ellipse(
            glass_surf, (200, 200, 200, 80), (0, 0, body_rect.width, body_rect.height)
        )
        screen.blit(glass_surf, (body_rect.x, body_rect.y))
        pygame.draw.ellipse(screen, (139, 69, 19), body_rect, 6)

        # 6. 壶盖 (顶部)
        lid_rect = pygame.Rect(cx - body_r * 0.8, cy - body_r - 10, body_r * 1.6, 14)
        pygame.draw.rect(screen, (139, 69, 19), lid_rect, 6, border_radius=8)
        knob_rect = pygame.Rect(cx - 8, cy - body_r - 18, 16, 10)
        pygame.draw.ellipse(screen, (160, 82, 45), knob_rect)

        # 7. 数值文字
        font = pygame.font.Font(None, 28)
        val_surf = font.render(f"{int(self.focus_value)}", True, (255, 255, 255))
        screen.blit(
            val_surf,
            (
                body_rect.x + (body_rect.width - val_surf.get_width()) // 2,
                body_rect.y + body_rect.height // 2 - val_surf.get_height() // 2,
            ),
        )


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
    bci_mode = mode_config["bci_mode"]

    font = load_chinese_font(36)
    hint_font = load_chinese_font(20)
    recipe_font = load_chinese_font(28)

    # === 游戏对象初始化 ===
    cup = Cup()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(cup)

    ingredients = pygame.sprite.Group()
    catch_effects = pygame.sprite.Group()
    miss_effects = pygame.sprite.Group()
    particles = pygame.sprite.Group()

    score_manager = ScoreManager()
    ingredient_manager = IngredientManager()
    ingredient_manager.spawn_interval = mode_config["spawn_interval"] / 1000.0

    # === BCI 脑电设备初始化 ===
    bci_reader = BCIDataReader()
    bci_available = False
    if bci_mode:
        bci_available = bci_reader.connect()

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
        if os.path.exists(BACKGROUND_IMG):
            background = pygame.image.load(BACKGROUND_IMG).convert()
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
    show_summary = False  # 标记是否显示结算界面
    use_yaw_control = False
    last_print_time = time.time()
    game_start_time = pygame.time.get_ticks()
    focus_samples = []  # 记录专注力数据用于结算

    # 专注力茶壶 UI (仅在图片存在时启用)
    teapot_img_path = FOCUS_TEAPOT_IMG if os.path.exists(FOCUS_TEAPOT_IMG) else None
    focus_teapot = None
    if teapot_img_path:
        focus_teapot = FocusTeapotUI(
            image_path=teapot_img_path, x=10, y=90, width=120, height=140
        )

    # 根据模式设置下落速度
    from config import INGREDIENT_SPEED

    original_ingredient_speed = INGREDIENT_SPEED

    print("=" * 50)
    print(f"疯狂奶茶杯 - {mode_name}")
    print("=" * 50)
    if bci_mode:
        print("脑机接口模式规则：")
        print("  使用BCI设备读取专注力和头动数据")
        print("  自由搭配食材，不同组合产生不同评分")
        print("  专注力越高，评分加成越大")
        if not bci_available:
            print("  [警告] BCI设备未连接，无法读取数据")
    elif free_combine:
        print("创意模式规则：")
        print("  没有必接食材，自由搭配")
        print("  不同组合产生不同评分（黑暗→米其林）")
        print("  专注力越高，评分加成越大")
    else:
        print("控制说明:")
        print("  方向键左/右: 移动杯子")
        print("  Y: 头动模式 | K: 键盘模式 | ESC: 返回菜单")
    print("=" * 50)

    # === 立即绘制第一帧，确保过场动画结束后屏幕不闪烁 ===
    if has_background and background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((255, 255, 255))

    all_sprites.draw(screen)
    score_text = font.render(f"分数: {score_manager.score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    mode_text = font.render(f"{mode_name}", True, (100, 50, 150))
    screen.blit(mode_text, (10, 50))
    pygame.display.flip()

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
                    show_summary = True
                    running = False
                    break

        # === 获取控制信号 ===
        if bci_available:
            result = bci_reader.read_with_timeout()
            if result != (None, None):
                attention, raw_yaw = result
            else:
                # BCI设备连接但无数据时，使用默认值
                attention = 50
                raw_yaw = 0
        else:
            # 非BCI模式或不使用BCI时，使用键盘控制，不显示专注力/头动
            attention = None
            raw_yaw = 0

        # === 信号处理 ===
        filtered_yaw = dead_zone.filter(raw_yaw)
        smoothed_yaw = smooth_yaw.smooth(filtered_yaw)

        # === 更新杯子位置 ===
        if use_yaw_control:
            cup.update(yaw=smoothed_yaw, dt=dt_sec)
        else:
            cup.update(keys=keys, dt=dt_sec)

        # === 计时与专注力记录 ===
        elapsed_ms = pygame.time.get_ticks() - game_start_time
        if elapsed_ms >= GAME_DURATION * 1000:
            show_summary = True
            running = False  # 时间到，触发结算
            break

        if attention is not None:
            focus_samples.append(attention)

        # === 生成并更新食材 ===
        required = ["红茶"] if has_required else None
        ingredient = ingredient_manager.update(required_types=required)
        if ingredient:
            ingredients.add(ingredient)

        ingredients.update()
        catch_effects.update(dt=dt_sec)
        miss_effects.update(dt=dt_sec)
        particles.update(dt=dt_sec)

        # === 碰撞检测 ===
        hits = pygame.sprite.spritecollide(cup, ingredients, False)
        # 判定线：杯子高度的 4/5 处（不可见）
        threshold_y = cup.rect.top + cup.rect.height * 0.8

        # 1. 处理与杯子发生碰撞的小料
        for hit in hits:
            if hit.rect.bottom > threshold_y:
                # 碰到杯子但位置太低 -> 视为没接住，触发失败动画
                hit.rect.bottom = int(threshold_y)  # 修正位置到判定线
                miss_effects.add(MissEffect(hit))

                # 添加少量收敛粒子
                color = INGREDIENT_COLORS.get(hit.type, (200, 200, 200))
                for _ in range(4):
                    p = Particle(hit.rect.centerx, int(threshold_y), color)
                    p.vx *= 0.4
                    p.vy *= 0.4
                    p.decay *= 1.5
                    particles.add(p)

                ingredients.remove(hit)
            else:
                # 正常接住
                ingredients.remove(hit)
                effect = CatchEffect(hit, cup.rect)
                catch_effects.add(effect)
                for _ in range(8):
                    color = INGREDIENT_COLORS.get(hit.type, (255, 200, 0))
                    particles.add(Particle(hit.rect.centerx, hit.rect.centery, color))
                cup.trigger_bounce()

                if free_combine:
                    creative_ingredients.append(hit.type)
                    score_manager.score += 10
                    recipe_result = evaluate_recipe(creative_ingredients)
                else:
                    score_manager.score += 10

                cup.update_level(score_manager.score)
                print(f"接住 {hit.type}！分数: {score_manager.score}")

        # 2. 处理未碰撞但掉落过深的小料（漏接）
        for ing in ingredients.sprites():
            if ing.rect.bottom > threshold_y:
                ing.rect.bottom = int(threshold_y)  # 修正位置到判定线
                miss_effects.add(MissEffect(ing))

                # 粒子效果
                color = INGREDIENT_COLORS.get(ing.type, (200, 200, 200))
                for _ in range(4):
                    p = Particle(ing.rect.centerx, int(threshold_y), color)
                    p.vx *= 0.4
                    p.vy *= 0.4
                    p.decay *= 1.5
                    particles.add(p)

                ingredients.remove(ing)

        # === 渲染画面 ===
        if has_background and background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((255, 255, 255))

        all_sprites.draw(screen)
        ingredients.draw(screen)
        catch_effects.draw(screen)
        miss_effects.draw(screen)
        particles.draw(screen)

        # === 绘制 HUD ===
        score_text = font.render(f"分数: {score_manager.score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        # 模式名称
        mode_text = font.render(f"{mode_name}", True, (100, 50, 150))
        screen.blit(mode_text, (10, 50))

        # 专注力茶壶 UI 更新与绘制
        if focus_teapot:
            if attention is not None:
                focus_teapot.update(attention)
            else:
                focus_teapot.update(0)
            focus_teapot.draw(screen)

        # BCI/专注力信息 (文字辅助显示)
        if bci_mode and attention is not None:
            if free_combine and attention_curve:
                multiplier = attention_curve.map_attention(attention)
                tier = attention_curve.get_rating_tier(attention)
                bci_text = hint_font.render(
                    f"{tier} x{multiplier:.2f}",
                    True,
                    (255, 255, 255),
                )
            else:
                bci_text = hint_font.render(
                    f"头动: {smoothed_yaw:.1f}",
                    True,
                    (255, 255, 255),
                )
            screen.blit(bci_text, (10, 235))
        elif bci_mode and attention is None:
            bci_text = hint_font.render("BCI设备未连接", True, (200, 0, 0))
            screen.blit(bci_text, (10, 235))

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
        if bci_mode:
            hint_text = "脑机接口模式 | ESC 返回"
        elif free_combine:
            hint_text = "自由搭配，创造你的专属奶茶 | ESC 返回"
        else:
            hint_text = "方向键: 移动 | Y: 头动 | K: 键盘 | ESC: 返回"

        hint1 = hint_font.render(hint_text, True, (50, 50, 50))
        screen.blit(hint1, (10, SCREEN_HEIGHT - 40))

        pygame.display.flip()

    # === 游戏结束结算逻辑 ===
    if show_summary:
        # 计算平均专注力
        avg_focus = sum(focus_samples) / len(focus_samples) if focus_samples else 0.0
        # 键盘模式/非BCI模式强制专注力为 0
        if not bci_mode:
            avg_focus = 0.0

        summary = SummaryScreen(screen, score_manager.score, avg_focus, game_mode)
        return summary.run()

    return "quit"


def main():
    """游戏主入口，管理界面循环跳转"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("疯狂奶茶杯 - 第1周")
    icon_path = os.path.join(IMAGES_DIR, "other", "游戏图标.png")
    if os.path.exists(icon_path):
        pygame.display.set_icon(pygame.image.load(icon_path))

    # 播放启动动画
    splash_font = load_chinese_font(110)
    SplashScreen(screen, splash_font).run()

    clock = pygame.time.Clock()

    while True:
        # 1. 显示主菜单（含模式选择）
        result, mode = show_menu(screen)

        if result == "quit":
            break
        elif result == "settings":
            settings_screen = GameSettingsScreen(
                screen, load_chinese_font(24), load_chinese_font(40)
            )
            settings_screen.run()
            continue
        elif result == "start":
            # 2. 播放开始过场动画
            StartTransition(screen).run()
            # 3. 进入主游戏
            game_result = run_game(screen, clock, game_mode=mode)
            if game_result == "quit":
                break
            elif game_result == "menu":
                continue

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
