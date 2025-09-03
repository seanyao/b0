#!/usr/bin/env python3
"""
基本使用示例 - 演示 PWM 和 LED 控制功能
使用简单的实现，不依赖复杂的类
"""

import time
import threading
import Jetson.GPIO as GPIO

class SimplePWMControl:
    """简单的 PWM 控制类"""
    
    def __init__(self, pin, frequency=1000):
        self.pin = pin
        self.frequency = frequency
        self.duty_cycle = 0
        self.running = False
        self.thread = None
        
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    
    def start(self):
        """启动 PWM"""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._pwm_loop)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def stop(self):
        """停止 PWM"""
        self.running = False
        if self.thread:
            self.thread.join()
        GPIO.output(self.pin, GPIO.LOW)
        return True
    
    def set_duty_cycle(self, duty_cycle):
        """设置占空比"""
        self.duty_cycle = max(0, min(100, duty_cycle))
    
    def set_frequency(self, frequency):
        """设置频率"""
        self.frequency = max(100, min(50000, frequency))
    
    def _pwm_loop(self):
        """PWM 生成循环"""
        period = 1.0 / self.frequency
        while self.running:
            if self.duty_cycle > 0:
                on_time = period * (self.duty_cycle / 100.0)
                off_time = period - on_time
                
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(on_time)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(off_time)
            else:
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(period)
    
    def cleanup(self):
        """清理资源"""
        self.stop()
    
    def get_status(self):
        """获取状态"""
        return {
            'pin': self.pin,
            'frequency': self.frequency,
            'duty_cycle': self.duty_cycle,
            'running': self.running
        }
    
    def __str__(self):
        return f"SimplePWMControl(pin={self.pin}, freq={self.frequency}Hz, duty={self.duty_cycle}%)"


class SimpleLEDControl:
    """简单的 LED 控制类"""
    
    def __init__(self, pin, max_brightness=100):
        self.pin = pin
        self.max_brightness = max_brightness
        self.brightness = 0
        self.running = False
        self.thread = None
        
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    
    def on(self, brightness=None):
        """打开 LED"""
        if brightness is not None:
            self.set_brightness(brightness)
        
        if self.brightness > 0:
            GPIO.output(self.pin, GPIO.HIGH)
        return True
    
    def off(self):
        """关闭 LED"""
        GPIO.output(self.pin, GPIO.LOW)
        return True
    
    def set_brightness(self, brightness):
        """设置亮度"""
        self.brightness = max(0, min(self.max_brightness, brightness))
        if self.brightness > 0:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)
        return True
    
    def get_brightness(self):
        """获取当前亮度"""
        return self.brightness
    
    def cleanup(self):
        """清理资源"""
        self.off()
    
    def __str__(self):
        return f"SimpleLEDControl(pin={self.pin}, brightness={self.brightness}%)"


def demo_pwm_basic():
    """
    演示基本的 PWM 控制功能
    """
    print("=== PWM 基本控制演示 ===")
    print("这个演示展示了 PWM 的基本功能：初始化、启动、设置占空比、停止")
    
    try:
        # 创建 PWM 控制器
        print("\n1. 创建 PWM 控制器")
        pwm = SimplePWMControl(pin=7, frequency=1000)
        print(f"   PWM 控制器已创建: {pwm}")
        
        # 启动 PWM
        print("\n2. 启动 PWM")
        if pwm.start():
            print("   PWM 启动成功")
        else:
            print("   PWM 启动失败")
            return
        
        # 测试不同的占空比
        print("\n3. 测试不同占空比 (LED 亮度变化)")
        duty_cycles = [0, 25, 50, 75, 100, 75, 50, 25, 0]
        
        for duty in duty_cycles:
            print(f"   设置占空比: {duty}%")
            pwm.set_duty_cycle(duty)
            time.sleep(1)
        
        # 测试频率变化
        print("\n4. 测试频率变化 (LED 闪烁频率变化)")
        frequencies = [100, 500, 1000, 2000]
        
        for freq in frequencies:
            print(f"   设置频率: {freq}Hz")
            pwm.set_frequency(freq)
            pwm.set_duty_cycle(50)  # 50% 占空比
            time.sleep(2)
        
        # 停止 PWM
        print("\n5. 停止 PWM")
        pwm.stop()
        print("   PWM 已停止")
        
        # 显示状态
        print("\n6. PWM 状态信息")
        status = pwm.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 清理资源
        if 'pwm' in locals():
            pwm.cleanup()
        print("\n资源已清理")


