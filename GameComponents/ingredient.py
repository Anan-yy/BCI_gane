import pygame


class Ingredient:
    """
    小料类，包含位置、图像和更新逻辑。
    """
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.image = None  # 将在主文件中设置
        self.active = True

    def update(self, speed):
        if self.active:
            self.rect.y += speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)