#!/usr/bin/env python3
"""
LED Dot Matrix Display (8x8)
Display patterns, text, and animations on an 8x8 LED matrix
"""

from gpiozero import OutputDevice
import time
import signal
import sys
import threading

# GPIO Configuration for 8x8 matrix with MAX7219 driver
# Using SPI-like interface
DIN_PIN = 17   # Data In
CS_PIN = 27    # Chip Select
CLK_PIN = 22   # Clock

# MAX7219 Register Addresses
REG_NOOP = 0x00
REG_DIGIT0 = 0x01
REG_DIGIT1 = 0x02
REG_DIGIT2 = 0x03
REG_DIGIT3 = 0x04
REG_DIGIT4 = 0x05
REG_DIGIT5 = 0x06
REG_DIGIT6 = 0x07
REG_DIGIT7 = 0x08
REG_DECODEMODE = 0x09
REG_INTENSITY = 0x0A
REG_SCANLIMIT = 0x0B
REG_SHUTDOWN = 0x0C
REG_DISPLAYTEST = 0x0F

# Character definitions (8x8 bitmaps)
CHARACTERS = {
    'A': [
        0b00011000,
        0b00100100,
        0b01000010,
        0b01000010,
        0b01111110,
        0b01000010,
        0b01000010,
        0b00000000
    ],
    'B': [
        0b01111100,
        0b01000010,
        0b01000010,
        0b01111100,
        0b01000010,
        0b01000010,
        0b01111100,
        0b00000000
    ],
    'C': [
        0b00111100,
        0b01000010,
        0b01000000,
        0b01000000,
        0b01000000,
        0b01000010,
        0b00111100,
        0b00000000
    ],
    'H': [
        0b01000010,
        0b01000010,
        0b01000010,
        0b01111110,
        0b01000010,
        0b01000010,
        0b01000010,
        0b00000000
    ],
    'I': [
        0b00111100,
        0b00001000,
        0b00001000,
        0b00001000,
        0b00001000,
        0b00001000,
        0b00111100,
        0b00000000
    ],
    '0': [
        0b00111100,
        0b01000010,
        0b01000110,
        0b01001010,
        0b01010010,
        0b01100010,
        0b00111100,
        0b00000000
    ],
    '1': [
        0b00001000,
        0b00011000,
        0b00001000,
        0b00001000,
        0b00001000,
        0b00001000,
        0b00111110,
        0b00000000
    ],
    '2': [
        0b00111100,
        0b01000010,
        0b00000010,
        0b00001100,
        0b00110000,
        0b01000000,
        0b01111110,
        0b00000000
    ],
    '3': [
        0b00111100,
        0b01000010,
        0b00000010,
        0b00011100,
        0b00000010,
        0b01000010,
        0b00111100,
        0b00000000
    ],
    ' ': [0, 0, 0, 0, 0, 0, 0, 0],
    '♥': [  # Heart
        0b00000000,
        0b01100110,
        0b11111111,
        0b11111111,
        0b11111111,
        0b01111110,
        0b00111100,
        0b00011000
    ],
    '☺': [  # Smiley
        0b00111100,
        0b01000010,
        0b10100101,
        0b10000001,
        0b10100101,
        0b10011001,
        0b01000010,
        0b00111100
    ]
}

