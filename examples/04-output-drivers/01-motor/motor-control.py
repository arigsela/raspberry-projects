#!/usr/bin/env python3
"""
DC Motor Control with L293D Motor Driver
Control motor speed and direction using PWM
"""

from gpiozero import Motor, PWMOutputDevice, Button, MCP3008
import time
import signal
import sys

# GPIO Configuration for L293D
# Motor A (Motor 1)
MOTOR_A_ENABLE = 17  # Enable pin (PWM for speed control)
MOTOR_A_IN1 = 27     # Input 1 (direction)
MOTOR_A_IN2 = 22     # Input 2 (direction)

# Motor B (Motor 2) - if using dual motor driver
MOTOR_B_ENABLE = 23  # Enable pin
MOTOR_B_IN1 = 24     # Input 1
MOTOR_B_IN2 = 25     # Input 2

# Control inputs (optional)
BUTTON_FORWARD = 5
BUTTON_REVERSE = 6
POT_CHANNEL = 0  # MCP3008 channel for speed control

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class MotorController:
    """Control a DC motor with L293D driver"""
    
    def __init__(self, enable_pin, in1_pin, in2_pin):
        """Initialize motor controller
        
        Args:
            enable_pin: GPIO pin for enable (speed control)
            in1_pin: GPIO pin for input 1 (direction)
            in2_pin: GPIO pin for input 2 (direction)
        """
        self.motor = Motor(forward=in1_pin, backward=in2_pin, enable=enable_pin)
        self.current_speed = 0
        self.current_direction = "stop"
    
    def forward(self, speed=1.0):
        """Drive motor forward
        
        Args:
            speed: Speed from 0.0 to 1.0
        """
        self.motor.forward(speed)
        self.current_speed = speed
        self.current_direction = "forward"
    
    def reverse(self, speed=1.0):
        """Drive motor in reverse
        
        Args:
            speed: Speed from 0.0 to 1.0
        """
        self.motor.backward(speed)
        self.current_speed = speed
        self.current_direction = "reverse"
    
    def stop(self):
        """Stop motor"""
        self.motor.stop()
        self.current_speed = 0
        self.current_direction = "stop"
    
    def brake(self):
        """Brake motor (both inputs high)"""
        # Note: Motor class doesn't have built-in brake
        # This is a hard stop
        self.motor.stop()
        self.current_speed = 0
        self.current_direction = "brake"
    
    def set_speed(self, speed):
        """Set motor speed maintaining direction
        
        Args:
            speed: Speed from 0.0 to 1.0
        """
        speed = max(0, min(1, speed))  # Clamp to valid range
        
        if self.current_direction == "forward":
            self.motor.forward(speed)
        elif self.current_direction == "reverse":
            self.motor.backward(speed)
        
        self.current_speed = speed
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.motor.close()

def basic_motor_control():
    """Basic motor control demo"""
    print("\n=== Basic Motor Control ===")
    print("Testing motor movements...")
    
    motor = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    
    try:
        # Forward at full speed
        print("\nForward at full speed")
        motor.forward(1.0)
        time.sleep(2)
        
        # Forward at half speed
        print("Forward at half speed")
        motor.forward(0.5)
        time.sleep(2)
        
        # Stop
        print("Stop")
        motor.stop()
        time.sleep(1)
        
        # Reverse at full speed
        print("Reverse at full speed")
        motor.reverse(1.0)
        time.sleep(2)
        
        # Reverse at half speed
        print("Reverse at half speed")
        motor.reverse(0.5)
        time.sleep(2)
        
        # Stop
        print("Stop")
        motor.stop()
        
    finally:
        motor.cleanup()

def speed_ramp_demo():
    """Gradually increase and decrease speed"""
    print("\n=== Speed Ramp Demo ===")
    print("Ramping speed up and down...")
    
    motor = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    
    try:
        # Ramp up forward
        print("\nRamping up forward...")
        for speed in range(0, 101, 5):
            motor.forward(speed / 100)
            print(f"\rSpeed: {speed}%", end='')
            time.sleep(0.1)
        
        # Ramp down
        print("\n\nRamping down...")
        for speed in range(100, -1, -5):
            motor.forward(speed / 100)
            print(f"\rSpeed: {speed}%", end='')
            time.sleep(0.1)
        
        motor.stop()
        time.sleep(1)
        
        # Ramp up reverse
        print("\n\nRamping up reverse...")
        for speed in range(0, 101, 5):
            motor.reverse(speed / 100)
            print(f"\rSpeed: {speed}%", end='')
            time.sleep(0.1)
        
        # Ramp down
        print("\n\nRamping down...")
        for speed in range(100, -1, -5):
            motor.reverse(speed / 100)
            print(f"\rSpeed: {speed}%", end='')
            time.sleep(0.1)
        
        print("\n")
        motor.stop()
        
    finally:
        motor.cleanup()

def direction_change_demo():
    """Change direction with different speeds"""
    print("\n=== Direction Change Demo ===")
    print("Changing directions...")
    
    motor = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    
    try:
        speeds = [0.3, 0.5, 0.7, 1.0]
        
        for speed in speeds:
            print(f"\nSpeed: {speed*100:.0f}%")
            
            print("  Forward")
            motor.forward(speed)
            time.sleep(1)
            
            print("  Stop")
            motor.stop()
            time.sleep(0.5)
            
            print("  Reverse")
            motor.reverse(speed)
            time.sleep(1)
            
            print("  Stop")
            motor.stop()
            time.sleep(0.5)
        
    finally:
        motor.cleanup()

