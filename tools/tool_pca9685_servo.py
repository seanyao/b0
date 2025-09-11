#!/usr/bin/env python3
"""
PCA9685 舵机控制测试工具
验证 PCA9685 的舵机控制功能
"""

import sys
import os
import time

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pca9685_control import PCA9685

def main():
    print("=== PCA9685 舵机控制测试 ===")
    print("连接: PCA9685 → I2C 总线 7 (Pin 3/5)")
    print("      舵机 → PCA9685 通道0")
    print("      舵机电源 → 独立5V供电")
    print("")
    
    try:
        # 创建控制器 - 明确使用总线 7
        pca = PCA9685(bus=7)
        print("✅ PCA9685 初始化成功")
        print(f"   I2C总线: 7, 地址: 0x40, 频率: 50Hz")
        print(f"   通道范围: 0-15, PWM分辨率: 12位 (0-4095)")
        
        # 测试角度序列
        angles = [0, 45, 90, 135, 180, 90, 0]
        
        print("\n开始舵机角度测试...")
        print("按 Ctrl+C 停止测试")
        
        for angle in angles:
            print(f"→ 设置角度: {angle}°")
            # 计算并显示PWM值用于调试
            pulse = int(150 + (angle / 180.0) * 450)
            print(f"   PWM脉冲值: {pulse} (0°=150, 180°=600)")
            pca.servo(0, angle)  # 通道0
            print(f"   ✅ PWM信号已发送到通道0")
            time.sleep(2)
        
        print("\n=== 连续扫描测试 ===")
        while True:
            # 0° → 180°
            for angle in range(0, 181, 10):
                pulse = int(150 + (angle / 180.0) * 450)
                pca.servo(0, angle)
                print(f"\r角度: {angle:3d}° | PWM: {pulse}", end="", flush=True)
                time.sleep(0.1)
            
            # 180° → 0°
            for angle in range(180, -1, -10):
                pulse = int(150 + (angle / 180.0) * 450)
                pca.servo(0, angle)
                print(f"\r角度: {angle:3d}° | PWM: {pulse}", end="", flush=True)
                time.sleep(0.1)
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n可能的原因:")
        print("- PCA9685 未连接或地址错误")
        print("- I2C 权限不足 (尝试 sudo)")
        print("- 硬件连接问题")
    finally:
        # 清理资源
        if 'pca' in locals():
            pca.off(0)  # 关闭通道0
        print("🧹 资源已清理")

if __name__ == "__main__":
    main()