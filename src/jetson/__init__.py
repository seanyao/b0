#!/usr/bin/env python3
"""
Jetson Orin PWM LED 控制包

提供 PWM 控制和 LED 亮度调节功能。
"""

__version__ = '1.0.0'
__author__ = 'Jetson PWM Project'
__description__ = 'Jetson Orin PWM LED Control Library'

# 导入主要类
from .pwm_control import PWMControl
from .led_control import LEDControl

__all__ = [
    'PWMControl',
    'LEDControl',
]