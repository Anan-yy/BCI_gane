"""
创意模式 - 奶茶配方评分系统
根据玩家接住的食材组合，给出创意命名和评分等级（黑暗料理 → 米其林三星）
"""

# ============================================================
# 评分等级定义
# ============================================================
RATING_LEVELS = [
    {"min_score": 0, "name": "黑暗料理", "color": (100, 50, 50), "emoji": "💀"},
    {"min_score": 15, "name": "勉强能喝", "color": (150, 100, 50), "emoji": "😅"},
    {"min_score": 30, "name": "普通奶茶", "color": (180, 150, 100), "emoji": "🙂"},
    {"min_score": 45, "name": "好喝推荐", "color": (100, 180, 100), "emoji": "😊"},
    {"min_score": 60, "name": "网红爆款", "color": (255, 150, 200), "emoji": "🔥"},
    {"min_score": 75, "name": "匠心之作", "color": (200, 150, 255), "emoji": "✨"},
    {"min_score": 90, "name": "米其林一星", "color": (255, 215, 0), "emoji": "⭐"},
    {"min_score": 100, "name": "米其林三星", "color": (255, 255, 100), "emoji": "👑"},
]


def get_rating(score):
    """
    根据评分获取等级信息

    参数:
        score: 配方总分（0-100+）

    返回:
        等级字典，包含 name, color, emoji
    """
    result = RATING_LEVELS[0]
    for level in RATING_LEVELS:
        if score >= level["min_score"]:
            result = level
    return result


# ============================================================
# 创意配方库
# 每个配方定义：食材组合 → 创意命名 + 基础评分
# ============================================================
CREATIVE_RECIPES = {
    # === 经典搭配（高分） ===
    frozenset(["红茶", "牛奶"]): {
        "name": "经典丝袜奶茶",
        "score": 85,
        "description": "港式茶餐厅的灵魂",
    },
    frozenset(["红茶", "珍珠"]): {
        "name": "珍珠红茶",
        "score": 80,
        "description": "经典入门款",
    },
    frozenset(["红茶", "牛奶", "珍珠"]): {
        "name": "珍珠奶茶·祖师爷",
        "score": 95,
        "description": "奶茶界的 OG",
    },
    frozenset(["红茶", "牛奶", "椰果"]): {
        "name": "椰香丝袜",
        "score": 82,
        "description": "南洋风味",
    },
    frozenset(["红茶", "牛奶", "布丁"]): {
        "name": "布丁奶茶",
        "score": 88,
        "description": "甜品控的最爱",
    },
    frozenset(["红茶", "牛奶", "仙草"]): {
        "name": "仙草奶绿",
        "score": 86,
        "description": "清凉降火",
    },
    # === 水果/清新系 ===
    frozenset(["牛奶", "椰果"]): {
        "name": "椰奶小清新",
        "score": 70,
        "description": "夏日海边味道",
    },
    frozenset(["牛奶", "布丁"]): {
        "name": "牛奶布丁冻",
        "score": 75,
        "description": "甜品站爆款",
    },
    frozenset(["牛奶", "仙草"]): {
        "name": "仙草牛奶",
        "score": 72,
        "description": "养生局标配",
    },
    frozenset(["牛奶", "珍珠", "布丁"]): {
        "name": "珍珠布丁奶",
        "score": 80,
        "description": "双重口感",
    },
    # === 纯茶系 ===
    frozenset(["红茶"]): {
        "name": "孤傲红茶",
        "score": 40,
        "description": "极简主义",
    },
    frozenset(["红茶", "椰果"]): {
        "name": "椰果冰红茶",
        "score": 65,
        "description": "便利店之王",
    },
    frozenset(["红茶", "仙草"]): {
        "name": "烧仙草红茶",
        "score": 68,
        "description": "台式经典",
    },
    frozenset(["红茶", "布丁"]): {
        "name": "布丁红茶",
        "score": 62,
        "description": "意外的搭配",
    },
    # === 纯配料系（黑暗预警） ===
    frozenset(["珍珠"]): {
        "name": "干嚼珍珠",
        "score": 20,
        "description": "你是在吃零食吗？",
    },
    frozenset(["椰果"]): {
        "name": "椰果刺身",
        "score": 25,
        "description": "纯粹的椰果体验",
    },
    frozenset(["布丁"]): {
        "name": "空口布丁",
        "score": 30,
        "description": "甜品当水喝",
    },
    frozenset(["仙草"]): {
        "name": "苦行僧仙草",
        "score": 22,
        "description": "苦到怀疑人生",
    },
    frozenset(["珍珠", "椰果"]): {
        "name": "珍珠椰果大乱斗",
        "score": 45,
        "description": "嚼到腮帮子酸",
    },
    frozenset(["珍珠", "布丁"]): {
        "name": "双重 Q 弹",
        "score": 50,
        "description": "牙口不好别试",
    },
    frozenset(["珍珠", "仙草"]): {
        "name": "珍珠仙草冻",
        "score": 48,
        "description": "黑与黑的碰撞",
    },
    frozenset(["椰果", "布丁"]): {
        "name": "椰果布丁船",
        "score": 52,
        "description": "甜品融合实验",
    },
    frozenset(["椰果", "仙草"]): {
        "name": "仙草椰椰",
        "score": 55,
        "description": "清凉加倍",
    },
    frozenset(["布丁", "仙草"]): {
        "name": "布丁仙草冻",
        "score": 58,
        "description": "双重冻品",
    },
    # === 三配料（重口味） ===
    frozenset(["珍珠", "椰果", "布丁"]): {
        "name": "料多多",
        "score": 60,
        "description": "一杯顶一顿饭",
    },
    frozenset(["珍珠", "椰果", "仙草"]): {
        "name": "暗黑三重奏",
        "score": 55,
        "description": "嚼嚼嚼嚼嚼",
    },
    frozenset(["珍珠", "布丁", "仙草"]): {
        "name": "全家福·黑化版",
        "score": 58,
        "description": "黑得发亮",
    },
    frozenset(["椰果", "布丁", "仙草"]): {
        "name": "甜品大杂烩",
        "score": 52,
        "description": "选择困难症的解药",
    },
    # === 四配料（究极体） ===
    frozenset(["珍珠", "椰果", "布丁", "仙草"]): {
        "name": "八宝奶茶·缺四样",
        "score": 65,
        "description": "粥既视感",
    },
    # === 全都要 ===
    frozenset(["红茶", "牛奶", "珍珠", "椰果", "布丁", "仙草"]): {
        "name": "奶茶界的满汉全席",
        "score": 100,
        "description": "传说中的究极奶茶",
    },
    frozenset(["红茶", "珍珠", "椰果", "布丁"]): {
        "name": "料王红茶",
        "score": 78,
        "description": "每一口都有料",
    },
    frozenset(["红茶", "珍珠", "椰果", "仙草"]): {
        "name": "四喜奶茶",
        "score": 75,
        "description": "吉祥如意",
    },
    frozenset(["红茶", "牛奶", "珍珠", "椰果"]): {
        "name": "豪华珍珠奶茶",
        "score": 88,
        "description": "升级版经典",
    },
    frozenset(["红茶", "牛奶", "珍珠", "布丁"]): {
        "name": "布丁珍珠奶",
        "score": 90,
        "description": "甜品奶茶巅峰",
    },
    frozenset(["红茶", "牛奶", "珍珠", "仙草"]): {
        "name": "仙草珍珠奶绿",
        "score": 89,
        "description": "清新又浓郁",
    },
    frozenset(["红茶", "牛奶", "椰果", "布丁"]): {
        "name": "椰果布丁奶",
        "score": 84,
        "description": "甜蜜炸弹",
    },
    frozenset(["红茶", "牛奶", "椰果", "仙草"]): {
        "name": "南洋仙草奶",
        "score": 83,
        "description": "热带风情",
    },
    frozenset(["红茶", "牛奶", "布丁", "仙草"]): {
        "name": "双冻奶茶",
        "score": 87,
        "description": "双倍快乐",
    },
    # === 五配料 ===
    frozenset(["红茶", "牛奶", "珍珠", "椰果", "布丁"]): {
        "name": "奶茶界的自助餐",
        "score": 92,
        "description": "吃到饱",
    },
    frozenset(["红茶", "牛奶", "珍珠", "椰果", "仙草"]): {
        "name": "南洋豪华版",
        "score": 91,
        "description": "热带顶配",
    },
    frozenset(["红茶", "牛奶", "珍珠", "布丁", "仙草"]): {
        "name": "五福奶茶",
        "score": 93,
        "description": "五福临门",
    },
    frozenset(["红茶", "牛奶", "椰果", "布丁", "仙草"]): {
        "name": "甜品奶茶船",
        "score": 88,
        "description": "甜品控狂喜",
    },
}


