# Project 02-03: LED Bar Graph - Visual Data Display

Create visual representations of data using a 10-segment LED bar graph for level indicators, meters, and status displays.

## What You'll Learn

- LED bar graph principles and wiring
- Creating visual data representations
- Level meters and indicators
- Animation and patterns
- Real-time data visualization
- Analog input integration

## Hardware Requirements

- Raspberry Pi 5
- 1x 10-segment LED bar graph
- 10x 220Ω resistors
- Optional: MCP3008 ADC
- Optional: Potentiometer (10kΩ)
- Jumper wires
- Breadboard

## LED Bar Graph Types

| Type | Configuration | Common Use |
|------|---------------|------------|
| Common Anode | Shared positive | All LEDs share VCC |
| Common Cathode | Shared negative | All LEDs share GND |
| Independent | No shared pins | Individual control |

## Circuit Diagram

```
LED Bar Graph Wiring (Common Cathode):
                    
    LED Bar Graph Module
    ┌─────────────────┐
    │ ▯ ▯ ▯ ▯ ▯ ▯ ▯ ▯ ▯ ▯ │  <- 10 LED segments
    └─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┘
      │ │ │ │ │ │ │ │ │ │
      │ │ │ │ │ │ │ │ │ └──[220Ω]── GPIO12 (Pin 32)
      │ │ │ │ │ │ │ │ └────[220Ω]── GPIO7  (Pin 26)
      │ │ │ │ │ │ │ └──────[220Ω]── GPIO8  (Pin 24)
      │ │ │ │ │ │ └────────[220Ω]── GPIO25 (Pin 22)
      │ │ │ │ │ └──────────[220Ω]── GPIO24 (Pin 18)
      │ │ │ │ └────────────[220Ω]── GPIO23 (Pin 16)
      │ │ │ └──────────────[220Ω]── GPIO22 (Pin 15)
      │ │ └────────────────[220Ω]── GPIO27 (Pin 13)
      │ └──────────────────[220Ω]── GPIO18 (Pin 12)
      └────────────────────[220Ω]── GPIO17 (Pin 11)

Common pins (if present) -> GND

Optional Potentiometer Control (with MCP3008):
    3.3V ──┬── Potentiometer ──┬── GND
           │                    │
           └────────────────────┴── MCP3008 CH0
```

## Pin Connections

| LED Segment | GPIO Pin | Physical Pin | Purpose |
|-------------|----------|--------------|---------|
| LED 1 | GPIO17 | Pin 11 | First segment |
| LED 2 | GPIO18 | Pin 12 | Second segment |
| LED 3 | GPIO27 | Pin 13 | Third segment |
| LED 4 | GPIO22 | Pin 15 | Fourth segment |
| LED 5 | GPIO23 | Pin 16 | Fifth segment |
| LED 6 | GPIO24 | Pin 18 | Sixth segment |
| LED 7 | GPIO25 | Pin 22 | Seventh segment |
| LED 8 | GPIO8 | Pin 24 | Eighth segment |
| LED 9 | GPIO7 | Pin 26 | Ninth segment |
| LED 10 | GPIO12 | Pin 32 | Tenth segment |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero
sudo apt install -y python3-gpiozero

# For ADC support (optional)
pip3 install adafruit-circuitpython-mcp3xxx
```

## Running the Examples

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/02-output-displays/03-led-bar-graph

# Run the LED bar graph examples
python3 led-bar-graph.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Bar Graph Control

1. **Creating Bar Graph Object**
   ```python
   from gpiozero import LEDBarGraph
   
   LED_PINS = [17, 18, 27, 22, 23, 24, 25, 8, 7, 12]
   graph = LEDBarGraph(*LED_PINS)
   ```
   - GPIO Zero handles individual LED control
   - Value range: 0.0 (all off) to 1.0 (all on)

2. **Setting Level**
   ```python
   graph.value = 0.5  # Light up 5 LEDs
   graph.value = 0.7  # Light up 7 LEDs
   ```

3. **Animation Effects**
   ```python
   graph.pulse()  # Fade in/out effect
   graph.blink()  # Blink all LEDs
   ```

### Level Meter Implementation

```python
# VU meter style display
level = audio_level / max_level
graph.value = level
```

### Pattern Display

```python
# Direct LED control
for i in range(10):
    graph.leds[i].on()  # Turn on specific LED
    time.sleep(0.1)
    graph.leds[i].off()
```

## Key Concepts

### Bar Graph Mathematics

1. **Value to LED Mapping**
   ```python
   # Value 0.0-1.0 maps to 0-10 LEDs
   num_leds = int(value * 10)
   ```

2. **Percentage Display**
   ```python
   percentage = data / max_value
   graph.value = percentage
   ```

3. **Logarithmic Scaling**
   ```python
   # For audio levels
   db_value = 20 * math.log10(level)
   graph.value = (db_value + 60) / 60  # -60dB to 0dB
   ```

## Common Applications

### 1. Volume/Level Indicator
- Audio equipment VU meters
- Signal strength displays
- Volume controls

### 2. Battery Level Display
- Device power monitoring
- Charging indicators
- Low battery warnings

### 3. Temperature Gauge
- Environmental monitoring
- System temperature display
- HVAC controls

### 4. Progress Indicators
- Download progress
- Loading bars
- Task completion

### 5. Data Visualization
- Sensor readings
- Network activity
- CPU/Memory usage

## Display Patterns

### Knight Rider Effect
```python
# Moving dot back and forth
for i in range(10):
    graph.leds[i].on()
    time.sleep(0.1)
    graph.leds[i].off()
