#!/usr/bin/env python3
import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)

print("开始简单脉冲测试...")

try:
    for i in range(100):
        # 1.5ms 高电平 (中位)
        GPIO.output(7, GPIO.HIGH)
        time.sleep(0.0015)
        
        # 18.5ms 低电平
        GPIO.output(7, GPIO.LOW)
        time.sleep(0.0185)
        
        if i % 10 == 0:
            print(f"已发送 {i+1} 个脉冲")
            
except KeyboardInterrupt:
    print("测试中断")
finally:
    GPIO.cleanup()
    print("测试结束")