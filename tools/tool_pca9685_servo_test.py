#!/usr/bin/env python3
"""
PCA9685 舵机测试工具
使用正确的PWM参数测试舵机，参考软件PWM的占空比设置
"""

import sys
import os
import time
import signal
import smbus

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def duty_to_pulse(duty, freq=50):
    """
    将占空比转换为PCA9685的脉冲计数值
    
    Args:
        duty: 占空比 (0.0 ~ 1.0)
        freq: 频率 (Hz)，默认50Hz
    
    Returns:
        pulse: PCA9685的脉冲计数值 (0~4095)
    
    换算逻辑：
    - PCA9685 的分辨率是 4096 steps (0~4095)
    - 一个周期时间 T = 1 / freq (舵机一般 50Hz → 20ms)
    - 每步时间 step_time = T / 4096
    - 高电平时间 high_time = duty * T
    - 计数值 pulse = int(high_time / step_time)
    """
    # 计算周期时间
    T = 1.0 / freq
    
    # 计算高电平时间
    high_time = duty * T
    
    # 计算每步时间
    step_time = T / 4096
    
    # 计算脉冲计数值
    pulse = int(high_time / step_time)
    
    # 限制在有效范围内
    pulse = max(0, min(pulse, 4095))
    
    return pulse


class PCA9685ServoTester:
    """PCA9685 舵机测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.bus_num = 7
        self.address = 0x40
        self.bus = None
        self.initialized = False
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理Ctrl+C信号"""
        print("\n⚠️  检测到中断信号，正在清理...")
        self.cleanup()
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
            print(f"设置预分频值: {prescale} (50Hz)")
            
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
    
    def set_servo_angle(self, channel, angle):
        """设置舵机角度 (0-180度)"""
        if not self.initialized:
            print("❌ PCA9685 未初始化")
            return False
        
        try:
            # 角度转占空比: 0°=5%, 90°=7.5%, 180°=10%
            # 线性映射: 0°→5%, 180°→10%
            duty_cycle = 5.0 + (angle / 180.0) * 5.0
            
            # 将百分比占空比转换为小数占空比
            duty_ratio = duty_cycle / 100.0
            
            # 使用duty_to_pulse函数计算脉冲值
            pulse = duty_to_pulse(duty_ratio, freq=50)
            
            print(f"设置角度: {angle}° → 占空比: {duty_cycle:.1f}% → 脉冲值: {pulse}")
            
            # 设置PWM
            base = 0x06 + 4 * channel
            self.bus.write_byte_data(self.address, base, 0)      # ON_L
            self.bus.write_byte_data(self.address, base + 1, 0)  # ON_H
            self.bus.write_byte_data(self.address, base + 2, pulse & 0xFF)      # OFF_L
            self.bus.write_byte_data(self.address, base + 3, pulse >> 8)        # OFF_H
            
            return True
            
        except Exception as e:
            print(f"❌ 设置舵机角度失败: {e}")
            return False
    
    def set_servo_duty_cycle(self, channel, duty_cycle):
        """设置舵机占空比 (参考软件PWM)"""
        if not self.initialized:
            print("❌ PCA9685 未初始化")
            return False
        
        try:
            # 将百分比占空比转换为小数占空比
            duty_ratio = duty_cycle / 100.0
            
            # 使用duty_to_pulse函数计算脉冲值
            pulse = duty_to_pulse(duty_ratio, freq=50)
            
            print(f"设置占空比: {duty_cycle}% → 脉冲值: {pulse}")
            
            # 设置PWM
            base = 0x06 + 4 * channel
            self.bus.write_byte_data(self.address, base, 0)      # ON_L
            self.bus.write_byte_data(self.address, base + 1, 0)  # ON_H
            self.bus.write_byte_data(self.address, base + 2, pulse & 0xFF)      # OFF_L
            self.bus.write_byte_data(self.address, base + 3, pulse >> 8)        # OFF_H
            
            return True
            
        except Exception as e:
            print(f"❌ 设置舵机占空比失败: {e}")
            return False
    
    def off_channel(self, channel):
        """关闭指定通道"""
        if not self.initialized:
            return False
        
        try:
            base = 0x06 + 4 * channel
            self.bus.write_byte_data(self.address, base, 0)
            self.bus.write_byte_data(self.address, base + 1, 0)
            self.bus.write_byte_data(self.address, base + 2, 0)
            self.bus.write_byte_data(self.address, base + 3, 0)
            print(f"✅ 通道 {channel} 已关闭")
            return True
        except Exception as e:
            print(f"❌ 关闭通道失败: {e}")
            return False
    
    def test_channel_with_angles(self, channel):
        """使用角度测试通道"""
        print(f"\n{'='*50}")
        print(f"🔍 使用角度测试通道 {channel}")
        print(f"{'='*50}")
        
        # 测试角度序列
        test_angles = [0, 90, 180]
        
        for angle in test_angles:
            print(f"\n--- 测试角度 {angle}° ---")
            if self.set_servo_angle(channel, angle):
                print("✅ PWM 信号已输出")
                time.sleep(3)
            else:
                print("❌ PWM 信号输出失败")
                return False
        
        # 关闭通道
        self.off_channel(channel)
        
        # 询问结果
        response = input(f"舵机在通道 {channel} 上有响应吗? (y/n): ").lower().strip()
        return response == 'y'
    
    def test_channel_with_duty_cycles(self, channel):
        """使用占空比测试通道 (参考软件PWM)"""
        print(f"\n{'='*50}")
        print(f"🔍 使用占空比测试通道 {channel}")
        print(f"{'='*50}")
        
        # 测试占空比序列 (参考软件PWM)
        test_cycles = [5.0, 7.5, 10.0]  # 0°, 90°, 180°
        
        for duty in test_cycles:
            print(f"\n--- 测试占空比 {duty}% ---")
            if self.set_servo_duty_cycle(channel, duty):
                print("✅ PWM 信号已输出")
                time.sleep(3)
            else:
                print("❌ PWM 信号输出失败")
                return False
        
        # 关闭通道
        self.off_channel(channel)
        
        # 询问结果
        response = input(f"舵机在通道 {channel} 上有响应吗? (y/n): ").lower().strip()
        return response == 'y'
    
    def cleanup(self):
        """清理资源"""
        if self.initialized:
            print("🧹 关闭所有通道...")
            for ch in range(16):
                self.off_channel(ch)
            print("✅ 清理完成")

def main():
    """主函数"""
    print("=== PCA9685 舵机测试工具 ===")
    print("使用正确的PWM参数测试舵机，参考软件PWM的占空比设置")
    print("")
    
    tester = PCA9685ServoTester()
    
    try:
        # 连接和初始化
        if not tester.connect():
            return
        
        if not tester.initialize():
            return
        
        # 固定使用通道0
        channel = 0
        print(f"使用通道 {channel} 进行测试")
        
        # 使用角度测试
        print("\n使用角度测试 (0°, 90°, 180°)")
        
        if tester.test_channel_with_angles(channel):
            print(f"\n🎯 舵机在通道 {channel} 上有响应!")
        else:
            print(f"\n❌ 舵机在通道 {channel} 上无响应")
    
    except Exception as e:
        print(f"\n❌ 程序运行错误: {e}")
    finally:
        tester.cleanup()
        print("👋 程序结束")

if __name__ == "__main__":
    main()
