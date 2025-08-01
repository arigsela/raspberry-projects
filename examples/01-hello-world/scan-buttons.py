#!/usr/bin/env python3
"""
Scan multiple GPIO pins to find where a button might be connected
"""

import gpiod
import time
import sys

# GPIO Configuration
GPIO_CHIP = "gpiochip4"
# Common GPIO pins for buttons on Pi
TEST_PINS = [17, 27, 22, 23, 24, 25, 5, 6, 12, 13, 16, 19, 20, 21, 26]

def main():
    print("=== GPIO Button Scanner ===")
    print("This will scan common GPIO pins to detect button presses")
    print("Press and hold your button while the scan runs\n")
    
    try:
        chip = gpiod.Chip(GPIO_CHIP)
    except Exception as e:
        print(f"Failed to open GPIO chip: {e}")
        sys.exit(1)
    
    print("Scanning pins:", TEST_PINS)
    print("\nPress and hold your button now!")
    print("Looking for pins that go LOW (0) when pressed...\n")
    
    # Configure all pins as inputs with pull-up
    lines = {}
    for pin in TEST_PINS:
        try:
            line = chip.get_line(pin)
            line.request(consumer="button-scan",
                        type=gpiod.LINE_REQ_DIR_IN,
                        flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
            lines[pin] = line
        except Exception as e:
            print(f"Could not configure GPIO{pin}: {e}")
    
    # Initial read
    initial_states = {}
    for pin, line in lines.items():
        initial_states[pin] = line.get_value()
    
    # Monitor for changes
    print("Monitoring for 10 seconds...\n")
    start_time = time.time()
    detected_pins = set()
    
    while time.time() - start_time < 10:
        for pin, line in lines.items():
            current_state = line.get_value()
            if current_state != initial_states[pin]:
                if current_state == 0:  # Button pressed
                    if pin not in detected_pins:
                        print(f"✓ BUTTON DETECTED on GPIO{pin}!")
                        detected_pins.add(pin)
        time.sleep(0.01)
    
    # Cleanup
    for line in lines.values():
        line.release()
    chip.close()
    
    print("\n--- Scan Complete ---")
    if detected_pins:
        print(f"Found button(s) on: {sorted(detected_pins)}")
    else:
        print("No button presses detected on any tested pins")
        print("\nPossible issues:")
        print("- Button not connected properly")
        print("- Button connected to a pin not in the scan list")
        print("- Button needs to be connected between GPIO and GND")
        print("- Faulty button or wiring")

if __name__ == "__main__":
    main()