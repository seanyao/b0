#!/usr/bin/env python3
"""
Servo Motor Control Script for Jetson Orin Nano
Uses software PWM for servo control
"""

import Jetson.GPIO as GPIO
import time
import threading

class SoftwarePWM:
    def __init__(self, pin, frequency):
        self.pin = pin
        self.frequency = frequency
        self.period = 1.0 / frequency
        self.duty_cycle = 0
        self.running = False
        self.thread = None
        
        # Setup GPIO
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
    
    def start(self, duty_cycle):
        """Start software PWM"""
        self.duty_cycle = duty_cycle
        self.running = True
        self.thread = threading.Thread(target=self._pwm_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def ChangeDutyCycle(self, duty_cycle):
        """Change duty cycle"""
        self.duty_cycle = duty_cycle
    
    def stop(self):
        """Stop PWM"""
        self.running = False
        if self.thread:
            self.thread.join()
        GPIO.output(self.pin, GPIO.LOW)
    
    def _pwm_loop(self):
        """PWM generation loop"""
        while self.running:
            if self.duty_cycle > 0:
                on_time = self.period * (self.duty_cycle / 100.0)
                off_time = self.period - on_time
                
                if on_time > 0:
                    GPIO.output(self.pin, GPIO.HIGH)
                    time.sleep(on_time)
                
                if off_time > 0:
                    GPIO.output(self.pin, GPIO.LOW)
                    time.sleep(off_time)
            else:
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(self.period)

# GPIO Configuration
SERVO_PIN = 7  # GPIO #7
PWM_FREQUENCY = 50  # 50Hz for servo control

# Servo constants
MIN_PULSE_WIDTH = 1.0  # 1ms
MAX_PULSE_WIDTH = 2.0  # 2ms
PERIOD_MS = 20.0       # 20ms period

MIN_DUTY_CYCLE = (MIN_PULSE_WIDTH / PERIOD_MS) * 100  # 5%
MAX_DUTY_CYCLE = (MAX_PULSE_WIDTH / PERIOD_MS) * 100  # 10%

def setup_gpio():
    """Initialize GPIO and software PWM"""
    print("Setting up GPIO with software PWM...")
    
    GPIO.setmode(GPIO.BOARD)
    
    # Create software PWM instance
    pwm = SoftwarePWM(SERVO_PIN, PWM_FREQUENCY)
    pwm.start(0)
    
    print(f"Software PWM initialized on GPIO #{SERVO_PIN} at {PWM_FREQUENCY}Hz")
    return pwm

def angle_to_duty_cycle(angle):
    """Convert angle to duty cycle"""
    angle = max(0, min(180, angle))
    duty_cycle = MIN_DUTY_CYCLE + (angle / 180.0) * (MAX_DUTY_CYCLE - MIN_DUTY_CYCLE)
    return duty_cycle

def move_servo(pwm, angle):
    """Move servo to specified angle"""
    duty_cycle = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Moving to {angle}° (duty cycle: {duty_cycle:.2f}%)")

def main():
    print("=== MG996R Servo Control Test (Software PWM) ===")
    print(f"Using GPIO #{SERVO_PIN} for PWM control")
    print(f"PWM Frequency: {PWM_FREQUENCY}Hz")
    print(f"Pulse Width Range: {MIN_PULSE_WIDTH}ms - {MAX_PULSE_WIDTH}ms")
    print(f"Duty Cycle Range: {MIN_DUTY_CYCLE:.1f}% - {MAX_DUTY_CYCLE:.1f}%")
    
    try:
        # Setup PWM
        pwm = setup_gpio()
        
        print("\nStarting servo sweep test...")
        
        # Test sequence
        angles = [0, 45, 90, 135, 180, 135, 90, 45, 0]
        
        for angle in angles:
            move_servo(pwm, angle)
            time.sleep(1)
        
        print("\nTest completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError occurred: {e}")
    finally:
        print("Cleaning up GPIO...")
        if 'pwm' in locals():
            pwm.stop()
        GPIO.cleanup()
        print("Program terminated")

if __name__ == "__main__":
    main()