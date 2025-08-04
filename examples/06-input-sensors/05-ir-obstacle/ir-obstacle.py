#!/usr/bin/env python3
"""
IR Obstacle Sensor Detection
Detect objects and measure proximity using infrared reflection
"""

from gpiozero import Button, LED, PWMLED, Buzzer
import time
import signal
import sys
from datetime import datetime
import statistics

# GPIO Configuration
IR_SENSOR_PIN = 17   # IR sensor output
LED_PIN = 18         # Status LED
BUZZER_PIN = 22      # Alert buzzer

# For multiple sensors (robot/security)
IR_SENSORS = {
    "front": 17,
    "left": 27,
    "right": 23,
    "back": 24
}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_obstacle_detection():
    """Basic IR obstacle detection"""
    print("\n=== Basic IR Obstacle Detection ===")
    print("Place objects in front of sensor")
    print("Detection range: typically 2-30cm")
    print("Press Ctrl+C to exit")
    
    # IR sensor outputs LOW when obstacle detected
    ir_sensor = Button(IR_SENSOR_PIN, pull_up=True)
    
    # Track state
    last_state = ir_sensor.is_pressed
    detection_count = 0
    
    # Initial state
    print(f"Initial state: {'CLEAR' if last_state else 'OBSTACLE DETECTED'}")
    
    try:
        while True:
            current_state = ir_sensor.is_pressed
            
            if current_state != last_state:
                if not current_state:  # Obstacle detected (LOW)
                    detection_count += 1
                    print(f"OBSTACLE DETECTED (Count: {detection_count})")
                else:  # Clear (HIGH)
                    print("Path CLEAR")
                last_state = current_state
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal detections: {detection_count}")
    finally:
        ir_sensor.close()

