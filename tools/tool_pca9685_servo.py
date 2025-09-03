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
    print("连接: PCA9685 → I2C (Pin 3/5)")
    print("      舵机 → PCA9685 通道0")
    print("      舵机电源 → 独立5V供电")
    print("")
    
    try:
        # 创建控制器
        pca = PCA9685()
        print("✅ PCA9685 初始化成功")
        
        # 测试角度序列
        angles = [0, 45, 90, 135, 180, 90, 0]
        
        print("\n开始舵机角度测试...")
        print("按 Ctrl+C 停止测试")
        
        for angle in angles:
            print(f"→ 设置角度: {angle}°")
            pca.servo(0, angle)  # 通道0
            time.sleep(2)
        
        print("\n=== 连续扫描测试 ===")
        while True:
            # 0° → 180°
            for angle in range(0, 181, 10):
                pca.servo(0, angle)
                print(f"\r角度: {angle:3d}°", end="", flush=True)
                time.sleep(0.1)
            
            # 180° → 0°
            for angle in range(180, -1, -10):
                pca.servo(0, angle)
                print(f"\r角度: {angle:3d}°", end="", flush=True)
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