```

### Growing Bar
```python
# Fill up gradually
for i in range(11):
    graph.value = i / 10
    time.sleep(0.1)
```

### Center Out
```python
# Light from center outward
center = 5
for offset in range(5):
    graph.leds[center + offset].on()
    graph.leds[center - offset - 1].on()
    time.sleep(0.1)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No LEDs light up | Check power, verify GPIO pins |
| Wrong LEDs light | Check pin order, verify wiring |
| Dim LEDs | Check resistor values, power supply |
| Flickering | Add delays, check connections |
| Some LEDs don't work | Test individual LEDs, check resistors |

## Advanced Techniques

### Multi-Color Bar Graph
```python
# Using RGB LEDs for color-coded levels
# Green for low, yellow for medium, red for high
if level < 0.3:
    set_color("green")
elif level < 0.7:
    set_color("yellow")
else:
    set_color("red")
```

### Smooth Transitions
```python
# Interpolate between values
def smooth_transition(start, end, steps=20):
    for i in range(steps):
        value = start + (end - start) * i / steps
        graph.value = value
        time.sleep(0.05)
```

### Peak Hold
```python
class PeakMeter:
    def __init__(self, graph):
        self.graph = graph
        self.peak = 0
        self.peak_time = 0
    
    def update(self, value):
        if value > self.peak:
            self.peak = value
            self.peak_time = time.time()
        elif time.time() - self.peak_time > 1:
            self.peak *= 0.95  # Decay
        
        # Show current and peak
        self.graph.value = value
        # Flash top LED for peak
        if self.peak > 0.9:
            self.graph.leds[9].blink()
```

## Performance Optimization

### Update Rate
- Human eye: 20-30 Hz sufficient
- Smooth animation: 50-60 Hz
- Battery saving: 10 Hz or less

### Efficient Updates
```python
# Only update when value changes
last_value = -1
while True:
    new_value = read_sensor()
    if abs(new_value - last_value) > 0.05:
        graph.value = new_value
        last_value = new_value
    time.sleep(0.01)
```

## LED Bar Graph Specifications

| Parameter | Typical Value |
|-----------|--------------|
| Forward Voltage | 2.0-2.2V (red), 3.0-3.2V (green/blue) |
| Forward Current | 20mA per LED |
| Total Current | 200mA (all LEDs on) |
| Viewing Angle | 120° |
| Segment Size | 5mm x 10mm typical |

## Integration Examples

### With Temperature Sensor
```python
# Display temperature on bar graph
temp_range = (0, 40)  # 0°C to 40°C
temp_normalized = (temperature - temp_range[0]) / (temp_range[1] - temp_range[0])
graph.value = temp_normalized
```

### With Sound Sensor
```python
# VU meter for audio
audio_level = read_audio_sensor()
# Apply logarithmic scaling
db = 20 * math.log10(audio_level + 0.001)
normalized = (db + 40) / 40  # -40dB to 0dB range
graph.value = max(0, min(1, normalized))
```

### With Network Monitor
```python
# Show network utilization
bandwidth_used = get_network_usage()
max_bandwidth = 100  # Mbps
graph.value = bandwidth_used / max_bandwidth
```

## Project Ideas

1. **Music Visualizer**
   - React to audio input
   - Different patterns for frequencies
   - Beat detection display

2. **Environmental Monitor**
   - Temperature gauge
   - Humidity indicator
   - Air quality display

3. **Game Score Display**
   - Player health bars
   - Power-up indicators
   - Timer displays

4. **System Monitor**
   - CPU usage
   - Memory utilization
   - Disk activity

5. **IoT Status Panel**
   - Device connection status
   - Signal strength indicators
   - Alert notifications

## Safety Notes

1. **Current Limiting**
   - Always use resistors
   - Total current under 200mA
   - Check Pi GPIO current limits

2. **Static Protection**
   - Handle with care
   - Ground yourself
   - Avoid touching pins

## Next Steps

After mastering LED bar graphs:
1. Combine with sensors for real displays
2. Create custom PCBs for permanent installations
3. Use shift registers for more LEDs
4. Implement PWM for brightness control
5. Build multi-bar displays for complex data

## Resources

- [GPIO Zero LEDBarGraph](https://gpiozero.readthedocs.io/en/stable/api_output.html#ledbargraph)
- [LED Current Calculations](https://www.electronics-tutorials.ws/diode/diode_8.html)
- [Bar Graph Display Patterns](https://www.arduino.cc/en/Tutorial/BarGraph)
- [Data Visualization Principles](https://www.interaction-design.org/literature/article/data-visualization)