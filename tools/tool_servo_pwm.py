#!/usr/bin/env python3
"""
舵机调试版本 - 添加信号检测
"""

import Jetson.GPIO as GPIO
import time
import threading

class DebugSoftwarePWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.period = 1.0 / frequency
        self.duty_cycle = 0
        self.running = False
        self.thread = None
        self.pulse_count = 0
        
        # Setup GPIO
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        print(f"GPIO {self.pin} 初始化完成，初始状态: LOW")
    
    def start(self, duty_cycle):
        """Start software PWM with debugging"""
        self.duty_cycle = duty_cycle
        self.running = True
        self.pulse_count = 0
        self.thread = threading.Thread(target=self._pwm_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"PWM 启动，占空比: {duty_cycle}%")
    
    def ChangeDutyCycle(self, duty_cycle):
        """Change duty cycle with debugging"""
        old_duty = self.duty_cycle
        self.duty_cycle = duty_cycle
        print(f"占空比变更: {old_duty}% → {duty_cycle}%")
    
    def stop(self):
        """Stop PWM"""
        self.running = False
        if self.thread:
            self.thread.join()
        GPIO.output(self.pin, GPIO.LOW)
        print(f"PWM 停止，总脉冲数: {self.pulse_count}")
    
    def _pwm_loop(self):
        """PWM generation loop with debugging"""
        while self.running:
            if self.duty_cycle > 0:
                on_time = self.period * (self.duty_cycle / 100.0)
                off_time = self.period - on_time
                
                # 输出高电平
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(on_time)
                
                # 输出低电平
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(off_time)
                
                self.pulse_count += 1
                
                # 每50个脉冲打印一次状态
                if self.pulse_count % 50 == 0:
                    print(f"已发送 {self.pulse_count} 个脉冲，当前占空比: {self.duty_cycle}%")
            else:
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(self.period)

# 测试代码
def test_servo_debug():
    SERVO_PIN = 7
    PWM_FREQUENCY = 50
    
    print("=== 舵机调试测试 ===")
    
    try:
        GPIO.setmode(GPIO.BOARD)
        
        # 创建调试PWM
        pwm = DebugSoftwarePWM(SERVO_PIN, PWM_FREQUENCY)
        
        # 测试不同占空比
        test_cycles = [5.0, 7.5, 10.0]  # 0°, 90°, 180°
        
        for duty in test_cycles:
            print(f"\n--- 测试占空比 {duty}% ---")
            pwm.start(duty)
            
            # 持续5秒，观察舵机反应
            time.sleep(5)
            
            pwm.stop()
            time.sleep(1)
        
        print("\n调试测试完成")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    test_servo_debug()