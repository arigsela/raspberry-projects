#!/usr/bin/env python3
"""
Passive Buzzer Control
Generate melodies and tones with a passive buzzer using PWM
"""

from gpiozero import PWMOutputDevice
import time
import math
import signal
import sys

# GPIO Configuration
BUZZER_PIN = 18

# Musical note frequencies (Hz)
NOTES = {
    # Octave 0
    'C0': 16.35, 'C#0': 17.32, 'D0': 18.35, 'D#0': 19.45,
    'E0': 20.60, 'F0': 21.83, 'F#0': 23.12, 'G0': 24.50,
    'G#0': 25.96, 'A0': 27.50, 'A#0': 29.14, 'B0': 30.87,
    
    # Octave 4 (Middle)
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
    'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
    'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
    
    # Octave 5
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
    'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99,
    'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
    
    # Octave 6
    'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51,
    'E6': 1318.51, 'F6': 1396.91, 'F#6': 1479.98, 'G6': 1567.98,
    'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53,
    
    # Special
    'REST': 0
}

class PassiveBuzzer:
    """Control a passive buzzer with PWM"""
    
    def __init__(self, pin):
        self.buzzer = PWMOutputDevice(pin)
        self.current_frequency = 0
    
    def play_tone(self, frequency, duration):
        """Play a tone at given frequency for duration"""
        if frequency > 0:
            # Calculate PWM frequency (limited by Pi's capabilities)
            # Max reliable frequency is about 8000 Hz
            freq = min(frequency, 8000)
            self.buzzer.frequency = freq
            self.buzzer.value = 0.5  # 50% duty cycle
        else:
            self.buzzer.value = 0  # Silence
        
        time.sleep(duration)
        self.buzzer.value = 0  # Stop
    
    def play_note(self, note, duration):
        """Play a musical note"""
        if note in NOTES:
            self.play_tone(NOTES[note], duration)
        else:
            print(f"Unknown note: {note}")
    
    def sweep(self, start_freq, end_freq, duration, steps=100):
        """Sweep frequency from start to end"""
        for i in range(steps):
            freq = start_freq + (end_freq - start_freq) * i / steps
            self.play_tone(freq, duration / steps)
    
    def close(self):
        """Clean up"""
        self.buzzer.close()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_tones_demo():
    """Demonstrate basic tone generation"""
    print("\n=== Basic Tones Demo ===")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    
    try:
        # Single tones
        print("Playing single tones...")
        frequencies = [262, 330, 392, 523]  # C, E, G, C
        for freq in frequencies:
            print(f"Frequency: {freq} Hz")
            buzzer.play_tone(freq, 0.5)
            time.sleep(0.1)
        
        # Frequency sweep
        print("\nFrequency sweep (100-2000 Hz)...")
        buzzer.sweep(100, 2000, 2)
        
        print("\nReverse sweep (2000-100 Hz)...")
        buzzer.sweep(2000, 100, 2)
        
    finally:
        buzzer.close()

def musical_scales():
    """Play musical scales"""
    print("\n=== Musical Scales ===")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    
    scales = {
        "C Major": ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'],
        "C Minor": ['C4', 'D4', 'D#4', 'F4', 'G4', 'G#4', 'A#4', 'C5'],
        "Chromatic": ['C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4', 'C5'],
        "Pentatonic": ['C4', 'D4', 'E4', 'G4', 'A4', 'C5']
    }
    
    try:
        for scale_name, notes in scales.items():
            print(f"\nPlaying {scale_name} scale...")
            
            # Ascending
            for note in notes:
                buzzer.play_note(note, 0.3)
            
            time.sleep(0.2)
            
            # Descending
            for note in reversed(notes[:-1]):
                buzzer.play_note(note, 0.3)
            
            time.sleep(0.5)
        
    finally:
        buzzer.close()

