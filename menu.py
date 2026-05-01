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
from bci.config import load_bci_config, save_bci_config


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


class BCIModeButton(MenuItem):
    """脑机接口模式按钮 - 带有特殊脉冲动画和发光效果以突出显示"""

    def __init__(self, text, x, y, font, title_font):
        self.text = text
        self.font = font
        self.title_font = title_font
        self.bg_color = (0, 120, 180)
        self.hover_color = (0, 160, 220)
        self.text_color = (255, 255, 255)
        self.padding = (50, 18)
        self.radius = 25

        self._text_surf = title_font.render("脑机接口", True, (255, 255, 255))
        w = self._text_surf.get_width() + self.padding[0] * 2
        h = self._text_surf.get_height() + self.padding[1] * 2
        self.rect = pygame.Rect(x - w // 2, y - h // 2, w, h)

        self.hovered = False
        self.scale_t = 0.0
        self.click_t = 0.0
        self.click_particles = []
        self.pulse_t = 0.0
        self.glow_particles = []

    def update(self, dt=0.016):
        target = 1.0 if self.hovered else 0.0
        self.scale_t += (target - self.scale_t) * 0.15
        if self.click_t > 0:
            self.click_t -= dt * 3
        self.click_particles = [p for p in self.click_particles if p.update(dt)]

        self.pulse_t += dt * 3
        if self.hovered and random.random() < 0.3:
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(self.rect.width / 2, self.rect.width / 2 + 20)
            px = self.rect.centerx + math.cos(angle) * r
            py = self.rect.centery + math.sin(angle) * r
            self.glow_particles.append(ClickParticle(px, py, (0, 180, 255)))
        self.glow_particles = [p for p in self.glow_particles if p.update(dt)]

    def draw(self, screen):
        pulse = math.sin(self.pulse_t) * 0.5 + 0.5
        glow_alpha = int(60 + pulse * 80)

        glow_size = int(10 + pulse * 15)
        glow_surf = pygame.Surface(
            (self.rect.width + glow_size * 2, self.rect.height + glow_size * 2),
            pygame.SRCALPHA,
        )
        pygame.draw.rect(
            glow_surf,
            (0, 150, 200, glow_alpha),
            (0, 0, glow_surf.get_width(), glow_surf.get_height()),
            border_radius=self.radius + glow_size,
        )
        screen.blit(
            glow_surf,
            (
                self.rect.x - glow_size,
                self.rect.y - glow_size,
            ),
        )

        s = 1.0 + 0.08 * self.scale_t + pulse * 0.02
        w = int(self.rect.width * s)
        h = int(self.rect.height * s)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        color = self.hover_color if self.hovered else self.bg_color
        border_color = (100, 220, 255) if self.hovered else (0, 180, 255)
        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=int(self.radius * s))
        pygame.draw.rect(
            surf,
            border_color,
            (0, 0, w, h),
            3,
            border_radius=int(self.radius * s),
        )

        if self.click_t > 0:
            click_color = (*color, int(self.click_t * 150))
            pygame.draw.rect(
                surf, click_color, (0, 0, w, h), border_radius=int(self.radius * s)
            )

        tw = self._text_surf.get_width()
        th = self._text_surf.get_height()
        surf.blit(self._text_surf, ((w - tw) // 2, (h - th) // 2))

        screen.blit(surf, (self.rect.centerx - w // 2, self.rect.centery - h // 2))

        for p in self.glow_particles:
            p.draw(screen)
        for p in self.click_particles:
            p.draw(screen)

    def trigger_click(self):
        self.click_t = 1.0
        for _ in range(25):
            self.click_particles.append(
                ClickParticle(self.rect.centerx, self.rect.centery, (0, 180, 255))
            )
        for _ in range(12):
            self.click_particles.append(
                ClickParticle(self.rect.centerx, self.rect.centery, (255, 255, 255))
            )


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
            "bci": ((0, 120, 180), (0, 150, 220)),
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


class TextInputBox:
    """文本输入框 - 用于BCI设置页面的IP和端口输入"""

    def __init__(self, x, y, w, h, font, default_text="", label="", max_length=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.label = label
        self.text = default_text
        self.max_length = max_length
        self.active = False
        self.color_inactive = (100, 100, 100)
        self.color_active = (0, 150, 200)
        self.color = self.color_inactive
        self.blink_t = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = self.color_active if self.active else self.color_inactive
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length:
                char = event.unicode
                if char.isprintable():
                    self.text += char

    def update(self, dt):
        self.blink_t += dt * 4

    def draw(self, screen):
        label_surf = self.font.render(self.label, True, (200, 200, 200))
        screen.blit(label_surf, (self.rect.x, self.rect.y - 30))

        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=8)

        bg_color = (*self.color[:3], 30) if self.active else (40, 40, 50, 50)
        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, bg_color, (0, 0, *self.rect.size), border_radius=8)
        screen.blit(surf, self.rect.topleft)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.x + 10, self.rect.y + 5))

        if self.active and int(self.blink_t) % 2 == 0:
            cursor_x = self.rect.x + 10 + text_surf.get_width()
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (cursor_x, self.rect.y + 8),
                (cursor_x, self.rect.y + self.rect.h - 8),
                2,
            )

    def get_text(self):
        return self.text


