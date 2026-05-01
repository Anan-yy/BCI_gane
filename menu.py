"""
主菜单模块 - 游戏启动后的第一个界面
包含：背景、浮动装饰粒子、标题、按钮、模式选择器（带粒子效果）等
"""

import pygame
import math
import random
import os
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASSETS_DIR,
    IMAGES_DIR,
    INGREDIENT_TYPES,
    INGREDIENT_COLORS,
    GAME_MODES,
)


class MenuItem:
    """菜单按钮组件，支持鼠标悬停动画和点击粒子效果"""

    def __init__(
        self,
        text,
        x,
        y,
        font,
        bg_color,
        hover_color,
        text_color,
        padding=(60, 18),
        radius=20,
    ):
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.padding = padding
        self.radius = radius

        self._text_surf = font.render(text, True, text_color)
        w = self._text_surf.get_width() + padding[0] * 2
        h = self._text_surf.get_height() + padding[1] * 2
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)

        self.hovered = False
        self.scale_t = 0.0
        self.click_t = 0.0
        self.click_particles = []

    def update(self, dt=0.016):
        target = 1.0 if self.hovered else 0.0
        self.scale_t += (target - self.scale_t) * 0.15
        if self.click_t > 0:
            self.click_t -= dt * 3
        self.click_particles = [p for p in self.click_particles if p.update(dt)]

    def draw(self, screen):
        s = 1.0 + 0.06 * self.scale_t
        w = int(self.rect.width * s)
        h = int(self.rect.height * s)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        color = self.hover_color if self.hovered else self.bg_color
        self._draw_rounded_rect(surf, (0, 0, w, h), color, int(self.radius * s))

        if self.click_t > 0:
            click_color = (*color, int(self.click_t * 100))
            self._draw_rounded_rect(
                surf, (0, 0, w, h), click_color, int(self.radius * s)
            )

        tw = self._text_surf.get_width()
        th = self._text_surf.get_height()
        surf.blit(self._text_surf, ((w - tw) // 2, (h - th) // 2))

        screen.blit(surf, (self.rect.centerx - w // 2, self.rect.centery - h // 2))

        for p in self.click_particles:
            p.draw(screen)

    def trigger_click(self):
        """触发点击粒子效果"""
        self.click_t = 1.0
        for _ in range(15):
            self.click_particles.append(
                ClickParticle(self.rect.centerx, self.rect.centery, self.bg_color)
            )
        for _ in range(8):
            self.click_particles.append(
                ClickParticle(self.rect.centerx, self.rect.centery, (255, 255, 255))
            )

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.trigger_click()
                return True
        return False

    @staticmethod
    def _draw_rounded_rect(surface, rect, color, radius):
        pygame.draw.rect(surface, color, rect, border_radius=radius)


class ClickParticle:
    """点击特效粒子 - 从点击位置向外扩散的彩色粒子"""

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 10)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.decay = random.uniform(1.5, 3.0)
        self.size = random.randint(3, 8)

    def update(self, dt=0.016):
        self.life -= self.decay * dt
        if self.life <= 0:
            return False
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.96
        self.vy *= 0.96
        return True

    def draw(self, screen):
        alpha = int(self.life * 255)
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*self.color, alpha), (self.size, self.size), self.size
        )
        screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))


