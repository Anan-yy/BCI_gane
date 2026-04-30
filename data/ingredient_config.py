"""食材属性配置表 - 何柒梅任务2"""

# 食材类型定义
INGREDIENT_TYPES = {
    "红茶": {
        "name": "红茶",
        "type": "base",
        "price": 8,
        "is_required": False,
        "unlock_level": 1,
    },
    "牛奶": {
        "name": "牛奶",
        "type": "base",
        "price": 5,
        "is_required": False,
        "unlock_level": 1,
    },
    "珍珠": {
        "name": "珍珠",
        "type": "topping",
        "price": 10,
        "is_required": True,
        "unlock_level": 2,
    },
    "椰果": {
        "name": "椰果",
        "type": "topping",
        "price": 6,
        "is_required": False,
        "unlock_level": 1,
    },
    "布丁": {
        "name": "布丁",
        "type": "topping",
        "price": 12,
        "is_required": True,
        "unlock_level": 3,
    },
    "仙草": {
        "name": "仙草",
        "type": "topping",
        "price": 8,
        "is_required": False,
        "unlock_level": 2,
    },
}


def get_ingredient_info(ing_type):
    """获取食材信息"""
    return INGREDIENT_TYPES.get(ing_type, None)


def get_available_ingredients(level=1):
    """根据等级获取可用的食材"""
    return [k for k, v in INGREDIENT_TYPES.items() if v["unlock_level"] <= level]
