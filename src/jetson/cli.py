#!/usr/bin/env python3
"""
LED 控制命令行界面

提供简单易用的命令行界面来控制 LED 亮度和特效。

使用示例:
    python cli.py --pin 33 --on --brightness 75
    python cli.py --pin 33 --fade-to 25 --duration 3
    python cli.py --pin 33 --blink --times 5 --interval 0.5
    python cli.py --pin 33 --breathe --period 2 --min-brightness 10 --max-brightness 80
    python cli.py --pin 33 --off
"""

import argparse
import sys
import time
import signal
import os
from typing import Optional

# 添加源代码路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from led_control import LEDControl


class LEDControlCLI:
    """
    LED 控制命令行界面类
    """
    
    def __init__(self):
        self.led_control: Optional[LEDControl] = None
        self.running = True
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        信号处理器，用于优雅退出
        
        Args:
            signum: 信号编号
            frame: 当前栈帧
        """
        print("\n收到退出信号，正在清理资源...")
        self.running = False
        if self.led_control:
            self.led_control.cleanup()
        sys.exit(0)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """
        创建命令行参数解析器
        
        Returns:
            argparse.ArgumentParser: 参数解析器
        """
        parser = argparse.ArgumentParser(
            description='Jetson Orin PWM LED 控制工具',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
使用示例:
  %(prog)s --pin 33 --on --brightness 75          # 打开LED，设置75%%亮度
  %(prog)s --pin 33 --fade-to 25 --duration 3     # 3秒内渐变到25%%亮度
  %(prog)s --pin 33 --blink --times 5 --interval 0.5  # 闪烁5次，间隔0.5秒
  %(prog)s --pin 33 --breathe --period 2          # 呼吸灯效果，周期2秒
  %(prog)s --pin 33 --off                         # 关闭LED
  %(prog)s --pin 33 --status                      # 查看LED状态
  %(prog)s --pin 33 --interactive                 # 进入交互模式
            """
        )
        
        # 基本参数
        parser.add_argument(
            '--pin', '-p',
            type=int,
            default=33,
            help='GPIO 引脚号 (默认: 33)'
        )
        
        parser.add_argument(
            '--frequency', '-f',
            type=int,
            default=1000,
            help='PWM 频率 (Hz) (默认: 1000)'
        )
        
        parser.add_argument(
            '--max-brightness',
            type=float,
            default=100.0,
            help='最大亮度限制 (0-100%%) (默认: 100)'
        )
        
        # 控制命令
        control_group = parser.add_mutually_exclusive_group()
        
        control_group.add_argument(
            '--on',
            action='store_true',
            help='打开 LED'
        )
        
        control_group.add_argument(
            '--off',
            action='store_true',
            help='关闭 LED'
        )
        
        control_group.add_argument(
            '--fade-to',
            type=float,
            metavar='BRIGHTNESS',
            help='渐变到指定亮度 (0-100%%)'
        )
        
        control_group.add_argument(
            '--blink',
            action='store_true',
            help='LED 闪烁'
        )
        
        control_group.add_argument(
            '--breathe',
            action='store_true',
            help='呼吸灯效果'
        )
        
        control_group.add_argument(
            '--status',
            action='store_true',
            help='显示 LED 状态'
        )
        
        control_group.add_argument(
            '--interactive', '-i',
            action='store_true',
            help='进入交互模式'
        )
        
        # 参数选项
        parser.add_argument(
            '--brightness', '-b',
            type=float,
            help='亮度 (0-100%%)'
        )
        
        parser.add_argument(
            '--duration', '-d',
            type=float,
            default=1.0,
            help='渐变持续时间 (秒) (默认: 1.0)'
        )
        
        parser.add_argument(
            '--times', '-t',
            type=int,
            default=1,
            help='闪烁次数 (默认: 1)'
        )
        
        parser.add_argument(
            '--interval',
            type=float,
            default=0.5,
            help='闪烁间隔 (秒) (默认: 0.5)'
        )
        
        parser.add_argument(
            '--period',
            type=float,
            default=2.0,
            help='呼吸灯周期 (秒) (默认: 2.0)'
        )
        
        parser.add_argument(
            '--min-brightness',
            type=float,
            default=0.0,
            help='呼吸灯最小亮度 (0-100%%) (默认: 0)'
        )
        
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='详细输出'
        )
        
        return parser
    
    def execute_command(self, args) -> bool:
        """
        执行命令行命令
        
        Args:
            args: 解析后的命令行参数
            
        Returns:
            bool: 执行成功返回 True
        """
        try:
            # 创建 LED 控制器
            self.led_control = LEDControl(
                pin=args.pin,
                frequency=args.frequency,
                max_brightness=args.max_brightness
            )
            
            if args.verbose:
                print(f"LED 控制器已创建: Pin={args.pin}, Freq={args.frequency}Hz, MaxBrightness={args.max_brightness}%")
            
            # 执行相应命令
            if args.on:
                return self._cmd_on(args)
            elif args.off:
                return self._cmd_off(args)
            elif args.fade_to is not None:
                return self._cmd_fade_to(args)
            elif args.blink:
                return self._cmd_blink(args)
            elif args.breathe:
                return self._cmd_breathe(args)
            elif args.status:
                return self._cmd_status(args)
            elif args.interactive:
                return self._cmd_interactive(args)
            else:
                print("错误: 请指定一个控制命令")
                return False
                
        except Exception as e:
            print(f"错误: {e}")
            return False
        finally:
            if self.led_control:
                self.led_control.cleanup()
    
    def _cmd_on(self, args) -> bool:
        """
        执行打开 LED 命令
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 执行成功返回 True
        """
        brightness = args.brightness if args.brightness is not None else args.max_brightness
        
        if self.led_control.on(brightness):
            print(f"LED 已打开，亮度: {brightness}%")
            return True
        else:
            print("错误: 无法打开 LED")
            return False
    
    def _cmd_off(self, args) -> bool:
        """
        执行关闭 LED 命令
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 执行成功返回 True
        """
        if self.led_control.off():
            print("LED 已关闭")
            return True
        else:
            print("错误: 无法关闭 LED")
            return False
    
    def _cmd_fade_to(self, args) -> bool:
        """
        执行渐变命令
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 执行成功返回 True
        """
        target_brightness = args.fade_to
        duration = args.duration
        
        # 确保 LED 已打开
        if not self.led_control.is_on:
            self.led_control.on(0)
        
        if self.led_control.fade_to(target_brightness, duration):
            print(f"开始渐变到 {target_brightness}%，持续时间 {duration} 秒")
            
            # 等待渐变完成
            time.sleep(duration + 0.1)
            
            print(f"渐变完成，当前亮度: {self.led_control.get_brightness()}%")
            return True
        else:
            print("错误: 无法启动渐变")
            return False
    
    def _cmd_blink(self, args) -> bool:
        """
        执行闪烁命令
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 执行成功返回 True
        """
        times = args.times
        interval = args.interval
        brightness = args.brightness if args.brightness is not None else args.max_brightness
        
        if self.led_control.blink(times=times, on_time=interval, off_time=interval, brightness=brightness):
            print(f"开始闪烁 {times} 次，间隔 {interval} 秒，亮度 {brightness}%")
            
            # 等待闪烁完成
            total_time = times * (interval * 2) + 0.5
            time.sleep(total_time)
            
            print("闪烁完成")
            return True
        else:
            print("错误: 无法启动闪烁")
            return False
    
    def _cmd_breathe(self, args) -> bool:
        """
        执行呼吸灯命令
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 执行成功返回 True
        """
        period = args.period
        min_brightness = args.min_brightness
        max_brightness = args.brightness if args.brightness is not None else args.max_brightness
        
        if self.led_control.breathe(period=period, min_brightness=min_brightness, max_brightness=max_brightness):
            print(f"开始呼吸灯效果，周期 {period} 秒，亮度范围 {min_brightness}%-{max_brightness}%")
            print("按 Ctrl+C 停止")
            
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
            
            self.led_control.stop_animation()
            print("\n呼吸灯效果已停止")
            return True
        else:
            print("错误: 无法启动呼吸灯效果")
            return False
    
    def _cmd_status(self, args) -> bool:
        """
        显示 LED 状态
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 总是返回 True
        """
        status = self.led_control.get_status()
        
        print("LED 状态信息:")
        print(f"  引脚: {status['pin']}")
        print(f"  频率: {status['frequency']} Hz")
        print(f"  最大亮度: {status['max_brightness']}%")
        print(f"  当前亮度: {status['current_brightness']}%")
        print(f"  状态: {'开启' if status['is_on'] else '关闭'}")
        print(f"  动画: {'运行中' if status['is_animating'] else '静态'}")
        
        if args.verbose:
            print(f"  PWM 状态: {status['pwm_status']}")
        
        return True
    
    def _cmd_interactive(self, args) -> bool:
        """
        进入交互模式
        
        Args:
            args: 命令行参数
            
        Returns:
            bool: 总是返回 True
        """
        print("进入交互模式 (输入 'help' 查看帮助，'quit' 退出)")
        print(f"LED 控制器: Pin={args.pin}, Freq={args.frequency}Hz")
        
        while self.running:
            try:
                command = input("LED> ").strip().lower()
                
                if not command:
                    continue
                
                if command in ['quit', 'exit', 'q']:
                    break
                elif command == 'help':
                    self._show_interactive_help()
                elif command == 'status':
                    self._cmd_status(args)
                elif command.startswith('on'):
                    parts = command.split()
                    brightness = float(parts[1]) if len(parts) > 1 else args.max_brightness
                    if self.led_control.on(brightness):
                        print(f"LED 已打开，亮度: {brightness}%")
                    else:
                        print("错误: 无法打开 LED")
                elif command == 'off':
                    if self.led_control.off():
                        print("LED 已关闭")
                    else:
                        print("错误: 无法关闭 LED")
                elif command.startswith('brightness'):
                    parts = command.split()
                    if len(parts) > 1:
                        brightness = float(parts[1])
                        if self.led_control.set_brightness(brightness):
                            print(f"亮度已设置为: {brightness}%")
                        else:
                            print("错误: 无法设置亮度")
                    else:
                        print(f"当前亮度: {self.led_control.get_brightness()}%")
                elif command.startswith('fade'):
                    parts = command.split()
                    if len(parts) >= 2:
                        target = float(parts[1])
                        duration = float(parts[2]) if len(parts) > 2 else 1.0
                        if not self.led_control.is_on:
                            self.led_control.on(0)
                        if self.led_control.fade_to(target, duration):
                            print(f"开始渐变到 {target}%，持续时间 {duration} 秒")
                        else:
                            print("错误: 无法启动渐变")
                    else:
                        print("用法: fade <目标亮度> [持续时间]")
                elif command.startswith('blink'):
                    parts = command.split()
                    times = int(parts[1]) if len(parts) > 1 else 3
                    interval = float(parts[2]) if len(parts) > 2 else 0.5
                    brightness = float(parts[3]) if len(parts) > 3 else args.max_brightness
                    if self.led_control.blink(times=times, on_time=interval, off_time=interval, brightness=brightness):
                        print(f"开始闪烁 {times} 次")
                    else:
                        print("错误: 无法启动闪烁")
                elif command == 'breathe':
                    if self.led_control.breathe():
                        print("开始呼吸灯效果 (输入 'stop' 停止)")
                    else:
                        print("错误: 无法启动呼吸灯效果")
                elif command == 'stop':
                    self.led_control.stop_animation()
                    print("动画已停止")
                else:
                    print(f"未知命令: {command}")
                    print("输入 'help' 查看帮助")
                    
            except KeyboardInterrupt:
                break
            except ValueError as e:
                print(f"参数错误: {e}")
            except Exception as e:
                print(f"错误: {e}")
        
        print("退出交互模式")
        return True
    
    def _show_interactive_help(self):
        """
        显示交互模式帮助信息
        """
        help_text = """
交互模式命令:
  on [亮度]              - 打开 LED，可选指定亮度 (0-100)
  off                    - 关闭 LED
  brightness [值]        - 设置或查看亮度
  fade <目标> [时间]     - 渐变到目标亮度
  blink [次数] [间隔] [亮度] - LED 闪烁
  breathe                - 呼吸灯效果
  stop                   - 停止当前动画
  status                 - 显示 LED 状态
  help                   - 显示此帮助信息
  quit/exit/q            - 退出交互模式

示例:
  on 75                  - 以 75% 亮度打开 LED
  fade 25 2              - 2 秒内渐变到 25% 亮度
  blink 5 0.3 80         - 以 80% 亮度闪烁 5 次，间隔 0.3 秒
        """
        print(help_text)


def main():
    """
    主函数
    """
    cli = LEDControlCLI()
    parser = cli.create_parser()
    
    try:
        args = parser.parse_args()
        
        # 验证参数
        if args.pin not in [32, 33, 35, 37, 38, 40]:
            print(f"警告: GPIO 引脚 {args.pin} 可能不支持 PWM")
        
        if not (0 <= args.max_brightness <= 100):
            print("错误: 最大亮度必须在 0-100% 范围内")
            return 1
        
        # 执行命令
        success = cli.execute_command(args)
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n用户中断")
        return 0
    except Exception as e:
        print(f"程序错误: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())