def demo_led_basic():
    """
    演示基本的 LED 控制功能
    """
    print("\n\n=== LED 基本控制演示 ===")
    print("这个演示展示了 LED 控制的基本功能：开关、亮度调节")
    
    try:
        # 创建 LED 控制器
        print("\n1. 创建 LED 控制器")
        led = SimpleLEDControl(pin=7, max_brightness=80)  # 限制最大亮度为 80%
        print(f"   LED 控制器已创建: {led}")
        
        # 打开 LED
        print("\n2. 打开 LED")
        led.on(50)  # 50% 亮度
        print(f"   LED 已打开，当前亮度: {led.get_brightness()}%")
        time.sleep(2)
        
        # 调节亮度
        print("\n3. 调节 LED 亮度")
        brightness_levels = [10, 30, 60, 80, 100]  # 注意：100% 会被限制到 80%
        
        for brightness in brightness_levels:
            print(f"   设置亮度: {brightness}%")
            led.set_brightness(brightness)
            print(f"   实际亮度: {led.get_brightness()}%")
            time.sleep(1.5)
        
        # 关闭 LED
        print("\n4. 关闭 LED")
        led.off()
        print("   LED 已关闭")
        
        # 显示状态
        print("\n5. LED 状态信息")
        print(f"   当前亮度: {led.get_brightness()}%")
        print(f"   最大亮度限制: {led.max_brightness}%")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 清理资源
        if 'led' in locals():
            led.cleanup()
        print("\n资源已清理")


def demo_led_advanced():
    """
    演示 LED 高级功能
    """
    print("\n\n=== LED 高级功能演示 ===")
    print("这个演示展示了 LED 的高级功能：渐变、闪烁、呼吸灯")
    
    try:
        # 创建 LED 控制器
        print("\n1. 创建 LED 控制器")
        led = SimpleLEDControl(pin=7, max_brightness=90)
        print(f"   LED 控制器已创建: {led}")
        
        # 渐变效果
        print("\n2. 渐变效果演示")
        print("   从暗到亮...")
        for i in range(0, 101, 5):
            led.set_brightness(i)
            time.sleep(0.1)
        
        print("   从亮到暗...")
        for i in range(100, -1, -5):
            led.set_brightness(i)
            time.sleep(0.1)
        
        # 闪烁效果
        print("\n3. 闪烁效果演示")
        for i in range(5):
            led.on(80)
            time.sleep(0.3)
            led.off()
            time.sleep(0.3)
        
        # 呼吸灯效果
        print("\n4. 呼吸灯效果演示")
        print("   模拟呼吸灯效果...")
        for i in range(3):  # 3次呼吸周期
            # 渐亮
            for j in range(0, 81, 5):
                led.set_brightness(j)
                time.sleep(0.05)
            # 渐暗
            for j in range(80, -1, -5):
                led.set_brightness(j)
                time.sleep(0.05)
        
        # 关闭 LED
        print("\n5. 关闭 LED")
        led.off()
        print("   LED 已关闭")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 清理资源
        if 'led' in locals():
            led.cleanup()
        print("\n资源已清理")


def main():
    """
    主函数
    """
    print("🚀 Jetson Orin PWM 和 LED 控制演示")
    print("=" * 50)
    print("硬件要求:")
    print("- GPIO Pin 7 连接到 LED (通过 330Ω 电阻)")
    print("- 确保 LED 正极连接到 GPIO，负极连接到 GND")
    print("=" * 50)
    
    # 初始化 GPIO
    try:
        GPIO.setmode(GPIO.BOARD)
        print("✅ GPIO 初始化成功")
    except Exception as e:
        print(f"❌ GPIO 初始化失败: {e}")
        return
    
    try:
        # 运行演示
        demo_pwm_basic()
        demo_led_basic()
        demo_led_advanced()
        
        print("\n🎉 所有演示完成!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
    finally:
        # 清理 GPIO
        GPIO.cleanup()
        print("🧹 GPIO 资源已清理")


if __name__ == "__main__":
    main()