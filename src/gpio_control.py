#!/usr/bin/env python3
"""
通用 GPIO 控制模块
提供基础的 GPIO 操作和软件 PWM 功能
"""

import Jetson.GPIO as GPIO
import time
import threading
import logging
from typing import Optional, Callable
from contextlib import contextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GPIOControl:
    """
    基础 GPIO 控制类
    提供 GPIO 引脚的基本操作功能
    """
    
    def __init__(self, pin: int, mode: str = 'BOARD', direction: str = 'OUT', 
                 initial: str = 'LOW', pull_up_down: str = None):
        """
        初始化 GPIO 控制器
        
        Args:
            pin: GPIO 引脚号
            mode: 引脚编号模式 ('BOARD' 或 'BCM')
            direction: 引脚方向 ('IN' 或 'OUT')
            initial: 初始状态 ('HIGH' 或 'LOW')
            pull_up_down: 上拉/下拉电阻 ('PUD_UP', 'PUD_DOWN', 或 None)
        """
        self.pin = pin
        self.mode = mode
        self.direction = direction
        self.initial = initial
        self.pull_up_down = pull_up_down
        self.is_setup = False
        
        # 设置 GPIO 模式
        if mode == 'BOARD':
            GPIO.setmode(GPIO.BOARD)
        elif mode == 'BCM':
            GPIO.setmode(GPIO.BCM)
        else:
            raise ValueError("mode 必须是 'BOARD' 或 'BCM'")
        
        # 设置引脚
        self._setup_pin()
    
    def _setup_pin(self):
        """设置 GPIO 引脚"""
        try:
            if self.direction == 'OUT':
                if self.pull_up_down:
                    GPIO.setup(self.pin, GPIO.OUT, 
                              initial=getattr(GPIO, self.initial),
                              pull_up_down=getattr(GPIO, self.pull_up_down))
                else:
                    GPIO.setup(self.pin, GPIO.OUT, 
                              initial=getattr(GPIO, self.initial))
            elif self.direction == 'IN':
                if self.pull_up_down:
                    GPIO.setup(self.pin, GPIO.IN, 
                              pull_up_down=getattr(GPIO, self.pull_up_down))
                else:
                    GPIO.setup(self.pin, GPIO.IN)
            
            self.is_setup = True
            logger.info(f"GPIO {self.pin} 设置完成: {self.direction}, 初始状态: {self.initial}")
            
        except Exception as e:
            logger.error(f"GPIO {self.pin} 设置失败: {e}")
            raise
    
    def output(self, state: str):
        """
        设置输出状态
        
        Args:
            state: 输出状态 ('HIGH' 或 'LOW')
        """
        if not self.is_setup:
            raise RuntimeError("GPIO 引脚未设置")
        
        try:
            GPIO.output(self.pin, getattr(GPIO, state))
            logger.debug(f"GPIO {self.pin} 设置为 {state}")
        except Exception as e:
            logger.error(f"GPIO {self.pin} 输出失败: {e}")
            raise
    
    def input(self) -> str:
        """
        读取输入状态
        
        Returns:
            输入状态 ('HIGH' 或 'LOW')
        """
        if not self.is_setup:
            raise RuntimeError("GPIO 引脚未设置")
        
        try:
            state = GPIO.input(self.pin)
            return 'HIGH' if state else 'LOW'
        except Exception as e:
            logger.error(f"GPIO {self.pin} 输入读取失败: {e}")
            raise
    
    def high(self):
        """设置高电平"""
        self.output('HIGH')
    
    def low(self):
        """设置低电平"""
        self.output('LOW')
    
    def toggle(self):
        """切换状态"""
        current = self.input()
        new_state = 'LOW' if current == 'HIGH' else 'HIGH'
        self.output(new_state)
    
    def cleanup(self):
        """清理 GPIO 引脚"""
        if self.is_setup:
            try:
                GPIO.cleanup(self.pin)
                self.is_setup = False
                logger.info(f"GPIO {self.pin} 清理完成")
            except Exception as e:
                logger.error(f"GPIO {self.pin} 清理失败: {e}")
    
    @contextmanager
    def context(self):
        """上下文管理器"""
        try:
            yield self
        finally:
            self.cleanup()
    
    def __str__(self):
        return f"GPIOControl(pin={self.pin}, mode={self.mode}, direction={self.direction})"


