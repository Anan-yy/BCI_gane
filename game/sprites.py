import pygame
import math
import random
from config import *


class Cup(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
        self._moving = False
        try:
            self._orig_image = pygame.image.load(CUP_IMG).convert_alpha()
            self._orig_image = pygame.transform.scale(
                self._orig_image, (CUP_WIDTH, CUP_HEIGHT)
            )
        except:
            self._orig_image = pygame.Surface((CUP_WIDTH, CUP_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(self._orig_image, CUP_COLOR, (0, 0, CUP_WIDTH, CUP_HEIGHT))
            pygame.draw.rect(
                self._orig_image, WHITE, (5, 5, CUP_WIDTH - 10, CUP_HEIGHT - 10), 2
            )
        self.image = self._orig_image
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = CUP_SPEED
        self.yaw_control = False
        self.last_yaw = 0

        # 动画状态
        self._tilt = 0.0  # 当前倾斜角度
        self._bounce_t = -1.0  # 弹跳进度 (0~1)，-1 表示无弹跳
        self._bounce_dur = 0.2  # 弹跳持续时间（秒）

    def trigger_bounce(self):
        """触发接住食材时的弹跳动画"""
        self._bounce_t = 0.0

    def update(self, keys=None, yaw=None, dt=1.0):
        move_dir = 0  # -1 左, 0 停, 1 右

        if self.yaw_control and yaw is not None:
            if abs(yaw) > DEAD_ZONE:
                self.rect.x += yaw * YAW_SCALE
                move_dir = -1 if yaw < 0 else 1
        elif keys:
            if keys[pygame.K_LEFT]:
                self.rect.x -= self.speed
                move_dir = -1
            if keys[pygame.K_RIGHT]:
                self.rect.x += self.speed
                move_dir = 1

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(SCREEN_WIDTH, self.rect.right)

        # 更新倾斜：目标角度 ±5°，平滑过渡
        target_tilt = move_dir * 5.0
        self._tilt += (target_tilt - self._tilt) * 0.2

        # 更新弹跳
        if self._bounce_t >= 0:
            self._bounce_t += dt / self._bounce_dur
            if self._bounce_t >= 1.0:
                self._bounce_t = -1.0

        # 应用变换
        scale = 1.0
        if self._bounce_t >= 0:
            bounce_phase = math.sin(self._bounce_t * math.pi)
            scale = 1.0 + 0.1 * bounce_phase

        rotated = pygame.transform.rotozoom(self._orig_image, -self._tilt, scale)
        new_rect = rotated.get_rect(center=(self.rect.centerx, self.rect.centery))
        new_rect.bottom = self.rect.bottom

        self.image = rotated
        self.rect = new_rect


class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, *groups):
        super().__init__(*groups)
        self.color = color
        size = random.randint(3, 8)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 2
        self.life = 1.0
        self.decay = random.uniform(2.0, 3.5)

    def update(self, dt=0.016):
        self.life -= self.decay * dt
        if self.life <= 0:
            self.kill()
            return
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += 0.15
        self.image.set_alpha(int(self.life * 255))


class CatchEffect(pygame.sprite.Sprite):
    def __init__(self, ingredient, cup_rect, *groups):
        super().__init__(*groups)
        self.image = ingredient.image.copy()
        self.rect = self.image.get_rect(center=ingredient.rect.center)
        self._target = (cup_rect.centerx, cup_rect.centery - cup_rect.height // 4)
        self._start_x = self.rect.centerx
        self._start_y = self.rect.centery
        self._start_image = self.image.copy()
        self._t = 0.0
        self._duration = 0.3
        self._done = False
        self.type = ingredient.type

    def update(self, dt=0.016):
        self._t += dt / self._duration
        if self._t >= 1.0:
            self._done = True
            self.kill()
            return

        ease = self._t * self._t
        self.rect.centerx = int(
            self._start_x + (self._target[0] - self._start_x) * ease
        )
        self.rect.centery = int(
            self._start_y + (self._target[1] - self._start_y) * ease
        )

        shrink = 1.0 - ease * 0.8
        w = int(self._start_image.get_width() * shrink)
        h = int(self._start_image.get_height() * shrink)
        if w > 0 and h > 0:
            self.image = pygame.transform.scale(self._start_image, (w, h))
            self.rect.size = (w, h)


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
