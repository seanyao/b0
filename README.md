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

### 2. 快速测试

1. **测试 GPIO 功能**:
   ```bash
   sudo python3 tools/tool_gpio_7.py
   ```

2. **测试 LED 控制**:
   ```bash
   python3 tools/tool_led_control.py
   ```

3. **测试舵机 PWM**:
   ```bash
   sudo python3 tools/tool_servo_pwm.py
   ```

4. **测试 PCA9685 舵机**:
   ```bash
   sudo python3 tools/tool_pca9685_servo.py
   ```

5. **检查 I2C 设备**:
   ```bash
   sudo python3 tools/tool_i2c_scan.py
   ```

## 🛠️ 测试工具集合

本项目包含各种硬件测试工具，用于验证 Jetson Orin 的硬件控制功能。

### GPIO 测试工具

- **`tool_gpio_7.py`** - GPIO 基本功能测试
  - 测试 GPIO Pin 7 的开关功能
  - 验证 LED 控制
  - 使用: `sudo python3 tools/tool_gpio_7.py`

### PWM 测试工具

- **`tool_servo_pwm.py`** - 软件 PWM 舵机测试
  - 使用 GPIO Pin 7 生成 PWM 信号
  - 测试舵机角度控制
  - 使用: `sudo python3 tools/tool_servo_pwm.py`

- **`tool_led_control.py`** - LED 控制工具
  - 使用 PCA9685 控制 LED 亮度
  - 支持开关和亮度调节
  - 使用: `python3 tools/tool_led_control.py`

### PCA9685 测试工具

- **`tool_pca9685_servo.py`** - PCA9685 舵机控制测试
  - 硬件 PWM 舵机控制
  - 16 通道 PWM 输出
  - 使用: `sudo python3 tools/tool_pca9685_servo.py`

- **`tool_pca9685_debug.py`** - PCA9685 调试工具
  - 诊断 PCA9685 连接和配置问题
  - 扫描所有 I2C 总线
  - 使用: `python3 tools/tool_pca9685_debug.py`

- **`tool_i2c_scan.py`** - I2C 设备扫描
  - 扫描 I2C 总线上的设备
  - 验证 PCA9685 连接状态
  - 使用: `sudo python3 tools/tool_i2c_scan.py`

- **`tool_servo_test.py`** - 舵机测试工具
  - 简化的舵机测试功能
  - 使用: `python3 tools/tool_servo_test.py`

### 开发工具

- **`git_cp.py`** - 智能 Git 提交助手
  - 自动分析代码变更
  - 生成合适的提交信息
  - 使用: `python3 tools/git_cp.py`

## 📚 源代码模块

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

### 3. `pca9685_control.py` - PCA9685 PWM 控制器
提供 PCA9685 硬件 PWM 控制功能。

**主要类：**
- **`PCA9685`**: 极简 PCA9685 控制器

**特性：**
- 16 通道 PWM 输出
- 舵机角度控制
- PWM 占空比控制



## 📋 硬件要求

- **Jetson Orin 开发板**
- **面包板**
- **LED 灯**（带 330Ω 电阻）
- **舵机**（可选）
- **12V 电源**
- **连接线**

## 🔌 硬件连接

### GPIO 测试连接
```
GPIO Pin 7 → 330Ω电阻 → LED正极 → LED负极 → GND
```

### 软件PWM舵机测试连接
```
GPIO Pin 7 → 舵机信号线
5V电源 → 舵机电源线
GND → 舵机地线 (共地)
```

### PCA9685测试连接
```
Jetson I2C:
  Pin 3 (SDA) → PCA9685 SDA
  Pin 5 (SCL) → PCA9685 SCL
  Pin 2 (5V)  → PCA9685 VCC
  Pin 6 (GND) → PCA9685 GND

PCA9685 → 舵机:
  通道0 PWM → 舵机信号线
  V+ → 舵机电源线 (独立5V)
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
- 大部分工具需要 `sudo` 权限
- 舵机需要独立的 5V 电源供电
- 确保所有设备共地连接
- 按 `Ctrl+C` 可以安全停止测试
- 建议在测试前备份重要数据
- 确保在 Jetson Orin 环境下运行

## 📞 问题解决

### 常见问题
1. **舵机无响应**: 检查信号线连接，使用 `tool_pca9685_debug.py` 诊断
2. **I2C设备未找到**: 使用 `tool_i2c_scan.py` 检查 I2C 设备
3. **工具权限问题**: 某些工具需要 `sudo` 权限

### 调试流程
1. 使用 `tool_i2c_scan.py` 检查 I2C 设备
2. 使用 `tool_pca9685_debug.py` 诊断 PCA9685
3. 使用 `tool_gpio_7.py` 测试基础 GPIO 功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。