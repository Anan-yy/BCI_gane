import pygame
import math


class Cup:
    """
    杯子类，包含位置、图像和更新逻辑。
    """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 120)
        self.image = None  # 将在主文件中设置
        self.bob_offset = 0

    def update(self):
        """
        更新杯子位置，使其跟随鼠标并产生上下浮动效果。
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.centerx = mouse_x
        self.rect.bottom = pygame.display.get_surface().get_size()[1] - 20  # 使用当前屏幕高度
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.003) * 2

    def draw(self, surface):
        """
        绘制杯子图像，上下浮动效果。
        """
        draw_rect = self.rect.copy()
        draw_rect.y += int(self.bob_offset)
        surface.blit(self.image, draw_rect)