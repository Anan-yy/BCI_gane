"""
主菜单模块 - 游戏启动后的第一个界面
包含：背景、浮动装饰粒子、标题、按钮、蒸汽粒子等
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
)


class MenuItem:
    """
    菜单按钮组件，支持鼠标悬停动画效果

    参数:
        text: 按钮显示文字
        x, y: 按钮中心坐标（像素）
        font: 文字字体对象
        bg_color: 按钮背景颜色 (R, G, B)
        hover_color: 鼠标悬停时的颜色 (R, G, B)
        text_color: 文字颜色 (R, G, B)
        padding: 文字内边距 (水平像素, 垂直像素)，默认 (40, 12)，值越大按钮越宽
        radius: 圆角半径（像素），默认 20，值越大圆角越圆
    """

    def __init__(
        self,
        text,
        x,
        y,
        font,
        bg_color,
        hover_color,
        text_color,
        padding=(40, 12),
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
        self.scale_t = 0.0  # 缩放动画进度（0.0~1.0）

    def update(self, dt=0.016):
        """
        更新悬停缩放动画

        参数:
            dt: 帧间隔时间（秒），默认 0.016（约 60fps）
        """
        target = 1.0 if self.hovered else 0.0
        self.scale_t += (target - self.scale_t) * 0.15  # 0.15 为动画平滑系数

    def draw(self, screen):
        """
        绘制按钮到屏幕

        参数:
            screen: pygame 屏幕对象
        """
        s = 1.0 + 0.06 * self.scale_t  # 悬停时最大放大 6%，0.06 为缩放幅度
        w = int(self.rect.width * s)
        h = int(self.rect.height * s)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        color = self.hover_color if self.hovered else self.bg_color
        self._draw_rounded_rect(surf, (0, 0, w, h), color, int(self.radius * s))

        tw = self._text_surf.get_width()
        th = self._text_surf.get_height()
        surf.blit(self._text_surf, ((w - tw) // 2, (h - th) // 2))

        screen.blit(surf, (self.rect.centerx - w // 2, self.rect.centery - h // 2))

    def handle_event(self, event):
        """
        处理鼠标事件

        参数:
            event: pygame 事件对象

        返回:
            True 表示按钮被点击，False 表示未点击
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    @staticmethod
    def _draw_rounded_rect(surface, rect, color, radius):
        """
        绘制圆角矩形

        参数:
            surface: pygame 绘图表面
            rect: 矩形区域 (x, y, w, h)
            color: 颜色 (R, G, B)
            radius: 圆角半径（像素）
        """
        pygame.draw.rect(surface, color, rect, border_radius=radius)


class SteamParticle:
    """
    蒸汽粒子效果（从杯口升起的白色半透明圆点）

    参数:
        x, y: 粒子初始位置（像素）
    """

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-0.3, 0.3)  # 水平速度（像素/帧）
        self.vy = random.uniform(-1.5, -0.5)  # 垂直速度（像素/帧），负值表示向上
        self.life = 1.0  # 生命值（1.0=满血，0=死亡）
        self.decay = random.uniform(0.01, 0.025)  # 生命衰减速度，值越大粒子消失越快
        self.size = random.randint(3, 7)  # 粒子半径（像素）

    def update(self):
        """更新粒子位置和生命，返回是否还存活"""
        self.x += self.vx + math.sin(self.life * 5) * 0.3  # 左右摇摆效果
        self.y += self.vy
        self.life -= self.decay
        return self.life > 0

    def draw(self, screen):
        """绘制半透明圆形粒子到屏幕"""
        alpha = int(self.life * 80)  # 透明度随生命衰减
        if alpha > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf, (255, 255, 255, alpha), (self.size, self.size), self.size
            )
            screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))


class FloatingItem:
    """
    背景浮动装饰元素（缓慢飘动的彩色圆点）

    参数:
        screen_w, screen_h: 屏幕宽高（像素），用于边界循环
        color: 装饰元素颜色 (R, G, B)，不提供则随机生成
    """

    def __init__(self, screen_w, screen_h, color=None):
        self.x = random.uniform(0, screen_w)
        self.y = random.uniform(0, screen_h)
        self.color = color or (
            random.randint(150, 255),
            random.randint(100, 200),
            random.randint(50, 150),
        )
        self.size = random.randint(12, 30)  # 装饰圆点半径（像素）
        self.speed_x = random.uniform(-0.5, 0.5)  # 水平飘动速度
        self.speed_y = random.uniform(-0.3, -0.05)  # 垂直飘动速度（向上）
        self.phase = random.uniform(0, 2 * math.pi)  # 正弦波初始相位，产生错落感
        self.screen_w = screen_w
        self.screen_h = screen_h

    def update(self):
        """更新装饰元素位置，超出边界后从底部/侧边重新出现"""
        self.x += self.speed_x + math.sin(self.phase) * 0.5
        self.y += self.speed_y
        self.phase += 0.02  # 相位递增，产生正弦波摆动
        if self.y < -self.size * 2:
            self.y = self.screen_h + self.size
            self.x = random.uniform(0, self.screen_w)
        if self.x < -self.size * 2:
            self.x = self.screen_w + self.size
        elif self.x > self.screen_w + self.size * 2:
            self.x = -self.size

    def draw(self, screen):
        """绘制半透明彩色圆点到屏幕"""
        alpha = 120  # 固定透明度
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf, (*self.color, alpha), (self.size, self.size), self.size // 2
        )
        screen.blit(surf, (int(self.x) - self.size, int(self.y) - self.size))


