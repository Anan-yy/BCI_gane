"""
信号滤波模块 - 处理 BCI 脑电设备的原始信号
包含：死区滤波、指数平滑、非线性灵敏度映射
"""


class DeadZoneFilter:
    """
    死区滤波器 - 消除微小抖动信号

    原理：当输入信号绝对值小于阈值时，输出 0；否则原样输出

    参数:
        threshold: 死区阈值，默认 5。信号绝对值 < threshold 时视为 0
                   值越大，过滤掉的微小信号越多，但灵敏度也会降低
    """

    def __init__(self, threshold=5):
        self.threshold = threshold

    def filter(self, value):
        """
        对输入值进行死区滤波

        参数:
            value: 原始信号值（如头动偏航角）

        返回:
            滤波后的值，小幅信号返回 0
        """
        return 0 if abs(value) < self.threshold else value


class ExponentialSmoothing:
    """
    指数平滑滤波器 - 使信号变化更平滑，减少抖动

    原理：y_n = α * x_n + (1-α) * y_{n-1}
    新输出 = 平滑因子 * 新输入 + (1 - 平滑因子) * 旧输出

    参数:
        alpha: 平滑因子，范围 (0, 1)，默认 0.3
               值越大：响应越快，但抖动越明显
               值越小：越平滑，但延迟越大，手感"粘滞"
    """

    def __init__(self, alpha=0.3):
        self.alpha = alpha  # 平滑因子
        self.filtered_value = None  # 上一次平滑后的值

    def smooth(self, new_value):
        """
        对新输入值进行指数平滑

        参数:
            new_value: 新的原始信号值

        返回:
            平滑后的信号值
        """
        if self.filtered_value is None:
            self.filtered_value = new_value
        else:
            self.filtered_value = (
                self.alpha * new_value + (1 - self.alpha) * self.filtered_value
            )
        return self.filtered_value


class SensitivityCurve:
    """
    头动灵敏度曲线 - 非线性映射，消除小幅度顿挫感

    原理：对输入信号进行指数映射，小幅度更灵敏，大幅度更稳定
    公式：y = sign * base_sensitivity * (|x| ^ exponent)

    参数:
        base_sensitivity: 基础灵敏度系数，默认 1.0，整体缩放输出值
        exponent: 指数系数，默认 1.5
                  值越大：小幅度信号被压缩更多，需要更大动作才能触发
                  值越小：小幅度信号响应更灵敏
    """

    def __init__(self, base_sensitivity=1.0, exponent=1.5):
        self.base_sensitivity = base_sensitivity
        self.exponent = exponent

    def apply(self, yaw_value):
        """
        对偏航角应用非线性灵敏度映射

        参数:
            yaw_value: 原始偏航角值

        返回:
            映射后的偏航角值
        """
        sign = 1 if yaw_value >= 0 else -1
        magnitude = abs(yaw_value)
        return sign * self.base_sensitivity * (magnitude**self.exponent)


class AttentionMappingCurve:
    """
    创意模式专注力映射曲线 - 将专注力转换为评分加成倍率

    原理：
        - 低专注力（0-30）：倍率低（0.5-0.8），配方评分打折扣
        - 中专注力（30-70）：倍率线性增长（0.8-1.0）
        - 高专注力（70-100）：倍率超线性增长（1.0-1.5），专注越高加成越大

    公式：分段函数
        - attention < 30:  multiplier = 0.5 + (attention / 30) * 0.3
        - 30 <= attention < 70:  multiplier = 0.8 + ((attention - 30) / 40) * 0.2
        - attention >= 70:  multiplier = 1.0 + ((attention - 70) / 30) * 0.5

    参数:
        low_threshold: 低专注力阈值，默认 30
        high_threshold: 高专注力阈值，默认 70
        max_multiplier: 最大倍率，默认 1.5
    """

    def __init__(self, low_threshold=30, high_threshold=70, max_multiplier=1.5):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.max_multiplier = max_multiplier

    def map_attention(self, attention):
        """
        将专注力值映射为评分倍率

        参数:
            attention: 专注力值（0-100）

        返回:
            倍率值（0.5-1.5），用于乘以配方基础评分
        """
        attention = max(0, min(100, attention))  # 限制在 0-100 范围

        if attention < self.low_threshold:
            # 低专注区：0.5 ~ 0.8
            multiplier = 0.5 + (attention / self.low_threshold) * 0.3
        elif attention < self.high_threshold:
            # 中专注区：0.8 ~ 1.0
            multiplier = (
                0.8
                + (
                    (attention - self.low_threshold)
                    / (self.high_threshold - self.low_threshold)
                )
                * 0.2
            )
        else:
            # 高专注区：1.0 ~ max_multiplier
            multiplier = 1.0 + (
                (attention - self.high_threshold) / (100 - self.high_threshold)
            ) * (self.max_multiplier - 1.0)

        return multiplier

    def get_rating_tier(self, attention):
        """
        根据专注力获取当前所处的倍率区间描述

        参数:
            attention: 专注力值（0-100）

        返回:
            区间描述字符串
        """
        if attention < self.low_threshold:
            return "分心状态"
        elif attention < self.high_threshold:
            return "平稳专注"
        else:
            return "高度专注"
