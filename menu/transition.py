"""点击开始游戏后的过场动画"""

import pygame
import math
import random
import os
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    IMAGES_DIR,
    INGREDIENT_COLORS,
    INGREDIENT_TYPES,
    INGREDIENT_IMGS,
    BACKGROUND_IMG,
)


class FallingIngredient:
    """下落的食材粒子"""

    def __init__(self, target_x, target_y, size=80):
        self.target_x = target_x
        self.target_y = target_y
        self.size = size
        self.x = random.uniform(50, SCREEN_WIDTH - 50)
        self.y = -50
        self.speed = random.uniform(4, 8)

        # 随机选择食材
        self.type = random.choice(INGREDIENT_TYPES)
        self.color = INGREDIENT_COLORS.get(self.type, (255, 200, 0))

        # 加载图片
        path = INGREDIENT_IMGS.get(self.type)
        self.image = None
        if path and os.path.exists(path):
            try:
                self.image = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (size, size))
            except:
                pass

        self.angle = 0
        self.rot_speed = random.uniform(-5, 5)
        self.caught = False

    def update(self):
        if not self.caught:
            self.y += self.speed
            self.angle += self.rot_speed

            # 判定落入杯中 (检查高度和水平位置)
            if (
                self.y > self.target_y - (self.size // 2)
                and abs(self.x - self.target_x) < self.size
            ):
                self.caught = True
                return True
        return False

    def draw(self, screen):
        if self.caught:
            return

        if self.image:
            rotated = pygame.transform.rotate(self.image, self.angle)
            rect = rotated.get_rect(center=(self.x, self.y))
            screen.blit(rotated, rect)
        else:
            pygame.draw.circle(
                screen, self.color, (int(self.x), int(self.y)), self.size // 2
            )


class SplashEffect:
    """接住食材的溅射效果"""

    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(10):
            angle = random.uniform(-math.pi, 0)
            speed = random.uniform(3, 8)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 1.0,
                }
            )
        self.color = color

    def update(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.15
            p["life"] -= 0.05
        self.particles = [p for p in self.particles if p["life"] > 0]
        return len(self.particles) > 0

    def draw(self, screen):
        for p in self.particles:
            s = pygame.Surface((10, 10), pygame.SRCALPHA)
            alpha = int(p["life"] * 255)
            s.fill((*self.color, alpha))
            screen.blit(s, (p["x"] - 5, p["y"] - 5))


class MissEffect:
    """食材掉落/未接住的失败特效"""

    def __init__(self, x, y, color):
        self.particles = []
        # 粒子向下及四周扩散
        for _ in range(12):
            angle = random.uniform(-0.2, math.pi + 0.2)  # 主要是下半圆
            speed = random.uniform(2, 5)
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 1.0,
                    "size": random.randint(3, 6),
                }
            )
        self.color = color

    def update(self):
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.1  # 重力
            p["life"] -= 0.04
        self.particles = [p for p in self.particles if p["life"] > 0]
        return len(self.particles) > 0

    def draw(self, screen):
        for p in self.particles:
            s = pygame.Surface((p["size"], p["size"]), pygame.SRCALPHA)
            alpha = int(p["life"] * 255)
            s.fill((*self.color, alpha))
            screen.blit(s, (p["x"] - p["size"] // 2, p["y"] - p["size"] // 2))


class StartTransition:
    """游戏开始过渡动画"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.ingredients = []
        self.splash_effects = []
        self.cup_img = None
        self.orig_cup_img = None

        # 初始位置：上移 (SCREEN_HEIGHT - 150)，确保完全显示
        self.cup_x = SCREEN_WIDTH // 2
        self.cup_y = SCREEN_HEIGHT - 150

        # 加载杯子图片
        cup_path = os.path.join(IMAGES_DIR, "cups", "cup1.png")
        if os.path.exists(cup_path):
            try:
                loaded_img = pygame.image.load(cup_path).convert_alpha()
                self.orig_cup_img = loaded_img
                self.cup_img = pygame.transform.scale(loaded_img, (160, 200))
            except:
                pass

        # 生成食材
        self.spawn_timer = 0
        # 每150ms生成一个食材，最多18个
        self.spawn_interval = 150
        # 当前已生成食材数
        self.ingredient_count = 0
        # 最大生成食材数
        self.max_ingredients = 25

        # 加载游戏背景
        self.game_background = None
        if os.path.exists(BACKGROUND_IMG):
            try:
                self.game_background = pygame.image.load(BACKGROUND_IMG).convert()
                self.game_background = pygame.transform.scale(
                    self.game_background, (SCREEN_WIDTH, SCREEN_HEIGHT)
                )
            except:
                pass

        # 动画状态控制
        self.phase = "falling"  # falling -> returning -> done
        self.return_start_time = 0
        self.miss_effects = []  # 失败特效列表

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

            # 获取鼠标位置用于移动
            keys = pygame.key.get_pressed()
            mouse_x, _ = pygame.mouse.get_pos()
            target_x = mouse_x
            if keys[pygame.K_LEFT]:
                target_x = self.cup_x - 20
            elif keys[pygame.K_RIGHT]:
                target_x = self.cup_x + 20

            # === 状态机 ===
            if self.phase == "falling":
                self._update_falling(dt, target_x)
            elif self.phase == "returning":
                done = self._update_returning()
                if done:
                    # 回归结束，绘制最终帧并返回
                    self._draw_final_frame()
                    pygame.display.flip()
                    return

            pygame.display.flip()

    def _update_falling(self, dt, target_x):
        """掉落阶段"""
        # 桃色背景
        self.screen.fill((255, 228, 181))

        # 杯子跟随鼠标
        self.cup_x += (target_x - self.cup_x) * 0.2
        for ing in self.ingredients:
            ing.target_x = self.cup_x

        # 生成食材
        self.spawn_timer += dt * 1000
        if (
            self.spawn_timer > self.spawn_interval
            and self.ingredient_count < self.max_ingredients
        ):
            self.ingredients.append(FallingIngredient(self.cup_x, self.cup_y, size=80))
            self.spawn_timer = 0
            self.ingredient_count += 1

        # 更新食材和溅射效果
        # 判定线：杯子高度的 4/5 处
        cup_h = self.cup_img.get_height() if self.cup_img else 200
        threshold_y = self.cup_y + cup_h * 0.3  # 中心 + 0.3高度 = 顶部 + 0.8高度

        # 判定宽度：杯子宽度
        cup_w = self.cup_img.get_width() if self.cup_img else 160

        caught_list = []
        for ing in self.ingredients:
            if ing.update():
                caught_list.append(ing)
                self.splash_effects.append(SplashEffect(ing.x, self.cup_y, ing.color))
            elif ing.y > threshold_y and abs(ing.x - self.cup_x) < cup_w / 2:
                # 没接住：触发失败特效
                self.miss_effects.append(MissEffect(ing.x, threshold_y, ing.color))
                caught_list.append(ing)
            elif ing.y > SCREEN_HEIGHT + 50:
                caught_list.append(ing)

        for ing in caught_list:
            if ing in self.ingredients:
                self.ingredients.remove(ing)

        active_effects = [e for e in self.splash_effects if e.update()]
        self.splash_effects = active_effects

        # 更新失败特效
        self.miss_effects = [e for e in self.miss_effects if e.update()]

        # 绘制
        for ing in self.ingredients:
            ing.draw(self.screen)
        for effect in self.splash_effects:
            effect.draw(self.screen)
        for effect in self.miss_effects:
            effect.draw(self.screen)

        if self.cup_img:
            rect = self.cup_img.get_rect(center=(self.cup_x, self.cup_y))
            self.screen.blit(self.cup_img, rect)

        # 判断是否结束掉落阶段
        if (
            self.ingredient_count >= self.max_ingredients
            and not self.ingredients
            and not self.splash_effects
            and not self.miss_effects
        ):
            self.phase = "returning"
            self.return_start_time = pygame.time.get_ticks()

    def _update_returning(self):
        """回归阶段：杯子缩小并移动到游戏初始位置，背景渐变到游戏场景"""
        elapsed_return = pygame.time.get_ticks() - self.return_start_time
        duration = 1500  # 回归动画持续1.5秒
        t = min(elapsed_return / duration, 1.0)
        ease = 1 - (1 - t) * (1 - t)

        # 目标位置：与游戏初始位置完全一致
        # 游戏中杯子: rect.centerx = SCREEN_WIDTH // 2, rect.bottom = SCREEN_HEIGHT - 10
        # 杯子高度100，所以中心y = SCREEN_HEIGHT - 10 - 50 = SCREEN_HEIGHT - 60
        game_cup_x = SCREEN_WIDTH // 2
        game_cup_y = SCREEN_HEIGHT - 60

        curr_x = self.cup_x + (game_cup_x - self.cup_x) * ease
        curr_y = self.cup_y + (game_cup_y - self.cup_y) * ease

        # 缩小比例：从2.0缩到1.0
        current_scale = 2.0 - (1.0 * ease)
        w = int(160 * (current_scale / 2.0))
        h = int(200 * (current_scale / 2.0))

        # 绘制桃色背景
        self.screen.fill((255, 228, 181))

        # 渐变显现游戏背景
        if self.game_background:
            bg_alpha = int(ease * 255)
            bg_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            bg_overlay.blit(self.game_background, (0, 0))
            bg_overlay.fill((255, 228, 181, 255 - bg_alpha))
            self.screen.blit(bg_overlay, (0, 0))

        # 绘制杯子
        if self.orig_cup_img:
            img = pygame.transform.scale(self.orig_cup_img, (w, h))
            rect = img.get_rect(center=(curr_x, curr_y))
            self.screen.blit(img, rect)

        if t >= 1.0:
            self.cup_x = game_cup_x
            self.cup_y = game_cup_y
            return True
        return False

    def _draw_final_frame(self):
        """绘制最终帧：完整游戏背景+杯子"""
        if self.game_background:
            self.screen.blit(self.game_background, (0, 0))
        else:
            self.screen.fill((255, 255, 255))

        if self.orig_cup_img:
            final_img = pygame.transform.scale(self.orig_cup_img, (80, 100))
            rect = final_img.get_rect(center=(self.cup_x, self.cup_y))
            self.screen.blit(final_img, rect)
