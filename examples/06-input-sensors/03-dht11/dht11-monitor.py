#!/usr/bin/env python3
"""
DHT11 Temperature and Humidity Monitor
Real-time environmental monitoring with comfort indicators
"""

import sys
import os
import time
import signal
from datetime import datetime

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from _shared.dht11 import DHT11

# GPIO Configuration
DHT_PIN = 17

# Comfort thresholds
TEMP_MIN_COMFORT = 20
TEMP_MAX_COMFORT = 26
HUMIDITY_MIN_COMFORT = 40
HUMIDITY_MAX_COMFORT = 60

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def get_comfort_level(temperature, humidity):
    """
    Determine comfort level based on temperature and humidity
    
    Returns:
        Tuple of (level, message, emoji)
    """
    # Perfect conditions
    if (TEMP_MIN_COMFORT <= temperature <= TEMP_MAX_COMFORT and 
        HUMIDITY_MIN_COMFORT <= humidity <= HUMIDITY_MAX_COMFORT):
        return "Optimal", "Perfect conditions", "😊"
    
    # Temperature issues
    if temperature > 30:
        return "Hot", "Too hot! Consider cooling", "🥵"
    elif temperature > TEMP_MAX_COMFORT:
        return "Warm", "Getting warm", "😓"
    elif temperature < 15:
        return "Cold", "Too cold! Consider heating", "🥶"
    elif temperature < TEMP_MIN_COMFORT:
        return "Cool", "Getting cool", "😐"
    
    # Humidity issues
    if humidity > 70:
        return "Humid", "Too humid! Use dehumidifier", "💧"
    elif humidity > HUMIDITY_MAX_COMFORT:
        return "Moist", "Getting humid", "💦"
    elif humidity < 30:
        return "Dry", "Too dry! Consider humidifier", "🏜️"
    elif humidity < HUMIDITY_MIN_COMFORT:
        return "Arid", "Getting dry", "🌵"
    
    return "Fair", "Acceptable conditions", "🙂"

def calculate_dew_point(temperature, humidity):
    """
    Calculate dew point temperature
    
    Uses Magnus formula approximation
    """
    a = 17.27
    b = 237.7
    
    alpha = ((a * temperature) / (b + temperature)) + np.log(humidity / 100.0)
    dew_point = (b * alpha) / (a - alpha)
    
    return dew_point

def calculate_heat_index(temperature, humidity):
    """
    Calculate heat index (feels like temperature)
    
    Simplified formula for Celsius
    """
    # Convert to Fahrenheit for calculation
    t_f = (temperature * 9/5) + 32
    
    # Simple heat index formula
    if t_f < 80:
        return temperature
    
    hi_f = -42.379 + 2.04901523*t_f + 10.14333127*humidity
    hi_f += -0.22475541*t_f*humidity - 0.00683783*t_f*t_f
    hi_f += -0.05481717*humidity*humidity + 0.00122874*t_f*t_f*humidity
    hi_f += 0.00085282*t_f*humidity*humidity - 0.00000199*t_f*t_f*humidity*humidity
    
    # Convert back to Celsius
    return (hi_f - 32) * 5/9

