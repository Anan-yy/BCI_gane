import pygame
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("疯狂奶茶杯")

WHITE = (255, 255, 255)
BACKGROUND = (240, 240, 240)

cup_img = pygame.image.load("f:/code/BCI_gane/cup.webp").convert_alpha()
ingredient_img = pygame.image.load("f:/code/BCI_gane/小料.webp").convert_alpha()

cup_width = 100
cup_height = 120
cup_img = pygame.transform.scale(cup_img, (cup_width, cup_height))
ingredient_img = pygame.transform.scale(ingredient_img, (50, 50))


class Cup:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 100, 120)
        self.image = cup_img

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.centerx = mouse_x
        self.rect.bottom = HEIGHT - 50

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Ingredient:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.image = ingredient_img
        self.active = True

    def update(self, speed):
        if self.active:
            self.rect.y += speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)


def main():
    clock = pygame.time.Clock()
    running = True

    cup = Cup(WIDTH // 2, HEIGHT - 50)
    ingredients = []
    fall_speed = 3.0

    SPAWN_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_EVENT, 2000)

    collected = 0

    while running:
        screen.fill(BACKGROUND)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_EVENT:
                x = random.randint(50, WIDTH - 50)
                ingredients.append(Ingredient(x, -50))
            elif event.type == pygame.MOUSEWHEEL:
                fall_speed = max(1.0, min(10.0, fall_speed + event.y))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fall_speed = min(10.0, fall_speed + 1.0)
                elif event.key == pygame.K_DOWN:
                    fall_speed = max(1.0, fall_speed - 1.0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            fall_speed = min(10.0, fall_speed + 0.1)

        cup.update()

        for ing in ingredients[:]:
            ing.update(fall_speed)
            if ing.rect.colliderect(cup.rect):
                collected += 1
                ingredients.remove(ing)
            elif ing.rect.top > HEIGHT:
                ingredients.remove(ing)

        cup.draw(screen)
        for ing in ingredients:
            ing.draw(screen)

        font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)
        speed_text = font.render(f"下落速度: {fall_speed:.2f}", True, (50, 50, 50))
        score_text = font.render(f"已收集: {collected}", True, (50, 50, 50))
        screen.blit(speed_text, (10, 10))
        screen.blit(score_text, (10, 50))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