# Animation patterns
PATTERNS = {
    'checkerboard1': [
        0b10101010,
        0b01010101,
        0b10101010,
        0b01010101,
        0b10101010,
        0b01010101,
        0b10101010,
        0b01010101
    ],
    'checkerboard2': [
        0b01010101,
        0b10101010,
        0b01010101,
        0b10101010,
        0b01010101,
        0b10101010,
        0b01010101,
        0b10101010
    ],
    'cross': [
        0b10000001,
        0b01000010,
        0b00100100,
        0b00011000,
        0b00011000,
        0b00100100,
        0b01000010,
        0b10000001
    ],
    'box': [
        0b11111111,
        0b10000001,
        0b10000001,
        0b10000001,
        0b10000001,
        0b10000001,
        0b10000001,
        0b11111111
    ]
}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class MAX7219Matrix:
    """Control an 8x8 LED matrix with MAX7219 driver"""
    
    def __init__(self, din=DIN_PIN, cs=CS_PIN, clk=CLK_PIN):
        """Initialize the matrix"""
        self.din = OutputDevice(din)
        self.cs = OutputDevice(cs)
        self.clk = OutputDevice(clk)
        
        # Initialize high
        self.cs.on()
        self.clk.off()
        self.din.off()
        
        # Display buffer
        self.buffer = [[0 for _ in range(8)] for _ in range(8)]
        
        # Initialize MAX7219
        self._init_display()
    
    def _init_display(self):
        """Initialize MAX7219 settings"""
        self._write_register(REG_DISPLAYTEST, 0x00)  # Normal operation
        self._write_register(REG_SCANLIMIT, 0x07)    # Display all digits
        self._write_register(REG_DECODEMODE, 0x00)   # No decode
        self._write_register(REG_SHUTDOWN, 0x01)     # Normal operation
        self.set_brightness(8)                       # Medium brightness
        self.clear()
    
    def _write_byte(self, data):
        """Write a byte to the MAX7219"""
        for i in range(8):
            # Send MSB first
            if data & 0x80:
                self.din.on()
            else:
                self.din.off()
            
            # Clock pulse
            self.clk.on()
            time.sleep(0.000001)  # 1 microsecond
            self.clk.off()
            
            # Shift to next bit
            data <<= 1
    
    def _write_register(self, address, data):
        """Write to a MAX7219 register"""
        self.cs.off()  # Select chip
        self._write_byte(address)
        self._write_byte(data)
        self.cs.on()   # Deselect chip
    
    def set_brightness(self, intensity):
        """Set display brightness (0-15)"""
        intensity = max(0, min(15, intensity))
        self._write_register(REG_INTENSITY, intensity)
    
    def clear(self):
        """Clear the display"""
        for row in range(8):
            self._write_register(REG_DIGIT0 + row, 0x00)
            self.buffer[row] = [0] * 8
    
    def set_pixel(self, x, y, state):
        """Set a single pixel"""
        if 0 <= x < 8 and 0 <= y < 8:
            self.buffer[y][x] = 1 if state else 0
            self._update_row(y)
    
    def _update_row(self, row):
        """Update a single row on the display"""
        if 0 <= row < 8:
            byte_val = 0
            for col in range(8):
                if self.buffer[row][col]:
                    byte_val |= (1 << (7 - col))
            self._write_register(REG_DIGIT0 + row, byte_val)
    
    def update_display(self):
        """Update entire display from buffer"""
        for row in range(8):
            self._update_row(row)
    
    def display_pattern(self, pattern):
        """Display an 8x8 pattern"""
        if len(pattern) == 8:
            for row in range(8):
                byte_val = pattern[row]
                for col in range(8):
                    self.buffer[row][col] = 1 if (byte_val & (1 << (7 - col))) else 0
                self._write_register(REG_DIGIT0 + row, byte_val)
    
    def display_character(self, char):
        """Display a single character"""
        if char in CHARACTERS:
            self.display_pattern(CHARACTERS[char])
    
    def scroll_text(self, text, delay=0.1):
        """Scroll text across the display"""
        # Convert text to bitmap
        full_bitmap = []
        for char in text:
            if char in CHARACTERS:
                for col in range(8):
                    column = 0
                    for row in range(8):
                        if CHARACTERS[char][row] & (1 << (7 - col)):
                            column |= (1 << row)
                    full_bitmap.append(column)
                full_bitmap.append(0)  # Space between characters
        
        # Scroll the bitmap
        for offset in range(len(full_bitmap) - 7):
            for col in range(8):
                for row in range(8):
                    if offset + col < len(full_bitmap):
                        self.buffer[row][col] = 1 if (full_bitmap[offset + col] & (1 << row)) else 0
                    else:
                        self.buffer[row][col] = 0
            self.update_display()
            time.sleep(delay)
    
    def draw_line(self, x0, y0, x1, y1, state=True):
        """Draw a line using Bresenham's algorithm"""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            self.set_pixel(x0, y0, state)
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    
    def draw_rect(self, x, y, width, height, filled=False):
        """Draw a rectangle"""
        if filled:
            for row in range(y, min(y + height, 8)):
                for col in range(x, min(x + width, 8)):
                    self.set_pixel(col, row, True)
        else:
            # Top and bottom
            for col in range(x, min(x + width, 8)):
                self.set_pixel(col, y, True)
                if y + height - 1 < 8:
                    self.set_pixel(col, y + height - 1, True)
            # Left and right
            for row in range(y, min(y + height, 8)):
                self.set_pixel(x, row, True)
                if x + width - 1 < 8:
                    self.set_pixel(x + width - 1, row, True)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.clear()
        self._write_register(REG_SHUTDOWN, 0x00)  # Shutdown display
        self.din.close()
        self.cs.close()
        self.clk.close()

