#!/usr/bin/env python3
"""
最简单的舵机控制代码
使用 adafruit_servokit 库控制 PCA9685 舵机
"""

from adafruit_servokit import ServoKit
import time

def main():
    print("=== 简单舵机控制测试 ===")
    print("使用 adafruit_servokit 库")
    print("")
    
    try:
        # 初始化 ServoKit，默认通道
        kit = ServoKit(channels=0)
        print("✅ ServoKit 初始化成功")
        
        # 设置舵机引脚
        servo_pin = 0
        print(f"使用通道: {servo_pin}")
        
        # 测试角度序列
        angles = [90, 120, 150]
        
        for angle in angles:
            print(f"→ 设置角度: {angle}°")
            kit.servo[servo_pin].angle = angle
            print(f"   ✅ 角度已设置")
            time.sleep(2)
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n可能的原因:")
        print("- 未安装 adafruit_servokit 库")
        print("- PCA9685 未连接或地址错误")
        print("- I2C 权限不足")

if __name__ == "__main__":
    main()