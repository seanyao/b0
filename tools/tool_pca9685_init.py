#!/usr/bin/env python3
"""
PCA9685 初始化工具
确保所有PWM通道关闭，输出0V
"""

import sys
import os
import smbus

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def init_pca9685():
    """初始化PCA9685，关闭所有通道"""
    print("=== PCA9685 初始化工具 ===")
    print("确保所有PWM通道关闭，输出0V")
    print("")
    
    try:
        # 连接到PCA9685
        bus = smbus.SMBus(7)
        address = 0x40
        print(f"✅ 连接到 I2C 总线 7，地址 0x{address:02X}")
        
        # 初始化PCA9685
        print("初始化 PCA9685...")
        
        # 计算50Hz的预分频值
        prescale = int(25000000.0 / (4096 * 50) - 1)
        
        # 进入睡眠模式
        old_mode = bus.read_byte_data(address, 0x00)
        bus.write_byte_data(address, 0x00, (old_mode & 0x7F) | 0x10)
        
        # 设置频率
        bus.write_byte_data(address, 0xFE, prescale)
        
        # 恢复并启用自动增量
        bus.write_byte_data(address, 0x00, old_mode)
        bus.write_byte_data(address, 0x00, old_mode | 0x80)
        
        print("✅ PCA9685 初始化成功")
        
        # 关闭所有通道
        print("关闭所有16个通道...")
        for channel in range(16):
            base = 0x06 + 4 * channel
            bus.write_byte_data(address, base, 0)      # ON_L
            bus.write_byte_data(address, base + 1, 0)  # ON_H
            bus.write_byte_data(address, base + 2, 0)  # OFF_L
            bus.write_byte_data(address, base + 3, 0)  # OFF_H
        
        print("✅ 所有通道已关闭，输出0V")
        print("")
        print("现在所有PWM通道都应该输出0V")
        print("如果LED仍然亮着，请检查连接方式")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

if __name__ == "__main__":
    init_pca9685()
