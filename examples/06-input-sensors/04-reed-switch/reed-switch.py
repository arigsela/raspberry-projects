#!/usr/bin/env python3
"""
Reed Switch Magnetic Field Detection
Detect magnetic fields for security, position sensing, and proximity detection
"""

from gpiozero import Button, LED, Buzzer
import time
import signal
import sys
from datetime import datetime

# GPIO Configuration
REED_PIN = 17    # Reed switch input
LED_PIN = 18     # Status LED
BUZZER_PIN = 22  # Alert buzzer

# For multiple reed switches (door/window system)
REED_PINS = {
    "front_door": 17,
    "back_door": 27,
    "window_1": 23,
    "window_2": 24
}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_reed_detection():
    """Basic magnetic field detection"""
    print("\n=== Basic Reed Switch Detection ===")
    print("Bring magnet close to detect")
    print("Press Ctrl+C to exit")
    
    # Reed switch closes when magnet is near
    reed = Button(REED_PIN, pull_up=True)
    
    # Track state
    last_state = reed.is_pressed
    
    # Initial state
    print(f"Initial state: {'CLOSED (Magnet detected)' if last_state else 'OPEN (No magnet)'}")
    
    try:
        while True:
            current_state = reed.is_pressed
            
            if current_state != last_state:
                if current_state:
                    print("Reed Switch: CLOSED - Magnet detected")
                else:
                    print("Reed Switch: OPEN - Magnet removed")
                last_state = current_state
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        reed.close()

def door_sensor():
    """Door/window security sensor"""
    print("\n=== Door/Window Sensor ===")
    print("Simulates door sensor operation")
    print("Press Ctrl+C to exit")
    
    reed = Button(REED_PIN, pull_up=True)
    led = LED(LED_PIN)
    
    # Door is closed when magnet is detected
    door_open_count = 0
    last_opened = None
    
    def door_opened():
        nonlocal door_open_count, last_opened
        door_open_count += 1
        last_opened = datetime.now()
        print(f"\n⚠️  DOOR OPENED at {last_opened.strftime('%H:%M:%S')}")
        led.on()
    
    def door_closed():
        if last_opened:
            duration = (datetime.now() - last_opened).total_seconds()
            print(f"\n✓ Door CLOSED (was open for {duration:.1f}s)")
        else:
            print("\n✓ Door CLOSED")
        led.off()
    
    # Set up event handlers
    reed.when_released = door_opened  # Magnet moved away
    reed.when_pressed = door_closed   # Magnet detected
    
    # Initial state
    if reed.is_pressed:
        print("Door is currently: CLOSED")
        led.off()
    else:
        print("Door is currently: OPEN")
        led.on()
    
    try:
        print("\nMonitoring door status...")
        signal.pause()
    
    except KeyboardInterrupt:
        print(f"\n\nTotal door openings: {door_open_count}")
    finally:
        reed.close()
        led.close()

