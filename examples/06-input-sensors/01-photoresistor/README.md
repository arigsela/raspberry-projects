# Project 06-01: Photoresistor (LDR) - Light Sensing

Measure ambient light levels with a photoresistor for automatic lighting, environmental monitoring, and light-activated controls.

## What You'll Learn

- How photoresistors work
- Light-dependent resistance
- Voltage divider circuits
- ADC integration with MCP3008
- Automatic light control
- Light data analysis

## Hardware Requirements

- Raspberry Pi 5
- 1x Photoresistor (LDR)
- 1x 10kΩ resistor (for voltage divider)
- 1x MCP3008 ADC
- Optional: LEDs for output
- Optional: Buzzer for alarms
- Jumper wires
- Breadboard

## Understanding Photoresistors

### How LDRs Work
```
Light-Dependent Resistor (LDR):

    Bright Light           Dark
    ═══════════           ═════════════════════
    Low Resistance         High Resistance
    (~1kΩ)                (~1MΩ)
    
    More photons → More conductivity → Less resistance
```

### Common Types
| Type | Spectral Peak | Response Time | Applications |
|------|---------------|---------------|--------------|
| CdS (Cadmium Sulfide) | 550nm (green) | 20-50ms | General purpose |
| CdSe (Cadmium Selenide) | 730nm (red) | 10-20ms | Red light sensing |
| PbS (Lead Sulfide) | 1000-3000nm (IR) | 100-500µs | Infrared detection |

## Circuit Diagram

```
Voltage Divider Circuit with LDR:

    3.3V ────┬──── R1 (10kΩ) ────┬──── GND
             │                    │
             │                    ├──── To MCP3008 CH0
             │                    │
             └──── LDR ──────────┘
             
    Vout = 3.3V × R1 / (R1 + LDR)
    
    Bright: LDR = 1kΩ  → Vout = 3.0V (high)
    Dark:   LDR = 100kΩ → Vout = 0.32V (low)

Complete MCP3008 Connection:
                        MCP3008
                    ┌─────────────┐
    LDR Divider ──→ │ CH0    VDD  │──── 3.3V
                    │             │
                    │ CH1    VREF │──── 3.3V
                    │             │
                    │ CH2    AGND │──── GND
                    │             │
                    │ CH3    CLK  │──── GPIO11 (SCLK)
                    │             │
                    │ CH4    DOUT │──── GPIO9  (MISO)
                    │             │
                    │ CH5    DIN  │──── GPIO10 (MOSI)
                    │             │
                    │ CH6    CS   │──── GPIO8  (CE0)
                    │             │
                    │ CH7    DGND │──── GND
                    └─────────────┘

Output Devices (Optional):
    LED:     GPIO17 ---[220Ω]--- LED --- GND
    Buzzer:  GPIO22 --- Buzzer (+)
    Bar Graph: GPIO18,23,24,25,8,7,12,16,20,21
```

## Pin Connections

### Photoresistor Circuit
| Component | Connection | Purpose |
|-----------|------------|---------|
| 3.3V | Top of 10kΩ resistor | Reference voltage |
| 10kΩ resistor | Between 3.3V and CH0 | Pull-up resistor |
| LDR | Between CH0 and GND | Variable resistance |
| MCP3008 CH0 | Voltage divider output | ADC input |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install required packages
sudo apt install -y python3-gpiozero python3-spidev

# Enable SPI interface
sudo raspi-config
# Navigate to: Interface Options > SPI > Enable

# Verify SPI
ls /dev/spi*
```

## Running the Examples

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/06-input-sensors/01-photoresistor

# Run the photoresistor examples
python3 photoresistor.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Light Reading

1. **Setup ADC**
   ```python
   from gpiozero import MCP3008
   
   ldr = MCP3008(channel=0)
   ```

2. **Read Light Level**
   ```python
   light_level = ldr.value  # 0.0 (dark) to 1.0 (bright)
   ```

3. **Interpret Values**
   ```python
   if light_level < 0.1:
       condition = "Very Dark"
   elif light_level < 0.3:
       condition = "Dark"
   elif light_level < 0.6:
       condition = "Normal"
   else:
       condition = "Bright"
   ```

### Automatic Control

```python
# Night light example
DARKNESS_THRESHOLD = 0.2

if ldr.value < DARKNESS_THRESHOLD:
    led.on()  # Turn on light when dark
else:
    led.off()  # Turn off when bright
```

## Key Concepts

### Resistance vs Light
```
Typical LDR Response:
                    
Resistance (Ω)
1M │ ●
   │  ●
100k│   ●
   │    ●●
10k│      ●●●
   │         ●●●●●
1k │              ●●●●●●
   └────────────────────→
   0.1  1   10  100  1000
   Light Intensity (lux)
```

### Light Units
| Unit | Description | Example |
|------|-------------|---------|
| Lux | Illuminance | 0.1 = Full moon |
| | | 400 = Office |
| | | 10,000 = Daylight |
| | | 100,000 = Direct sun |

### Voltage Divider Math
```python
# Calculate LDR resistance from ADC reading
def calculate_resistance(adc_value, r_fixed=10000):
    if adc_value == 0:
        return float('inf')
    return r_fixed * (1 / adc_value - 1)

# Estimate lux (requires calibration)
def resistance_to_lux(resistance):
    # Rough approximation
    return 500 / (resistance / 1000)
