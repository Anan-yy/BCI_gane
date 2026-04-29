import pygame
import random
from colors import PINK, PEACH, CREAM


class Particle:
    """
    粒子类。
    包含位置、速度、颜色和生命周期，用于模拟小料掉落时的粒子效果。
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.size = random.randint(3, 8)
        self.color = random.choice([PINK, PEACH, CREAM])
        self.life = random.randint(30, 60)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.rect(
                surface, self.color, (self.x, self.y, self.size, self.size)
            )