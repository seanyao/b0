#!/usr/bin/env python3
"""
测试包初始化文件

确保测试包能够正确导入和运行。
"""

# 测试包版本
__version__ = '1.0.0'

# 测试配置
TEST_CONFIG = {
    'mock_gpio': True,  # 是否模拟 GPIO
    'verbose': True,    # 详细输出
    'coverage': True,   # 代码覆盖率
}