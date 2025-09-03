#!/usr/bin/env python3
"""
LED 亮度控制类

基于 PWM 控制实现 LED 亮度调节功能，提供：
- LED 亮度控制 (0-100%)
- 渐变效果
- 闪烁模式
- 呼吸灯效果

使用示例:
    led = LEDControl(pin=33)
    led.on()
    led.set_brightness(75)  # 75% 亮度
    led.fade_to(25, duration=2)  # 2秒内渐变到25%亮度
    led.off()

或使用上下文管理器:
    with LEDControl(pin=33) as led:
        led.on()
        led.blink(times=5, interval=0.5)
"""

import time
import threading
import logging
import os
import sys
from typing import Optional, Callable

# 添加源代码路径以支持直接运行
if __name__ == '__main__' or 'jetson.led_control' not in sys.modules:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pwm_control import PWMControl
else:
    from .pwm_control import PWMControl

# 配置日志
logger = logging.getLogger(__name__)


class LEDControl:
    """
    LED 亮度控制类
    
    基于 PWM 控制实现 LED 亮度调节和特效。
    """
    
    def __init__(self, pin: int, frequency: int = 1000, max_brightness: float = 100.0, invert_logic: bool = False):
        """
        初始化 LED 控制器
        
        Args:
            pin: GPIO 引脚号
            frequency: PWM 频率 (Hz)，默认 1000Hz
            max_brightness: 最大亮度限制 (0-100%)，默认 100%
            invert_logic: 是否使用反向逻辑，默认 False
                         True: 高电平=LED灭，低电平=LED亮
                         False: 高电平=LED亮，低电平=LED灭
            
        Raises:
            ValueError: 引脚号、频率或最大亮度无效
        """
        # 验证最大亮度
        if not (0 <= max_brightness <= 100):
            raise ValueError(f"Invalid max_brightness {max_brightness}%. Range: 0-100%")
        
        self.pin = pin
        self.frequency = frequency
        self.max_brightness = max_brightness
        self.invert_logic = invert_logic
        self.current_brightness = 0.0
        self.is_on = False
        
        # 创建 PWM 控制器
        self._pwm_control = PWMControl(pin=pin, frequency=frequency, invert_logic=invert_logic)
        
        # 动画控制
        self._animation_thread: Optional[threading.Thread] = None
        self._stop_animation = threading.Event()
        
        logic_desc = "反向逻辑" if invert_logic else "正向逻辑"
        logger.info(f"LED Controller initialized: Pin={pin}, Freq={frequency}Hz, MaxBrightness={max_brightness}%, {logic_desc}")
    
    def on(self, brightness: Optional[float] = None) -> bool:
        """
        打开 LED
        
        Args:
            brightness: 亮度 (0-100%)，默认使用当前亮度或最大亮度
            
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        if brightness is None:
            brightness = self.current_brightness if self.current_brightness > 0 else self.max_brightness
        
        if not self._pwm_control.is_started:
            if not self._pwm_control.start():
                logger.error("Failed to start PWM for LED")
                return False
        
        success = self.set_brightness(brightness)
        if success:
            self.is_on = True
            logger.info(f"LED turned on: Brightness={brightness}%")
        
        return success
    
    def off(self) -> bool:
        """
        关闭 LED
        
        Returns:
            bool: 成功返回 True，失败返回 False
        """
        # 停止任何正在进行的动画
        self.stop_animation()
        
        success = self.set_brightness(0)
        if success:
            self.is_on = False
            logger.info("LED turned off")
        
        return success
    
    def set_brightness(self, brightness: float) -> bool:
        """
        设置 LED 亮度
        
        Args:
            brightness: 亮度 (0-100%)
            
        Returns:
            bool: 设置成功返回 True，失败返回 False
        """
        # 验证亮度范围
        if not (0 <= brightness <= 100):
            logger.error(f"Invalid brightness {brightness}%. Range: 0-100%")
            return False
        
        # 限制最大亮度
        actual_brightness = min(brightness, self.max_brightness)
        
        # 确保 PWM 已启动
        if not self._pwm_control.is_started:
            if not self._pwm_control.start():
                logger.error("Failed to start PWM for brightness control")
                return False
        
        # 设置 PWM 占空比
        success = self._pwm_control.set_duty_cycle(actual_brightness)
        if success:
            self.current_brightness = actual_brightness
            logger.debug(f"LED brightness set to {actual_brightness}%")
        
        return success
    
    def get_brightness(self) -> float:
        """
        获取当前 LED 亮度
        
        Returns:
            float: 当前亮度 (0-100%)
        """
        return self.current_brightness
    
    def fade_to(self, target_brightness: float, duration: float = 1.0, steps: int = 50) -> bool:
        """
        渐变到目标亮度
        
        Args:
            target_brightness: 目标亮度 (0-100%)
            duration: 渐变时间 (秒)
            steps: 渐变步数
            
        Returns:
            bool: 启动成功返回 True，失败返回 False
        """
        # 验证参数
        if not (0 <= target_brightness <= 100):
            logger.error(f"Invalid target brightness {target_brightness}%. Range: 0-100%")
            return False
        
        if duration <= 0 or steps <= 0:
            logger.error("Duration and steps must be positive")
            return False
        
        # 停止当前动画
        self.stop_animation()
        
        # 启动渐变动画
        self._animation_thread = threading.Thread(
            target=self._fade_animation,
            args=(target_brightness, duration, steps),
            daemon=True
        )
        self._stop_animation.clear()
        self._animation_thread.start()
        
        logger.info(f"Started fade animation: {self.current_brightness}% -> {target_brightness}% in {duration}s")
        return True
    
    def _fade_animation(self, target_brightness: float, duration: float, steps: int) -> None:
        """
        渐变动画实现
        
        Args:
            target_brightness: 目标亮度
            duration: 渐变时间
            steps: 渐变步数
        """
        start_brightness = self.current_brightness
        brightness_step = (target_brightness - start_brightness) / steps
        time_step = duration / steps
        
        for i in range(steps + 1):
            if self._stop_animation.is_set():
                break
            
            current = start_brightness + brightness_step * i
            self.set_brightness(current)
            
            if i < steps:  # 最后一步不需要等待
                time.sleep(time_step)
    
    def blink(self, times: int = 1, on_time: float = 0.5, off_time: float = 0.5, 
              brightness: Optional[float] = None) -> bool:
        """
        LED 闪烁
        
        Args:
            times: 闪烁次数
            on_time: 点亮时间 (秒)
            off_time: 熄灭时间 (秒)
            brightness: 闪烁亮度，默认使用最大亮度
            
        Returns:
            bool: 启动成功返回 True，失败返回 False
        """
        if times <= 0 or on_time <= 0 or off_time <= 0:
            logger.error("Times, on_time and off_time must be positive")
            return False
        
        if brightness is None:
            brightness = self.max_brightness
        
        # 停止当前动画
        self.stop_animation()
        
        # 启动闪烁动画
        self._animation_thread = threading.Thread(
            target=self._blink_animation,
            args=(times, on_time, off_time, brightness),
            daemon=True
        )
        self._stop_animation.clear()
        self._animation_thread.start()
        
        logger.info(f"Started blink animation: {times} times, on={on_time}s, off={off_time}s, brightness={brightness}%")
        return True
    
    def _blink_animation(self, times: int, on_time: float, off_time: float, brightness: float) -> None:
        """
        闪烁动画实现
        
        Args:
            times: 闪烁次数
            on_time: 点亮时间
            off_time: 熄灭时间
            brightness: 闪烁亮度
        """
        original_brightness = self.current_brightness
        
        for _ in range(times):
            if self._stop_animation.is_set():
                break
            
            # 点亮
            self.set_brightness(brightness)
            if self._stop_animation.wait(on_time):
                break
            
            # 熄灭
            self.set_brightness(0)
            if self._stop_animation.wait(off_time):
                break
        
        # 恢复原始亮度
        if not self._stop_animation.is_set():
            self.set_brightness(original_brightness)
    
    def breathe(self, period: float = 2.0, min_brightness: float = 0.0, 
                max_brightness: Optional[float] = None) -> bool:
        """
        呼吸灯效果
        
        Args:
            period: 呼吸周期 (秒)
            min_brightness: 最小亮度 (0-100%)
            max_brightness: 最大亮度 (0-100%)，默认使用设定的最大亮度
            
        Returns:
            bool: 启动成功返回 True，失败返回 False
        """
        if period <= 0:
            logger.error("Period must be positive")
            return False
        
        if not (0 <= min_brightness <= 100):
            logger.error(f"Invalid min_brightness {min_brightness}%. Range: 0-100%")
            return False
        
        if max_brightness is None:
            max_brightness = self.max_brightness
        
        if not (0 <= max_brightness <= 100) or max_brightness < min_brightness:
            logger.error(f"Invalid max_brightness {max_brightness}%. Must be >= min_brightness")
            return False
        
        # 停止当前动画
        self.stop_animation()
        
        # 启动呼吸动画
        self._animation_thread = threading.Thread(
            target=self._breathe_animation,
            args=(period, min_brightness, max_brightness),
            daemon=True
        )
        self._stop_animation.clear()
        self._animation_thread.start()
        
        logger.info(f"Started breathe animation: period={period}s, range={min_brightness}%-{max_brightness}%")
        return True
    
    def _breathe_animation(self, period: float, min_brightness: float, max_brightness: float) -> None:
        """
        呼吸灯动画实现
        
        Args:
            period: 呼吸周期
            min_brightness: 最小亮度
            max_brightness: 最大亮度
        """
        import math
        
        steps_per_second = 50  # 50 FPS
        time_step = 1.0 / steps_per_second
        brightness_range = max_brightness - min_brightness
        
        start_time = time.time()
        
        while not self._stop_animation.is_set():
            elapsed = time.time() - start_time
            # 使用正弦波生成呼吸效果
            phase = (elapsed % period) / period * 2 * math.pi
            brightness = min_brightness + brightness_range * (math.sin(phase) + 1) / 2
            
            self.set_brightness(brightness)
            
            if self._stop_animation.wait(time_step):
                break
    
    def stop_animation(self) -> None:
        """
        停止当前动画
        """
        if self._animation_thread and self._animation_thread.is_alive():
            self._stop_animation.set()
            self._animation_thread.join(timeout=1.0)
            
            if self._animation_thread.is_alive():
                logger.warning("Animation thread did not stop gracefully")
            else:
                logger.debug("Animation stopped")
    
    def get_status(self) -> dict:
        """
        获取 LED 状态信息
        
        Returns:
            dict: 包含 LED 状态的字典
        """
        return {
            'pin': self.pin,
            'frequency': self.frequency,
            'max_brightness': self.max_brightness,
            'current_brightness': self.current_brightness,
            'is_on': self.is_on,
            'is_animating': self._animation_thread is not None and self._animation_thread.is_alive(),
            'pwm_status': self._pwm_control.get_status(),
        }
    
    def cleanup(self) -> None:
        """
        清理资源
        
        停止所有动画并释放 PWM 资源。
        """
        try:
            # 停止动画
            self.stop_animation()
            
            # 关闭 LED
            self.off()
            
            # 清理 PWM 资源
            self._pwm_control.cleanup()
            
            logger.info("LED Controller resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup LED Controller: {e}")
    
    def __enter__(self):
        """
        上下文管理器入口
        
        Returns:
            LEDControl: 当前实例
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
            str: LED 控制器状态描述
        """
        status = "On" if self.is_on else "Off"
        animating = "Animating" if (self._animation_thread and self._animation_thread.is_alive()) else "Static"
        return (
            f"LEDControl(pin={self.pin}, brightness={self.current_brightness}%, "
            f"status={status}, mode={animating})"
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
    
    print("LED Control Test")
    print("=================")
    
    try:
        # 创建 LED 控制器
        with LEDControl(pin=33, max_brightness=80) as led:
            print(f"Created: {led}")
            
            # 基本控制测试
            print("\n1. Basic Control Test")
            led.on(50)  # 50% 亮度
            print(f"LED on at 50%: {led.get_brightness()}%")
            time.sleep(2)
            
            led.set_brightness(100)  # 最大亮度
            print(f"LED at max brightness: {led.get_brightness()}%")
            time.sleep(2)
            
            led.off()
            print("LED off")
            time.sleep(1)
            
            # 渐变测试
            print("\n2. Fade Test")
            led.on(0)
            led.fade_to(80, duration=3)
            time.sleep(4)
            
            led.fade_to(20, duration=2)
            time.sleep(3)
            
            # 闪烁测试
            print("\n3. Blink Test")
            led.blink(times=5, on_time=0.3, off_time=0.3, brightness=60)
            time.sleep(4)
            
            # 呼吸灯测试
            print("\n4. Breathe Test")
            led.breathe(period=3.0, min_brightness=10, max_brightness=70)
            time.sleep(10)
            
            led.stop_animation()
            led.off()
            
            print("\nTest completed successfully")
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()