class ModePreviewDisplay:
    """
    模式预览显示框 - 鼠标靠近时在按钮右侧显示三个模式按键样式

    参数:
        x, y: 面板左上角坐标
        font: 描述文字字体
        title_font: 标题字体
        mode_key: 当前选中的模式 key
    """

    def __init__(self, x, y, font, title_font, mode_key="regular"):
        self.x = x
        self.y = y
        self.font = font
        self.title_font = title_font
        self.mode_key = mode_key
        self.alpha = 0
        self.target_alpha = 0
        self.width = 260
        self.height = 180

        self._mode_keys = ["regular", "challenge", "creative"]
        self._mode_colors = {
            "regular": ((60, 160, 100), (80, 200, 120)),
            "challenge": ((200, 80, 60), (240, 100, 80)),
            "creative": ((120, 80, 200), (150, 110, 240)),
        }

    def update(self, dt=0.016):
        self.alpha += (self.target_alpha - self.alpha) * 0.2

    def set_mode(self, mode_key):
        self.mode_key = mode_key
        self.target_alpha = 200

    def hide(self):
        self.target_alpha = 0

    def draw(self, screen):
        if self.alpha < 5:
            return

        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # 背景框
        pygame.draw.rect(
            surf,
            (30, 30, 40, int(self.alpha * 0.6)),
            (0, 0, self.width, self.height),
            border_radius=12,
        )
        pygame.draw.rect(
            surf,
            (255, 255, 255, int(self.alpha * 0.3)),
            (0, 0, self.width, self.height),
            2,
            border_radius=12,
        )

        btn_h = 45
        gap = 10
        start_y = 15

        for i, key in enumerate(self._mode_keys):
            bg, hover = self._mode_colors[key]
            is_active = key == self.mode_key

            # 按钮背景
            y = start_y + i * (btn_h + gap)
            color = hover if is_active else bg
            alpha_color = (*color, int(self.alpha))
            pygame.draw.rect(
                surf, alpha_color, (10, y, self.width - 20, btn_h), border_radius=8
            )

            if is_active:
                # 选中效果
                pygame.draw.rect(
                    surf,
                    (255, 255, 255, int(self.alpha * 0.8)),
                    (10, y, self.width - 20, btn_h),
                    2,
                    border_radius=8,
                )

            # 文字
            name = GAME_MODES[key]["name"]
            txt = self.font.render(name, True, (255, 255, 255))
            txt.set_alpha(int(self.alpha))
            surf.blit(
                txt,
                (
                    10 + (self.width - 20 - txt.get_width()) // 2,
                    y + (btn_h - txt.get_height()) // 2,
                ),
            )

        screen.blit(surf, (self.x, self.y))


