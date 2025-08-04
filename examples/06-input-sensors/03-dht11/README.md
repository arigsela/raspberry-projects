# Project 06-03: DHT11 - Digital Temperature and Humidity Sensor

Monitor environmental conditions with the DHT11 digital temperature and humidity sensor using custom single-wire protocol.

## What You'll Learn

- Single-wire digital communication protocol
- Temperature and humidity measurement
- Sensor data validation and checksums
- Environmental comfort calculations
- Data logging and visualization
- Combining sensors with displays

## Hardware Requirements

- Raspberry Pi 5
- 1x DHT11 sensor module (or bare sensor with pull-up resistor)
- 1x 10kΩ resistor (if using bare sensor)
- 3x Jumper wires
- Optional: LCD1602 display for readings
- Breadboard

## Circuit Diagram

```
DHT11 Module (3-pin):
┌─────────────┐
│    DHT11    │
│   ┌─────┐   │
│   │     │   │
│   │     │   │
│   └─────┘   │
│ VCC DATA GND│
└──┬───┬───┬──┘
   │   │   │
   │   │   └──── GND (Pin 6)
   │   └──────── GPIO17 (Pin 11)
   └──────────── 5V (Pin 2)

DHT11 Bare Sensor (4-pin):
    Front View
    ┌─────────┐
    │ ░░░░░░░ │  <- Humidity sensing element
    │ ░░░░░░░ │
    │ DHT11   │
    └─┬─┬─┬─┬─┘
      1 2 3 4
      │ │ │ │
      │ │ │ └── GND
      │ │ └──── No Connection
      │ └────── DATA → 10kΩ → 5V (Pull-up)
      └──────── VCC (5V)     │
                            GPIO17
```

## Pin Connections

| DHT11 Pin | Connection | GPIO | Notes |
|-----------|------------|------|-------|
| VCC | Pin 2 | 5V | Power supply |
| DATA | Pin 11 | GPIO17 | With 10kΩ pull-up |
| GND | Pin 6 | GND | Common ground |
| NC | - | - | Not connected (4-pin only) |

## DHT11 Specifications

| Parameter | Value |
|-----------|-------|
| Temperature Range | 0-50°C |
| Temperature Accuracy | ±2°C |
| Humidity Range | 20-80% RH |
| Humidity Accuracy | ±5% RH |
| Resolution | 1°C, 1% RH |
| Sampling Rate | 1 Hz (once per second) |
| Operating Voltage | 3.3-5.5V |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install RPi.GPIO (usually pre-installed)
sudo apt install -y python3-rpi.gpio

# For data logging features (optional)
pip3 install matplotlib pandas
```

## Running the Programs

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/06-input-sensors/03-dht11

# Run the basic monitor
python3 dht11-monitor.py

# Or run with LCD display
python3 dht11-display.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### DHT11 Protocol (_shared/dht11.py)

1. **Communication Sequence**
   - Send start signal (18ms LOW)
   - DHT11 responds with 80μs LOW, 80μs HIGH
   - 40 bits of data follow

2. **Data Format** (40 bits total)
   - 8 bits: Humidity integer
   - 8 bits: Humidity decimal (always 0 for DHT11)
   - 8 bits: Temperature integer
   - 8 bits: Temperature decimal (always 0 for DHT11)
   - 8 bits: Checksum

3. **Bit Encoding**
   - 0: 50μs LOW + 26-28μs HIGH
   - 1: 50μs LOW + 70μs HIGH

### Monitor Application (dht11-monitor.py)

1. **Continuous Monitoring**
   - Real-time readings every 3 seconds
   - Comfort level analysis
   - Statistics tracking

2. **Data Logging Mode**
   - CSV format output
   - Timestamped readings
   - Suitable for analysis

### Display Integration (dht11-display.py)

- LCD output with custom symbols
- Trend indicators (rising/falling)
- Comfort recommendations

## Key Concepts

### Single-Wire Protocol
- **Bidirectional**: Same pin for send/receive
- **Time-Critical**: Precise timing required
- **Pull-up Resistor**: Ensures defined idle state

### Data Validation
```python
checksum = (humidity_int + humidity_dec + 
           temp_int + temp_dec) & 0xFF
