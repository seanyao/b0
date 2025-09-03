#!/usr/bin/env python3
"""
Servo Motor Control Script for Jetson Orin Nano
Controls MG996R servo motor using PWM on GPIO #7
Sweeps servo from 0° → 180° → 0°

Hardware Setup:
- Servo signal wire connected to GPIO #7 (Pin 26)
- Servo powered by external 5V supply
- Ground shared between Jetson and servo power supply

Usage: sudo python3 servo_test.py
"""

import Jetson.GPIO as GPIO
import time

# GPIO Configuration
SERVO_PIN = 7  # GPIO #7 (Physical pin 26)
PWM_FREQUENCY = 50  # 50Hz for servo control (20ms period)

# Servo pulse width constants (in milliseconds)
MIN_PULSE_WIDTH = 1.0  # 1ms pulse = 0 degrees
MAX_PULSE_WIDTH = 2.0  # 2ms pulse = 180 degrees
PERIOD_MS = 20.0       # 20ms period for 50Hz

# Calculate duty cycles (percentage of 20ms period)
MIN_DUTY_CYCLE = (MIN_PULSE_WIDTH / PERIOD_MS) * 100  # 5%
MAX_DUTY_CYCLE = (MAX_PULSE_WIDTH / PERIOD_MS) * 100  # 10%

def setup_gpio():
    """
    Initialize GPIO settings and PWM
    """
    print("Setting up GPIO...")
    
    # Set GPIO numbering mode to BOARD (physical pin numbers)
    GPIO.setmode(GPIO.BOARD)
    
    # Configure GPIO #7 as output
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    
    # Create PWM instance with 50Hz frequency
    pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)
    
    # Start PWM with 0% duty cycle (servo off)
    pwm.start(0)
    
    print(f"GPIO #{SERVO_PIN} configured for PWM at {PWM_FREQUENCY}Hz")
    return pwm

def angle_to_duty_cycle(angle):
    """
    Convert servo angle (0-180°) to PWM duty cycle percentage
    
    Args:
        angle (float): Servo angle in degrees (0-180)
    
    Returns:
        float: Duty cycle percentage (5-10%)
    """
    # Linear interpolation between min and max duty cycles
    duty_cycle = MIN_DUTY_CYCLE + (angle / 180.0) * (MAX_DUTY_CYCLE - MIN_DUTY_CYCLE)
    return duty_cycle

def move_servo_to_angle(pwm, angle, delay=0.5):
    """
    Move servo to specified angle
    
    Args:
        pwm: PWM instance
        angle (float): Target angle in degrees (0-180)
        delay (float): Time to wait after movement
    """
    duty_cycle = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Moving servo to {angle}° (duty cycle: {duty_cycle:.2f}%)")
    time.sleep(delay)

def servo_sweep(pwm):
    """
    Perform servo sweep: 0° → 180° → 0°
    
    Args:
        pwm: PWM instance
    """
    print("\nStarting servo sweep...")
    
    # Move to starting position (0 degrees)
    print("Phase 1: Moving to 0°")
    move_servo_to_angle(pwm, 0, 1.0)
    
    # Sweep from 0° to 180° in 20° increments
    print("Phase 2: Sweeping from 0° to 180°")
    for angle in range(0, 181, 20):
        move_servo_to_angle(pwm, angle, 0.3)
    
    # Hold at 180° for a moment
    print("Holding at 180°...")
    time.sleep(1.0)
    
    # Sweep back from 180° to 0° in 20° increments
    print("Phase 3: Sweeping from 180° to 0°")
    for angle in range(180, -1, -20):
        move_servo_to_angle(pwm, angle, 0.3)
    
    # Final position at 0°
    print("Returning to 0° position")
    move_servo_to_angle(pwm, 0, 1.0)
    
    print("Servo sweep completed!")

def cleanup_gpio(pwm):
    """
    Clean up GPIO resources
    
    Args:
        pwm: PWM instance to stop
    """
    print("\nCleaning up GPIO...")
    
    # Stop PWM signal
    pwm.stop()
    
    # Clean up all GPIO channels
    GPIO.cleanup()
    
    print("GPIO cleanup completed")

def main():
    """
    Main function - orchestrates servo control sequence
    """
    print("=== MG996R Servo Control Test ===")
    print(f"Using GPIO #{SERVO_PIN} for PWM control")
    print(f"PWM Frequency: {PWM_FREQUENCY}Hz")
    print(f"Pulse Width Range: {MIN_PULSE_WIDTH}ms - {MAX_PULSE_WIDTH}ms")
    print(f"Duty Cycle Range: {MIN_DUTY_CYCLE:.1f}% - {MAX_DUTY_CYCLE:.1f}%")
    
    pwm = None
    
    try:
        # Initialize GPIO and PWM
        pwm = setup_gpio()
        
        # Wait a moment for servo to initialize
        print("Waiting for servo to initialize...")
        time.sleep(2)
        
        # Perform servo sweep
        servo_sweep(pwm)
        
        # Optional: Keep servo at 0° for a few seconds
        print("\nHolding servo at 0° for 3 seconds...")
        time.sleep(3)
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C)")
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        
    finally:
        # Always clean up GPIO resources
        if pwm:
            cleanup_gpio(pwm)
        print("Program terminated")

if __name__ == "__main__":
    main()