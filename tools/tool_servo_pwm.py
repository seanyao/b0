#!/usr/bin/env python3
"""
舵机 PWM 测试 - 验证 GPIO Pin 7 的舵机控制信号
使用新的 SoftwarePWM 类
"""

import sys
import os
import time

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from gpio_control import SoftwarePWM

def main():
    print("=== 舵机 PWM 信号测试 ===")
    print("连接: GPIO Pin 7 → 舵机信号线")
    print("      5V/12V → 舵机电源线")
    print("      GND → 舵机地线")
    print("")
    
    try:
        # 创建软件 PWM 控制器
        pwm = SoftwarePWM(pin=7, frequency=50, mode='BOARD')  # 50Hz 舵机标准频率
        print(f"✅ PWM 控制器创建成功: {pwm}")
        
        print("\n开始测试舵机控制信号...")
        print("按 Ctrl+C 停止测试")
        
        # 测试不同占空比，对应舵机的不同角度
        test_cycles = [5.0, 7.5, 10.0]  # 0°, 90°, 180°
        
        for duty in test_cycles:
            print(f"\n--- 测试占空比 {duty}% (对应舵机角度) ---")
            pwm.start(duty)
            
            # 持续5秒，观察舵机反应
            time.sleep(5)
            
            pwm.stop()
            time.sleep(1)
        
        print("\n=== 舵机测试完成 ===")
        print("如果舵机能够：")
        print("✅ 在 5.0% 占空比时转到 0° 位置")
        print("✅ 在 7.5% 占空比时转到 90° 位置")
        print("✅ 在 10.0% 占空比时转到 180° 位置")
        print("")
        print("那么舵机控制是正常的！")
        print("如果舵机不动，可能的原因：")
        print("1. 电源电压不足（舵机需要 5V 或 12V）")
        print("2. 信号线连接错误")
        print("3. 舵机损坏")
        print("4. 舵机参数不匹配")
        
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