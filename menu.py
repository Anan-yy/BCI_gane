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
        self.scale_t = 0.0

    def update(self, dt=0.016):
        target = 1.0 if self.hovered else 0.0
        self.scale_t += (target - self.scale_t) * 0.15

    def draw(self, screen):
        s = 1.0 + 0.06 * self.scale_t
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
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    @staticmethod
    def _draw_rounded_rect(surface, rect, color, radius):
        pygame.draw.rect(surface, color, rect, border_radius=radius)


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

        self.bg = self._load_bg()
        self.steam_particles = []
        self.floating_items = [
            FloatingItem(SCREEN_WIDTH, SCREEN_HEIGHT, c)
            for c in list(INGREDIENT_COLORS.values()) + [(255, 180, 100)] * 3
        ]

        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        btn_w = 280
        btn_h = 64
        btn_spacing = 85
        start_y = cy + 60

        self.buttons = [
            MenuItem(
                "开始游戏",
                cx,
                start_y,
                title_font,
                (255, 140, 50),
                (255, 170, 80),
                (255, 255, 255),
            ),
            MenuItem(
                "难度设置",
                cx,
                start_y + btn_spacing,
                title_font,
                (120, 80, 200),
                (150, 110, 230),
                (255, 255, 255),
            ),
            MenuItem(
                "游戏设置",
                cx,
                start_y + btn_spacing * 2,
                title_font,
                (60, 140, 80),
                (90, 170, 110),
                (255, 255, 255),
            ),
        ]

        self.title_y = 100
        self.title_phase = 0.0

        cup_x = cx
        cup_y = SCREEN_HEIGHT - 160
        self.cup_img = self._load_cup()
        self.cup_pos = (cup_x, cup_y)
        self.cup_steam_spawn = 0

    def _load_bg(self):
        path = os.path.join(IMAGES_DIR, "奶茶店1.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            return pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        return None

    def _load_cup(self):
        path = os.path.join(IMAGES_DIR, "cup.png")
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (100, 130))
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
        for btn in self.buttons:
            btn.update(dt)

        for item in self.floating_items:
            item.update()

        self.title_phase += dt * 2

        self.cup_steam_spawn += dt
        if self.cup_steam_spawn > 0.08:
            self.cup_steam_spawn = 0
            cx = self.cup_pos[0] + random.randint(20, 80)
            cy = self.cup_pos[1] + 10
            self.steam_particles.append(SteamParticle(cx, cy))

        self.steam_particles = [p for p in self.steam_particles if p.update()]

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

        if self.cup_img:
            cup_x = self.cup_pos[0]
            cup_y = self.cup_pos[1] + math.sin(self.title_phase * 0.7) * 5
            self.screen.blit(self.cup_img, (cup_x, cup_y))

        for p in self.steam_particles:
            p.draw(self.screen)

        for btn in self.buttons:
            btn.draw(self.screen)

        hint = self.font.render("ESC 退出", True, (180, 180, 180))
        self.screen.blit(
            hint, (SCREEN_WIDTH - hint.get_width() - 20, SCREEN_HEIGHT - 35)
        )