def evaluate_recipe(ingredients):
    """
    评估创意模式的奶茶配方

    参数:
        ingredients: 接住的食材列表，如 ["红茶", "牛奶", "珍珠"]

    返回:
        字典，包含：
            - recipe_name: 配方创意名称
            - score: 基础评分（0-100）
            - description: 配方描述
            - rating: 等级信息（name, color, emoji）
            - total_score: 最终得分（基础评分 + 食材数量奖励）
    """
    if not ingredients:
        return {
            "recipe_name": "空气奶茶",
            "score": 0,
            "description": "你接了个寂寞...",
            "rating": get_rating(0),
            "total_score": 0,
        }

    ingredient_set = frozenset(ingredients)

    # 查找匹配的配方
    if ingredient_set in CREATIVE_RECIPES:
        recipe = CREATIVE_RECIPES[ingredient_set]
        base_score = recipe["score"]
        recipe_name = recipe.get("name", "神秘特调")
        description = recipe.get("description", "独家秘密配方")
    else:
        # 未收录的组合，根据食材数量估算评分
        base_score = _estimate_score(ingredients)
        recipe_name = _generate_random_name(ingredients)
        description = "未被收录的神秘搭配"

    # 食材数量奖励（鼓励多接食材）
    count_bonus = min(len(ingredients) * 3, 15)  # 最多 +15 分
    total_score = min(base_score + count_bonus, 120)  # 上限 120

    return {
        "recipe_name": recipe_name,
        "score": base_score,
        "description": description,
        "rating": get_rating(total_score),
        "total_score": total_score,
    }


def _estimate_score(ingredients):
    """估算未收录配方的基础评分"""
    base = 40  # 基础分
    has_tea = "红茶" in ingredients
    has_milk = "牛奶" in ingredients
    topping_count = sum(1 for i in ingredients if i in ["珍珠", "椰果", "布丁", "仙草"])

    # 有茶有奶加分
    if has_tea and has_milk:
        base += 20
    elif has_tea or has_milk:
        base += 10

    # 配料数量加分
    base += topping_count * 5

    return min(base, 70)


def _generate_random_name(ingredients):
    """为未收录的配方生成随机创意名称"""
    if "红茶" in ingredients and "牛奶" in ingredients:
        return "私房奶茶"
    if len(ingredients) >= 4:
        return "暗黑大满贯"
    if len(ingredients) >= 3:
        return "三料特调"
    if "珍珠" in ingredients:
        return "珍珠特饮"
    if "椰果" in ingredients:
        return "椰果特饮"
    return "未知特调"
