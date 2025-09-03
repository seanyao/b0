# 测试工具集合

本目录包含各种硬件测试工具，用于验证 Jetson Orin 的硬件控制功能。

## 🛠️ 工具列表

### GPIO 测试工具

- **`tool_gpio_7.py`** - GPIO 基本功能测试
  - 测试 GPIO Pin 7 的开关功能
  - 验证 LED 控制
  - 使用: `sudo python3 tool_gpio_7.py`

### PWM 测试工具

- **`tool_servo_pwm.py`** - 软件 PWM 舵机测试
  - 使用 GPIO Pin 7 生成 PWM 信号
  - 测试舵机角度控制
  - 使用: `sudo python3 tool_servo_pwm.py`

### PCA9685 测试工具

- **`tool_pca9685_servo.py`** - PCA9685 舵机控制测试
  - 硬件 PWM 舵机控制
  - 16 通道 PWM 输出
  - 使用: `sudo python3 tool_pca9685_servo.py`

- **`tool_i2c_scan.py`** - I2C 设备扫描
  - 扫描 I2C 总线上的设备
  - 验证 PCA9685 连接状态
  - 使用: `sudo python3 tool_i2c_scan.py`

### 开发工具

- **`git_cp.py`** - 智能 Git 提交助手
  - 自动分析代码变更
  - 生成合适的提交信息
  - 使用: `python3 git_cp.py`

## 🔌 硬件连接要求

### GPIO 测试
```
GPIO Pin 7 → 330Ω电阻 → LED正极 → LED负极 → GND
```

### 软件PWM舵机测试
```
GPIO Pin 7 → 舵机信号线
5V电源 → 舵机电源线
GND → 舵机地线 (共地)
```

### PCA9685测试
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

## ⚠️ 注意事项

- 运行硬件测试工具前，请确保硬件连接正确
- 大部分工具需要 `sudo` 权限
- 舵机需要独立的 5V 电源供电
- 确保所有设备共地连接
- 按 `Ctrl+C` 可以安全停止测试

## 🚀 快速开始

1. **检查 I2C 设备**:
   ```bash
   sudo python3 tool_i2c_scan.py
   ```

2. **测试 GPIO 功能**:
   ```bash
   sudo python3 tool_gpio_7.py
   ```

3. **测试 PCA9685 舵机**:
   ```bash
   sudo python3 tool_pca9685_servo.py
   ```

## 📝 开发说明

所有工具遵循项目的极简设计原则：
- 单一职责，专注特定功能
- 最小化依赖
- 清晰的错误提示
- 优雅的资源清理