```

## Common Applications

### 1. Automatic Lighting
- Street lights
- Night lights
- Porch lights
- Display backlights

### 2. Light Meters
- Photography
- Plant monitoring
- Solar panels
- Weather stations

### 3. Security Systems
- Beam break detection
- Laser trip wires
- Shadow detection
- Intrusion alarms

### 4. User Interfaces
- Gesture detection
- Proximity sensing
- Touch-free switches
- Light pens

### 5. Environmental Monitoring
- Day/night detection
- Cloud coverage
- Indoor/outdoor sensing
- Seasonal tracking

## Advanced Techniques

### Calibration
```python
class CalibratedLDR:
    def __init__(self, channel):
        self.ldr = MCP3008(channel)
        self.dark_reading = 0.05   # Measured in darkness
        self.bright_reading = 0.95  # Measured in bright light
    
    def get_normalized(self):
        raw = self.ldr.value
        # Normalize to 0-1 range
        normalized = (raw - self.dark_reading) / (self.bright_reading - self.dark_reading)
        return max(0, min(1, normalized))
```

### Averaging Filter
```python
class FilteredLDR:
    def __init__(self, channel, samples=10):
        self.ldr = MCP3008(channel)
        self.samples = samples
        self.readings = []
    
    def read(self):
        self.readings.append(self.ldr.value)
        if len(self.readings) > self.samples:
            self.readings.pop(0)
        return sum(self.readings) / len(self.readings)
```

### Rate of Change Detection
```python
class LightChangeDetector:
    def __init__(self, ldr, threshold=0.1):
        self.ldr = ldr
        self.threshold = threshold
        self.last_value = ldr.value
        self.last_time = time.time()
    
    def detect_change(self):
        current = self.ldr.value
        current_time = time.time()
        
        rate = abs(current - self.last_value) / (current_time - self.last_time)
        
        if rate > self.threshold:
            direction = "increasing" if current > self.last_value else "decreasing"
            self.last_value = current
            self.last_time = current_time
            return True, direction, rate
        
        return False, None, rate
```

### Hysteresis Control
```python
class HysteresisLight:
    def __init__(self, ldr, led):
        self.ldr = ldr
        self.led = led
        self.on_threshold = 0.2   # Turn on when darker
        self.off_threshold = 0.3  # Turn off when brighter
        self.is_on = False
    
    def update(self):
        level = self.ldr.value
        
        if not self.is_on and level < self.on_threshold:
            self.led.on()
            self.is_on = True
        elif self.is_on and level > self.off_threshold:
            self.led.off()
            self.is_on = False
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Always reads high | Check LDR orientation, verify resistor value |
| Always reads low | Check connections, test LDR with multimeter |
| Erratic readings | Add capacitor (0.1µF) across LDR |
| Slow response | Normal for CdS, consider phototransistor |
| Wrong threshold | Calibrate for your lighting conditions |

## Performance Optimization

### Response Time
```python
# LDR response is non-linear
def compensate_response(current, previous, alpha=0.3):
    # Exponential moving average
    return alpha * current + (1 - alpha) * previous
```

### Power Saving
```python
# Read less frequently in stable conditions
def adaptive_sampling(ldr):
    last_value = ldr.value
    stable_count = 0
    
    while True:
        current = ldr.value
        
        if abs(current - last_value) < 0.02:
            stable_count += 1
            delay = min(5.0, 0.1 * stable_count)
        else:
            stable_count = 0
            delay = 0.1
        
        last_value = current
        time.sleep(delay)
```

## Project Ideas

1. **Smart Room Lighting**
   - Multiple zones
   - Gradual transitions
   - Energy monitoring

2. **Plant Growth Monitor**
   - Daily light integral
   - Grow light control
   - Data logging

3. **Solar Tracker**
   - Follow sun position
   - Maximize panel efficiency
   - Weather detection

4. **Light Painting**
   - Long exposure trigger
   - Pattern detection
   - Art installations

5. **Sleep/Wake System**
   - Circadian lighting
   - Gradual wake-up
   - Sleep tracking

## Integration Examples

### With Temperature Sensor
```python
# Greenhouse controller
if temp > 25 and light > 0.7:
    # Too hot and bright - close blinds
    servo.angle = 0
elif temp < 20 or light < 0.3:
    # Too cold or dark - open blinds
    servo.angle = 90
```

### With Motion Sensor
```python
# Smart lighting
if motion_detected and light_level < 0.3:
    # Someone present and dark
    lights.on()
```

### With RTC
```python
# Time-aware lighting
if 6 <= hour <= 22:  # Daytime hours
    threshold = 0.3
else:  # Nighttime
    threshold = 0.1
```

## Spectral Response

### Typical CdS Response
```
Response
100% │     ╱╲
     │    ╱  ╲
 50% │   ╱    ╲
     │  ╱      ╲
  0% │ ╱        ╲
     └────────────→
     400  550  700
     Wavelength (nm)
     
Peak sensitivity around 550nm (green light)
```

## Safety Notes

1. **Electrical Safety**
   - Use appropriate resistor values
   - Don't exceed voltage ratings
   - Insulate connections

2. **Environmental**
   - Some LDRs contain cadmium
   - Dispose properly
   - Use RoHS compliant parts

## Next Steps

After mastering photoresistors:
1. Try phototransistors for faster response
2. Use photodiodes for linear response
3. Build color sensors with filters
4. Create multi-zone light systems
5. Implement machine learning for patterns

## Resources

- [LDR Characteristics](https://www.electronics-tutorials.ws/io/io_4.html)
- [Light Measurement Units](https://www.intl-lighttech.com/support/light-measurement-tutorial)
- [MCP3008 with GPIO Zero](https://gpiozero.readthedocs.io/en/stable/api_spi.html)
- [Voltage Divider Calculator](https://www.allaboutcircuits.com/tools/voltage-divider-calculator/)