def play_melody():
    """Play simple melodies"""
    print("\n=== Melody Player ===")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    
    # Format: (note, duration)
    melodies = {
        "Happy Birthday": [
            ('G4', 0.25), ('G4', 0.25), ('A4', 0.5), ('G4', 0.5), ('C5', 0.5), ('B4', 1.0),
            ('G4', 0.25), ('G4', 0.25), ('A4', 0.5), ('G4', 0.5), ('D5', 0.5), ('C5', 1.0),
            ('G4', 0.25), ('G4', 0.25), ('G5', 0.5), ('E5', 0.5), ('C5', 0.5), ('B4', 0.5), ('A4', 0.5),
            ('F5', 0.25), ('F5', 0.25), ('E5', 0.5), ('C5', 0.5), ('D5', 0.5), ('C5', 1.0)
        ],
        
        "Twinkle Twinkle": [
            ('C4', 0.5), ('C4', 0.5), ('G4', 0.5), ('G4', 0.5),
            ('A4', 0.5), ('A4', 0.5), ('G4', 1.0),
            ('F4', 0.5), ('F4', 0.5), ('E4', 0.5), ('E4', 0.5),
            ('D4', 0.5), ('D4', 0.5), ('C4', 1.0),
            ('G4', 0.5), ('G4', 0.5), ('F4', 0.5), ('F4', 0.5),
            ('E4', 0.5), ('E4', 0.5), ('D4', 1.0),
            ('G4', 0.5), ('G4', 0.5), ('F4', 0.5), ('F4', 0.5),
            ('E4', 0.5), ('E4', 0.5), ('D4', 1.0)
        ],
        
        "Mary Had a Little Lamb": [
            ('E4', 0.5), ('D4', 0.5), ('C4', 0.5), ('D4', 0.5),
            ('E4', 0.5), ('E4', 0.5), ('E4', 1.0),
            ('D4', 0.5), ('D4', 0.5), ('D4', 1.0),
            ('E4', 0.5), ('G4', 0.5), ('G4', 1.0),
            ('E4', 0.5), ('D4', 0.5), ('C4', 0.5), ('D4', 0.5),
            ('E4', 0.5), ('E4', 0.5), ('E4', 0.5), ('E4', 0.5),
            ('D4', 0.5), ('D4', 0.5), ('E4', 0.5), ('D4', 0.5),
            ('C4', 1.0)
        ]
    }
    
    try:
        for melody_name, notes in melodies.items():
            print(f"\nPlaying: {melody_name}")
            input("Press Enter to play...")
            
            for note, duration in notes:
                buzzer.play_note(note, duration * 0.8)  # Small gap between notes
                time.sleep(duration * 0.2)
            
            time.sleep(0.5)
        
    finally:
        buzzer.close()

def sound_effects():
    """Generate various sound effects"""
    print("\n=== Sound Effects ===")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    
    try:
        # Siren
        print("\n1. Siren")
        for _ in range(3):
            buzzer.sweep(400, 800, 0.5)
            buzzer.sweep(800, 400, 0.5)
        
        time.sleep(0.5)
        
        # Laser
        print("\n2. Laser")
        buzzer.sweep(2000, 100, 0.3)
        
        time.sleep(0.5)
        
        # Explosion
        print("\n3. Explosion")
        # White noise simulation with rapid frequency changes
        import random
        for _ in range(50):
            freq = random.randint(100, 500)
            buzzer.play_tone(freq, 0.01)
        
        time.sleep(0.5)
        
        # R2-D2 style
        print("\n4. Robot voice")
        for _ in range(10):
            freq = random.choice([500, 800, 1000, 1200])
            duration = random.uniform(0.05, 0.2)
            buzzer.play_tone(freq, duration)
        
        time.sleep(0.5)
        
        # Phone ring
        print("\n5. Phone ring")
        for _ in range(3):
            buzzer.play_tone(1000, 0.1)
            buzzer.play_tone(800, 0.1)
            time.sleep(0.3)
        
    finally:
        buzzer.close()

