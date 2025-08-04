# Project 02-07: I2C LCD1602 - Character Display with I2C Interface

Master I2C communication and character LCD displays for user interfaces and data visualization.

## What You'll Learn

- I2C protocol and communication
- Character LCD control and features
- Custom character creation
- Text scrolling and animations
- Real-time data display
- Menu systems and user interfaces

## Hardware Requirements

- Raspberry Pi 5
- 1x LCD1602 display with I2C backpack
- 4x Jumper wires
- Pull-up resistors (usually included on I2C backpack)

## Circuit Diagram

```
LCD I2C Module        Raspberry Pi
VCC --------------- 5V (Pin 2)
GND --------------- GND (Pin 6)
SDA --------------- GPIO2/SDA1 (Pin 3)
SCL --------------- GPIO3/SCL1 (Pin 5)

I2C Backpack Pinout:
┌─────────────┐
│ GND VCC SDA SCL │ <- To Raspberry Pi
└─────────────┘
        ║
┌───────────────────┐
│   LCD1602 Display │
│ ┌───────────────┐ │
│ │Hello, World!  │ │
│ │Raspberry Pi 5 │ │
│ └───────────────┘ │
└───────────────────┘
```

## Pin Connections

| LCD I2C Pin | Raspberry Pi Pin | GPIO | Notes |
|-------------|------------------|------|-------|
| VCC | Pin 2 | 5V | Power supply |
| GND | Pin 6 | GND | Common ground |
| SDA | Pin 3 | GPIO2 | I2C Data |
| SCL | Pin 5 | GPIO3 | I2C Clock |

## I2C Setup

### Enable I2C Interface
```bash
# Method 1: Using raspi-config
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable

# Method 2: Command line
sudo raspi-config nonint do_i2c 0

# Reboot after enabling
sudo reboot
```

### Install Dependencies
```bash
# Update package list
sudo apt update

# Install I2C tools
sudo apt install -y i2c-tools python3-smbus2

# Install Python library
pip3 install smbus2
```

### Detect I2C Device
```bash
# Scan I2C bus for devices
sudo i2cdetect -y 1

# Output should show device address (usually 0x27 or 0x3F):
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- 27 -- -- -- -- -- -- -- --
```

## Running the Programs

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/02-output-displays/07-i2c-lcd1602

# Run the main demo
python3 lcd-display.py

# Or run the clock application
python3 lcd-clock.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Display (lcd-display.py)

1. **LCD Initialization**
   ```python
   from _shared.lcd1602 import LCD1602
   lcd = LCD1602(i2c_addr=0x27)
   ```
   - Uses shared module for consistency
   - Auto-detects I2C bus

2. **Text Display**
   ```python
   lcd.clear()
   lcd.write_line("Hello, World!", 0)
   lcd.write_line("Line 2 Text", 1)
   ```
   - Line-based writing
   - Automatic padding/truncation

3. **Custom Characters**
   ```python
   lcd.create_char(0, pattern)
   lcd.write(chr(0))  # Display custom char
   ```
   - 8 custom character slots (0-7)
   - 5x8 pixel patterns

### Clock Application (lcd-clock.py)

1. **Real-time Updates**
   - System time display
   - CPU temperature monitoring
   - Network information

2. **Multiple Modes**
   - Clock with temperature
   - Countdown timer
   - Stopwatch
   - System info display

## Key Concepts

### I2C Protocol
- **Two-wire Interface**: SDA (data) and SCL (clock)
- **Addressing**: Each device has unique 7-bit address
- **Multi-master**: Multiple devices can initiate communication
- **Speed**: Standard (100kHz), Fast (400kHz), High-speed (3.4MHz)

### LCD1602 Features
- **Display**: 16 characters × 2 lines
- **Character Set**: ASCII + Japanese
- **Custom Characters**: 8 user-definable
- **Cursor Control**: Position, visibility, blinking
- **Backlight**: Software controllable

### I2C Backpack (PCF8574)
- **Purpose**: Reduce pins from 16 to 4
- **8-bit I/O Expander**: Maps to LCD pins
- **Address Selection**: Jumpers set address
- **Contrast**: Onboard potentiometer

## Custom Character Creation

### Character Designer
```python
# 5x8 pixel grid (example: heart)
heart = [
    0b00000,  # Row 1: ·····
    0b01010,  # Row 2: ·█·█·
    0b11111,  # Row 3: █████
    0b11111,  # Row 4: █████
    0b01110,  # Row 5: ·███·
    0b00100,  # Row 6: ··█··
    0b00000,  # Row 7: ·····
    0b00000   # Row 8: ·····
]
```

### Binary to Hex Conversion
```python
# Convert binary to hex list
heart_hex = [0x00, 0x0A, 0x1F, 0x1F, 0x0E, 0x04, 0x00, 0x00]
```