def basic_patterns():
    """Display basic patterns"""
    print("\n=== Basic Patterns ===")
    print("Showing various patterns")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    
    patterns = [
        ('Checkerboard 1', PATTERNS['checkerboard1']),
        ('Checkerboard 2', PATTERNS['checkerboard2']),
        ('Cross', PATTERNS['cross']),
        ('Box', PATTERNS['box'])
    ]
    
    try:
        while True:
            for name, pattern in patterns:
                print(f"\rShowing: {name:15s}", end='')
                matrix.display_pattern(pattern)
                time.sleep(1)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def scrolling_message():
    """Scroll a text message"""
    print("\n=== Scrolling Message ===")
    
    message = input("Enter message to scroll (default: HELLO): ") or "HELLO"
    message = message.upper() + "  "  # Add space at end
    
    print(f"Scrolling: {message}")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    
    try:
        while True:
            matrix.scroll_text(message, delay=0.08)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def animation_demo():
    """Animated patterns"""
    print("\n=== Animation Demo ===")
    print("Showing animations")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    
    try:
        while True:
            # Expanding box
            print("\rAnimation: Expanding box     ", end='')
            for size in range(1, 5):
                matrix.clear()
                matrix.draw_rect(4-size, 4-size, size*2, size*2, False)
                matrix.update_display()
                time.sleep(0.1)
            for size in range(4, 0, -1):
                matrix.clear()
                matrix.draw_rect(4-size, 4-size, size*2, size*2, False)
                matrix.update_display()
                time.sleep(0.1)
            
            # Moving dot
            print("\rAnimation: Moving dot        ", end='')
            for _ in range(2):
                # Move around perimeter
                for x in range(8):
                    matrix.clear()
                    matrix.set_pixel(x, 0, True)
                    matrix.update_display()
                    time.sleep(0.05)
                for y in range(1, 8):
                    matrix.clear()
                    matrix.set_pixel(7, y, True)
                    matrix.update_display()
                    time.sleep(0.05)
                for x in range(6, -1, -1):
                    matrix.clear()
                    matrix.set_pixel(x, 7, True)
                    matrix.update_display()
                    time.sleep(0.05)
                for y in range(6, 0, -1):
                    matrix.clear()
                    matrix.set_pixel(0, y, True)
                    matrix.update_display()
                    time.sleep(0.05)
            
            # Rain effect
            print("\rAnimation: Rain effect       ", end='')
            import random
            drops = []
            for _ in range(50):
                # Add new drop
                if random.random() > 0.7:
                    drops.append([random.randint(0, 7), 0])
                
                # Update drops
                matrix.clear()
                new_drops = []
                for drop in drops:
                    matrix.set_pixel(drop[0], drop[1], True)
                    drop[1] += 1
                    if drop[1] < 8:
                        new_drops.append(drop)
                drops = new_drops
                matrix.update_display()
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def pixel_draw():
    """Interactive pixel drawing"""
    print("\n=== Pixel Drawing ===")
    print("Use arrow keys to move, space to toggle pixel")
    print("Press 'c' to clear, 'q' to quit")
    
    matrix = MAX7219Matrix()
    cursor_x, cursor_y = 4, 4
    cursor_blink = True
    
    # For non-blocking keyboard input
    import termios, tty, select
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        tty.setraw(sys.stdin.fileno())
        
        while True:
            # Display with blinking cursor
            saved_state = matrix.buffer[cursor_y][cursor_x]
            if cursor_blink:
                matrix.set_pixel(cursor_x, cursor_y, not saved_state)
            matrix.update_display()
            
            # Check for keyboard input
            if select.select([sys.stdin], [], [], 0.1)[0]:
                key = sys.stdin.read(1)
                
                # Restore pixel state before moving
                matrix.set_pixel(cursor_x, cursor_y, saved_state)
                
                # Handle keys
                if key == '\x1b':  # ESC sequence
                    key2 = sys.stdin.read(1)
                    if key2 == '[':
                        key3 = sys.stdin.read(1)
                        if key3 == 'A':  # Up
                            cursor_y = max(0, cursor_y - 1)
                        elif key3 == 'B':  # Down
                            cursor_y = min(7, cursor_y + 1)
                        elif key3 == 'C':  # Right
                            cursor_x = min(7, cursor_x + 1)
                        elif key3 == 'D':  # Left
                            cursor_x = max(0, cursor_x - 1)
                elif key == ' ':
                    # Toggle pixel
                    current = matrix.buffer[cursor_y][cursor_x]
                    matrix.set_pixel(cursor_x, cursor_y, not current)
                elif key == 'c':
                    matrix.clear()
                elif key == 'q':
                    break
            
            cursor_blink = not cursor_blink
    
    except KeyboardInterrupt:
        pass
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        matrix.cleanup()

