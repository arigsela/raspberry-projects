#!/usr/bin/env python3
"""
Active Buzzer Control
Generate simple sounds and alerts with an active buzzer
"""

from gpiozero import Buzzer, Button
import time
import signal
import sys
from threading import Thread

# GPIO Configuration
BUZZER_PIN = 17
BUTTON_PIN = 18  # Optional button for interactive modes

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_buzzer_test():
    """Test basic buzzer functionality"""
    print("\n=== Basic Buzzer Test ===")
    print("Testing buzzer on/off...")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    try:
        # Simple on/off
        print("Buzzer ON")
        buzzer.on()
        time.sleep(1)
        
        print("Buzzer OFF")
        buzzer.off()
        time.sleep(0.5)
        
        # Multiple beeps
        print("3 short beeps")
        for _ in range(3):
            buzzer.on()
            time.sleep(0.1)
            buzzer.off()
            time.sleep(0.1)
        
    finally:
        buzzer.close()

def morse_code_demo():
    """Send Morse code messages"""
    print("\n=== Morse Code Demo ===")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    # Morse code timing (in seconds)
    DOT = 0.1
    DASH = 0.3
    SYMBOL_GAP = 0.1
    LETTER_GAP = 0.3
    WORD_GAP = 0.7
    
    # Morse code dictionary
    morse_code = {
        'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
        'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
        'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
        'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
        'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
        'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
        'Y': '-.--',  'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.',
        ' ': ' '
    }
    
    def send_morse(text):
        """Send text as Morse code"""
        text = text.upper()
        print(f"Sending: '{text}'")
        
        for char in text:
            if char in morse_code:
                code = morse_code[char]
                print(f"{char}: {code}")
                
                if char == ' ':
                    time.sleep(WORD_GAP)
                else:
                    for symbol in code:
                        if symbol == '.':
                            buzzer.on()
                            time.sleep(DOT)
                        elif symbol == '-':
                            buzzer.on()
                            time.sleep(DASH)
                        buzzer.off()
                        time.sleep(SYMBOL_GAP)
                    time.sleep(LETTER_GAP)
    
    try:
        # Send SOS
        send_morse("SOS")
        time.sleep(1)
        
        # Send custom message
        message = input("\nEnter message to send (or press Enter for 'HELLO'): ")
        if not message:
            message = "HELLO"
        send_morse(message)
        
    finally:
        buzzer.close()

def alarm_patterns():
    """Different alarm sound patterns"""
    print("\n=== Alarm Patterns ===")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    patterns = {
        "Fire Alarm": {
            "pattern": [(0.5, 0.5)] * 6,
            "description": "Continuous beeping"
        },
        "Burglar Alarm": {
            "pattern": [(0.1, 0.1)] * 10 + [(0, 1)],
            "description": "Rapid beeps with pause"
        },
        "Warning Beep": {
            "pattern": [(1, 1)] * 3,
            "description": "Slow beeps"
        },
        "Critical Alert": {
            "pattern": [(0.1, 0.05, 0.1, 0.05, 0.5, 0.5)] * 2,
            "description": "Two short, one long"
        },
        "Success": {
            "pattern": [(0.1, 0.05, 0.1, 0.05, 0.1, 0.05)],
            "description": "Three quick beeps"
        }
    }
    
    try:
        for name, config in patterns.items():
            print(f"\n{name}: {config['description']}")
            input("Press Enter to play...")
            
            pattern = config['pattern']
            for timing in pattern:
                if isinstance(timing, tuple):
                    for i in range(0, len(timing), 2):
                        if i < len(timing):
                            buzzer.on()
                            time.sleep(timing[i])
                            buzzer.off()
                            if i + 1 < len(timing):
                                time.sleep(timing[i + 1])
            
            time.sleep(0.5)
        
    finally:
        buzzer.close()

def doorbell_system():
    """Doorbell with button trigger"""
    print("\n=== Doorbell System ===")
    print("Press the button to ring doorbell")
    print("Press Ctrl+C to exit")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    try:
        button = Button(BUTTON_PIN)
        
        def ring_doorbell():
            """Play doorbell sound"""
            print("Ding Dong!")
            # Ding
            buzzer.on()
            time.sleep(0.2)
            buzzer.off()
            time.sleep(0.1)
            # Dong (same tone on active buzzer)
            buzzer.on()
            time.sleep(0.3)
            buzzer.off()
        
        button.when_pressed = ring_doorbell
        
        # Keep running
        signal.pause()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure button is connected to GPIO18")
    finally:
        buzzer.close()

