#!/usr/bin/env python3
"""
4x4 Matrix Keypad Scanner
Demonstrates matrix keypad scanning techniques
"""

from gpiozero import OutputDevice, InputDevice
import time
import signal
import sys

# GPIO Configuration for 4x4 Keypad
# Rows are outputs (scan lines)
ROW_PINS = [18, 23, 24, 25]  # GPIO pins for rows
# Columns are inputs (read lines)
COL_PINS = [10, 22, 27, 17]  # GPIO pins for columns

# Keypad layout (4x4 matrix)
KEYS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

class Keypad:
    """4x4 Matrix Keypad Interface"""
    
    def __init__(self, row_pins, col_pins, keys):
        """Initialize keypad with GPIO pins and key layout"""
        self.keys = keys
        self.rows = [OutputDevice(pin) for pin in row_pins]
        self.cols = [InputDevice(pin, pull_up=True) for pin in col_pins]
        self.last_key = None
        self.key_down_time = None
        
    def scan(self):
        """
        Scan keypad matrix for pressed keys
        
        Returns:
            Pressed key character or None
        """
        key_pressed = None
        
        # Scan each row
        for row_num, row_pin in enumerate(self.rows):
            # Set current row LOW (active)
            row_pin.on()  # Note: on() sets the pin LOW for OutputDevice
            
            # Small delay for signal to settle
            time.sleep(0.001)
            
            # Check each column
            for col_num, col_pin in enumerate(self.cols):
                # If column is LOW, key is pressed
                if not col_pin.is_active:
                    key_pressed = self.keys[row_num][col_num]
            
            # Set row back to HIGH (inactive)
            row_pin.off()
        
        return key_pressed
    
    def get_key(self):
        """
        Get single key press with debouncing
        
        Returns:
            Key character on press, None otherwise
        """
        key = self.scan()
        
        # Detect key press (transition from None to key)
        if key and not self.last_key:
            self.last_key = key
            self.key_down_time = time.time()
            return key
        
        # Detect key release
        elif not key and self.last_key:
            self.last_key = None
            self.key_down_time = None
        
        return None
    
    def get_key_with_hold(self, hold_time=1.0):
        """
        Get key press with hold detection
        
        Args:
            hold_time: Time in seconds to detect hold
            
        Returns:
            Tuple of (key, is_held)
        """
        key = self.scan()
        
        if key and not self.last_key:
            # New key press
            self.last_key = key
            self.key_down_time = time.time()
            return (key, False)
        
        elif key and self.last_key == key and self.key_down_time:
            # Key being held
            if time.time() - self.key_down_time > hold_time:
                return (key, True)
        
        elif not key and self.last_key:
            # Key released
            self.last_key = None
            self.key_down_time = None
        
        return (None, False)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        for row in self.rows:
            row.close()
        for col in self.cols:
            col.close()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_scanner_demo(keypad):
    """Basic keypad scanning demonstration"""
    print("\n=== Basic Keypad Scanner ===")
    print("Press keys on the keypad")
    print("Press Ctrl+C to return to menu\n")
    
    try:
        while True:
            key = keypad.get_key()
            if key:
                print(f"Key pressed: {key}")
            time.sleep(0.05)  # Small delay to reduce CPU usage
    
    except KeyboardInterrupt:
        print("\nReturning to menu...")

def password_entry_demo(keypad):
    """Password entry demonstration"""
    print("\n=== Password Entry Demo ===")
    print("Enter 4-digit password (use # to submit, * to clear)")
    print("Correct password: 1234")
    
    password = ""
    correct_password = "1234"
    
    try:
        while True:
            key = keypad.get_key()
            
            if key:
                if key == '#':
                    # Submit password
                    if password == correct_password:
                        print(f"\n✓ Correct! Password was: {password}")
                        break
                    else:
                        print(f"\n✗ Incorrect! You entered: {password}")
                        password = ""
                        print("Try again:")
                
                elif key == '*':
                    # Clear password
                    password = ""
                    print("\nPassword cleared. Enter password:")
                
                elif len(password) < 4:
                    # Add digit to password
                    password += key
                    print("*", end='', flush=True)
                    
                    # Auto-submit at 4 digits
                    if len(password) == 4:
                        time.sleep(0.5)
                        if password == correct_password:
                            print(f"\n✓ Correct! Password was: {password}")
                            break
                        else:
                            print(f"\n✗ Incorrect! You entered: {password}")
                            password = ""
                            print("Try again:")
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\nReturning to menu...")

