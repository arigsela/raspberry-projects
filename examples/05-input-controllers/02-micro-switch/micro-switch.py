#!/usr/bin/env python3
"""
Micro Switch Input Detection
Detect momentary switch presses with debouncing
"""

from gpiozero import Button, LED
import time
import signal
import sys

# GPIO Configuration
SWITCH_PIN = 17  # Micro switch input
LED_PIN = 18     # Status LED (optional)

# Debounce time in seconds
DEBOUNCE_TIME = 0.01  # 10ms debounce

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_switch_detection():
    """Basic micro switch detection"""
    print("\n=== Basic Micro Switch Detection ===")
    print("Press the micro switch...")
    print("Press Ctrl+C to exit")
    
    # Create button with debouncing
    switch = Button(SWITCH_PIN, bounce_time=DEBOUNCE_TIME)
    
    try:
        while True:
            if switch.is_pressed:
                print("Switch PRESSED")
                # Wait for release
                switch.wait_for_release()
                print("Switch RELEASED")
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()

def switch_with_led():
    """Control LED with micro switch"""
    print("\n=== Switch-Controlled LED ===")
    print("Press switch to toggle LED")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, bounce_time=DEBOUNCE_TIME)
    led = LED(LED_PIN)
    
    try:
        # Toggle LED on each press
        def toggle_led():
            led.toggle()
            state = "ON" if led.is_lit else "OFF"
            print(f"LED {state}")
        
        switch.when_pressed = toggle_led
        
        # Keep running
        signal.pause()
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()
        led.close()

def press_counter():
    """Count switch presses"""
    print("\n=== Press Counter ===")
    print("Count the number of presses")
    print("Press Ctrl+C to show total")
    
    switch = Button(SWITCH_PIN, bounce_time=DEBOUNCE_TIME)
    press_count = 0
    
    def increment_counter():
        nonlocal press_count
        press_count += 1
        print(f"Press #{press_count}")
    
    switch.when_pressed = increment_counter
    
    try:
        signal.pause()
    except KeyboardInterrupt:
        print(f"\n\nTotal presses: {press_count}")
    finally:
        switch.close()

def timing_game():
    """Reaction time game with micro switch"""
    print("\n=== Reaction Time Game ===")
    print("Press the switch as fast as possible when prompted!")
    
    switch = Button(SWITCH_PIN, bounce_time=DEBOUNCE_TIME)
    
    try:
        for round_num in range(3):
            print(f"\n\nRound {round_num + 1}/3")
            print("Get ready...")
            
            # Random delay
            import random
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            print("PRESS NOW!")
            start_time = time.time()
            
            # Wait for press
            switch.wait_for_press()
            
            reaction_time = time.time() - start_time
            print(f"Reaction time: {reaction_time*1000:.0f} ms")
            
            if reaction_time < 0.2:
                print("Excellent!")
            elif reaction_time < 0.3:
                print("Good!")
            else:
                print("Try to be faster!")
            
            time.sleep(1)
        
        print("\n\nGame Over!")
    
    finally:
        switch.close()

def morse_code_input():
    """Input Morse code with micro switch"""
    print("\n=== Morse Code Input ===")
    print("Use the switch to input Morse code")
    print("Short press = dot, Long press = dash")
    print("Press Enter when done with a letter")
    print("Type 'quit' to exit")
    
    switch = Button(SWITCH_PIN, bounce_time=DEBOUNCE_TIME)
    
    morse_dict = {
        '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
        '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
        '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
        '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
        '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
        '--..': 'Z'
    }
    
    try:
        while True:
            code = ""
            print("\nInput Morse code (press Enter when done):")
            
            while True:
                # Check for keyboard input
                import select
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    input()  # Consume the Enter key
                    break
                
                if switch.is_pressed:
                    press_start = time.time()
                    switch.wait_for_release()
                    press_duration = time.time() - press_start
                    
                    if press_duration < 0.3:
                        code += "."
                        print(".", end="", flush=True)
                    else:
                        code += "-"
                        print("-", end="", flush=True)
                
                time.sleep(0.01)
            
            if code in morse_dict:
                print(f" = {morse_dict[code]}")
            elif code == "":
                print("No code entered")
            else:
                print(f" = Unknown code: {code}")
            
            if input("Continue? (y/n): ").lower() != 'y':
                break
    
    finally:
        switch.close()

def debounce_demo():
    """Demonstrate the importance of debouncing"""
    print("\n=== Debounce Demonstration ===")
    print("Compare with and without debouncing")
    
    # First without debouncing
    print("\n1. WITHOUT debouncing (may show multiple presses):")
    switch_no_debounce = Button(SWITCH_PIN, bounce_time=0)
    
    press_count = 0
    
    def count_press():
        nonlocal press_count
        press_count += 1
        print(f"Press detected: {press_count}")
    
    switch_no_debounce.when_pressed = count_press
    
    print("Press the switch a few times...")
    time.sleep(5)
    
    switch_no_debounce.close()
    
    # Now with debouncing
    print(f"\n2. WITH debouncing ({DEBOUNCE_TIME*1000}ms):")
    switch_debounced = Button(SWITCH_PIN, bounce_time=DEBOUNCE_TIME)
    
    press_count = 0
    switch_debounced.when_pressed = count_press
    
    print("Press the switch a few times...")
    time.sleep(5)
    
    switch_debounced.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Micro Switch Examples")
    print("====================")
    print(f"Switch GPIO: {SWITCH_PIN}")
    print(f"LED GPIO: {LED_PIN} (optional)")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic switch detection")
        print("2. Switch-controlled LED")
        print("3. Press counter")
        print("4. Reaction time game")
        print("5. Morse code input")
        print("6. Debounce demonstration")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            basic_switch_detection()
        elif choice == '2':
            switch_with_led()
        elif choice == '3':
            press_counter()
        elif choice == '4':
            timing_game()
        elif choice == '5':
            morse_code_input()
        elif choice == '6':
            debounce_demo()
        elif choice == '7':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()