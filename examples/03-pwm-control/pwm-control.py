#!/usr/bin/env python3
"""
Raspberry Pi 5 PWM LED Brightness Control

This program demonstrates Pulse Width Modulation (PWM) for LED brightness control
on Raspberry Pi 5. Since Pi 5's gpiod doesn't have built-in PWM support,
we implement software PWM using threading.

PWM Concepts:
- Frequency: How many on/off cycles per second (Hz)
- Duty Cycle: Percentage of time the signal is HIGH (0-100%)
- Period: Total time for one complete cycle (1/frequency)

Hardware setup:
- LED connected to GPIO17 (pin 11) with a 330Ω resistor to GND
- Optional: Button on GPIO27 for mode switching

Author: Your Name
Date: 2024
"""

import gpiod
import threading
import time
import signal
import sys
import math
from enum import Enum

# GPIO Configuration
GPIO_CHIP = "gpiochip4"  # Pi 5 main GPIO chip
LED_PIN = 17             # GPIO17 for LED output
BUTTON_PIN = 27          # GPIO27 for mode selection

# PWM Configuration
PWM_FREQUENCY = 1000     # 1 kHz PWM frequency
PWM_PERIOD = 1.0 / PWM_FREQUENCY  # Period in seconds

# Animation modes
class AnimationMode(Enum):
    MANUAL = 0      # Fixed brightness
    BREATHING = 1   # Smooth fade in/out
    SINE_WAVE = 2   # Sine wave pattern
    STROBE = 3      # Fast blinking

# Global variables
running = True
current_mode = AnimationMode.MANUAL
manual_brightness = 50  # Default 50% brightness

class PWMController:
    """Software PWM controller using threading"""
    
    def __init__(self, line, frequency=1000):
        self.line = line
        self.frequency = frequency
        self.period = 1.0 / frequency
        self.duty_cycle = 0
        self.active = True
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._pwm_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def _pwm_loop(self):
        """PWM generation loop running in separate thread"""
        while self.active:
            with self.lock:
                duty = self.duty_cycle
            
            # Calculate on and off times
            on_time = self.period * (duty / 100.0)
            off_time = self.period - on_time
            
            if duty > 0:
                self.line.set_value(1)
                time.sleep(on_time)
            
            if duty < 100:
                self.line.set_value(0)
                time.sleep(off_time)
    
    def set_duty_cycle(self, duty_cycle):
        """Set PWM duty cycle (0-100%)"""
        duty_cycle = max(0, min(100, duty_cycle))  # Clamp to 0-100
        with self.lock:
            self.duty_cycle = duty_cycle
    
    def stop(self):
        """Stop PWM generation"""
        self.active = False
        self.thread.join()
        self.line.set_value(0)

def signal_handler(sig, frame):
    """Handle Ctrl+C for graceful shutdown"""
    global running
    print("\nShutting down PWM control...")
    running = False

def breathing_animation(pwm):
    """Breathing effect - smooth fade in and out"""
    # Use static variables to maintain state between calls
    if not hasattr(breathing_animation, 'brightness'):
        breathing_animation.brightness = 0
        breathing_animation.direction = 1
    
    breathing_animation.brightness += breathing_animation.direction * 2
    
    if breathing_animation.brightness >= 100:
        breathing_animation.brightness = 100
        breathing_animation.direction = -1
    elif breathing_animation.brightness <= 0:
        breathing_animation.brightness = 0
        breathing_animation.direction = 1
    
    pwm.set_duty_cycle(breathing_animation.brightness)

def sine_wave_animation(pwm):
    """Sine wave pattern for smooth periodic brightness"""
    # Use static variable for phase
    if not hasattr(sine_wave_animation, 'phase'):
        sine_wave_animation.phase = 0.0
    
    # Calculate brightness using sine function
    # Maps sine wave (-1 to 1) to brightness (0 to 100)
    brightness = int(50 * (1 + math.sin(sine_wave_animation.phase)))
    
    pwm.set_duty_cycle(brightness)
    
    # Increment phase
    sine_wave_animation.phase += 0.1
    if sine_wave_animation.phase > 2 * math.pi:
        sine_wave_animation.phase -= 2 * math.pi

