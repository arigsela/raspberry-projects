#!/usr/bin/env python3
"""
7-Segment Display Control
Display numbers and characters on a 7-segment LED display
"""

from gpiozero import LED
import time
import signal
import sys

# GPIO Pin Configuration for 7-segment display
# Segments: a, b, c, d, e, f, g, dp (decimal point)
SEGMENT_PINS = {
    'a': 17,  # Top
    'b': 18,  # Top right
    'c': 27,  # Bottom right
    'd': 22,  # Bottom
    'e': 23,  # Bottom left
    'f': 24,  # Top left
    'g': 25,  # Middle
    'dp': 4   # Decimal point
}

# Common cathode configuration (1 = LED on, 0 = LED off)
# For common anode, invert these values
DIGITS = {
    '0': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0, 'dp': 0},
    '1': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 0},
    '2': {'a': 1, 'b': 1, 'c': 0, 'd': 1, 'e': 1, 'f': 0, 'g': 1, 'dp': 0},
    '3': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 0, 'f': 0, 'g': 1, 'dp': 0},
    '4': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 1, 'g': 1, 'dp': 0},
    '5': {'a': 1, 'b': 0, 'c': 1, 'd': 1, 'e': 0, 'f': 1, 'g': 1, 'dp': 0},
    '6': {'a': 1, 'b': 0, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    '7': {'a': 1, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 0},
    '8': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    '9': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 0, 'f': 1, 'g': 1, 'dp': 0},
    'A': {'a': 1, 'b': 1, 'c': 1, 'd': 0, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    'b': {'a': 0, 'b': 0, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    'C': {'a': 1, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 0, 'dp': 0},
    'd': {'a': 0, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 0, 'g': 1, 'dp': 0},
    'E': {'a': 1, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    'F': {'a': 1, 'b': 0, 'c': 0, 'd': 0, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    'H': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    'L': {'a': 0, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 0, 'dp': 0},
    'P': {'a': 1, 'b': 1, 'c': 0, 'd': 0, 'e': 1, 'f': 1, 'g': 1, 'dp': 0},
    'U': {'a': 0, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0, 'dp': 0},
    '-': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 1, 'dp': 0},
    '_': {'a': 0, 'b': 0, 'c': 0, 'd': 1, 'e': 0, 'f': 0, 'g': 0, 'dp': 0},
    ' ': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 0},
    '.': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'dp': 1}
}

class SevenSegmentDisplay:
    """Control a 7-segment display"""
    
    def __init__(self, segment_pins=SEGMENT_PINS, common_cathode=True):
        """Initialize the display
        
        Args:
            segment_pins: Dictionary mapping segment names to GPIO pins
            common_cathode: True for common cathode, False for common anode
        """
        self.segments = {}
        self.common_cathode = common_cathode
        
        # Create LED objects for each segment
        for segment, pin in segment_pins.items():
            self.segments[segment] = LED(pin)
    
    def clear(self):
        """Turn off all segments"""
        for segment in self.segments.values():
            segment.off()
    
    def display_digit(self, digit, decimal_point=False):
        """Display a digit or character
        
        Args:
            digit: Character to display ('0'-'9', 'A'-'F', etc.)
            decimal_point: Whether to show decimal point
        """
        digit = str(digit).upper()
        
        if digit in DIGITS:
            pattern = DIGITS[digit].copy()
            if decimal_point:
                pattern['dp'] = 1
            
            for segment_name, state in pattern.items():
                # Invert for common anode
                if not self.common_cathode:
                    state = 1 - state
                
                if state:
                    self.segments[segment_name].on()
                else:
                    self.segments[segment_name].off()
        else:
            self.clear()
    
    def display_segments(self, segments):
        """Display specific segments
        
        Args:
            segments: List of segment names to turn on
        """
        self.clear()
        for segment in segments:
            if segment in self.segments:
                self.segments[segment].on()
    
    def test_segments(self):
        """Test each segment individually"""
        for name, led in self.segments.items():
            print(f"Testing segment {name}")
            led.on()
            time.sleep(0.5)
            led.off()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        for segment in self.segments.values():
            segment.close()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def count_demo(display):
    """Count from 0 to 9"""
    print("\n=== Counting Demo ===")
    print("Counting 0-9...")
    
    for i in range(10):
        display.display_digit(i)
        time.sleep(0.5)
    
    display.clear()

def hex_demo(display):
    """Display hexadecimal digits"""
    print("\n=== Hexadecimal Demo ===")
    print("Displaying 0-F...")
    
    hex_digits = '0123456789ABCDEF'
    for digit in hex_digits:
        display.display_digit(digit)
        time.sleep(0.5)
    
    display.clear()

