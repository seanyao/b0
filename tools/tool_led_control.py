#!/usr/bin/env python3
"""
简化版LED控制工具
使用PCA9685控制LED亮度，支持开关和亮度调节
"""

import sys
import os
import time
import signal

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 导入PCA9685控制类
from pca9685_control import PCA9685


def main():
    """主函数"""
    print("=== LED闪烁控制工具 ===")
    print("控制通道0的LED闪烁10次，每次间隔1秒")
    print("")
    
    # 创建PCA9685控制器实例
    try:
        # 初始化PCA9685，默认使用总线7和地址0x40
        pca = PCA9685(bus=7, address=0x40)
        print("✅ PCA9685 初始化成功")
        
        print("💡 LED连接方式:")
        print("   方式1 (共阴极): PCA9685通道0 → 电阻(220Ω) → LED正极 → LED负极 → GND")
        print("   注意: 需要串联限流电阻保护LED")
        print("")
        print("开始闪烁...")
        print("="*50)
        
        # 设置信号处理
        def signal_handler(sig, frame):
            print("\n⚠️  检测到中断信号，正在关闭LED...")
            pca.off(0)  # 关闭通道0
            print("👋 程序结束")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # 闪烁10次
        brightness = 100  # 100%亮度
        for i in range(10):
            # 点亮LED
            pca.pwm(0, brightness)
            print(f"💡 第{i+1}次闪烁 - LED点亮")
            time.sleep(0.5)  # 亮0.5秒
            
            # 关闭LED
            pca.off(0)
            print(f"⚫ 第{i+1}次闪烁 - LED熄灭")
            time.sleep(0.5)  # 灭0.5秒
        
        print("\n✅ 闪烁完成！")
            
    except Exception as e:
        print(f"\n❌ 程序运行错误: {e}")
        print("可能的原因:")
        print("- PCA9685未连接或地址错误")
        print("- I2C权限不足 (尝试sudo)")
        print("- 硬件连接问题")
    finally:
        # 确保资源被清理
        if 'pca' in locals():
            pca.off(0)  # 关闭通道0


if __name__ == "__main__":
    main()