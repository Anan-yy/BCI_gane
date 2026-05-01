# 疯狂奶茶杯

一款基于 Pygame 开发的脑机接口（BCI）主题休闲小游戏。玩家通过键盘或头动控制杯子，接住从天而降的奶茶食材，制作专属奶茶。

## 项目简介

本项目为 BCI（Brain-Computer Interface）游戏的第 1 周开发版本，目前使用模拟数据代替真实脑电信号。后续版本将接入 HybridBCI SDK，实现真实的头动控制。

**游戏特色：**
- 四种游戏模式：常规 / 挑战 / 创意 / 脑机接口
- 键盘 / 头动双模式控制
- 创意模式：自由搭配，黑暗料理→米其林三星评分系统
- 专注力映射曲线：高专注获得更高评分加成
- BCI 设备支持：通过 TCP 连接科创平台，实时获取专注力和头动数据
- 食材接住特效（粒子爆炸 + 缩放动画）
- 杯子弹跳与倾斜动画
- 主菜单模式选择按钮，悬停显示模式详情，点击切换带粒子特效

## 项目结构

```
BCI_gane/
├── main.py                  # 游戏主入口，管理界面跳转
├── config.py                # 全局配置文件（分辨率、速度、颜色、BCI参数等）
├── requirements.txt         # Python 依赖列表
├── bci_config.json          # BCI连接配置（自动生成）
│
├── menu/                    # 菜单系统模块（重构后）
│   ├── __init__.py          # 导出主菜单和设置页面
│   ├── components.py        # 基础组件：MenuItem按钮、ClickParticle粒子
│   ├── particles.py         # 粒子系统：FloatingItem浮动粒子、SteamParticle蒸汽
│   ├── mode_selector.py     # 模式选择器：ModeSelector、ModePreviewDisplay
│   ├── bci_button.py        # BCI模式按钮：带脉冲动画和发光特效
│   ├── text_input.py        # 文本输入框：用于IP和端口输入
│   └── screens/             # 页面屏幕
│       ├── __init__.py
│       ├── main_menu.py     # 主菜单页面
│       ├── game_settings.py # 游戏设置页面
│       └── bci_settings.py  # BCI连接设置页面
│
├── game/                    # 游戏核心模块
│   ├── sprites.py           # 精灵定义（杯子、食材、粒子、接住特效）
│   ├── ingredient_manager.py# 食材生成管理器
│   └── game_manager.py      # 游戏管理器（旧版，已被 main.py 取代）
│
├── bci/                     # 脑机接口模块
│   ├── __init__.py
│   ├── config.py            # BCI配置管理（保存/加载 bci_config.json）
│   ├── data_reader.py       # BCI数据读取器（TCP连接科创平台）
│   └── filter.py            # 信号滤波器（死区滤波、指数平滑、灵敏度曲线）
│
├── data/                    # 数据管理模块
│   ├── score_manager.py     # 分数/金钱管理系统
│   ├── ingredient_config.py # 食材属性配置表
│   └── recipes.py           # 创意模式配方评分系统
│
├── bci_cup_control.py       # PyQt5独立BCI演示程序（TCP客户端）
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
| Y | 切换到头动控制模式 |
| K | 切换回键盘控制模式 |
| ESC | 返回主菜单 / 退出 |
| Enter | 开始游戏 |
| 2 | 切换模式 |

## 游戏模式

### 常规模式 🍵（绿色）
- **玩法**：接住必接食材（红茶）后才能累积本杯收益
- **难度**：标准下落速度，1 秒生成一个食材
- **适合**：新手入门，体验基础玩法

### 挑战模式 🔥（红色）
- **玩法**：同常规模式，但节奏更快
- **难度**：下落速度提升 60%，生成间隔缩短至 0.6 秒
- **适合**：追求刺激，考验反应速度

### 创意模式 ✨（紫色）
- **玩法**：无必接食材限制，自由接住任意食材组合
- **评分**：根据接住的食材组合，系统自动评估配方等级
- **专注力加成**：专注力越高，评分倍率越大（最高 1.5 倍）
- **适合**：喜欢探索不同搭配的玩家

### 脑机接口模式 🧠（蓝色）
- **玩法**：通过 BCI 设备读取真实专注力和头动数据
- **控制**：头部转动控制杯子移动，专注力影响评分倍率
- **配置**：点击"游戏设置" → "BCI设置"，配置服务器IP和端口
- **适合**：已连接脑机接口设备的玩家

## 脑机接口配置

### 连接科创平台

1. 启动游戏，在主菜单点击 **"游戏设置"**
2. 点击 **"BCI设置"** 按钮进入配置页面
3. 输入科创平台服务器的 IP 地址和端口号（默认 `127.0.0.1:8000`）
4. 点击 **"测试连接"** 验证连接是否成功
5. 点击 **"返回"** 自动保存配置
6. 回到主菜单，点击 **"脑机接口"** 按钮进入游戏

### 数据格式要求

BCI 设备通过 TCP Socket 发送 JSON 格式数据（4字节长度前缀 + JSON payload）：

```json
// 专注力数据
{"msg": "ipc_algorithm_test", "algorithm_name": "attention", "result_args": {"data": 75}}

