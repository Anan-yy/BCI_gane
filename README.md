# 疯狂奶茶杯

一款基于 Pygame 开发的脑机接口（BCI）主题休闲小游戏。玩家通过键盘或头动控制杯子，接住从天而降的奶茶食材，制作专属奶茶。

## 项目简介

本项目为 BCI（Brain-Computer Interface）游戏的第 1 周开发版本，目前使用模拟数据代替真实脑电信号。后续版本将接入 HybridBCI SDK，实现真实的头动控制。

**游戏特色：**
- 键盘 / 头动双模式控制
- 食材接住特效（粒子爆炸 + 缩放动画）
- 杯子弹跳与倾斜动画
- 主菜单与开始确认界面，含浮动装饰效果

## 项目结构

```
BCI_gane/
├── main.py                  # 游戏主入口，管理界面跳转
├── config.py                # 全局配置文件（分辨率、速度、颜色、字号等）
├── menu.py                  # 主菜单界面（标题、按钮、浮动粒子）
├── game_start_screen.py     # 游戏开始确认界面
├── requirements.txt         # Python 依赖列表
│
├── game/                    # 游戏核心模块
│   ├── sprites.py           # 精灵定义（杯子、食材、粒子、接住特效）
│   ├── ingredient_manager.py# 食材生成管理器
│   └── game_manager.py      # 游戏管理器（旧版，已被 main.py 取代）
│
├── bci/                     # 脑机接口模块
│   ├── data_reader.py       # BCI 数据读取器（当前为模拟数据）
│   └── filter.py            # 信号滤波器（死区滤波、指数平滑、灵敏度曲线）
│
├── data/                    # 数据管理模块
│   ├── score_manager.py     # 分数/金钱管理系统
│   └── ingredient_config.py # 食材属性配置表
│
└── assets/                  # 资源文件夹
    ├── images/              # 图片资源（背景、杯子、食材）
    ├── fonts/               # 字体文件（站酷快乐体等）
    └── sounds/              # 音效文件（预留）
```

## 快速开始

### 环境要求

- Python 3.8+
- Pygame 2.0+

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行游戏

```bash
python main.py
```

## 游戏控制

| 按键 | 功能 |
|------|------|
| ← / → | 左右移动杯子（键盘模式） |
| Y | 切换到头动控制模式（模拟） |
| K | 切换回键盘控制模式 |
| ESC | 返回主菜单 / 退出 |
| Enter | 开始游戏 |
| 1 / 2 / 3 | 快捷选择菜单项 |

## 配置说明

所有可调参数集中在 `config.py` 中，常用修改项：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `SCREEN_WIDTH` | 1280 | 窗口宽度（像素） |
| `SCREEN_HEIGHT` | 720 | 窗口高度（像素） |
| `FPS` | 60 | 游戏帧率 |
| `CUP_WIDTH` / `CUP_HEIGHT` | 80 / 100 | 杯子尺寸 |
| `CUP_SPEED` | 5 | 杯子移动速度 |
| `INGREDIENT_SIZE` | 40 | 食材尺寸 |
| `INGREDIENT_SPEED` | 3 | 食材下落速度（调大 = 难度增加） |
| `INGREDIENT_SPAWN_INTERVAL` | 1000 | 食材生成间隔（毫秒），调小 = 难度增加 |
| `DEAD_ZONE` | 5 | 头动死区阈值，防抖动 |
| `SMOOTHING_FACTOR` | 0.3 | 信号平滑因子，越大响应越快 |
| `YAW_SCALE` | 0.5 | 头动映射系数 |

### 字体大小调整

在 `main.py` 中修改各界面的字号：

```python
# 主菜单
font = load_chinese_font(24)       # 副标题字号
title_font = load_chinese_font(40) # 按钮文字字号

# 开始界面
font = load_chinese_font(24)       # 副标题字号
title_font = load_chinese_font(48) # 标题字号

# 游戏中
font = load_chinese_font(36)       # HUD 文字字号
hint_font = load_chinese_font(20)  # 底部提示字号
```

## 模块说明

### 信号滤波器 (`bci/filter.py`)

- **DeadZoneFilter（死区滤波）**：忽略幅度小于阈值的微小信号，防止手抖误触
- **ExponentialSmoothing（指数平滑）**：使信号变化更平滑，减少抖动。公式：`y_n = α * x_n + (1-α) * y_{n-1}`
- **SensitivityCurve（灵敏度曲线）**：非线性映射，小幅度更灵敏，大幅度更稳定

### 食材系统

- 食材由 `IngredientManager` 按固定间隔生成
- 避免连续掉落同一种食材
- 每种食材有独立的分值（`INGREDIENT_POINTS`）
- 支持"必接食材"机制：接到必接食材后才能累积本杯金钱

## 接入真实 BCI 设备

当前版本使用模拟数据。接入真实设备时，只需修改 `bci/data_reader.py` 中的 `read_data()` 方法：

```python
def read_data(self, verbose=False):
    # TODO: 替换为 HybridBCI SDK 的真实读取代码
    self.attention, self.yaw = bci_sdk.get_attention(), bci_sdk.get_yaw()
    return self.attention, self.yaw
```

## 开发计划

- [x] 第 1 周：基础游戏框架 + 模拟数据
- [ ] 第 2 周：接入 HybridBCI SDK + 真实头动控制
- [ ] 第 3 周：难度系统 + 关卡解锁
- [ ] 第 4 周：音效 + UI 优化

## 许可证

本项目仅供学习和研究使用。
