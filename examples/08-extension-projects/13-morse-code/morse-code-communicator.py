#!/usr/bin/env python3
"""
Morse Code Communicator

Interactive Morse code learning and communication system with LED/buzzer output,
button input, automatic translation, and educational features.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime
from enum import Enum
from collections import deque
import random

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602

# Hardware Pin Definitions
# Output devices
LED_PIN = 17          # Visual Morse output
BUZZER_PIN = 27       # Audio Morse output

# Input controls
KEY_BUTTON_PIN = 22   # Telegraph key / input button
MODE_BUTTON_PIN = 23  # Mode selection
SPEED_UP_PIN = 24     # Increase speed
SPEED_DOWN_PIN = 25   # Decrease speed

# Status indicators
LED_POWER_PIN = 5     # Power/ready indicator
LED_TX_PIN = 6        # Transmitting indicator
LED_RX_PIN = 13       # Receiving indicator

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Morse Code Timing (in seconds)
# Standard ratio is 1:3:7 (dot:dash:word)
BASE_UNIT = 0.1       # Base time unit (100ms default)
DOT_TIME = 1          # Dot duration (1 unit)
DASH_TIME = 3         # Dash duration (3 units)
INTRA_CHAR_GAP = 1    # Gap between dots/dashes (1 unit)
INTER_CHAR_GAP = 3    # Gap between characters (3 units)
INTER_WORD_GAP = 7    # Gap between words (7 units)

# WPM (Words Per Minute) settings
MIN_WPM = 5
MAX_WPM = 30
DEFAULT_WPM = 10

from gpiozero import LED, Button, Buzzer

class MorseMode(Enum):
    """Operating modes"""
    TRANSLATOR = "Translator"    # Text to Morse
    DECODER = "Decoder"         # Morse to text
    TRAINER = "Trainer"         # Learning mode
    GAME = "Game"               # Practice game
    BEACON = "Beacon"           # Repeating message

class MorseCode:
    """Morse code dictionary and utilities"""
    
    # International Morse Code
    MORSE_CODE = {
        # Letters
        'A': '.-',      'B': '-...',    'C': '-.-.',    'D': '-..',
        'E': '.',       'F': '..-.',    'G': '--.',     'H': '....',
        'I': '..',      'J': '.---',    'K': '-.-',     'L': '.-..',
        'M': '--',      'N': '-.',      'O': '---',     'P': '.--.',
        'Q': '--.-',    'R': '.-.',     'S': '...',     'T': '-',
        'U': '..-',     'V': '...-',    'W': '.--',     'X': '-..-',
        'Y': '-.--',    'Z': '--..',
        
        # Numbers
        '0': '-----',   '1': '.----',   '2': '..---',   '3': '...--',
        '4': '....-',   '5': '.....',   '6': '-....',   '7': '--...',
        '8': '---..',   '9': '----.',
        
        # Punctuation
        '.': '.-.-.-',  ',': '--..--',  '?': '..--..',  "'": '.----.',
        '!': '-.-.--',  '/': '-..-.',   '(': '-.--.',   ')': '-.--.-',
        '&': '.-...',   ':': '---...',  ';': '-.-.-.',  '=': '-...-',
        '+': '.-.-.',   '-': '-....-',  '_': '..--.-',  '"': '.-..-.',
        '$': '...-..-', '@': '.--.-.',  ' ': '/',
        
        # Prosigns (procedural signals)
        '<AR>': '.-.-.',    # End of message
        '<AS>': '.-...',    # Wait
        '<BT>': '-...-',    # Break / New paragraph
        '<SK>': '...-.-',   # End of contact
        '<SOS>': '...---...',  # Distress
        '<ERROR>': '........'  # Error/correction
    }
    
    # Reverse lookup dictionary
    REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items() if k not in ['<AR>', '<AS>', '<BT>', '<SK>', '<SOS>', '<ERROR>']}
    
    @staticmethod
    def encode(text):
        """Convert text to Morse code"""
        morse = []
        for char in text.upper():
            if char in MorseCode.MORSE_CODE:
                morse.append(MorseCode.MORSE_CODE[char])
            elif char == ' ':
                morse.append('/')
        return ' '.join(morse)
    
    @staticmethod
    def decode(morse):
        """Convert Morse code to text"""
        text = []
        words = morse.split(' / ')
        
        for word in words:
            chars = word.split(' ')
            for char in chars:
                if char in MorseCode.REVERSE_MORSE:
                    text.append(MorseCode.REVERSE_MORSE[char])
            text.append(' ')
        
        return ''.join(text).strip()

class MorseTransmitter:
    """Handles Morse code transmission"""
    
    def __init__(self, led_pin, buzzer_pin, wpm=DEFAULT_WPM):
        self.led = LED(led_pin)
        self.buzzer = Buzzer(buzzer_pin)
        self.wpm = wpm
        self.unit_time = self._calculate_unit_time(wpm)
        self.transmitting = False
        
    def _calculate_unit_time(self, wpm):
        """Calculate base unit time from WPM"""
        # PARIS standard: 50 units per word
        return 60.0 / (wpm * 50)
    
    def set_speed(self, wpm):
        """Set transmission speed"""
        self.wpm = max(MIN_WPM, min(MAX_WPM, wpm))
        self.unit_time = self._calculate_unit_time(self.wpm)
    
    def transmit_dot(self):
        """Transmit a dot"""
        self.led.on()
        self.buzzer.on()
        time.sleep(self.unit_time * DOT_TIME)
        self.led.off()
        self.buzzer.off()
        time.sleep(self.unit_time * INTRA_CHAR_GAP)
    
    def transmit_dash(self):
        """Transmit a dash"""
        self.led.on()
        self.buzzer.on()
        time.sleep(self.unit_time * DASH_TIME)
        self.led.off()
        self.buzzer.off()
        time.sleep(self.unit_time * INTRA_CHAR_GAP)
    
    def transmit_character(self, morse_char):
        """Transmit a single character in Morse"""
        for symbol in morse_char:
            if symbol == '.':
                self.transmit_dot()
            elif symbol == '-':
                self.transmit_dash()
        
        # Inter-character gap (minus the intra-char gap already added)
        time.sleep(self.unit_time * (INTER_CHAR_GAP - INTRA_CHAR_GAP))
    
    def transmit_message(self, message):
        """Transmit a complete message"""
        self.transmitting = True
        morse = MorseCode.encode(message)
        
        for i, char in enumerate(morse.split(' ')):
            if not self.transmitting:
                break
                
            if char == '/':
                # Word gap (minus inter-char gap)
                time.sleep(self.unit_time * (INTER_WORD_GAP - INTER_CHAR_GAP))
            else:
                self.transmit_character(char)
        
        self.transmitting = False
    
    def stop(self):
        """Stop transmission"""
        self.transmitting = False
        self.led.off()
        self.buzzer.off()
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        self.led.close()
        self.buzzer.close()

class MorseDecoder:
    """Handles Morse code decoding from button input"""
    
    def __init__(self, button_pin, wpm=DEFAULT_WPM):
        self.button = Button(button_pin, pull_up=True, bounce_time=0.01)
        self.wpm = wpm
        self.unit_time = self._calculate_unit_time(wpm)
        
        # Decoding state
        self.current_symbol = []
        self.current_word = []
        self.decoded_message = []
        
        # Timing tracking
        self.key_down_time = None
        self.key_up_time = time.time()
        self.last_activity = time.time()
        
        # Callbacks
        self.button.when_pressed = self._key_down
        self.button.when_released = self._key_up
        
        # Decoder thread
        self.decoding = False
        self.decode_thread = None
        
    def _calculate_unit_time(self, wpm):
        """Calculate base unit time from WPM"""
        return 60.0 / (wpm * 50)
    
    def set_speed(self, wpm):
        """Set expected input speed"""
        self.wpm = max(MIN_WPM, min(MAX_WPM, wpm))
        self.unit_time = self._calculate_unit_time(self.wpm)
    
    def _key_down(self):
        """Handle key press"""
        self.key_down_time = time.time()
        
        # Check gap since last activity
        gap = self.key_down_time - self.key_up_time
        
        if gap > self.unit_time * INTER_WORD_GAP:
            # New word
            if self.current_word:
                self._finish_word()
        elif gap > self.unit_time * INTER_CHAR_GAP:
            # New character
            if self.current_symbol:
                self._finish_character()
    
    def _key_up(self):
        """Handle key release"""
        if self.key_down_time is None:
            return
            
        self.key_up_time = time.time()
        duration = self.key_up_time - self.key_down_time
        
        # Determine dot or dash
        if duration < self.unit_time * 2:
            self.current_symbol.append('.')
        else:
            self.current_symbol.append('-')
        
        self.last_activity = time.time()
    
    def _finish_character(self):
        """Complete current character"""
        if not self.current_symbol:
            return
            
        morse_char = ''.join(self.current_symbol)
        if morse_char in MorseCode.REVERSE_MORSE:
            char = MorseCode.REVERSE_MORSE[morse_char]
            self.current_word.append(char)
        
        self.current_symbol = []
    
    def _finish_word(self):
        """Complete current word"""
        if self.current_symbol:
            self._finish_character()
            
        if self.current_word:
            word = ''.join(self.current_word)
            self.decoded_message.append(word)
            self.current_word = []
    
    def start_decoding(self):
        """Start the decoding process"""
        self.decoding = True
        self.decode_thread = threading.Thread(target=self._decode_loop, daemon=True)
        self.decode_thread.start()
    
    def stop_decoding(self):
        """Stop decoding"""
        self.decoding = False
        if self.decode_thread:
            self.decode_thread.join()
    
    def _decode_loop(self):
        """Monitor for timeout and finish characters/words"""
        while self.decoding:
            current_time = time.time()
            gap = current_time - self.last_activity
            
            if gap > self.unit_time * INTER_WORD_GAP and self.current_word:
                self._finish_word()
            elif gap > self.unit_time * INTER_CHAR_GAP and self.current_symbol:
                self._finish_character()
            
            time.sleep(0.1)
    
    def get_decoded_message(self):
        """Get the decoded message"""
        # Finish any pending input
        if self.current_symbol:
            self._finish_character()
        if self.current_word:
            self._finish_word()
            
        return ' '.join(self.decoded_message)
    
    def clear(self):
        """Clear decoded message"""
        self.current_symbol = []
        self.current_word = []
        self.decoded_message = []
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_decoding()
        self.button.close()

class MorseCommunicator:
    """Main Morse code communication system"""
    
    def __init__(self):
        print("🔤 Initializing Morse Code Communicator...")
        
        # Initialize hardware
        self._init_hardware()
        self._init_display()
        
        # System components
        self.transmitter = MorseTransmitter(LED_PIN, BUZZER_PIN)
        self.decoder = MorseDecoder(KEY_BUTTON_PIN)
        
        # System state
        self.mode = MorseMode.TRANSLATOR
        self.wpm = DEFAULT_WPM
        self.running = False
        
        # Message queues
        self.tx_queue = queue.Queue()
        self.rx_queue = queue.Queue()
        
        # Training data
        self.training_chars = list('ETAOINSHRDLCUMWFGYPBVKJXQZ0123456789')
        self.training_index = 0
        self.training_score = 0
        self.training_attempts = 0
        
        # Beacon message
        self.beacon_message = "CQ CQ CQ DE RASPI"
        self.beacon_interval = 30  # seconds
        
        # Statistics
        self.session_start = datetime.now()
        self.chars_transmitted = 0
        self.chars_received = 0
        self.training_sessions = 0
        
        # Load configuration
        self._load_configuration()
        
        print("✅ Morse communicator initialized")
    
    def _init_hardware(self):
        """Initialize hardware components"""
        # Status LEDs
        self.led_power = LED(LED_POWER_PIN)
        self.led_tx = LED(LED_TX_PIN)
        self.led_rx = LED(LED_RX_PIN)
        
        # Control buttons
        self.mode_button = Button(MODE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.speed_up_button = Button(SPEED_UP_PIN, pull_up=True, bounce_time=0.1)
        self.speed_down_button = Button(SPEED_DOWN_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.mode_button.when_pressed = self._cycle_mode
        self.speed_up_button.when_pressed = self._increase_speed
        self.speed_down_button.when_pressed = self._decrease_speed
        
        # Initial state
        self.led_power.on()
        
        print("✓ Hardware initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Morse Code")
            self.lcd.write(1, 0, "System Ready")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load saved configuration"""
        config_file = "morse_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.wpm = config.get('wpm', DEFAULT_WPM)
                    self.beacon_message = config.get('beacon_message', self.beacon_message)
                    self.beacon_interval = config.get('beacon_interval', self.beacon_interval)
                    
                    # Update components
                    self.transmitter.set_speed(self.wpm)
                    self.decoder.set_speed(self.wpm)
                    
                    print("✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def _save_configuration(self):
        """Save current configuration"""
        config_file = "morse_config.json"
        try:
            config = {
                'wpm': self.wpm,
                'beacon_message': self.beacon_message,
                'beacon_interval': self.beacon_interval,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
    
    def run(self):
        """Main system loop"""
        print("\n🔤 Morse Code Communicator Active!")
        print(f"Mode: {self.mode.value}")
        print(f"Speed: {self.wpm} WPM")
        print("Press MODE to change mode")
        print("Press Ctrl+C to exit\n")
        
        self.running = True
        self.decoder.start_decoding()
        
        # Start mode-specific threads
        if self.mode == MorseMode.TRANSLATOR:
            threading.Thread(target=self._translator_mode, daemon=True).start()
        elif self.mode == MorseMode.DECODER:
            threading.Thread(target=self._decoder_mode, daemon=True).start()
        elif self.mode == MorseMode.TRAINER:
            threading.Thread(target=self._trainer_mode, daemon=True).start()
        elif self.mode == MorseMode.GAME:
            threading.Thread(target=self._game_mode, daemon=True).start()
        elif self.mode == MorseMode.BEACON:
            threading.Thread(target=self._beacon_mode, daemon=True).start()
        
        # Update display
        self._update_display()
        
        try:
            while self.running:
                # Handle any pending operations
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down Morse communicator...")
            self.running = False
            self.transmitter.stop()
            self.decoder.stop_decoding()
            time.sleep(1)
    
    def _translator_mode(self):
        """Text to Morse translator mode"""
        print("📝 Translator Mode - Enter text to transmit as Morse")
        
        while self.running and self.mode == MorseMode.TRANSLATOR:
            try:
                # Get user input
                text = input("\nEnter message (or 'quit'): ")
                
                if text.lower() == 'quit':
                    break
                
                # Display and transmit
                morse = MorseCode.encode(text)
                print(f"Morse: {morse}")
                
                self.led_tx.on()
                self._update_display("Transmitting", text[:16])
                
                self.transmitter.transmit_message(text)
                self.chars_transmitted += len(text)
                
                self.led_tx.off()
                self._update_display("Ready", f"Speed: {self.wpm} WPM")
                
            except EOFError:
                break
    
    def _decoder_mode(self):
        """Morse to text decoder mode"""
        print("🎧 Decoder Mode - Use the key to input Morse code")
        self._update_display("Decoder Mode", "Key to input")
        
        last_message = ""
        
        while self.running and self.mode == MorseMode.DECODER:
            # Check for decoded input
            message = self.decoder.get_decoded_message()
            
            if message and message != last_message:
                self.led_rx.on()
                print(f"\nDecoded: {message}")
                self._update_display("Received:", message[-16:])
                self.chars_received += len(message) - len(last_message)
                last_message = message
                time.sleep(0.5)
                self.led_rx.off()
            
            time.sleep(0.1)
    
    def _trainer_mode(self):
        """Interactive training mode"""
        print("🎓 Training Mode - Learn Morse code!")
        self.training_sessions += 1
        
        while self.running and self.mode == MorseMode.TRAINER:
            # Get next character to practice
            char = self.training_chars[self.training_index]
            morse = MorseCode.MORSE_CODE[char]
            
            print(f"\nTransmitting: {char} = {morse}")
            self._update_display(f"Learn: {char}", f"Morse: {morse}")
            
            # Transmit the character
            self.led_tx.on()
            self.transmitter.transmit_character(morse)
            self.led_tx.off()
            
            # Wait for user to echo it back
            print("Now you try! Press the key to repeat")
            self._update_display("Your turn:", f"Send {char}")
            
            # Clear decoder
            self.decoder.clear()
            
            # Wait for input
            start_time = time.time()
            timeout = 15  # seconds
            
            while time.time() - start_time < timeout:
                if not self.running or self.mode != MorseMode.TRAINER:
                    break
                    
                received = self.decoder.get_decoded_message()
                if received:
                    self.training_attempts += 1
                    
                    if char in received.upper():
                        print("✅ Correct!")
                        self._update_display("Correct!", "Well done!")
                        self.training_score += 1
                        time.sleep(2)
                        break
                    else:
                        print(f"❌ Incorrect. You sent: {received}")
                        self._update_display("Try again", f"Got: {received}")
                        self.decoder.clear()
                
                time.sleep(0.1)
            
            # Move to next character
            self.training_index = (self.training_index + 1) % len(self.training_chars)
            
            # Show score periodically
            if self.training_attempts % 10 == 0 and self.training_attempts > 0:
                accuracy = (self.training_score / self.training_attempts) * 100
                print(f"\n📊 Score: {self.training_score}/{self.training_attempts} ({accuracy:.1f}%)")
                time.sleep(2)
    
    def _game_mode(self):
        """Morse code game mode"""
        print("🎮 Game Mode - Random Morse challenges!")
        
        words = ['THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 
                'CAN', 'HAD', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY']
        
        score = 0
        rounds = 0
        
        while self.running and self.mode == MorseMode.GAME:
            # Pick random word
            word = random.choice(words)
            morse = MorseCode.encode(word)
            
            rounds += 1
            print(f"\nRound {rounds}: Listen carefully...")
            self._update_display(f"Round {rounds}", "Listen...")
            
            time.sleep(2)
            
            # Transmit the word
            self.led_tx.on()
            self.transmitter.transmit_message(word)
            self.led_tx.off()
            
            # Get user input
            print("What word was that? ")
            self._update_display("Your answer?", "Use key")
            
            # Clear decoder
            self.decoder.clear()
            
            # Wait for response
            start_time = time.time()
            timeout = 20
            
            while time.time() - start_time < timeout:
                if not self.running or self.mode != MorseMode.GAME:
                    break
                    
                answer = self.decoder.get_decoded_message().strip().upper()
                if answer:
                    if answer == word:
                        score += 1
                        print(f"✅ Correct! Score: {score}/{rounds}")
                        self._update_display("Correct!", f"Score: {score}/{rounds}")
                    else:
                        print(f"❌ Wrong. It was '{word}'. You sent: '{answer}'")
                        self._update_display("Wrong!", f"Was: {word}")
                    
                    time.sleep(3)
                    break
                
                time.sleep(0.1)
    
    def _beacon_mode(self):
        """Automatic beacon transmission mode"""
        print(f"📡 Beacon Mode - Transmitting every {self.beacon_interval}s")
        print(f"Message: {self.beacon_message}")
        
        while self.running and self.mode == MorseMode.BEACON:
            # Transmit beacon
            self._update_display("Beacon TX", self.beacon_message[:16])
            self.led_tx.on()
            
            self.transmitter.transmit_message(self.beacon_message)
            self.chars_transmitted += len(self.beacon_message)
            
            self.led_tx.off()
            self._update_display("Beacon Mode", f"Next: {self.beacon_interval}s")
            
            # Wait for next transmission
            for i in range(self.beacon_interval):
                if not self.running or self.mode != MorseMode.BEACON:
                    break
                time.sleep(1)
    
    def _cycle_mode(self):
        """Cycle through operating modes"""
        modes = list(MorseMode)
        current_index = modes.index(self.mode)
        new_index = (current_index + 1) % len(modes)
        self.mode = modes[new_index]
        
        print(f"\n🔄 Mode: {self.mode.value}")
        self._update_display(self.mode.value, f"{self.wpm} WPM")
        
        # Stop current mode operations
        self.transmitter.stop()
        self.decoder.clear()
        
        # Restart in new mode
        if self.mode == MorseMode.TRANSLATOR:
            threading.Thread(target=self._translator_mode, daemon=True).start()
        elif self.mode == MorseMode.DECODER:
            threading.Thread(target=self._decoder_mode, daemon=True).start()
        elif self.mode == MorseMode.TRAINER:
            threading.Thread(target=self._trainer_mode, daemon=True).start()
        elif self.mode == MorseMode.GAME:
            threading.Thread(target=self._game_mode, daemon=True).start()
        elif self.mode == MorseMode.BEACON:
            threading.Thread(target=self._beacon_mode, daemon=True).start()
    
    def _increase_speed(self):
        """Increase transmission speed"""
        if self.wpm < MAX_WPM:
            self.wpm += 1
            self.transmitter.set_speed(self.wpm)
            self.decoder.set_speed(self.wpm)
            print(f"⬆ Speed: {self.wpm} WPM")
            self._update_display(self.mode.value, f"{self.wpm} WPM")
            self._save_configuration()
    
    def _decrease_speed(self):
        """Decrease transmission speed"""
        if self.wpm > MIN_WPM:
            self.wpm -= 1
            self.transmitter.set_speed(self.wpm)
            self.decoder.set_speed(self.wpm)
            print(f"⬇ Speed: {self.wpm} WPM")
            self._update_display(self.mode.value, f"{self.wpm} WPM")
            self._save_configuration()
    
    def _update_display(self, line1="", line2=""):
        """Update LCD display"""
        if not self.lcd:
            return
            
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, line1[:16])
            self.lcd.write(1, 0, line2[:16])
        except Exception as e:
            print(f"⚠ Display error: {e}")
    
    def get_statistics(self):
        """Get session statistics"""
        runtime = (datetime.now() - self.session_start).total_seconds()
        
        return {
            'runtime_seconds': runtime,
            'chars_transmitted': self.chars_transmitted,
            'chars_received': self.chars_received,
            'training_sessions': self.training_sessions,
            'training_score': self.training_score,
            'training_attempts': self.training_attempts,
            'current_wpm': self.wpm
        }
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop operation
        self.running = False
        
        # Save configuration
        self._save_configuration()
        
        # Stop components
        self.transmitter.cleanup()
        self.decoder.cleanup()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
        
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Runtime: {stats['runtime_seconds']/60:.1f} minutes")
        print(f"  Characters transmitted: {stats['chars_transmitted']}")
        print(f"  Characters received: {stats['chars_received']}")
        
        if stats['training_attempts'] > 0:
            accuracy = (stats['training_score'] / stats['training_attempts']) * 100
            print(f"  Training accuracy: {accuracy:.1f}%")
        
        # Clean up hardware
        self.led_power.close()
        self.led_tx.close()
        self.led_rx.close()
        self.mode_button.close()
        self.speed_up_button.close()
        self.speed_down_button.close()
        
        print("\n✅ Cleanup complete")


def morse_demo():
    """Demonstrate Morse code features"""
    print("\n🎮 Morse Code Demo")
    print("=" * 50)
    
    transmitter = MorseTransmitter(LED_PIN, BUZZER_PIN, wpm=15)
    
    try:
        # Demo 1: Common signals
        print("\n1. Common Morse Signals")
        
        signals = [
            ("SOS", "... --- ..."),
            ("OK", "--- -.-"),
            ("73", "--... ...--"),  # Best regards
            ("88", "---.. ---.."),  # Love and kisses
        ]
        
        for name, morse in signals:
            print(f"\nTransmitting {name}: {morse}")
            transmitter.transmit_message(name)
            time.sleep(1)
        
        # Demo 2: Alphabet
        print("\n2. Morse Alphabet")
        for char in "MORSE":
            morse = MorseCode.MORSE_CODE[char]
            print(f"{char} = {morse}")
            transmitter.transmit_character(morse)
            time.sleep(0.5)
        
        # Demo 3: Speed demonstration
        print("\n3. Speed Demonstration")
        for wpm in [5, 10, 20]:
            print(f"\nSpeed: {wpm} WPM")
            transmitter.set_speed(wpm)
            transmitter.transmit_message("TEST")
            time.sleep(1)
        
        print("\n✅ Demo complete!")
        
    finally:
        transmitter.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        morse_demo()
    else:
        # Normal operation
        communicator = MorseCommunicator()
        try:
            communicator.run()
        finally:
            communicator.cleanup()
