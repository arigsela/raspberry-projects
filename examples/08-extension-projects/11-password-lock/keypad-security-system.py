#!/usr/bin/env python3
"""
Keypad Security System

Advanced password lock system with matrix keypad, multiple security levels,
time-based codes, access logging, and anti-tampering protection.
"""

import time
import threading
import queue
import json
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from enum import Enum
from collections import deque
import re

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602

# Hardware Pin Definitions
# 4x4 Matrix Keypad
KEYPAD_ROW_PINS = [17, 27, 22, 23]  # Row 1-4
KEYPAD_COL_PINS = [24, 25, 8, 7]    # Column 1-4

# Security Indicators
LED_LOCKED_PIN = 5      # Red - System locked
LED_UNLOCKED_PIN = 6    # Green - System unlocked
LED_ALERT_PIN = 13      # Yellow - Alert/warning

# Access Control
LOCK_RELAY_PIN = 19     # Electronic lock control
ALARM_PIN = 26          # Alarm buzzer

# Additional Controls
RESET_BUTTON_PIN = 20   # Factory reset (hidden)
EMERGENCY_BUTTON_PIN = 21  # Emergency unlock

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Security Constants
MAX_ATTEMPTS = 3
LOCKOUT_TIME = 300  # 5 minutes
CODE_MIN_LENGTH = 4
CODE_MAX_LENGTH = 8
TEMP_CODE_DURATION = 300  # 5 minutes for temporary codes
SESSION_TIMEOUT = 30  # Auto-lock after 30 seconds

from gpiozero import LED, Button, Buzzer, OutputDevice

class SecurityLevel(Enum):
    """Security access levels"""
    USER = "User"
    ADMIN = "Admin"
    MASTER = "Master"
    TEMPORARY = "Temporary"
    EMERGENCY = "Emergency"

class AccessStatus(Enum):
    """Access attempt status"""
    GRANTED = "Granted"
    DENIED = "Denied"
    LOCKED = "Locked"
    TIMEOUT = "Timeout"
    EMERGENCY = "Emergency"

class MatrixKeypad:
    """4x4 Matrix keypad handler"""
    
    KEYS = [
        ['1', '2', '3', 'A'],
        ['4', '5', '6', 'B'],
        ['7', '8', '9', 'C'],
        ['*', '0', '#', 'D']
    ]
    
    def __init__(self, row_pins, col_pins):
        # Initialize row pins as outputs
        self.rows = [OutputDevice(pin) for pin in row_pins]
        # Initialize column pins as inputs with pull-up
        self.cols = [Button(pin, pull_up=True) for pin in col_pins]
        self.last_key = None
        self.key_pressed_time = 0
        
    def scan(self):
        """Scan keypad for pressed keys"""
        key = None
        
        # Scan each row
        for row_idx, row in enumerate(self.rows):
            # Set current row low
            row.off()
            
            # Check each column
            for col_idx, col in enumerate(self.cols):
                if not col.is_pressed:  # Active low
                    key = self.KEYS[row_idx][col_idx]
                    break
            
            # Set row back to high
            row.on()
            
            if key:
                break
        
        # Debounce
        if key:
            if key != self.last_key or time.time() - self.key_pressed_time > 0.3:
                self.last_key = key
                self.key_pressed_time = time.time()
                return key
        else:
            self.last_key = None
        
        return None
    
    def cleanup(self):
        """Clean up GPIO resources"""
        for row in self.rows:
            row.close()
        for col in self.cols:
            col.close()

