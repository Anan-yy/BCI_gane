class DeadZoneFilter:
    """死区滤波器"""

    def __init__(self, threshold=5):
        self.threshold = threshold

    def filter(self, value):
        """死区滤波：小于阈值的信号视为0"""
        return 0 if abs(value) < self.threshold else value


class ExponentialSmoothing:
    """指数平滑滤波器"""

    def __init__(self, alpha=0.3):
        self.alpha = alpha  # 平滑因子 0<alpha<1
        self.filtered_value = None

    def smooth(self, new_value):
        """指数平滑：y_n = α * x_n + (1-α) * y_{n-1}"""
        if self.filtered_value is None:
            self.filtered_value = new_value
        else:
            self.filtered_value = (
                self.alpha * new_value + (1 - self.alpha) * self.filtered_value
            )
        return self.filtered_value


class SensitivityCurve:
    """头动灵敏度曲线 - 指数映射"""

    def __init__(self, base_sensitivity=1.0, exponent=1.5):
        self.base_sensitivity = base_sensitivity
        self.exponent = exponent

    def apply(self, yaw_value):
        """应用非线性映射，消除顿挫感"""
        sign = 1 if yaw_value >= 0 else -1
        magnitude = abs(yaw_value)
        # 指数映射：y = sign * base * (magnitude^exponent)
        return sign * self.base_sensitivity * (magnitude**self.exponent)
