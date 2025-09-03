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
├── tools/                 # 测试工具和示例
│   ├── basic_usage.py    # 基本使用示例
│   ├── tool_gpio_7.py   # GPIO 测试工具
│   ├── tool_led_pwm.py  # LED PWM 测试工具
│   ├── tool_servo_pwm.py # 舵机 PWM 测试工具
│   ├── git_cp.py         # 智能 Git 提交助手
│   └── README.md         # 工具使用说明
└── requirements.txt       # Python 依赖
```

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 查看硬件连接：`docs/hardware.md`
3. 运行基本示例：`python tools/basic_usage.py`
4. 使用测试工具：`python tools/tool_led_pwm.py`

## 开发进度

- [x] 项目基础结构
- [x] 硬件连接文档
- [x] PWM 控制功能
- [x] LED 亮度控制
- [x] 测试工具集合
- [x] 智能 Git 提交助手
- [x] 使用示例和教程

## 测试状态

✅ 所有测试工具正常工作
✅ PWM 控制功能完整
✅ LED 亮度控制功能完整
✅ 基本使用示例可运行
✅ 智能 Git 提交助手可用

## 使用方法

### 基本使用

```python
# 运行基本示例
python tools/basic_usage.py

# 使用测试工具
python tools/tool_led_pwm.py
python tools/tool_servo_pwm.py
python tools/tool_gpio_7.py
```

### 智能 Git 提交

```bash
# 自动提交所有变更
python tools/git_cp.py

# 查看工具使用说明
python tools/git_cp.py --help
```