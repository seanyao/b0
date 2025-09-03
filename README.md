# Jetson Orin 硬件控制项目

一个用于 Jetson Orin 开发板的硬件控制项目，提供 GPIO、PWM、LED 和舵机控制功能。

## 🎯 项目目标

- 学习 Jetson Orin 的硬件控制
- 掌握 GPIO 和 PWM 的基本操作
- 实现 LED 亮度控制和舵机角度控制
- 提供简单易用的测试工具集合

## 🏗️ 项目结构

```
b0/
├── README.md                    # 项目说明文档
├── docs/                        # 文档目录
│   └── hardware.md              # 硬件连接说明
├── tools/                       # 测试工具和示例
│   ├── basic_usage.py          # 基本使用示例
│   ├── tool_gpio_7.py         # GPIO 测试工具
│   ├── tool_led_pwm.py        # LED PWM 测试工具
│   ├── tool_servo_pwm.py      # 舵机 PWM 测试工具
│   ├── git_cp.py              # 智能 Git 提交助手
│   └── README.md              # 工具使用说明
├── PCA9685ServoControl.py      # 舵机控制代码
├── requirements.txt             # Python 依赖
└── .gitignore                  # Git 忽略文件
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 查看硬件连接说明
cat docs/hardware.md
```

### 2. 运行基本示例
```bash
# 运行基本使用示例
python tools/basic_usage.py
```

### 3. 使用测试工具
```bash
# GPIO 测试
python tools/tool_gpio_7.py

# LED PWM 测试
python tools/tool_led_pwm.py

# 舵机 PWM 测试
python tools/tool_servo_pwm.py
```

## 🛠️ 工具详解

### 1. `basic_usage.py` - 基本使用示例
演示 PWM 和 LED 控制的基本功能，包括：
- PWM 基本控制（启动、停止、占空比调节、频率调节）
- LED 基本控制（开关、亮度调节）
- LED 高级功能（渐变、闪烁、呼吸灯效果）

**使用方法：**
```bash
python tools/basic_usage.py
```

### 2. `tool_gpio_7.py` - GPIO 测试工具
测试 GPIO 引脚的基本功能，验证硬件连接。

**使用方法：**
```bash
python tools/tool_gpio_7.py
```

### 3. `tool_led_pwm.py` - LED PWM 测试工具
测试 LED 的 PWM 控制功能，包括：
- 不同占空比的亮度控制
- 舵机频率 PWM (50Hz) 测试
- 连续变化测试

**使用方法：**
```bash
python tools/tool_led_pwm.py
```

### 4. `tool_servo_pwm.py` - 舵机 PWM 测试工具
测试舵机的 PWM 控制功能，包括：
- 角度控制（0°, 90°, 180°）
- PWM 信号验证

**使用方法：**
```bash
python tools/tool_servo_pwm.py
```

### 5. `git_cp.py` - 智能 Git 提交助手
自动分析代码变更并生成合适的 commit message，一键执行 add、commit 和 push。

**使用方法：**
```bash
# 直接执行，无需任何参数
python tools/git_cp.py
```

**功能特点：**
- 自动分析文件变更类型（修改、新增、删除、重命名、未跟踪）
- 智能分类文件（文档、源代码、测试、工具、配置等）
- 生成简洁有效的 commit message
- 一键执行 add、commit、push 操作
- 无需交互确认，直接执行

## 📋 硬件要求

- **Jetson Orin 开发板**
- **面包板**
- **LED 灯**（带 330Ω 电阻）
- **舵机**（可选）
- **12V 电源**
- **连接线**

## 🔌 硬件连接

### LED 连接
```
GPIO Pin 7 → 330Ω电阻 → LED正极 → LED负极 → GND
```

### 舵机连接
```
GPIO Pin 7 → 舵机信号线
5V/12V → 舵机电源线
GND → 舵机地线
```

详细的硬件连接说明请参考 `docs/hardware.md`。

## 📚 使用示例

### 基本 PWM 控制
```python
# 运行基本示例
python tools/basic_usage.py
```

### 测试工具使用
```bash
# 测试 GPIO
python tools/tool_gpio_7.py

# 测试 LED PWM
python tools/tool_led_pwm.py

# 测试舵机 PWM
python tools/tool_servo_pwm.py
```

### 智能 Git 提交
```bash
# 自动提交所有变更
python tools/git_cp.py
```

## ⚠️ 注意事项

- 运行硬件测试工具前，请确保硬件连接正确
- 某些工具可能需要 root 权限（如 GPIO 访问）
- 建议在测试前备份重要数据
- 确保在 Jetson Orin 环境下运行

## 🔄 开发进度

- [x] 项目基础结构
- [x] 硬件连接文档
- [x] PWM 控制功能
- [x] LED 亮度控制
- [x] 测试工具集合
- [x] 智能 Git 提交助手
- [x] 使用示例和教程

## ✅ 测试状态

- ✅ 所有测试工具正常工作
- ✅ PWM 控制功能完整
- ✅ LED 亮度控制功能完整
- ✅ 基本使用示例可运行
- ✅ 智能 Git 提交助手可用

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。