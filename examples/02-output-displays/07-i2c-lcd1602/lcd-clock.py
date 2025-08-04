#!/usr/bin/env python3
"""
LCD Clock with Temperature Display
Real-time clock display with system temperature monitoring
"""

import sys
import os
import time
import signal
from datetime import datetime
import subprocess

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from _shared.lcd1602 import LCD1602, CUSTOM_CHARS

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    if 'lcd' in globals():
        lcd.cleanup()
    sys.exit(0)

def get_cpu_temperature():
    """Get CPU temperature from Raspberry Pi"""
    try:
        # Read temperature from thermal zone
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = float(f.read()) / 1000.0
        return temp
    except:
        return None

def get_system_info():
    """Get system information"""
    try:
        # Get hostname
        hostname = subprocess.check_output(['hostname']).decode().strip()
        
        # Get IP address
        ip_cmd = "hostname -I | awk '{print $1}'"
        ip_addr = subprocess.check_output(ip_cmd, shell=True).decode().strip()
        
        return hostname, ip_addr
    except:
        return "Unknown", "No IP"

def create_clock_chars(lcd):
    """Create custom characters for clock display"""
    # Big number segments (for creating large digits)
    segments = {
        'top_left': [0x07, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F],
        'top_right': [0x1C, 0x1E, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F],
        'bottom_left': [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0F, 0x07],
        'bottom_right': [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1E, 0x1C],
        'full_block': [0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F]
    }
    
    # Temperature symbol
    lcd.create_char(0, CUSTOM_CHARS['degree'])
    # Clock symbol
    lcd.create_char(1, CUSTOM_CHARS['clock'])

def display_time_simple(lcd):
    """Display time in simple format"""
    current_time = datetime.now()
    time_str = current_time.strftime("%H:%M:%S")
    date_str = current_time.strftime("%a %d %b")
    
    lcd.write_line(chr(1) + " " + time_str, 0)
    lcd.write_line(date_str, 1)

def display_with_temp(lcd):
    """Display time with temperature"""
    current_time = datetime.now()
    time_str = current_time.strftime("%H:%M:%S")
    
    temp = get_cpu_temperature()
    if temp:
        temp_str = f"CPU: {temp:.1f}{chr(0)}C"
    else:
        temp_str = "Temp: N/A"
    
    lcd.write_line(time_str + "        ", 0)
    lcd.write_line(temp_str + "        ", 1)

def display_system_info(lcd, duration=5):
    """Display system information for specified duration"""
    hostname, ip_addr = get_system_info()
    
    lcd.clear()
    lcd.write_line(f"Host: {hostname[:10]}", 0)
    lcd.write_line(f"IP: {ip_addr}", 1)
    
    time.sleep(duration)

def clock_mode(lcd):
    """Main clock display mode"""
    print("Clock Mode - Press Ctrl+C to exit")
    
    # Create custom characters
    create_clock_chars(lcd)
    
    # Display system info on startup
    display_system_info(lcd, 3)
    
    lcd.clear()
    info_counter = 0
    
    try:
        while True:
            # Show system info every 30 seconds
            if info_counter >= 30:
                display_system_info(lcd, 3)
                lcd.clear()
                info_counter = 0
            
            # Update display
            display_with_temp(lcd)
            
            time.sleep(1)
            info_counter += 1
            
    except KeyboardInterrupt:
        pass

def countdown_timer(lcd, minutes):
    """Countdown timer mode"""
    print(f"Countdown Timer: {minutes} minutes")
    
    lcd.clear()
    total_seconds = minutes * 60
    
    try:
        while total_seconds > 0:
            mins = total_seconds // 60
            secs = total_seconds % 60
            
            lcd.write_line("Timer Running:", 0)
            lcd.write_line(f"  {mins:02d}:{secs:02d} left  ", 1)
            
            time.sleep(1)
            total_seconds -= 1
        
        # Timer complete
        lcd.clear()
        lcd.write_line("Timer Complete!", 0)
        lcd.write_line(chr(1) + " Time's Up! " + chr(1), 1)
        
        # Flash backlight
        for _ in range(5):
            lcd.backlight_off()
            time.sleep(0.3)
            lcd.backlight_on()
            time.sleep(0.3)
            
    except KeyboardInterrupt:
        lcd.clear()
        lcd.write_line("Timer Cancelled", 0)
        time.sleep(2)

def stopwatch_mode(lcd):
    """Stopwatch mode"""
    print("Stopwatch Mode - Press Ctrl+C to stop")
    
    lcd.clear()
    lcd.write_line("Stopwatch Ready", 0)
    lcd.write_line("Press Enter...", 1)
    
    input()  # Wait for Enter to start
    
    start_time = time.time()
    
    try:
        while True:
            elapsed = time.time() - start_time
            
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            milliseconds = int((elapsed % 1) * 100)
            
            lcd.write_line("Stopwatch:", 0)
            if hours > 0:
                lcd.write_line(f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:02d}", 1)
            else:
                lcd.write_line(f"  {minutes:02d}:{seconds:02d}.{milliseconds:02d}  ", 1)
            
            time.sleep(0.01)  # Update every 10ms
            
    except KeyboardInterrupt:
        # Show final time
        elapsed = time.time() - start_time
        lcd.clear()
        lcd.write_line("Final Time:", 0)
        time.sleep(3)

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("LCD Clock & Timer Application")
    print("=============================")
    print("1. Clock with Temperature")
    print("2. Countdown Timer")
    print("3. Stopwatch")
    print("4. Exit")
    
    try:
        # Initialize LCD
        global lcd
        lcd = LCD1602(i2c_addr=0x27)
        
        while True:
            choice = input("\nSelect mode (1-4): ").strip()
            
            if choice == '1':
                clock_mode(lcd)
            elif choice == '2':
                try:
                    minutes = int(input("Enter minutes for countdown: "))
                    countdown_timer(lcd, minutes)
                except ValueError:
                    print("Invalid input!")
            elif choice == '3':
                stopwatch_mode(lcd)
            elif choice == '4':
                break
            else:
                print("Invalid choice!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Check I2C connection and address")
    
    finally:
        if 'lcd' in globals():
            lcd.clear()
            lcd.write_line("Goodbye!", 0)
            time.sleep(1)
            lcd.cleanup()

if __name__ == "__main__":
    main()