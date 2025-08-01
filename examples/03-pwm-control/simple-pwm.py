#!/usr/bin/env python3
"""
Simple PWM Example - Minimal LED brightness control

This is a simplified version without threads or animations,
useful for understanding basic PWM concepts.

Compile: python3 simple-pwm.py
Run: sudo python3 simple-pwm.py
"""

import gpiod
import time
import signal
import sys

# GPIO Configuration
GPIO_CHIP = "gpiochip4"
LED_PIN = 17
PWM_FREQUENCY = 1000  # 1 kHz

# Global flag for clean shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C"""
    global running
    running = False

def main():
    print("Simple PWM Demo - LED Brightness Control\n")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Open GPIO chip
    try:
        chip = gpiod.Chip(GPIO_CHIP)
        led_line = chip.get_line(LED_PIN)
        led_line.request(consumer="simple-pwm", 
                        type=gpiod.LINE_REQ_DIR_OUT,
                        default_vals=[0])
    except Exception as e:
        print(f"GPIO setup failed: {e}")
        sys.exit(1)
    
    print(f"PWM on GPIO{LED_PIN}")
    print("Watch LED brightness change!")
    print("Press Ctrl+C to exit\n")
    
    # Calculate PWM period in seconds
    period = 1.0 / PWM_FREQUENCY  # 0.001s for 1 kHz
    
    # Main PWM loop - gradually change brightness
    brightness = 0
    direction = 1
    cycle_count = 0
    
    while running:
        # Simple PWM generation
        # Duty cycle determines brightness (0-100%)
        on_time = period * (brightness / 100.0)
        off_time = period - on_time
        
        if on_time > 0:
            led_line.set_value(1)
            time.sleep(on_time)
        
        if off_time > 0:
            led_line.set_value(0)
            time.sleep(off_time)
        
        # Update brightness every 100 cycles (~100ms)
        cycle_count += 1
        if cycle_count >= 100:
            cycle_count = 0
            
            brightness += direction * 5  # 5% steps
            if brightness >= 100:
                brightness = 100
                direction = -1
            elif brightness <= 0:
                brightness = 0
                direction = 1
            
            print(f"\rBrightness: {brightness:3d}%", end='', flush=True)
    
    print("\n\nCleaning up...")
    
    # Turn off LED and cleanup
    led_line.set_value(0)
    led_line.release()
    chip.close()

if __name__ == "__main__":
    main()

"""
This simple example demonstrates:
1. Basic PWM without threading
2. Gradual brightness changes
3. How duty cycle affects LED brightness

Limitations:
- Less accurate timing than threaded version
- Can't do other tasks while generating PWM
- More susceptible to timing jitter
"""