def proximity_indicator():
    """Visual proximity indication with LED"""
    print("\n=== Proximity Indicator ===")
    print("LED brightness indicates proximity")
    print("Press Ctrl+C to exit")
    
    ir_sensor = Button(IR_SENSOR_PIN, pull_up=True)
    
    try:
        led = PWMLED(LED_PIN)
        has_led = True
    except:
        has_led = False
        print("Note: No LED connected")
    
    # Simulate proximity with pulse counting
    proximity_samples = []
    
    try:
        while True:
            # Sample detection frequency
            detections = 0
            sample_start = time.time()
            
            while time.time() - sample_start < 0.1:  # 100ms sample
                if not ir_sensor.is_pressed:
                    detections += 1
                time.sleep(0.001)
            
            # Update samples
            proximity_samples.append(detections)
            if len(proximity_samples) > 10:
                proximity_samples.pop(0)
            
            # Calculate average proximity
            avg_proximity = sum(proximity_samples) / len(proximity_samples)
            
            # Map to LED brightness (more detections = closer)
            if has_led:
                if avg_proximity == 0:
                    led.off()
                else:
                    brightness = min(1.0, avg_proximity / 50)
                    led.value = brightness
            
            # Display proximity level
            if avg_proximity == 0:
                level = "No object"
                bar = " " * 20
            elif avg_proximity < 10:
                level = "Far"
                bar = "█" * 5 + " " * 15
            elif avg_proximity < 30:
                level = "Medium"
                bar = "█" * 10 + " " * 10
            elif avg_proximity < 50:
                level = "Near"
                bar = "█" * 15 + " " * 5
            else:
                level = "Very near"
                bar = "█" * 20
            
            print(f"\rProximity: {level:10s} [{bar}]", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        ir_sensor.close()
        if has_led:
            led.close()

def line_follower():
    """Line following robot simulation"""
    print("\n=== Line Follower Simulation ===")
    print("Simulates line detection for robot")
    print("Black surface = Line detected")
    print("Press Ctrl+C to exit")
    
    # Typically uses 2-5 IR sensors
    left_sensor = Button(17, pull_up=True)
    right_sensor = Button(27, pull_up=True)
    
    # Motor simulation
    motor_speed = {"left": 50, "right": 50}
    
    try:
        while True:
            # Read sensors (LOW = black line detected)
            left_detect = not left_sensor.is_pressed
            right_detect = not right_sensor.is_pressed
            
            # Line following logic
            if left_detect and right_detect:
                # Both sensors on line - go straight
                motor_speed["left"] = 50
                motor_speed["right"] = 50
                direction = "STRAIGHT"
                symbol = "↑"
            elif left_detect and not right_detect:
                # Left sensor on line - turn left
                motor_speed["left"] = 20
                motor_speed["right"] = 50
                direction = "LEFT"
                symbol = "←"
            elif not left_detect and right_detect:
                # Right sensor on line - turn right  
                motor_speed["left"] = 50
                motor_speed["right"] = 20
                direction = "RIGHT"
                symbol = "→"
            else:
                # No line detected - search mode
                motor_speed["left"] = 30
                motor_speed["right"] = -30
                direction = "SEARCHING"
                symbol = "↻"
            
            # Display status
            left_status = "█" if left_detect else "░"
            right_status = "█" if right_detect else "░"
            
            print(f"\r{symbol} {direction:10s} | "
                  f"Sensors: [{left_status}] [{right_status}] | "
                  f"Motors: L={motor_speed['left']:3d}% R={motor_speed['right']:3d}%", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        left_sensor.close()
        right_sensor.close()

def obstacle_avoidance_robot():
    """Robot obstacle avoidance system"""
    print("\n=== Obstacle Avoidance Robot ===")
    print("Simulates robot navigation with obstacle detection")
    print("Press Ctrl+C to exit")
    
    # Initialize sensors
    sensors = {}
    for name, pin in IR_SENSORS.items():
        try:
            sensors[name] = Button(pin, pull_up=True)
            print(f"Sensor '{name}' on GPIO{pin}: Active")
        except:
            print(f"Sensor '{name}' on GPIO{pin}: Not connected")
    
    if not sensors:
        print("No sensors available!")
        return
    
    # Robot state
    robot_state = "MOVING"
    direction = "FORWARD"
    speed = 50
    
    try:
        while True:
            # Check all sensors
            obstacles = {}
            for name, sensor in sensors.items():
                obstacles[name] = not sensor.is_pressed
            
            # Decision logic
            if obstacles.get("front", False):
                if not obstacles.get("left", False):
                    direction = "LEFT"
                    robot_state = "TURNING"
                elif not obstacles.get("right", False):
                    direction = "RIGHT"
                    robot_state = "TURNING"
                else:
                    direction = "REVERSE"
                    robot_state = "BACKING"
                speed = 30
            elif obstacles.get("left", False) and obstacles.get("right", False):
                direction = "FORWARD"
                robot_state = "CORRIDOR"
                speed = 30
            elif obstacles.get("left", False):
                direction = "RIGHT-BIAS"
                robot_state = "AVOIDING"
                speed = 40
            elif obstacles.get("right", False):
                direction = "LEFT-BIAS"
                robot_state = "AVOIDING"
                speed = 40
            else:
                direction = "FORWARD"
                robot_state = "MOVING"
                speed = 50
            
            # Visual representation
            visual = ""
            visual += "L" if obstacles.get("left", False) else " "
            visual += "F" if obstacles.get("front", False) else " "
            visual += "R" if obstacles.get("right", False) else " "
            
            # Direction arrow
            arrows = {
                "FORWARD": "↑",
                "LEFT": "←",
                "RIGHT": "→",
                "REVERSE": "↓",
                "LEFT-BIAS": "↖",
                "RIGHT-BIAS": "↗"
            }
            
            print(f"\r{arrows.get(direction, '?')} State: {robot_state:10s} | "
                  f"Obstacles: [{visual}] | "
                  f"Direction: {direction:10s} | "
                  f"Speed: {speed}%", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        for sensor in sensors.values():
            sensor.close()

def parking_sensor():
    """Car parking sensor simulation"""
    print("\n=== Parking Sensor ===")
    print("Simulates car parking assistance")
    print("Move object closer/farther")
    print("Press Ctrl+C to exit")
    
    ir_sensor = Button(IR_SENSOR_PIN, pull_up=True)
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
        print("Note: No buzzer connected")
    
    # Distance zones (simulated)
    last_beep = 0
    
    try:
        while True:
            if not ir_sensor.is_pressed:  # Object detected
                # Simulate distance with random variation
                import random
                base_distance = 30
                distance = base_distance + random.randint(-5, 5)
                
                # Determine warning level
                if distance > 50:
                    zone = "Safe"
                    beep_interval = 0  # No beep
                    bar_color = "█"  # Full block
                    bar_length = 20
                elif distance > 30:
                    zone = "Caution"
                    beep_interval = 1.0
                    bar_color = "▓"  # Medium shade
                    bar_length = 15
                elif distance > 15:
                    zone = "Warning"
                    beep_interval = 0.5
                    bar_color = "▒"  # Light shade
                    bar_length = 10
                else:
                    zone = "STOP!"
                    beep_interval = 0.1
                    bar_color = "░"  # Very light
                    bar_length = 5
                
                # Beep control
                current_time = time.time()
                if has_buzzer and beep_interval > 0:
                    if current_time - last_beep > beep_interval:
                        buzzer.beep(0.1, 0.1, n=1)
                        last_beep = current_time
                
                # Display
                bar = bar_color * bar_length + " " * (20 - bar_length)
                print(f"\r{zone:8s} [{bar}] Distance: ~{distance}cm", end='')
                
            else:
                # No obstacle
                if has_buzzer:
                    buzzer.off()
                print(f"\rClear    [" + " " * 20 + "] No obstacle    ", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        ir_sensor.close()
        if has_buzzer:
            buzzer.close()

def hand_gesture_detection():
    """Simple hand gesture detection"""
    print("\n=== Hand Gesture Detection ===")
    print("Wave hand over sensor for gesture detection")
    print("Press Ctrl+C to exit")
    
    ir_sensor = Button(IR_SENSOR_PIN, pull_up=True)
    
    # Gesture tracking
    gesture_buffer = []
    last_change = 0
    
    try:
        while True:
            detected = not ir_sensor.is_pressed
            current_time = time.time()
            
            # Record state changes
            if len(gesture_buffer) == 0 or gesture_buffer[-1][1] != detected:
                gesture_buffer.append((current_time, detected))
                
                # Keep only recent events (last 2 seconds)
                gesture_buffer = [(t, s) for t, s in gesture_buffer 
                                 if current_time - t < 2.0]
                
                # Analyze gesture
                if len(gesture_buffer) >= 4:
                    # Count transitions
                    transitions = len(gesture_buffer) - 1
                    duration = gesture_buffer[-1][0] - gesture_buffer[0][0]
                    
                    if transitions >= 6 and duration < 2.0:
                        print("\nGesture detected: WAVE")
                        gesture_buffer.clear()
                    elif transitions == 2 and duration < 0.5:
                        print("\nGesture detected: QUICK SWIPE")
                        gesture_buffer.clear()
                    elif transitions == 1 and detected and duration > 1.0:
                        print("\nGesture detected: HOLD")
                        gesture_buffer.clear()
            
            # Status display
            status = "Detecting" if detected else "Ready"
            activity = len([1 for t, _ in gesture_buffer if current_time - t < 0.5])
            activity_bar = "█" * min(activity, 10) + "░" * (10 - min(activity, 10))
            
            print(f"\rStatus: {status:10s} | Activity: [{activity_bar}]", end='')
            
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        pass
    finally:
        ir_sensor.close()

def object_counter():
    """Count objects passing sensor"""
    print("\n=== Object Counter ===")
    print("Counts objects passing in front of sensor")
    print("Press 'r' to reset, Ctrl+C to exit")
    
    ir_sensor = Button(IR_SENSOR_PIN, pull_up=True, bounce_time=0.2)
    
    # Counting variables
    count = 0
    last_count_time = None
    hourly_counts = {}
    start_time = datetime.now()
    
    def object_passed():
        nonlocal count, last_count_time
        count += 1
        last_count_time = datetime.now()
        
        # Track hourly
        hour = last_count_time.strftime("%H:00")
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        print(f"\nObject #{count} at {last_count_time.strftime('%H:%M:%S')}")
    
    # Trigger on object leaving (rising edge)
    ir_sensor.when_released = object_passed
    
    try:
        import select
        
        while True:
            # Check for reset
            if select.select([sys.stdin], [], [], 0.01)[0]:
                if sys.stdin.read(1).lower() == 'r':
                    count = 0
                    hourly_counts.clear()
                    start_time = datetime.now()
                    print("\nCounter reset")
            
            # Calculate statistics
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = (count / elapsed * 3600) if elapsed > 0 else 0
            
            # Display
            status = "Blocked" if not ir_sensor.is_pressed else "Clear"
            print(f"\rCount: {count:4d} | Rate: {rate:5.1f}/hr | "
                  f"Status: {status:7s} | "
                  f"Last: {last_count_time.strftime('%H:%M:%S') if last_count_time else 'None':8s}", 
                  end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n--- Summary ---")
        print(f"Total count: {count}")
        print(f"Duration: {elapsed/60:.1f} minutes")
        print(f"Average rate: {rate:.1f} per hour")
        if hourly_counts:
            print("\nHourly breakdown:")
            for hour, cnt in sorted(hourly_counts.items()):
                print(f"  {hour}: {cnt} objects")
    finally:
        ir_sensor.close()

def security_beam():
    """Invisible security beam simulation"""
    print("\n=== Security Beam ===")
    print("Detects beam interruption for security")
    print("Commands: 'a' = arm, 'd' = disarm")
    print("Press Ctrl+C to exit")
    
    ir_sensor = Button(IR_SENSOR_PIN, pull_up=True)
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
    
    try:
        led = LED(LED_PIN)
        has_led = True
    except:
        has_led = False
    
    # Security state
    armed = False
    alarm_active = False
    breach_count = 0
    breach_log = []
    
    def beam_broken():
        nonlocal alarm_active, breach_count
        if armed and not alarm_active:
            alarm_active = True
            breach_count += 1
            breach_time = datetime.now()
            breach_log.append(breach_time)
            
            print(f"\n🚨 SECURITY BREACH! Time: {breach_time.strftime('%H:%M:%S')}")
            
            if has_buzzer:
                buzzer.beep(0.2, 0.2)
            if has_led:
                led.blink(0.1, 0.1)
    
    # Set up detection
    ir_sensor.when_pressed = beam_broken  # Beam restored
    ir_sensor.when_released = beam_broken  # Beam broken
    
    try:
        import select
        
        while True:
            # Check for commands
            if select.select([sys.stdin], [], [], 0.01)[0]:
                cmd = sys.stdin.read(1).lower()
                
                if cmd == 'a':
                    if ir_sensor.is_pressed:  # Beam clear
                        armed = True
                        alarm_active = False
                        print("\nSystem ARMED")
                        if has_led:
                            led.blink(1, 1)  # Slow blink
                    else:
                        print("\nCannot arm - beam is interrupted!")
                
                elif cmd == 'd':
                    armed = False
                    alarm_active = False
                    if has_buzzer:
                        buzzer.off()
                    if has_led:
                        led.off()
                    print("\nSystem DISARMED")
            
            # Status display
            beam_status = "Clear" if ir_sensor.is_pressed else "INTERRUPTED"
            system_status = "ARMED" if armed else "DISARMED"
            alarm_status = " - ALARM!" if alarm_active else ""
            
            print(f"\rSystem: {system_status}{alarm_status} | "
                  f"Beam: {beam_status:11s} | "
                  f"Breaches: {breach_count}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n--- Security Log ---")
        print(f"Total breaches: {breach_count}")
        if breach_log:
            print("\nBreach times:")
            for breach in breach_log[-10:]:  # Last 10
                print(f"  {breach.strftime('%H:%M:%S')}")
    finally:
        ir_sensor.close()
        if has_buzzer:
            buzzer.close()
        if has_led:
            led.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("IR Obstacle Sensor Examples")
    print("==========================")
    print(f"IR Sensor GPIO: {IR_SENSOR_PIN}")
    print(f"LED GPIO: {LED_PIN} (optional)")
    print(f"Buzzer GPIO: {BUZZER_PIN} (optional)")
    print("\nNote: Sensor outputs LOW when obstacle detected")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic obstacle detection")
        print("2. Proximity indicator")
        print("3. Line follower robot")
        print("4. Obstacle avoidance robot")
        print("5. Parking sensor")
        print("6. Hand gesture detection")
        print("7. Object counter")
        print("8. Security beam")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_obstacle_detection()
        elif choice == '2':
            proximity_indicator()
        elif choice == '3':
            line_follower()
        elif choice == '4':
            obstacle_avoidance_robot()
        elif choice == '5':
            parking_sensor()
        elif choice == '6':
            hand_gesture_detection()
        elif choice == '7':
            object_counter()
        elif choice == '8':
            security_beam()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()