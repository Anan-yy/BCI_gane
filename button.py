import pygame
from colors import BUTTON_COLORS


class Button:
    """
    按钮类,包含位置、大小、文本、回调函数等属性，以及更新和绘制方法。
    """
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False
        self.bob_offset = 0

    def update(self, mouse_pos, mouse_pressed):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.pressed = mouse_pressed and self.hovered

        if self.hovered:
            self.bob_offset = 2
        else:
            self.bob_offset = 0

    def draw(self, surface, y_offset=0):
        draw_rect = self.rect.copy()
        draw_rect.y += int(self.bob_offset) + y_offset

        color = (
            BUTTON_COLORS["press"]
            if self.pressed
            else (BUTTON_COLORS["hover"] if self.hovered else BUTTON_COLORS["normal"])
        )

        pygame.draw.rect(surface, (0, 0, 0), draw_rect, border_radius=0)
        pygame.draw.rect(surface, color, draw_rect.inflate(-4, -4), border_radius=0)

        pygame.draw.rect(surface, (255, 255, 255), draw_rect.inflate(-8, -8), 2, border_radius=0)

        # 使用全局字体对象，避免硬编码路径导致的字体加载失败
        from game import button_font
        if button_font:
            text_surf = button_font.render(self.text, True, (0, 0, 0))
        else:
            # 如果全局字体不可用，使用默认字体
            text_surf = pygame.font.Font(None, 32).render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self):
        if self.hovered and self.callback:
            self.callback()