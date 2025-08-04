#!/usr/bin/env python3
"""
Ultrasonic Radar System
Combine ultrasonic sensor with servo for scanning
"""

from gpiozero import DistanceSensor, Servo
import time
import signal
import sys
import math

# GPIO Configuration
TRIGGER_PIN = 23
ECHO_PIN = 24
SERVO_PIN = 18

# Configuration
MAX_DISTANCE = 2.0  # meters
SCAN_ANGLES = range(0, 181, 10)  # 0 to 180 degrees in 10-degree steps

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def angle_to_servo_value(angle):
    """Convert angle (0-180) to servo value (-1 to 1)"""
    return (angle / 90.0) - 1

def draw_radar_display(scan_data, current_angle):
    """Draw ASCII radar display"""
    print("\033[2J\033[H")  # Clear screen and move to top
    
    print("Ultrasonic Radar Scanner")
    print("========================")
    print(f"Current angle: {current_angle}°")
    print("\n   180°")
    print("    |")
    
    # Draw semicircle radar display
    display_radius = 20
    for y in range(display_radius, -1, -1):
        line = ""
        for x in range(-display_radius, display_radius + 1):
            distance = math.sqrt(x*x + y*y)
            
            if distance > display_radius:
                line += " "
            elif y == 0 and x == 0:
                line += "●"  # Center point (sensor)
            else:
                # Check if there's an object at this position
                angle = math.degrees(math.atan2(x, y))
                if angle < 0:
                    angle += 180
                
                # Find closest scan angle
                found_object = False
                for scan_angle, scan_distance in scan_data.items():
                    if abs(angle - scan_angle) < 5:  # Within 5 degrees
                        # Scale distance to display
                        object_radius = (scan_distance / (MAX_DISTANCE * 100)) * display_radius
                        if abs(distance - object_radius) < 1:
                            found_object = True
                            break
                
                if found_object:
                    line += "█"
                elif abs(angle - current_angle) < 2:
                    line += "-"  # Current scan line
                elif distance < display_radius * 0.33:
                    line += "·"
                elif distance < display_radius * 0.66:
                    line += "·"
                else:
                    line += "·"
        
        print(line)
    
    print(" 0°" + " " * (display_radius * 2 - 6) + "180°")
    
    # Display distance scale
    print(f"\nDistance scale: · = {MAX_DISTANCE/3:.1f}m, ·· = {2*MAX_DISTANCE/3:.1f}m, ··· = {MAX_DISTANCE:.1f}m")
    print("\nDetected objects:")
    
    # List detected objects
    for angle in sorted(scan_data.keys()):
        if scan_data[angle] < MAX_DISTANCE * 100:
            print(f"  {angle:3d}° : {scan_data[angle]:5.1f} cm")

def radar_scan(sensor, servo):
    """Perform radar scan"""
    print("Starting radar scan...")
    print("Press Ctrl+C to stop\n")
    
    scan_data = {}
    
    try:
        while True:
            # Scan left to right
            for angle in SCAN_ANGLES:
                servo.value = angle_to_servo_value(angle)
                time.sleep(0.1)  # Wait for servo to move
                
                # Take distance reading
                distance = sensor.distance * 100  # Convert to cm
                
                if distance < MAX_DISTANCE * 100:
                    scan_data[angle] = distance
                else:
                    scan_data[angle] = MAX_DISTANCE * 100
                
                # Update display
                draw_radar_display(scan_data, angle)
                
            # Scan right to left
            for angle in reversed(SCAN_ANGLES[:-1]):
                servo.value = angle_to_servo_value(angle)
                time.sleep(0.1)
                
                distance = sensor.distance * 100
                
                if distance < MAX_DISTANCE * 100:
                    scan_data[angle] = distance
                else:
                    scan_data[angle] = MAX_DISTANCE * 100
                
                draw_radar_display(scan_data, angle)
    
    except KeyboardInterrupt:
        print("\n\nScan stopped")
        servo.mid()  # Return to center

