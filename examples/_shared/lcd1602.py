#!/usr/bin/env python3
"""
LCD1602 I2C Display Driver
Interface for 16x2 LCD displays with I2C backpack (PCF8574)
"""

import smbus2
import time

class LCD1602:
    """
    Driver for 16x2 LCD display with I2C interface
    
    Uses PCF8574 I2C expander for communication
    Default I2C address is 0x27 (can be 0x3F for some modules)
    """
    
    # LCD Commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80
    
    # Display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00
    
    # Display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00
    
    # Display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00
    
    # Function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00
    
    # Backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00
    
    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005
    
    def __init__(self, i2c_addr=0x27, i2c_bus=1):
        """
        Initialize LCD display
        
        Args:
            i2c_addr: I2C address (default 0x27, try 0x3F if not working)
            i2c_bus: I2C bus number (default 1 for Raspberry Pi)
        """
        self.addr = i2c_addr
        self.bus = smbus2.SMBus(i2c_bus)
        self.backlight_state = self.LCD_BACKLIGHT
        
        # Initialize display
        self._write(0x03)
        self._write(0x03)
        self._write(0x03)
        self._write(0x02)
        
        # Function set: 4-bit mode, 2 lines, 5x8 dots
        self._write_command(self.LCD_FUNCTIONSET | self.LCD_4BITMODE | 
                           self.LCD_2LINE | self.LCD_5x8DOTS)
        
        # Display control: display on, cursor off, blink off
        self._write_command(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON | 
                           self.LCD_CURSOROFF | self.LCD_BLINKOFF)
        
        # Clear display
        self.clear()
        
        # Entry mode: left to right, no shift
        self._write_command(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT | 
                           self.LCD_ENTRYSHIFTDECREMENT)
    
    def _write_byte(self, data):
        """Write byte to I2C device"""
        self.bus.write_byte(self.addr, data)
    
    def _toggle_enable(self, data):
        """Toggle enable pin to latch data"""
        time.sleep(self.E_DELAY)
        self._write_byte(data | 0x04)  # En high
        time.sleep(self.E_PULSE)
        self._write_byte(data & ~0x04)  # En low
        time.sleep(self.E_DELAY)
    
    def _write(self, data, mode=0):
        """
        Write 4 bits to LCD
        
        Args:
            data: Data to write
            mode: 0 for command, 1 for character
        """
        high_nibble = (data & 0xF0) | mode | self.backlight_state
        low_nibble = ((data << 4) & 0xF0) | mode | self.backlight_state
        
        self._write_byte(high_nibble)
        self._toggle_enable(high_nibble)
        
        self._write_byte(low_nibble)
        self._toggle_enable(low_nibble)
    
    def _write_command(self, cmd):
        """Write command to LCD"""
        self._write(cmd, 0)
    
    def _write_char(self, char):
        """Write character to LCD"""
        self._write(char, 1)
    
    def clear(self):
        """Clear display and return cursor home"""
        self._write_command(self.LCD_CLEARDISPLAY)
        time.sleep(0.002)  # Clear command takes longer
    
    def home(self):
        """Return cursor to home position"""
        self._write_command(self.LCD_RETURNHOME)
        time.sleep(0.002)
    
    def set_cursor(self, col, row):
        """
        Set cursor position
        
        Args:
            col: Column (0-15)
            row: Row (0-1)
        """
        if row > 1:
            row = 1
        if col > 15:
            col = 15
        
        # DDRAM addresses for 16x2 LCD
        row_offsets = [0x00, 0x40]
        self._write_command(self.LCD_SETDDRAMADDR | (col + row_offsets[row]))
    
    def write(self, text):
        """
        Write text at current cursor position
        
        Args:
            text: String to display
        """
        for char in text:
            self._write_char(ord(char))
    
    def write_line(self, text, line=0):
        """
        Write text on specified line
        
        Args:
            text: String to display
            line: Line number (0 or 1)
        """
        self.set_cursor(0, line)
        # Pad or truncate to 16 characters
        text = text[:16].ljust(16)
        self.write(text)
    
    def display_on(self):
        """Turn display on"""
        self._display_control |= self.LCD_DISPLAYON
        self._write_command(self.LCD_DISPLAYCONTROL | self._display_control)
    
    def display_off(self):
        """Turn display off"""
        self._display_control &= ~self.LCD_DISPLAYON
        self._write_command(self.LCD_DISPLAYCONTROL | self._display_control)
    
    def backlight_on(self):
        """Turn backlight on"""
        self.backlight_state = self.LCD_BACKLIGHT
        self._write_byte(self.backlight_state)
    
    def backlight_off(self):
        """Turn backlight off"""
        self.backlight_state = self.LCD_NOBACKLIGHT
        self._write_byte(self.backlight_state)
    
    def create_char(self, location, charmap):
        """
        Create custom character
        
        Args:
            location: Memory location (0-7)
            charmap: List of 8 bytes defining character
        """
        location &= 0x07  # Only 8 locations
        self._write_command(self.LCD_SETCGRAMADDR | (location << 3))
        
        for byte in charmap:
            self._write_char(byte)
    
    def scroll_left(self):
        """Scroll display left"""
        self._write_command(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | 
                           self.LCD_MOVELEFT)
    
    def scroll_right(self):
        """Scroll display right"""
        self._write_command(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | 
                           self.LCD_MOVERIGHT)
    
    def cleanup(self):
        """Clean up resources"""
        self.clear()
        self.backlight_off()
        self.bus.close()


