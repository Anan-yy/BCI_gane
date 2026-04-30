import pygame


def check_collision(cup, ingredients):
    """检查杯子和食材的碰撞"""
    return pygame.sprite.spritecollide(cup, ingredients, True)
