#!/usr/bin/env python3
"""
4-Digit 7-Segment Display Control
Display numbers and text on a multiplexed 4-digit display
"""

from gpiozero import OutputDevice, Button
import time
import signal
import sys
import threading
from datetime import datetime

# GPIO Configuration for segments (common cathode)
SEGMENTS = {
    'a': 17,  # Top
    'b': 27,  # Top right
    'c': 22,  # Bottom right
    'd': 10,  # Bottom
    'e': 9,   # Bottom left
    'f': 11,  # Top left
    'g': 5,   # Middle
    'dp': 4   # Decimal point
}

# GPIO Configuration for digit selection (active low)
DIGITS = [18, 23, 24, 25]  # Digit 1, 2, 3, 4

# Character definitions
CHARACTERS = {
    '0': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0},
    '1': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 0, 'g': 0},
    '2': {'a': 1, 'b': 1, 'c': 0, 'd': 1, 'e': 1, 'f': 0, 'g': 1},
    '3': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 0, 'f': 0, 'g': 1},
    '4': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 1, 'g': 1},
    '5': {'a': 1, 'b': 0, 'c': 1, 'd': 1, 'e': 0, 'f': 1, 'g': 1},
    '6': {'a': 1, 'b': 0, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1},
    '7': {'a': 1, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 0, 'g': 0},
    '8': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1},
    '9': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 0, 'f': 1, 'g': 1},
    'A': {'a': 1, 'b': 1, 'c': 1, 'd': 0, 'e': 1, 'f': 1, 'g': 1},
    'b': {'a': 0, 'b': 0, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1},
    'C': {'a': 1, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 0},
    'd': {'a': 0, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 0, 'g': 1},
    'E': {'a': 1, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 1},
    'F': {'a': 1, 'b': 0, 'c': 0, 'd': 0, 'e': 1, 'f': 1, 'g': 1},
    'H': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 1, 'f': 1, 'g': 1},
    'L': {'a': 0, 'b': 0, 'c': 0, 'd': 1, 'e': 1, 'f': 1, 'g': 0},
    'P': {'a': 1, 'b': 1, 'c': 0, 'd': 0, 'e': 1, 'f': 1, 'g': 1},
    'U': {'a': 0, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0},
    '-': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 1},
    '_': {'a': 0, 'b': 0, 'c': 0, 'd': 1, 'e': 0, 'f': 0, 'g': 0},
    ' ': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0},
    '.': {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0}
}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class FourDigitDisplay:
    """Control a 4-digit 7-segment display"""
    
    def __init__(self):
        """Initialize display"""
        # Create segment outputs
        self.segments = {}
        for name, pin in SEGMENTS.items():
            self.segments[name] = OutputDevice(pin)
        
        # Create digit selectors (active low)
        self.digits = []
        for pin in DIGITS:
            digit = OutputDevice(pin, active_high=False)
            digit.off()  # Turn off all digits initially
            self.digits.append(digit)
        
        # Display buffer
        self.buffer = ['', '', '', '']
        self.decimal_points = [False, False, False, False]
        
        # Multiplexing thread
        self.running = False
        self.display_thread = None
        self.brightness = 1.0  # 0.0 to 1.0
    
    def set_digit(self, position, character, decimal=False):
        """Set a single digit"""
        if 0 <= position < 4:
            self.buffer[position] = str(character).upper()
            self.decimal_points[position] = decimal
    
    def set_number(self, number, leading_zeros=False, decimal_pos=None):
        """Display a number"""
        # Convert to string
        num_str = str(int(number))
        
        # Pad with zeros or spaces
        if leading_zeros:
            num_str = num_str.zfill(4)
        else:
            num_str = num_str.rjust(4)
        
        # Set digits
        for i in range(4):
            if i < len(num_str):
                self.buffer[i] = num_str[i]
            else:
                self.buffer[i] = ' '
            
            # Set decimal point
            self.decimal_points[i] = (decimal_pos == i)
    
    def set_text(self, text):
        """Display text (up to 4 characters)"""
        text = str(text).upper()[:4]
        text = text.ljust(4)  # Pad with spaces
        
        for i in range(4):
            self.buffer[i] = text[i]
    
    def set_time(self, hours, minutes, colon=True):
        """Display time in HH:MM format"""
        self.buffer[0] = str(hours // 10)
        self.buffer[1] = str(hours % 10)
        self.buffer[2] = str(minutes // 10)
        self.buffer[3] = str(minutes % 10)
        
        # Use decimal points as colon
        if colon:
            self.decimal_points[1] = True
        else:
            self.decimal_points[1] = False
    
    def clear(self):
        """Clear display"""
        self.buffer = [' ', ' ', ' ', ' ']
        self.decimal_points = [False, False, False, False]
    
    def _display_character(self, character, show_dp=False):
        """Display a single character on current digit"""
        if character in CHARACTERS:
            pattern = CHARACTERS[character]
            for segment, state in pattern.items():
                if segment != 'dp':
                    if state:
                        self.segments[segment].on()
                    else:
                        self.segments[segment].off()
            
            # Decimal point
            if show_dp or (character == '.' and 'dp' in pattern):
                self.segments['dp'].on()
            else:
                self.segments['dp'].off()
    
    def _multiplex_display(self):
        """Multiplex the display"""
        while self.running:
            for digit in range(4):
                # Turn off all digits
                for d in self.digits:
                    d.off()
                
                # Display character on current digit
                self._display_character(self.buffer[digit], 
                                      self.decimal_points[digit])
                
                # Turn on current digit
                self.digits[digit].on()
                
                # Control brightness with duty cycle
                time.sleep(0.001 * self.brightness)
                self.digits[digit].off()
                time.sleep(0.001 * (1 - self.brightness))
    
    def start(self):
        """Start display multiplexing"""
        if not self.running:
            self.running = True
            self.display_thread = threading.Thread(target=self._multiplex_display)
            self.display_thread.daemon = True
            self.display_thread.start()
    
    def stop(self):
        """Stop display"""
        self.running = False
        if self.display_thread:
            self.display_thread.join()
        
        # Turn off all segments and digits
        for segment in self.segments.values():
            segment.off()
        for digit in self.digits:
            digit.off()
    
    def set_brightness(self, brightness):
        """Set display brightness (0.0 to 1.0)"""
        self.brightness = max(0.1, min(1.0, brightness))
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop()
        for segment in self.segments.values():
            segment.close()
        for digit in self.digits:
            digit.close()

def basic_counter():
    """Basic counting demonstration"""
    print("\n=== Basic Counter ===")
    print("Counting from 0 to 9999")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    display.start()
    
    try:
        for i in range(10000):
            display.set_number(i, leading_zeros=True)
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def clock_display():
    """Digital clock display"""
    print("\n=== Digital Clock ===")
    print("Showing current time")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    display.start()
    
    colon_blink = True
    
    try:
        while True:
            now = datetime.now()
            display.set_time(now.hour, now.minute, colon_blink)
            
            # Blink colon every second
            colon_blink = not colon_blink
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def temperature_display():
    """Temperature display with decimal point"""
    print("\n=== Temperature Display ===")
    print("Simulating temperature readings")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    display.start()
    
    try:
        import random
        
        while True:
            # Simulate temperature 20.0 - 30.0
            temp = random.uniform(20.0, 30.0)
            
            # Format as XX.X
            temp_str = f"{temp:.1f}"
            
            # Display with decimal point
            display.buffer[0] = temp_str[0]
            display.buffer[1] = temp_str[1]
            display.buffer[2] = temp_str[3]  # Skip decimal point
            display.buffer[3] = 'C'  # Celsius
            display.decimal_points[1] = True  # Decimal after second digit
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def scrolling_text():
    """Scrolling text demonstration"""
    print("\n=== Scrolling Text ===")
    print("Displaying scrolling message")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    display.start()
    
    message = "    HELLO WORLD    RASPBERRY PI 5    "
    
    try:
        position = 0
        while True:
            # Get 4 characters from message
            visible = message[position:position+4]
            display.set_text(visible)
            
            # Move to next position
            position = (position + 1) % len(message)
            
            time.sleep(0.3)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def stopwatch():
    """Stopwatch with button control"""
    print("\n=== Stopwatch ===")
    print("Press button to start/stop")
    print("Hold button to reset")
    print("Press Ctrl+C to exit")
    
    display = FourDigitDisplay()
    display.start()
    
    # Optional button for control
    try:
        button = Button(26)  # GPIO26 for button
        has_button = True
    except:
        has_button = False
        print("Note: No button connected, using keyboard")
    
    running = False
    start_time = 0
    elapsed_time = 0
    
    def toggle_stopwatch():
        nonlocal running, start_time, elapsed_time
        if running:
            # Stop
            elapsed_time += time.time() - start_time
            running = False
        else:
            # Start
            start_time = time.time()
            running = True
    
    def reset_stopwatch():
        nonlocal running, elapsed_time
        running = False
        elapsed_time = 0
    
    if has_button:
        button.when_pressed = toggle_stopwatch
        button.when_held = reset_stopwatch
    
    try:
        while True:
            if running:
                current_time = elapsed_time + (time.time() - start_time)
            else:
                current_time = elapsed_time
            
            # Display as MM:SS or SS.HH (seconds.hundredths)
            if current_time < 60:
                # Show seconds and hundredths
                seconds = int(current_time)
                hundredths = int((current_time - seconds) * 100)
                display.buffer[0] = str(seconds // 10)
                display.buffer[1] = str(seconds % 10)
                display.buffer[2] = str(hundredths // 10)
                display.buffer[3] = str(hundredths % 10)
                display.decimal_points[1] = True
            else:
                # Show minutes and seconds
                minutes = int(current_time // 60)
                seconds = int(current_time % 60)
                display.set_time(minutes, seconds, True)
            
            # Manual control if no button
            if not has_button:
                import select
                if select.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)
                    if key == ' ':
                        toggle_stopwatch()
                    elif key == 'r':
                        reset_stopwatch()
            
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()
        if has_button:
            button.close()

def brightness_demo():
    """Demonstrate brightness control"""
    print("\n=== Brightness Control ===")
    print("Adjusting display brightness")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    display.start()
    display.set_text("8888")  # All segments on
    
    try:
        while True:
            # Fade up
            for i in range(10, 101, 5):
                display.set_brightness(i / 100)
                print(f"\rBrightness: {i}%", end='')
                time.sleep(0.1)
            
            # Fade down
            for i in range(100, 9, -5):
                display.set_brightness(i / 100)
                print(f"\rBrightness: {i}%", end='')
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def segment_test():
    """Test individual segments"""
    print("\n=== Segment Test ===")
    print("Testing each segment individually")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    
    try:
        # Turn on all digits
        for digit in display.digits:
            digit.on()
        
        segment_names = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'dp']
        
        while True:
            for seg_name in segment_names:
                # Turn off all segments
                for segment in display.segments.values():
                    segment.off()
                
                # Turn on current segment
                display.segments[seg_name].on()
                print(f"\rTesting segment: {seg_name}", end='')
                time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def countdown_timer():
    """Countdown timer"""
    print("\n=== Countdown Timer ===")
    
    try:
        seconds = int(input("Enter countdown time in seconds (max 9999): "))
        seconds = min(9999, max(0, seconds))
    except ValueError:
        seconds = 60
    
    print(f"Counting down from {seconds} seconds")
    print("Press Ctrl+C to stop")
    
    display = FourDigitDisplay()
    display.start()
    
    try:
        for i in range(seconds, -1, -1):
            if i >= 60:
                # Show as MM:SS
                minutes = i // 60
                secs = i % 60
                display.set_time(minutes, secs, True)
            else:
                # Show as seconds
                display.set_number(i, leading_zeros=False)
            
            # Flash when reaching zero
            if i == 0:
                for _ in range(10):
                    display.clear()
                    time.sleep(0.2)
                    display.set_text("0000")
                    time.sleep(0.2)
                break
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def dice_roller():
    """Electronic dice with 4 digits"""
    print("\n=== 4-Digit Dice Roller ===")
    print("Press Enter to roll 4 dice")
    print("Press Ctrl+C to exit")
    
    display = FourDigitDisplay()
    display.start()
    
    import random
    
    try:
        display.set_text("----")
        
        while True:
            input("\nPress Enter to roll...")
            
            # Animation
            for _ in range(20):
                for digit in range(4):
                    display.buffer[digit] = str(random.randint(1, 6))
                time.sleep(0.05)
            
            # Final result
            total = 0
            for digit in range(4):
                value = random.randint(1, 6)
                display.buffer[digit] = str(value)
                total += value
            
            print(f"Rolled: {display.buffer[0]} {display.buffer[1]} "
                  f"{display.buffer[2]} {display.buffer[3]} = {total}")
    
    except KeyboardInterrupt:
        pass
    finally:
        display.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("4-Digit 7-Segment Display Examples")
    print("==================================")
    print("Segment GPIOs:")
    for name, pin in SEGMENTS.items():
        print(f"  {name}: GPIO{pin}")
    print("\nDigit select GPIOs:", DIGITS)
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic counter (0-9999)")
        print("2. Digital clock")
        print("3. Temperature display")
        print("4. Scrolling text")
        print("5. Stopwatch")
        print("6. Brightness control")
        print("7. Segment test")
        print("8. Countdown timer")
        print("9. Dice roller")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '1':
            basic_counter()
        elif choice == '2':
            clock_display()
        elif choice == '3':
            temperature_display()
        elif choice == '4':
            scrolling_text()
        elif choice == '5':
            stopwatch()
        elif choice == '6':
            brightness_demo()
        elif choice == '7':
            segment_test()
        elif choice == '8':
            countdown_timer()
        elif choice == '9':
            dice_roller()
        elif choice == '0':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()