def object_tracker(sensor, servo):
    """Track closest object"""
    print("Object Tracking Mode")
    print("====================")
    print("Servo will track the closest object")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            min_distance = MAX_DISTANCE * 100
            best_angle = 90
            
            # Quick scan to find closest object
            for angle in range(0, 181, 30):
                servo.value = angle_to_servo_value(angle)
                time.sleep(0.05)
                
                distance = sensor.distance * 100
                if distance < min_distance:
                    min_distance = distance
                    best_angle = angle
            
            # Fine-tune position
            if min_distance < MAX_DISTANCE * 100:
                for offset in [-10, -5, 0, 5, 10]:
                    test_angle = best_angle + offset
                    if 0 <= test_angle <= 180:
                        servo.value = angle_to_servo_value(test_angle)
                        time.sleep(0.05)
                        
                        distance = sensor.distance * 100
                        if distance < min_distance:
                            min_distance = distance
                            best_angle = test_angle
                
                # Point at closest object
                servo.value = angle_to_servo_value(best_angle)
                print(f"\rTracking object at {best_angle}° - Distance: {min_distance:.1f} cm   ", end='')
            else:
                print(f"\rNo object in range. Scanning...                                  ", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nTracking stopped")
        servo.mid()

def security_sweep(sensor, servo):
    """Security sweep mode - alert on movement"""
    print("Security Sweep Mode")
    print("===================")
    print("Monitoring for changes in environment")
    print("Press Ctrl+C to stop\n")
    
    # Initial scan to establish baseline
    print("Establishing baseline...")
    baseline = {}
    
    for angle in range(0, 181, 10):
        servo.value = angle_to_servo_value(angle)
        time.sleep(0.1)
        baseline[angle] = sensor.distance * 100
    
    print("Baseline established. Monitoring...\n")
    
    try:
        while True:
            for angle in range(0, 181, 10):
                servo.value = angle_to_servo_value(angle)
                time.sleep(0.05)
                
                current_distance = sensor.distance * 100
                baseline_distance = baseline[angle]
                
                # Check for significant change
                if abs(current_distance - baseline_distance) > 20:  # 20cm threshold
                    print(f"\n🚨 ALERT! Change detected at {angle}°")
                    print(f"   Baseline: {baseline_distance:.1f} cm")
                    print(f"   Current:  {current_distance:.1f} cm")
                    print(f"   Change:   {current_distance - baseline_distance:+.1f} cm\n")
                    
                    # Update baseline
                    baseline[angle] = current_distance
                
                print(f"\rScanning: {angle}°   ", end='')
    
    except KeyboardInterrupt:
        print("\n\nSecurity sweep stopped")
        servo.mid()

def main():
    """Main program"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Ultrasonic Radar System")
    print("=======================")
    print(f"Ultrasonic: Trigger=GPIO{TRIGGER_PIN}, Echo=GPIO{ECHO_PIN}")
    print(f"Servo: GPIO{SERVO_PIN}")
    print(f"Max range: {MAX_DISTANCE}m\n")
    
    # Initialize components
    try:
        sensor = DistanceSensor(
            echo=ECHO_PIN,
            trigger=TRIGGER_PIN,
            max_distance=MAX_DISTANCE,
            queue_len=2
        )
        
        servo = Servo(SERVO_PIN)
        servo.mid()  # Center position
        
        print("Components initialized successfully!\n")
    except Exception as e:
        print(f"Error initializing components: {e}")
        return
    
    while True:
        print("\nSelect Mode:")
        print("1. Radar scan")
        print("2. Object tracker")
        print("3. Security sweep")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            radar_scan(sensor, servo)
        elif choice == '2':
            object_tracker(sensor, servo)
        elif choice == '3':
            security_sweep(sensor, servo)
        elif choice == '4':
            servo.detach()
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()