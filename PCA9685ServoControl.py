import smbus
import time

class PCA9685ServoControl:
    def __init__(self, address=0x40, channel=0):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.channel = channel
        self.init_pca9685()
    
    def init_pca9685(self):
        # 设置 PWM 频率为 50Hz（舵机标准）
        self.set_pwm_freq(50)
    
    def set_pwm_freq(self, freq):
        prescale = int(25000000.0 / (4096 * freq) - 1)
        old_mode = self.bus.read_byte_data(self.address, 0x00)
        self.bus.write_byte_data(self.address, 0x00, (old_mode & 0x7F) | 0x10)
        self.bus.write_byte_data(self.address, 0xFE, prescale)
        self.bus.write_byte_data(self.address, 0x00, old_mode)
        time.sleep(0.005)
        self.bus.write_byte_data(self.address, 0x00, old_mode | 0x80)
    
    def set_servo_angle(self, angle):
        # 将角度转换为 PWM 值
        # 0° = ~150, 180° = ~600 (根据舵机调整)
        pulse = int(150 + (angle / 180.0) * 450)
        self.set_pwm(self.channel, 0, pulse)
    
    def set_pwm(self, channel, on, off):
        reg_base = 0x06 + 4 * channel
        self.bus.write_byte_data(self.address, reg_base, on & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 1, on >> 8)
        self.bus.write_byte_data(self.address, reg_base + 2, off & 0xFF)
        self.bus.write_byte_data(self.address, reg_base + 3, off >> 8)