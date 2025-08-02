#!/usr/bin/env python3
"""
Raspberry Pi 5 GPIO Interrupts - Event-Driven Programming

This example demonstrates event-driven GPIO programming using the gpiod library's
event detection capabilities. Instead of constantly polling, we wait for GPIO
state changes, which is more efficient.

Key concepts:
- Edge detection (rising/falling edges)
- Event timestamps
- Non-blocking I/O
- Multiple input monitoring

Hardware connections:
- Button 1: GPIO27 (pin 13) -> GND
- Button 2: GPIO22 (pin 15) -> GND  
- LED: GPIO17 (pin 11) -> 330Ω -> GND

Author: Your Name
Date: 2024
"""

import gpiod
import time
import signal
import sys
import select
from datetime import datetime

# GPIO Configuration
GPIO_CHIP = "gpiochip4"  # Pi 5's main GPIO chip
LED_PIN = 17            # GPIO17 for LED
BUTTON1_PIN = 27        # GPIO27 for button 1
BUTTON2_PIN = 22        # GPIO22 for button 2

# Event types
RISING_EDGE = gpiod.LINE_REQ_EV_RISING_EDGE
FALLING_EDGE = gpiod.LINE_REQ_EV_FALLING_EDGE
BOTH_EDGES = RISING_EDGE | FALLING_EDGE

# Global flags
running = True
press_count = 0
led_state = False

def signal_handler(sig, frame):
    """Handle Ctrl+C for graceful shutdown"""
    global running
    print("\nShutting down...")
    running = False

def format_timestamp(timestamp_ns):
    """Convert nanosecond timestamp to readable format"""
    # Convert nanoseconds to seconds
    timestamp_s = timestamp_ns / 1_000_000_000
    dt = datetime.fromtimestamp(timestamp_s)
    return dt.strftime("%H:%M:%S.%f")[:-3]  # Show milliseconds

def handle_button_event(event, button_num, led_line):
    """Process button events and control LED"""
    global press_count, led_state
    
    # Get event details
    timestamp = format_timestamp(event.timestamp)
    
    if event.type == RISING_EDGE:
        # Button released (due to pull-up)
        print(f"[{timestamp}] Button {button_num} released")
        
    elif event.type == FALLING_EDGE:
        # Button pressed
        press_count += 1
        print(f"[{timestamp}] Button {button_num} pressed! (Total: {press_count})")
        
        # Toggle LED
        led_state = not led_state
        led_line.set_value(1 if led_state else 0)
        print(f"LED: {'ON' if led_state else 'OFF'}")

def main():
    """Main program function"""
    print("=== Raspberry Pi 5 GPIO Interrupts Demo ===")
    print("Event-driven GPIO Programming\n")
    
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
        button1_line = chip.get_line(BUTTON1_PIN)
        button2_line = chip.get_line(BUTTON2_PIN)
    except Exception as e:
        print(f"Failed to get GPIO lines: {e}")
        chip.close()
        sys.exit(1)
    
    # Configure LED as output
    try:
        led_line.request(consumer="gpio-interrupts",
                        type=gpiod.LINE_REQ_DIR_OUT,
                        default_vals=[0])
    except Exception as e:
        print(f"Failed to configure LED: {e}")
        chip.close()
        sys.exit(1)
    
    # Configure buttons for event detection
    # We request both edges to see press and release
    try:
        button1_line.request(consumer="gpio-interrupts",
                           type=gpiod.LINE_REQ_EV_BOTH_EDGES,
                           flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
        
        button2_line.request(consumer="gpio-interrupts",
                           type=gpiod.LINE_REQ_EV_BOTH_EDGES,
                           flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
    except Exception as e:
        print(f"Failed to configure buttons: {e}")
        led_line.release()
        chip.close()
        sys.exit(1)
    
    print("GPIO Configuration:")
    print(f"  LED: GPIO{LED_PIN}")
    print(f"  Button 1: GPIO{BUTTON1_PIN}")
    print(f"  Button 2: GPIO{BUTTON2_PIN}")
    print("\nWaiting for button events...")
    print("Press either button to toggle LED")
    print("Press Ctrl+C to exit\n")
    
    # Get file descriptors for event monitoring
    button1_fd = button1_line.event_get_fd()
    button2_fd = button2_line.event_get_fd()
    
    # Main event loop
    while running:
        # Use select to wait for events on either button
        # Timeout of 0.1s allows checking the running flag
        readable, _, _ = select.select([button1_fd, button2_fd], [], [], 0.1)
        
        # Check for button 1 events
        if button1_fd in readable:
            event = button1_line.event_read()
            if event:
                handle_button_event(event, 1, led_line)
        
        # Check for button 2 events
        if button2_fd in readable:
            event = button2_line.event_read()
            if event:
                handle_button_event(event, 2, led_line)
    
    # Cleanup
    print(f"\nTotal button presses: {press_count}")
    print("Cleaning up GPIO...")
    
    led_line.set_value(0)  # Turn off LED
    led_line.release()
    button1_line.release()
    button2_line.release()
    chip.close()
    
    print("Goodbye!")

if __name__ == "__main__":
    main()

"""
Advanced Concepts Explained:

1. Event-Driven vs Polling:
   - Polling: Constantly checking GPIO state (wastes CPU)
   - Event-Driven: Wait for state changes (efficient)
   - Uses select() to monitor multiple inputs

2. Edge Detection:
   - Rising Edge: LOW to HIGH transition
   - Falling Edge: HIGH to LOW transition
   - With pull-up: Press = falling, Release = rising

3. Event Timestamps:
   - Hardware timestamps for precise timing
   - Useful for debouncing and timing analysis

4. File Descriptors:
   - Linux treats everything as files
   - GPIO events use file descriptors
   - select() monitors multiple descriptors

5. Non-Blocking I/O:
   - Program can do other work while waiting
   - More responsive than polling
   - Better for battery-powered devices

Extending This Example:
- Add debouncing logic using timestamps
- Count press duration for long-press detection
- Monitor more inputs simultaneously
- Create interrupt service routines
"""