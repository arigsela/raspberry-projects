#!/usr/bin/env python3
"""
Blinking LED - Basic GPIO Output Control
Demonstrates fundamental GPIO output operations on Raspberry Pi 5
"""

from gpiozero import LED
from time import sleep
import signal
import sys

# GPIO Configuration
LED_PIN = 17

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def main():
    """Main program loop"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize LED
    led = LED(LED_PIN)
    
    print("Blinking LED - Press Ctrl+C to exit")
    print(f"LED connected to GPIO{LED_PIN}")
    
    # Main loop
    while True:
        led.on()
        print("LED ON")
        sleep(1)
        
        led.off()
        print("LED OFF")
        sleep(1)

if __name__ == "__main__":
    main()