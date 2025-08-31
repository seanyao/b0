#!/usr/bin/env python3
"""
PWM 控制类单元测试

遵循 TDD 原则，先定义测试用例，再实现功能。
测试覆盖 PWM 控制的核心功能：初始化、设置占空比、频率控制等。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestPWMControl:
    """PWM 控制类测试套件"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # Mock Jetson.GPIO 模块，避免在非 Jetson 环境下运行失败
        self.gpio_mock = Mock()
        self.pwm_mock = Mock()
        
        # 模拟 GPIO 模块的行为
        self.gpio_mock.PWM.return_value = self.pwm_mock
        self.gpio_mock.OUT = 'OUT'
        self.gpio_mock.BCM = 'BCM'
        
        # 将 mock 对象注入到模块中
        sys.modules['Jetson.GPIO'] = self.gpio_mock
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理模块缓存
        if 'jetson.pwm_control' in sys.modules:
            del sys.modules['jetson.pwm_control']
        if 'Jetson.GPIO' in sys.modules:
            del sys.modules['Jetson.GPIO']
    
    def test_pwm_control_initialization(self):
        """测试 PWM 控制器初始化"""
        from jetson.pwm_control import PWMControl
        
        # 测试默认参数初始化
        pwm_control = PWMControl(pin=33)
        
        assert pwm_control.pin == 33
        assert pwm_control.frequency == 1000  # 默认频率 1kHz
        assert pwm_control.duty_cycle == 0    # 默认占空比 0%
        assert not pwm_control.is_started     # 初始状态未启动
        
        # 验证 GPIO 设置调用
        self.gpio_mock.setmode.assert_called_once_with(self.gpio_mock.BCM)
        self.gpio_mock.setup.assert_called_once_with(33, self.gpio_mock.OUT)
    
    def test_pwm_control_custom_initialization(self):
        """测试自定义参数初始化"""
        from jetson.pwm_control import PWMControl
        
        # 测试自定义参数
        pwm_control = PWMControl(pin=32, frequency=2000)
        
        assert pwm_control.pin == 32
        assert pwm_control.frequency == 2000
        assert pwm_control.duty_cycle == 0
        assert not pwm_control.is_started
    
    def test_pwm_start(self):
        """测试 PWM 启动功能"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        
        # 测试启动 PWM
        result = pwm_control.start()
        
        assert result is True
        assert pwm_control.is_started is True
        
        # 验证 PWM 对象创建和启动
        self.gpio_mock.PWM.assert_called_once_with(33, 1000)
        self.pwm_mock.start.assert_called_once_with(0)
    
    def test_pwm_start_already_started(self):
        """测试重复启动 PWM"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试重复启动
        result = pwm_control.start()
        
        assert result is False  # 应该返回 False 表示已经启动
        assert pwm_control.is_started is True
    
    def test_pwm_stop(self):
        """测试 PWM 停止功能"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试停止 PWM
        result = pwm_control.stop()
        
        assert result is True
        assert pwm_control.is_started is False
        
        # 验证 PWM 停止调用
        self.pwm_mock.stop.assert_called_once()
    
    def test_pwm_stop_not_started(self):
        """测试停止未启动的 PWM"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        
        # 测试停止未启动的 PWM
        result = pwm_control.stop()
        
        assert result is False  # 应该返回 False 表示未启动
        assert pwm_control.is_started is False
    
    def test_set_duty_cycle_valid_range(self):
        """测试设置有效范围的占空比"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试有效占空比值
        test_values = [0, 25, 50, 75, 100]
        
        for duty_cycle in test_values:
            result = pwm_control.set_duty_cycle(duty_cycle)
            
            assert result is True
            assert pwm_control.duty_cycle == duty_cycle
            
        # 验证 PWM 占空比设置调用
        expected_calls = [((value,), {}) for value in test_values]
        assert self.pwm_mock.ChangeDutyCycle.call_args_list == expected_calls
    
    def test_set_duty_cycle_invalid_range(self):
        """测试设置无效范围的占空比"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试无效占空比值
        invalid_values = [-1, -10, 101, 150]
        
        for duty_cycle in invalid_values:
            result = pwm_control.set_duty_cycle(duty_cycle)
            
            assert result is False
            assert pwm_control.duty_cycle == 0  # 应该保持原值
    
    def test_set_duty_cycle_not_started(self):
        """测试在未启动状态下设置占空比"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        
        # 测试未启动时设置占空比
        result = pwm_control.set_duty_cycle(50)
        
        assert result is False
        assert pwm_control.duty_cycle == 0
    
    def test_set_frequency_valid_range(self):
        """测试设置有效范围的频率"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试有效频率值
        test_values = [100, 1000, 5000, 10000]
        
        for frequency in test_values:
            result = pwm_control.set_frequency(frequency)
            
            assert result is True
            assert pwm_control.frequency == frequency
            
        # 验证 PWM 频率设置调用
        expected_calls = [((value,), {}) for value in test_values]
        assert self.pwm_mock.ChangeFrequency.call_args_list == expected_calls
    
    def test_set_frequency_invalid_range(self):
        """测试设置无效范围的频率"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试无效频率值
        invalid_values = [0, -100, 50001, 100000]
        
        for frequency in invalid_values:
            result = pwm_control.set_frequency(frequency)
            
            assert result is False
            assert pwm_control.frequency == 1000  # 应该保持原值
    
    def test_cleanup(self):
        """测试资源清理"""
        from jetson.pwm_control import PWMControl
        
        pwm_control = PWMControl(pin=33)
        pwm_control.start()
        
        # 测试清理资源
        pwm_control.cleanup()
        
        assert pwm_control.is_started is False
        
        # 验证清理调用
        self.pwm_mock.stop.assert_called()
        self.gpio_mock.cleanup.assert_called_once()
    
    def test_context_manager(self):
        """测试上下文管理器功能"""
        from jetson.pwm_control import PWMControl
        
        # 测试 with 语句
        with PWMControl(pin=33) as pwm_control:
            assert pwm_control.pin == 33
            pwm_control.start()
            assert pwm_control.is_started is True
        
        # 验证自动清理
        self.gpio_mock.cleanup.assert_called()
    
    def test_pin_validation(self):
        """测试引脚号验证"""
        from jetson.pwm_control import PWMControl
        
        # 测试有效引脚号
        valid_pins = [32, 33, 35, 37]
        for pin in valid_pins:
            pwm_control = PWMControl(pin=pin)
            assert pwm_control.pin == pin
        
        # 测试无效引脚号
        invalid_pins = [0, 1, 100, -1]
        for pin in invalid_pins:
            with pytest.raises(ValueError, match="Invalid GPIO pin"):
                PWMControl(pin=pin)
    
    def test_frequency_validation(self):
        """测试频率参数验证"""
        from jetson.pwm_control import PWMControl
        
        # 测试有效频率
        valid_frequencies = [100, 1000, 5000, 10000]
        for freq in valid_frequencies:
            pwm_control = PWMControl(pin=33, frequency=freq)
            assert pwm_control.frequency == freq
        
        # 测试无效频率
        invalid_frequencies = [0, -100, 50001]
        for freq in invalid_frequencies:
            with pytest.raises(ValueError, match="Invalid frequency"):
                PWMControl(pin=33, frequency=freq)


class TestPWMControlIntegration:
    """PWM 控制集成测试"""
    
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
        if 'jetson.pwm_control' in sys.modules:
            del sys.modules['jetson.pwm_control']
        if 'Jetson.GPIO' in sys.modules:
            del sys.modules['Jetson.GPIO']
    
    def test_complete_pwm_workflow(self):
        """测试完整的 PWM 工作流程"""
        from jetson.pwm_control import PWMControl
        
        # 创建 PWM 控制器
        pwm_control = PWMControl(pin=33, frequency=2000)
        
        # 启动 PWM
        assert pwm_control.start() is True
        
        # 设置不同的占空比
        duty_cycles = [0, 25, 50, 75, 100]
        for duty_cycle in duty_cycles:
            assert pwm_control.set_duty_cycle(duty_cycle) is True
            assert pwm_control.duty_cycle == duty_cycle
        
        # 改变频率
        assert pwm_control.set_frequency(5000) is True
        assert pwm_control.frequency == 5000
        
        # 停止 PWM
        assert pwm_control.stop() is True
        
        # 清理资源
        pwm_control.cleanup()
        
        # 验证所有调用
        self.gpio_mock.setmode.assert_called_with(self.gpio_mock.BCM)
        self.gpio_mock.setup.assert_called_with(33, self.gpio_mock.OUT)
        self.gpio_mock.PWM.assert_called_with(33, 2000)
        self.pwm_mock.start.assert_called_with(0)
        self.pwm_mock.stop.assert_called()
        self.gpio_mock.cleanup.assert_called()


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v'])