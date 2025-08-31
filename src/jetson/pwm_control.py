#!/usr/bin/env python3
"""
PWM 控制核心类

提供 Jetson Orin GPIO PWM 控制功能，包括：
- PWM 初始化和配置
- 占空比控制 (0-100%)
- 频率调节 (100Hz-50kHz)
- 资源管理和清理

使用示例:
    pwm = PWMControl(pin=33, frequency=1000)
    pwm.start()
    pwm.set_duty_cycle(50)  # 50% 占空比
    pwm.stop()
    pwm.cleanup()

或使用上下文管理器:
    with PWMControl(pin=33) as pwm:
        pwm.start()
        pwm.set_duty_cycle(75)
"""

import logging
from typing import Optional

# 尝试导入 Jetson.GPIO，如果失败则使用 Mock
try:
    import Jetson.GPIO as GPIO
    # 测试是否可以正常使用
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
except (ImportError, RuntimeError, Exception):
    # 在非 Jetson 环境下或权限不足时使用 Mock 对象
    import warnings
    warnings.warn("Jetson.GPIO not available or insufficient permissions, using mock for development")
    
    class MockGPIO:
        """Mock GPIO 类，用于开发和测试"""
        BCM = 'BCM'
        OUT = 'OUT'
        
        @staticmethod
        def setmode(mode):
            pass
        
        @staticmethod
        def setup(pin, mode):
            pass
        
        @staticmethod
        def cleanup():
            pass
        
        class PWM:
            def __init__(self, pin, frequency):
                self.pin = pin
                self.frequency = frequency
            
            def start(self, duty_cycle):
                pass
            
            def stop(self):
                pass
            
            def ChangeDutyCycle(self, duty_cycle):
                pass
            
            def ChangeFrequency(self, frequency):
                pass
    
    GPIO = MockGPIO()


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PWMControl:
    """
    PWM 控制类
    
    提供 Jetson Orin GPIO PWM 控制功能。
    """
    
    # 支持的 GPIO 引脚 (Jetson Orin)
    VALID_PINS = [32, 33, 35, 37, 38, 40]
    
    # 频率范围 (Hz)
    MIN_FREQUENCY = 100
    MAX_FREQUENCY = 50000
    
    # 占空比范围 (%)
    MIN_DUTY_CYCLE = 0
    MAX_DUTY_CYCLE = 100
    
    def __init__(self, pin: int, frequency: int = 1000):
        """
        初始化 PWM 控制器
        
        Args:
            pin: GPIO 引脚号
            frequency: PWM 频率 (Hz)，默认 1000Hz
            
        Raises:
            ValueError: 引脚号或频率无效
        """
        # 验证引脚号
        if pin not in self.VALID_PINS:
            raise ValueError(f"Invalid GPIO pin {pin}. Valid pins: {self.VALID_PINS}")
        
        # 验证频率
        if not (self.MIN_FREQUENCY <= frequency <= self.MAX_FREQUENCY):
            raise ValueError(
                f"Invalid frequency {frequency}Hz. "
                f"Range: {self.MIN_FREQUENCY}-{self.MAX_FREQUENCY}Hz"
            )
        
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0
        self.is_started = False
        self._pwm_instance: Optional[GPIO.PWM] = None
        
        # 初始化 GPIO
        self._init_gpio()
        
        logger.info(f"PWM Controller initialized: Pin={pin}, Frequency={frequency}Hz")
    
    def _init_gpio(self) -> None:
        """
        初始化 GPIO 设置
        """
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.OUT)
            logger.debug(f"GPIO pin {self.pin} configured as output")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            raise
    
    def start(self) -> bool:
        """
        启动 PWM 输出
        
        Returns:
            bool: 成功返回 True，已启动返回 False
        """
        if self.is_started:
            logger.warning("PWM already started")
            return False
        
        try:
            self._pwm_instance = GPIO.PWM(self.pin, self.frequency)
            self._pwm_instance.start(self.duty_cycle)
            self.is_started = True
            
            logger.info(f"PWM started: Pin={self.pin}, Frequency={self.frequency}Hz, Duty={self.duty_cycle}%")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start PWM: {e}")
            return False
    
    def stop(self) -> bool:
        """
        停止 PWM 输出
        
        Returns:
            bool: 成功返回 True，未启动返回 False
        """
        if not self.is_started:
            logger.warning("PWM not started")
            return False
        
        try:
            if self._pwm_instance:
                self._pwm_instance.stop()
                self._pwm_instance = None
            
            self.is_started = False
            logger.info(f"PWM stopped: Pin={self.pin}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop PWM: {e}")
            return False
    
    def set_duty_cycle(self, duty_cycle: float) -> bool:
        """
        设置 PWM 占空比
        
        Args:
            duty_cycle: 占空比 (0-100%)
            
        Returns:
            bool: 设置成功返回 True，失败返回 False
        """
        # 检查 PWM 是否已启动
        if not self.is_started:
            logger.error("PWM not started. Call start() first.")
            return False
        
        # 验证占空比范围
        if not (self.MIN_DUTY_CYCLE <= duty_cycle <= self.MAX_DUTY_CYCLE):
            logger.error(
                f"Invalid duty cycle {duty_cycle}%. "
                f"Range: {self.MIN_DUTY_CYCLE}-{self.MAX_DUTY_CYCLE}%"
            )
            return False
        
        try:
            if self._pwm_instance:
                self._pwm_instance.ChangeDutyCycle(duty_cycle)
                self.duty_cycle = duty_cycle
                
                logger.debug(f"Duty cycle set to {duty_cycle}%")
                return True
            else:
                logger.error("PWM instance not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set duty cycle: {e}")
            return False
    
    def set_frequency(self, frequency: int) -> bool:
        """
        设置 PWM 频率
        
        Args:
            frequency: PWM 频率 (Hz)
            
        Returns:
            bool: 设置成功返回 True，失败返回 False
        """
        # 检查 PWM 是否已启动
        if not self.is_started:
            logger.error("PWM not started. Call start() first.")
            return False
        
        # 验证频率范围
        if not (self.MIN_FREQUENCY <= frequency <= self.MAX_FREQUENCY):
            logger.error(
                f"Invalid frequency {frequency}Hz. "
                f"Range: {self.MIN_FREQUENCY}-{self.MAX_FREQUENCY}Hz"
            )
            return False
        
        try:
            if self._pwm_instance:
                self._pwm_instance.ChangeFrequency(frequency)
                self.frequency = frequency
                
                logger.debug(f"Frequency set to {frequency}Hz")
                return True
            else:
                logger.error("PWM instance not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set frequency: {e}")
            return False
    
    def get_status(self) -> dict:
        """
        获取 PWM 状态信息
        
        Returns:
            dict: 包含 PWM 状态的字典
        """
        return {
            'pin': self.pin,
            'frequency': self.frequency,
            'duty_cycle': self.duty_cycle,
            'is_started': self.is_started,
        }
    
    def cleanup(self) -> None:
        """
        清理 GPIO 资源
        
        停止 PWM 并释放 GPIO 资源。
        """
        try:
            if self.is_started:
                self.stop()
            
            GPIO.cleanup()
            logger.info("GPIO resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup GPIO: {e}")
    
    def __enter__(self):
        """
        上下文管理器入口
        
        Returns:
            PWMControl: 当前实例
        """
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        
        自动清理资源。
        """
        self.cleanup()
    
    def __str__(self) -> str:
        """
        字符串表示
        
        Returns:
            str: PWM 控制器状态描述
        """
        status = "Started" if self.is_started else "Stopped"
        return (
            f"PWMControl(pin={self.pin}, freq={self.frequency}Hz, "
            f"duty={self.duty_cycle}%, status={status})"
        )
    
    def __repr__(self) -> str:
        """
        对象表示
        
        Returns:
            str: 对象的详细表示
        """
        return self.__str__()


if __name__ == '__main__':
    # 简单测试
    import time
    
    print("PWM Control Test")
    print("=================")
    
    try:
        # 创建 PWM 控制器
        with PWMControl(pin=33, frequency=1000) as pwm:
            print(f"Created: {pwm}")
            
            # 启动 PWM
            if pwm.start():
                print("PWM started successfully")
                
                # 测试不同占空比
                duty_cycles = [0, 25, 50, 75, 100]
                for duty in duty_cycles:
                    print(f"Setting duty cycle to {duty}%")
                    pwm.set_duty_cycle(duty)
                    time.sleep(1)
                
                # 测试频率变化
                frequencies = [500, 1000, 2000]
                for freq in frequencies:
                    print(f"Setting frequency to {freq}Hz")
                    pwm.set_frequency(freq)
                    pwm.set_duty_cycle(50)  # 50% 占空比
                    time.sleep(2)
                
                print("Test completed")
            else:
                print("Failed to start PWM")
                
    except Exception as e:
        print(f"Test failed: {e}")