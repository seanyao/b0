#!/usr/bin/env python3
"""
PCA9685 控制模块
提供极简的 PCA9685 PWM 控制功能
"""

import smbus
import time


class PCA9685:
    """极简 PCA9685 控制器"""
    
    def __init__(self, address=0x40, bus=7):
        self.bus = smbus.SMBus(bus)
        self.addr = address
        self._init()
    
    def _init(self):
        """初始化 - 设置50Hz频率"""
        # 计算50Hz的预分频值
        prescale = int(25000000.0 / (4096 * 50) - 1)
        
        # 进入睡眠模式
        old_mode = self.bus.read_byte_data(self.addr, 0x00)
        self.bus.write_byte_data(self.addr, 0x00, (old_mode & 0x7F) | 0x10)
        
        # 设置频率
        self.bus.write_byte_data(self.addr, 0xFE, prescale)
        
        # 恢复并启用自动增量
        self.bus.write_byte_data(self.addr, 0x00, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.addr, 0x00, old_mode | 0x80)
    
    def servo(self, channel, angle):
        """设置舵机角度 (0-180度)"""
        # 角度转PWM值: 0°=150, 180°=600
        pulse = int(150 + (angle / 180.0) * 450)
        self._set_pwm(channel, 0, pulse)
    
    def pwm(self, channel, duty_cycle):
        """设置PWM占空比 (0-100%)"""
        pulse = int(4095 * duty_cycle / 100.0)
        self._set_pwm(channel, 0, pulse)
    
    def _set_pwm(self, channel, on, off):
        """设置PWM值"""
        base = 0x06 + 4 * channel
        self.bus.write_byte_data(self.addr, base, on & 0xFF)
        self.bus.write_byte_data(self.addr, base + 1, on >> 8)
        self.bus.write_byte_data(self.addr, base + 2, off & 0xFF)
        self.bus.write_byte_data(self.addr, base + 3, off >> 8)
    
    def off(self, channel):
        """关闭指定通道"""
        self._set_pwm(channel, 0, 0)
    
    def all_off(self):
        """关闭所有通道"""
        for ch in range(16):
            self.off(ch)