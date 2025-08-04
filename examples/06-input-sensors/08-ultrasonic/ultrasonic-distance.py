#!/usr/bin/env python3
"""
HC-SR04 Ultrasonic Distance Sensor
Measure distances using ultrasonic sound waves
"""

from gpiozero import DistanceSensor
import time
import signal
import sys
import statistics

# GPIO Configuration
TRIGGER_PIN = 23
ECHO_PIN = 24

# Sensor configuration
MAX_DISTANCE = 4.0  # Maximum measurable distance in meters
QUEUE_LEN = 5       # Number of readings to average

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def get_distance_stats(readings):
    """Calculate statistics from distance readings"""
    if not readings:
        return None, None, None
    
    avg = statistics.mean(readings)
    if len(readings) > 1:
        stdev = statistics.stdev(readings)
    else:
        stdev = 0
    
    return min(readings), max(readings), avg, stdev

def continuous_measurement(sensor):
    """Continuously measure and display distance"""
    print("Continuous Distance Measurement")
    print("===============================")
    print("Press Ctrl+C to stop\n")
    
    readings = []
    reading_count = 0
    
    try:
        while True:
            # Get distance reading
            distance = sensor.distance * 100  # Convert to cm
            
            if distance < MAX_DISTANCE * 100:
                reading_count += 1
                readings.append(distance)
                
                # Keep only last 10 readings
                if len(readings) > 10:
                    readings.pop(0)
                
                # Display current reading
                print(f"\rDistance: {distance:6.1f} cm  ", end='')
                
                # Show statistics every 10 readings
                if reading_count % 10 == 0:
                    min_d, max_d, avg_d, stdev = get_distance_stats(readings)
                    print(f"\n--- Stats (last 10) ---")
                    print(f"Min: {min_d:.1f} cm, Max: {max_d:.1f} cm")
                    print(f"Avg: {avg_d:.1f} cm, StdDev: {stdev:.1f} cm")
                    print("---------------------")
            else:
                print(f"\rOut of range! (>{MAX_DISTANCE*100:.0f} cm)     ", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal readings: {reading_count}")

def proximity_alarm(sensor, threshold_cm=30):
    """Proximity alarm - alert when object is too close"""
    print(f"Proximity Alarm - Threshold: {threshold_cm} cm")
    print("=====================================")
    print("Move object closer/farther to test")
    print("Press Ctrl+C to stop\n")
    
    alarm_active = False
    
    try:
        while True:
            distance = sensor.distance * 100
            
            if distance < threshold_cm:
                if not alarm_active:
                    alarm_active = True
                    print(f"\n⚠️  ALARM! Object at {distance:.1f} cm - TOO CLOSE!")
                else:
                    print(f"\r⚠️  Distance: {distance:.1f} cm - ALARM ACTIVE!   ", end='')
            else:
                if alarm_active:
                    alarm_active = False
                    print(f"\n✓ Clear - Object at {distance:.1f} cm")
                else:
                    print(f"\r✓ Distance: {distance:.1f} cm - Safe         ", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nAlarm deactivated")

def parking_sensor(sensor):
    """Parking sensor with distance zones"""
    print("Parking Sensor Simulator")
    print("========================")
    print("Distance zones:")
    print("  > 100 cm : Safe (Green)")
    print("  50-100 cm: Caution (Yellow)")
    print("  20-50 cm : Warning (Orange)")
    print("  < 20 cm  : Stop! (Red)")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        while True:
            distance = sensor.distance * 100
            
            # Determine zone and display
            if distance > 100:
                zone = "SAFE    "
                symbol = "🟢"
                beep_delay = 0
            elif distance > 50:
                zone = "CAUTION "
                symbol = "🟡"
                beep_delay = 0.5
            elif distance > 20:
                zone = "WARNING "
                symbol = "🟠"
                beep_delay = 0.2
            else:
                zone = "STOP!   "
                symbol = "🔴"
                beep_delay = 0.05
            
            # Display status
            bar_length = int(distance / 5) if distance < 100 else 20
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            print(f"\r{symbol} {zone} [{bar}] {distance:5.1f} cm   ", end='')
            
            # Simulate beeping (just visual)
            if beep_delay > 0:
                time.sleep(beep_delay)
                print(f"\r{symbol} {zone} [{bar}] {distance:5.1f} cm 🔊", end='')
                time.sleep(0.05)
    
    except KeyboardInterrupt:
        print("\n\nParking sensor stopped")

def liquid_level_monitor(sensor, container_height_cm):
    """Monitor liquid level in a container"""
    print(f"Liquid Level Monitor - Container: {container_height_cm} cm")
    print("==========================================")
    print("Place sensor above liquid container")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Measure distance to liquid surface
            distance_to_liquid = sensor.distance * 100
            
            # Calculate liquid level
            if distance_to_liquid < container_height_cm:
                liquid_level = container_height_cm - distance_to_liquid
                percentage = (liquid_level / container_height_cm) * 100
                
                # Create visual representation
                bars = int(percentage / 5)
                level_display = "█" * bars + "░" * (20 - bars)
                
                print(f"\rLevel: [{level_display}] {percentage:4.1f}% ({liquid_level:.1f} cm)   ", end='')
                
                # Alerts
                if percentage > 90:
                    print(" ⚠️  NEARLY FULL!", end='')
                elif percentage < 10:
                    print(" ⚠️  NEARLY EMPTY!", end='')
            else:
                print(f"\rNo liquid detected or out of range (>{container_height_cm} cm)           ", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")

def speed_measurement(sensor):
    """Measure speed of passing objects"""
    print("Speed Measurement")
    print("=================")
    print("Pass object through sensor beam")
    print("Press Ctrl+C to stop\n")
    
    detection_threshold = 50  # cm
    in_detection = False
    entry_time = None
    
    try:
        while True:
            distance = sensor.distance * 100
            
            if distance < detection_threshold and not in_detection:
                # Object entered detection zone
                in_detection = True
                entry_time = time.time()
                print(f"Object detected at {distance:.1f} cm")
            
            elif distance > detection_threshold and in_detection:
                # Object left detection zone
                in_detection = False
                if entry_time:
                    transit_time = time.time() - entry_time
                    # Assume object size is ~10cm
                    speed = 10 / transit_time  # cm/s
                    speed_kmh = speed * 0.036  # Convert to km/h
                    
                    print(f"Transit time: {transit_time:.3f}s")
                    print(f"Estimated speed: {speed:.1f} cm/s ({speed_kmh:.1f} km/h)\n")
                
                entry_time = None
            
            time.sleep(0.01)  # Fast sampling for speed measurement
    
    except KeyboardInterrupt:
        print("\n\nSpeed measurement stopped")

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("HC-SR04 Ultrasonic Sensor Demos")
    print("================================")
    print(f"Trigger: GPIO{TRIGGER_PIN}, Echo: GPIO{ECHO_PIN}")
    print(f"Maximum range: {MAX_DISTANCE}m\n")
    
    # Initialize sensor
    try:
        sensor = DistanceSensor(
            echo=ECHO_PIN,
            trigger=TRIGGER_PIN,
            max_distance=MAX_DISTANCE,
            queue_len=QUEUE_LEN
        )
        print("Sensor initialized successfully!\n")
    except Exception as e:
        print(f"Error initializing sensor: {e}")
        print("Check wiring:")
        print(f"  Trigger -> GPIO{TRIGGER_PIN}")
        print(f"  Echo -> GPIO{ECHO_PIN}")
        print("  VCC -> 5V")
        print("  GND -> GND")
        return
    
    while True:
        print("\nSelect Demo:")
        print("1. Continuous measurement")
        print("2. Proximity alarm")
        print("3. Parking sensor")
        print("4. Liquid level monitor")
        print("5. Speed measurement")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            continuous_measurement(sensor)
        elif choice == '2':
            try:
                threshold = int(input("Enter alarm threshold in cm (default 30): ") or "30")
                proximity_alarm(sensor, threshold)
            except ValueError:
                print("Invalid threshold")
        elif choice == '3':
            parking_sensor(sensor)
        elif choice == '4':
            try:
                height = int(input("Enter container height in cm: "))
                liquid_level_monitor(sensor, height)
            except ValueError:
                print("Invalid height")
        elif choice == '5':
            speed_measurement(sensor)
        elif choice == '6':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()