class BCISettingsScreen:
    """BCI连接设置页面"""

    def __init__(self, screen, font, title_font):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.clock = pygame.time.Clock()
        self.running = True

        bci_config = load_bci_config()

        self.ip_input = TextInputBox(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 - 40,
            300,
            40,
            font,
            default_text=bci_config["server_ip"],
            label="服务器IP:",
        )
        self.port_input = TextInputBox(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT // 2 + 40,
            300,
            40,
            font,
            default_text=str(bci_config["server_port"]),
            label="端口号:",
        )

        self.test_btn = MenuItem(
            "测试连接",
            SCREEN_WIDTH // 2 - 120,
            SCREEN_HEIGHT // 2 + 130,
            font,
            (0, 120, 180),
            (0, 150, 220),
            (255, 255, 255),
            padding=(50, 15),
            radius=15,
        )
        self.back_btn = MenuItem(
            "返回",
            SCREEN_WIDTH // 2 - 60,
            SCREEN_HEIGHT // 2 + 210,
            font,
            (80, 80, 80),
            (100, 100, 100),
            (255, 255, 255),
            padding=(50, 15),
            radius=15,
        )

        self.status_text = ""
        self.status_color = (255, 255, 255)
        self.testing = False
        self.test_result = None

    def run(self):
        """运行设置页面，返回 (result, ip, port)"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._save_and_close()
                else:
                    self.ip_input.handle_event(event)
                    self.port_input.handle_event(event)
                    if self.test_btn.handle_event(event):
                        self._test_connection()
                    if self.back_btn.handle_event(event):
                        self._save_and_close()

            self._update(dt)
            self._draw()
            pygame.display.flip()

        return self.result

    def _save_and_close(self):
        """保存配置并关闭"""
        ip = self.ip_input.get_text()
        try:
            port = int(self.port_input.get_text())
            save_bci_config(ip, port)
            self.status_text = "配置已保存"
            self.status_color = (100, 255, 100)
        except ValueError:
            self.status_text = "端口号格式错误，未保存"
            self.status_color = (255, 100, 100)
            return

        pygame.display.flip()
        pygame.time.wait(500)
        self.running = False
        self.result = "back"

    def _test_connection(self):
        """测试BCI连接"""
        ip = self.ip_input.get_text()
        try:
            port = int(self.port_input.get_text())
        except ValueError:
            self.status_text = "端口号格式错误"
            self.status_color = (255, 100, 100)
            return

        self.status_text = "正在连接..."
        self.status_color = (255, 255, 100)
        pygame.display.flip()

        from bci.data_reader import BCIDataReader

        reader = BCIDataReader()
        connected = reader.connect(ip, port)
        reader.disconnect()

        if connected:
            self.status_text = "连接成功！"
            self.status_color = (100, 255, 100)
        else:
            self.status_text = "连接失败，请检查IP和端口"
            self.status_color = (255, 100, 100)

    def _update(self, dt):
        self.ip_input.update(dt)
        self.port_input.update(dt)
        self.test_btn.update(dt)
        self.back_btn.update(dt)

    def _draw(self):
        self.screen.fill((30, 30, 40))

        title = self.title_font.render("脑机接口设置", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

        desc = self.font.render("配置科创平台TCP服务器连接参数", True, (180, 180, 180))
        self.screen.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, 130))

        self.ip_input.draw(self.screen)
        self.port_input.draw(self.screen)

        self.test_btn.draw(self.screen)
        self.back_btn.draw(self.screen)

        if self.status_text:
            status = self.font.render(self.status_text, True, self.status_color)
            self.screen.blit(
                status,
                (SCREEN_WIDTH // 2 - status.get_width() // 2, SCREEN_HEIGHT // 2 + 180),
            )

        hint = self.font.render("ESC 返回主菜单", True, (100, 100, 100))
        self.screen.blit(
            hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50)
        )


class GameSettingsScreen:
    """游戏设置页面，包含BCI设置等子设置项"""

    def __init__(self, screen, font, title_font):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.clock = pygame.time.Clock()
        self.running = True
        self.result = None

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        self.bci_btn = BCIModeButton(
            "BCI设置",
            cx,
            cy - 40,
            font,
            title_font,
        )
        self.back_btn = MenuItem(
            "返回",
            cx,
            cy + 60,
            title_font,
            (80, 80, 80),
            (100, 100, 100),
            (255, 255, 255),
            padding=(50, 15),
            radius=15,
        )

    def run(self):
        """运行设置页面"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.result = "back"
                else:
                    if self.bci_btn.handle_event(event):
                        bci_settings = BCISettingsScreen(
                            self.screen, self.font, self.title_font
                        )
                        bci_settings.run()
                    if self.back_btn.handle_event(event):
                        self.running = False
                        self.result = "back"

            self._update(dt)
            self._draw()
            pygame.display.flip()

        return self.result

    def _update(self, dt):
        self.bci_btn.update(dt)
        self.back_btn.update(dt)

    def _draw(self):
        self.screen.fill((30, 30, 40))

        title = self.title_font.render("游戏设置", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        desc = self.font.render("请选择需要配置的项目", True, (180, 180, 180))
        self.screen.blit(desc, (SCREEN_WIDTH // 2 - desc.get_width() // 2, 160))

        self.bci_btn.draw(self.screen)
        self.back_btn.draw(self.screen)

        hint = self.font.render("ESC 返回主菜单", True, (100, 100, 100))
        self.screen.blit(
            hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50)
        )


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
        btn_spacing = 90
        start_y = cy + 20

        self.start_btn = MenuItem(
            "开始游戏",
            cx,
            start_y,
            title_font,
            (255, 140, 50),
            (255, 170, 80),
            (255, 255, 255),
        )

        self.mode_selector = ModeSelector(
            cx,
            start_y + btn_spacing,
            font,
            title_font,
            mode_keys=["regular", "challenge", "creative"],
        )

        self.bci_btn = BCIModeButton(
            "脑机接口",
            cx,
            start_y + btn_spacing * 2,
            font,
            title_font,
        )

        self.settings_btn = MenuItem(
            "游戏设置",
            cx,
            start_y + btn_spacing * 3,
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
                    if self.bci_btn.handle_event(event):
                        self.running = False
                        self.result = "start"
                        self.current_mode = "bci"
                    if self.settings_btn.handle_event(event):
                        settings_screen = GameSettingsScreen(
                            self.screen, self.font, self.title_font
                        )
                        settings_screen.run()

            self._update(dt)
            self._draw(dt)
            pygame.display.flip()

        return self.result, self.current_mode

    def _update(self, dt):
        self.start_btn.update(dt)
        self.mode_selector.update(dt)
        self.bci_btn.update(dt)
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
        self.bci_btn.draw(self.screen)
        self.settings_btn.draw(self.screen)

        hint = self.font.render("ESC 退出", True, (180, 180, 180))
        self.screen.blit(
            hint, (SCREEN_WIDTH - hint.get_width() - 20, SCREEN_HEIGHT - 35)
        )
