#!/usr/bin/env python3
"""
LED 控制类集成测试

测试 LED 亮度控制、动画效果等功能。
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLEDControl:
    """LED 控制类测试套件"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # Mock Jetson.GPIO 模块
        self.gpio_mock = Mock()
        self.pwm_mock = Mock()
        
        self.gpio_mock.PWM.return_value = self.pwm_mock
        self.gpio_mock.OUT = 'OUT'
        self.gpio_mock.BCM = 'BCM'
        
        sys.modules['Jetson.GPIO'] = self.gpio_mock
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理模块缓存
        modules_to_remove = [
            'jetson.led_control',
            'jetson.pwm_control', 
            'Jetson.GPIO'
        ]
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
    
    def test_led_control_initialization(self):
        """测试 LED 控制器初始化"""
        from jetson.led_control import LEDControl
        
        # 测试默认参数初始化
        led = LEDControl(pin=33)
        
        assert led.pin == 33
        assert led.frequency == 1000
        assert led.max_brightness == 100.0
        assert led.current_brightness == 0.0
        assert not led.is_on
    
    def test_led_control_custom_initialization(self):
        """测试自定义参数初始化"""
        from jetson.led_control import LEDControl
        
        # 测试自定义参数
        led = LEDControl(pin=32, frequency=2000, max_brightness=80.0)
        
        assert led.pin == 32
        assert led.frequency == 2000
        assert led.max_brightness == 80.0
        assert led.current_brightness == 0.0
        assert not led.is_on
    
    def test_led_control_invalid_max_brightness(self):
        """测试无效最大亮度参数"""
        from jetson.led_control import LEDControl
        
        # 测试无效最大亮度
        with pytest.raises(ValueError, match="Invalid max_brightness"):
            LEDControl(pin=33, max_brightness=150)
        
        with pytest.raises(ValueError, match="Invalid max_brightness"):
            LEDControl(pin=33, max_brightness=-10)
    
    def test_led_on_off(self):
        """测试 LED 开关功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33, max_brightness=80)
        
        # 测试打开 LED
        result = led.on()
        assert result is True
        assert led.is_on is True
        assert led.current_brightness == 80.0  # 默认使用最大亮度
        
        # 测试关闭 LED
        result = led.off()
        assert result is True
        assert led.is_on is False
        assert led.current_brightness == 0.0
    
    def test_led_on_with_brightness(self):
        """测试指定亮度打开 LED"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 测试指定亮度打开
        result = led.on(brightness=50)
        assert result is True
        assert led.is_on is True
        assert led.current_brightness == 50.0
    
    def test_set_brightness_valid_range(self):
        """测试设置有效范围的亮度"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        led.on()
        
        # 测试有效亮度值
        test_values = [0, 25, 50, 75, 100]
        
        for brightness in test_values:
            result = led.set_brightness(brightness)
            assert result is True
            assert led.current_brightness == brightness
    
    def test_set_brightness_invalid_range(self):
        """测试设置无效范围的亮度"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        led.on()
        
        original_brightness = led.current_brightness
        
        # 测试无效亮度值
        invalid_values = [-1, -10, 101, 150]
        
        for brightness in invalid_values:
            result = led.set_brightness(brightness)
            assert result is False
            assert led.current_brightness == original_brightness
    
    def test_brightness_limit(self):
        """测试亮度限制功能"""
        from jetson.led_control import LEDControl
        
        # 设置最大亮度为 80%
        led = LEDControl(pin=33, max_brightness=80)
        led.on()
        
        # 尝试设置超过限制的亮度
        result = led.set_brightness(100)
        assert result is True
        assert led.current_brightness == 80.0  # 应该被限制到最大值
    
    def test_get_brightness(self):
        """测试获取亮度功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 初始亮度应该为 0
        assert led.get_brightness() == 0.0
        
        # 设置亮度后检查
        led.on(60)
        assert led.get_brightness() == 60.0
    
    def test_fade_to_valid_parameters(self):
        """测试有效参数的渐变功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        led.on(0)
        
        # 测试渐变到目标亮度
        result = led.fade_to(target_brightness=80, duration=0.1, steps=5)
        assert result is True
        
        # 等待渐变完成
        time.sleep(0.2)
        
        # 检查最终亮度
        assert abs(led.current_brightness - 80.0) < 1.0
        
        # 清理
        led.stop_animation()
    
    def test_fade_to_invalid_parameters(self):
        """测试无效参数的渐变功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        led.on()
        
        # 测试无效目标亮度
        result = led.fade_to(target_brightness=150)
        assert result is False
        
        # 测试无效持续时间
        result = led.fade_to(target_brightness=50, duration=-1)
        assert result is False
        
        # 测试无效步数
        result = led.fade_to(target_brightness=50, duration=1, steps=0)
        assert result is False
    
    def test_blink_valid_parameters(self):
        """测试有效参数的闪烁功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 测试闪烁
        result = led.blink(times=2, on_time=0.05, off_time=0.05, brightness=50)
        assert result is True
        
        # 等待闪烁完成
        time.sleep(0.3)
        
        # 清理
        led.stop_animation()
    
    def test_blink_invalid_parameters(self):
        """测试无效参数的闪烁功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 测试无效次数
        result = led.blink(times=0)
        assert result is False
        
        # 测试无效时间
        result = led.blink(times=1, on_time=-1)
        assert result is False
        
        result = led.blink(times=1, on_time=0.5, off_time=0)
        assert result is False
    
    def test_breathe_valid_parameters(self):
        """测试有效参数的呼吸灯功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 测试呼吸灯
        result = led.breathe(period=0.2, min_brightness=10, max_brightness=80)
        assert result is True
        
        # 运行一段时间
        time.sleep(0.3)
        
        # 检查亮度在范围内
        brightness = led.get_brightness()
        assert 10 <= brightness <= 80
        
        # 清理
        led.stop_animation()
    
    def test_breathe_invalid_parameters(self):
        """测试无效参数的呼吸灯功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 测试无效周期
        result = led.breathe(period=0)
        assert result is False
        
        # 测试无效最小亮度
        result = led.breathe(period=1, min_brightness=-10)
        assert result is False
        
        # 测试无效最大亮度
        result = led.breathe(period=1, min_brightness=20, max_brightness=10)
        assert result is False
    
    def test_stop_animation(self):
        """测试停止动画功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 启动呼吸灯
        led.breathe(period=1.0)
        time.sleep(0.1)  # 让动画开始
        
        # 停止动画
        led.stop_animation()
        
        # 检查动画是否停止
        time.sleep(0.1)
        assert not (led._animation_thread and led._animation_thread.is_alive())
    
    def test_get_status(self):
        """测试获取状态功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33, frequency=2000, max_brightness=90)
        led.on(60)
        
        status = led.get_status()
        
        assert status['pin'] == 33
        assert status['frequency'] == 2000
        assert status['max_brightness'] == 90
        assert status['current_brightness'] == 60
        assert status['is_on'] is True
        assert 'is_animating' in status
        assert 'pwm_status' in status
    
    def test_cleanup(self):
        """测试资源清理"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        led.on(50)
        led.breathe(period=1.0)  # 启动动画
        
        # 清理资源
        led.cleanup()
        
        # 检查状态
        assert led.current_brightness == 0.0
        assert not led.is_on
        assert not (led._animation_thread and led._animation_thread.is_alive())
    
    def test_context_manager(self):
        """测试上下文管理器功能"""
        from jetson.led_control import LEDControl
        
        # 测试 with 语句
        with LEDControl(pin=33) as led:
            assert led.pin == 33
            led.on(75)
            assert led.current_brightness == 75
        
        # 验证自动清理（通过 mock 验证）
        self.gpio_mock.cleanup.assert_called()
    
    def test_string_representation(self):
        """测试字符串表示"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        # 测试关闭状态
        str_repr = str(led)
        assert "pin=33" in str_repr
        assert "brightness=0" in str_repr
        assert "status=Off" in str_repr
        
        # 测试打开状态
        led.on(50)
        str_repr = str(led)
        assert "brightness=50" in str_repr
        assert "status=On" in str_repr


class TestLEDControlIntegration:
    """LED 控制集成测试"""
    
    def setup_method(self):
        """设置集成测试环境"""
        self.gpio_mock = Mock()
        self.pwm_mock = Mock()
        
        self.gpio_mock.PWM.return_value = self.pwm_mock
        self.gpio_mock.OUT = 'OUT'
        self.gpio_mock.BCM = 'BCM'
        
        sys.modules['Jetson.GPIO'] = self.gpio_mock
    
    def teardown_method(self):
        """清理集成测试环境"""
        modules_to_remove = [
            'jetson.led_control',
            'jetson.pwm_control',
            'Jetson.GPIO'
        ]
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
    
    def test_complete_led_workflow(self):
        """测试完整的 LED 控制工作流程"""
        from jetson.led_control import LEDControl
        
        # 创建 LED 控制器
        led = LEDControl(pin=33, frequency=1000, max_brightness=90)
        
        try:
            # 基本控制
            assert led.on(50) is True
            assert led.get_brightness() == 50
            
            # 亮度调节
            assert led.set_brightness(75) is True
            assert led.get_brightness() == 75
            
            # 渐变效果
            assert led.fade_to(25, duration=0.1) is True
            time.sleep(0.15)
            assert abs(led.get_brightness() - 25) < 5
            
            # 闪烁效果
            assert led.blink(times=2, on_time=0.05, off_time=0.05) is True
            time.sleep(0.25)
            
            # 呼吸灯效果
            assert led.breathe(period=0.2, min_brightness=10, max_brightness=80) is True
            time.sleep(0.3)
            brightness = led.get_brightness()
            assert 10 <= brightness <= 80
            
            # 停止动画
            led.stop_animation()
            
            # 关闭 LED
            assert led.off() is True
            assert led.get_brightness() == 0
            
        finally:
            # 清理资源
            led.cleanup()
        
        # 验证 PWM 调用
        self.gpio_mock.setmode.assert_called_with(self.gpio_mock.BCM)
        self.gpio_mock.setup.assert_called_with(33, self.gpio_mock.OUT)
        self.gpio_mock.PWM.assert_called_with(33, 1000)
        self.pwm_mock.start.assert_called()
        self.gpio_mock.cleanup.assert_called()
    
    def test_animation_interruption(self):
        """测试动画中断功能"""
        from jetson.led_control import LEDControl
        
        led = LEDControl(pin=33)
        
        try:
            # 启动长时间呼吸灯
            led.breathe(period=2.0)
            time.sleep(0.1)  # 让动画开始
            
            # 启动闪烁（应该中断呼吸灯）
            led.blink(times=1, on_time=0.05, off_time=0.05)
            time.sleep(0.15)
            
            # 启动渐变（应该中断闪烁）
            led.fade_to(80, duration=0.1)
            time.sleep(0.15)
            
            # 检查最终状态
            assert abs(led.get_brightness() - 80) < 5
            
        finally:
            led.cleanup()


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])