def calculator_demo(keypad):
    """Simple calculator demonstration"""
    print("\n=== Calculator Demo ===")
    print("Enter calculations (use A=+, B=-, C=×, D=÷)")
    print("Use # to calculate, * to clear")
    
    display = ""
    
    try:
        while True:
            key = keypad.get_key()
            
            if key:
                if key == '#':
                    # Calculate result
                    if display:
                        # Replace operation symbols
                        calc_str = display.replace('A', '+').replace('B', '-')
                        calc_str = calc_str.replace('C', '*').replace('D', '/')
                        
                        try:
                            result = eval(calc_str)
                            print(f"\n{display} = {result}")
                            display = str(result)
                        except:
                            print("\nError in calculation!")
                            display = ""
                
                elif key == '*':
                    # Clear
                    display = ""
                    print("\nCleared")
                
                else:
                    # Add to display
                    display += key
                    print(f"\r{display}", end='', flush=True)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\nReturning to menu...")

def hold_detection_demo(keypad):
    """Demonstrate key hold detection"""
    print("\n=== Hold Detection Demo ===")
    print("Press and hold keys to see hold detection")
    print("Hold for 1 second to trigger")
    
    try:
        while True:
            key, is_held = keypad.get_key_with_hold(hold_time=1.0)
            
            if key and not is_held:
                print(f"Key pressed: {key}")
            elif key and is_held:
                print(f"Key HELD: {key} (special action!)")
                # Wait for release
                while keypad.scan() == key:
                    time.sleep(0.05)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\nReturning to menu...")

def phone_dialer_demo(keypad):
    """Phone dialer interface demonstration"""
    print("\n=== Phone Dialer Demo ===")
    print("Enter phone number (* = backspace, # = dial)")
    
    phone_number = ""
    
    try:
        while True:
            key = keypad.get_key()
            
            if key:
                if key == '#':
                    # Dial number
                    if phone_number:
                        print(f"\n📞 Dialing: {phone_number}")
                        time.sleep(2)
                        print("Call ended")
                        phone_number = ""
                
                elif key == '*':
                    # Backspace
                    if phone_number:
                        phone_number = phone_number[:-1]
                        print(f"\r{phone_number}          ", end='', flush=True)
                
                elif key in '0123456789':
                    # Add digit
                    phone_number += key
                    # Format display
                    if len(phone_number) <= 3:
                        display = phone_number
                    elif len(phone_number) <= 6:
                        display = f"{phone_number[:3]}-{phone_number[3:]}"
                    else:
                        display = f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"
                    
                    print(f"\r{display}", end='', flush=True)
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\nReturning to menu...")

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("4x4 Matrix Keypad Demo")
    print("======================")
    print("Keypad Layout:")
    print("┌───┬───┬───┬───┐")
    print("│ 1 │ 2 │ 3 │ A │")
    print("├───┼───┼───┼───┤")
    print("│ 4 │ 5 │ 6 │ B │")
    print("├───┼───┼───┼───┤")
    print("│ 7 │ 8 │ 9 │ C │")
    print("├───┼───┼───┼───┤")
    print("│ * │ 0 │ # │ D │")
    print("└───┴───┴───┴───┘")
    
    # Initialize keypad
    keypad = Keypad(ROW_PINS, COL_PINS, KEYS)
    
    try:
        while True:
            print("\n\nSelect Demo:")
            print("1. Basic Scanner")
            print("2. Password Entry")
            print("3. Calculator")
            print("4. Hold Detection")
            print("5. Phone Dialer")
            print("6. Exit")
            
            # Wait for menu selection
            choice = None
            while choice not in ['1', '2', '3', '4', '5', '6']:
                key = keypad.get_key()
                if key in ['1', '2', '3', '4', '5', '6']:
                    choice = key
                    print(f"Selected: {choice}")
                time.sleep(0.05)
            
            if choice == '1':
                basic_scanner_demo(keypad)
            elif choice == '2':
                password_entry_demo(keypad)
            elif choice == '3':
                calculator_demo(keypad)
            elif choice == '4':
                hold_detection_demo(keypad)
            elif choice == '5':
                phone_dialer_demo(keypad)
            elif choice == '6':
                break
    
    finally:
        keypad.cleanup()
        print("Cleanup complete")

if __name__ == "__main__":
    main()