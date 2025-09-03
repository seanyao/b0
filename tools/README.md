# 测试工具集合

这个文件夹包含了用于测试各种物理组件的工具脚本。

## 工具列表

### 1. `git_cp.py` - 智能 Git 提交助手
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

### 2. `tool_gpio_7.py` - GPIO 测试工具
测试 GPIO 引脚的基本功能。

### 3. `tool_led_pwm.py` - LED PWM 测试工具
测试 LED 的 PWM 控制功能，包括亮度调节、渐变效果等。

### 4. `tool_servo_pwm.py` - 舵机 PWM 测试工具
测试舵机的 PWM 控制功能，包括角度控制等。

### 5. `basic_usage.py` - 基本使用示例
演示 PWM 控制的基本功能和使用方法。

## 快速开始

1. 确保已安装所需依赖：`pip install -r requirements.txt`
2. 根据需要选择合适的测试工具
3. 运行工具进行测试

## 注意事项

- 运行硬件测试工具前，请确保硬件连接正确
- 某些工具可能需要 root 权限（如 GPIO 访问）
- 建议在测试前备份重要数据
