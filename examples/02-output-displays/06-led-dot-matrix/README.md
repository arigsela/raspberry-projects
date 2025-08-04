# 8x8 LED Dot Matrix Display

Control an 8x8 LED matrix display using MAX7219 driver chip with software SPI.

## What You'll Learn
- MAX7219 LED driver communication protocol
- Software SPI implementation
- Matrix display multiplexing
- Pattern generation and animation
- Character bitmap definitions
- Real-time graphics programming
- Conway's Game of Life algorithm

## Hardware Requirements
- Raspberry Pi 5
- 8x8 LED Matrix with MAX7219 driver module
- Jumper wires

## Circuit Diagram

```
MAX7219 LED Matrix Module:
┌─────────────────────┐
│  ● ● ● ● ● ● ● ●   │  8x8 LED Matrix
│  ● ● ● ● ● ● ● ●   │
│  ● ● ● ● ● ● ● ●   │
│  ● ● ● ● ● ● ● ●   │
│  ● ● ● ● ● ● ● ●   │
│  ● ● ● ● ● ● ● ●   │
│  ● ● ● ● ● ● ● ●   │
│  ● ● ● ● ● ● ● ●   │
├─────────────────────┤
│ VCC GND DIN CS CLK  │
└──┬───┬───┬──┬───┬──┘
   │   │   │  │   │
   │   │   │  │   └── GPIO22 (Clock)
   │   │   │  └────── GPIO27 (Chip Select)
   │   │   └───────── GPIO17 (Data In)
   │   └───────────── GND
   └───────────────── 5V

Note: MAX7219 modules typically operate at 5V but
      have 3.3V compatible inputs
```

## Software Dependencies

Install required libraries:
```bash
pip install gpiozero
```

## Running the Program

```bash
cd examples/02-output-displays/06-led-dot-matrix
python led-matrix.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Run with test pattern
make install  # Install dependencies
```

## Code Walkthrough

### MAX7219 Communication
The MAX7219 uses a serial interface similar to SPI:
```python
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
```

### Register Configuration
The MAX7219 has various control registers:
```python
REG_NOOP = 0x00         # No operation
REG_DIGIT0-7 = 0x01-0x08  # Row data
REG_DECODEMODE = 0x09   # BCD decode mode
REG_INTENSITY = 0x0A    # Brightness control
REG_SCANLIMIT = 0x0B    # Number of digits
REG_SHUTDOWN = 0x0C     # Display on/off
REG_DISPLAYTEST = 0x0F  # Test mode
```

### Character Bitmaps
Characters are defined as 8-byte arrays:
```python
CHARACTERS = {
    'A': [
        0b00011000,  # Row 0
        0b00100100,  # Row 1
        0b01000010,  # Row 2
        0b01000010,  # Row 3
        0b01111110,  # Row 4
        0b01000010,  # Row 5
        0b01000010,  # Row 6
        0b00000000   # Row 7
    ]
}
```

### Text Scrolling
Scrolling involves shifting column data:
```python
def scroll_text(self, text, delay=0.1):
    # Convert text to column-based bitmap
    for offset in range(len(full_bitmap) - 7):
        for col in range(8):
            # Copy 8 columns starting from offset
            self.update_display()
            time.sleep(delay)
```

## Key Concepts

### MAX7219 Features
- Controls up to 64 LEDs (8x8 matrix)
- Built-in multiplexing
- 16 brightness levels
- Low power shutdown mode
- No resistors needed (built-in current limiting)

### Display Update Strategy
1. **Row-based updates**: Each register controls one row
2. **Column scanning**: Internal multiplexing handles columns
3. **Double buffering**: Update buffer then display

### Animation Techniques
- **Frame-based**: Update entire display each frame
- **Scrolling**: Shift data horizontally/vertically
- **Morphing**: Transition between patterns
- **Particle effects**: Individual pixel movement

## Available Demos

1. **Basic Patterns**: Static pattern display
2. **Scrolling Message**: Text scrolling
3. **Animation Demo**: Various animated effects
4. **Pixel Drawing**: Interactive drawing tool
5. **Brightness Control**: Fade effects
6. **Clock Display**: Digital time display
7. **Game of Life**: Cellular automaton simulation
8. **Spectrum Analyzer**: Audio visualization simulation

## Troubleshooting

### Display not working
- Check 5V power connection (matrix needs more current)
- Verify all 5 connections (VCC, GND, DIN, CS, CLK)
- Ensure CS pin goes low during communication

### Garbled display
- Check clock timing (may need adjustment)
- Verify bit order (MSB first)
- Ensure proper initialization sequence

### Dim display
- Increase brightness with set_brightness()
- Check power supply current capability
- Some modules have hardware brightness limit

### Flickering
- Reduce delays in display loop
- Check for power supply noise
- Ensure good connections

## Advanced Usage

### Custom Animations
```python
# Create expanding box animation
for size in range(1, 5):
    matrix.clear()
    matrix.draw_rect(4-size, 4-size, size*2, size*2, False)
    matrix.update_display()
    time.sleep(0.1)
```

### Bitmap Fonts
Create custom fonts by defining bitmaps:
```python
# 3x5 font for more characters
SMALL_FONT = {
    '0': [0x7, 0x5, 0x5, 0x5, 0x7],
    '1': [0x2, 0x6, 0x2, 0x2, 0x7]
}
```

### Multiple Matrices
Chain multiple MAX7219 modules:
```python
# Daisy-chain by connecting DOUT to next DIN
# Send 16 bytes for 2 matrices, 24 for 3, etc.
```

## Next Steps
- Try creating custom animations
- Implement a scrolling news ticker
- Create simple games (Snake, Tetris)
- Add sensor-driven visualizations
- Chain multiple matrices for larger displays