def button_control():
    """Control motor with buttons"""
    print("\n=== Button Control ===")
    print("Press buttons to control motor")
    print("Press Ctrl+C to exit")
    
    motor = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    
    try:
        forward_btn = Button(BUTTON_FORWARD)
        reverse_btn = Button(BUTTON_REVERSE)
        
        def go_forward():
            print("Forward")
            motor.forward(0.7)
        
        def go_reverse():
            print("Reverse")
            motor.reverse(0.7)
        
        def stop_motor():
            print("Stop")
            motor.stop()
        
        forward_btn.when_pressed = go_forward
        forward_btn.when_released = stop_motor
        reverse_btn.when_pressed = go_reverse
        reverse_btn.when_released = stop_motor
        
        # Keep running
        signal.pause()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure buttons are connected")
    finally:
        motor.cleanup()

def potentiometer_speed_control():
    """Control motor speed with potentiometer"""
    print("\n=== Potentiometer Speed Control ===")
    print("Rotate potentiometer to control speed")
    print("Press Ctrl+C to exit")
    
    motor = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        
        # Start forward
        motor.forward(0)
        
        while True:
            # Read potentiometer (0.0 to 1.0)
            speed = pot.value
            
            # Set motor speed
            motor.set_speed(speed)
            
            # Display
            bar_length = int(speed * 20)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"\rSpeed: [{bar}] {speed*100:5.1f}%", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n")
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure MCP3008 is connected")
    finally:
        motor.cleanup()

def dual_motor_demo():
    """Control two motors simultaneously"""
    print("\n=== Dual Motor Demo ===")
    print("Controlling two motors...")
    
    motor_a = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    motor_b = MotorController(MOTOR_B_ENABLE, MOTOR_B_IN1, MOTOR_B_IN2)
    
    try:
        # Both forward
        print("\nBoth motors forward")
        motor_a.forward(0.7)
        motor_b.forward(0.7)
        time.sleep(2)
        
        # Turn left (A slow, B fast)
        print("Turn left")
        motor_a.forward(0.3)
        motor_b.forward(0.9)
        time.sleep(2)
        
        # Turn right (A fast, B slow)
        print("Turn right")
        motor_a.forward(0.9)
        motor_b.forward(0.3)
        time.sleep(2)
        
        # Spin in place (opposite directions)
        print("Spin in place")
        motor_a.forward(0.7)
        motor_b.reverse(0.7)
        time.sleep(2)
        
        # Stop both
        print("Stop")
        motor_a.stop()
        motor_b.stop()
        
    finally:
        motor_a.cleanup()
        motor_b.cleanup()

def pwm_frequency_test():
    """Test different PWM frequencies"""
    print("\n=== PWM Frequency Test ===")
    print("Testing different PWM frequencies...")
    print("Listen for motor whine changes")
    
    # Direct PWM control for testing
    enable = PWMOutputDevice(MOTOR_A_ENABLE)
    motor = Motor(forward=MOTOR_A_IN1, backward=MOTOR_A_IN2, enable=None)
    
    try:
        motor.forward()  # Set direction
        
        frequencies = [100, 500, 1000, 5000, 10000, 20000]
        
        for freq in frequencies:
            print(f"\nPWM Frequency: {freq} Hz")
            enable.frequency = freq
            enable.value = 0.5  # 50% duty cycle
            time.sleep(2)
        
        print("\nTest complete")
        
    finally:
        enable.close()
        motor.close()

def acceleration_profile():
    """Smooth acceleration and deceleration"""
    print("\n=== Acceleration Profile ===")
    print("Smooth speed changes...")
    
    motor = MotorController(MOTOR_A_ENABLE, MOTOR_A_IN1, MOTOR_A_IN2)
    
    try:
        # S-curve acceleration
        print("\nS-curve acceleration")
        steps = 50
        for i in range(steps):
            # S-curve formula
            t = i / steps
            speed = t * t * (3 - 2 * t)
            motor.forward(speed)
            print(f"\rSpeed: {speed*100:5.1f}%", end='')
            time.sleep(0.05)
        
        print("\n\nConstant speed")
        time.sleep(2)
        
        # S-curve deceleration
        print("\nS-curve deceleration")
        for i in range(steps):
            t = i / steps
            speed = 1 - (t * t * (3 - 2 * t))
            motor.forward(speed)
            print(f"\rSpeed: {speed*100:5.1f}%", end='')
            time.sleep(0.05)
        
        print("\n")
        motor.stop()
        
    finally:
        motor.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("DC Motor Control with L293D")
    print("===========================")
    print("Motor A GPIO pins:")
    print(f"  Enable: GPIO{MOTOR_A_ENABLE}")
    print(f"  IN1: GPIO{MOTOR_A_IN1}")
    print(f"  IN2: GPIO{MOTOR_A_IN2}")
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic motor control")
        print("2. Speed ramp up/down")
        print("3. Direction changes")
        print("4. Button control")
        print("5. Potentiometer speed control")
        print("6. Dual motor control")
        print("7. PWM frequency test")
        print("8. Acceleration profile")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_motor_control()
        elif choice == '2':
            speed_ramp_demo()
        elif choice == '3':
            direction_change_demo()
        elif choice == '4':
            button_control()
        elif choice == '5':
            potentiometer_speed_control()
        elif choice == '6':
            dual_motor_demo()
        elif choice == '7':
            pwm_frequency_test()
        elif choice == '8':
            acceleration_profile()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()