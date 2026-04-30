import pygame

# 屏幕配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "疯狂奶茶杯 - 第1周"

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 杯子配置
CUP_WIDTH = 80
CUP_HEIGHT = 100
CUP_SPEED = 5
CUP_COLOR = BROWN

# 食材配置
INGREDIENT_SIZE = 40
INGREDIENT_SPEED = 3
INGREDIENT_TYPES = ["红茶", "牛奶", "珍珠", "椰果"]
INGREDIENT_COLORS = {
    "红茶": (160, 82, 45),
    "牛奶": (255, 250, 240),
    "珍珠": (105, 105, 105),
    "椰果": (240, 230, 140),
}
INGREDIENT_POINTS = {"红茶": 8, "牛奶": 5, "珍珠": 10, "椰果": 6}

# 脑电数据配置
DEFAULT_ATTENTION = 50
DEAD_ZONE = 5
SMOOTHING_FACTOR = 0.3
YAW_SCALE = 0.5

# 生成间隔（毫秒）
INGREDIENT_SPAWN_INTERVAL = 1000
