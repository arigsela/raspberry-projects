#!/usr/bin/env python3
"""
Raspberry Pi 5 Hello World - LED Blink with Button Control

This is your first Raspberry Pi 5 Python program! It demonstrates:
- Controlling an LED (output)
- Reading a button press (input)
- Using the gpiod library for Pi 5 compatibility

The gpiod library is the modern way to control GPIO on Raspberry Pi,
replacing the older RPi.GPIO which doesn't work on Pi 5.

Hardware connections:
- LED: GPIO17 (pin 11) -> 330Ω resistor -> LED -> GND
- Button: GPIO27 (pin 13) -> Button -> GND

Author: Your Name
Date: 2024
"""

import gpiod
import time
import signal
import sys

# GPIO Configuration
GPIO_CHIP = "gpiochip4"  # Pi 5's main GPIO chip
LED_PIN = 17            # GPIO17 for LED
BUTTON_PIN = 27         # GPIO27 for button

# Global flag for clean shutdown
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C for graceful shutdown"""
    global running
    print("\nShutting down...")
    running = False

def main():
    """Main program function"""
    print("=== Raspberry Pi 5 Hello World ===")
    print("LED Control with Button Input\n")
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Open the GPIO chip
    # This is like opening a file - we need to access the GPIO hardware
    try:
        chip = gpiod.Chip(GPIO_CHIP)
    except Exception as e:
        print(f"Failed to open GPIO chip: {e}")
        sys.exit(1)
    
    # Get the GPIO lines (pins) we want to use
    try:
        led_line = chip.get_line(LED_PIN)
        button_line = chip.get_line(BUTTON_PIN)
    except Exception as e:
        print(f"Failed to get GPIO lines: {e}")
        chip.close()
        sys.exit(1)
    
    # Configure the LED pin as output
    # consumer: a name for this program (shows in GPIO debugging)
    # type: gpiod.LINE_REQ_DIR_OUT means output
    # default_vals: initial value (0 = off)
    try:
        led_line.request(consumer="hello-world", 
                        type=gpiod.LINE_REQ_DIR_OUT,
                        default_vals=[0])
    except Exception as e:
        print(f"Failed to configure LED pin: {e}")
        chip.close()
        sys.exit(1)
    
    # Configure the button pin as input with pull-up resistor
    # flags: BIAS_PULL_UP means internal pull-up resistor enabled
    try:
        button_line.request(consumer="hello-world",
                           type=gpiod.LINE_REQ_DIR_IN,
                           flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
    except Exception as e:
        print(f"Failed to configure button pin: {e}")
        led_line.release()
        chip.close()
        sys.exit(1)
    
    print(f"LED connected to GPIO{LED_PIN}")
    print(f"Button connected to GPIO{BUTTON_PIN}")
    print("\nPress the button to toggle the LED on/off")
    print("Press Ctrl+C to exit\n")
    
    # Initialize variables
    led_state = False
    last_button_state = 1  # Pull-up means 1 when not pressed
    
    # Main control loop
    while running:
        # Read button state
        # Returns 1 when not pressed (pull-up), 0 when pressed
        button_state = button_line.get_value()
        
        # Detect button press (transition from not pressed to pressed)
        if button_state == 0 and last_button_state == 1:
            print("Button pressed!")
            led_state = not led_state  # Toggle LED
            led_line.set_value(1 if led_state else 0)
            print(f"LED: {'ON' if led_state else 'OFF'}")
            
        # Detect button release
        elif button_state == 1 and last_button_state == 0:
            print("Button released!")
        
        # Remember button state for next iteration
        last_button_state = button_state
        
        # Small delay to prevent CPU spinning
        # 10ms is good for responsive button detection
        time.sleep(0.01)
    
    # Cleanup
    print("\nCleaning up GPIO...")
    led_line.set_value(0)  # Turn off LED
    led_line.release()     # Release the GPIO line
    button_line.release()
    chip.close()          # Close the GPIO chip
    
    print("Goodbye!")

if __name__ == "__main__":
    main()

"""
Key Concepts Explained:

1. gpiod Library:
   - Modern GPIO control for Linux
   - Works with Pi 5's new RP1 chip
   - Object-oriented interface

2. GPIO Chip:
   - Represents the GPIO hardware
   - Pi 5 uses "gpiochip4" 
   - Must be opened before use

3. GPIO Lines:
   - Individual pins on the chip
   - Can be configured as input or output
   - Support various flags (pull-up, pull-down, etc.)

4. Pull-up Resistor:
   - Keeps input at HIGH (1) when not connected
   - Button press connects to GND, making it LOW (0)
   - Prevents floating input issues

5. Event Loop:
   - Continuously checks inputs
   - Responds to state changes
   - Small sleep prevents 100% CPU usage

Common Issues:
- Permission denied: Run with sudo or add user to gpio group
- Chip not found: Make sure you're on Pi 5
- LED doesn't light: Check polarity (long leg is positive)
"""