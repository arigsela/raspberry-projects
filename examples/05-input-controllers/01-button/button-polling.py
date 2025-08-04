#!/usr/bin/env python3
"""
Button-Controlled LED - Polling Method
Alternative implementation using polling instead of events
"""

from gpiozero import LED, Button
from time import sleep
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
    """Main program using polling method"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize components
    led = LED(LED_PIN)
    button = Button(BUTTON_PIN)
    
    print("Button-Controlled LED (Polling) - Press Ctrl+C to exit")
    print(f"LED: GPIO{LED_PIN}, Button: GPIO{BUTTON_PIN}")
    print("Press and hold the button to turn on the LED!")
    
    # Track button state to detect changes
    last_state = False
    
    # Main polling loop
    while True:
        current_state = button.is_pressed
        
        # Detect state changes
        if current_state != last_state:
            if current_state:
                led.on()
                print("Button pressed - LED ON")
            else:
                led.off()
                print("Button released - LED OFF")
            
            last_state = current_state
        
        # Small delay to prevent CPU spinning
        sleep(0.01)

if __name__ == "__main__":
    main()