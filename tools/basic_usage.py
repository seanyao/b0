#!/usr/bin/env python3
"""
Jetson Orin PWM LED 控制基本使用示例

演示如何使用 PWM 控制 LED 亮度和特效。
这个示例展示了从最基本的功能开始，逐步学习 PWM 控制。

运行前请确保:
1. 硬件连接正确 (参考 docs/hardware.md)
2. 已安装依赖 (pip install -r requirements.txt)
3. 在 Jetson Orin 上运行
"""

import sys
import time
import os

# 添加源代码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jetson import PWMControl, LEDControl


def demo_pwm_basic():
    """
    演示基本的 PWM 控制功能
    """
    print("=== PWM 基本控制演示 ===")
    print("这个演示展示了 PWM 的基本功能：初始化、启动、设置占空比、停止")
    
    try:
        # 创建 PWM 控制器
        print("\n1. 创建 PWM 控制器")
        pwm = PWMControl(pin=32, frequency=1000)
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
        led = LEDControl(pin=33, max_brightness=80)  # 限制最大亮度为 80%
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
        print(f"   LED 已关闭，当前亮度: {led.get_brightness()}%")
        time.sleep(1)
        
        # 显示状态
        print("\n5. LED 状态信息")
        status = led.get_status()
        for key, value in status.items():
            if key != 'pwm_status':  # 简化输出
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 清理资源
        if 'led' in locals():
            led.cleanup()
        print("\n资源已清理")


def demo_led_effects():
    """
    演示 LED 特效功能
    """
    print("\n\n=== LED 特效演示 ===")
    print("这个演示展示了 LED 的各种特效：渐变、闪烁、呼吸灯")
    
    try:
        # 创建 LED 控制器
        print("\n1. 创建 LED 控制器")
        led = LEDControl(pin=32)
        print(f"   LED 控制器已创建: {led}")
        
        # 渐变效果
        print("\n2. 渐变效果演示")
        led.on(0)  # 从 0% 开始
        print("   从 0% 渐变到 80%")
        led.fade_to(80, duration=3)
        time.sleep(3.5)
        
        print("   从 80% 渐变到 20%")
        led.fade_to(20, duration=2)
        time.sleep(2.5)
        
        # 闪烁效果
        print("\n3. 闪烁效果演示")
        print("   快速闪烁 5 次")
        led.blink(times=5, on_time=0.2, off_time=0.2, brightness=70)
        time.sleep(2.5)
        
        print("   慢速闪烁 3 次")
        led.blink(times=3, on_time=0.8, off_time=0.8, brightness=90)
        time.sleep(4)
        
        # 呼吸灯效果
        print("\n4. 呼吸灯效果演示")
        print("   呼吸灯效果 (10 秒)")
        led.breathe(period=2.0, min_brightness=5, max_brightness=85)
        
        # 运行 10 秒
        for i in range(10):
            time.sleep(1)
            if i % 2 == 0:
                print(f"   运行中... ({i+1}/10 秒)")
        
        # 停止呼吸灯
        led.stop_animation()
        print("   呼吸灯效果已停止")
        
        # 关闭 LED
        led.off()
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 清理资源
        if 'led' in locals():
            led.cleanup()
        print("\n资源已清理")


def demo_context_manager():
    """
    演示上下文管理器的使用
    """
    print("\n\n=== 上下文管理器演示 ===")
    print("这个演示展示了如何使用 with 语句自动管理资源")
    
    try:
        # 使用 PWM 上下文管理器
        print("\n1. PWM 上下文管理器")
        with PWMControl(pin=7, frequency=1000) as pwm:
            print(f"   PWM 控制器: {pwm}")
            pwm.start()
            
            # 简单的亮度变化
            for duty in [0, 50, 100, 50, 0]:
                print(f"   占空比: {duty}%")
                pwm.set_duty_cycle(duty)
                time.sleep(0.8)
        
        print("   PWM 资源已自动清理")
        
        # 使用 LED 上下文管理器
        print("\n2. LED 上下文管理器")
        with LEDControl(pin=7) as led:
            print(f"   LED 控制器: {led}")
            
            # 简单的特效组合
            led.on(30)
            time.sleep(1)
            
            led.fade_to(80, duration=2)
            time.sleep(2.5)
            
            led.blink(times=3, on_time=0.3, off_time=0.3)
            time.sleep(2.5)
            
            led.off()
        
        print("   LED 资源已自动清理")
        
    except Exception as e:
        print(f"错误: {e}")


def demo_error_handling():
    """
    演示错误处理和边界情况
    """
    print("\n\n=== 错误处理演示 ===")
    print("这个演示展示了如何处理各种错误情况")
    
    try:
        led = LEDControl(pin=33)
        
        print("\n1. 测试无效参数")
        
        # 测试无效亮度
        print("   尝试设置无效亮度 (150%)")
        result = led.set_brightness(150)
        print(f"   结果: {result} (应该为 False)")
        
        print("   尝试设置负亮度 (-10%)")
        result = led.set_brightness(-10)
        print(f"   结果: {result} (应该为 False)")
        
        # 测试未启动状态下的操作
        print("\n2. 测试未启动状态下的操作")
        print("   尝试在未启动状态下设置亮度")
        result = led.set_brightness(50)
        print(f"   结果: {result} (应该为 False)")
        
        # 正常启动后测试
        print("\n3. 正常启动后测试")
        led.on(50)
        print(f"   LED 已启动，当前亮度: {led.get_brightness()}%")
        
        # 测试有效范围
        print("\n4. 测试有效范围")
        valid_values = [0, 25, 50, 75, 100]
        for value in valid_values:
            result = led.set_brightness(value)
            print(f"   设置亮度 {value}%: {result} (当前: {led.get_brightness()}%)")
            time.sleep(0.5)
        
        led.cleanup()
        
    except Exception as e:
        print(f"错误: {e}")
        if 'led' in locals():
            led.cleanup()


def main():
    """
    主函数 - 运行所有演示
    """
    print("Jetson Orin PWM LED 控制基本使用示例")
    print("=====================================")
    print("\n这个示例将演示 PWM 和 LED 控制的各种功能")
    print("请确保硬件连接正确，LED 连接到 GPIO 33 引脚")
    
    try:
        # 询问用户是否继续
        response = input("\n按 Enter 继续，或输入 'q' 退出: ").strip().lower()
        if response == 'q':
            print("用户取消")
            return
        
        # 运行各个演示
        demo_pwm_basic()
        
        input("\n按 Enter 继续下一个演示...")
        demo_led_basic()
        
        input("\n按 Enter 继续下一个演示...")
        demo_led_effects()
        
        input("\n按 Enter 继续下一个演示...")
        demo_context_manager()
        
        input("\n按 Enter 继续下一个演示...")
        demo_error_handling()
        
        print("\n\n=== 演示完成 ===")
        print("恭喜！你已经学会了 PWM LED 控制的基本用法")
        print("\n下一步可以尝试:")
        print("1. 修改引脚号，控制多个 LED")
        print("2. 调整 PWM 频率，观察效果变化")
        print("3. 创建自定义的 LED 特效")
        print("4. 使用命令行工具: python src/jetson/cli.py --help")
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n程序错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()