class User:
    """User account with access credentials"""
    def __init__(self, name, code_hash, level=SecurityLevel.USER):
        self.name = name
        self.code_hash = code_hash
        self.level = level
        self.created = datetime.now()
        self.last_access = None
        self.access_count = 0
        self.failed_attempts = 0
        self.locked_until = None
        self.temp_code_hash = None
        self.temp_code_expires = None
    
    def verify_code(self, code):
        """Verify access code"""
        # Check if account is locked
        if self.locked_until and datetime.now() < self.locked_until:
            return False
        
        # Check temporary code first
        if self.temp_code_hash and self.temp_code_expires:
            if datetime.now() < self.temp_code_expires:
                if self._verify_hash(code, self.temp_code_hash):
                    # Temporary code used, clear it
                    self.temp_code_hash = None
                    self.temp_code_expires = None
                    return True
        
        # Check main code
        return self._verify_hash(code, self.code_hash)
    
    def _verify_hash(self, code, stored_hash):
        """Verify code against stored hash"""
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        return code_hash == stored_hash
    
    def update_access(self, success):
        """Update access statistics"""
        if success:
            self.last_access = datetime.now()
            self.access_count += 1
            self.failed_attempts = 0
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= MAX_ATTEMPTS:
                self.locked_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
    
    def set_temporary_code(self, code, duration=TEMP_CODE_DURATION):
        """Set a temporary access code"""
        self.temp_code_hash = hashlib.sha256(code.encode()).hexdigest()
        self.temp_code_expires = datetime.now() + timedelta(seconds=duration)
    
    def to_dict(self):
        """Convert to dictionary for saving"""
        return {
            'name': self.name,
            'code_hash': self.code_hash,
            'level': self.level.value,
            'created': self.created.isoformat(),
            'last_access': self.last_access.isoformat() if self.last_access else None,
            'access_count': self.access_count,
            'failed_attempts': self.failed_attempts,
            'locked_until': self.locked_until.isoformat() if self.locked_until else None
        }

