#!/usr/bin/env python3
"""
RFID Welcome System
Personalized greeting system using RFID cards with voice synthesis and display
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

from lcd1602 import LCD1602
import time
import signal
import threading
import json
from datetime import datetime, timedelta
import spidev
import subprocess

from gpiozero import LED, PWMLED, Buzzer, Button

# MFRC522 RFID Reader Configuration
RST_PIN = 22         # Reset pin
SDA_PIN = 8          # SPI CE0 (Chip Enable)
SCK_PIN = 11         # SPI Clock
MOSI_PIN = 10        # SPI MOSI
MISO_PIN = 9         # SPI MISO

# LCD Display (I2C)
LCD_I2C_ADDRESS = 0x27

# Status indicators
SCAN_LED_PIN = 17        # Scanning indicator
SUCCESS_LED_PIN = 18     # Successful scan
ERROR_LED_PIN = 27       # Error/unknown card
GREETING_LED_PIN = 23    # Greeting active

# Audio feedback
WELCOME_BUZZER_PIN = 24  # Welcome sound
ALERT_BUZZER_PIN = 25    # Alert/error sound

# Control buttons
REGISTER_BUTTON_PIN = 26 # Register new user
MODE_BUTTON_PIN = 19     # Change greeting mode
MUTE_BUTTON_PIN = 20     # Mute audio

# MFRC522 Commands
MFRC522_IDLE = 0x00
MFRC522_MEM = 0x01
MFRC522_GENID = 0x02
MFRC522_CALCCRC = 0x03
MFRC522_TRANSMIT = 0x04
MFRC522_NOCMDCH = 0x07
MFRC522_RECEIVE = 0x08
MFRC522_TRANSCEIVE = 0x0C
MFRC522_AUTHENT = 0x0E
MFRC522_SOFTRESET = 0x0F

# MFRC522 Registers
CommandReg = 0x01
ComIEnReg = 0x02
ComIrqReg = 0x04
DivIrqReg = 0x05
ErrorReg = 0x06
Status2Reg = 0x08
FIFODataReg = 0x09
FIFOLevelReg = 0x0A
ControlReg = 0x0C
BitFramingReg = 0x0D
CollReg = 0x0E
ModeReg = 0x11
TxControlReg = 0x14
TxASKReg = 0x15
TModeReg = 0x2A
TPrescalerReg = 0x2B
TReloadRegH = 0x2C
TReloadRegL = 0x2D
TCounterValueRegH = 0x2E
TCounterValueRegL = 0x2F

# MIFARE Commands
MIFARE_REQUEST = 0x26
MIFARE_ANTICOLL = 0x93
MIFARE_SELECTTAG = 0x93
MIFARE_AUTHENT1A = 0x60
MIFARE_AUTHENT1B = 0x61
MIFARE_READ = 0x30
MIFARE_WRITE = 0xA0
MIFARE_DECREMENT = 0xC0
MIFARE_INCREMENT = 0xC1
MIFARE_RESTORE = 0xC2
MIFARE_TRANSFER = 0xB0
MIFARE_HALT = 0x50

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class MFRC522:
    """MFRC522 RFID Reader Driver"""
    
    def __init__(self, spi_device=0, spi_bus=0):
        """Initialize MFRC522 RFID reader"""
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000
        self._init_device()
    
    def _init_device(self):
        """Initialize MFRC522 device"""
        self._reset()
        self._write_register(TModeReg, 0x8D)
        self._write_register(TPrescalerReg, 0x3E)
        self._write_register(TReloadRegL, 30)
        self._write_register(TReloadRegH, 0)
        self._write_register(TxASKReg, 0x40)
        self._write_register(ModeReg, 0x3D)
        self._antenna_on()
    
    def _reset(self):
        """Reset MFRC522"""
        self._write_register(CommandReg, MFRC522_SOFTRESET)
    
    def _write_register(self, addr, val):
        """Write to MFRC522 register"""
        self.spi.xfer2([(addr << 1) & 0x7E, val])
    
    def _read_register(self, addr):
        """Read from MFRC522 register"""
        val = self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0])
        return val[1]
    
    def _set_bit_mask(self, reg, mask):
        """Set bits in register"""
        tmp = self._read_register(reg)
        self._write_register(reg, tmp | mask)
    
    def _clear_bit_mask(self, reg, mask):
        """Clear bits in register"""
        tmp = self._read_register(reg)
        self._write_register(reg, tmp & (~mask))
    
    def _antenna_on(self):
        """Turn antenna on"""
        temp = self._read_register(TxControlReg)
        if ~(temp & 0x03):
            self._set_bit_mask(TxControlReg, 0x03)
    
    def _antenna_off(self):
        """Turn antenna off"""
        self._clear_bit_mask(TxControlReg, 0x03)
    
    def _to_card(self, command, send_data):
        """Communicate with card"""
        back_data = []
        back_len = 0
        status = 2  # Error
        irq_en = 0x00
        wait_irq = 0x00
        
        if command == MFRC522_AUTHENT:
            irq_en = 0x12
            wait_irq = 0x10
        elif command == MFRC522_TRANSCEIVE:
            irq_en = 0x77
            wait_irq = 0x30
        
        self._write_register(ComIEnReg, irq_en | 0x80)
        self._clear_bit_mask(ComIrqReg, 0x80)
        self._set_bit_mask(FIFOLevelReg, 0x80)
        self._write_register(CommandReg, MFRC522_IDLE)
        
        for data in send_data:
            self._write_register(FIFODataReg, data)
        
        self._write_register(CommandReg, command)
        
        if command == MFRC522_TRANSCEIVE:
            self._set_bit_mask(BitFramingReg, 0x80)
        
        i = 2000
        while True:
            n = self._read_register(ComIrqReg)
            i -= 1
            if ~((i != 0) and ~(n & 0x01) and ~(n & wait_irq)):
                break
        
        self._clear_bit_mask(BitFramingReg, 0x80)
        
        if i != 0:
            if (self._read_register(ErrorReg) & 0x1B) == 0x00:
                status = 0  # OK
                
                if n & irq_en & 0x01:
                    status = 1  # No card
                
                if command == MFRC522_TRANSCEIVE:
                    n = self._read_register(FIFOLevelReg)
                    last_bits = self._read_register(ControlReg) & 0x07
                    if last_bits != 0:
                        back_len = (n - 1) * 8 + last_bits
                    else:
                        back_len = n * 8
                    
                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16
                    
                    for i in range(n):
                        back_data.append(self._read_register(FIFODataReg))
            else:
                status = 2  # Error
        
        return (status, back_data, back_len)
    
    def request(self, req_mode=MIFARE_REQUEST):
        """Request card"""
        back_bits = 0
        self._write_register(BitFramingReg, 0x07)
        
        tag_type = [req_mode]
        (status, back_data, back_bits) = self._to_card(MFRC522_TRANSCEIVE, tag_type)
        
        if status != 0 or back_bits != 0x10:
            status = 2
        
        return (status, back_bits)
    
    def anticoll(self):
        """Anti-collision detection"""
        ser_num_check = 0
        ser_num = []
        
        self._write_register(BitFramingReg, 0x00)
        
        ser_num.append(MIFARE_ANTICOLL)
        ser_num.append(0x20)
        
        (status, back_data, back_bits) = self._to_card(MFRC522_TRANSCEIVE, ser_num)
        
        if status == 0:
            if len(back_data) == 5:
                for i in range(4):
                    ser_num_check ^= back_data[i]
                if ser_num_check != back_data[4]:
                    status = 2
                else:
                    ser_num = back_data[:4]
            else:
                status = 2
        
        return (status, ser_num)
    
    def select_tag(self, ser_num):
        """Select tag"""
        buf = []
        buf.append(MIFARE_SELECTTAG)
        buf.append(0x70)
        
        for i in range(5):
            buf.append(ser_num[i])
        
        pOut = self._calc_crc(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        
        (status, back_data, back_len) = self._to_card(MFRC522_TRANSCEIVE, buf)
        
        if (status == 0) and (back_len == 0x18):
            return back_data[0]
        else:
            return 0
    
    def _calc_crc(self, p_in_data):
        """Calculate CRC"""
        self._clear_bit_mask(DivIrqReg, 0x04)
        self._set_bit_mask(FIFOLevelReg, 0x80)
        
        for data in p_in_data:
            self._write_register(FIFODataReg, data)
        
        self._write_register(CommandReg, MFRC522_CALCCRC)
        
        i = 0xFF
        while True:
            n = self._read_register(DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        
        p_out_data = []
        p_out_data.append(self._read_register(0x22))
        p_out_data.append(self._read_register(0x21))
        
        return p_out_data
    
    def cleanup(self):
        """Clean up SPI"""
        self.spi.close()

class RFIDWelcomeSystem:
    """RFID-based personalized welcome system"""
    
    def __init__(self):
        """Initialize RFID welcome system"""
        
        # Initialize RFID reader
        try:
            self.rfid = MFRC522()
            self.has_rfid = True
            print("✓ RFID reader initialized")
        except Exception as e:
            self.has_rfid = False
            print(f"✗ RFID reader failed: {e}")
        
        # Initialize LCD display
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Welcome System")
            self.lcd.write(1, 0, "Initializing...")
            self.has_lcd = True
            print("✓ LCD display initialized")
        except Exception as e:
            self.has_lcd = False
            print(f"✗ LCD display failed: {e}")
        
        # Initialize status indicators
        try:
            self.scan_led = PWMLED(SCAN_LED_PIN)      # Breathing effect while scanning
            self.success_led = LED(SUCCESS_LED_PIN)
            self.error_led = LED(ERROR_LED_PIN)
            self.greeting_led = PWMLED(GREETING_LED_PIN)
            
            self.welcome_buzzer = Buzzer(WELCOME_BUZZER_PIN)
            self.alert_buzzer = Buzzer(ALERT_BUZZER_PIN)
            
            self.has_indicators = True
            print("✓ Status indicators initialized")
        except Exception as e:
            self.has_indicators = False
            print(f"✗ Status indicators failed: {e}")
        
        # Initialize control buttons
        try:
            self.register_button = Button(REGISTER_BUTTON_PIN, bounce_time=0.2)
            self.mode_button = Button(MODE_BUTTON_PIN, bounce_time=0.2)
            self.mute_button = Button(MUTE_BUTTON_PIN, bounce_time=0.2)
            
            self.register_button.when_pressed = self._start_registration
            self.mode_button.when_pressed = self._cycle_mode
            self.mute_button.when_pressed = self._toggle_mute
            
            self.has_buttons = True
            print("✓ Control buttons initialized")
        except Exception as e:
            self.has_buttons = False
            print(f"✗ Control buttons failed: {e}")
        
        # User database
        self.users = self.load_users()
        self.last_scanned_card = None
        self.last_scan_time = 0
        self.scan_cooldown = 3.0  # seconds between same card scans
        
        # Greeting modes
        self.greeting_modes = ["standard", "time_based", "custom", "silent"]
        self.current_mode = 0
        self.audio_muted = False
        
        # Registration state
        self.registration_mode = False
        self.registration_step = 0
        self.new_user_data = {}
        
        # Statistics
        self.scan_count = 0
        self.successful_scans = 0
        self.unknown_cards = 0
        self.scan_history = []
        
        # Background scanning
        self.scanning_active = True
        self.scan_thread = threading.Thread(target=self._scanning_loop, daemon=True)
        self.scan_thread.start()
        
        # Display update thread
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
        # Initialize display and indicators
        self._update_display()
        if self.has_indicators:
            self.scan_led.pulse()  # Breathing effect while scanning
            self.welcome_buzzer.beep(0.1, 0.1, n=3)  # Startup sound
        
        print("🎉 RFID Welcome System Initialized")
        print(f"Registered users: {len(self.users)}")
        print(f"Mode: {self.greeting_modes[self.current_mode].upper()}")
    
    def _scanning_loop(self):
        """Main RFID scanning loop"""
        while self.scanning_active:
            try:
                if self.has_rfid and not self.registration_mode:
                    # Request card
                    (status, tag_type) = self.rfid.request()
                    
                    if status == 0:
                        # Get card UID
                        (status, uid) = self.rfid.anticoll()
                        
                        if status == 0:
                            # Convert UID to string
                            card_id = ''.join([f'{byte:02X}' for byte in uid])
                            
                            # Check cooldown period
                            current_time = time.time()
                            if (card_id != self.last_scanned_card or 
                                current_time - self.last_scan_time > self.scan_cooldown):
                                
                                self._process_card_scan(card_id)
                                self.last_scanned_card = card_id
                                self.last_scan_time = current_time
                
                time.sleep(0.1)  # Scan frequency
                
            except Exception as e:
                print(f"Scanning error: {e}")
                time.sleep(1)
    
    def _process_card_scan(self, card_id):
        """Process scanned RFID card"""
        self.scan_count += 1
        
        # Log scan event
        scan_event = {
            'timestamp': datetime.now().isoformat(),
            'card_id': card_id,
            'mode': self.greeting_modes[self.current_mode]
        }
        
        # Check if user is registered
        if card_id in self.users:
            user = self.users[card_id]
            self.successful_scans += 1
            scan_event['user'] = user['name']
            scan_event['status'] = 'success'
            
            print(f"👤 Card recognized: {user['name']}")
            self._greet_user(user)
        else:
            self.unknown_cards += 1
            scan_event['status'] = 'unknown'
            
            print(f"❓ Unknown card: {card_id}")
            self._handle_unknown_card(card_id)
        
        self.scan_history.append(scan_event)
    
    def _greet_user(self, user):
        """Greet registered user"""
        name = user['name']
        custom_greeting = user.get('greeting', None)
        last_seen = user.get('last_seen', None)
        visits = user.get('visits', 0) + 1
        
        # Update user data
        user['last_seen'] = datetime.now().isoformat()
        user['visits'] = visits
        self.save_users()
        
        # Visual feedback
        if self.has_indicators:
            self.success_led.on()
            self.greeting_led.pulse()
        
        # Generate greeting based on mode
        greeting = self._generate_greeting(name, custom_greeting, visits, last_seen)
        
        # Display greeting
        if self.has_lcd:
            self._display_greeting(name, greeting)
        
        # Audio feedback
        if not self.audio_muted:
            self._play_greeting_sound(user.get('sound_pattern', 'default'))
            
            # Text-to-speech if available
            if user.get('tts_enabled', True):
                self._speak_greeting(greeting)
        
        # Schedule cleanup
        threading.Timer(5.0, self._clear_greeting).start()
    
    def _handle_unknown_card(self, card_id):
        """Handle unknown RFID card"""
        if self.has_indicators:
            self.error_led.on()
            self.alert_buzzer.beep(0.5, 0.5, n=2)  # Alert sound
        
        if self.has_lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Unknown Card")
            self.lcd.write(1, 0, "Not Registered")
        
        # Auto-clear after delay
        threading.Timer(3.0, self._clear_display).start()
    
    def _generate_greeting(self, name, custom_greeting, visits, last_seen):
        """Generate personalized greeting based on mode"""
        mode = self.greeting_modes[self.current_mode]
        
        if mode == "standard":
            return f"Welcome, {name}!"
        
        elif mode == "time_based":
            hour = datetime.now().hour
            if 5 <= hour < 12:
                return f"Good morning, {name}!"
            elif 12 <= hour < 17:
                return f"Good afternoon, {name}!"
            elif 17 <= hour < 21:
                return f"Good evening, {name}!"
            else:
                return f"Good night, {name}!"
        
        elif mode == "custom" and custom_greeting:
            return custom_greeting.replace("{name}", name)
        
        elif mode == "silent":
            return ""  # No verbal greeting
        
        else:
            return f"Hello, {name}!"
    
    def _display_greeting(self, name, greeting):
        """Display greeting on LCD"""
        if not self.has_lcd:
            return
        
        self.lcd.clear()
        
        # Split greeting for two lines if needed
        if len(greeting) <= 16:
            self.lcd.write(0, 0, greeting)
            self.lcd.write(1, 0, f"Visit #{self.users[self.last_scanned_card]['visits']}")
        else:
            # Display name on first line, message on second
            self.lcd.write(0, 0, f"Hi {name}!")
            time_str = datetime.now().strftime("%H:%M")
            self.lcd.write(1, 0, f"Welcome  {time_str}")
    
    def _play_greeting_sound(self, pattern="default"):
        """Play greeting sound pattern"""
        if not self.has_indicators:
            return
        
        patterns = {
            'default': [(0.1, 0.1), (0.1, 0.1), (0.2, 0.0)],
            'vip': [(0.1, 0.05)] * 5 + [(0.3, 0.0)],
            'simple': [(0.2, 0.0)],
            'melody': [(0.1, 0.1), (0.15, 0.1), (0.1, 0.1), (0.2, 0.0)]
        }
        
        pattern_sequence = patterns.get(pattern, patterns['default'])
        
        def play_pattern():
            for duration, pause in pattern_sequence:
                self.welcome_buzzer.beep(duration, pause, n=1)
        
        threading.Thread(target=play_pattern, daemon=True).start()
    
    def _speak_greeting(self, greeting):
        """Use text-to-speech for greeting (if available)"""
        if not greeting:
            return
        
        try:
            # Try to use espeak for TTS
            subprocess.run(['espeak', greeting], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         timeout=5)
        except:
            # TTS not available
            pass
    
    def _clear_greeting(self):
        """Clear greeting display and indicators"""
        if self.has_indicators:
            self.success_led.off()
            self.greeting_led.off()
        
        self._update_display()
    
    def _clear_display(self):
        """Clear error display"""
        if self.has_indicators:
            self.error_led.off()
        
        self._update_display()
    
    def _start_registration(self):
        """Start new user registration process"""
        if self.registration_mode:
            return
        
        print("\n📝 Starting user registration...")
        self.registration_mode = True
        self.registration_step = 0
        self.new_user_data = {}
        
        if self.has_lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Registration")
            self.lcd.write(1, 0, "Scan new card...")
        
        if self.has_indicators:
            self.alert_buzzer.beep(0.1, 0.1, n=3)
            # Flash all LEDs
            for led in [self.scan_led, self.success_led, self.error_led]:
                led.blink(on_time=0.2, off_time=0.2, n=3, background=True)
        
        # Start registration timeout
        threading.Timer(30.0, self._cancel_registration).start()
    
    def _cancel_registration(self):
        """Cancel registration if timeout"""
        if self.registration_mode:
            print("⏰ Registration timeout")
            self.registration_mode = False
            self._update_display()
            
            if self.has_indicators:
                self.alert_buzzer.beep(0.5, 0.0, n=1)
    
    def _display_loop(self):
        """Background display update loop"""
        display_cycle = 0
        
        while self.scanning_active:
            try:
                if self.has_lcd and not self.registration_mode:
                    # Only update display if no active greeting
                    if not self.greeting_led.is_lit:
                        if display_cycle % 60 == 0:  # Every 3 seconds
                            self._update_display()
                        elif display_cycle % 120 == 60:
                            self._show_statistics()
                    
                    display_cycle = (display_cycle + 1) % 120
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Display loop error: {e}")
                time.sleep(1)
    
    def _update_display(self):
        """Update LCD with system status"""
        if not self.has_lcd:
            return
        
        try:
            self.lcd.clear()
            
            if self.registration_mode:
                self.lcd.write(0, 0, "Registration")
                self.lcd.write(1, 0, "Scan card...")
            else:
                # Show welcome message and stats
                self.lcd.write(0, 0, "RFID Welcome")
                mode_char = {"standard": "S", "time_based": "T", 
                           "custom": "C", "silent": "Q"}
                mode_indicator = mode_char.get(self.greeting_modes[self.current_mode], "?")
                
                users_count = len(self.users)
                scans_today = sum(1 for scan in self.scan_history 
                                if datetime.fromisoformat(scan['timestamp']).date() == datetime.now().date())
                
                self.lcd.write(1, 0, f"U:{users_count} S:{scans_today} [{mode_indicator}]")
                
        except Exception as e:
            print(f"Display update error: {e}")
    
    def _show_statistics(self):
        """Show statistics on LCD"""
        if not self.has_lcd:
            return
        
        try:
            self.lcd.clear()
            
            accuracy = (self.successful_scans / self.scan_count * 100) if self.scan_count > 0 else 0
            
            self.lcd.write(0, 0, f"Scans: {self.scan_count}")
            self.lcd.write(1, 0, f"Success: {accuracy:.0f}%")
            
        except Exception as e:
            print(f"Statistics display error: {e}")
    
    def _cycle_mode(self):
        """Cycle through greeting modes"""
        self.current_mode = (self.current_mode + 1) % len(self.greeting_modes)
        mode_name = self.greeting_modes[self.current_mode]
        
        print(f"🔄 Mode: {mode_name.upper()}")
        
        if self.has_indicators:
            self.welcome_buzzer.beep(0.1, 0.1, n=self.current_mode + 1)
        
        if self.has_lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, f"Mode: {mode_name}")
            threading.Timer(2.0, self._update_display).start()
    
    def _toggle_mute(self):
        """Toggle audio mute"""
        self.audio_muted = not self.audio_muted
        
        print(f"🔇 Audio {'muted' if self.audio_muted else 'unmuted'}")
        
        if self.has_indicators:
            if self.audio_muted:
                self.alert_buzzer.beep(0.3, 0.0, n=1)  # Long beep for mute
            else:
                self.welcome_buzzer.beep(0.1, 0.1, n=2)  # Double beep for unmute
    
    def register_card(self, card_id, name, custom_greeting=None):
        """Register new RFID card"""
        self.users[card_id] = {
            'name': name,
            'greeting': custom_greeting,
            'registered': datetime.now().isoformat(),
            'last_seen': None,
            'visits': 0,
            'sound_pattern': 'default',
            'tts_enabled': True
        }
        
        self.save_users()
        print(f"✅ Registered {name} with card {card_id}")
        
        return True
    
    def load_users(self):
        """Load user database from file"""
        try:
            with open('rfid_users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Pre-populate with demo users
            return {
                'DEMO0001': {
                    'name': 'Alice',
                    'greeting': 'Welcome back, {name}! Have a great day!',
                    'sound_pattern': 'vip',
                    'visits': 0
                }
            }
    
    def save_users(self):
        """Save user database to file"""
        with open('rfid_users.json', 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def save_scan_history(self):
        """Save scan history to file"""
        try:
            with open('scan_history.json', 'w') as f:
                json.dump(self.scan_history, f, indent=2)
        except Exception as e:
            print(f"Failed to save scan history: {e}")
    
    def get_statistics(self):
        """Get system statistics"""
        return {
            'total_scans': self.scan_count,
            'successful_scans': self.successful_scans,
            'unknown_cards': self.unknown_cards,
            'registered_users': len(self.users),
            'success_rate': (self.successful_scans / self.scan_count * 100) if self.scan_count > 0 else 0,
            'current_mode': self.greeting_modes[self.current_mode],
            'audio_muted': self.audio_muted
        }
    
    def cleanup(self):
        """Clean up system resources"""
        print("\n🧹 Cleaning up welcome system...")
        
        # Stop scanning
        self.scanning_active = False
        
        # Wait for threads
        if self.scan_thread.is_alive():
            self.scan_thread.join(timeout=2)
        if self.display_thread.is_alive():
            self.display_thread.join(timeout=2)
        
        # Save data
        self.save_users()
        self.save_scan_history()
        
        # Clear display
        if self.has_lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Shutdown")
            time.sleep(2)
            self.lcd.clear()
        
        # Turn off indicators
        if self.has_indicators:
            for led in [self.scan_led, self.success_led, self.error_led, self.greeting_led]:
                led.off()
            self.welcome_buzzer.beep(0.2, 0.1, n=3)  # Shutdown sound
        
        # Close hardware
        if self.has_rfid:
            self.rfid.cleanup()
        
        if self.has_buttons:
            self.register_button.close()
            self.mode_button.close()
            self.mute_button.close()
        
        if self.has_indicators:
            self.scan_led.close()
            self.success_led.close()
            self.error_led.close()
            self.greeting_led.close()
            self.welcome_buzzer.close()
            self.alert_buzzer.close()

def interactive_demo():
    """Interactive RFID welcome system demo"""
    print("\n🎉 Interactive RFID Welcome Demo")
    print("Scan RFID cards for personalized greetings")
    print("Press Ctrl+C to exit")
    
    try:
        system = RFIDWelcomeSystem()
        
        print(f"\n📋 Controls:")
        print("📝 REGISTER Button: Register new users")
        print("🔄 MODE Button: Cycle greeting modes")
        print("🔇 MUTE Button: Toggle audio on/off")
        
        print(f"\n🎮 Greeting Modes:")
        for i, mode in enumerate(system.greeting_modes):
            indicator = "👉" if i == system.current_mode else "  "
            print(f"{indicator} {i+1}. {mode.upper()}")
        
        print(f"\n👥 Registered Users: {len(system.users)}")
        
        start_time = time.time()
        
        while True:
            # Display real-time status
            stats = system.get_statistics()
            elapsed = time.time() - start_time
            
            mode_icon = {"standard": "📢", "time_based": "🕐", 
                        "custom": "✨", "silent": "🔇"}
            current_icon = mode_icon.get(stats['current_mode'], "🎉")
            
            audio_status = "🔇" if stats['audio_muted'] else "🔊"
            scan_status = "🟢" if system.scan_led.is_lit else "⚫"
            
            print(f"\r{current_icon} {stats['current_mode'].upper()} | "
                  f"Scans: {stats['total_scans']:3d} | "
                  f"Success: {stats['success_rate']:3.0f}% | "
                  f"Users: {stats['registered_users']:2d} | "
                  f"{audio_status} {scan_status} | "
                  f"Time: {elapsed:.0f}s", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\n📊 Session Summary:")
        stats = system.get_statistics()
        print(f"Total scans: {stats['total_scans']}")
        print(f"Successful recognitions: {stats['successful_scans']}")
        print(f"Unknown cards: {stats['unknown_cards']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
        # Show user activity
        print(f"\n👥 User Activity:")
        for card_id, user in system.users.items():
            visits = user.get('visits', 0)
            last_seen = user.get('last_seen', 'Never')
            if last_seen != 'Never':
                last_seen = datetime.fromisoformat(last_seen).strftime('%H:%M:%S')
            print(f"  {user['name']}: {visits} visits (last: {last_seen})")
    finally:
        system.cleanup()

def demo_registration():
    """Demonstrate user registration process"""
    print("\n📝 RFID Registration Demo")
    
    try:
        system = RFIDWelcomeSystem()
        
        # Simulate registration of demo cards
        demo_users = [
            ('DEMO0002', 'Bob', 'Hey {name}! Good to see you!'),
            ('DEMO0003', 'Charlie', None),  # Use default greeting
            ('DEMO0004', 'Diana', 'Welcome aboard, Captain {name}!')
        ]
        
        for card_id, name, greeting in demo_users:
            print(f"\nRegistering {name}...")
            system.register_card(card_id, name, greeting)
            
            # Set custom properties
            if name == 'Bob':
                system.users[card_id]['sound_pattern'] = 'melody'
            elif name == 'Diana':
                system.users[card_id]['sound_pattern'] = 'vip'
            
            time.sleep(1)
        
        system.save_users()
        print(f"\n✅ Registered {len(demo_users)} demo users")
        
        # Simulate card scans
        print("\n🎬 Simulating card scans...")
        for card_id, name, _ in demo_users:
            print(f"\nScanning {name}'s card...")
            system._process_card_scan(card_id)
            time.sleep(5)  # Wait for greeting to complete
        
        # Show final statistics
        stats = system.get_statistics()
        print(f"\n📊 Demo Statistics:")
        print(f"Total users: {stats['registered_users']}")
        print(f"Total scans: {stats['total_scans']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    finally:
        system.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("RFID Welcome System")
    print("==================")
    print("🎉 Personalized Greeting System")
    print("👤 User Recognition & Tracking")
    print("🔊 Multi-Mode Greetings")
    print("📊 Visit Statistics")
    
    while True:
        print("\n\nSelect Demo Mode:")
        print("1. Interactive welcome system")
        print("2. User registration demo")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            interactive_demo()
        elif choice == '2':
            demo_registration()
        elif choice == '3':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()