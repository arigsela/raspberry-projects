#!/usr/bin/env python3
"""
Button-Controlled LED - Basic GPIO Input/Output
Demonstrates reading button state and controlling an LED
"""

from gpiozero import LED, Button
from signal import pause
import signal
import sys

# GPIO Configuration
LED_PIN = 17
BUTTON_PIN = 18

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def main():
    """Main program"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize components
    led = LED(LED_PIN)
    button = Button(BUTTON_PIN)
    
    print("Button-Controlled LED - Press Ctrl+C to exit")
    print(f"LED: GPIO{LED_PIN}, Button: GPIO{BUTTON_PIN}")
    print("Press the button to turn on the LED!")
    
    # Event-driven approach
    button.when_pressed = led.on
    button.when_released = led.off
    
    # Alternative callback approach with messages
    def button_pressed():
        led.on()
        print("Button pressed - LED ON")
    
    def button_released():
        led.off()
        print("Button released - LED OFF")
    
    # Use callbacks with print statements
    button.when_pressed = button_pressed
    button.when_released = button_released
    
    # Keep the program running
    pause()

if __name__ == "__main__":
    main()