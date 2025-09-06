#!/usr/bin/env python3
"""
PCA9685 调试工具
用于诊断 PCA9685 连接和配置问题
"""

import sys
import os
import time
import smbus

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def scan_all_i2c_buses():
    """扫描所有可用的I2C总线"""
    print("=== 扫描所有 I2C 总线 ===")
    
    available_buses = [0, 1, 2, 4, 5, 7]  # Jetson 常用总线
    found_devices = {}
    
    for bus_num in available_buses:
        print(f"\n--- I2C Bus {bus_num} ---")
        try:
            bus = smbus.SMBus(bus_num)
            devices = []
            
            # 扫描地址范围 0x03-0x77
            for addr in range(0x03, 0x78):
                try:
                    bus.read_byte(addr)
                    devices.append(addr)
                    print(f"  发现设备: 0x{addr:02X}")
                except:
                    pass
            
            if devices:
                found_devices[bus_num] = devices
                print(f"  总线 {bus_num} 发现 {len(devices)} 个设备")
            else:
                print(f"  总线 {bus_num} 无设备")
                
        except Exception as e:
            print(f"  总线 {bus_num} 不可访问: {e}")
    
    return found_devices

def test_pca9685_on_bus(bus_num, address=0x40):
    """在指定总线上测试PCA9685"""
    print(f"\n=== 在总线 {bus_num} 上测试 PCA9685 (0x{address:02X}) ===")
    
    try:
        bus = smbus.SMBus(bus_num)
        
        # 尝试读取模式寄存器
        try:
            mode1 = bus.read_byte_data(address, 0x00)
            print(f"✅ MODE1 寄存器读取成功: 0x{mode1:02X}")
        except Exception as e:
            print(f"❌ MODE1 寄存器读取失败: {e}")
            return False
        
        # 尝试读取预分频寄存器
        try:
            prescale = bus.read_byte_data(address, 0xFE)
            freq = 25000000.0 / (4096 * (prescale + 1))
            print(f"✅ 预分频寄存器读取成功: {prescale}, 频率: {freq:.1f}Hz")
        except Exception as e:
            print(f"❌ 预分频寄存器读取失败: {e}")
            return False
        
        # 尝试初始化PCA9685
        try:
            print("尝试初始化 PCA9685...")
            
            # 计算50Hz的预分频值
            prescale = int(25000000.0 / (4096 * 50) - 1)
            print(f"设置预分频值: {prescale}")
            
            # 进入睡眠模式
            old_mode = bus.read_byte_data(address, 0x00)
            bus.write_byte_data(address, 0x00, (old_mode & 0x7F) | 0x10)
            
            # 设置频率
            bus.write_byte_data(address, 0xFE, prescale)
            
            # 恢复并启用自动增量
            bus.write_byte_data(address, 0x00, old_mode)
            time.sleep(0.005)
            bus.write_byte_data(address, 0x00, old_mode | 0x80)
            
            print("✅ PCA9685 初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ PCA9685 初始化失败: {e}")
            return False
        
    except Exception as e:
        print(f"❌ 总线 {bus_num} 访问失败: {e}")
        return False

def test_pwm_output(bus_num, address=0x40, channel=0):
    """测试PWM输出"""
    print(f"\n=== 测试 PWM 输出 (总线 {bus_num}, 通道 {channel}) ===")
    
    try:
        bus = smbus.SMBus(bus_num)
        
        # 设置PWM值 (约7.5%占空比，对应舵机90度)
        pulse = int(150 + (90 / 180.0) * 450)  # 约375
        print(f"设置PWM脉冲值: {pulse}")
        
        # 写入PWM寄存器
        base = 0x06 + 4 * channel
        bus.write_byte_data(address, base, 0)      # ON_L
        bus.write_byte_data(address, base + 1, 0)  # ON_H
        bus.write_byte_data(address, base + 2, pulse & 0xFF)      # OFF_L
        bus.write_byte_data(address, base + 3, pulse >> 8)        # OFF_H
        
        print(f"✅ PWM 设置成功，通道 {channel} 输出 90° 信号")
        print("请检查舵机是否移动")
        
        time.sleep(3)
        
        # 关闭PWM
        bus.write_byte_data(address, base, 0)
        bus.write_byte_data(address, base + 1, 0)
        bus.write_byte_data(address, base + 2, 0)
        bus.write_byte_data(address, base + 3, 0)
        
        print("✅ PWM 已关闭")
        return True
        
    except Exception as e:
        print(f"❌ PWM 测试失败: {e}")
        return False

