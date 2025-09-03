#!/usr/bin/env python3
"""
LED PWM 测试 - 验证 GPIO Pin 7 的 PWM 信号
使用新的 SoftwarePWM 类
"""

import sys
import os
import time

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gpio_control import SoftwarePWM

def main():
    print("=== LED PWM 信号测试 ===")
    print("连接: GPIO Pin 7 → 330Ω电阻 → LED正极 → LED负极 → GND")
    print("")
    
    try:
        # 创建软件 PWM 控制器
        pwm = SoftwarePWM(pin=7, frequency=50, mode='BOARD')  # 50Hz，和舵机一样
        print(f"✅ PWM 控制器创建成功: {pwm}")
        
        print("\n1. 测试基本 PWM 功能...")
        
        # 测试不同占空比
        duty_cycles = [10, 25, 50, 75, 100]
        
        for duty in duty_cycles:
            print(f"\n--- 设置占空比: {duty}% ---")
            pwm.start(duty)
            time.sleep(3)  # 观察3秒
            pwm.stop()
            time.sleep(1)
        
        print("\n2. 测试舵机频率 PWM (50Hz)...")
        
        # 测试舵机相关的占空比范围
        servo_duties = [5.0, 7.5, 10.0]  # 对应舵机的 0°, 90°, 180°
        
        for duty in servo_duties:
            print(f"\n--- 舵机占空比: {duty}% ---")
            pwm.start(duty)
            time.sleep(3)
            pwm.stop()
            time.sleep(1)
        
        print("\n3. 连续变化测试...")
        pwm.start(0)
        
        # 从暗到亮再到暗
        for i in range(101):
            pwm.set_duty_cycle(i)
            time.sleep(0.05)
        
        for i in range(100, -1, -1):
            pwm.set_duty_cycle(i)
            time.sleep(0.05)
        
        pwm.stop()
        
        print("\n=== 测试结果分析 ===")
        print("如果 LED 能够：")
        print("✅ 在不同占空比下显示不同亮度")
        print("✅ 平滑地从暗变亮再变暗")
        print("✅ 在 5%-10% 占空比下有可见的亮度变化")
        print("")
        print("那么 PWM 信号是正常的！")
        print("舵机不动的问题可能是：")
        print("1. 舵机需要 5V 信号电平（当前是 3.3V）")
        print("2. 舵机损坏")
        print("3. 舵机参数不匹配")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
    finally:
        # 清理资源
        if 'pwm' in locals():
            pwm.cleanup()
        print("🧹 PWM 资源已清理")

if __name__ == "__main__":
    main()