### Available Characters
- Standard ASCII (32-127)
- Custom slots (0-7)
- Extended characters (128-255)
- Japanese kana (certain models)

## Common Display Patterns

### Progress Bar
```python
def show_progress(lcd, percent):
    filled = int((percent / 100) * 16)
    bar = "█" * filled + "░" * (16 - filled)
    lcd.write_line(bar, 1)
```

### Scrolling Text
```python
def scroll_text(lcd, text, delay=0.3):
    padded = text + "    "
    for i in range(len(padded)):
        lcd.write_line(padded[i:i+16], 0)
        time.sleep(delay)
```

### Menu System
```python
menu_items = ["Option 1", "Option 2", "Option 3"]
selected = 0

lcd.write_line("> " + menu_items[selected], 0)
lcd.write_line("  " + menu_items[selected + 1], 1)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No display | Check power (5V), adjust contrast pot |
| Blocks/garbage | Wrong I2C address, try 0x3F instead of 0x27 |
| Dim display | Adjust contrast potentiometer on backpack |
| No I2C device found | Enable I2C, check connections |
| IOError | I2C not enabled or wrong address |
| Garbled text | Timing issues, reduce I2C speed |

## I2C Address Issues

### Finding Correct Address
```bash
# Scan for all I2C devices
i2cdetect -y 1

# Common addresses:
# 0x27 - Default for many modules
# 0x3F - Alternative common address
# 0x20-0x27 - PCF8574 range
# 0x38-0x3F - PCF8574A range
```

### Address Jumpers
Many I2C backpacks have jumpers (A0, A1, A2):
- All open: 0x27 (or 0x3F)
- A0 closed: 0x26 (or 0x3E)
- A1 closed: 0x25 (or 0x3D)
- A0+A1 closed: 0x24 (or 0x3C)

## Advanced Features

### Multi-line Scrolling
```python
def scroll_vertical(lcd, lines, delay=1):
    for i in range(len(lines) - 1):
        lcd.write_line(lines[i], 0)
        lcd.write_line(lines[i + 1], 1)
        time.sleep(delay)
```

### Blinking Text
```python
def blink_text(lcd, text, times=3):
    for _ in range(times):
        lcd.write_line(text, 0)
        time.sleep(0.5)
        lcd.write_line(" " * 16, 0)
        time.sleep(0.5)
```

### Data Logging Display
```python
def display_sensor_data(lcd, temp, humidity):
    lcd.write_line(f"Temp: {temp:.1f}°C", 0)
    lcd.write_line(f"Humidity: {humidity}%", 1)
```

## Project Ideas

1. **Weather Station Display**
   - Temperature, humidity, pressure
   - Weather icons using custom chars
   - Forecast scrolling

2. **System Monitor**
   - CPU usage and temperature
   - Memory and disk usage
   - Network statistics

3. **Music Player Interface**
   - Now playing information
   - Progress bar
   - Volume indicator

4. **Smart Home Controller**
   - Room temperatures
   - Light controls
   - Security status

5. **Data Logger Display**
   - Real-time sensor values
   - Min/max tracking
   - Graphical trends

## Performance Tips

### Update Optimization
- Only update changed characters
- Use cursor positioning wisely
- Batch updates when possible

### Power Saving
- Turn off backlight when idle
- Reduce update frequency
- Use display sleep modes

## LCD1602 Specifications

| Parameter | Value |
|-----------|-------|
| Display Format | 16×2 characters |
| Character Size | 5×8 dots |
| Operating Voltage | 5V |
| Backlight | LED (blue/yellow) |
| Interface | Parallel or I2C |
| Viewing Angle | 170° |
| Response Time | 150ms |
| Operating Temp | -20°C to +70°C |

## Next Steps

After mastering LCD displays:
1. Create menu-driven interfaces
2. Build data visualization projects
3. Combine with sensors for monitoring
4. Try OLED displays for graphics
5. Implement touch interfaces

## Alternative Displays

- **LCD2004**: 20×4 characters
- **OLED SSD1306**: 128×64 pixels, graphics
- **Nokia 5110**: 84×48 pixels, low power
- **TFT Displays**: Full color, touch capable
- **E-Ink**: Ultra-low power, persistent

## Resources

- [HD44780 Datasheet](https://www.sparkfun.com/datasheets/LCD/HD44780.pdf)
- [PCF8574 I2C Expander](https://www.nxp.com/docs/en/data-sheet/PCF8574_PCF8574A.pdf)
- [I2C Protocol Specification](https://www.nxp.com/docs/en/user-guide/UM10204.pdf)
- [Character LCD Tutorial](https://learn.adafruit.com/character-lcds)
- [Custom Character Generator](https://maxpromer.github.io/LCD-Character-Creator/)