def security_system():
    """Complete security system with multiple sensors"""
    print("\n=== Security System ===")
    print("Multi-zone security monitoring")
    print("Commands: 'a' = arm, 'd' = disarm, 's' = status")
    print("Press Ctrl+C to exit")
    
    # Create sensors for each zone
    sensors = {}
    for name, pin in REED_PINS.items():
        try:
            sensors[name] = Button(pin, pull_up=True)
            print(f"Zone '{name}' on GPIO{pin}: Active")
        except:
            print(f"Zone '{name}' on GPIO{pin}: Not connected")
    
    if not sensors:
        print("No sensors connected!")
        return
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
    
    # System state
    armed = False
    alarm_active = False
    breached_zones = set()
    
    def check_breach(zone_name):
        if armed and not sensors[zone_name].is_pressed:
            breached_zones.add(zone_name)
            if not alarm_active:
                trigger_alarm()
    
    def trigger_alarm():
        nonlocal alarm_active
        alarm_active = True
        print(f"\n🚨 ALARM! Breach detected in: {', '.join(breached_zones)}")
        if has_buzzer:
            buzzer.beep(0.2, 0.2)
    
    # Monitor all zones
    for name in sensors:
        sensors[name].when_released = lambda n=name: check_breach(n)
    
    try:
        import select
        
        while True:
            # Check for commands
            if select.select([sys.stdin], [], [], 0.01)[0]:
                cmd = sys.stdin.read(1).lower()
                
                if cmd == 'a':
                    # Check all zones before arming
                    open_zones = [name for name, sensor in sensors.items() 
                                 if not sensor.is_pressed]
                    
                    if open_zones:
                        print(f"\nCannot arm - zones open: {', '.join(open_zones)}")
                    else:
                        armed = True
                        alarm_active = False
                        breached_zones.clear()
                        print("\nSystem ARMED")
                
                elif cmd == 'd':
                    armed = False
                    alarm_active = False
                    breached_zones.clear()
                    if has_buzzer:
                        buzzer.off()
                    print("\nSystem DISARMED")
                
                elif cmd == 's':
                    print("\n--- Zone Status ---")
                    for name, sensor in sensors.items():
                        status = "Secure" if sensor.is_pressed else "OPEN"
                        print(f"{name:12s}: {status}")
                    print(f"\nSystem: {'ARMED' if armed else 'DISARMED'}")
                    if alarm_active:
                        print(f"ALARM ACTIVE - Breached: {', '.join(breached_zones)}")
            
            # Status line
            status = "ARMED" if armed else "DISARMED"
            alarm = " - ALARM!" if alarm_active else ""
            zones = len([s for s in sensors.values() if s.is_pressed])
            print(f"\rSystem: {status}{alarm} | Secure zones: {zones}/{len(sensors)}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        for sensor in sensors.values():
            sensor.close()
        if has_buzzer:
            buzzer.close()

def proximity_counter():
    """Count objects passing by using reed switch"""
    print("\n=== Proximity Counter ===")
    print("Counts magnetic objects passing sensor")
    print("Press 'r' to reset, Ctrl+C to exit")
    
    reed = Button(REED_PIN, pull_up=True, bounce_time=0.1)
    
    # Counting variables
    count = 0
    last_detect = None
    hourly_counts = {}
    
    def object_detected():
        nonlocal count, last_detect
        count += 1
        last_detect = datetime.now()
        
        # Track hourly
        hour = last_detect.strftime("%H:00")
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        print(f"\nObject #{count} detected at {last_detect.strftime('%H:%M:%S')}")
    
    reed.when_pressed = object_detected
    
    try:
        import select
        start_time = datetime.now()
        
        while True:
            # Check for reset
            if select.select([sys.stdin], [], [], 0.01)[0]:
                if sys.stdin.read(1).lower() == 'r':
                    count = 0
                    hourly_counts.clear()
                    start_time = datetime.now()
                    print("\nCounter reset")
            
            # Calculate rate
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = (count / elapsed * 3600) if elapsed > 0 else 0
            
            # Display status
            print(f"\rCount: {count:4d} | Rate: {rate:5.1f}/hour | "
                  f"Last: {last_detect.strftime('%H:%M:%S') if last_detect else 'None':8s}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n--- Summary ---")
        print(f"Total count: {count}")
        print(f"Duration: {elapsed/60:.1f} minutes")
        print(f"Average rate: {rate:.1f} per hour")
        if hourly_counts:
            print("\nHourly breakdown:")
            for hour, cnt in sorted(hourly_counts.items()):
                print(f"  {hour}: {cnt} detections")
    finally:
        reed.close()

def position_encoder():
    """Linear position encoding with multiple reed switches"""
    print("\n=== Position Encoder ===")
    print("Simulates linear position detection")
    print("Press Ctrl+C to exit")
    
    # Define position sensors (simulate 4 positions)
    positions = {
        17: "Position 1 (0cm)",
        27: "Position 2 (10cm)",
        23: "Position 3 (20cm)",
        24: "Position 4 (30cm)"
    }
    
    sensors = {}
    for pin, name in positions.items():
        try:
            sensors[pin] = Button(pin, pull_up=True)
            print(f"{name}: Connected")
        except:
            print(f"{name}: Not available")
    
    if not sensors:
        print("No position sensors available!")
        return
    
    current_position = None
    position_history = []
    
    try:
        while True:
            # Check which sensor is active
            active_position = None
            for pin, sensor in sensors.items():
                if sensor.is_pressed:
                    active_position = positions[pin]
                    break
            
            # Detect position changes
            if active_position != current_position:
                current_position = active_position
                position_history.append((datetime.now(), current_position))
                
                if current_position:
                    print(f"\nMoved to: {current_position}")
                else:
                    print("\nNo position detected (between sensors)")
                
                # Show movement pattern
                if len(position_history) > 1:
                    prev_pos = position_history[-2][1]
                    if prev_pos and current_position:
                        # Extract position numbers
                        prev_num = int(prev_pos.split()[1])
                        curr_num = int(current_position.split()[1])
                        direction = "Forward" if curr_num > prev_num else "Backward"
                        print(f"Direction: {direction}")
            
            # Display current status
            pos_str = current_position if current_position else "Unknown"
            print(f"\rPosition: {pos_str:20s}", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\n--- Movement History ---")
        for timestamp, position in position_history[-10:]:
            print(f"{timestamp.strftime('%H:%M:%S')}: {position}")
    finally:
        for sensor in sensors.values():
            sensor.close()

def rpm_measurement():
    """Measure rotation speed using reed switch"""
    print("\n=== RPM Measurement ===")
    print("Measures rotation speed with magnetic marker")
    print("Press Ctrl+C to exit")
    
    reed = Button(REED_PIN, pull_up=True, bounce_time=0.01)
    
    # Rotation tracking
    pulse_times = []
    rpm = 0
    max_rpm = 0
    
    def pulse_detected():
        nonlocal rpm, max_rpm
        current_time = time.time()
        pulse_times.append(current_time)
        
        # Keep only recent pulses (last 2 seconds)
        pulse_times[:] = [t for t in pulse_times if current_time - t < 2.0]
        
        # Calculate RPM from recent pulses
        if len(pulse_times) >= 2:
            # Time between first and last pulse
            duration = pulse_times[-1] - pulse_times[0]
            if duration > 0:
                # RPM = (pulses - 1) / duration * 60
                rpm = (len(pulse_times) - 1) / duration * 60
                max_rpm = max(max_rpm, rpm)
    
    reed.when_pressed = pulse_detected
    
    try:
        print("Rotate object with magnetic marker...")
        
        while True:
            # Create visual RPM bar
            bar_length = int(rpm / 10)  # Scale for display
            bar = '█' * min(bar_length, 50) + '░' * (50 - min(bar_length, 50))
            
            # Display
            print(f"\rRPM: {rpm:6.1f} [{bar}] Max: {max_rpm:6.1f}", end='')
            
            # Decay RPM if no recent pulses
            if pulse_times and time.time() - pulse_times[-1] > 0.5:
                rpm *= 0.9  # Gradual decay
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nMaximum RPM recorded: {max_rpm:.1f}")
    finally:
        reed.close()

def liquid_level_sensor():
    """Simulate liquid level detection with float and reed switch"""
    print("\n=== Liquid Level Sensor ===")
    print("Simulates tank level monitoring")
    print("Press Ctrl+C to exit")
    
    # Multiple reed switches at different levels
    level_sensors = {
        17: {"name": "LOW", "percent": 25, "alert": True},
        27: {"name": "MEDIUM", "percent": 50, "alert": False},
        23: {"name": "HIGH", "percent": 75, "alert": False},
        24: {"name": "FULL", "percent": 100, "alert": True}
    }
    
    sensors = {}
    for pin, info in level_sensors.items():
        try:
            sensors[pin] = Button(pin, pull_up=True)
        except:
            pass
    
    if not sensors:
        print("No level sensors connected! Using single sensor mode.")
        sensors[REED_PIN] = Button(REED_PIN, pull_up=True)
        single_mode = True
    else:
        single_mode = False
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
    
    alert_active = False
    
    try:
        while True:
            if single_mode:
                # Single sensor mode - simple full/empty
                if sensors[REED_PIN].is_pressed:
                    level = 100
                    status = "FULL"
                else:
                    level = 0
                    status = "EMPTY"
                    if not alert_active and has_buzzer:
                        alert_active = True
                        buzzer.beep(0.5, 0.5, n=3)
                        print("\n⚠️  Low level alert!")
            else:
                # Multi-sensor mode
                level = 0
                status = "EMPTY"
                
                for pin, sensor in sensors.items():
                    if sensor.is_pressed:
                        info = level_sensors[pin]
                        level = info["percent"]
                        status = info["name"]
                        
                        # Check for alerts
                        if info["alert"] and not alert_active:
                            alert_active = True
                            if has_buzzer:
                                buzzer.beep(0.2, 0.2, n=2)
                            if info["name"] == "LOW":
                                print("\n⚠️  Low level warning!")
                            elif info["name"] == "FULL":
                                print("\n⚠️  Tank full warning!")
            
            # Reset alert when level changes
            if level > 25 and level < 100:
                alert_active = False
                if has_buzzer:
                    buzzer.off()
            
            # Visual display
            bar_length = int(level / 2)
            bar = '█' * bar_length + '░' * (50 - bar_length)
            
            print(f"\rLevel: {status:6s} [{bar}] {level:3d}%", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        for sensor in sensors.values():
            sensor.close()
        if has_buzzer:
            buzzer.close()

def magnetic_field_strength():
    """Estimate magnetic field strength by detection frequency"""
    print("\n=== Magnetic Field Strength ===")
    print("Estimates field strength by switch activation")
    print("Move magnet closer/farther to test")
    print("Press Ctrl+C to exit")
    
    reed = Button(REED_PIN, pull_up=True, bounce_time=0.001)
    
    # Sampling parameters
    sample_window = 0.1  # 100ms windows
    samples = []
    max_strength = 0
    
    try:
        while True:
            # Count activations in sample window
            activations = 0
            start_time = time.time()
            
            while time.time() - start_time < sample_window:
                if reed.is_pressed:
                    activations += 1
                    # Wait for release
                    while reed.is_pressed and time.time() - start_time < sample_window:
                        time.sleep(0.001)
            
            # Estimate strength (0-100 scale)
            strength = min(100, activations * 10)
            samples.append(strength)
            if len(samples) > 10:
                samples.pop(0)
            
            # Average for stability
            avg_strength = sum(samples) / len(samples)
            max_strength = max(max_strength, avg_strength)
            
            # Determine field level
            if avg_strength == 0:
                level = "No field"
                bar_char = "░"
            elif avg_strength < 20:
                level = "Weak"
                bar_char = "▒"
            elif avg_strength < 50:
                level = "Moderate"
                bar_char = "▓"
            elif avg_strength < 80:
                level = "Strong"
                bar_char = "█"
            else:
                level = "Very strong"
                bar_char = "█"
            
            # Visual display
            bar_length = int(avg_strength / 2)
            bar = bar_char * bar_length + '░' * (50 - bar_length)
            
            print(f"\rField: {level:11s} [{bar}] {avg_strength:3.0f}% (Max: {max_strength:3.0f}%)", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nMaximum field strength: {max_strength:.0f}%")
    finally:
        reed.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Reed Switch Examples")
    print("===================")
    print(f"Reed Switch GPIO: {REED_PIN}")
    print(f"LED GPIO: {LED_PIN} (optional)")
    print(f"Buzzer GPIO: {BUZZER_PIN} (optional)")
    print("\nNote: Reed switch closes circuit when magnet is near")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic magnetic detection")
        print("2. Door/window sensor")
        print("3. Security system")
        print("4. Proximity counter")
        print("5. Position encoder")
        print("6. RPM measurement")
        print("7. Liquid level sensor")
        print("8. Magnetic field strength")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_reed_detection()
        elif choice == '2':
            door_sensor()
        elif choice == '3':
            security_system()
        elif choice == '4':
            proximity_counter()
        elif choice == '5':
            position_encoder()
        elif choice == '6':
            rpm_measurement()
        elif choice == '7':
            liquid_level_sensor()
        elif choice == '8':
            magnetic_field_strength()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()