import pygame
import random
from config import *


class Cup(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        # 尝试加载杯子图片，失败则用默认图形
        try:
            self.image = pygame.image.load(CUP_IMG).convert_alpha()
            self.image = pygame.transform.scale(self.image, (CUP_WIDTH, CUP_HEIGHT))
        except:
            # 使用默认图形
            self.image = pygame.Surface((CUP_WIDTH, CUP_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(self.image, CUP_COLOR, (0, 0, CUP_WIDTH, CUP_HEIGHT))
            pygame.draw.rect(
                self.image, WHITE, (5, 5, CUP_WIDTH - 10, CUP_HEIGHT - 10), 2
            )
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = CUP_SPEED
        self.yaw_control = False
        self.last_yaw = 0

    def update(self, keys=None, yaw=None):
        if self.yaw_control and yaw is not None:
            if abs(yaw) > DEAD_ZONE:
                self.rect.x += yaw * YAW_SCALE
        elif keys:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)


class Ingredient(pygame.sprite.Sprite):
    def __init__(self, ing_type, is_required=False, *groups):
        super().__init__(*groups)
        self.type = ing_type
        self.is_required = is_required
        # 尝试加载食材图片，失败则用默认图形
        try:
            img_path = INGREDIENT_IMGS.get(ing_type)
            if img_path:
                self.image = pygame.image.load(img_path).convert_alpha()
                self.image = pygame.transform.scale(
                    self.image, (INGREDIENT_SIZE, INGREDIENT_SIZE)
                )
            else:
                raise FileNotFoundError
        except:
            # 使用默认图形
            self.image = pygame.Surface(
                (INGREDIENT_SIZE, INGREDIENT_SIZE), pygame.SRCALPHA
            )
            color = INGREDIENT_COLORS.get(ing_type, RED)
            pygame.draw.circle(
                self.image,
                color,
                (INGREDIENT_SIZE // 2, INGREDIENT_SIZE // 2),
                INGREDIENT_SIZE // 2,
            )
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - INGREDIENT_SIZE)
        self.rect.y = -INGREDIENT_SIZE
        self.speed = INGREDIENT_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
