import random
import time
from game.sprites import Ingredient
from config import *


class IngredientManager:
    def __init__(self):
        self.ingredients = []
        self.last_spawn_time = time.time()
        self.spawn_interval = INGREDIENT_SPAWN_INTERVAL / 1000.0
        self.last_type = None

    def should_spawn(self):
        current_time = time.time()
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = current_time
            return True
        return False

    def spawn_ingredient(self, required_types=None):
        # 避免连续掉同一食材
        available_types = [t for t in INGREDIENT_TYPES if t != self.last_type]
        if not available_types:
            available_types = INGREDIENT_TYPES

        ing_type = random.choice(available_types)
        self.last_type = ing_type

        is_required = False
        if required_types and ing_type in required_types:
            is_required = True

        return Ingredient(ing_type, is_required)

    def update(self, required_types=None):
        if self.should_spawn():
            ingredient = self.spawn_ingredient(required_types)
            return ingredient
        return None
