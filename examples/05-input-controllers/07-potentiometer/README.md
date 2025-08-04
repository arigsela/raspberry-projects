# Project 05-07: Potentiometer - Analog Input Control

Read analog values from a potentiometer for variable control, volume adjustment, and parameter tuning in your projects.

## What You'll Learn

- Analog vs digital signals
- ADC (Analog-to-Digital Conversion)
- Using MCP3008 ADC with Raspberry Pi
- Reading potentiometer values
- Mapping analog values to outputs
- Creating smooth control interfaces

## Hardware Requirements

- Raspberry Pi 5
- 1x Potentiometer (10kΩ recommended)
- 1x MCP3008 ADC chip
- Optional: LED for brightness control
- Optional: Servo for position control
- Optional: Passive buzzer for frequency control
- Jumper wires
- Breadboard

## Understanding Potentiometers

### How Potentiometers Work
```
    Potentiometer Internal Structure:
    
    Terminal 1 ────[████████████████]──── Terminal 3
                          ↑
                        Wiper
                    (Terminal 2)
    
    Rotating shaft moves wiper along resistive track
```

- **Three terminals**: Two ends + wiper (middle)
- **Variable resistance**: Between wiper and ends
- **Voltage divider**: Outputs 0V to VCC

### Types of Potentiometers
| Type | Characteristics | Use Cases |
|------|----------------|-----------|
| Linear | Resistance changes linearly | Volume, brightness |
| Logarithmic | Non-linear change | Audio applications |
| Rotary | Continuous rotation | Knob controls |
| Slide | Linear motion | Faders, sliders |
| Trimmer | Small, preset | Calibration |

## Circuit Diagram

```
MCP3008 ADC Connection:

                        MCP3008
                    ┌─────────────┐
    Potentiometer   │             │
    Terminal 1 ──── │ CH0    VDD  │──── 3.3V
           ↓        │             │
       [10kΩ POT]   │ CH1    VREF │──── 3.3V
           ↓        │             │
    Terminal 2 ──── │ CH2    AGND │──── GND
    (Wiper to CH0)  │             │
           ↓        │ CH3    CLK  │──── GPIO11 (SCLK)
    Terminal 3 ──── │             │
         │          │ CH4    DOUT │──── GPIO9  (MISO)
        GND         │             │
                    │ CH5    DIN  │──── GPIO10 (MOSI)
                    │             │
                    │ CH6    CS   │──── GPIO8  (CE0)
                    │             │
                    │ CH7    DGND │──── GND
                    └─────────────┘

Simple Potentiometer Wiring:
    3.3V ──── Terminal 1
              Terminal 2 (Wiper) ──── MCP3008 CH0
    GND  ──── Terminal 3

Optional Output Devices:
    LED:    GPIO17 ---[220Ω]--- LED --- GND
    Servo:  GPIO22 --- Servo Signal
    Buzzer: GPIO18 --- Buzzer (+)
```

## Pin Connections

### MCP3008 to Raspberry Pi
| MCP3008 Pin | Raspberry Pi Pin | GPIO | Function |
|-------------|------------------|------|----------|
| VDD | Pin 1 | 3.3V | Power |
| VREF | Pin 1 | 3.3V | Reference voltage |
| AGND | Pin 6 | GND | Analog ground |
| CLK | Pin 23 | GPIO11 | SPI clock |
| DOUT | Pin 21 | GPIO9 | SPI MISO |
| DIN | Pin 19 | GPIO10 | SPI MOSI |
| CS/SHDN | Pin 24 | GPIO8 | SPI CE0 |
| DGND | Pin 6 | GND | Digital ground |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero and SPI support
sudo apt install -y python3-gpiozero python3-spidev

# Enable SPI interface
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable

# Verify SPI is enabled
ls /dev/spi*
# Should show: /dev/spidev0.0 /dev/spidev0.1
```

## Running the Examples

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/05-input-controllers/07-potentiometer

# Run the potentiometer examples
python3 potentiometer.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Reading

1. **MCP3008 Setup**
   ```python
   from gpiozero import MCP3008
   
   pot = MCP3008(channel=0)  # Potentiometer on CH0
   ```

2. **Reading Values**
   ```python
   value = pot.value  # Returns 0.0 to 1.0
   voltage = value * 3.3  # Convert to voltage
   ```

3. **Value Mapping**
   ```python
   # Map to custom range
   min_val = 0
   max_val = 100
   mapped = min_val + (value * (max_val - min_val))
   ```

### Controlling Outputs

```python
# LED brightness
led.value = pot.value

# Servo position (-1 to 1)
servo.value = (pot.value * 2) - 1

# Frequency (100-2000 Hz)
frequency = 100 + (pot.value * 1900)
```

## Key Concepts

### Analog-to-Digital Conversion
- **Resolution**: MCP3008 is 10-bit (0-1023)
- **Sampling**: How often to read values
- **Reference voltage**: Determines max reading
- **Quantization**: Discrete steps in digital

### ADC Calculation
```
Digital Value = (Analog Voltage / Reference Voltage) × 1023

For 1.65V input with 3.3V reference:
Digital = (1.65 / 3.3) × 1023 = 511
```

### Noise and Filtering
```python
# Simple moving average
class FilteredPot:
    def __init__(self, channel, window=10):
        self.pot = MCP3008(channel)
        self.window = window
        self.values = []
    
    def read(self):
        self.values.append(self.pot.value)
        if len(self.values) > self.window:
            self.values.pop(0)
        return sum(self.values) / len(self.values)
```

## Common Applications

### 1. Volume Control
- Audio equipment
- Speaker systems
- Headphone amplifiers
- Mixing consoles

### 2. Display Brightness
- LCD backlights
- LED strips
- Monitor controls
- Ambient lighting

### 3. Motor Speed Control
- DC motor speed
- Fan controllers
- Pump flow rate
- Servo positioning

### 4. User Interfaces
- Menu navigation
- Value selection
- Parameter adjustment
- Game controllers

### 5. Sensor Calibration
- Threshold setting
- Offset adjustment
- Gain control
- Range limiting

## Advanced Techniques

### Non-Linear Mapping
```python
# Logarithmic response (audio taper)
def log_map(value):
    if value == 0:
        return 0
    return math.pow(10, (value - 1) * 2)

# Exponential response
def exp_map(value):
    return math.pow(value, 2)

# S-curve response
def s_curve(value):
    return 0.5 * (1 + math.tanh(4 * (value - 0.5)))
```

### Dead Zone Implementation
```python
def apply_deadzone(value, threshold=0.05):
    if value < threshold:
        return 0
    elif value > (1 - threshold):
        return 1
    else:
        # Scale remaining range
        return (value - threshold) / (1 - 2 * threshold)
```

### Hysteresis
```python
class HysteresisPot:
    def __init__(self, channel, threshold=0.02):
        self.pot = MCP3008(channel)
        self.threshold = threshold
        self.last_value = 0
    
    def read(self):
        current = self.pot.value
        if abs(current - self.last_value) > self.threshold:
            self.last_value = current
        return self.last_value
```

### Multi-Turn Detection
```python
class MultiTurnPot:
    def __init__(self, channel):
        self.pot = MCP3008(channel)
        self.last_raw = 0.5
        self.turns = 0
        self.value = 0
    
    def read(self):
        raw = self.pot.value
        
        # Detect wrap-around
        if self.last_raw > 0.9 and raw < 0.1:
            self.turns += 1
        elif self.last_raw < 0.1 and raw > 0.9:
            self.turns -= 1
        
        self.last_raw = raw
        self.value = self.turns + raw
        return self.value
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No readings | Check SPI enabled, verify wiring |
| Always max/min | Check potentiometer connections |
| Jumpy values | Add filtering, check ground |
| Wrong range | Verify reference voltage |
| Slow response | Reduce sampling delay |

