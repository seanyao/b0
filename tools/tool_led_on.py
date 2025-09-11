#!/usr/bin/env python3
"""
LED 持续点亮工具
持续点亮通道0的LED蓝灯，直到用户停止
"""

import sys
import os
import time
import signal
import smbus

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def duty_to_pulse(duty, freq=50):
    """将占空比转换为PCA9685的脉冲计数值"""
    T = 1.0 / freq
    high_time = duty * T
    step_time = T / 4096
    pulse = int(high_time / step_time)
    return max(0, min(pulse, 4095))

class LEDController:
    """LED控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.bus_num = 7
        self.address = 0x40
        self.bus = None
        self.initialized = False
        self.running = False
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理Ctrl+C信号"""
        print("\n⚠️  检测到中断信号，正在关闭LED...")
        self.stop()
        sys.exit(0)
    
    def connect(self):
        """连接到PCA9685"""
        try:
            self.bus = smbus.SMBus(self.bus_num)
            print(f"✅ 连接到 I2C 总线 {self.bus_num}")
            return True
        except Exception as e:
            print(f"❌ I2C 连接失败: {e}")
            return False
    
    def initialize(self):
        """初始化PCA9685"""
        if not self.bus:
            print("❌ 未连接到I2C总线")
            return False
        
        try:
            print("初始化 PCA9685...")
            
            # 计算50Hz的预分频值
            prescale = int(25000000.0 / (4096 * 50) - 1)
            
            # 进入睡眠模式
            old_mode = self.bus.read_byte_data(self.address, 0x00)
            self.bus.write_byte_data(self.address, 0x00, (old_mode & 0x7F) | 0x10)
            
            # 设置频率
            self.bus.write_byte_data(self.address, 0xFE, prescale)
            
            # 恢复并启用自动增量
            self.bus.write_byte_data(self.address, 0x00, old_mode)
            time.sleep(0.005)
            self.bus.write_byte_data(self.address, 0x00, old_mode | 0x80)
            
            self.initialized = True
            print("✅ PCA9685 初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ PCA9685 初始化失败: {e}")
            return False
    
    def turn_on_led(self, channel=0, brightness=50):
        """点亮LED"""
        if not self.initialized:
            print("❌ PCA9685 未初始化")
            return False
        
        try:
            # 将亮度百分比转换为占空比
            duty_ratio = brightness / 100.0
            
            # 计算脉冲值
            pulse = duty_to_pulse(duty_ratio, freq=50)
            
            print(f"点亮通道 {channel} LED，亮度 {brightness}% (脉冲值: {pulse})")
            
            # 设置PWM
            base = 0x06 + 4 * channel
            self.bus.write_byte_data(self.address, base, 0)      # ON_L
            self.bus.write_byte_data(self.address, base + 1, 0)  # ON_H
            self.bus.write_byte_data(self.address, base + 2, pulse & 0xFF)      # OFF_L
            self.bus.write_byte_data(self.address, base + 3, pulse >> 8)        # OFF_H
            
            self.running = True
            return True
            
        except Exception as e:
            print(f"❌ 点亮LED失败: {e}")
            return False
    
    def turn_off_led(self, channel=0):
        """关闭LED"""
        if not self.initialized:
            return False
        
        try:
            base = 0x06 + 4 * channel
            self.bus.write_byte_data(self.address, base, 0)
            self.bus.write_byte_data(self.address, base + 1, 0)
            self.bus.write_byte_data(self.address, base + 2, 0)
            self.bus.write_byte_data(self.address, base + 3, 0)
            
            self.running = False
            print(f"✅ 通道 {channel} LED 已关闭")
            return True
        except Exception as e:
            print(f"❌ 关闭LED失败: {e}")
            return False
    
    def stop(self):
        """停止LED"""
        self.turn_off_led(0)

def main():
    """主函数"""
    print("=== LED 持续点亮工具 ===")
    print("持续点亮通道0的LED蓝灯")
    print("")
    
    controller = LEDController()
    
    try:
        # 连接和初始化
        if not controller.connect():
            return
        
        if not controller.initialize():
            return
        
        # 点亮LED
        print("正在点亮通道0的LED...")
        if not controller.turn_on_led(0, 50):  # 50%亮度
            return
        
        print("✅ LED已点亮！")
        print("")
        print("💡 LED连接方式:")
        print("   方式1 (共阴极): PCA9685通道0 → 电阻(220Ω) → LED正极 → LED负极 → GND")
        print("   方式2 (共阳极): 5V → 电阻(220Ω) → LED正极 → LED负极 → PCA9685通道0")
        print("   注意: 需要串联限流电阻保护LED")
        print("")
        print("按 Ctrl+C 停止并关闭LED")
        print("="*50)
        
        # 持续运行
        while controller.running:
            time.sleep(1)
    
    except Exception as e:
        print(f"\n❌ 程序运行错误: {e}")
    finally:
        controller.stop()
        print("👋 程序结束")

if __name__ == "__main__":
    main()