class ModeSelector(MenuItem):
    """
    模式选择按钮 - 点击循环切换模式，悬停显示模式信息

    参数:
        x, y: 按钮中心坐标
        font: 描述文字字体
        title_font: 按钮标题字体
        mode_keys: 模式 key 列表
    """

    def __init__(self, x, y, font, title_font, mode_keys=None):
        self.mode_keys = mode_keys or list(GAME_MODES.keys())
        self.current_index = 0
        self.font = font
        self.title_font = title_font
        self.x = x
        self.y = y

        self._mode_colors = {
            "regular": ((60, 160, 100), (80, 200, 120)),
            "challenge": ((200, 80, 60), (240, 100, 80)),
            "creative": ((120, 80, 200), (150, 110, 240)),
        }

        self._mode_icons = {
            "regular": "🍵",
            "challenge": "🔥",
            "creative": "✨",
        }

        self.hovered = False
        self.scale_t = 0.0
        self.click_t = 0.0
        self.ripple = 0.0

        bg_color, _ = self._mode_colors[self.mode_keys[0]]
        padding = (50, 14)
        self.padding = padding
        self.radius = 20

        mode_name = GAME_MODES[self.mode_keys[0]]["name"]
        self._text_surf = title_font.render(f"模式选择", True, (255, 255, 255))
        w = self._text_surf.get_width() + padding[0] * 2
        h = self._text_surf.get_height() + padding[1] * 2
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)

        self.click_particles = []
        self.info_display = ModePreviewDisplay(
            self.rect.right + 20,
            self.rect.top - 10,
            font,
            title_font,
            self.mode_keys[0],
        )

    def _update_text(self):
        mode_key = self.mode_keys[self.current_index]
        mode_name = GAME_MODES[mode_key]["name"]
        self._text_surf = self.title_font.render("模式选择", True, (255, 255, 255))
        w = self._text_surf.get_width() + self.padding[0] * 2
        h = self._text_surf.get_height() + self.padding[1] * 2
        old_center = self.rect.center
        self.rect = pygame.Rect(old_center[0] - w // 2, old_center[1] - h // 2, w, h)
        self.info_display = ModePreviewDisplay(
            self.rect.right + 20,
            self.rect.top - 10,
            self.font,
            self.title_font,
            mode_key,
        )

    def cycle_mode(self):
        self.current_index = (self.current_index + 1) % len(self.mode_keys)
        self.click_t = 1.0
        self.ripple = 1.0
        self._update_text()
        mode_key = self.mode_keys[self.current_index]
        bg, _ = self._mode_colors.get(mode_key, ((100, 100, 100), (120, 120, 120)))

        for _ in range(20):
            self.click_particles.append(
                ClickParticle(self.rect.centerx, self.rect.centery, bg)
            )
        for _ in range(10):
            self.click_particles.append(
                ClickParticle(self.rect.centerx, self.rect.centery, (255, 255, 255))
            )

        return mode_key

    def update(self, dt=0.016):
        target = 1.0 if self.hovered else 0.0
        self.scale_t += (target - self.scale_t) * 0.15
        if self.click_t > 0:
            self.click_t -= dt * 3
        if self.ripple > 0:
            self.ripple -= dt * 2

        self.click_particles = [p for p in self.click_particles if p.update(dt)]
        self.info_display.update(dt)

    def draw(self, screen):
        s = 1.0 + 0.06 * self.scale_t
        w = int(self.rect.width * s)
        h = int(self.rect.height * s)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        mode_key = self.mode_keys[self.current_index]
        bg_color, hover_color = self._mode_colors.get(
            mode_key, ((100, 100, 100), (120, 120, 120))
        )
        color = hover_color if self.hovered else bg_color

        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=int(self.radius * s))

        if self.click_t > 0:
            click_color = (*color, int(self.click_t * 100))
            pygame.draw.rect(
                surf, click_color, (0, 0, w, h), border_radius=int(self.radius * s)
            )

        if self.ripple > 0:
            ripple_r = int((1 - self.ripple) * max(w, h) * 0.3)
            ripple_surf = pygame.Surface((ripple_r * 2, ripple_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                ripple_surf,
                (255, 255, 255, int(self.ripple * 80)),
                (ripple_r, ripple_r),
                ripple_r,
            )
            screen.blit(
                ripple_surf,
                (self.rect.centerx - ripple_r, self.rect.centery - ripple_r),
            )

        tw = self._text_surf.get_width()
        th = self._text_surf.get_height()
        surf.blit(self._text_surf, ((w - tw) // 2, (h - th) // 2))

        screen.blit(surf, (self.rect.centerx - w // 2, self.rect.centery - h // 2))

        for p in self.click_particles:
            p.draw(screen)

        if self.hovered:
            self.info_display.set_mode(mode_key)
            self.info_display.draw(screen)

    def handle_event(self, event):
        """处理鼠标事件，返回模式 key 或 None"""
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            if self.hovered:
                self.info_display.set_mode(self.mode_keys[self.current_index])
            elif was_hovered:
                self.info_display.hide()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.cycle_mode()
        return None


class SteamParticle:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-1.5, -0.5)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.025)
        self.size = random.randint(3, 7)

    def update(self):
        self.x += self.vx + math.sin(self.life * 5) * 0.3
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, screen):
        alpha = int(self.life * 80)
        if alpha > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf, (255, 255, 255, alpha), (self.size, self.size), self.size
            )
            screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))