class MainMenu:
    """
    主菜单界面控制器

    参数:
        screen: pygame 屏幕对象
        font: 副标题/提示文字字体
        title_font: 标题/按钮文字字体
    """

    def __init__(self, screen, font, title_font):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.clock = pygame.time.Clock()
        self.running = True
        self.result = None

        self.bg = self._load_bg()
        self.floating_items = [
            FloatingItem(SCREEN_WIDTH, SCREEN_HEIGHT, c)
            for c in list(INGREDIENT_COLORS.values()) + [(255, 180, 100)] * 3
        ]

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        btn_w = 280  # 按钮宽度（像素），当前未直接使用（按钮大小由文字+padding决定）
        btn_h = 64  # 按钮高度（像素），当前未直接使用
        btn_spacing = 85  # 按钮垂直间距（像素），值越大按钮间距越大
        start_y = cy + 60  # 第一个按钮的 Y 坐标，值越大按钮组整体越靠下

        self.buttons = [
            MenuItem(
                "开始游戏",
                cx,
                start_y,
                title_font,
                (255, 140, 50),  # 按钮背景色（橙色）
                (255, 170, 80),  # 悬停色（亮橙色）
                (255, 255, 255),  # 文字颜色（白色）
            ),
            MenuItem(
                "难度设置",
                cx,
                start_y + btn_spacing,
                title_font,
                (120, 80, 200),  # 紫色
                (150, 110, 230),
                (255, 255, 255),
            ),
            MenuItem(
                "游戏设置",
                cx,
                start_y + btn_spacing * 2,
                title_font,
                (60, 140, 80),  # 绿色
                (90, 170, 110),
                (255, 255, 255),
            ),
        ]

        self.title_y = 100  # 标题初始 Y 坐标（像素），值越大标题越靠下
        self.title_phase = 0.0  # 标题浮动动画相位

    def _load_bg(self):
        """加载背景图，如果文件不存在则返回 None"""
        path = os.path.join(IMAGES_DIR, "奶茶店1.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return None

    def run(self):
        """主循环，返回用户选择结果"""
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
                        self.result = "difficulty"
                    elif event.key == pygame.K_3:
                        self.running = False
                        self.result = "settings"
                else:
                    for btn in self.buttons:
                        if btn.handle_event(event):
                            self.running = False
                            if btn.text == "开始游戏":
                                self.result = "start"
                            elif btn.text == "难度设置":
                                self.result = "difficulty"
                            elif btn.text == "游戏设置":
                                self.result = "settings"

            self._update(dt)
            self._draw(dt)
            pygame.display.flip()

        return self.result

    def _update(self, dt):
        """更新动画状态"""
        for btn in self.buttons:
            btn.update(dt)

        for item in self.floating_items:
            item.update()

        self.title_phase += dt * 2  # 2 为标题浮动速度系数

    def _draw(self, dt):
        """渲染画面"""
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((255, 240, 220))  # 浅米色默认背景

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # 半透明黑色遮罩，alpha=100 控制暗度
        self.screen.blit(overlay, (0, 0))

        for item in self.floating_items:
            item.draw(self.screen)

        # 绘制浮动标题
        title_offset = math.sin(self.title_phase) * 8  # 8 为标题上下浮动幅度（像素）
        title_surf = self.title_font.render("疯狂奶茶杯", True, (255, 220, 150))
        title_shadow = self.title_font.render("疯狂奶茶杯", True, (80, 40, 10))

        tw = title_surf.get_width()
        tx = (SCREEN_WIDTH - tw) // 2
        ty = self.title_y + title_offset - 3
        self.screen.blit(title_shadow, (tx + 3, ty + 3))
        self.screen.blit(title_surf, (tx, ty))

        # 绘制副标题
        sub_surf = self.font.render(
            "接住食材 · 制作属于你的美味奶茶", True, (220, 200, 170)
        )
        sw = sub_surf.get_width()
        self.screen.blit(
            sub_surf, ((SCREEN_WIDTH - sw) // 2, ty + 60)
        )  # 60 为副标题与标题间距

        # 绘制按钮
        for btn in self.buttons:
            btn.draw(self.screen)

        # 绘制提示
        hint = self.font.render("ESC 退出", True, (180, 180, 180))
        self.screen.blit(
            hint, (SCREEN_WIDTH - hint.get_width() - 20, SCREEN_HEIGHT - 35)
        )