## Performance Optimization

### Sampling Rate
```python
# Adjust based on application
FAST_SAMPLE = 0.001    # 1000 Hz for audio
NORMAL_SAMPLE = 0.01   # 100 Hz for controls
SLOW_SAMPLE = 0.1      # 10 Hz for displays
```

### Efficient Reading
```python
# Read only when needed
class ChangeDetector:
    def __init__(self, pot, threshold=0.01):
        self.pot = pot
        self.threshold = threshold
        self.last = pot.value
    
    def has_changed(self):
        current = self.pot.value
        if abs(current - self.last) > self.threshold:
            self.last = current
            return True
        return False
```

### Multiple Potentiometers
```python
# Read all channels efficiently
pots = [MCP3008(channel=i) for i in range(8)]

def read_all():
    return [pot.value for pot in pots]
```

## Calibration Guide

### Hardware Calibration
1. Measure actual resistance range
2. Check for dead zones at extremes
3. Verify linear response
4. Test under load

### Software Calibration
```python
class CalibratedPot:
    def __init__(self, channel):
        self.pot = MCP3008(channel)
        self.min_cal = 0.05  # Measured minimum
        self.max_cal = 0.95  # Measured maximum
    
    def read(self):
        raw = self.pot.value
        # Map to full range
        value = (raw - self.min_cal) / (self.max_cal - self.min_cal)
        return max(0, min(1, value))
```

## Integration Examples

### With LCD Display
```python
# Show potentiometer value on LCD
lcd.write_line(f"Volume: {int(pot.value * 100)}%", 0)
lcd.write_line(f"[{'=' * int(pot.value * 16)}]", 1)
```

### With PWM LED
```python
# Smooth LED fading
led = PWMLED(17)
while True:
    led.pulse(fade_in_time=pot.value, fade_out_time=pot.value)
```

### With Data Logging
```python
# Log values to file
with open('pot_data.csv', 'w') as f:
    f.write("timestamp,value,voltage\n")
    while True:
        value = pot.value
        voltage = value * 3.3
        f.write(f"{time.time()},{value},{voltage}\n")
        time.sleep(0.1)
```

## Project Ideas

1. **MIDI Controller**
   - Multiple pots for parameters
   - Send MIDI CC messages
   - LED feedback

2. **Color Mixer**
   - Three pots for RGB
   - Control LED strip
   - Display color codes

3. **Game Controller**
   - Analog stick simulation
   - Steering wheel
   - Throttle control

4. **Environmental Controller**
   - Temperature setpoint
   - Fan speed control
   - Light dimming

5. **Audio Mixer**
   - Channel faders
   - EQ controls
   - Master volume

## MCP3008 Specifications

| Parameter | Value |
|-----------|-------|
| Resolution | 10-bit (1024 levels) |
| Channels | 8 single-ended |
| Sample Rate | 200 ksps max |
| Voltage Range | 0V to VREF |
| Interface | SPI |
| Power | 2.7V to 5.5V |

## Safety Notes

1. **Voltage Limits**
   - Never exceed 3.3V on inputs
   - Use voltage dividers for 5V
   - Check potentiometer rating

2. **Static Protection**
   - Ground yourself
   - Use anti-static mat
   - Handle chips carefully

## Next Steps

After mastering potentiometers:
1. Try other analog sensors
2. Build MIDI controllers
3. Create custom input devices
4. Implement PID control
5. Design audio equipment

## Resources

- [MCP3008 Datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/21295d.pdf)
- [GPIO Zero MCP3008](https://gpiozero.readthedocs.io/en/stable/api_spi.html#mcp3008)
- [SPI Communication](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/)
- [ADC Tutorial](https://learn.sparkfun.com/tutorials/analog-to-digital-conversion)