def brightness_control():
    """Demonstrate brightness levels"""
    print("\n=== Brightness Control ===")
    print("Adjusting display brightness")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    
    # Display a pattern
    matrix.display_pattern(PATTERNS['cross'])
    
    try:
        while True:
            # Fade up
            for brightness in range(16):
                matrix.set_brightness(brightness)
                print(f"\rBrightness: {brightness:2d}/15", end='')
                time.sleep(0.1)
            
            # Fade down
            for brightness in range(15, -1, -1):
                matrix.set_brightness(brightness)
                print(f"\rBrightness: {brightness:2d}/15", end='')
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def clock_display():
    """Simple digital clock (hours and minutes)"""
    print("\n=== Clock Display ===")
    print("Showing time on matrix")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    
    # Simple digit patterns (3x5)
    digits_3x5 = {
        '0': [0x7, 0x5, 0x5, 0x5, 0x7],
        '1': [0x2, 0x6, 0x2, 0x2, 0x7],
        '2': [0x7, 0x1, 0x7, 0x4, 0x7],
        '3': [0x7, 0x1, 0x3, 0x1, 0x7],
        '4': [0x5, 0x5, 0x7, 0x1, 0x1],
        '5': [0x7, 0x4, 0x7, 0x1, 0x7],
        '6': [0x7, 0x4, 0x7, 0x5, 0x7],
        '7': [0x7, 0x1, 0x1, 0x1, 0x1],
        '8': [0x7, 0x5, 0x7, 0x5, 0x7],
        '9': [0x7, 0x5, 0x7, 0x1, 0x7]
    }
    
    try:
        from datetime import datetime
        
        while True:
            now = datetime.now()
            hour_str = f"{now.hour:02d}"
            min_str = f"{now.minute:02d}"
            
            # Clear display
            matrix.clear()
            
            # Draw hours (left side)
            for row in range(5):
                for col in range(3):
                    # First digit
                    if digits_3x5[hour_str[0]][row] & (1 << (2 - col)):
                        matrix.set_pixel(col, row + 1, True)
                    # Second digit
                    if digits_3x5[hour_str[1]][row] & (1 << (2 - col)):
                        matrix.set_pixel(col + 4, row + 1, True)
            
            # Draw colon
            matrix.set_pixel(3, 2, True)
            matrix.set_pixel(3, 4, True)
            
            # Update display
            matrix.update_display()
            time.sleep(0.5)
            
            # Blink colon
            matrix.set_pixel(3, 2, False)
            matrix.set_pixel(3, 4, False)
            matrix.update_display()
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def game_of_life():
    """Conway's Game of Life"""
    print("\n=== Game of Life ===")
    print("Conway's Game of Life simulation")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    
    # Initialize with random pattern
    import random
    grid = [[random.randint(0, 1) for _ in range(8)] for _ in range(8)]
    
    def count_neighbors(grid, x, y):
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % 8, (y + dy) % 8
                count += grid[ny][nx]
        return count
    
    generation = 0
    
    try:
        while True:
            # Display current generation
            for y in range(8):
                for x in range(8):
                    matrix.set_pixel(x, y, grid[y][x])
            matrix.update_display()
            
            # Calculate next generation
            new_grid = [[0 for _ in range(8)] for _ in range(8)]
            
            for y in range(8):
                for x in range(8):
                    neighbors = count_neighbors(grid, x, y)
                    
                    if grid[y][x]:
                        # Live cell
                        if neighbors in [2, 3]:
                            new_grid[y][x] = 1
                    else:
                        # Dead cell
                        if neighbors == 3:
                            new_grid[y][x] = 1
            
            # Check if stable or dead
            if new_grid == grid or all(cell == 0 for row in new_grid for cell in row):
                print(f"\nStable after {generation} generations")
                time.sleep(2)
                # Restart with new pattern
                grid = [[random.randint(0, 1) for _ in range(8)] for _ in range(8)]
                generation = 0
            else:
                grid = new_grid
                generation += 1
            
            print(f"\rGeneration: {generation:4d}", end='')
            time.sleep(0.2)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def spectrum_analyzer():
    """Simulated audio spectrum analyzer"""
    print("\n=== Spectrum Analyzer ===")
    print("Simulated audio visualization")
    print("Press Ctrl+C to stop")
    
    matrix = MAX7219Matrix()
    import random
    
    # Initialize spectrum levels
    levels = [0] * 8
    
    try:
        while True:
            # Update levels with some randomness
            for i in range(8):
                # Add random change
                change = random.randint(-2, 2)
                levels[i] = max(0, min(8, levels[i] + change))
                
                # Gravity effect
                if levels[i] > 0:
                    levels[i] -= random.random() * 0.5
            
            # Display spectrum
            matrix.clear()
            for col in range(8):
                height = int(levels[col])
                for row in range(height):
                    matrix.set_pixel(col, 7 - row, True)
            
            matrix.update_display()
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        matrix.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("8x8 LED Matrix Display Examples")
    print("===============================")
    print(f"Data In: GPIO{DIN_PIN}")
    print(f"Chip Select: GPIO{CS_PIN}")
    print(f"Clock: GPIO{CLK_PIN}")
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic patterns")
        print("2. Scrolling message")
        print("3. Animation demo")
        print("4. Interactive pixel drawing")
        print("5. Brightness control")
        print("6. Clock display")
        print("7. Game of Life")
        print("8. Spectrum analyzer")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_patterns()
        elif choice == '2':
            scrolling_message()
        elif choice == '3':
            animation_demo()
        elif choice == '4':
            pixel_draw()
        elif choice == '5':
            brightness_control()
        elif choice == '6':
            clock_display()
        elif choice == '7':
            game_of_life()
        elif choice == '8':
            spectrum_analyzer()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()