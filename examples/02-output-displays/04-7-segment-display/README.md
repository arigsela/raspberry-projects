# Project 02-04: 7-Segment Display - Digital Number Display

Display numbers, letters, and custom patterns on a 7-segment LED display for counters, clocks, and indicators.

## What You'll Learn

- 7-segment display structure and operation
- Segment mapping for digits and letters
- Common cathode vs common anode
- Creating custom characters
- Animation techniques
- Multiplexing basics (for multiple digits)

## Hardware Requirements

- Raspberry Pi 5
- 1x 7-segment LED display (common cathode or anode)
- 8x 220Ω resistors (one per segment)
- Jumper wires
- Breadboard

## Understanding 7-Segment Displays

### Display Structure
```
     aaaa
    f    b
    f    b
     gggg
    e    c
    e    c
     dddd  dp

Segments labeled a-g plus decimal point (dp)
```

### Pin Configuration
```
Common Cathode Display:
    ┌─────────────┐
    │  a f CC b e │  Top view
    │  ● ● ●  ● ● │
    │             │
    │  ● ● ●  ● ● │
    │  d CC g c dp│
    └─────────────┘

CC = Common Cathode (connect to GND)
For Common Anode, connect to VCC
```

## Circuit Diagram

```
7-Segment Display Connection:

Each segment through resistor to GPIO:

    GPIO17 ---[220Ω]--- a
    GPIO18 ---[220Ω]--- b
    GPIO27 ---[220Ω]--- c
    GPIO22 ---[220Ω]--- d
    GPIO23 ---[220Ω]--- e
    GPIO24 ---[220Ω]--- f
    GPIO25 ---[220Ω]--- g
    GPIO4  ---[220Ω]--- dp

Common Cathode Display:
    CC --------------- GND

Common Anode Display:
    CA --------------- 3.3V

Note: For common anode, logic is inverted
      (GPIO LOW = segment ON)
```

## Pin Connections

| Segment | GPIO Pin | Physical Pin | Purpose |
|---------|----------|--------------|---------|
| a | GPIO17 | Pin 11 | Top horizontal |
| b | GPIO18 | Pin 12 | Top right vertical |
| c | GPIO27 | Pin 13 | Bottom right vertical |
| d | GPIO22 | Pin 15 | Bottom horizontal |
| e | GPIO23 | Pin 16 | Bottom left vertical |
| f | GPIO24 | Pin 18 | Top left vertical |
| g | GPIO25 | Pin 22 | Middle horizontal |
| dp | GPIO4 | Pin 7 | Decimal point |
| CC/CA | - | GND/3.3V | Common connection |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero
sudo apt install -y python3-gpiozero

