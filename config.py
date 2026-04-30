import pygame
import os

# 屏幕配置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "疯狂奶茶杯 - 第1周"

# 资源路径
ASSETS_DIR = "assets"
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# 图片路径（后期导入图片时只需替换文件）
BACKGROUND_IMG = os.path.join(IMAGES_DIR, "background.png")
CUP_IMG = os.path.join(IMAGES_DIR, "cup.png")
INGREDIENT_IMGS = {
    "红茶": os.path.join(IMAGES_DIR, "tea.png"),
    "牛奶": os.path.join(IMAGES_DIR, "milk.png"),
    "珍珠": os.path.join(IMAGES_DIR, "pearl.png"),
    "椰果": os.path.join(IMAGES_DIR, "coconut.png"),
    "布丁": os.path.join(IMAGES_DIR, "pudding.png"),
    "仙草": os.path.join(IMAGES_DIR, "grass_jelly.png"),
    "秘方": os.path.join(IMAGES_DIR, "secret_recipe.png"),
}

# 支持中文的字体列表（按优先级）
CHINESE_FONTS = [
    "simhei.ttf",  # 黑体
    "simkai.ttf",  # 楷体
    "msyh.ttf",  # 微软雅黑
    "msyhbd.ttf",  # 微软雅黑粗体
    os.path.join(ASSETS_DIR, "fonts", "simhei.ttf"),  # 项目内字体
]

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
