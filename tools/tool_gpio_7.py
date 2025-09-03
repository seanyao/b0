import Jetson.GPIO as GPIO
import time

# 引脚编号采用物理针脚号
GPIO.setmode(GPIO.BOARD)

# 设置针脚 07 为输出
pin = 7
GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

try:
    while True:
        GPIO.output(pin, GPIO.HIGH)   # 输出高电平
        print("GPIO07 = HIGH")
        time.sleep(5)
        
        GPIO.output(pin, GPIO.LOW)    # 输出低电平
        print("GPIO07 = LOW")
        time.sleep(5)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("GPIO 清理完成")
