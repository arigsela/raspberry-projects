#!/usr/bin/env python3
"""
2-Axis Analog Joystick with Push Button
Read X and Y position and button state from analog joystick
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

from adc0834 import ADC0834
from gpiozero import Button, LED, PWMLED, Servo
import time
import signal
import math
from collections import deque

# GPIO Configuration
ADC_CS = 17     # ADC Chip Select
ADC_CLK = 18    # ADC Clock
ADC_DI = 27     # ADC Data In
ADC_DO = 22     # ADC Data Out

# ADC Channels
JOYSTICK_X_CHANNEL = 0
JOYSTICK_Y_CHANNEL = 1

# Joystick button (if separate)
JOYSTICK_SW = 23

# Optional outputs
LED_UP_PIN = 24     # Up direction LED
LED_DOWN_PIN = 25   # Down direction LED
LED_LEFT_PIN = 26   # Left direction LED
LED_RIGHT_PIN = 19  # Right direction LED
SERVO_X_PIN = 20    # X-axis servo
SERVO_Y_PIN = 21    # Y-axis servo

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class AnalogJoystick:
    """2-axis analog joystick with calibration and dead zone"""
    
    def __init__(self, adc, x_channel=0, y_channel=1, sw_pin=None):
        """
        Initialize joystick
        
        Args:
            adc: ADC0834 instance
            x_channel: ADC channel for X axis
            y_channel: ADC channel for Y axis
            sw_pin: GPIO pin for button (optional)
        """
        self.adc = adc
        self.x_channel = x_channel
        self.y_channel = y_channel
        
        # Button setup
        self.button = Button(sw_pin, pull_up=True) if sw_pin else None
        
        # Calibration values (will be set during calibration)
        self.x_center = 127
        self.y_center = 127
        self.x_min = 0
        self.x_max = 255
        self.y_min = 0
        self.y_max = 255
        
        # Dead zone (ignore small movements near center)
        self.dead_zone = 0.1  # 10% dead zone
        
        # Movement tracking
        self.position_history = deque(maxlen=10)
        
        # Callbacks
        self.position_callback = None
        self.button_callback = None
        
        # Set up button callback
        if self.button:
            self.button.when_pressed = self._on_button_press
    
    def _on_button_press(self):
        """Handle button press"""
        if self.button_callback:
            self.button_callback()
    
    def read_raw(self):
        """Read raw ADC values"""
        x_raw = self.adc.read_channel(self.x_channel)
        y_raw = self.adc.read_channel(self.y_channel)
        return x_raw, y_raw
    
    def read_position(self):
        """
        Read calibrated position (-1.0 to 1.0 for each axis)
        
        Returns:
            (x, y) tuple where -1.0 is left/down, 1.0 is right/up
        """
        x_raw, y_raw = self.read_raw()
        
        # Convert to -1.0 to 1.0 range
        x_normalized = (x_raw - self.x_center) / (self.x_max - self.x_center) if x_raw > self.x_center else (x_raw - self.x_center) / (self.x_center - self.x_min)
        y_normalized = (y_raw - self.y_center) / (self.y_max - self.y_center) if y_raw > self.y_center else (y_raw - self.y_center) / (self.y_center - self.y_min)
        
        # Clamp values
        x_normalized = max(-1.0, min(1.0, x_normalized))
        y_normalized = max(-1.0, min(1.0, y_normalized))
        
        # Apply dead zone
        if abs(x_normalized) < self.dead_zone:
            x_normalized = 0.0
        if abs(y_normalized) < self.dead_zone:
            y_normalized = 0.0
        
        return x_normalized, y_normalized
    
    def read_direction(self):
        """
        Get directional reading
        
        Returns:
            Dictionary with direction booleans and magnitudes
        """
        x, y = self.read_position()
        
        return {
            'up': y > self.dead_zone,
            'down': y < -self.dead_zone,
            'left': x < -self.dead_zone,
            'right': x > self.dead_zone,
            'x_magnitude': abs(x),
            'y_magnitude': abs(y),
            'total_magnitude': math.sqrt(x*x + y*y)
        }
    
    def read_polar(self):
        """
        Read position in polar coordinates
        
        Returns:
            (angle, magnitude) where angle is in degrees (0-360)
        """
        x, y = self.read_position()
        
        if x == 0 and y == 0:
            return 0, 0
        
        angle = math.degrees(math.atan2(y, x))
        if angle < 0:
            angle += 360
        
        magnitude = math.sqrt(x*x + y*y)
        magnitude = min(magnitude, 1.0)  # Clamp to max 1.0
        
        return angle, magnitude
    
    def calibrate(self):
        """
        Calibrate joystick center and range
        Follow on-screen instructions
        """
        print("\n=== Joystick Calibration ===")
        print("Step 1: Center the joystick and press Enter")
        input("Press Enter when joystick is centered...")
        
        # Read center position
        x_raw, y_raw = self.read_raw()
        self.x_center = x_raw
        self.y_center = y_raw
        print(f"Center position: X={x_raw}, Y={y_raw}")
        
        print("\nStep 2: Move joystick to all extreme positions")
        print("Press Enter when done...")
        
        x_readings = []
        y_readings = []
        
        # Collect readings for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            x_raw, y_raw = self.read_raw()
            x_readings.append(x_raw)
            y_readings.append(y_raw)
            
            print(f"\rCollecting... X={x_raw:3d}, Y={y_raw:3d} "
                  f"(Time remaining: {5 - int(time.time() - start_time)}s)", end='')
            time.sleep(0.1)
        
        # Find min/max values
        self.x_min = min(x_readings)
        self.x_max = max(x_readings)
        self.y_min = min(y_readings)
        self.y_max = max(y_readings)
        
        print(f"\n\nCalibration complete:")
        print(f"X range: {self.x_min} to {self.x_max} (center: {self.x_center})")
        print(f"Y range: {self.y_min} to {self.y_max} (center: {self.y_center})")
        
        # Test calibration
        print("\nTesting calibration (move joystick around):")
        for _ in range(20):
            x, y = self.read_position()
            print(f"\rX: {x:+5.2f}, Y: {y:+5.2f}", end='')
            time.sleep(0.2)
        print()
    
    def set_position_callback(self, callback):
        """Set callback for position changes"""
        self.position_callback = callback
    
    def set_button_callback(self, callback):
        """Set callback for button presses"""
        self.button_callback = callback
    
    def is_button_pressed(self):
        """Check if button is pressed"""
        return self.button.is_pressed if self.button else False
    
    def cleanup(self):
        """Clean up resources"""
        if self.button:
            self.button.close()

def basic_position_reading():
    """Basic joystick position reading"""
    print("\n=== Basic Position Reading ===")
    print("Move joystick to see position")
    print("Press joystick button to reset")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    def on_button():
        print("\nButton pressed! Center position reset.")
    
    joystick.set_button_callback(on_button)
    
    try:
        while True:
            x_raw, y_raw = joystick.read_raw()
            x, y = joystick.read_position()
            angle, magnitude = joystick.read_polar()
            
            # Visual position indicator
            bar_length = 10
            x_bar_pos = int((x + 1) * bar_length)
            y_bar_pos = int((y + 1) * bar_length)
            
            x_bar = " " * x_bar_pos + "|" + " " * (2 * bar_length - x_bar_pos)
            y_bar = " " * y_bar_pos + "|" + " " * (2 * bar_length - y_bar_pos)
            
            print(f"\rRaw: X={x_raw:3d} Y={y_raw:3d} | "
                  f"Pos: X={x:+5.2f} Y={y:+5.2f} | "
                  f"Polar: {angle:3.0f}° {magnitude:.2f} | "
                  f"Btn: {'YES' if joystick.is_button_pressed() else 'NO '}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        joystick.cleanup()
        adc.cleanup()

def direction_leds():
    """Control LEDs based on joystick direction"""
    print("\n=== Direction LEDs ===")
    print("LEDs indicate joystick direction")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    # Setup LEDs
    leds = {}
    try:
        leds['up'] = LED(LED_UP_PIN)
        leds['down'] = LED(LED_DOWN_PIN)
        leds['left'] = LED(LED_LEFT_PIN)
        leds['right'] = LED(LED_RIGHT_PIN)
        has_leds = True
    except:
        has_leds = False
        print("Note: No LEDs connected for direction indication")
    
    try:
        while True:
            directions = joystick.read_direction()
            
            # Control LEDs
            if has_leds:
                for direction, led in leds.items():
                    if directions[direction]:
                        led.on()
                    else:
                        led.off()
            
            # Display status
            indicators = []
            if directions['up']: indicators.append("↑")
            if directions['down']: indicators.append("↓")
            if directions['left']: indicators.append("←")
            if directions['right']: indicators.append("→")
            
            direction_str = "".join(indicators) if indicators else "•"
            
            print(f"\rDirection: {direction_str:4s} | "
                  f"Magnitude: {directions['total_magnitude']:.2f} | "
                  f"X: {directions['x_magnitude']:.2f} Y: {directions['y_magnitude']:.2f}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        for led in leds.values():
            led.close()
        joystick.cleanup()
        adc.cleanup()

def servo_control():
    """Control servo motors with joystick"""
    print("\n=== Servo Control ===")
    print("Control servo positions with joystick")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    # Setup servos
    servos = {}
    try:
        servos['x'] = Servo(SERVO_X_PIN)
        servos['y'] = Servo(SERVO_Y_PIN)
        has_servos = True
    except:
        has_servos = False
        print("Note: No servos connected")
    
    try:
        while True:
            x, y = joystick.read_position()
            
            # Control servos (joystick position directly maps to servo position)
            if has_servos:
                servos['x'].value = x  # -1 to 1 range
                servos['y'].value = y
            
            # Display servo positions
            x_angle = (x + 1) * 90  # Convert to 0-180 degrees
            y_angle = (y + 1) * 90
            
            # Visual servo position bars
            bar_length = 20
            x_bar_pos = int((x + 1) * bar_length / 2)
            y_bar_pos = int((y + 1) * bar_length / 2)
            
            x_bar = "█" * x_bar_pos + "░" * (bar_length - x_bar_pos)
            y_bar = "█" * y_bar_pos + "░" * (bar_length - y_bar_pos)
            
            print(f"\rX Servo: {x_angle:5.1f}° [{x_bar}] | "
                  f"Y Servo: {y_angle:5.1f}° [{y_bar}]", end='')
            
            time.sleep(0.05)  # Faster update for servo control
    
    except KeyboardInterrupt:
        pass
    finally:
        for servo in servos.values():
            servo.close()
        joystick.cleanup()
        adc.cleanup()

def cursor_control():
    """ASCII cursor control with joystick"""
    print("\n=== Cursor Control ===")
    print("Control cursor on screen with joystick")
    print("Press joystick button to place marker")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    # Screen dimensions
    screen_width = 40
    screen_height = 15
    
    # Cursor position
    cursor_x = screen_width // 2
    cursor_y = screen_height // 2
    
    # Markers placed by button press
    markers = set()
    
    def on_button():
        markers.add((cursor_x, cursor_y))
        print(f"\nMarker placed at ({cursor_x}, {cursor_y})")
    
    joystick.set_button_callback(on_button)
    
    try:
        while True:
            x, y = joystick.read_position()
            
            # Update cursor position
            if abs(x) > 0.3:  # Threshold for movement
                cursor_x += int(x * 2)  # Speed factor
                cursor_x = max(0, min(screen_width - 1, cursor_x))
            
            if abs(y) > 0.3:
                cursor_y -= int(y * 2)  # Invert Y (up is positive)
                cursor_y = max(0, min(screen_height - 1, cursor_y))
            
            # Clear screen and draw
            print("\033[2J\033[H", end='')  # Clear screen, move to top
            
            for row in range(screen_height):
                line = ""
                for col in range(screen_width):
                    if col == cursor_x and row == cursor_y:
                        line += "+"  # Cursor
                    elif (col, row) in markers:
                        line += "●"  # Marker
                    else:
                        line += " "
                print(f"|{line}|")
            
            print("-" * (screen_width + 2))
            print(f"Position: ({cursor_x:2d}, {cursor_y:2d}) | "
                  f"Joystick: ({x:+4.1f}, {y:+4.1f}) | "
                  f"Markers: {len(markers)}")
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        joystick.cleanup()
        adc.cleanup()

def joystick_game():
    """Simple reaction game using joystick"""
    print("\n=== Joystick Reaction Game ===")
    print("Follow the direction prompts as quickly as possible!")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    import random
    
    directions = ['up', 'down', 'left', 'right']
    direction_symbols = {'up': '↑', 'down': '↓', 'left': '←', 'right': '→'}
    
    score = 0
    round_num = 0
    
    try:
        print("Game starting in 3 seconds...")
        time.sleep(3)
        
        while True:
            round_num += 1
            target_direction = random.choice(directions)
            symbol = direction_symbols[target_direction]
            
            print(f"\n=== Round {round_num} ===")
            print(f"Move joystick: {symbol} ({target_direction.upper()})")
            
            start_time = time.time()
            success = False
            
            # Wait for correct movement
            while time.time() - start_time < 5.0:  # 5 second timeout
                directions_state = joystick.read_direction()
                
                if directions_state[target_direction] and directions_state['total_magnitude'] > 0.7:
                    reaction_time = time.time() - start_time
                    points = max(1, int(10 - reaction_time * 2))  # Faster = more points
                    score += points
                    print(f"✓ Correct! Time: {reaction_time:.2f}s | Points: +{points} | Total: {score}")
                    success = True
                    break
                
                time.sleep(0.05)
            
            if not success:
                print("✗ Too slow! No points.")
            
            # Brief pause before next round
            time.sleep(1)
            
            # Check for quit condition
            if round_num % 5 == 0:
                print(f"\nScore after {round_num} rounds: {score}")
                continue_game = input("Continue? (y/n): ").lower().startswith('y')
                if not continue_game:
                    break
    
    except KeyboardInterrupt:
        pass
    finally:
        print(f"\n=== Game Over ===")
        print(f"Final Score: {score} points in {round_num} rounds")
        if round_num > 0:
            print(f"Average: {score/round_num:.1f} points per round")
        joystick.cleanup()
        adc.cleanup()

def analog_clock():
    """Display analog clock controlled by joystick"""
    print("\n=== Analog Clock Control ===")
    print("Use joystick to set time")
    print("X-axis: Hours, Y-axis: Minutes")
    print("Press button to toggle between set/display mode")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    from datetime import datetime
    
    # Clock state
    set_mode = False
    set_hour = 12
    set_minute = 0
    
    def on_button():
        nonlocal set_mode
        set_mode = not set_mode
        print(f"\nMode: {'SET TIME' if set_mode else 'DISPLAY'}")
    
    joystick.set_button_callback(on_button)
    
    try:
        while True:
            x, y = joystick.read_position()
            
            if set_mode:
                # Set time mode
                if abs(x) > 0.1:
                    set_hour = int((x + 1) * 12)  # 0-24 hours
                    set_hour = max(0, min(23, set_hour))
                
                if abs(y) > 0.1:
                    set_minute = int((y + 1) * 30)  # 0-60 minutes
                    set_minute = max(0, min(59, set_minute))
                
                current_hour = set_hour
                current_minute = set_minute
                mode_str = "SET"
            else:
                # Display current time
                now = datetime.now()
                current_hour = now.hour
                current_minute = now.minute
                mode_str = "LIVE"
            
            # Draw simple ASCII clock
            print("\033[2J\033[H", end='')  # Clear screen
            
            print("    12")
            print("  ┌─────┐")
            print("9 │  :  │ 3")
            print("  │  .  │")
            print("  └─────┘")
            print("     6")
            print()
            
            # Digital display
            print(f"Time: {current_hour:02d}:{current_minute:02d}")
            print(f"Mode: {mode_str}")
            
            if set_mode:
                print(f"Joystick: X={x:+4.1f} (Hour) Y={y:+4.1f} (Min)")
            
            time.sleep(0.2)
    
    except KeyboardInterrupt:
        pass
    finally:
        joystick.cleanup()
        adc.cleanup()

def joystick_calibration():
    """Calibrate joystick center and range"""
    print("\n=== Joystick Calibration ===")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    joystick = AnalogJoystick(adc, JOYSTICK_X_CHANNEL, JOYSTICK_Y_CHANNEL, JOYSTICK_SW)
    
    try:
        joystick.calibrate()
        
        print("\nCalibration saved! Testing...")
        
        # Test calibrated joystick
        for i in range(50):
            x, y = joystick.read_position()
            angle, magnitude = joystick.read_polar()
            
            print(f"\rTest {i+1}/50: X={x:+5.2f} Y={y:+5.2f} | "
                  f"Polar: {angle:3.0f}° {magnitude:.2f}", end='')
            time.sleep(0.1)
        
        print("\nCalibration test complete!")
    
    except KeyboardInterrupt:
        pass
    finally:
        joystick.cleanup()
        adc.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("2-Axis Analog Joystick Controller")
    print("================================")
    print("ADC Pins:")
    print(f"  CS:  GPIO{ADC_CS}")
    print(f"  CLK: GPIO{ADC_CLK}")
    print(f"  DI:  GPIO{ADC_DI}")
    print(f"  DO:  GPIO{ADC_DO}")
    print(f"\nJoystick X: ADC Channel {JOYSTICK_X_CHANNEL}")
    print(f"Joystick Y: ADC Channel {JOYSTICK_Y_CHANNEL}")
    print(f"Button: GPIO{JOYSTICK_SW}")
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic position reading")
        print("2. Direction LEDs")
        print("3. Servo control")
        print("4. Cursor control")
        print("5. Reaction game")
        print("6. Analog clock control")
        print("7. Calibrate joystick")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_position_reading()
        elif choice == '2':
            direction_leds()
        elif choice == '3':
            servo_control()
        elif choice == '4':
            cursor_control()
        elif choice == '5':
            joystick_game()
        elif choice == '6':
            analog_clock()
        elif choice == '7':
            joystick_calibration()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()