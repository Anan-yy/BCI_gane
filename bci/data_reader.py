"""
BCI 脑电数据读取模块
当前为 Demo 模拟版本，后续接入 HybridBCI SDK 时只需替换 read_data 方法
"""

import random
import time


class BCIDataReader:
    """
    脑电数据读取器 - 第1周 Demo 版

    功能:
        - 模拟读取专注力（attention）和头动偏航角（yaw）数据
        - 支持超时检测，模拟设备丢包情况

    接入真实设备时:
        替换 read_data() 方法中的模拟代码为真实 SDK 调用
    """

    def __init__(self):
        self.attention = 50  # 专注力值（0-100），初始值 50
        self.yaw = 0  # 头动偏航角（度），正负表示左右
        self.last_update_time = time.time()  # 上一次成功读取的时间戳
        self.timeout = 0.1  # 超时阈值（秒），100ms 内无新数据视为丢包
        self.last_print_time = 0  # 上一次打印日志的时间戳
        self.print_interval = 1.0  # 日志打印间隔（秒），防止终端刷屏

    def read_data(self, verbose=False):
        """
        读取脑电数据（当前为模拟数据）

        参数:
            verbose: 是否打印数据到终端，默认 False

        返回:
            (attention, yaw) 元组
                attention: 专注力值（0-100）
                yaw: 头动偏航角（-30 ~ 30）
        """
        # TODO: 替换为 HybridBCI SDK 的真实读取代码
        # 示例：self.attention, self.yaw = bci_sdk.get_attention(), bci_sdk.get_yaw()
        self.attention = random.randint(30, 90)  # 模拟专注力 30~90 波动
        self.yaw = random.uniform(-30, 30)  # 模拟偏航角 -30~30 波动

        if verbose:
            current_time = time.time()
            if current_time - self.last_print_time >= self.print_interval:
                print(f"[BCI Demo] 专注力: {self.attention}, Yaw: {self.yaw:.1f}")
                self.last_print_time = current_time

        return self.attention, self.yaw

    def read_with_timeout(self):
        """
        带超时的数据读取

        如果距离上次更新超过 timeout（0.1 秒），则认为数据丢失，返回上一次有效数据

        返回:
            (attention, yaw) 元组
        """
        current_time = time.time()
        if current_time - self.last_update_time > self.timeout:
            # 模拟丢包：保持上一次数据不变
            print("[BCI] 数据丢包，保持上一次位置")
            return self.attention, self.yaw

        self.last_update_time = current_time
        return self.read_data()
