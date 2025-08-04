#!/usr/bin/env python3
"""
Slide Switch State Detection
Read SPDT slide switch position for mode selection
"""

from gpiozero import Button, LED, PWMLED
import time
import signal
import sys

# GPIO Configuration
SWITCH_PIN = 17  # Slide switch input (center pin)
# For SPDT switch: Connect one throw to GND, leave other open
# For DPDT switch: Can use second pole for additional functions

# Optional outputs for state indication
LED1_PIN = 18    # LED for state 1
LED2_PIN = 27    # LED for state 2
RGB_RED = 22     # RGB LED pins
RGB_GREEN = 23
RGB_BLUE = 24

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_slide_switch():
    """Basic slide switch position detection"""
    print("\n=== Basic Slide Switch Detection ===")
    print("Slide switch changes between two states")
    print("Press Ctrl+C to exit")
    
    # Switch reads LOW when connected to GND, HIGH when open
    switch = Button(SWITCH_PIN, pull_up=True)
    
    # Track state
    last_state = switch.is_pressed
    
    # Initial state
    print(f"Initial position: {'Position 1' if last_state else 'Position 2'}")
    
    try:
        while True:
            current_state = switch.is_pressed
            
            if current_state != last_state:
                if current_state:
                    print("Switch moved to Position 1")
                else:
                    print("Switch moved to Position 2")
                last_state = current_state
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()

def switch_with_leds():
    """Control LEDs based on switch position"""
    print("\n=== Switch-Controlled LEDs ===")
    print("LEDs indicate current switch position")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    led1 = LED(LED1_PIN)
    led2 = LED(LED2_PIN)
    
    try:
        while True:
            if switch.is_pressed:
                led1.on()
                led2.off()
            else:
                led1.off()
                led2.on()
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()
        led1.close()
        led2.close()

def mode_selector():
    """Use slide switch to select operating modes"""
    print("\n=== Mode Selector ===")
    print("Switch position selects operating mode")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    
    # Define modes
    modes = {
        True: {"name": "Normal Mode", "speed": 1.0, "pattern": "steady"},
        False: {"name": "Turbo Mode", "speed": 0.1, "pattern": "blink"}
    }
    
    # Optional LED for visual feedback
    try:
        led = PWMLED(LED1_PIN)
        has_led = True
    except:
        has_led = False
        print("Note: No LED connected for visual feedback")
    
    last_mode = None
    
    try:
        while True:
            current_mode = switch.is_pressed
            
            if current_mode != last_mode:
                mode = modes[current_mode]
                print(f"\nMode: {mode['name']}")
                print(f"  Speed: {mode['speed']}")
                print(f"  Pattern: {mode['pattern']}")
                
                if has_led:
                    if mode['pattern'] == 'steady':
                        led.pulse(fade_in_time=mode['speed'], 
                                 fade_out_time=mode['speed'])
                    else:
                        led.blink(on_time=mode['speed'], 
                                 off_time=mode['speed'])
                
                last_mode = current_mode
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()
        if has_led:
            led.close()

def rgb_color_selector():
    """Use slide switch to select RGB LED colors"""
    print("\n=== RGB Color Selector ===")
    print("Switch position changes LED color")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    
    # Create RGB LED
    try:
        red = PWMLED(RGB_RED)
        green = PWMLED(RGB_GREEN)
        blue = PWMLED(RGB_BLUE)
        has_rgb = True
    except:
        has_rgb = False
        print("Note: RGB LED not connected")
    
    # Color presets
    colors = {
        True: {"name": "Warm White", "r": 1.0, "g": 0.8, "b": 0.6},
        False: {"name": "Cool Blue", "r": 0.2, "g": 0.4, "b": 1.0}
    }
    
    last_position = None
    
    try:
        while True:
            position = switch.is_pressed
            
            if position != last_position:
                color = colors[position]
                print(f"Color: {color['name']}")
                
                if has_rgb:
                    red.value = color['r']
                    green.value = color['g']
                    blue.value = color['b']
                
                last_position = position
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()
        if has_rgb:
            red.close()
            green.close()
            blue.close()

def state_machine_demo():
    """Implement a state machine controlled by slide switch"""
    print("\n=== State Machine Demo ===")
    print("Switch controls state transitions")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    
    # State machine definition
    class StateMachine:
        def __init__(self):
            self.state = "IDLE"
            self.counter = 0
            self.last_switch = switch.is_pressed
        
        def update(self):
            current_switch = switch.is_pressed
            
            # State transitions
            if self.state == "IDLE":
                if current_switch and not self.last_switch:
                    self.state = "RUNNING"
                    print("State: IDLE -> RUNNING")
            
            elif self.state == "RUNNING":
                self.counter += 1
                if self.counter >= 50:  # 5 seconds
                    self.state = "COMPLETE"
                    print("State: RUNNING -> COMPLETE")
                elif not current_switch and self.last_switch:
                    self.state = "PAUSED"
                    print("State: RUNNING -> PAUSED")
            
            elif self.state == "PAUSED":
                if current_switch and not self.last_switch:
                    self.state = "RUNNING"
                    print("State: PAUSED -> RUNNING")
            
            elif self.state == "COMPLETE":
                if not current_switch and self.last_switch:
                    self.state = "IDLE"
                    self.counter = 0
                    print("State: COMPLETE -> IDLE")
            
            self.last_switch = current_switch
        
        def display(self):
            if self.state == "RUNNING":
                print(f"\r{self.state}: {self.counter/10:.1f}s", end='')
            else:
                print(f"\r{self.state}" + " " * 20, end='')
    
    sm = StateMachine()
    
    try:
        while True:
            sm.update()
            sm.display()
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()

