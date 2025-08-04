#!/usr/bin/env python3
"""
Servo Motor Control - PWM Position Control
Demonstrates precise servo positioning using GPIO Zero
"""

from gpiozero import Servo
from time import sleep
import signal
import sys

# GPIO Configuration
SERVO_PIN = 18

# Servo correction factor (adjust if your servo doesn't reach full range)
# Most servos need some correction: -1 = full left, 0 = center, 1 = full right
MIN_PULSE_WIDTH = 0.5/1000   # 0.5ms
MAX_PULSE_WIDTH = 2.5/1000   # 2.5ms

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def angle_to_value(angle):
    """Convert angle (0-180) to servo value (-1 to 1)"""
    # Map 0-180 degrees to -1 to 1
    return (angle / 90.0) - 1

def main():
    """Main servo control demonstration"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize servo with pulse width correction
    servo = Servo(SERVO_PIN, 
                  min_pulse_width=MIN_PULSE_WIDTH,
                  max_pulse_width=MAX_PULSE_WIDTH)
    
    print("Servo Motor Control Demo - Press Ctrl+C to exit")
    print(f"Servo connected to GPIO{SERVO_PIN}")
    print("\nStarting servo movement sequence...")
    
    try:
        while True:
            # Test basic positions
            print("\n--- Basic Positions ---")
            
            print("Moving to 0° (full left)")
            servo.min()
            sleep(2)
            
            print("Moving to 90° (center)")
            servo.mid()
            sleep(2)
            
            print("Moving to 180° (full right)")
            servo.max()
            sleep(2)
            
            # Test specific angles
            print("\n--- Specific Angles ---")
            angles = [0, 45, 90, 135, 180]
            
            for angle in angles:
                print(f"Moving to {angle}°")
                servo.value = angle_to_value(angle)
                sleep(1)
            
            # Smooth sweep
            print("\n--- Smooth Sweep ---")
            print("Sweeping left to right...")
            
            # Sweep from 0 to 180 degrees
            for angle in range(0, 181, 2):
                servo.value = angle_to_value(angle)
                sleep(0.02)
            
            print("Sweeping right to left...")
            
            # Sweep from 180 to 0 degrees
            for angle in range(180, -1, -2):
                servo.value = angle_to_value(angle)
                sleep(0.02)
            
            # Return to center
            print("\nReturning to center position")
            servo.mid()
            sleep(2)
            
    except KeyboardInterrupt:
        pass
    finally:
        # Detach servo (stop sending pulses)
        print("\nDetaching servo...")
        servo.detach()

if __name__ == "__main__":
    main()