#!/usr/bin/env python3
"""
RGB LED Color Control - PWM and Color Mixing
Demonstrates color mixing with a common cathode RGB LED
"""

from gpiozero import RGBLED
from time import sleep
import signal
import sys

# GPIO Configuration for RGB LED
RED_PIN = 17
GREEN_PIN = 18
BLUE_PIN = 27

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def main():
    """Main program demonstrating RGB LED colors"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize RGB LED (common cathode)
    led = RGBLED(red=RED_PIN, green=GREEN_PIN, blue=BLUE_PIN)
    
    print("RGB LED Color Demo - Press Ctrl+C to exit")
    print(f"Pins - Red: GPIO{RED_PIN}, Green: GPIO{GREEN_PIN}, Blue: GPIO{BLUE_PIN}")
    print("\nCycling through colors...")
    
    # Define colors as (red, green, blue) tuples
    colors = {
        "Red": (1, 0, 0),
        "Green": (0, 1, 0),
        "Blue": (0, 0, 1),
        "Yellow": (1, 1, 0),
        "Cyan": (0, 1, 1),
        "Magenta": (1, 0, 1),
        "White": (1, 1, 1),
        "Off": (0, 0, 0)
    }
    
    # Main color cycling loop
    while True:
        # Cycle through defined colors
        for color_name, (r, g, b) in colors.items():
            print(f"Color: {color_name}")
            led.color = (r, g, b)
            sleep(2)
        
        # Smooth color transitions
        print("\nSmooth color transitions...")
        
        # Fade from red to green
        print("Red to Green fade")
        for i in range(101):
            led.color = (1 - i/100, i/100, 0)
            sleep(0.01)
        
        # Fade from green to blue
        print("Green to Blue fade")
        for i in range(101):
            led.color = (0, 1 - i/100, i/100)
            sleep(0.01)
        
        # Fade from blue to red
        print("Blue to Red fade")
        for i in range(101):
            led.color = (i/100, 0, 1 - i/100)
            sleep(0.01)
        
        # Rainbow effect
        print("\nRainbow effect...")
        led.pulse(fade_in_time=1, fade_out_time=1, n=2)
        sleep(2)

if __name__ == "__main__":
    main()