class FloatingItem:
    def __init__(self, screen_w, screen_h, color=None):
        self.x = random.uniform(0, screen_w)
        self.y = random.uniform(0, screen_h)
        self.color = color or (
            random.randint(150, 255),
            random.randint(100, 200),
            random.randint(50, 150),
        )
        self.size = random.randint(12, 30)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.3, -0.05)
        self.phase = random.uniform(0, 2 * math.pi)
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self):
        self.x += self.speed_x + math.sin(self.phase) * 0.5
        self.y += self.speed_y
        self.phase += 0.02
        if self.y < -self.size * 2:
            self.y = self.screen_h + self.size
            self.x = random.uniform(0, self.screen_w)
        if self.x < -self.size * 2:
            self.x = self.screen_w + self.size
        elif self.x > self.screen_w + self.size * 2:
            self.x = -self.size

    def draw(self, screen):
        alpha = 120
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*self.color, alpha), (self.size, self.size), self.size // 2
        )
        screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))


class MainMenu:
    def __init__(self, screen, font, title_font):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.clock = pygame.time.Clock()
        self.running = True
        self.result = None
        self.current_mode = "regular"

        self.bg = self._load_bg()
        self.floating_items = [
            FloatingItem(SCREEN_WIDTH, SCREEN_HEIGHT, c)
            for c in list(INGREDIENT_COLORS.values()) + [(255, 180, 100)] * 3
        ]

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        btn_spacing = 110
        start_y = cy + 40

        self.start_btn = MenuItem(
            "开始游戏",
            cx,
            start_y,
            title_font,
            (255, 140, 50),
            (255, 170, 80),
            (255, 255, 255),
        )

        self.mode_selector = ModeSelector(cx, start_y + btn_spacing, font, title_font)

        self.settings_btn = MenuItem(
            "游戏设置",
            cx,
            start_y + btn_spacing * 2,
            title_font,
            (60, 140, 80),
            (90, 170, 110),
            (255, 255, 255),
        )

        self.title_y = 100
        self.title_phase = 0.0

    def _load_bg(self):
        path = os.path.join(IMAGES_DIR, "奶茶店1.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return None

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.result = "quit"
                    elif event.key == pygame.K_RETURN:
                        self.running = False
                        self.result = "start"
                    elif event.key == pygame.K_1:
                        self.running = False
                        self.result = "start"
                    elif event.key == pygame.K_2:
                        self.running = False
                        self.result = "mode"
                    elif event.key == pygame.K_3:
                        self.running = False
                        self.result = "settings"
                else:
                    if self.start_btn.handle_event(event):
                        self.running = False
                        self.result = "start"
                    mode = self.mode_selector.handle_event(event)
                    if mode:
                        self.current_mode = mode
                    if self.settings_btn.handle_event(event):
                        self.running = False
                        self.result = "settings"

            self._update(dt)
            self._draw(dt)
            pygame.display.flip()

        return self.result, self.current_mode

    def _update(self, dt):
        self.start_btn.update(dt)
        self.mode_selector.update(dt)
        self.settings_btn.update(dt)

        for item in self.floating_items:
            item.update()

        self.title_phase += dt * 2

    def _draw(self, dt):
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((255, 240, 220))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))

        for item in self.floating_items:
            item.draw(self.screen)

        title_offset = math.sin(self.title_phase) * 8
        title_surf = self.title_font.render("疯狂奶茶杯", True, (255, 220, 150))
        title_shadow = self.title_font.render("疯狂奶茶杯", True, (80, 40, 10))

        tw = title_surf.get_width()
        tx = (SCREEN_WIDTH - tw) // 2
        ty = self.title_y + title_offset - 3
        self.screen.blit(title_shadow, (tx + 3, ty + 3))
        self.screen.blit(title_surf, (tx, ty))

        sub_surf = self.font.render(
            "接住食材 · 制作属于你的美味奶茶", True, (220, 200, 170)
        )
        sw = sub_surf.get_width()
        self.screen.blit(sub_surf, ((SCREEN_WIDTH - sw) // 2, ty + 60))

        self.start_btn.draw(self.screen)
        self.mode_selector.draw(self.screen)
        self.settings_btn.draw(self.screen)

        hint = self.font.render("ESC 退出", True, (180, 180, 180))
        self.screen.blit(
            hint, (SCREEN_WIDTH - hint.get_width() - 20, SCREEN_HEIGHT - 35)
        )
