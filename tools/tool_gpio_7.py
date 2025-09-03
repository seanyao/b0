#!/usr/bin/env python3
"""
GPIO 测试工具 - 验证 GPIO Pin 7 的基本功能
使用新的 GPIOControl 类
"""

import sys
import os
import time

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gpio_control import GPIOControl

def main():
    print("=== GPIO 基本功能测试 ===")
    print("连接: GPIO Pin 7 → LED (通过 330Ω 电阻) → GND")
    print("")
    
    try:
        # 创建 GPIO 控制器
        gpio = GPIOControl(pin=7, mode='BOARD', direction='OUT', initial='LOW')
        print(f"✅ GPIO 控制器创建成功: {gpio}")
        
        print("\n开始测试 GPIO 开关功能...")
        print("按 Ctrl+C 停止测试")
        
        while True:
            # 输出高电平
            gpio.high()
            print("GPIO07 = HIGH")
            time.sleep(5)
            
            # 输出低电平
            gpio.low()
            print("GPIO07 = LOW")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
    finally:
        # 清理资源
        if 'gpio' in locals():
            gpio.cleanup()
        print("🧹 GPIO 资源已清理")

if __name__ == "__main__":
    main()
