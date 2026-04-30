import pygame
from game.sprites import Cup, Ingredient
from game.ingredient_manager import IngredientManager
from data.score_manager import ScoreManager
import sys


class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("疯狂奶茶杯 - 第1周")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)

        self.cup = Cup()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.cup)
        self.ingredients = pygame.sprite.Group()

        self.score_manager = ScoreManager()
        self.ingredient_manager = IngredientManager()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        keys = pygame.key.get_pressed()
        self.cup.update(keys=keys)
        self.ingredients.update()

        # 生成食材（第1周只生成红茶）
        ingredient = self.ingredient_manager.update()
        if ingredient:
            self.ingredients.add(ingredient)

        # 碰撞检测
        hits = pygame.sprite.spritecollide(self.cup, self.ingredients, False)
        for hit in hits:
            hit.kill()
            self.score_manager.score += 10
            print(f"接住食材！分数: {self.score_manager.score}")
        for hit in hits:
            self.score_manager.score += 10
            print(f"接住食材！分数: {self.score_manager.score}")

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.all_sprites.draw(self.screen)
        self.ingredients.draw(self.screen)
        self.score_manager.draw(self.screen, self.font)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