# No additional dependencies needed
```

## Running the Examples

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/02-output-displays/04-7-segment-display

# Run the 7-segment display examples
python3 seven-segment.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Display Structure

1. **Segment Mapping**
   ```python
   SEGMENT_PINS = {
       'a': 17, 'b': 18, 'c': 27, 'd': 22,
       'e': 23, 'f': 24, 'g': 25, 'dp': 4
   }
   ```

2. **Digit Patterns**
   ```python
   # Which segments to light for each digit
   DIGITS = {
       '0': {'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 0},
       '1': {'a': 0, 'b': 1, 'c': 1, 'd': 0, 'e': 0, 'f': 0, 'g': 0},
       # ... more digits
   }
   ```

3. **Display Control**
   ```python
   def display_digit(self, digit):
       pattern = DIGITS[digit]
       for segment, state in pattern.items():
           if state:
               self.segments[segment].on()
           else:
               self.segments[segment].off()
   ```

## Key Concepts

### Segment Combinations
Each digit/character is formed by specific segment combinations:

| Character | Segments | Binary (gfedcba) |
|-----------|----------|-------------------|
| 0 | a,b,c,d,e,f | 0111111 |
| 1 | b,c | 0000110 |
| 2 | a,b,d,e,g | 1011011 |
| 3 | a,b,c,d,g | 1001111 |
| 4 | b,c,f,g | 1100110 |
| 5 | a,c,d,f,g | 1101101 |
| 6 | a,c,d,e,f,g | 1111101 |
| 7 | a,b,c | 0000111 |
| 8 | a,b,c,d,e,f,g | 1111111 |
| 9 | a,b,c,d,f,g | 1101111 |

### Common Cathode vs Common Anode

| Type | Common Pin | Logic | Current Flow |
|------|------------|-------|--------------|
| Common Cathode | GND | HIGH = ON | GPIO → LED → GND |
| Common Anode | VCC | LOW = ON | VCC → LED → GPIO |

### Current Limiting
- Each segment is an LED requiring current limiting
- 220Ω resistors limit current to ~10mA per segment
- Maximum current with all segments: 8 × 10mA = 80mA

## Common Applications

### 1. Digital Clocks
- Time display
- Alarm clocks
- Countdown timers
- Stopwatches

### 2. Counters
- People counters
- Production counters
- Score displays
- Lap counters

### 3. Measurement Displays
- Temperature readouts
- Voltage meters
- Speed displays
- Distance meters

### 4. Status Indicators
- Error codes
- Channel numbers
- Mode displays
- Level indicators

### 5. Games
- Dice simulators
- Score keeping
- Random numbers
- Reaction timers

## Display Techniques

### Scrolling Text
```python
def scroll_text(display, text, delay=0.5):
    """Scroll text across display"""
    text = text.upper()
    for char in text:
        if char in DIGITS:
            display.display_digit(char)
            time.sleep(delay)
        else:
            display.clear()
            time.sleep(delay * 0.5)
```

### Blinking Display
```python
def blink_digit(display, digit, times=3):
    """Blink a digit"""
    for _ in range(times):
        display.display_digit(digit)
        time.sleep(0.3)
        display.clear()
        time.sleep(0.3)
```

### Fading Effect (with PWM)
```python
# Note: Requires PWMLED instead of LED
def fade_digit(display, digit, fade_time=1):
    """Fade digit in/out"""
    # Set all segments for digit
    # Then use PWM to fade brightness
    pass
```

## Custom Characters

### Creating Letters
```python
# Additional displayable characters
LETTERS = {
    'A': ['a', 'b', 'c', 'e', 'f', 'g'],     # A
    'b': ['c', 'd', 'e', 'f', 'g'],          # b (lowercase)
    'C': ['a', 'd', 'e', 'f'],               # C
    'd': ['b', 'c', 'd', 'e', 'g'],          # d (lowercase)
    'E': ['a', 'd', 'e', 'f', 'g'],          # E
    'F': ['a', 'e', 'f', 'g'],               # F
    'H': ['b', 'c', 'e', 'f', 'g'],          # H
    'L': ['d', 'e', 'f'],                    # L
    'P': ['a', 'b', 'e', 'f', 'g'],          # P
    'U': ['b', 'c', 'd', 'e', 'f'],          # U
}
```

### Special Symbols
```python
SYMBOLS = {
    '-': ['g'],                    # Minus
    '_': ['d'],                    # Underscore
    '°': ['a', 'b', 'f', 'g'],    # Degree symbol
    '=': ['d', 'g'],              # Equals
    '[': ['a', 'd', 'e', 'f'],    # Left bracket
    ']': ['a', 'b', 'c', 'd'],    # Right bracket
}
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No display | Check common pin connection, verify power |
| Dim segments | Check resistor values, ensure good connections |
| Wrong segments | Verify pin mapping, check display datasheet |
| Inverted display | Wrong common type (cathode/anode) |
| Flickering | Check connections, add delays between updates |

## Advanced Techniques

### Brightness Control
```python
# Using PWM for brightness control
from gpiozero import PWMLED

class DimmableDisplay:
    def __init__(self, pins, brightness=1.0):
        self.segments = {}
        for segment, pin in pins.items():
            self.segments[segment] = PWMLED(pin)
        self.brightness = brightness
    
    def set_brightness(self, level):
        """Set display brightness (0.0 to 1.0)"""
        self.brightness = level
```

### Character Animation
```python
def animate_loading(display):
    """Rotating loading animation"""
    sequence = [
        ['a'], ['b'], ['c'], ['d'], ['e'], ['f']
    ]
    for _ in range(10):
        for segments in sequence:
            display.display_segments(segments)
            time.sleep(0.1)
```

### Error Display
```python
def display_error(display, code):
    """Flash error code"""
    # Flash 'E'
    for _ in range(3):
        display.display_digit('E')
        time.sleep(0.2)
        display.clear()
        time.sleep(0.2)
    
    # Show error code
    display.display_digit(str(code))
    time.sleep(1)
```

## Multi-Digit Displays

For displaying multiple digits, you'll need:
1. **Multiple displays**: Wire each similarly
2. **Digit selection**: Use transistors to enable each digit
3. **Multiplexing**: Rapidly switch between digits

```python
# Concept for 4-digit display
def display_number(displays, number):
    """Display multi-digit number"""
    digits = str(number).zfill(4)
    for i, digit in enumerate(digits):
        displays[i].display_digit(digit)
```

## Performance Optimization

### Lookup Tables
```python
# Pre-calculate segment states
SEGMENT_LUT = {
    '0': 0b00111111,  # Segments a-f on, g off
    '1': 0b00000110,  # Segments b,c on
    # ... more entries
}
```

### Direct Port Manipulation
For faster updates with multiple digits, consider:
- Using shift registers (74HC595)
- SPI/I2C display drivers (MAX7219)
- Dedicated display modules

## Project Ideas

1. **Digital Clock**
   - Show hours and minutes
   - Add alarm function
   - Temperature display

2. **Reaction Timer**
   - Random start delay
   - Display reaction time
   - High score tracking

3. **Thermometer**
   - Read temperature sensor
   - Display in C or F
   - Min/max recording

4. **Counter**
   - Button increment/decrement
   - Preset values
   - Direction control

5. **Dice Game**
   - Random number generation
   - Animation before result
   - Multiple dice support

## Integration Examples

### With Buttons
```python
# Up/down counter
up_button = Button(2)
down_button = Button(3)
counter = 0

up_button.when_pressed = lambda: increment()
down_button.when_pressed = lambda: decrement()
```

### With Sensors
```python
# Temperature display
def show_temperature():
    temp = read_temperature()
    tens = temp // 10
    units = temp % 10
    
    display.display_digit(tens)
    time.sleep(0.5)
    display.display_digit(units)
```

## Safety Notes

1. **Current Limiting**
   - Always use resistors
   - Calculate total current draw
   - Stay within GPIO limits

2. **Static Protection**
   - Handle displays carefully
   - Ground yourself
   - Use anti-static workspace

## Next Steps

After mastering single 7-segment displays:
1. Build multi-digit displays
2. Add display drivers (MAX7219)
3. Create LED matrix displays
4. Implement alpha-numeric displays
5. Design custom PCBs

## Resources

- [7-Segment Display Tutorial](https://www.electronics-tutorials.ws/blog/7-segment-display-tutorial.html)
- [Common Anode vs Cathode](https://components101.com/7-segment-display-pinout-working-datasheet)
- [GPIO Zero LED Control](https://gpiozero.readthedocs.io/en/stable/api_output.html#led)
- [Multiplexing Techniques](https://learn.sparkfun.com/tutorials/using-the-serial-7-segment-display)