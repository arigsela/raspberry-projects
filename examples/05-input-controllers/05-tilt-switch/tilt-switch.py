#!/usr/bin/env python3
"""
Tilt Switch Orientation Detection
Detect device tilt and orientation changes using mercury/ball tilt switches
"""

from gpiozero import Button, LED, Buzzer
import time
import signal
import sys
import math

# GPIO Configuration
TILT_PIN = 17    # Tilt switch input
LED_PIN = 18     # Status LED
BUZZER_PIN = 22  # Alert buzzer (optional)

# For multi-axis detection (optional)
TILT_X_PIN = 17  # X-axis tilt
TILT_Y_PIN = 27  # Y-axis tilt

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_tilt_detection():
    """Basic tilt switch detection"""
    print("\n=== Basic Tilt Detection ===")
    print("Tilt the sensor to detect orientation changes")
    print("Press Ctrl+C to exit")
    
    # Tilt switch closes circuit when tilted
    tilt = Button(TILT_PIN, pull_up=True)
    
    # Track state
    last_state = tilt.is_pressed
    
    # Initial state
    print(f"Initial state: {'TILTED' if last_state else 'UPRIGHT'}")
    
    try:
        while True:
            current_state = tilt.is_pressed
            
            if current_state != last_state:
                if current_state:
                    print("Status: TILTED")
                else:
                    print("Status: UPRIGHT")
                last_state = current_state
            
            time.sleep(0.05)  # Faster polling for tilt detection
    
    except KeyboardInterrupt:
        pass
    finally:
        tilt.close()

def tilt_with_led():
    """Visual feedback with LED"""
    print("\n=== Tilt Detection with LED ===")
    print("LED indicates tilt status")
    print("Press Ctrl+C to exit")
    
    tilt = Button(TILT_PIN, pull_up=True)
    led = LED(LED_PIN)
    
    try:
        while True:
            if tilt.is_pressed:
                led.on()
            else:
                led.off()
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        tilt.close()
        led.close()