class SoftwarePWM:
    """
    软件 PWM 控制类
    使用软件方式生成 PWM 信号
    """
    
    def __init__(self, pin: int, frequency: float = 1000.0, 
                 mode: str = 'BOARD', invert_logic: bool = False):
        """
        初始化软件 PWM 控制器
        
        Args:
            pin: GPIO 引脚号
            frequency: PWM 频率 (Hz)
            mode: 引脚编号模式 ('BOARD' 或 'BCM')
            invert_logic: 是否使用反向逻辑
        """
        self.pin = pin
        self.frequency = frequency
        self.mode = mode
        self.invert_logic = invert_logic
        self.duty_cycle = 0.0
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.pulse_count = 0
        self.period = 1.0 / frequency
        
        # 创建 GPIO 控制器
        self.gpio = GPIOControl(pin, mode, 'OUT', 'LOW')
        
        logger.info(f"软件 PWM 初始化完成: 引脚={pin}, 频率={frequency}Hz")
    
    def start(self, duty_cycle: float = None):
        """
        启动 PWM 输出
        
        Args:
            duty_cycle: 占空比 (0-100%)
        """
        if self.running:
            logger.warning("PWM 已在运行")
            return False
        
        if duty_cycle is not None:
            self.set_duty_cycle(duty_cycle)
        
        self.running = True
        self.pulse_count = 0
        self.thread = threading.Thread(target=self._pwm_loop, daemon=True)
        self.thread.start()
        
        logger.info(f"PWM 启动: 占空比={self.duty_cycle}%")
        return True
    
    def stop(self):
        """停止 PWM 输出"""
        if not self.running:
            logger.warning("PWM 未在运行")
            return False
        
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None
        
        # 设置引脚为低电平
        self.gpio.low()
        
        logger.info(f"PWM 停止: 总脉冲数={self.pulse_count}")
        return True
    
    def set_duty_cycle(self, duty_cycle: float):
        """
        设置占空比
        
        Args:
            duty_cycle: 占空比 (0-100%)
        """
        if not (0.0 <= duty_cycle <= 100.0):
            raise ValueError("占空比必须在 0-100% 范围内")
        
        old_duty = self.duty_cycle
        self.duty_cycle = duty_cycle
        
        if old_duty != duty_cycle:
            logger.debug(f"占空比变更: {old_duty}% → {duty_cycle}%")
    
    def set_frequency(self, frequency: float):
        """
        设置频率
        
        Args:
            frequency: 频率 (Hz)
        """
        if frequency <= 0:
            raise ValueError("频率必须大于 0")
        
        old_freq = self.frequency
        self.frequency = frequency
        self.period = 1.0 / frequency
        
        logger.debug(f"频率变更: {old_freq}Hz → {frequency}Hz")
    
    def _pwm_loop(self):
        """PWM 生成循环"""
        while self.running:
            if self.duty_cycle > 0:
                # 计算高电平和低电平时间
                on_time = self.period * (self.duty_cycle / 100.0)
                off_time = self.period - on_time
                
                # 输出高电平
                if self.invert_logic:
                    self.gpio.low()
                else:
                    self.gpio.high()
                
                time.sleep(on_time)
                
                # 输出低电平
                if self.invert_logic:
                    self.gpio.high()
                else:
                    self.gpio.low()
                
                time.sleep(off_time)
                
                self.pulse_count += 1
                
                # 每100个脉冲打印一次状态
                if self.pulse_count % 100 == 0:
                    logger.debug(f"已发送 {self.pulse_count} 个脉冲，占空比: {self.duty_cycle}%")
            else:
                # 占空比为0时，保持低电平
                if self.invert_logic:
                    self.gpio.high()
                else:
                    self.gpio.low()
                time.sleep(self.period)
    
    def get_status(self) -> dict:
        """获取状态信息"""
        return {
            'pin': self.pin,
            'frequency': self.frequency,
            'duty_cycle': self.duty_cycle,
            'running': self.running,
            'pulse_count': self.pulse_count,
            'period': self.period
        }
    
    def cleanup(self):
        """清理资源"""
        self.stop()
        self.gpio.cleanup()
        logger.info("软件 PWM 清理完成")
    
    @contextmanager
    def context(self):
        """上下文管理器"""
        try:
            yield self
        finally:
            self.cleanup()
    
    def __str__(self):
        return f"SoftwarePWM(pin={self.pin}, freq={self.frequency}Hz, duty={self.duty_cycle}%)"


# 便捷函数
def create_gpio(pin: int, **kwargs) -> GPIOControl:
    """创建 GPIO 控制器"""
    return GPIOControl(pin, **kwargs)


def create_pwm(pin: int, frequency: float = 1000.0, **kwargs) -> SoftwarePWM:
    """创建软件 PWM 控制器"""
    return SoftwarePWM(pin, frequency, **kwargs)
