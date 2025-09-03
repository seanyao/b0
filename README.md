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
├── src/                         # 源代码目录
│   ├── __init__.py             # 包初始化文件
│   ├── gpio_control.py         # GPIO 控制器类
│   └── software_pwm.py         # 软件 PWM 控制类
├── tools/                       # 测试工具集合
│   ├── tool_gpio_7.py         # GPIO 测试工具
│   ├── tool_servo_pwm.py      # 舵机 PWM 测试工具
│   └── git_cp.py              # 智能 Git 提交助手
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

### 2. 使用测试工具
```bash
# GPIO 测试
python tools/tool_gpio_7.py

# LED PWM 测试
python tools/tool_led_pwm.py

# 舵机 PWM 测试
python tools/tool_servo_pwm.py
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

### 1. `gpio_control.py` - GPIO 控制器类
提供基础的 GPIO 操作功能。

**主要类：**
- **`GPIOControl`**: 基础 GPIO 控制，支持高低电平切换

**特性：**
- 支持 BOARD 和 BCM 两种引脚编号模式
- 简单的引脚设置和清理

### 2. `software_pwm.py` - 软件 PWM 控制类
提供软件 PWM 功能。

**主要类：**
- **`SoftwarePWM`**: 软件 PWM 生成，支持频率和占空比调节

**特性：**
- 内置线程管理和资源清理
- 支持占空比动态调节

### 3. `tool_gpio_7.py` - GPIO 测试工具
测试 GPIO 引脚的基本功能，验证硬件连接。



### 3. `tool_servo_pwm.py` - 舵机 PWM 测试工具
测试舵机的 PWM 控制功能，包括：
- 角度控制（0°, 90°, 180°）
- PWM 信号验证

**使用方法：**
```bash
python tools/tool_servo_pwm.py
```

### 4. `git_cp.py` - 智能 Git 提交助手
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

### 使用 GPIO 控制类
```python
from src.gpio_control import GPIOControl, SoftwarePWM

# 基础 GPIO 控制
with GPIOControl(pin=7, mode='BOARD', direction='OUT') as gpio:
    gpio.high()      # 设置高电平
    time.sleep(1)
    gpio.low()       # 设置低电平
    gpio.toggle()    # 切换状态

# 软件 PWM 控制
with SoftwarePWM(pin=7, frequency=50) as pwm:
    pwm.start(25)    # 启动 PWM，25% 占空比
    time.sleep(2)
    pwm.set_duty_cycle(75)  # 改变占空比
    time.sleep(2)
    pwm.stop()       # 停止 PWM
```

### 测试工具使用
```bash
# 测试 GPIO
python tools/tool_gpio_7.py

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