def strobe_animation(pwm):
    """Strobe effect - rapid on/off"""
    if not hasattr(strobe_animation, 'state'):
        strobe_animation.state = False
        strobe_animation.counter = 0
    
    strobe_animation.counter += 1
    if strobe_animation.counter >= 5:  # Adjust for strobe speed
        strobe_animation.counter = 0
        strobe_animation.state = not strobe_animation.state
        pwm.set_duty_cycle(100 if strobe_animation.state else 0)

def main():
    """Main program function"""
    global current_mode
    
    print("\n=== Raspberry Pi 5 PWM LED Control ===")
    print("Demonstrates software PWM for LED brightness\n")
    
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Open GPIO chip
    try:
        chip = gpiod.Chip(GPIO_CHIP)
    except Exception as e:
        print(f"Failed to open GPIO chip: {e}")
        sys.exit(1)
    
    # Get GPIO lines
    try:
        led_line = chip.get_line(LED_PIN)
        button_line = chip.get_line(BUTTON_PIN)
    except Exception as e:
        print(f"Failed to get GPIO lines: {e}")
        chip.close()
        sys.exit(1)
    
    # Configure LED as output
    try:
        led_line.request(consumer="pwm-control",
                        type=gpiod.LINE_REQ_DIR_OUT,
                        default_vals=[0])
    except Exception as e:
        print(f"Failed to configure LED: {e}")
        chip.close()
        sys.exit(1)
    
    # Configure button as input with pull-up
    try:
        button_line.request(consumer="pwm-control",
                           type=gpiod.LINE_REQ_DIR_IN,
                           flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
    except Exception as e:
        print(f"Failed to configure button: {e}")
        led_line.release()
        chip.close()
        sys.exit(1)
    
    # Create PWM controller
    pwm = PWMController(led_line, PWM_FREQUENCY)
    
    print(f"PWM Configuration:")
    print(f"  Frequency: {PWM_FREQUENCY} Hz")
    print(f"  Period: {PWM_PERIOD*1000:.2f} ms")
    print(f"  Resolution: 100 steps\n")
    
    print("Controls:")
    print("  Press button to cycle through modes")
    print("  Modes: Manual -> Breathing -> Sine Wave -> Strobe")
    print("  Press Ctrl+C to exit\n")
    
    # Main control loop
    last_button_state = 1
    animation_counter = 0
    
    while running:
        # Check button for mode change
        button_state = button_line.get_value()
        
        # Detect button press (falling edge)
        if button_state == 0 and last_button_state == 1:
            # Cycle to next mode
            mode_list = list(AnimationMode)
            current_idx = mode_list.index(current_mode)
            current_mode = mode_list[(current_idx + 1) % len(mode_list)]
            
            mode_names = {
                AnimationMode.MANUAL: "Manual (50%)",
                AnimationMode.BREATHING: "Breathing",
                AnimationMode.SINE_WAVE: "Sine Wave",
                AnimationMode.STROBE: "Strobe"
            }
            print(f"Mode: {mode_names[current_mode]}")
        
        last_button_state = button_state
        
        # Run animation based on current mode
        animation_counter += 1
        if animation_counter >= 10:  # Control animation speed
            animation_counter = 0
            
            if current_mode == AnimationMode.MANUAL:
                pwm.set_duty_cycle(manual_brightness)
            elif current_mode == AnimationMode.BREATHING:
                breathing_animation(pwm)
            elif current_mode == AnimationMode.SINE_WAVE:
                sine_wave_animation(pwm)
            elif current_mode == AnimationMode.STROBE:
                strobe_animation(pwm)
        
        time.sleep(0.01)  # 10ms main loop delay
    
    # Cleanup
    print("\nCleaning up...")
    pwm.stop()
    led_line.release()
    button_line.release()
    chip.close()
    
    print("PWM control terminated.")

if __name__ == "__main__":
    main()

"""
Key concepts demonstrated:

1. Software PWM Implementation:
   - Uses threading for consistent timing
   - Separate thread generates PWM signal
   - Thread-safe duty cycle updates

2. PWM Theory:
   - Frequency determines flicker perception
   - Duty cycle controls average power/brightness
   - Higher frequency = smoother control

3. Python Threading:
   - Threading module for concurrent execution
   - Lock for thread synchronization
   - Daemon threads for clean shutdown

4. Animation Patterns:
   - State persistence using function attributes
   - Mathematical functions for smooth animations
   - Different visual effects showcase PWM versatility

Note: For production use, consider hardware PWM pins or
kernel PWM drivers for better performance and accuracy.
"""