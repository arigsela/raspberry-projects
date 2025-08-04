#!/usr/bin/env python3
"""
Keypad Door Lock System
Security keypad with codes, timeouts, and lockout
"""

from gpiozero import OutputDevice, InputDevice, LED, Buzzer
import time
import signal
import sys
import json
import hashlib
from datetime import datetime

# GPIO Configuration
ROW_PINS = [18, 23, 24, 25]
COL_PINS = [10, 22, 27, 17]

# Output devices
GREEN_LED = 5     # Access granted
RED_LED = 6       # Access denied
BUZZER_PIN = 13   # Feedback buzzer
LOCK_PIN = 19     # Door lock relay/solenoid

# Keypad layout
KEYS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Security configuration
ACCESS_CODE_FILE = "access_codes.json"
LOG_FILE = "access_log.txt"
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 30  # seconds
DOOR_OPEN_TIME = 5  # seconds

class KeypadLock:
    """Keypad-based door lock system"""
    
    def __init__(self):
        """Initialize lock system components"""
        # Keypad setup
        self.rows = [OutputDevice(pin) for pin in ROW_PINS]
        self.cols = [InputDevice(pin, pull_up=True) for pin in COL_PINS]
        
        # Output devices
        self.green_led = LED(GREEN_LED)
        self.red_led = LED(RED_LED)
        self.buzzer = Buzzer(BUZZER_PIN)
        self.lock = OutputDevice(LOCK_PIN, initial_value=False)
        
        # Security state
        self.failed_attempts = 0
        self.lockout_until = 0
        self.last_key = None
        self.current_code = ""
        
        # Load access codes
        self.load_codes()
        
        # Start with locked state
        self.lock_door()
    
    def load_codes(self):
        """Load access codes from file"""
        try:
            with open(ACCESS_CODE_FILE, 'r') as f:
                data = json.load(f)
                self.access_codes = data.get('codes', {})
                self.master_code = data.get('master', '999999')
        except FileNotFoundError:
            # Default codes if file doesn't exist
            self.access_codes = {
                '1234': 'User 1',
                '5678': 'User 2',
                '0000': 'Guest'
            }
            self.master_code = '999999'
            self.save_codes()
    
    def save_codes(self):
        """Save access codes to file"""
        data = {
            'codes': self.access_codes,
            'master': self.master_code
        }
        with open(ACCESS_CODE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def hash_code(self, code):
        """Hash access code for storage"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def log_access(self, event, user=None):
        """Log access attempts"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {event}"
        if user:
            log_entry += f" - {user}"
        log_entry += "\n"
        
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def scan_key(self):
        """Scan keypad for pressed key"""
        for row_num, row_pin in enumerate(self.rows):
            row_pin.on()
            time.sleep(0.001)
            
            for col_num, col_pin in enumerate(self.cols):
                if not col_pin.is_active:
                    row_pin.off()
                    return KEYS[row_num][col_num]
            
            row_pin.off()
        
        return None
    
    def get_key(self):
        """Get key press with debouncing"""
        key = self.scan_key()
        
        if key and not self.last_key:
            self.last_key = key
            self.beep_feedback()
            return key
        elif not key and self.last_key:
            self.last_key = None
        
        return None
    
    def beep_feedback(self, duration=0.05):
        """Provide audio feedback for key press"""
        self.buzzer.beep(on_time=duration, off_time=0, n=1)
    
    def beep_error(self):
        """Error beep pattern"""
        for _ in range(3):
            self.buzzer.beep(on_time=0.1, off_time=0.1, n=1)
    
    def beep_success(self):
        """Success beep pattern"""
        self.buzzer.beep(on_time=0.5, off_time=0, n=1)
    
    def lock_door(self):
        """Lock the door"""
        self.lock.off()
        self.green_led.off()
        self.red_led.on()
    
    def unlock_door(self, duration=DOOR_OPEN_TIME):
        """Unlock door for specified duration"""
        self.lock.on()
        self.green_led.on()
        self.red_led.off()
        self.beep_success()
        
        # Keep door open for duration
        time.sleep(duration)
        
        # Re-lock door
        self.lock_door()
        self.log_access("Door locked")
    
    def check_lockout(self):
        """Check if system is in lockout"""
        if time.time() < self.lockout_until:
            remaining = int(self.lockout_until - time.time())
            return True, remaining
        return False, 0
    
    def enter_lockout(self):
        """Enter lockout mode"""
        self.lockout_until = time.time() + LOCKOUT_TIME
        self.log_access(f"LOCKOUT - {LOCKOUT_TIME} seconds")
        self.red_led.blink(on_time=0.5, off_time=0.5)
    
    def verify_code(self, code):
        """Verify entered code"""
        # Check master code
        if code == self.master_code:
            return True, "Master"
        
        # Check user codes
        if code in self.access_codes:
            return True, self.access_codes[code]
        
        return False, None
    
    def handle_code_entry(self):
        """Handle code entry process"""
        print("\nEnter access code (* to clear, # to submit):")
        self.current_code = ""
        
        while True:
            # Check lockout
            locked, remaining = self.check_lockout()
            if locked:
                print(f"\rLOCKED - Wait {remaining}s", end='', flush=True)
                time.sleep(1)
                continue
            else:
                self.red_led.on()  # Stop blinking after lockout
            
            key = self.get_key()
            
            if key:
                if key == '#':
                    # Submit code
                    if len(self.current_code) >= 4:
                        valid, user = self.verify_code(self.current_code)
                        
                        if valid:
                            # Access granted
                            self.log_access("ACCESS GRANTED", user)
                            print(f"\n✓ Access granted - {user}")
                            self.failed_attempts = 0
                            self.unlock_door()
                            return True
                        else:
                            # Access denied
                            self.failed_attempts += 1
                            self.log_access(f"ACCESS DENIED - Attempt {self.failed_attempts}")
                            print(f"\n✗ Access denied - Attempt {self.failed_attempts}/{MAX_ATTEMPTS}")
                            self.beep_error()
                            
                            if self.failed_attempts >= MAX_ATTEMPTS:
                                self.enter_lockout()
                            
                            return False
                    else:
                        print("\nCode too short!")
                        self.beep_error()
                
                elif key == '*':
                    # Clear code
                    self.current_code = ""
                    print("\nCode cleared")
                
                elif key in '0123456789':
                    # Add digit
                    if len(self.current_code) < 8:  # Max 8 digits
                        self.current_code += key
                        print("*", end='', flush=True)
                
                elif key == 'D':
                    # Cancel and return
                    print("\nCancelled")
                    return False
            
            time.sleep(0.05)
    
    def admin_menu(self):
        """Administrator menu for managing codes"""
        print("\n=== Admin Menu ===")
        print("A - Add user code")
        print("B - Remove user code")
        print("C - List users")
        print("D - Exit admin")
        
        while True:
            key = self.get_key()
            
            if key == 'A':
                self.add_user_code()
                break
            elif key == 'B':
                self.remove_user_code()
                break
            elif key == 'C':
                self.list_users()
                break
            elif key == 'D':
                print("Exiting admin menu")
                break
            
            time.sleep(0.05)
    
    def add_user_code(self):
        """Add new user code"""
        print("\nEnter new code (# to submit):")
        new_code = ""
        
        while True:
            key = self.get_key()
            
            if key == '#' and len(new_code) >= 4:
                print("\nEnter user name:")
                # For demo, use keypad to enter numeric ID
                user_name = f"User {len(self.access_codes) + 1}"
                self.access_codes[new_code] = user_name
                self.save_codes()
                print(f"Added: {user_name}")
                self.log_access(f"Code added for {user_name}")
                break
            elif key in '0123456789':
                new_code += key
                print("*", end='', flush=True)
            
            time.sleep(0.05)
    
    def list_users(self):
        """List all users"""
        print("\n=== User List ===")
        for i, (code, user) in enumerate(self.access_codes.items()):
            print(f"{i+1}. {user} - {'*' * len(code)}")
        print(f"Total users: {len(self.access_codes)}")
        time.sleep(3)
    
    def run(self):
        """Main lock system loop"""
        print("Keypad Lock System Active")
        print("========================")
        self.log_access("System started")
        
        try:
            while True:
                # Show ready state
                print("\nPress any key to begin...")
                
                # Wait for first key press
                while not self.get_key():
                    time.sleep(0.05)
                
                # Handle code entry
                success = self.handle_code_entry()
                
                # Check for admin access
                if success and self.current_code == self.master_code:
                    self.admin_menu()
                
                # Reset for next entry
                self.current_code = ""
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.log_access("System shutdown")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.lock_door()
        for row in self.rows:
            row.close()
        for col in self.cols:
            col.close()
        self.green_led.close()
        self.red_led.close()
        self.buzzer.close()
        self.lock.close()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def main():
    """Main program"""
    signal.signal(signal.SIGINT, signal_handler)
    
    lock_system = KeypadLock()
    
    try:
        lock_system.run()
    finally:
        lock_system.cleanup()

if __name__ == "__main__":
    main()