// 头动数据
{"msg": "ipc_algorithm_test", "algorithm_name": "gyroscope", "result_args": {"data": {"gyroscope_x": 15.2}}}

// 眨眼数据（可选）
{"msg": "ipc_algorithm_test", "algorithm_name": "blink", "result_args": {"data": true}}
```

### 配置文件

BCI 连接配置保存在 `bci_config.json` 文件中：

```json
{
  "server_ip": "127.0.0.1",
  "server_port": 8000
}
```

## 创意模式评分系统

### 评分等级（从低到高）

| 等级 | 最低分 | 描述 |
|------|--------|------|
| 💀 黑暗料理 | 0 | 搭配翻车，勉强入口 |
| 😅 勉强能喝 | 15 | 味道奇怪，但能喝 |
| 🙂 普通奶茶 | 30 | 中规中矩的日常款 |
| 😊 好喝推荐 | 45 | 味道不错，值得一试 |
| 🔥 网红爆款 | 60 | 热门配方，人气之选 |
| ✨ 匠心之作 | 75 | 精心搭配，品质出众 |
| ⭐ 米其林一星 | 90 | 专业级奶茶配方 |
| 👑 米其林三星 | 100 | 传说中的究极奶茶 |

### 专注力映射曲线

创意模式中，玩家的专注力会转换为评分倍率：

- **分心状态（0-30）**：倍率 0.5~0.8，专注不够，配方打折扣
- **平稳专注（30-70）**：倍率 0.8~1.0，正常发挥
- **高度专注（70-100）**：倍率 1.0~1.5，超常发挥，评分飙升

> 最终得分 = 配方基础分 + 食材数量奖励 × 专注力倍率

### 部分经典配方示例

| 食材组合 | 配方名称 | 基础评分 |
|----------|----------|----------|
| 红茶 + 牛奶 + 珍珠 | 珍珠奶茶·祖师爷 | 95 |
| 红茶 + 牛奶 | 经典丝袜奶茶 | 85 |
| 红茶 + 牛奶 + 布丁 | 布丁奶茶 | 88 |
| 红茶 + 仙草 | 烧仙草红茶 | 68 |
| 珍珠 | 干嚼珍珠 | 20 |
| 全部食材 | 奶茶界的满汉全席 | 100 |

> 完整配方表见 `data/recipes.py`，包含 40+ 种预设组合

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
| `BCI_CONNECTION_TIMEOUT` | 5 | BCI连接超时时间（秒） |

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

### 菜单系统 (`menu/`)

重构后的菜单系统按功能拆分：

| 文件 | 说明 |
|------|------|
| `components.py` | 基础组件：`MenuItem`（按钮）、`ClickParticle`（点击粒子） |
| `particles.py` | 粒子系统：`FloatingItem`（浮动装饰）、`SteamParticle`（蒸汽） |
| `mode_selector.py` | 模式选择器：`ModeSelector`（循环切换）、`ModePreviewDisplay`（预览面板） |
| `bci_button.py` | BCI模式按钮：带脉冲呼吸动画和发光粒子特效 |
| `text_input.py` | 文本输入框：支持光标闪烁和键盘输入 |
| `screens/main_menu.py` | 主菜单页面 |
| `screens/game_settings.py` | 游戏设置页面 |
| `screens/bci_settings.py` | BCI连接设置页面 |

### 信号滤波器 (`bci/filter.py`)

- **DeadZoneFilter（死区滤波）**：忽略幅度小于阈值的微小信号，防止手抖误触
- **ExponentialSmoothing（指数平滑）**：使信号变化更平滑，减少抖动。公式：`y_n = α * x_n + (1-α) * y_{n-1}`
- **SensitivityCurve（灵敏度曲线）**：非线性映射，小幅度更灵敏，大幅度更稳定
- **AttentionMappingCurve（专注力映射）**：创意模式专用，将专注力转换为评分倍率（0.5~1.5）

### BCI数据读取器 (`bci/data_reader.py`)

- 通过 TCP Socket 连接到科创平台
- 解析 JSON 格式数据（专注力、头动、眨眼）
- 支持超时检测和连接状态管理
- 可自定义服务器IP和端口

### 创意模式配方系统 (`data/recipes.py`)

- 40+ 种预设配方组合，每种有独特的创意命名和评分
- 未收录的组合会根据食材类型和数量估算评分
- 评分等级从"黑暗料理"到"米其林三星"共 8 级
- 食材数量奖励机制，鼓励玩家接住更多食材

### 食材系统

- 食材由 `IngredientManager` 按固定间隔生成
- 避免连续掉落同一种食材
- 每种食材有独立的分值（`INGREDIENT_POINTS`）
- 支持"必接食材"机制：接到必接食材后才能累积本杯金钱

## 开发计划

- [x] 第 1 周：基础游戏框架 + 模拟数据
- [x] 第 2 周：三种游戏模式 + 创意模式评分系统
- [x] 第 3 周：BCI模块实现 + TCP连接科创平台 + 菜单重构
- [ ] 第 4 周：接入 HybridBCI SDK + 真实头动控制
- [ ] 第 5 周：音效 + UI 优化 + 关卡解锁

## 许可证

本项目仅供学习和研究使用。