def timer_alarm():
    """Countdown timer with alarm"""
    print("\n=== Timer Alarm ===")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    try:
        minutes = input("Enter timer duration in minutes (default 1): ")
        minutes = float(minutes) if minutes else 1.0
        seconds = minutes * 60
        
        print(f"Timer set for {minutes} minutes")
        print("Timer starting...")
        
        # Countdown
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            remaining = seconds - elapsed
            
            if remaining <= 0:
                break
            
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            print(f"\rTime remaining: {mins:02d}:{secs:02d}", end='')
            
            # Warning beeps in last 10 seconds
            if remaining <= 10 and remaining > 0:
                buzzer.on()
                time.sleep(0.05)
                buzzer.off()
            
            time.sleep(0.1)
        
        print("\n\nTIMER EXPIRED!")
        
        # Alarm sound
        for _ in range(5):
            buzzer.on()
            time.sleep(0.5)
            buzzer.off()
            time.sleep(0.2)
        
    finally:
        buzzer.close()

def metronome():
    """Musical metronome"""
    print("\n=== Metronome ===")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    try:
        bpm = input("Enter BPM (60-200, default 120): ")
        bpm = int(bpm) if bpm else 120
        bpm = max(60, min(200, bpm))  # Clamp to range
        
        beat_interval = 60.0 / bpm
        
        print(f"Metronome at {bpm} BPM")
        print("Press Ctrl+C to stop")
        
        beat_count = 0
        while True:
            beat_count += 1
            
            # Accent on first beat of measure
            if beat_count % 4 == 1:
                print(f"\r{beat_count}: TICK", end='')
                buzzer.on()
                time.sleep(0.05)
            else:
                print(f"\r{beat_count}: tick", end='')
                buzzer.on()
                time.sleep(0.02)
            
            buzzer.off()
            time.sleep(beat_interval - 0.05)
        
    except KeyboardInterrupt:
        print("\nMetronome stopped")
    finally:
        buzzer.close()

def notification_sounds():
    """System notification sounds"""
    print("\n=== Notification Sounds ===")
    
    buzzer = Buzzer(BUZZER_PIN)
    
    notifications = {
        "Message": [(0.1, 0.05, 0.1, 0)],
        "Email": [(0.05, 0.05, 0.05, 0.05, 0.1, 0)],
        "Error": [(0.5, 0)],
        "Warning": [(0.2, 0.1, 0.2, 0)],
        "Success": [(0.05, 0.05)] * 3,
        "Startup": [(0.1, 0.05, 0.15, 0.05, 0.2, 0)],
        "Shutdown": [(0.2, 0.05, 0.15, 0.05, 0.1, 0)]
    }
    
    try:
        for name, pattern in notifications.items():
            print(f"\n{name} notification")
            
            for timing in pattern:
                for i in range(0, len(timing), 2):
                    if timing[i] > 0:
                        buzzer.on()
                        time.sleep(timing[i])
                        buzzer.off()
                    if i + 1 < len(timing) and timing[i + 1] > 0:
                        time.sleep(timing[i + 1])
            
            time.sleep(0.5)
        
    finally:
        buzzer.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Active Buzzer Examples")
    print("=====================")
    print(f"Buzzer GPIO: {BUZZER_PIN}")
    print(f"Button GPIO: {BUTTON_PIN} (for doorbell demo)")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic buzzer test")
        print("2. Morse code sender")
        print("3. Alarm patterns")
        print("4. Doorbell system (needs button)")
        print("5. Timer alarm")
        print("6. Metronome")
        print("7. Notification sounds")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_buzzer_test()
        elif choice == '2':
            morse_code_demo()
        elif choice == '3':
            alarm_patterns()
        elif choice == '4':
            doorbell_system()
        elif choice == '5':
            timer_alarm()
        elif choice == '6':
            metronome()
        elif choice == '7':
            notification_sounds()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()