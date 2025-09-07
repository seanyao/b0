#!/usr/bin/env python3
"""
I2C 设备扫描工具
检测连接的 I2C 设备，验证 PCA9685 连接
"""

import smbus
import time

def scan_i2c_bus(bus_num=1):
    """扫描 I2C 总线上的设备"""
    print(f"=== 扫描 I2C 总线 {bus_num} ===")
    
    try:
        bus = smbus.SMBus(bus_num)
        devices = []
        
        print("扫描地址范围: 0x03-0x77")
        print("     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f")
        
        for row in range(0, 8):
            print(f"{row}0: ", end="")
            
            for col in range(0, 16):
                addr = row * 16 + col
                
                if addr < 0x03 or addr > 0x77:
                    print("   ", end="")
                    continue
                
                try:
                    bus.read_byte(addr)
                    print(f"{addr:02x} ", end="")
                    devices.append(addr)
                except:
                    print("-- ", end="")
            
            print()  # 换行
        
        print(f"\n发现 {len(devices)} 个设备:")
        for addr in devices:
            device_name = get_device_name(addr)
            print(f"  0x{addr:02X} - {device_name}")
        
        return devices
        
    except Exception as e:
        print(f"❌ I2C 扫描失败: {e}")
        print("\n可能的原因:")
        print("- I2C 权限不足 (尝试 sudo)")
        print("- I2C 总线未启用")
        print("- 硬件连接问题")
        return []

def get_device_name(addr):
    """根据地址推测设备类型"""
    device_map = {
        0x40: "PCA9685 (PWM驱动器)",
        0x48: "ADS1115 (ADC)",
        0x68: "DS1307/DS3231 (RTC)",
        0x76: "BMP280 (气压传感器)",
        0x77: "BMP180 (气压传感器)"
    }
    return device_map.get(addr, "未知设备")

def test_pca9685(addr=0x40):
    """测试 PCA9685 连接"""
    print(f"\n=== 测试 PCA9685 (0x{addr:02X}) ===")
    
    try:
        bus = smbus.SMBus(7)
        
        # 读取模式寄存器
        mode1 = bus.read_byte_data(addr, 0x00)
        print(f"✅ MODE1 寄存器: 0x{mode1:02X}")
        
        # 读取预分频寄存器
        prescale = bus.read_byte_data(addr, 0xFE)
        freq = 25000000.0 / (4096 * (prescale + 1))
        print(f"✅ 预分频值: {prescale}, 频率: {freq:.1f}Hz")
        
        print("✅ PCA9685 连接正常")
        return True
        
    except Exception as e:
        print(f"❌ PCA9685 测试失败: {e}")
        return False

def main():
    print("=== I2C 设备检测工具 ===")
    print("")
    
    # 扫描 I2C 设备
    devices = scan_i2c_bus(7)
    
    # 检查 PCA9685
    if 0x40 in devices:
        test_pca9685(0x40)
    else:
        print("\n⚠️  未发现 PCA9685 (0x40)")
        print("请检查:")
        print("- 硬件连接 (SDA/SCL/VCC/GND)")
        print("- 电源供电")
        print("- 地址跳线设置")

if __name__ == "__main__":
    main()