class KeypadSecuritySystem:
    """Main security system controller"""
    
    def __init__(self):
        print("🔐 Initializing Keypad Security System...")
        
        # Initialize hardware
        self._init_keypad()
        self._init_indicators()
        self._init_access_control()
        self._init_display()
        
        # User management
        self.users = {}
        self.current_user = None
        self.system_locked = True
        
        # Security state
        self.input_buffer = ""
        self.last_activity = time.time()
        self.failed_attempts = 0
        self.lockout_until = None
        self.panic_mode = False
        
        # Access logging
        self.access_log = deque(maxlen=1000)
        self.event_queue = queue.Queue()
        
        # System settings
        self.auto_lock_enabled = True
        self.tamper_detection = True
        self.duress_code_enabled = True
        
        # Threading
        self.running = False
        self.keypad_thread = None
        self.monitor_thread = None
        
        # Load configuration and users
        self._load_configuration()
        self._setup_default_users()
        
        print("✅ Security system initialized")
    
    def _init_keypad(self):
        """Initialize matrix keypad"""
        self.keypad = MatrixKeypad(KEYPAD_ROW_PINS, KEYPAD_COL_PINS)
        print("✓ Keypad initialized")
    
    def _init_indicators(self):
        """Initialize LED indicators and buzzer"""
        self.led_locked = LED(LED_LOCKED_PIN)
        self.led_unlocked = LED(LED_UNLOCKED_PIN)
        self.led_alert = LED(LED_ALERT_PIN)
        self.buzzer = Buzzer(ALARM_PIN)
        
        # Set initial state
        self.led_locked.on()
        self.led_unlocked.off()
        self.led_alert.off()
        
        print("✓ Indicators initialized")
    
    def _init_access_control(self):
        """Initialize access control hardware"""
        self.lock_relay = OutputDevice(LOCK_RELAY_PIN)
        self.reset_button = Button(RESET_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.emergency_button = Button(EMERGENCY_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.reset_button.when_held = self._factory_reset
        self.emergency_button.when_pressed = self._emergency_unlock
        
        # Ensure locked state
        self.lock_relay.off()
        
        print("✓ Access control initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Security System")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load system configuration"""
        config_file = "security_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                    # Load users
                    if 'users' in config:
                        for user_data in config['users']:
                            user = User(
                                user_data['name'],
                                user_data['code_hash'],
                                SecurityLevel(user_data['level'])
                            )
                            # Restore user data
                            if user_data['last_access']:
                                user.last_access = datetime.fromisoformat(user_data['last_access'])
                            user.access_count = user_data.get('access_count', 0)
                            self.users[user.name] = user
                    
                    # Load settings
                    if 'settings' in config:
                        self.auto_lock_enabled = config['settings'].get('auto_lock', True)
                        self.tamper_detection = config['settings'].get('tamper_detection', True)
                    
                    print("✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def _save_configuration(self):
        """Save system configuration"""
        config_file = "security_config.json"
        try:
            config = {
                'users': [user.to_dict() for user in self.users.values()],
                'settings': {
                    'auto_lock': self.auto_lock_enabled,
                    'tamper_detection': self.tamper_detection
                },
                'last_saved': datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
    
    def _setup_default_users(self):
        """Set up default users if none exist"""
        if not self.users:
            # Create default master user
            master_code = "1234"  # Change this!
            master_hash = hashlib.sha256(master_code.encode()).hexdigest()
            
            self.users['master'] = User('master', master_hash, SecurityLevel.MASTER)
            
            # Create default admin
            admin_code = "9876"
            admin_hash = hashlib.sha256(admin_code.encode()).hexdigest()
            self.users['admin'] = User('admin', admin_hash, SecurityLevel.ADMIN)
            
            print("⚠ Default users created - CHANGE PASSWORDS!")
            self._save_configuration()
    
    def run(self):
        """Main system loop"""
        print("\n🔐 Keypad Security System Active!")
        print("Enter access code on keypad")
        print("* = Clear, # = Enter")
        print("Press Ctrl+C to exit\n")
        
        self.running = True
        
        # Start keypad scanning thread
        self.keypad_thread = threading.Thread(target=self._keypad_scan_loop, daemon=True)
        self.keypad_thread.start()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        # Update display
        self._update_display("LOCKED", "Enter Code")
        
        try:
            while True:
                # Process events
                self._process_event_queue()
                
                # Check for auto-lock
                if not self.system_locked and self.auto_lock_enabled:
                    if time.time() - self.last_activity > SESSION_TIMEOUT:
                        self._lock_system("Timeout")
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down security system...")
            self.running = False
            self._lock_system("Shutdown")
            time.sleep(1)
    
    def _keypad_scan_loop(self):
        """Continuous keypad scanning"""
        while self.running:
            try:
                key = self.keypad.scan()
                
                if key:
                    self.last_activity = time.time()
                    self._handle_keypress(key)
                    
                time.sleep(0.05)  # 50ms scan rate
                
            except Exception as e:
                print(f"⚠ Keypad error: {e}")
                time.sleep(1)
    
    def _handle_keypress(self, key):
        """Handle keypad input"""
        # Check if system is in lockout
        if self.lockout_until and datetime.now() < self.lockout_until:
            remaining = (self.lockout_until - datetime.now()).seconds
            self._update_display("LOCKOUT", f"Wait {remaining}s")
            return
        
        # Provide feedback
        self.buzzer.beep(0.05, 0, n=1)
        
        if key == '*':
            # Clear input
            self.input_buffer = ""
            self._update_display("LOCKED" if self.system_locked else "UNLOCKED", "Cleared")
            
        elif key == '#':
            # Submit code
            if len(self.input_buffer) >= CODE_MIN_LENGTH:
                self._process_code(self.input_buffer)
            else:
                self._update_display("ERROR", "Too Short")
            self.input_buffer = ""
            
        elif key in 'ABCD':
            # Function keys
            self._handle_function_key(key)
            
        else:
            # Numeric input
            if len(self.input_buffer) < CODE_MAX_LENGTH:
                self.input_buffer += key
                # Show masked input
                masked = '*' * len(self.input_buffer)
                self._update_display("ENTER CODE", masked)
    
    def _process_code(self, code):
        """Process entered access code"""
        print(f"📝 Code entered: {'*' * len(code)}")
        
        # Check for duress code
        if self.duress_code_enabled and code.endswith('99'):
            self._trigger_duress_alarm()
            return
        
        # Verify code against all users
        user_found = None
        for user in self.users.values():
            if user.verify_code(code):
                user_found = user
                break
        
        if user_found:
            # Access granted
            user_found.update_access(True)
            self.current_user = user_found
            self.failed_attempts = 0
            
            self._log_access(user_found.name, AccessStatus.GRANTED)
            
            if self.system_locked:
                self._unlock_system()
            else:
                # Already unlocked - show menu
                self._show_user_menu()
        else:
            # Access denied
            self.failed_attempts += 1
            self._log_access("Unknown", AccessStatus.DENIED)
            
            if self.failed_attempts >= MAX_ATTEMPTS:
                self.lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
                self._update_display("LOCKOUT", f"{LOCKOUT_TIME}s")
                print(f"🔒 System locked out for {LOCKOUT_TIME} seconds")
            else:
                remaining = MAX_ATTEMPTS - self.failed_attempts
                self._update_display("DENIED", f"{remaining} tries")
                self.buzzer.beep(0.2, 0.2, n=2)
    
    def _unlock_system(self):
        """Unlock the system"""
        self.system_locked = False
        self.lock_relay.on()  # Energize lock
        self.led_locked.off()
        self.led_unlocked.on()
        
        self._update_display("UNLOCKED", f"Hi {self.current_user.name}")
        print(f"🔓 System unlocked by {self.current_user.name}")
        
        # Success beep
        self.buzzer.beep(0.1, 0.1, n=3)
    
    def _lock_system(self, reason="Manual"):
        """Lock the system"""
        self.system_locked = True
        self.lock_relay.off()  # De-energize lock
        self.led_locked.on()
        self.led_unlocked.off()
        self.current_user = None
        
        self._update_display("LOCKED", reason)
        self._log_access("System", AccessStatus.LOCKED)
        print(f"🔒 System locked: {reason}")
    
    def _handle_function_key(self, key):
        """Handle function keys A-D"""
        if not self.current_user:
            self._update_display("ERROR", "Login First")
            return
        
        if key == 'A':
            # Add user (admin only)
            if self.current_user.level in [SecurityLevel.ADMIN, SecurityLevel.MASTER]:
                self._add_user_mode()
            else:
                self._update_display("DENIED", "No Permission")
        
        elif key == 'B':
            # Change password
            self._change_password_mode()
        
        elif key == 'C':
            # Create temporary code (admin only)
            if self.current_user.level in [SecurityLevel.ADMIN, SecurityLevel.MASTER]:
                self._create_temp_code()
            else:
                self._update_display("DENIED", "No Permission")
        
        elif key == 'D':
            # Lock system
            self._lock_system("User Lock")
    
    def _show_user_menu(self):
        """Show user menu options"""
        self._update_display(f"{self.current_user.level.value} Menu", "A B C D")
        time.sleep(2)
        
        if self.current_user.level in [SecurityLevel.ADMIN, SecurityLevel.MASTER]:
            self._update_display("A:User B:Pass", "C:Temp D:Lock")
        else:
            self._update_display("B:Change Pass", "D:Lock System")
    
    def _add_user_mode(self):
        """Add new user (simplified for demo)"""
        # Generate random username
        username = f"user{secrets.randbelow(1000):03d}"
        
        # Generate random 6-digit code
        temp_code = f"{secrets.randbelow(1000000):06d}"
        code_hash = hashlib.sha256(temp_code.encode()).hexdigest()
        
        # Create new user
        new_user = User(username, code_hash, SecurityLevel.USER)
        self.users[username] = new_user
        
        self._save_configuration()
        
        print(f"👤 New user created: {username}")
        self._update_display(f"User: {username}", f"Code: {temp_code}")
        time.sleep(5)  # Show code briefly
        
        self._log_access(self.current_user.name, AccessStatus.GRANTED, f"Created user {username}")
    
    def _change_password_mode(self):
        """Change password mode"""
        self._update_display("Enter NEW code", "Then press #")
        self.input_buffer = ""
        
        # Wait for new code
        new_code = self._wait_for_code_input()
        
        if new_code and len(new_code) >= CODE_MIN_LENGTH:
            # Update password
            new_hash = hashlib.sha256(new_code.encode()).hexdigest()
            self.current_user.code_hash = new_hash
            self._save_configuration()
            
            self._update_display("SUCCESS", "Code Changed")
            print(f"🔑 Password changed for {self.current_user.name}")
            self._log_access(self.current_user.name, AccessStatus.GRANTED, "Password changed")
        else:
            self._update_display("ERROR", "Invalid Code")
    
    def _create_temp_code(self):
        """Create temporary access code"""
        # Generate 6-digit temporary code
        temp_code = f"{secrets.randbelow(1000000):06d}"
        
        # Create temporary user
        temp_user = User("temp_user", "", SecurityLevel.TEMPORARY)
        temp_user.set_temporary_code(temp_code)
        
        # Add to users
        self.users['temp_user'] = temp_user
        
        print(f"🎫 Temporary code created: {temp_code}")
        self._update_display("Temp Code:", temp_code)
        time.sleep(5)  # Show code briefly
        
        self._log_access(self.current_user.name, AccessStatus.GRANTED, "Created temp code")
    
    def _wait_for_code_input(self, timeout=30):
        """Wait for code input with timeout"""
        start_time = time.time()
        self.input_buffer = ""
        
        while time.time() - start_time < timeout:
            if '#' in self.input_buffer:
                # Code submitted
                code = self.input_buffer.replace('#', '')
                self.input_buffer = ""
                return code
            
            time.sleep(0.1)
        
        return None
    
    def _emergency_unlock(self):
        """Emergency unlock procedure"""
        print("🚨 EMERGENCY UNLOCK ACTIVATED")
        
        # Unlock immediately
        self.system_locked = False
        self.lock_relay.on()
        self.led_locked.off()
        self.led_unlocked.on()
        self.led_alert.blink(on_time=0.2, off_time=0.2)
        
        # Sound alarm
        self.buzzer.beep(0.5, 0.5, n=5)
        
        self._update_display("EMERGENCY", "UNLOCK")
        self._log_access("Emergency", AccessStatus.EMERGENCY)
        
        # Auto-relock after 60 seconds
        threading.Timer(60, self._lock_system, args=["Emergency Reset"]).start()
    
    def _trigger_duress_alarm(self):
        """Trigger silent duress alarm"""
        print("🚨 DURESS ALARM TRIGGERED")
        self.panic_mode = True
        
        # Unlock system (appear normal)
        self._unlock_system()
        
        # Silent alarm - flash alert LED
        self.led_alert.blink(on_time=0.1, off_time=0.9)
        
        # Log duress event
        self._log_access("DURESS", AccessStatus.GRANTED, "DURESS CODE USED")
        
        # In real system: notify authorities
    
    def _factory_reset(self):
        """Factory reset (hold reset button 10 seconds)"""
        print("⚠️  FACTORY RESET INITIATED")
        
        # Clear all users
        self.users.clear()
        
        # Reset to defaults
        self._setup_default_users()
        
        # Clear logs
        self.access_log.clear()
        
        # Lock system
        self._lock_system("Factory Reset")
        
        self._update_display("RESET", "Complete")
        print("✅ Factory reset complete")
    
    def _monitor_loop(self):
        """Background monitoring thread"""
        while self.running:
            try:
                # Check for expired temporary codes
                expired_users = []
                for username, user in self.users.items():
                    if user.level == SecurityLevel.TEMPORARY:
                        if user.temp_code_expires and datetime.now() > user.temp_code_expires:
                            expired_users.append(username)
                
                # Remove expired users
                for username in expired_users:
                    del self.users[username]
                    print(f"🗑️  Temporary user {username} expired")
                
                # Save logs periodically
                if len(self.access_log) > 0 and len(self.access_log) % 10 == 0:
                    self._save_access_log()
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠ Monitor error: {e}")
    
    def _log_access(self, user, status, details=""):
        """Log access attempt"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'status': status.value,
            'details': details
        }
        
        self.access_log.append(log_entry)
        self.event_queue.put(log_entry)
        
        # Print to console
        print(f"📋 Access: {user} - {status.value} {details}")
    
    def _save_access_log(self):
        """Save access log to file"""
        try:
            log_file = f"access_log_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(log_file, 'a') as f:
                for entry in list(self.access_log):
                    json.dump(entry, f)
                    f.write('\n')
            
            self.access_log.clear()
            
        except Exception as e:
            print(f"⚠ Could not save log: {e}")
    
    def _update_display(self, line1, line2):
        """Update LCD display"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, line1[:16])
            self.lcd.write(1, 0, line2[:16])
        except Exception as e:
            print(f"⚠ Display error: {e}")
    
    def _process_event_queue(self):
        """Process queued events"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                
                # Could send to remote monitoring, trigger alerts, etc.
                
        except queue.Empty:
            pass
    
    def get_statistics(self):
        """Get system statistics"""
        total_users = len(self.users)
        admin_users = sum(1 for u in self.users.values() 
                         if u.level in [SecurityLevel.ADMIN, SecurityLevel.MASTER])
        
        # Count access attempts from log
        granted = sum(1 for log in self.access_log if log['status'] == 'Granted')
        denied = sum(1 for log in self.access_log if log['status'] == 'Denied')
        
        return {
            'total_users': total_users,
            'admin_users': admin_users,
            'access_granted': granted,
            'access_denied': denied,
            'current_user': self.current_user.name if self.current_user else None,
            'system_locked': self.system_locked
        }
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop operation
        self.running = False
        
        # Lock system
        self._lock_system("Shutdown")
        
        # Save configuration and logs
        self._save_configuration()
        self._save_access_log()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
        
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Total users: {stats['total_users']}")
        print(f"  Admin users: {stats['admin_users']}")
        print(f"  Access granted: {stats['access_granted']}")
        print(f"  Access denied: {stats['access_denied']}")
        
        # Clean up hardware
        self.keypad.cleanup()
        self.led_locked.close()
        self.led_unlocked.close()
        self.led_alert.close()
        self.buzzer.close()
        self.lock_relay.close()
        self.reset_button.close()
        self.emergency_button.close()
        
        print("\n✅ Cleanup complete")


def security_demo():
    """Demonstrate security system features"""
    print("\n🎮 Security System Demo")
    print("=" * 50)
    
    system = KeypadSecuritySystem()
    
    try:
        print("\nDemonstrating security features...")
        
        # Demo 1: Access denied
        print("\n1. Access Denied")
        system._update_display("DEMO", "Wrong Code")
        system.buzzer.beep(0.2, 0.2, n=2)
        system.led_alert.on()
        time.sleep(2)
        system.led_alert.off()
        
        # Demo 2: Access granted
        print("\n2. Access Granted")
        system._update_display("DEMO", "Correct Code")
        system.buzzer.beep(0.1, 0.1, n=3)
        system.led_locked.off()
        system.led_unlocked.on()
        time.sleep(2)
        
        # Demo 3: Lockout
        print("\n3. Lockout Mode")
        system._update_display("LOCKOUT", "300s")
        system.led_alert.blink(on_time=0.5, off_time=0.5)
        time.sleep(3)
        system.led_alert.off()
        
        # Demo 4: Emergency
        print("\n4. Emergency Unlock")
        system._update_display("EMERGENCY", "UNLOCK")
        system.buzzer.beep(0.5, 0.5, n=3)
        system.led_alert.blink(on_time=0.2, off_time=0.2)
        system.led_unlocked.on()
        time.sleep(3)
        
        # Reset
        system.led_locked.on()
        system.led_unlocked.off()
        system.led_alert.off()
        
        print("\n✅ Demo complete!")
        
    finally:
        system.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        security_demo()
    else:
        # Normal operation
        system = KeypadSecuritySystem()
        try:
            system.run()
        finally:
            system.cleanup()
