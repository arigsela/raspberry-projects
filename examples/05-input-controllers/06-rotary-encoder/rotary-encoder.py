#!/usr/bin/env python3
"""
Rotary Encoder Position and Direction Detection
Read rotational position and direction from a rotary encoder
"""

from gpiozero import Button, LED, PWMLED, Buzzer
import time
import signal
import sys
import threading
from collections import deque

# GPIO Configuration
ENCODER_CLK = 17    # Clock signal (A)
ENCODER_DT = 18     # Data signal (B)
ENCODER_SW = 27     # Switch (push button)

# Optional outputs
LED_CW_PIN = 23     # Clockwise indicator LED
LED_CCW_PIN = 24    # Counter-clockwise indicator LED
BUZZER_PIN = 25     # Click feedback buzzer
PWM_LED_PIN = 22    # PWM LED for brightness control

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class RotaryEncoder:
    """Rotary encoder with direction and position tracking"""
    
    def __init__(self, clk_pin=ENCODER_CLK, dt_pin=ENCODER_DT, sw_pin=ENCODER_SW):
        """
        Initialize rotary encoder
        
        Args:
            clk_pin: Clock signal pin (A)
            dt_pin: Data signal pin (B)
            sw_pin: Switch button pin
        """
        self.clk = Button(clk_pin, pull_up=True, bounce_time=0.001)
        self.dt = Button(dt_pin, pull_up=True, bounce_time=0.001)
        self.sw = Button(sw_pin, pull_up=True, bounce_time=0.05)
        
        # Position tracking
        self.position = 0
        self.last_clk_state = self.clk.is_pressed
        
        # Direction tracking
        self.direction = 0  # -1=CCW, 0=None, 1=CW
        
        # Speed tracking
        self.last_rotation_time = time.time()
        self.rotation_times = deque(maxlen=5)
        
        # Callbacks
        self.rotation_callback = None
        self.button_callback = None
        
        # Setup event handlers
        self.clk.when_pressed = self._on_rotation
        self.clk.when_released = self._on_rotation
        self.sw.when_pressed = self._on_button_press
        
        # Reset tracking
        self.reset_count = 0
    
    def _on_rotation(self):
        """Handle rotation detection"""
        current_clk = self.clk.is_pressed
        current_dt = self.dt.is_pressed
        
        # Check if this is a valid edge
        if current_clk != self.last_clk_state:
            # Determine direction based on DT state
            if current_clk == current_dt:
                # Counter-clockwise
                self.position -= 1
                self.direction = -1
            else:
                # Clockwise
                self.position += 1
                self.direction = 1
            
            # Update speed tracking
            current_time = time.time()
            self.rotation_times.append(current_time - self.last_rotation_time)
            self.last_rotation_time = current_time
            
            # Call rotation callback
            if self.rotation_callback:
                self.rotation_callback(self.position, self.direction)
        
        self.last_clk_state = current_clk
    
    def _on_button_press(self):
        """Handle button press"""
        if self.button_callback:
            self.button_callback()
    
    def get_position(self):
        """Get current position"""
        return self.position
    
    def get_direction(self):
        """Get last direction (-1=CCW, 0=None, 1=CW)"""
        return self.direction
    
    def get_speed(self):
        """Get rotation speed (rotations per second)"""
        if len(self.rotation_times) < 2:
            return 0
        
        avg_time = sum(self.rotation_times) / len(self.rotation_times)
        if avg_time > 0:
            return 1.0 / avg_time
        return 0
    
    def reset_position(self):
        """Reset position to zero"""
        self.position = 0
        self.reset_count += 1
    
    def set_rotation_callback(self, callback):
        """Set callback for rotation events"""
        self.rotation_callback = callback
    
    def set_button_callback(self, callback):
        """Set callback for button press events"""
        self.button_callback = callback
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.clk.close()
        self.dt.close()
        self.sw.close()

def basic_position_tracking():
    """Basic position and direction tracking"""
    print("\n=== Basic Position Tracking ===")
    print("Rotate encoder to change position")
    print("Press encoder button to reset")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    def on_rotation(position, direction):
        dir_symbol = "↻" if direction > 0 else "↺" if direction < 0 else "•"
        print(f"\rPosition: {position:4d} | Direction: {dir_symbol} | Speed: {encoder.get_speed():4.1f} r/s", end='')
    
    def on_button():
        encoder.reset_position()
        print(f"\n--- Position Reset (#{encoder.reset_count}) ---")
    
    encoder.set_rotation_callback(on_rotation)
    encoder.set_button_callback(on_button)
    
    try:
        print("Starting position tracking...")
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        encoder.cleanup()

