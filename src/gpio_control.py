#!/usr/bin/env python3
"""
GPIO 控制模块
提供基础的 GPIO 操作功能
"""

import Jetson.GPIO as GPIO


class GPIOControl:
    """基础 GPIO 控制类"""
    
    def __init__(self, pin: int, mode: str = 'BOARD', direction: str = 'OUT', initial: str = 'LOW'):
        self.pin = pin
        self.mode = mode
        self.direction = direction
        self.initial = initial
        
        # 设置 GPIO 模式
        if mode == 'BOARD':
            GPIO.setmode(GPIO.BOARD)
        elif mode == 'BCM':
            GPIO.setmode(GPIO.BCM)
        
        # 设置引脚
        GPIO.setup(self.pin, GPIO.OUT, initial=getattr(GPIO, self.initial))
    
    def high(self):
        """设置高电平"""
        GPIO.output(self.pin, GPIO.HIGH)
    
    def low(self):
        """设置低电平"""
        GPIO.output(self.pin, GPIO.LOW)
    
    def cleanup(self):
        """清理 GPIO 引脚"""
        GPIO.cleanup(self.pin)