def check_alternative_addresses(bus_num):
    """检查PCA9685的其他可能地址"""
    print(f"\n=== 检查 PCA9685 其他地址 (总线 {bus_num}) ===")
    
    # PCA9685可能的地址
    possible_addresses = [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]
    
    try:
        bus = smbus.SMBus(bus_num)
        
        for addr in possible_addresses:
            try:
                # 尝试读取模式寄存器
                mode1 = bus.read_byte_data(addr, 0x00)
                print(f"✅ 地址 0x{addr:02X}: MODE1 = 0x{mode1:02X}")
                
                # 尝试读取预分频寄存器
                prescale = bus.read_byte_data(addr, 0xFE)
                freq = 25000000.0 / (4096 * (prescale + 1))
                print(f"   预分频: {prescale}, 频率: {freq:.1f}Hz")
                
                return addr
                
            except:
                print(f"❌ 地址 0x{addr:02X}: 无响应")
        
        return None
        
    except Exception as e:
        print(f"❌ 总线 {bus_num} 访问失败: {e}")
        return None

def main():
    """主函数"""
    print("=== PCA9685 调试工具 ===")
    print("用于诊断 PCA9685 连接和配置问题")
    print("")
    
    # 1. 扫描所有I2C总线
    found_devices = scan_all_i2c_buses()
    
    # 2. 检查每个总线上的PCA9685
    working_configs = []
    
    for bus_num, devices in found_devices.items():
        print(f"\n检查总线 {bus_num} 上的设备...")
        
        # 检查标准地址0x40
        if 0x40 in devices:
            print(f"✅ 总线 {bus_num} 发现设备 0x40")
            if test_pca9685_on_bus(bus_num, 0x40):
                working_configs.append((bus_num, 0x40))
        else:
            print(f"❌ 总线 {bus_num} 未发现设备 0x40")
            
            # 检查其他可能的地址
            alt_addr = check_alternative_addresses(bus_num)
            if alt_addr:
                working_configs.append((bus_num, alt_addr))
    
    # 3. 显示结果
    print("\n" + "="*50)
    print("诊断结果")
    print("="*50)
    
    if working_configs:
        print("✅ 发现可用的 PCA9685 配置:")
        for bus_num, address in working_configs:
            print(f"   总线: {bus_num}, 地址: 0x{address:02X}")
        
        # 测试第一个可用配置
        bus_num, address = working_configs[0]
        print(f"\n测试配置: 总线 {bus_num}, 地址 0x{address:02X}")
        
        if test_pwm_output(bus_num, address, 0):
            print(f"\n🎯 建议使用以下配置:")
            print(f"   PCA9685(bus={bus_num}, address=0x{address:02X})")
    else:
        print("❌ 未发现可用的 PCA9685 配置")
        print("\n可能的原因:")
        print("1. PCA9685 未正确连接")
        print("2. 电源供电问题")
        print("3. I2C 信号线连接错误")
        print("4. PCA9685 地址跳线设置错误")
        print("5. 硬件故障")
        
        print("\n建议检查:")
        print("1. 确认 PCA9685 的 VCC 和 GND 连接")
        print("2. 确认 SDA 和 SCL 信号线连接")
        print("3. 检查 PCA9685 的地址跳线设置")
        print("4. 尝试不同的 I2C 总线")

if __name__ == "__main__":
    main()
