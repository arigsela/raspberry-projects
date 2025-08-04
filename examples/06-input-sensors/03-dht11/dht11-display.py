#!/usr/bin/env python3
"""
DHT11 with LCD Display
Temperature and humidity monitoring with LCD output
"""

import sys
import os
import time
import signal
from datetime import datetime

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from _shared.dht11 import DHT11
from _shared.lcd1602 import LCD1602, CUSTOM_CHARS

# GPIO Configuration
DHT_PIN = 17

# LCD Configuration
LCD_ADDR = 0x27

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    if 'lcd' in globals():
        lcd.cleanup()
    if 'sensor' in globals():
        sensor.cleanup()
    sys.exit(0)

def create_display_chars(lcd):
    """Create custom characters for display"""
    # Thermometer symbol
    thermometer = [
        0b00100,
        0b01010,
        0b01010,
        0b01110,
        0b01110,
        0b11111,
        0b11111,
        0b01110
    ]
    
    # Water drop (humidity)
    water_drop = [
        0b00100,
        0b00100,
        0b01010,
        0b01010,
        0b10001,
        0b10001,
        0b10001,
        0b01110
    ]
    
    # Up arrow (rising)
    up_arrow = [
        0b00100,
        0b01110,
        0b11111,
        0b00100,
        0b00100,
        0b00100,
        0b00100,
        0b00000
    ]
    
    # Down arrow (falling)
    down_arrow = [
        0b00000,
        0b00100,
        0b00100,
        0b00100,
        0b00100,
        0b11111,
        0b01110,
        0b00100
    ]
    
    lcd.create_char(0, thermometer)
    lcd.create_char(1, water_drop)
    lcd.create_char(2, up_arrow)
    lcd.create_char(3, down_arrow)
    lcd.create_char(4, CUSTOM_CHARS['degree'])

def get_trend_symbol(current, previous):
    """Get trend symbol based on value change"""
    if previous is None:
        return " "
    elif current > previous + 0.5:
        return chr(2)  # Up arrow
    elif current < previous - 0.5:
        return chr(3)  # Down arrow
    else:
        return "="

def display_readings(lcd, temperature, humidity, prev_temp=None, prev_humid=None):
    """Display temperature and humidity on LCD"""
    # Line 1: Temperature
    temp_trend = get_trend_symbol(temperature, prev_temp)
    temp_line = f"{chr(0)} {temperature:.1f}{chr(4)}C {temp_trend}"
    lcd.write_line(temp_line, 0)
    
    # Line 2: Humidity
    humid_trend = get_trend_symbol(humidity, prev_humid)
    humid_line = f"{chr(1)} {humidity:.1f}% {humid_trend}"
    lcd.write_line(humid_line, 1)

def display_comfort(lcd, temperature, humidity):
    """Display comfort level on LCD"""
    lcd.clear()
    
    if 20 <= temperature <= 26 and 40 <= humidity <= 60:
        lcd.write_line("Comfort Level:", 0)
        lcd.write_line("   Optimal!", 1)
    elif temperature > 28:
        lcd.write_line("Too Hot!", 0)
        lcd.write_line("Cool Down", 1)
    elif temperature < 18:
        lcd.write_line("Too Cold!", 0)
        lcd.write_line("Warm Up", 1)
    elif humidity > 70:
        lcd.write_line("Too Humid!", 0)
        lcd.write_line("Dehumidify", 1)
    elif humidity < 30:
        lcd.write_line("Too Dry!", 0)
        lcd.write_line("Humidify", 1)
    else:
        lcd.write_line("Comfort Level:", 0)
        lcd.write_line("   Fair", 1)

def main():
    """Main program"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("DHT11 + LCD1602 Environmental Monitor")
    print("=====================================")
    print(f"DHT11 on GPIO{DHT_PIN}")
    print(f"LCD on I2C address 0x{LCD_ADDR:02X}")
    print("Press Ctrl+C to exit\n")
    
    try:
        # Initialize components
        global sensor, lcd
        sensor = DHT11(DHT_PIN)
        lcd = LCD1602(i2c_addr=LCD_ADDR)
        
        # Create custom characters
        create_display_chars(lcd)
        
        # Welcome message
        lcd.clear()
        lcd.write_line("  Environmental", 0)
        lcd.write_line("    Monitor", 1)
        time.sleep(2)
        
        # Initialize variables
        prev_temp = None
        prev_humid = None
        reading_count = 0
        error_count = 0
        last_comfort_check = 0
        
        print("Monitoring started...")
        
        while True:
            # Read sensor
            humidity, temperature = sensor.read_retry(retries=5)
            
            if humidity is not None and temperature is not None:
                reading_count += 1
                
                # Update display
                display_readings(lcd, temperature, humidity, prev_temp, prev_humid)
                
                # Console output
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"T: {temperature:.1f}°C, H: {humidity:.1f}% "
                      f"(Reading #{reading_count})", end='', flush=True)
                
                # Store previous values
                prev_temp = temperature
                prev_humid = humidity
                
                # Show comfort level every 30 seconds
                current_time = time.time()
                if current_time - last_comfort_check > 30:
                    time.sleep(0.5)
                    display_comfort(lcd, temperature, humidity)
                    time.sleep(3)
                    # Redisplay readings
                    display_readings(lcd, temperature, humidity, prev_temp, prev_humid)
                    last_comfort_check = current_time
                
            else:
                error_count += 1
                lcd.clear()
                lcd.write_line("Sensor Error!", 0)
                lcd.write_line("Check wiring", 1)
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Error reading sensor! (Error #{error_count})")
            
            # Wait before next reading
            time.sleep(3)
            
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Check connections:")
        print("- DHT11: VCC->5V, Data->GPIO17, GND->GND")
        print("- LCD: VCC->5V, GND->GND, SDA->Pin3, SCL->Pin5")
    
    finally:
        print(f"\n\nTotal readings: {reading_count}")
        print(f"Total errors: {error_count}")
        
        if 'lcd' in globals():
            lcd.clear()
            lcd.write_line("Monitor Stopped", 0)
            time.sleep(1)
            lcd.cleanup()
        
        if 'sensor' in globals():
            sensor.cleanup()

if __name__ == "__main__":
    main()