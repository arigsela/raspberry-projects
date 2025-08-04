#!/usr/bin/env python3
"""
Interactive RGB LED Control
Control RGB LED colors using keyboard input
"""

from gpiozero import RGBLED
import signal
import sys

# GPIO Configuration
RED_PIN = 17
GREEN_PIN = 18
BLUE_PIN = 27

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def get_color_value(color_name):
    """Get color value from user (0-100)"""
    while True:
        try:
            value = int(input(f"Enter {color_name} value (0-100): "))
            if 0 <= value <= 100:
                return value / 100  # Convert to 0-1 range
            else:
                print("Please enter a value between 0 and 100")
        except ValueError:
            print("Please enter a valid number")

def main():
    """Interactive RGB LED control"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize RGB LED
    led = RGBLED(red=RED_PIN, green=GREEN_PIN, blue=BLUE_PIN)
    
    print("Interactive RGB LED Control - Press Ctrl+C to exit")
    print(f"Pins - Red: GPIO{RED_PIN}, Green: GPIO{GREEN_PIN}, Blue: GPIO{BLUE_PIN}")
    print("\nCommands:")
    print("  1-8: Preset colors")
    print("  c: Custom color")
    print("  p: Pulse effect")
    print("  b: Blink effect")
    print("  r: Rainbow cycle")
    print("  q: Quit")
    
    # Preset colors
    presets = {
        '1': ("Red", (1, 0, 0)),
        '2': ("Green", (0, 1, 0)),
        '3': ("Blue", (0, 0, 1)),
        '4': ("Yellow", (1, 1, 0)),
        '5': ("Cyan", (0, 1, 1)),
        '6': ("Magenta", (1, 0, 1)),
        '7': ("White", (1, 1, 1)),
        '8': ("Off", (0, 0, 0))
    }
    
    while True:
        command = input("\nEnter command: ").lower()
        
        if command == 'q':
            break
        elif command in presets:
            name, color = presets[command]
            print(f"Setting color to: {name}")
            led.color = color
        elif command == 'c':
            print("Custom color mode")
            r = get_color_value("red")
            g = get_color_value("green")
            b = get_color_value("blue")
            led.color = (r, g, b)
            print(f"Custom color set: R={r:.2f}, G={g:.2f}, B={b:.2f}")
        elif command == 'p':
            print("Pulse effect (2 times)")
            led.pulse(fade_in_time=0.5, fade_out_time=0.5, n=2)
        elif command == 'b':
            print("Blink effect (5 times)")
            led.blink(on_time=0.5, off_time=0.5, n=5)
        elif command == 'r':
            print("Rainbow cycle (press Enter to stop)")
            # Simple rainbow cycle
            import threading
            stop_rainbow = False
            
            def rainbow():
                while not stop_rainbow:
                    # Red to Yellow
                    for i in range(101):
                        if stop_rainbow: break
                        led.color = (1, i/100, 0)
                        sleep(0.01)
                    # Yellow to Green
                    for i in range(101):
                        if stop_rainbow: break
                        led.color = (1-i/100, 1, 0)
                        sleep(0.01)
                    # Green to Cyan
                    for i in range(101):
                        if stop_rainbow: break
                        led.color = (0, 1, i/100)
                        sleep(0.01)
                    # Cyan to Blue
                    for i in range(101):
                        if stop_rainbow: break
                        led.color = (0, 1-i/100, 1)
                        sleep(0.01)
                    # Blue to Magenta
                    for i in range(101):
                        if stop_rainbow: break
                        led.color = (i/100, 0, 1)
                        sleep(0.01)
                    # Magenta to Red
                    for i in range(101):
                        if stop_rainbow: break
                        led.color = (1, 0, 1-i/100)
                        sleep(0.01)
            
            from time import sleep
            rainbow_thread = threading.Thread(target=rainbow)
            rainbow_thread.start()
            input()  # Wait for Enter
            stop_rainbow = True
            rainbow_thread.join()
            led.off()
        else:
            print("Invalid command. Try again.")
    
    print("Goodbye!")
    led.off()

if __name__ == "__main__":
    main()