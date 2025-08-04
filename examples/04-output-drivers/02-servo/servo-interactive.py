#!/usr/bin/env python3
"""
Interactive Servo Control
Control servo position using keyboard commands or continuous input
"""

from gpiozero import Servo
from time import sleep
import signal
import sys

# GPIO Configuration
SERVO_PIN = 18

# Servo pulse width configuration
MIN_PULSE_WIDTH = 0.5/1000   # 0.5ms
MAX_PULSE_WIDTH = 2.5/1000   # 2.5ms

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def angle_to_value(angle):
    """Convert angle (0-180) to servo value (-1 to 1)"""
    return (angle / 90.0) - 1

def value_to_angle(value):
    """Convert servo value (-1 to 1) to angle (0-180)"""
    return (value + 1) * 90

def get_angle_input():
    """Get valid angle input from user"""
    while True:
        try:
            angle = float(input("Enter angle (0-180): "))
            if 0 <= angle <= 180:
                return angle
            else:
                print("Please enter an angle between 0 and 180 degrees")
        except ValueError:
            print("Please enter a valid number")

def main():
    """Interactive servo control interface"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize servo
    servo = Servo(SERVO_PIN,
                  min_pulse_width=MIN_PULSE_WIDTH,
                  max_pulse_width=MAX_PULSE_WIDTH)
    
    print("Interactive Servo Control - Press Ctrl+C to exit")
    print(f"Servo connected to GPIO{SERVO_PIN}")
    
    # Start at center position
    servo.mid()
    current_angle = 90
    
    print("\nCommands:")
    print("  a: Enter specific angle")
    print("  +: Increase angle by 10°")
    print("  -: Decrease angle by 10°")
    print("  [: Increase angle by 1°")
    print("  ]: Decrease angle by 1°")
    print("  c: Center (90°)")
    print("  l: Full left (0°)")
    print("  r: Full right (180°)")
    print("  s: Smooth sweep")
    print("  p: Current position")
    print("  d: Detach servo")
    print("  q: Quit")
    
    try:
        while True:
            command = input(f"\nCurrent: {current_angle:.1f}° > ").lower().strip()
            
            if command == 'q':
                break
            elif command == 'a':
                angle = get_angle_input()
                servo.value = angle_to_value(angle)
                current_angle = angle
                print(f"Moved to {angle}°")
            elif command == '+':
                new_angle = min(current_angle + 10, 180)
                servo.value = angle_to_value(new_angle)
                current_angle = new_angle
                print(f"Moved to {new_angle}°")
            elif command == '-':
                new_angle = max(current_angle - 10, 0)
                servo.value = angle_to_value(new_angle)
                current_angle = new_angle
                print(f"Moved to {new_angle}°")
            elif command == '[':
                new_angle = min(current_angle + 1, 180)
                servo.value = angle_to_value(new_angle)
                current_angle = new_angle
                print(f"Moved to {new_angle}°")
            elif command == ']':
                new_angle = max(current_angle - 1, 0)
                servo.value = angle_to_value(new_angle)
                current_angle = new_angle
                print(f"Moved to {new_angle}°")
            elif command == 'c':
                servo.mid()
                current_angle = 90
                print("Centered at 90°")
            elif command == 'l':
                servo.min()
                current_angle = 0
                print("Moved to 0° (full left)")
            elif command == 'r':
                servo.max()
                current_angle = 180
                print("Moved to 180° (full right)")
            elif command == 's':
                print("Smooth sweep in progress...")
                # Sweep to current position first
                start_angle = value_to_angle(servo.value)
                
                # Sweep full range
                for angle in range(0, 181, 2):
                    servo.value = angle_to_value(angle)
                    sleep(0.02)
                for angle in range(180, -1, -2):
                    servo.value = angle_to_value(angle)
                    sleep(0.02)
                
                # Return to previous position
                servo.value = angle_to_value(current_angle)
                print(f"Returned to {current_angle}°")
            elif command == 'p':
                print(f"Current position: {current_angle}°")
                print(f"Servo value: {servo.value:.3f}")
            elif command == 'd':
                servo.detach()
                print("Servo detached (no control signal)")
                input("Press Enter to reattach...")
                servo.value = angle_to_value(current_angle)
                print("Servo reattached")
            else:
                print("Invalid command. Type 'q' to quit.")
                
    except KeyboardInterrupt:
        pass
    finally:
        print("\nDetaching servo...")
        servo.detach()
        print("Goodbye!")

if __name__ == "__main__":
    main()