def orientation_monitor():
    """Monitor orientation with detailed feedback"""
    print("\n=== Orientation Monitor ===")
    print("Continuous orientation monitoring")
    print("Press Ctrl+C to exit")
    
    tilt = Button(TILT_PIN, pull_up=True)
    
    # Orientation tracking
    tilt_count = 0
    upright_time = 0
    tilted_time = 0
    last_change = time.time()
    
    try:
        while True:
            current_time = time.time()
            
            if tilt.is_pressed:
                tilted_time += 0.1
                status = "TILTED"
                symbol = "╲"  # Tilted line
            else:
                upright_time += 0.1
                status = "UPRIGHT"
                symbol = "│"  # Vertical line
            
            # Detect state changes
            if tilt.is_pressed != (tilted_time > upright_time):
                tilt_count += 1
                last_change = current_time
            
            # Display status
            print(f"\r{symbol} {status:8s} | "
                  f"Tilts: {tilt_count:3d} | "
                  f"Upright: {upright_time:5.1f}s | "
                  f"Tilted: {tilted_time:5.1f}s", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal tilts detected: {tilt_count}")
        print(f"Time upright: {upright_time:.1f}s ({upright_time/(upright_time+tilted_time)*100:.1f}%)")
        print(f"Time tilted: {tilted_time:.1f}s ({tilted_time/(upright_time+tilted_time)*100:.1f}%)")
    finally:
        tilt.close()

def security_alarm():
    """Tilt-based security alarm"""
    print("\n=== Security Alarm System ===")
    print("System will alert on movement/tilt")
    print("Press 'a' to arm, 'd' to disarm")
    print("Press Ctrl+C to exit")
    
    tilt = Button(TILT_PIN, pull_up=True)
    
    try:
        led = LED(LED_PIN)
        has_led = True
    except:
        has_led = False
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
        print("Note: No buzzer connected")
    
    armed = False
    alarm_active = False
    
    def trigger_alarm():
        nonlocal alarm_active
        if armed and not alarm_active:
            alarm_active = True
            print("\n⚠️  ALARM! Movement detected!")
            if has_buzzer:
                buzzer.beep(0.1, 0.1, n=5)
    
    # Set up tilt detection
    tilt.when_pressed = trigger_alarm
    
    try:
        import select
        
        while True:
            # Check for keyboard input
            if select.select([sys.stdin], [], [], 0.01)[0]:
                cmd = sys.stdin.read(1).lower()
                if cmd == 'a':
                    armed = True
                    alarm_active = False
                    print("\nSystem ARMED")
                    if has_led:
                        led.blink(0.5, 0.5)  # Slow blink when armed
                elif cmd == 'd':
                    armed = False
                    alarm_active = False
                    print("\nSystem DISARMED")
                    if has_led:
                        led.off()
                    if has_buzzer:
                        buzzer.off()
            
            # Status display
            status = "ARMED" if armed else "DISARMED"
            alarm = " - ALARM ACTIVE" if alarm_active else ""
            print(f"\rStatus: {status}{alarm}" + " " * 20, end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        tilt.close()
        if has_led:
            led.close()
        if has_buzzer:
            buzzer.close()

def motion_game():
    """Balance game using tilt detection"""
    print("\n=== Balance Game ===")
    print("Keep the device level for as long as possible!")
    print("Game starts in 3 seconds...")
    
    tilt = Button(TILT_PIN, pull_up=True)
    
    try:
        led = LED(LED_PIN)
        has_led = True
    except:
        has_led = False
    
    # Countdown
    for i in range(3, 0, -1):
        print(f"{i}...")
        if has_led:
            led.on()
            time.sleep(0.2)
            led.off()
            time.sleep(0.8)
        else:
            time.sleep(1)
    
    print("GO! Keep it level!")
    
    start_time = time.time()
    level_time = 0
    best_time = 0
    attempts = 0
    
    try:
        while True:
            if not tilt.is_pressed:  # Level/upright
                level_time = time.time() - start_time
                if has_led:
                    led.on()
                print(f"\rLevel time: {level_time:.1f}s", end='')
            else:  # Tilted
                if level_time > 0.5:  # Minimum time to count
                    attempts += 1
                    print(f"\n\nTilted! Score: {level_time:.1f} seconds")
                    if level_time > best_time:
                        best_time = level_time
                        print("★ New best time!")
                    print(f"Best: {best_time:.1f}s | Attempts: {attempts}")
                    print("\nTry again in 3 seconds...")
                    time.sleep(3)
                    print("GO!")
                if has_led:
                    led.off()
                start_time = time.time()
                level_time = 0
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nGame Over!")
        print(f"Best time: {best_time:.1f} seconds")
        print(f"Total attempts: {attempts}")
    finally:
        tilt.close()
        if has_led:
            led.close()

def dual_axis_detection():
    """Detect tilt in two axes"""
    print("\n=== Dual-Axis Tilt Detection ===")
    print("Detects tilt in X and Y directions")
    print("Press Ctrl+C to exit")
    
    tilt_x = Button(TILT_X_PIN, pull_up=True)
    tilt_y = Button(TILT_Y_PIN, pull_up=True)
    
    # Visual representation
    def get_position_char(x_tilt, y_tilt):
        if not x_tilt and not y_tilt:
            return "┼"  # Center
        elif x_tilt and not y_tilt:
            return "→"  # Right
        elif not x_tilt and y_tilt:
            return "↑"  # Up
        elif x_tilt and y_tilt:
            return "↗"  # Up-right
        # Add more combinations as needed
    
    try:
        while True:
            x_tilted = tilt_x.is_pressed
            y_tilted = tilt_y.is_pressed
            
            # Determine orientation
            if not x_tilted and not y_tilted:
                orientation = "CENTER"
            elif x_tilted and not y_tilted:
                orientation = "TILTED RIGHT"
            elif not x_tilted and y_tilted:
                orientation = "TILTED FORWARD"
            elif x_tilted and y_tilted:
                orientation = "TILTED CORNER"
            
            # Display with visual
            char = get_position_char(x_tilted, y_tilted)
            print(f"\r{char}  {orientation:15s} | X: {'TILT' if x_tilted else 'OK  '} | Y: {'TILT' if y_tilted else 'OK  '}", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        tilt_x.close()
        tilt_y.close()

def vibration_detector():
    """Detect vibration/movement patterns"""
    print("\n=== Vibration Detector ===")
    print("Detects vibration intensity and patterns")
    print("Press Ctrl+C to exit")
    
    tilt = Button(TILT_PIN, pull_up=True, bounce_time=0.001)  # Very fast response
    
    # Vibration tracking
    vibration_count = 0
    last_sample = time.time()
    samples = []
    
    def detect_vibration():
        nonlocal vibration_count
        vibration_count += 1
    
    tilt.when_pressed = detect_vibration
    tilt.when_released = detect_vibration
    
    try:
        while True:
            current_time = time.time()
            
            # Sample every second
            if current_time - last_sample >= 1.0:
                samples.append(vibration_count)
                if len(samples) > 10:  # Keep last 10 samples
                    samples.pop(0)
                
                # Calculate intensity
                avg_vibration = sum(samples) / len(samples)
                
                # Determine level
                if vibration_count == 0:
                    level = "STABLE"
                    bar = "─" * 10
                elif vibration_count < 5:
                    level = "LOW"
                    bar = "█" * 2 + "─" * 8
                elif vibration_count < 15:
                    level = "MEDIUM"
                    bar = "█" * 5 + "─" * 5
                elif vibration_count < 30:
                    level = "HIGH"
                    bar = "█" * 8 + "─" * 2
                else:
                    level = "EXTREME"
                    bar = "█" * 10
                
                print(f"\rVibration: {level:8s} [{bar}] Count: {vibration_count:3d}/s | Avg: {avg_vibration:5.1f}", end='')
                
                vibration_count = 0
                last_sample = current_time
            
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\nVibration monitoring stopped")
    finally:
        tilt.close()

def package_drop_detector():
    """Detect if package has been dropped or mishandled"""
    print("\n=== Package Drop Detector ===")
    print("Monitors for drops and rough handling")
    print("Press 'r' to reset, Ctrl+C to exit")
    
    tilt = Button(TILT_PIN, pull_up=True, bounce_time=0.01)
    
    # Event tracking
    drop_count = 0
    tilt_events = 0
    start_time = time.time()
    last_event = None
    
    def handle_tilt():
        nonlocal tilt_events, drop_count, last_event
        current_time = time.time()
        
        tilt_events += 1
        
        # Rapid tilts indicate drop
        if last_event and (current_time - last_event) < 0.1:
            drop_count += 1
            print(f"\n⚠️  DROP DETECTED! Total drops: {drop_count}")
        
        last_event = current_time
    
    tilt.when_pressed = handle_tilt
    
    try:
        import select
        
        while True:
            # Check for reset command
            if select.select([sys.stdin], [], [], 0.01)[0]:
                cmd = sys.stdin.read(1).lower()
                if cmd == 'r':
                    drop_count = 0
                    tilt_events = 0
                    start_time = time.time()
                    print("\nCounters reset")
            
            # Calculate time
            elapsed = time.time() - start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            
            # Display status
            print(f"\rMonitoring: {hours:02d}:{minutes:02d} | "
                  f"Tilts: {tilt_events:3d} | "
                  f"Drops: {drop_count:2d}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring complete")
        print(f"Total monitoring time: {elapsed/60:.1f} minutes")
        print(f"Total tilt events: {tilt_events}")
        print(f"Detected drops: {drop_count}")
    finally:
        tilt.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Tilt Switch Examples")
    print("===================")
    print(f"Tilt Switch GPIO: {TILT_PIN}")
    print(f"LED GPIO: {LED_PIN} (optional)")
    print(f"Buzzer GPIO: {BUZZER_PIN} (optional)")
    print("\nNote: Tilt switch connects GPIO to GND when tilted")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic tilt detection")
        print("2. Tilt with LED indicator")
        print("3. Orientation monitor")
        print("4. Security alarm system")
        print("5. Balance game")
        print("6. Dual-axis detection")
        print("7. Vibration detector")
        print("8. Package drop detector")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_tilt_detection()
        elif choice == '2':
            tilt_with_led()
        elif choice == '3':
            orientation_monitor()
        elif choice == '4':
            security_alarm()
        elif choice == '5':
            motion_game()
        elif choice == '6':
            dual_axis_detection()
        elif choice == '7':
            vibration_detector()
        elif choice == '8':
            package_drop_detector()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()