```

### Comfort Zones
| Condition | Temperature | Humidity |
|-----------|------------|----------|
| Optimal | 20-26°C | 40-60% |
| Too Hot | >28°C | - |
| Too Cold | <18°C | - |
| Too Humid | - | >70% |
| Too Dry | - | <30% |

## Common Issues and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| All zeros | No communication | Check wiring, pull-up resistor |
| Checksum errors | Timing issues | Ensure no interrupts during read |
| Constant values | Sensor not updating | Power cycle, check minimum read interval |
| Read failures | Loose connection | Secure all connections |
| Wrong values | Damaged sensor | Test with known good sensor |

## Advanced Calculations

### Heat Index (Feels Like)
```python
# Simplified heat index for comfort
if temp > 26 and humidity > 40:
    feels_like = temp + (humidity - 40) * 0.1
```

### Dew Point
```python
# Magnus formula approximation
a, b = 17.27, 237.7
alpha = (a * temp) / (b + temp) + log(humidity / 100)
dew_point = (b * alpha) / (a - alpha)
```

### Absolute Humidity
```python
# Grams of water per cubic meter
abs_humidity = 6.112 * exp((17.67 * temp) / (temp + 243.5))
abs_humidity = abs_humidity * humidity * 2.1674 / (273.15 + temp)
```

## DHT11 vs DHT22 Comparison

| Feature | DHT11 | DHT22 |
|---------|-------|-------|
| Temperature Range | 0-50°C | -40-80°C |
| Temperature Accuracy | ±2°C | ±0.5°C |
| Humidity Range | 20-80% | 0-100% |
| Humidity Accuracy | ±5% | ±2% |
| Resolution | 1°C, 1% | 0.1°C, 0.1% |
| Sampling Rate | 1 Hz | 0.5 Hz |
| Price | Lower | Higher |

## Project Ideas

1. **Weather Station**
   - Log data over time
   - Calculate trends
   - Weather predictions

2. **Greenhouse Monitor**
   - Alert when outside comfort zone
   - Automatic fan/heater control
   - Data logging for plants

3. **HVAC Controller**
   - Smart thermostat
   - Humidity control
   - Energy optimization

4. **Server Room Monitor**
   - Temperature alerts
   - Historical graphs
   - Email notifications

5. **Comfort Indicator**
   - RGB LED for zones
   - LCD display
   - Mobile app integration

## Data Visualization

### Simple Console Graph
```python
def print_bar_graph(value, max_value, width=20):
    filled = int((value / max_value) * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar

# Temperature bar (0-50°C)
temp_bar = print_bar_graph(temperature, 50)
print(f"Temp: {temp_bar} {temperature}°C")
```

### CSV Data Analysis
```python
import pandas as pd
import matplotlib.pyplot as plt

# Read logged data
df = pd.read_csv('dht11_log.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Plot
df.plot(x='timestamp', y=['temperature_c', 'humidity_percent'])
plt.show()
```

## Optimization Tips

### Reading Frequency
- DHT11 updates once per second
- Reading faster won't get new data
- Minimum 2 seconds between reads recommended

### Error Handling
```python
def read_with_retry(sensor, max_retries=5):
    for _ in range(max_retries):
        humidity, temp = sensor.read()
        if humidity and temp:
            return humidity, temp
        time.sleep(2)
    return None, None
```

### Power Saving
- Read less frequently for battery operation
- Power down between reads
- Use deep sleep modes

## Troubleshooting

1. **"No module named RPi.GPIO"**
   ```bash
   sudo apt install python3-rpi.gpio
   ```

2. **Always reading 0 or 255**
   - Check pull-up resistor (10kΩ)
   - Verify 5V power supply
   - Test with different GPIO pin

3. **Checksum failures**
   - Move away from sources of interference
   - Use shorter wires
   - Add small capacitor (100nF) across power

4. **Slow response**
   - Normal - DHT11 is slow
   - Consider DHT22 for faster response

## Integration Examples

### With Email Alerts
```python
import smtplib
if temperature > 30:
    send_email("Temperature Alert", 
               f"Temperature is {temperature}°C!")
```

### With IoT Platforms
```python
# Send to ThingSpeak
import requests
url = f"https://api.thingspeak.com/update?api_key={KEY}"
url += f"&field1={temperature}&field2={humidity}"
requests.get(url)
```

## Next Steps

After mastering DHT11:
1. Upgrade to DHT22 for better accuracy
2. Add data logging and graphing
3. Create web interface for remote monitoring
4. Implement predictive algorithms
5. Build complete weather station

## Resources

- [DHT11 Datasheet](https://www.mouser.com/datasheet/2/758/DHT11-Technical-Data-Sheet-Translated-Version-1143054.pdf)
- [Humidity Calculations](https://www.vaisala.com/en/measurement/humidity)
- [Comfort Zone Research](https://www.ashrae.org/technical-resources/thermal-comfort)
- [Single-Wire Protocol](https://en.wikipedia.org/wiki/1-Wire)