# Custom characters
CUSTOM_CHARS = {
    'degree': [0x0C, 0x12, 0x12, 0x0C, 0x00, 0x00, 0x00, 0x00],
    'heart': [0x00, 0x0A, 0x1F, 0x1F, 0x0E, 0x04, 0x00, 0x00],
    'bell': [0x04, 0x0E, 0x0E, 0x0E, 0x1F, 0x00, 0x04, 0x00],
    'note': [0x02, 0x03, 0x02, 0x0E, 0x1E, 0x0C, 0x00, 0x00],
    'clock': [0x00, 0x0E, 0x15, 0x17, 0x11, 0x0E, 0x00, 0x00],
    'duck': [0x00, 0x0C, 0x1D, 0x0F, 0x0F, 0x06, 0x00, 0x00],
    'check': [0x00, 0x01, 0x03, 0x16, 0x1C, 0x08, 0x00, 0x00],
    'cross': [0x00, 0x1B, 0x0E, 0x04, 0x0E, 0x1B, 0x00, 0x00]
}


# Example usage and test code
if __name__ == "__main__":
    print("Testing LCD1602 I2C Display...")
    
    try:
        # Initialize LCD
        lcd = LCD1602()
        
        # Test 1: Basic text
        print("Test 1: Basic text display")
        lcd.clear()
        lcd.write_line("Hello, World!", 0)
        lcd.write_line("LCD1602 Test", 1)
        time.sleep(2)
        
        # Test 2: Scrolling text
        print("Test 2: Scrolling text")
        lcd.clear()
        lcd.write("Scrolling Text Demo -->")
        for i in range(16):
            lcd.scroll_left()
            time.sleep(0.3)
        
        # Test 3: Custom characters
        print("Test 3: Custom characters")
        lcd.clear()
        lcd.create_char(0, CUSTOM_CHARS['heart'])
        lcd.create_char(1, CUSTOM_CHARS['degree'])
        lcd.write_line("Temp: 25" + chr(1) + "C " + chr(0), 0)
        time.sleep(2)
        
        # Test 4: Backlight control
        print("Test 4: Backlight control")
        lcd.clear()
        lcd.write_line("Backlight Test", 0)
        for i in range(3):
            lcd.backlight_off()
            time.sleep(0.5)
            lcd.backlight_on()
            time.sleep(0.5)
        
        # Test 5: Dynamic updates
        print("Test 5: Counter")
        lcd.clear()
        lcd.write_line("Counter:", 0)
        for i in range(10):
            lcd.write_line(f"Value: {i}", 1)
            time.sleep(0.5)
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure I2C is enabled and the display is connected correctly")
        print("Try address 0x3F if 0x27 doesn't work")
    
    finally:
        if 'lcd' in locals():
            lcd.cleanup()
            print("Cleanup complete")