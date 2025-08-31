#!/usr/bin/env python3
"""
测试引脚的简单脚本
强制重新加载模块以确保使用最新代码
"""

import sys
import os

# 清除相关模块缓存
modules_to_remove = [k for k in sys.modules.keys() if k.startswith('jetson')]
for module in modules_to_remove:
    del sys.modules[module]

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 重新导入
from jetson.pwm_control import PWMControl

print(f"当前有效引脚列表: {PWMControl.VALID_PINS}")

# 测试引脚 33
try:
    print("\n测试引脚 33...")
    pwm = PWMControl(pin=33)
    print("引脚 33 验证通过！")
    
    # 尝试启动
    if pwm.start():
        print("PWM 启动成功！")
        pwm.set_duty_cycle(100)
        print("LED 应该已经点亮！")
        
        import time
        time.sleep(2)
        
        pwm.set_duty_cycle(0)
        print("LED 应该已经熄灭！")
        
        pwm.stop()
        pwm.cleanup()
        print("测试完成！")
    else:
        print("PWM 启动失败")
        
except Exception as e:
    print(f"错误: {e}")