def animation_demo(display):
    """Animated patterns"""
    print("\n=== Animation Demo ===")
    
    # Rotating pattern
    print("Rotating pattern...")
    rotation = ['a', 'b', 'c', 'd', 'e', 'f']
    for _ in range(10):
        for segment in rotation:
            display.display_segments([segment])
            time.sleep(0.1)
    
    # Figure 8 pattern
    print("Figure 8 pattern...")
    figure8 = [
        ['a', 'f', 'g'],
        ['g', 'e', 'd'],
        ['d', 'c', 'g'],
        ['g', 'b', 'a']
    ]
    for _ in range(5):
        for segments in figure8:
            display.display_segments(segments)
            time.sleep(0.1)
    
    display.clear()

def dice_demo(display):
    """Dice rolling simulation"""
    print("\n=== Dice Demo ===")
    print("Rolling dice...")
    
    import random
    
    # Animate rolling
    for _ in range(20):
        digit = random.randint(1, 6)
        display.display_digit(digit)
        time.sleep(0.05 + _ * 0.01)  # Slow down
    
    # Show final result
    final = random.randint(1, 6)
    print(f"Rolled: {final}")
    display.display_digit(final, decimal_point=True)
    time.sleep(2)
    
    display.clear()

def temperature_display(display):
    """Display temperature readings"""
    print("\n=== Temperature Display ===")
    print("Simulating temperature readings...")
    
    temps = [20, 21, 22, 23, 24, 25, 24, 23, 22, 21]
    
    for temp in temps:
        # Display tens
        tens = temp // 10
        display.display_digit(tens)
        time.sleep(0.7)
        
        # Display units
        units = temp % 10
        display.display_digit(units)
        time.sleep(0.7)
        
        # Display C for Celsius
        display.display_digit('C')
        time.sleep(0.7)
        
        # Blank
        display.clear()
        time.sleep(0.3)

def error_codes(display):
    """Display error codes"""
    print("\n=== Error Code Display ===")
    
    errors = [
        ('E', '1', "Sensor error"),
        ('E', '2', "Overheating"),
        ('E', '3', "Low battery"),
        ('E', '4', "Connection lost")
    ]
    
    for e_char, code, description in errors:
        print(f"Error {e_char}{code}: {description}")
        
        # Flash E
        for _ in range(3):
            display.display_digit(e_char)
            time.sleep(0.2)
            display.clear()
            time.sleep(0.2)
        
        # Show code
        display.display_digit(code)
        time.sleep(1)
        
        display.clear()
        time.sleep(0.5)

def custom_characters(display):
    """Display custom patterns"""
    print("\n=== Custom Characters ===")
    
    # Define custom patterns
    patterns = {
        "square": ['a', 'b', 'd', 'e'],
        "top_bar": ['a'],
        "bottom_bar": ['d'],
        "left_bars": ['e', 'f'],
        "right_bars": ['b', 'c'],
        "cross": ['b', 'e', 'g'],
        "h_shape": ['b', 'c', 'e', 'f', 'g']
    }
    
    for name, segments in patterns.items():
        print(f"Pattern: {name}")
        display.display_segments(segments)
        time.sleep(1)
    
    display.clear()

def segment_test(display):
    """Test individual segments"""
    print("\n=== Segment Test ===")
    print("Testing each segment...")
    
    display.test_segments()
    
    # All on
    print("All segments on")
    display.display_digit('8', decimal_point=True)
    time.sleep(1)
    
    display.clear()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("7-Segment Display Control")
    print("========================")
    print("GPIO Pins:")
    for segment, pin in SEGMENT_PINS.items():
        print(f"  Segment {segment}: GPIO{pin}")
    
    # Initialize display
    display = SevenSegmentDisplay(SEGMENT_PINS, common_cathode=True)
    
    try:
        while True:
            print("\n\nSelect Demo:")
            print("1. Count 0-9")
            print("2. Hexadecimal (0-F)")
            print("3. Animations")
            print("4. Dice roll")
            print("5. Temperature display")
            print("6. Error codes")
            print("7. Custom characters")
            print("8. Segment test")
            print("9. Exit")
            
            choice = input("\nEnter choice (1-9): ").strip()
            
            if choice == '1':
                count_demo(display)
            elif choice == '2':
                hex_demo(display)
            elif choice == '3':
                animation_demo(display)
            elif choice == '4':
                dice_demo(display)
            elif choice == '5':
                temperature_display(display)
            elif choice == '6':
                error_codes(display)
            elif choice == '7':
                custom_characters(display)
            elif choice == '8':
                segment_test(display)
            elif choice == '9':
                break
            else:
                print("Invalid choice")
    
    finally:
        display.cleanup()
        print("\nGoodbye!")

if __name__ == "__main__":
    main()