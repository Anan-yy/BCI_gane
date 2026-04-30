class ScoreManager:
    """分数和金钱管理系统"""

    def __init__(self):
        self.score = 0
        self.money = 0
        self.current_cup_ingredients = []  # 当前杯子的食材
        self.has_required = False  # 是否接到了必接食材
        self.required_ingredient = None  # 当前必接食材

    def set_required_ingredient(self, ingredient_type):
        """设置当前杯子的必接食材"""
        self.required_ingredient = ingredient_type
        self.has_required = False
        self.current_cup_ingredients = []

    def add_ingredient(self, ingredient_type, is_required=False):
        """接住食材，加分"""
        from config import INGREDIENT_POINTS

        points = INGREDIENT_POINTS.get(ingredient_type, 5)

        if is_required:
            self.has_required = True
            self.money += points
            print(f"接住必接食材 {ingredient_type}，获得 {points} 金钱")
        elif self.has_required:
            # 只有接到必接后才能累积单价
            self.money += points
            print(f"接住选接食材 {ingredient_type}，获得 {points} 金钱")
        else:
            # 没接到必接，整杯单价为0
            print(f"未接到必接食材，{ingredient_type} 无效")

        self.score += points
        self.current_cup_ingredients.append(ingredient_type)

    def finish_cup(self):
        """完成一杯，重置状态"""
        if not self.has_required:
            self.money = max(0, self.money - 10)  # 惩罚
            print("未接到必接食材，整杯单价归零！")

        print(f"本杯完成！当前总分: {self.score}, 总金钱: {self.money}")
        self.has_required = False
        self.current_cup_ingredients = []

    def draw(self, screen, font):
        """在屏幕上显示分数和金钱"""
        score_text = font.render(f"分数: {self.score}", True, (0, 0, 0))
        money_text = font.render(f"金钱: {self.money}", True, (0, 100, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(money_text, (10, 50))