def led_direction_indicator():
    """Visual direction indication with LEDs"""
    print("\n=== LED Direction Indicator ===")
    print("LEDs show rotation direction")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    try:
        led_cw = LED(LED_CW_PIN)
        led_ccw = LED(LED_CCW_PIN)
        has_leds = True
    except:
        has_leds = False
        print("Note: No LEDs connected for direction indication")
    
    def on_rotation(position, direction):
        if has_leds:
            if direction > 0:  # Clockwise
                led_cw.on()
                led_ccw.off()
            elif direction < 0:  # Counter-clockwise
                led_ccw.on()
                led_cw.off()
            
            # Brief flash then off
            threading.Timer(0.1, lambda: [led_cw.off(), led_ccw.off()]).start()
        
        dir_name = "Clockwise" if direction > 0 else "Counter-clockwise" if direction < 0 else "None"
        print(f"\rPosition: {position:4d} | Direction: {dir_name:15s}", end='')
    
    encoder.set_rotation_callback(on_rotation)
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_leds:
            led_cw.close()
            led_ccw.close()
        encoder.cleanup()

def brightness_control():
    """Control LED brightness with encoder"""
    print("\n=== Brightness Control ===")
    print("Rotate encoder to adjust LED brightness")
    print("Press encoder button to toggle on/off")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    try:
        pwm_led = PWMLED(PWM_LED_PIN)
        has_pwm_led = True
    except:
        has_pwm_led = False
        print("Note: No PWM LED connected")
    
    brightness = 50  # Start at 50%
    led_on = True
    
    def on_rotation(position, direction):
        nonlocal brightness
        
        # Adjust brightness
        brightness += direction * 5  # 5% steps
        brightness = max(0, min(100, brightness))
        
        if has_pwm_led and led_on:
            pwm_led.value = brightness / 100.0
        
        print(f"\rBrightness: {brightness:3d}% | LED: {'ON ' if led_on else 'OFF'}", end='')
    
    def on_button():
        nonlocal led_on
        led_on = not led_on
        
        if has_pwm_led:
            if led_on:
                pwm_led.value = brightness / 100.0
            else:
                pwm_led.off()
        
        print(f"\nLED {'ON' if led_on else 'OFF'}")
    
    encoder.set_rotation_callback(on_rotation)
    encoder.set_button_callback(on_button)
    
    # Set initial brightness
    if has_pwm_led:
        pwm_led.value = brightness / 100.0
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_pwm_led:
            pwm_led.close()
        encoder.cleanup()

def menu_navigation():
    """Navigate through menu using encoder"""
    print("\n=== Menu Navigation ===")
    print("Rotate to navigate, press to select")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    menu_items = [
        "File Operations",
        "Edit Settings", 
        "View Options",
        "Tools",
        "Help",
        "Exit"
    ]
    
    selected_index = 0
    
    def display_menu():
        print("\n" + "=" * 30)
        print("        MAIN MENU")
        print("=" * 30)
        for i, item in enumerate(menu_items):
            prefix = ">>> " if i == selected_index else "    "
            print(f"{prefix}{item}")
        print("=" * 30)
        print("Rotate to navigate, press to select")
    
    def on_rotation(position, direction):
        nonlocal selected_index
        selected_index = (selected_index + direction) % len(menu_items)
        display_menu()
    
    def on_button():
        selected_item = menu_items[selected_index]
        print(f"\n✓ Selected: {selected_item}")
        
        if selected_item == "Exit":
            raise KeyboardInterrupt
        else:
            print("(Menu item would open here)")
            time.sleep(1)
            display_menu()
    
    encoder.set_rotation_callback(on_rotation)
    encoder.set_button_callback(on_button)
    
    # Show initial menu
    display_menu()
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        encoder.cleanup()

