#!/usr/bin/env python3
"""
检查可用的I2C总线
"""

import os
import subprocess

def check_i2c_devices():
    """检查I2C设备"""
    print("=== 检查I2C设备 ===")
    
    # 方法1: 检查/dev/i2c-*设备
    try:
        result = subprocess.run(['ls', '/dev/i2c-*'], capture_output=True, text=True)
        if result.returncode == 0:
            devices = result.stdout.strip().split()
            print(f"发现I2C设备: {devices}")
        else:
            print("未发现I2C设备文件")
    except:
        print("无法检查I2C设备文件")
    
    # 方法2: 使用i2cdetect -l
    try:
        result = subprocess.run(['sudo', 'i2cdetect', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("\n=== I2C总线列表 ===")
            print(result.stdout)
        else:
            print("无法获取I2C总线列表")
    except:
        print("无法运行i2cdetect -l")

def scan_all_buses():
    """扫描所有可能的I2C总线"""
    print("\n=== 扫描所有I2C总线 ===")
    
    # 常见的I2C总线号
    common_buses = [0, 1, 2, 4, 5, 6, 7, 8, 9, 10]
    
    for bus_num in common_buses:
        print(f"\n--- 扫描总线 {bus_num} ---")
        try:
            result = subprocess.run(['sudo', 'i2cdetect', '-y', str(bus_num)], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(result.stdout)
                
                # 检查是否有设备
                if '40' in result.stdout:
                    print(f"🎯 在总线 {bus_num} 上发现PCA9685 (0x40)!")
                    return bus_num
            else:
                print(f"总线 {bus_num} 不可访问")
        except subprocess.TimeoutExpired:
            print(f"总线 {bus_num} 扫描超时")
        except Exception as e:
            print(f"总线 {bus_num} 错误: {e}")
    
    return None

def main():
    print("=== I2C总线检测工具 ===")
    print("用于确定PCA9685连接在哪个I2C总线上")
    print("")
    
    check_i2c_devices()
    
    found_bus = scan_all_buses()
    
    if found_bus is not None:
        print(f"\n✅ 建议使用总线 {found_bus}")
        print(f"修改代码中的 bus 参数为: {found_bus}")
    else:
        print("\n❌ 未在任何总线上发现PCA9685")
        print("请检查:")
        print("1. 硬件连接 (VCC, GND, SDA, SCL)")
        print("2. 电源供电")
        print("3. I2C总线是否启用")

if __name__ == "__main__":
    main()