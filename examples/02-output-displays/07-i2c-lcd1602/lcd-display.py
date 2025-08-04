#!/usr/bin/env python3
"""
I2C LCD1602 Display Demo
Shows various LCD display features using I2C interface
"""

import sys
import os
import time
import signal

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from _shared.lcd1602 import LCD1602, CUSTOM_CHARS

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    if 'lcd' in globals():
        lcd.cleanup()
    sys.exit(0)

def display_intro(lcd):
    """Display introduction message"""
    lcd.clear()
    lcd.write_line("  I2C LCD1602", 0)
    lcd.write_line("    Demo", 1)
    time.sleep(2)
    
    # Fade effect with backlight
    for _ in range(3):
        lcd.backlight_off()
        time.sleep(0.2)
        lcd.backlight_on()
        time.sleep(0.2)

def demo_basic_text(lcd):
    """Demonstrate basic text display"""
    print("Demo 1: Basic Text Display")
    
    lcd.clear()
    lcd.write_line("Hello, World!", 0)
    lcd.write_line("Raspberry Pi 5", 1)
    time.sleep(2)
    
    # Show text alignment
    lcd.clear()
    lcd.write_line("Left Aligned", 0)
    lcd.write_line("   Centered   ", 1)
    time.sleep(2)
    
    lcd.clear()
    lcd.write_line("Line 1: Top", 0)
    lcd.write_line("Line 2: Bottom", 1)
    time.sleep(2)

def demo_scrolling(lcd):
    """Demonstrate text scrolling"""
    print("Demo 2: Scrolling Text")
    
    lcd.clear()
    long_text = "This is a long message that will scroll across the display... "
    lcd.write(long_text[:16])
    
    # Scroll the long message
    for _ in range(len(long_text)):
        time.sleep(0.3)
        lcd.scroll_left()
    
    time.sleep(1)
    
    # Return home
    lcd.clear()
    lcd.write_line("Scroll Complete!", 0)
    time.sleep(1)

def demo_custom_chars(lcd):
    """Demonstrate custom character creation"""
    print("Demo 3: Custom Characters")
    
    # Create custom characters
    lcd.create_char(0, CUSTOM_CHARS['heart'])
    lcd.create_char(1, CUSTOM_CHARS['bell'])
    lcd.create_char(2, CUSTOM_CHARS['note'])
    lcd.create_char(3, CUSTOM_CHARS['clock'])
    lcd.create_char(4, CUSTOM_CHARS['degree'])
    lcd.create_char(5, CUSTOM_CHARS['check'])
    lcd.create_char(6, CUSTOM_CHARS['cross'])
    
    lcd.clear()
    lcd.write_line("Custom Chars:", 0)
    lcd.set_cursor(0, 1)
    
    # Display custom characters
    for i in range(7):
        lcd.write(chr(i) + " ")
    
    time.sleep(3)
    
    # Practical example
    lcd.clear()
    lcd.write_line("Temp: 25" + chr(4) + "C " + chr(0), 0)
    lcd.write_line("Music " + chr(2) + " Time " + chr(3), 1)
    time.sleep(3)

def demo_live_data(lcd):
    """Demonstrate live data updates"""
    print("Demo 4: Live Data Display")
    
    lcd.clear()
    lcd.write_line("Live Updates:", 0)
    
    # Simulate sensor readings
    for i in range(10):
        temp = 20 + (i * 0.5)
        humidity = 50 + (i * 2)
        
        lcd.write_line(f"T:{temp:.1f}C H:{humidity}%", 1)
        time.sleep(0.5)
    
    # Progress bar
    lcd.clear()
    lcd.write_line("Progress Bar:", 0)
    
    for i in range(17):
        progress = "=" * i
        lcd.write_line(progress, 1)
        time.sleep(0.2)
    
    lcd.write_line("Complete!       ", 1)
    time.sleep(1)

def demo_menu_system(lcd):
    """Demonstrate a simple menu system"""
    print("Demo 5: Menu System")
    
    menu_items = [
        "1. Temperature",
        "2. Humidity",
        "3. Pressure",
        "4. Settings"
    ]
    
    lcd.clear()
    lcd.write_line("== Main Menu ==", 0)
    
    # Cycle through menu items
    for item in menu_items:
        lcd.write_line(item, 1)
        time.sleep(1)
    
    lcd.clear()
    lcd.write_line("Menu Demo", 0)
    lcd.write_line("Complete!", 1)
    time.sleep(1)

def demo_animations(lcd):
    """Demonstrate simple animations"""
    print("Demo 6: Animations")
    
    # Pac-Man style animation
    pac_chars = [
        [0x0E, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x0E, 0x00],  # Closed
        [0x0E, 0x1F, 0x1E, 0x1C, 0x1E, 0x1F, 0x0E, 0x00]   # Open
    ]
    
    lcd.create_char(0, pac_chars[0])
    lcd.create_char(1, pac_chars[1])
    
    lcd.clear()
    lcd.write_line("Animation Demo", 0)
    
    # Move Pac-Man across screen
    for pos in range(16):
        lcd.set_cursor(pos, 1)
        lcd.write(chr(pos % 2))
        if pos > 0:
            lcd.set_cursor(pos - 1, 1)
            lcd.write(" ")
        time.sleep(0.2)
    
    time.sleep(1)

def main():
    """Main program"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("I2C LCD1602 Display Demo")
    print("========================")
    print("Make sure I2C is enabled and LCD is connected")
    print("Default address: 0x27 (try 0x3F if not working)")
    print("Press Ctrl+C to exit\n")
    
    try:
        # Initialize LCD
        global lcd
        lcd = LCD1602(i2c_addr=0x27)
        print("LCD initialized successfully!\n")
        
        # Run demonstrations
        display_intro(lcd)
        
        demos = [
            demo_basic_text,
            demo_scrolling,
            demo_custom_chars,
            demo_live_data,
            demo_menu_system,
            demo_animations
        ]
        
        for demo in demos:
            demo(lcd)
            time.sleep(1)
        
        # Final message
        lcd.clear()
        lcd.write_line("Demo Complete!", 0)
        lcd.write_line("Thanks! " + chr(0), 1)  # Heart symbol
        
        print("\nAll demos completed!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("1. Check I2C is enabled: sudo raspi-config")
        print("2. Check connections: SDA->Pin3, SCL->Pin5")
        print("3. Scan I2C devices: sudo i2cdetect -y 1")
        print("4. Try alternate address: change 0x27 to 0x3F")
    
    finally:
        time.sleep(3)
        if 'lcd' in globals():
            lcd.cleanup()

if __name__ == "__main__":
    main()