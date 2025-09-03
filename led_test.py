#!/usr/bin/env python3
"""
LED PWM 测试 - 验证 GPIO Pin 7 的 PWM 信号
"""

import Jetson.GPIO as GPIO
import time
import threading

class LEDPWMTest:
    def __init__(self, pin):
        self.pin = pin
        self.running = False
        self.duty_cycle = 0
        self.frequency = 50  # 50Hz，和舵机一样
        self.period = 1.0 / self.frequency
        self.thread = None
        
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    
    def start_pwm(self, duty_cycle):
        """启动软件PWM"""
        self.duty_cycle = duty_cycle
        self.running = True
        self.thread = threading.Thread(target=self._pwm_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"LED PWM 启动，占空比: {duty_cycle}%")
    
    def set_duty_cycle(self, duty_cycle):
        """改变占空比"""
        self.duty_cycle = duty_cycle
        print(f"LED 亮度调整到: {duty_cycle}%")
    
    def stop_pwm(self):
        """停止PWM"""
        self.running = False
        if self.thread:
            self.thread.join()
        GPIO.output(self.pin, GPIO.LOW)
        print("LED PWM 停止")
    
    def _pwm_loop(self):
        """PWM 生成循环"""
        while self.running:
            if self.duty_cycle > 0:
                on_time = self.period * (self.duty_cycle / 100.0)
                off_time = self.period - on_time
                
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(on_time)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(off_time)
            else:
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(self.period)

def main():
    print("=== LED PWM 信号测试 ===")
    print("连接: GPIO Pin 7 → 330Ω电阻 → LED正极 → LED负极 → GND")
    print("")
    
    GPIO.setmode(GPIO.BOARD)
    
    try:
        led_pwm = LEDPWMTest(7)
        
        print("1. 测试基本 PWM 功能...")
        
        # 测试不同占空比
        duty_cycles = [10, 25, 50, 75, 100]
        
        for duty in duty_cycles:
            print(f"\n--- 设置占空比: {duty}% ---")
            led_pwm.start_pwm(duty)
            time.sleep(3)  # 观察3秒
            led_pwm.stop_pwm()
            time.sleep(1)
        
        print("\n2. 测试舵机频率 PWM (50Hz)...")
        
        # 测试舵机相关的占空比范围
        servo_duties = [5.0, 7.5, 10.0]  # 对应舵机的 0°, 90°, 180°
        
        for duty in servo_duties:
            print(f"\n--- 舵机占空比: {duty}% ---")
            led_pwm.start_pwm(duty)
            time.sleep(3)
            led_pwm.stop_pwm()
            time.sleep(1)
        
        print("\n3. 连续变化测试...")
        led_pwm.start_pwm(0)
        
        # 从暗到亮再到暗
        for i in range(101):
            led_pwm.set_duty_cycle(i)
            time.sleep(0.05)
        
        for i in range(100, -1, -1):
            led_pwm.set_duty_cycle(i)
            time.sleep(0.05)
        
        led_pwm.stop_pwm()
        
        print("\n=== 测试结果分析 ===")
        print("如果 LED 能够：")
        print("✅ 在不同占空比下显示不同亮度")
        print("✅ 平滑地从暗变亮再变暗")
        print("✅ 在 5%-10% 占空比下有可见的亮度变化")
        print("")
        print("那么 PWM 信号是正常的！")
        print("舵机不动的问题可能是：")
        print("1. 舵机需要 5V 信号电平（当前是 3.3V）")
        print("2. 舵机损坏")
        print("3. 舵机参数不匹配")
        
    except KeyboardInterrupt:
        print("\n测试中断")
    except Exception as e:
        print(f"\n错误: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO 清理完成")

if __name__ == "__main__":
    main()