def volume_control():
    """Simulate volume control with audio feedback"""
    print("\n=== Volume Control ===")
    print("Rotate encoder to adjust volume")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
        print("Note: No buzzer connected for audio feedback")
    
    volume = 50  # Start at 50%
    
    def on_rotation(position, direction):
        nonlocal volume
        
        # Adjust volume
        volume += direction * 2  # 2% steps
        volume = max(0, min(100, volume))
        
        # Audio feedback
        if has_buzzer and volume > 0:
            # Pitch increases with volume
            duration = 0.05
            buzzer.beep(duration, duration)
        
        # Visual volume bar
        bar_length = 20
        filled = int(volume * bar_length / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\rVolume: {volume:3d}% [{bar}]", end='')
    
    encoder.set_rotation_callback(on_rotation)
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_buzzer:
            buzzer.close()
        encoder.cleanup()

def step_counter():
    """Count steps with different step sizes"""
    print("\n=== Step Counter ===")
    print("Count encoder steps with configurable step size")
    print("Press encoder to change step size")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    step_sizes = [1, 2, 5, 10, 25, 50]
    step_size_index = 0
    step_size = step_sizes[step_size_index]
    
    counter = 0
    
    def on_rotation(position, direction):
        nonlocal counter
        counter += direction * step_size
        print(f"\rCounter: {counter:6d} | Step size: {step_size:2d} | Raw position: {position:4d}", end='')
    
    def on_button():
        nonlocal step_size_index, step_size
        step_size_index = (step_size_index + 1) % len(step_sizes)
        step_size = step_sizes[step_size_index]
        print(f"\nStep size changed to: {step_size}")
    
    encoder.set_rotation_callback(on_rotation)
    encoder.set_button_callback(on_button)
    
    try:
        print(f"Initial step size: {step_size}")
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        encoder.cleanup()

def speed_monitor():
    """Monitor rotation speed and acceleration"""
    print("\n=== Speed Monitor ===")
    print("Monitor encoder rotation speed")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    max_speed = 0
    total_rotations = 0
    start_time = time.time()
    
    def on_rotation(position, direction):
        nonlocal max_speed, total_rotations
        
        speed = encoder.get_speed()
        max_speed = max(max_speed, speed)
        total_rotations += 1
        
        elapsed = time.time() - start_time
        avg_speed = total_rotations / elapsed if elapsed > 0 else 0
        
        # Speed bar visualization
        bar_length = 20
        speed_percent = min(speed / 10.0, 1.0)  # Max 10 r/s
        filled = int(speed_percent * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\rSpeed: {speed:5.1f} r/s [{bar}] Max: {max_speed:5.1f} | Avg: {avg_speed:5.1f}", end='')
    
    encoder.set_rotation_callback(on_rotation)
    
    try:
        while True:
            time.sleep(0.05)  # Faster update for speed
    
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n\n--- Session Summary ---")
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Total rotations: {total_rotations}")
        print(f"Max speed: {max_speed:.1f} r/s")
        print(f"Average speed: {total_rotations/elapsed:.1f} r/s")
    finally:
        encoder.cleanup()

def encoder_calibration():
    """Calibrate encoder sensitivity and accuracy"""
    print("\n=== Encoder Calibration ===")
    print("Test encoder accuracy and sensitivity")
    print("Rotate encoder exactly 10 full turns clockwise")
    print("Press encoder button when done")
    print("Press Ctrl+C to exit")
    
    encoder = RotaryEncoder()
    
    # Assume 20 pulses per revolution (common for rotary encoders)
    PULSES_PER_REVOLUTION = 20
    target_pulses = 10 * PULSES_PER_REVOLUTION
    
    start_position = encoder.get_position()
    calibration_active = True
    
    def on_rotation(position, direction):
        if calibration_active:
            pulses = position - start_position
            revolutions = pulses / PULSES_PER_REVOLUTION
            progress = (pulses / target_pulses) * 100
            
            print(f"\rPulses: {pulses:3d}/{target_pulses} | "
                  f"Revolutions: {revolutions:5.2f}/10.00 | "
                  f"Progress: {progress:5.1f}%", end='')
    
    def on_button():
        nonlocal calibration_active
        if calibration_active:
            calibration_active = False
            final_position = encoder.get_position()
            actual_pulses = final_position - start_position
            actual_revolutions = actual_pulses / PULSES_PER_REVOLUTION
            error = actual_revolutions - 10.0
            accuracy = (1 - abs(error) / 10.0) * 100
            
            print(f"\n\n--- Calibration Results ---")
            print(f"Target: 200 pulses (10 revolutions)")
            print(f"Actual: {actual_pulses} pulses ({actual_revolutions:.2f} revolutions)")
            print(f"Error: {error:+.2f} revolutions")
            print(f"Accuracy: {accuracy:.1f}%")
            
            if accuracy > 95:
                print("✓ Excellent accuracy!")
            elif accuracy > 90:
                print("✓ Good accuracy")
            elif accuracy > 80:
                print("⚠ Fair accuracy - check connections")
            else:
                print("⚠ Poor accuracy - check encoder or connections")
    
    encoder.set_rotation_callback(on_rotation)
    encoder.set_button_callback(on_button)
    
    try:
        while calibration_active:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        encoder.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Rotary Encoder Controller")
    print("========================")
    print(f"CLK (A): GPIO{ENCODER_CLK}")
    print(f"DT (B):  GPIO{ENCODER_DT}")
    print(f"SW:      GPIO{ENCODER_SW}")
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic position tracking")
        print("2. LED direction indicator")
        print("3. Brightness control")
        print("4. Menu navigation")
        print("5. Volume control")
        print("6. Step counter")
        print("7. Speed monitor")
        print("8. Encoder calibration")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_position_tracking()
        elif choice == '2':
            led_direction_indicator()
        elif choice == '3':
            brightness_control()
        elif choice == '4':
            menu_navigation()
        elif choice == '5':
            volume_control()
        elif choice == '6':
            step_counter() 
        elif choice == '7':
            speed_monitor()
        elif choice == '8':
            encoder_calibration()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()