def multi_position_switch():
    """Simulate multi-position switch using timing"""
    print("\n=== Multi-Position Switch Simulation ===")
    print("Quick toggle simulates 3-position switch:")
    print("  Position 1: Steady state 1")
    print("  Position 2: Quick toggle (< 0.5s)")
    print("  Position 3: Steady state 2")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    
    position = 1
    last_change = 0
    toggle_count = 0
    
    try:
        while True:
            if switch.is_pressed:
                # Check for quick toggle
                current_time = time.time()
                if current_time - last_change < 0.5:
                    toggle_count += 1
                    if toggle_count >= 2:
                        position = 2
                        print("\nPosition 2 (Center) selected")
                else:
                    position = 1
                    toggle_count = 0
                    print("\nPosition 1 selected")
                
                last_change = current_time
            else:
                if time.time() - last_change > 0.5:
                    if position != 3:
                        position = 3
                        toggle_count = 0
                        print("\nPosition 3 selected")
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()

def power_save_mode():
    """Use slide switch for power saving mode"""
    print("\n=== Power Save Mode ===")
    print("Switch controls power consumption")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    
    # Simulated components
    components = {
        "CPU": {"normal": 100, "save": 40},
        "Display": {"normal": 50, "save": 10},
        "WiFi": {"normal": 30, "save": 0},
        "Sensors": {"normal": 20, "save": 5}
    }
    
    try:
        while True:
            power_save = not switch.is_pressed
            
            total_power = 0
            print(f"\n{'Power Save Mode' if power_save else 'Normal Mode'}")
            print("-" * 30)
            
            for component, power in components.items():
                mode = "save" if power_save else "normal"
                current = power[mode]
                total_power += current
                
                status = "OFF" if current == 0 else f"{current}mA"
                print(f"{component:10s}: {status:>6s}")
            
            print("-" * 30)
            print(f"Total:      {total_power:>6d}mA")
            
            # Update less frequently in power save mode
            sleep_time = 2.0 if power_save else 0.5
            time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()

def safety_interlock():
    """Safety interlock system with slide switch"""
    print("\n=== Safety Interlock System ===")
    print("Slide switch acts as safety enable")
    print("System can only operate when switch is in 'SAFE' position")
    print("Press Ctrl+C to exit")
    
    switch = Button(SWITCH_PIN, pull_up=True)
    
    # Simulated dangerous operation
    operation_requested = False
    operation_active = False
    
    print("\nCommands:")
    print("  s - Start operation")
    print("  x - Stop operation")
    
    try:
        import select
        
        while True:
            # Check for keyboard input
            if select.select([sys.stdin], [], [], 0.01)[0]:
                cmd = sys.stdin.read(1)
                if cmd == 's':
                    operation_requested = True
                elif cmd == 'x':
                    operation_requested = False
            
            # Safety logic
            safety_enabled = switch.is_pressed
            
            if operation_requested and safety_enabled:
                if not operation_active:
                    print("\nOperation STARTED (safety enabled)")
                    operation_active = True
            elif operation_active:
                if not safety_enabled:
                    print("\nOperation STOPPED (safety disabled)")
                elif not operation_requested:
                    print("\nOperation STOPPED (user request)")
                operation_active = False
            elif operation_requested and not safety_enabled:
                print("\nWARNING: Cannot start - safety disabled!")
                operation_requested = False
            
            # Status display
            status = f"\rSafety: {'ENABLED' if safety_enabled else 'DISABLED':8s} | "
            status += f"Operation: {'ACTIVE' if operation_active else 'STOPPED':8s}"
            print(status, end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        switch.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Slide Switch Examples")
    print("====================")
    print(f"Switch GPIO: {SWITCH_PIN}")
    print(f"LED1 GPIO: {LED1_PIN}")
    print(f"LED2 GPIO: {LED2_PIN}")
    print("\nNote: Connect switch center to GPIO, one side to GND")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic position detection")
        print("2. Switch-controlled LEDs")
        print("3. Mode selector")
        print("4. RGB color selector")
        print("5. State machine demo")
        print("6. Multi-position simulation")
        print("7. Power save mode")
        print("8. Safety interlock system")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_slide_switch()
        elif choice == '2':
            switch_with_leds()
        elif choice == '3':
            mode_selector()
        elif choice == '4':
            rgb_color_selector()
        elif choice == '5':
            state_machine_demo()
        elif choice == '6':
            multi_position_switch()
        elif choice == '7':
            power_save_mode()
        elif choice == '8':
            safety_interlock()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()