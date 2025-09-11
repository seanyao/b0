#!/usr/bin/env python3
"""
增强版PCA9685检测工具
使用严格的寄存器验证，避免误判
"""

import os
import smbus

CANDIDATE_BUSES = [7, 1, 0, 2, 4, 5]
CANDIDATE_ADDRS = [0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]

def likely_pca9685(bus, addr):
    """纯读校验，不写寄存器，尽量避免误判"""
    # MODE1 / PRE_SCALE
    mode1 = bus.read_byte_data(addr, 0x00)
    prescale = bus.read_byte_data(addr, 0xFE)
    if not (0x03 <= prescale <= 0xFF):
        return None
    
    # MODE2（常见 0x04，允许非0x04但确保保留位为0）
    mode2 = bus.read_byte_data(addr, 0x01)
    if mode2 & 0xE0:  # MODE2 高3位保留，应为0
        return None
    
    # ALLCALLADR 默认 0xE0（=0x70<<1），若被改过也不强制，但优先作为指纹
    try:
        allcall = bus.read_byte_data(addr, 0x05)
        if allcall not in (0xE0, 0x00) and (allcall & 0x01):  # 低位应为0
            return None
    except Exception:
        allcall = None
    
    # LEDALL_* 一般为0
    try:
        ledall_on_h  = bus.read_byte_data(addr, 0xFB)
        ledall_off_h = bus.read_byte_data(addr, 0xFD)
        if (ledall_on_h & 0x10) or (ledall_off_h & 0x10):  # FULL_ON/FULL_OFF 位通常未置
            return None
    except Exception:
        pass
    
    return mode1, mode2, prescale, allcall

def probe_pca9685():
    print("=== PCA9685 设备探测（主动读寄存器）===")
    found = []
    for bus_num in CANDIDATE_BUSES:
        # 已知 Jetson 上 i2c-1@0x40 是板载 ina3221，直接跳过这对组合
        skip_pairs = {(1, 0x40)}
        try:
            bus = smbus.SMBus(bus_num)
            print(f"正在探测总线 {bus_num}...")
        except Exception as e:
            print(f"总线 {bus_num} 不可访问: {e}")
            continue
        try:
            for addr in CANDIDATE_ADDRS:
                if (bus_num, addr) in skip_pairs:
                    continue
                try:
                    r = likely_pca9685(bus, addr)
                    if r:
                        mode1, mode2, prescale, allcall = r
                        print(f"  ✅ 在总线 {bus_num}, 地址 0x{addr:02X} 发现 PCA9685")
                        print(f"     MODE1=0x{mode1:02X}, MODE2=0x{mode2:02X}, PRE_SCALE={prescale}"
                              + (f", ALLCALL=0x{allcall:02X}" if allcall is not None else ""))
                        found.append((bus_num, addr, mode1, prescale))
                except Exception:
                    # 无响应或被内核驱动占用：忽略
                    pass
        finally:
            try:
                bus.close()
            except Exception:
                pass
    return found

def main():
    found = probe_pca9685()
    
    print(f"\n=== 探测结果 ===")
    if found:
        for bus_num, addr, mode1, prescale in found:
            print(f"✅ 总线 {bus_num}, 地址 0x{addr:02X} - PCA9685确认")
            print(f"   MODE1: 0x{mode1:02X}, 预分频: {prescale}")
            
            # 计算PWM频率
            freq = 25000000.0 / (4096 * (prescale + 1))
            print(f"   当前PWM频率: {freq:.1f} Hz")
            
        # 建议使用第一个找到的设备
        recommended_bus, recommended_addr, _, _ = found[0]
        print(f"\n🎯 建议配置: bus={recommended_bus}, addr=0x{recommended_addr:02X}")
        
    else:
        print("❌ 未发现PCA9685设备")
        print("请检查:")
        print("- 硬件连接 (VCC, GND, SDA, SCL)")
        print("- I2C地址跳线设置")
        print("- 电源供电")

if __name__ == "__main__":
    main()