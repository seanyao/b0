#!/usr/bin/env python3
"""
PWM 控制模块
提供软件 PWM 功能
"""

import time
import threading
from gpio_control import GPIOControl


class SoftwarePWM:
    """软件 PWM 控制类"""
    
    def __init__(self, pin: int, frequency: float = 1000.0, mode: str = 'BOARD'):
        self.pin = pin
        self.frequency = frequency
        self.mode = mode
        self.duty_cycle = 0.0
        self.running = False
        self.thread = None
        self.period = 1.0 / frequency
        
        # 创建 GPIO 控制器
        self.gpio = GPIOControl(pin, mode, 'OUT', 'LOW')
    
    def start(self, duty_cycle: float = None):
        """启动 PWM 输出"""
        if self.running:
            return False
        
        if duty_cycle is not None:
            self.set_duty_cycle(duty_cycle)
        
        self.running = True
        self.thread = threading.Thread(target=self._pwm_loop, daemon=True)
        self.thread.start()
        return True
    
    def stop(self):
        """停止 PWM 输出"""
        if not self.running:
            return False
        
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None
        
        # 设置引脚为低电平
        self.gpio.low()
        return True
    
    def set_duty_cycle(self, duty_cycle: float):
        """设置占空比"""
        if not (0.0 <= duty_cycle <= 100.0):
            raise ValueError("占空比必须在 0-100% 范围内")
        self.duty_cycle = duty_cycle
    
    def _pwm_loop(self):
        """PWM 生成循环"""
        while self.running:
            if self.duty_cycle > 0:
                # 计算高电平和低电平时间
                on_time = self.period * (self.duty_cycle / 100.0)
                off_time = self.period - on_time
                
                # 输出高电平
                self.gpio.high()
                time.sleep(on_time)
                
                # 输出低电平
                self.gpio.low()
                time.sleep(off_time)
            else:
                # 占空比为0时，保持低电平
                self.gpio.low()
                time.sleep(self.period)
    
    def cleanup(self):
        """清理资源"""
        self.stop()
        self.gpio.cleanup()
