# Shared Utility Modules

This directory contains reusable Python modules that are used across multiple tutorial examples.

## Available Modules

### ADC0834
4-Channel 8-bit Analog-to-Digital Converter interface

**Features:**
- 4 analog input channels
- 8-bit resolution (0-255)
- Voltage and percentage reading methods
- Serial communication interface

**Usage:**
```python
from _shared.adc0834 import ADC0834

adc = ADC0834(cs_pin=17, clk_pin=18, di_pin=27, do_pin=22)
value = adc.read_channel(0)  # Read channel 0
voltage = adc.read_voltage(0, vref=3.3)  # Read as voltage
percentage = adc.read_percentage(0)  # Read as percentage
```

### LCD1602
16x2 Character LCD Display with I2C Interface

**Features:**
- I2C communication (default address 0x27)
- Backlight control
- Custom character support
- Text scrolling
- Easy line-based writing

**Usage:**
```python
from _shared.lcd1602 import LCD1602

lcd = LCD1602(i2c_addr=0x27)
lcd.clear()
lcd.write_line("Hello World!", 0)
lcd.write_line("Line 2 Text", 1)
```

## Installation Requirements

```bash
# For LCD1602
sudo apt install python3-smbus2
pip3 install smbus2

# Enable I2C on Raspberry Pi
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable
```

## Module Development Guidelines

When adding new shared modules:

1. **Clear Documentation**: Include docstrings for all classes and methods
2. **Error Handling**: Implement proper error handling and cleanup
3. **Default Values**: Use sensible defaults for GPIO pins
4. **Test Code**: Include standalone test code in `if __name__ == "__main__":`
5. **Dependencies**: Document any required libraries or system configuration

## Common Pin Assignments

To maintain consistency across examples:

### ADC0834 Default Pins:
- CS (Chip Select): GPIO17
- CLK (Clock): GPIO18
- DI (Data In): GPIO27
- DO (Data Out): GPIO22

### I2C Default Pins:
- SDA: GPIO2 (Pin 3)
- SCL: GPIO3 (Pin 5)

## Troubleshooting

### ADC0834 Issues:
- Check wiring, especially DO/DI connections
- Verify 5V power to ADC chip
- Ensure common ground with Pi

### LCD1602 Issues:
- Try alternate I2C address (0x3F)
- Check I2C is enabled: `sudo i2cdetect -y 1`
- Verify pull-up resistors on SDA/SCL
- Adjust contrast potentiometer on LCD board

## Contributing

When contributing new modules:
1. Follow existing code style
2. Include comprehensive error handling
3. Add example usage in module
4. Update this README
5. Test on Raspberry Pi 5