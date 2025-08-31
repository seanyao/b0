# Jetson Orin PWM LED 控制项目

## 项目简介

这是一个学习项目，用于了解如何使用 Jetson Orin 通过 PWM 控制 LED 亮度。项目采用分离供电设计，Jetson Orin 和面包板分别使用 12V 供电。

## 学习目标

- 掌握 PWM (脉宽调制) 的基本原理和应用
- 学习分离供电系统的设计和实现
- 理解嵌入式系统中的硬件控制

## 项目特点

- 遵循 MVP (最小可行产品) 原则
- 采用 TDD 开发方法，所有代码都可测试
- 从最简单的功能开始，逐步扩展

## 硬件清单

- Jetson Orin 开发板
- 面包板
- LED 灯
- 12V 电源 (2个)
- 连接线
- 电阻

## 项目结构

```
b0/
├── README.md              # 项目说明
├── docs/                  # 文档目录
│   └── hardware.md        # 硬件连接说明
├── src/                   # 源代码目录
│   └── jetson/           # Jetson 相关代码
│       ├── pwm_control.py # PWM 控制核心类
│       ├── led_control.py # LED 控制类
│       └── cli.py         # 命令行界面
├── tests/                 # 测试目录
│   ├── test_pwm.py       # PWM 控制测试
│   └── test_led.py       # LED 控制测试
├── examples/              # 使用示例
│   └── basic_usage.py    # 基本使用示例
└── requirements.txt       # Python 依赖
```

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 查看硬件连接：`docs/hardware.md`
3. 运行基本示例：`python examples/basic_usage.py`
4. 运行测试：`python -m pytest tests/`

## 开发进度

- [x] 项目基础结构
- [x] 硬件连接文档
- [x] PWM 控制核心功能
- [x] 单元测试
- [x] LED 亮度控制
- [x] 集成测试
- [x] 命令行界面
- [x] 使用示例和教程

## 测试状态

✅ 所有单元测试通过 (38/38)
✅ PWM 控制功能完整
✅ LED 亮度控制功能完整
✅ 命令行界面可用
✅ 使用示例可运行

## 使用方法

### 基本使用

```python
from jetson import LEDControl

# 创建 LED 控制器
with LEDControl(pin=33) as led:
    led.on(75)  # 75% 亮度
    led.fade_to(25, duration=2)  # 2秒渐变到25%
    led.blink(times=5, interval=0.5)  # 闪烁5次
    led.breathe(period=3)  # 呼吸灯效果
```

### 命令行使用

```bash
# 打开LED，设置75%亮度
python src/jetson/cli.py --pin 33 --on --brightness 75

# 渐变效果
python src/jetson/cli.py --pin 33 --fade-to 25 --duration 3

# 闪烁效果
python src/jetson/cli.py --pin 33 --blink --times 5 --interval 0.5

# 呼吸灯效果
python src/jetson/cli.py --pin 33 --breathe --period 2

# 交互模式
python src/jetson/cli.py --pin 33 --interactive
```