"""
游戏开始确认界面模块
在主菜单之后显示，提示玩家准备开始游戏
"""

import pygame
import math
import os
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASSETS_DIR,
    IMAGES_DIR,
)


class MenuItem:
    """
    菜单按钮组件，支持鼠标悬停动画

    参数:
        text: 按钮显示文字
        x, y: 按钮中心坐标（像素）
        font: 文字字体对象
        bg_color: 按钮背景颜色 (R, G, B)
        hover_color: 鼠标悬停时的颜色 (R, G, B)
        text_color: 文字颜色 (R, G, B)
        padding: 文字内边距 (水平像素, 垂直像素)，默认 (40, 12)
        radius: 圆角半径（像素），默认 20
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
        """更新悬停缩放动画，dt 为帧间隔时间（秒）"""
        target = 1.0 if self.hovered else 0.0
        self.scale_t += (target - self.scale_t) * 0.15

    def draw(self, screen):
        """绘制按钮到屏幕，悬停时放大 6%"""
        s = 1.0 + 0.06 * self.scale_t
        w = int(self.rect.width * s)
        h = int(self.rect.height * s)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        color = self.hover_color if self.hovered else self.bg_color
        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=int(self.radius * s))

        tw = self._text_surf.get_width()
        th = self._text_surf.get_height()
        surf.blit(self._text_surf, ((w - tw) // 2, (h - th) // 2))

        screen.blit(surf, (self.rect.centerx - w // 2, self.rect.centery - h // 2))

    def handle_event(self, event):
        """处理鼠标事件，返回 True 表示按钮被点击"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class GameStartScreen:
    """
    游戏开始界面，展示游戏标题和说明，等待玩家按下回车键开始游戏

    参数:
        screen: pygame 屏幕对象
        font: 副标题/提示文字字体
        title_font: 标题字体
    """

    def __init__(self, screen, font, title_font):
        self.screen = screen
        self.font = font
        self.title_font = title_font
        self.clock = pygame.time.Clock()
        self.running = True
        self.result = None

        self.bg = self._load_bg()
        self.phase = 0.0  # 标题浮动动画相位

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.buttons = []

    def _load_bg(self):
        """加载背景图（奶茶店2.png），如果文件不存在则返回 None"""
        path = os.path.join(IMAGES_DIR, "奶茶店2.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return None

    def run(self):
        """
        主循环，等待玩家按下回车键开始游戏

        返回:
            "quit" - 退出游戏
            "back" - 返回主菜单（ESC 或 B 键）
            "start" - 开始游戏（回车键）
        """
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
                    elif event.key == pygame.K_RETURN:
                        self.running = False
                        self.result = "start"
                    elif event.key == pygame.K_b:
                        self.running = False
                        self.result = "back"
                else:
                    for btn in self.buttons:
                        if btn.handle_event(event):
                            self.running = False
                            self.result = "back"

            self._update(dt)
            self._draw(dt)
            pygame.display.flip()

        return self.result

    def _update(self, dt):
        """更新动画状态"""
        for btn in self.buttons:
            btn.update(dt)
        self.phase += dt * 1.5  # 1.5 为标题浮动速度系数

    def _draw(self, dt):
        """渲染画面"""
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((240, 220, 200))  # 浅褐色默认背景

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))  # 半透明黑色遮罩，alpha=80 控制暗度
        self.screen.blit(overlay, (0, 0))

        # 绘制浮动标题
        title_offset = math.sin(self.phase) * 5  # 5 为标题上下浮动幅度（像素）
        title_surf = self.title_font.render("选择你的奶茶配方", True, (255, 230, 180))
        title_shadow = self.title_font.render("选择你的奶茶配方", True, (80, 40, 10))
        tw = title_surf.get_width()
        tx = (SCREEN_WIDTH - tw) // 2
        ty = 100 + title_offset - 3  # 100 为标题初始 Y 坐标
        self.screen.blit(title_shadow, (tx + 3, ty + 3))  # 阴影偏移 3 像素
        self.screen.blit(title_surf, (tx, ty))

        # 绘制副标题
        sub_surf = self.font.render(
            "即将开始游戏，准备好制作你的专属奶茶了吗？", True, (220, 200, 170)
        )
        sw = sub_surf.get_width()
        self.screen.blit(
            sub_surf, ((SCREEN_WIDTH - sw) // 2, ty + 65)
        )  # 65 为副标题与标题间距

        # 绘制按钮
        for btn in self.buttons:
            btn.draw(self.screen)

        # 绘制底部提示
        hint = self.font.render("ESC 返回主菜单  |  回车 开始游戏", True, (0, 0, 0))
        self.screen.blit(
            hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40)
        )
