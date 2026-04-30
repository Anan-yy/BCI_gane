import random
import time


class BCIDataReader:
    """HybridBCI SDK数据读取器 - 第1周Demo版"""

    def __init__(self):
        self.attention = 50  # 专注力 0-100
        self.yaw = 0  # 头动偏航角
        self.last_update_time = time.time()
        self.timeout = 0.1  # 100ms超时
        self.last_print_time = 0
        self.print_interval = 1.0  # 每秒只打印一次

    def read_data(self, verbose=False):
        """读取脑电数据 - 实际使用时替换为真实SDK调用"""
        # TODO: 替换为HybridBCI SDK的真实读取代码
        # 模拟数据输出
        self.attention = random.randint(30, 90)
        self.yaw = random.uniform(-30, 30)

        # 控制打印频率，默认不打印（减少终端输出）
        if verbose:
            current_time = time.time()
            if current_time - self.last_print_time >= self.print_interval:
                print(f"[BCI Demo] 专注力: {self.attention}, Yaw: {self.yaw:.1f}")
                self.last_print_time = current_time

        return self.attention, self.yaw

    def read_with_timeout(self):
        """带超时的数据读取，超时返回上一次数据"""
        current_time = time.time()
        if current_time - self.last_update_time > self.timeout:
            # 模拟丢包，保持上一次数据
            print("[BCI] 数据丢包，保持上一次位置")
            return self.attention, self.yaw

        self.last_update_time = current_time
        return self.read_data()