def piano_simulator():
    """Simple piano keyboard simulator"""
    print("\n=== Piano Simulator ===")
    print("Press keys to play notes (q to quit):")
    print("  a s d f g h j k l  - white keys (C D E F G A B C)")
    print("  w e   t y u   o p  - black keys (sharps)")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    
    # Keyboard mapping
    key_map = {
        'a': 'C4', 'w': 'C#4', 's': 'D4', 'e': 'D#4', 'd': 'E4',
        'f': 'F4', 't': 'F#4', 'g': 'G4', 'y': 'G#4', 'h': 'A4',
        'u': 'A#4', 'j': 'B4', 'k': 'C5', 'o': 'C#5', 'l': 'D5',
        'p': 'D#5'
    }
    
    try:
        import termios, tty
        
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        
        try:
            # Set terminal to raw mode
            tty.setraw(sys.stdin.fileno())
            
            while True:
                key = sys.stdin.read(1)
                
                if key == 'q':
                    break
                elif key in key_map:
                    note = key_map[key]
                    # Play note in separate thread to not block input
                    import threading
                    threading.Thread(
                        target=lambda: buzzer.play_note(note, 0.2)
                    ).start()
        
        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    except ImportError:
        print("Terminal control not available. Playing demo instead...")
        # Play a simple tune
        for note in ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5']:
            buzzer.play_note(note, 0.3)
    
    finally:
        buzzer.close()

def alarm_clock():
    """Alarm clock with increasing intensity"""
    print("\n=== Alarm Clock ===")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    
    try:
        seconds = input("Enter alarm duration in seconds (default 5): ")
        seconds = int(seconds) if seconds else 5
        
        print("Alarm starting...")
        
        # Gentle wake-up
        print("Phase 1: Gentle")
        for _ in range(3):
            buzzer.play_note('C5', 0.1)
            time.sleep(0.5)
        
        # Medium intensity
        print("Phase 2: Medium")
        for _ in range(5):
            buzzer.play_note('E5', 0.1)
            buzzer.play_note('G5', 0.1)
            time.sleep(0.3)
        
        # High intensity
        print("Phase 3: Wake up!")
        end_time = time.time() + (seconds - 3)
        while time.time() < end_time:
            buzzer.play_tone(1000, 0.1)
            buzzer.play_tone(1500, 0.1)
        
    finally:
        buzzer.close()

def morse_code_advanced():
    """Morse code with tones"""
    print("\n=== Morse Code with Tones ===")
    
    buzzer = PassiveBuzzer(BUZZER_PIN)
    TONE_FREQ = 800  # Hz
    
    # Timing
    DOT = 0.1
    DASH = 0.3
    
    morse = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', ' ': ' '
    }
    
    try:
        message = input("Enter message (or press Enter for 'SOS'): ").upper()
        if not message:
            message = "SOS"
        
        print(f"Sending: {message}")
        
        for char in message:
            if char in morse:
                print(f"{char}: {morse[char]}")
                
                if char == ' ':
                    time.sleep(0.5)
                else:
                    for symbol in morse[char]:
                        if symbol == '.':
                            buzzer.play_tone(TONE_FREQ, DOT)
                        elif symbol == '-':
                            buzzer.play_tone(TONE_FREQ, DASH)
                        time.sleep(DOT)
                    time.sleep(DASH)
        
    finally:
        buzzer.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Passive Buzzer Examples")
    print("======================")
    print(f"Buzzer GPIO: {BUZZER_PIN}")
    print("Note: Passive buzzers require PWM signal")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic tones and sweeps")
        print("2. Musical scales")
        print("3. Play melodies")
        print("4. Sound effects")
        print("5. Piano simulator")
        print("6. Alarm clock")
        print("7. Morse code with tones")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_tones_demo()
        elif choice == '2':
            musical_scales()
        elif choice == '3':
            play_melody()
        elif choice == '4':
            sound_effects()
        elif choice == '5':
            piano_simulator()
        elif choice == '6':
            alarm_clock()
        elif choice == '7':
            morse_code_advanced()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()