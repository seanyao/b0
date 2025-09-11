#!/usr/bin/env python3
"""
Adafruit ServoKit 舵机控制测试工具
使用 adafruit_servokit 库进行舵机控制
"""

import sys
import os
import time

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from adafruit_servokit import ServoKit
except ImportError:
    print("❌ 错误: 未找到 adafruit_servokit 库")
    print("请运行: pip install adafruit-circuitpython-servokit")
    sys.exit(1)

def main():
    print("=== Adafruit ServoKit 舵机控制测试 ===")
    print("连接: 舵机 → 默认 I2C 总线")
    print("      舵机通道: 0")
    print("      舵机电源: 独立5V供电")
    print("")
    
    try:
        # 创建 ServoKit 实例
        kit = ServoKit(channels=0)
        print("✅ ServoKit 初始化成功")
        
        # 设置舵机引脚
        servo_pin = 0
        print(f"✅ 舵机引脚设置为: {servo_pin}")
        
        # 测试角度序列 (90°, 120°, 150°)
        angles = [90, 120, 150]
        
        print("\n开始舵机角度测试...")
        print("按 Ctrl+C 停止测试")
        print("")
        
        for i, angle in enumerate(angles):
            print(f"→ 设置角度: {angle}°")
            kit.servo[servo_pin].angle = angle
            time.sleep(2)
        
        print("\n=== 测试完成 ===")
        print("舵机已移动到最终位置 (150°)")
        
        # 连续循环测试
        print("\n=== 连续循环测试 ===")
        print("按 Ctrl+C 停止测试")
        while True:
            for angle in angles:
                print(f"\r角度: {angle:3d}°", end="", flush=True)
                kit.servo[servo_pin].angle = angle
                time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n可能的原因:")
        print("- 舵机驱动板未连接")
        print("- I2C 权限不足 (尝试 sudo)")
        print("- 硬件连接问题")
        print("- adafruit_servokit 库未正确安装")
    finally:
        # 清理资源
        if 'kit' in locals():
            # 将舵机设置为安全位置
            try:
                kit.servo[0].angle = 90
                print("🧹 舵机已重置到安全位置 (90°)")
            except:
                print("⚠️  无法重置舵机位置")

if __name__ == "__main__":
    main()