def display_reading(temperature, humidity, reading_num):
    """Display formatted sensor reading"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    comfort_level, comfort_msg, emoji = get_comfort_level(temperature, humidity)
    
    print(f"\n===== Reading #{reading_num} - {timestamp} =====")
    print(f"Temperature: {temperature:.1f}°C ({temperature*9/5+32:.1f}°F)")
    print(f"Humidity:    {humidity:.1f}%")
    print(f"Comfort:     {comfort_level} {emoji}")
    print(f"Status:      {comfort_msg}")
    
    # Additional calculations (without numpy, simplified)
    if temperature > 26 and humidity > 40:
        feels_like = temperature + (humidity - 40) * 0.1
        print(f"Feels like:  {feels_like:.1f}°C")

def continuous_monitor(sensor):
    """Continuously monitor temperature and humidity"""
    print("DHT11 Environmental Monitor")
    print("===========================")
    print(f"Sensor on GPIO{DHT_PIN}")
    print("Press Ctrl+C to stop\n")
    
    # Statistics tracking
    readings = []
    reading_count = 0
    error_count = 0
    
    # Initial delay for sensor stabilization
    print("Waiting for sensor to stabilize...")
    time.sleep(2)
    
    try:
        while True:
            # Read sensor
            humidity, temperature = sensor.read_retry(retries=5)
            
            if humidity is not None and temperature is not None:
                reading_count += 1
                readings.append((temperature, humidity))
                
                # Display current reading
                display_reading(temperature, humidity, reading_count)
                
                # Keep only last 10 readings for statistics
                if len(readings) > 10:
                    readings.pop(0)
                
                # Display statistics every 5 readings
                if reading_count % 5 == 0 and len(readings) > 1:
                    temps = [r[0] for r in readings]
                    humids = [r[1] for r in readings]
                    
                    print("\n--- Statistics (last 10 readings) ---")
                    print(f"Temp  - Min: {min(temps):.1f}°C, Max: {max(temps):.1f}°C, Avg: {sum(temps)/len(temps):.1f}°C")
                    print(f"Humid - Min: {min(humids):.1f}%, Max: {max(humids):.1f}%, Avg: {sum(humids)/len(humids):.1f}%")
                    print(f"Success rate: {reading_count/(reading_count+error_count)*100:.1f}%")
            else:
                error_count += 1
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Error reading sensor! Check connections.")
            
            # DHT11 needs 2+ seconds between readings
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
        print(f"Total readings: {reading_count}")
        print(f"Total errors: {error_count}")
        if reading_count > 0:
            print(f"Success rate: {reading_count/(reading_count+error_count)*100:.1f}%")

def data_logger_mode(sensor, log_file="dht11_log.csv"):
    """Log sensor data to CSV file"""
    print(f"Data Logger Mode - Logging to {log_file}")
    print("Press Ctrl+C to stop\n")
    
    # Create/open log file
    file_exists = os.path.exists(log_file)
    
    with open(log_file, 'a') as f:
        # Write header if new file
        if not file_exists:
            f.write("timestamp,temperature_c,humidity_percent,comfort_level\n")
        
        reading_count = 0
        
        try:
            while True:
                humidity, temperature = sensor.read_retry()
                
                if humidity is not None and temperature is not None:
                    reading_count += 1
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    comfort_level, _, _ = get_comfort_level(temperature, humidity)
                    
                    # Write to file
                    f.write(f"{timestamp},{temperature:.1f},{humidity:.1f},{comfort_level}\n")
                    f.flush()  # Ensure data is written
                    
                    print(f"[{timestamp}] T: {temperature:.1f}°C, H: {humidity:.1f}%, Logged: {reading_count}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Read error, skipping...")
                
                time.sleep(60)  # Log every minute
                
        except KeyboardInterrupt:
            print(f"\n\nLogging stopped. {reading_count} readings saved to {log_file}")

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("DHT11 Temperature & Humidity Sensor")
    print("===================================")
    print("1. Continuous Monitor")
    print("2. Data Logger (CSV)")
    print("3. Single Reading")
    print("4. Exit")
    
    sensor = DHT11(DHT_PIN)
    
    try:
        while True:
            choice = input("\nSelect mode (1-4): ").strip()
            
            if choice == '1':
                continuous_monitor(sensor)
            elif choice == '2':
                log_file = input("Enter log filename (default: dht11_log.csv): ").strip()
                if not log_file:
                    log_file = "dht11_log.csv"
                data_logger_mode(sensor, log_file)
            elif choice == '3':
                print("\nReading sensor...")
                humidity, temperature = sensor.read_retry()
                if humidity is not None and temperature is not None:
                    display_reading(temperature, humidity, 1)
                else:
                    print("Failed to read sensor!")
            elif choice == '4':
                break
            else:
                print("Invalid choice!")
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        sensor.cleanup()
        print("Cleanup complete")

if __name__ == "__main__":
    # Simple numpy alternative for heat index
    class np:
        @staticmethod
        def log(x):
            import math
            return math.log(x)
    
    main()