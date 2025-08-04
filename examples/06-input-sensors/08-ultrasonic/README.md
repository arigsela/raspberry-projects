# Project 06-08: HC-SR04 Ultrasonic Sensor - Distance Measurement

Measure distances using ultrasonic sound waves with the HC-SR04 sensor for robotics, automation, and sensing applications.

## What You'll Learn

- Ultrasonic distance measurement principles
- Trigger and echo signal timing
- Sound wave physics and calculations
- Distance averaging and filtering
- Practical applications (parking sensors, liquid level, etc.)
- Servo integration for radar systems

## Hardware Requirements

- Raspberry Pi 5
- 1x HC-SR04 Ultrasonic Sensor
- 4x Jumper wires
- Optional: Servo motor for radar system
- Optional: Voltage divider (1kΩ + 2kΩ resistors) for echo pin
- Breadboard

## Circuit Diagram

```
HC-SR04 Sensor:
┌─────────────────┐
│     HC-SR04     │
│                 │
│  ┌─┐      ┌─┐  │
│  │O│      │O│  │  <- Ultrasonic transducers
│  └─┘      └─┘  │
│                 │
│ VCC TRIG ECHO GND│
└──┬───┬────┬────┬─┘
   │   │    │    │
   │   │    │    └──── GND (Pin 6)
   │   │    │
   │   │    └───────── GPIO24 (Pin 18) - Echo
   │   │               (Through voltage divider)
   │   │
   │   └────────────── GPIO23 (Pin 16) - Trigger
   │
   └────────────────── 5V (Pin 2)

Voltage Divider for Echo (5V to 3.3V):
Echo Pin ----[1kΩ]----●----[2kΩ]---- GND
                      │
                   GPIO24

Note: Some HC-SR04 modules work fine with 3.3V logic directly
```

## Pin Connections

| HC-SR04 Pin | Raspberry Pi Pin | GPIO | Notes |
|-------------|------------------|------|-------|
| VCC | Pin 2 | 5V | Power supply |
| Trigger | Pin 16 | GPIO23 | 3.3V compatible |
| Echo | Pin 18 | GPIO24 | Use voltage divider |
| GND | Pin 6 | GND | Common ground |

## How Ultrasonic Sensors Work

### Operating Principle
1. **Trigger**: 10µs HIGH pulse starts measurement
2. **Transmit**: 8 cycles of 40kHz ultrasound
3. **Echo**: HIGH while waiting for reflection
4. **Calculate**: Distance = (Time × Speed of Sound) / 2

### Timing Diagram
```
Trigger: ___│‾‾‾│_________________
            10µs

Echo:    _______│‾‾‾‾‾‾‾‾‾│_______
                  Duration = Round trip time
```

### Distance Calculation
- Speed of sound: ~343 m/s at 20°C
- Distance = (Duration × 343) / 2
- Or: Distance (cm) = Duration (µs) / 58

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero
sudo apt install -y python3-gpiozero

# For advanced features
pip3 install numpy matplotlib
```

## Running the Programs

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/06-input-sensors/08-ultrasonic

# Run the distance measurement demos
python3 ultrasonic-distance.py

# Or run the radar system (requires servo)
python3 ultrasonic-radar.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Distance Measurement (ultrasonic-distance.py)

1. **Sensor Initialization**
   ```python
   sensor = DistanceSensor(
       echo=ECHO_PIN,
       trigger=TRIGGER_PIN,
       max_distance=4.0,
       queue_len=5
   )
   ```
   - GPIO Zero handles timing automatically
   - Queue averages multiple readings

2. **Reading Distance**
   ```python
   distance = sensor.distance * 100  # In cm
   ```
   - Returns distance in meters
   - Multiply by 100 for centimeters

3. **Multiple Applications**
   - Continuous measurement
   - Proximity alarms
   - Parking sensors
   - Liquid level monitoring

### Radar System (ultrasonic-radar.py)

1. **Servo Integration**
   - Sweep servo 0-180 degrees
   - Take distance reading at each angle
   - Build radar map

2. **Display Methods**
   - ASCII radar display
   - Object tracking
   - Security monitoring

## Key Concepts

### Speed of Sound Variables
| Factor | Effect on Speed |
|--------|----------------|
| Temperature | +0.6 m/s per °C |
| Humidity | Slight increase |
| Air Pressure | Minimal effect |
| Altitude | Decreases with altitude |

### Temperature Compensation
```python
# Accurate speed of sound calculation
def speed_of_sound(temperature_c):
    return 331.3 * math.sqrt(1 + temperature_c / 273.15)
```

### Measurement Limitations
- **Minimum Distance**: ~2 cm (sensor dead zone)
- **Maximum Distance**: ~4 m (depends on object)
- **Beam Angle**: ~15° cone
- **Resolution**: ~3 mm

### Object Detection Factors
1. **Surface Material**
   - Hard, flat surfaces: Best reflection
   - Soft materials: Absorb sound
   - Angled surfaces: Deflect sound

2. **Object Size**
   - Must be larger than wavelength (~8.5mm)
   - Small objects may not be detected

## Common Applications

### 1. Parking Sensor
```python
if distance < 20:
    print("STOP! Too close")
elif distance < 50:
    print("Warning - Slow down")
```

### 2. Liquid Level Monitor
```python
liquid_level = container_height - distance_to_surface
percentage = (liquid_level / container_height) * 100
```

### 3. Security System
```python
if abs(current_distance - baseline_distance) > threshold:
    trigger_alarm()
```

### 4. Robot Navigation
```python
if distance < obstacle_threshold:
    robot.turn()
else:
    robot.forward()
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No readings | Check 5V power, verify connections |
| Always max distance | Check trigger pulse, echo connection |
| Erratic readings | Add voltage divider, check for interference |
| Short range only | Clean sensor face, check for obstructions |
| Inconsistent values | Increase queue_len, add filtering |

## Advanced Techniques

### Moving Average Filter
```python
class FilteredSensor:
    def __init__(self, sensor, window_size=5):
        self.sensor = sensor
        self.readings = []
        self.window_size = window_size
    
    def get_distance(self):
        self.readings.append(self.sensor.distance)
        if len(self.readings) > self.window_size:
            self.readings.pop(0)
        return sum(self.readings) / len(self.readings)
```

### Kalman Filter
```python
def kalman_filter(measurement, estimate, error_est, error_meas):
    kalman_gain = error_est / (error_est + error_meas)
    estimate = estimate + kalman_gain * (measurement - estimate)
    error_est = (1 - kalman_gain) * error_est
    return estimate, error_est
```

### Multiple Sensor Array
```python
sensors = [
    DistanceSensor(echo=24, trigger=23),  # Front
    DistanceSensor(echo=25, trigger=22),  # Left
    DistanceSensor(echo=27, trigger=17),  # Right
]
```

## Performance Optimization

### Measurement Rate
- Maximum: ~60 Hz (must wait for echo timeout)
- Recommended: 10-20 Hz for stability
- Multiple sensors: Trigger sequentially

### Power Consumption
- Active: ~15mA
- Idle: ~2mA
- Use GPIO to control VCC for power saving

### Accuracy Improvements
1. **Temperature Compensation**
2. **Multiple Readings Average**
3. **Outlier Rejection**
4. **Calibration with Known Distances**

## HC-SR04 Specifications

| Parameter | Value |
|-----------|-------|
| Operating Voltage | 5V |
| Operating Current | 15mA |
| Frequency | 40kHz |
| Min Range | 2cm |
| Max Range | 400cm |
| Measuring Angle | 15° |
| Trigger Pulse | 10µs TTL |
| Echo Pulse | TTL level signal |
| Dimensions | 45×20×15mm |

## Alternative Sensors

### HC-SR04 vs Others
| Sensor | Range | Accuracy | Price | Features |
|--------|-------|----------|-------|----------|
| HC-SR04 | 2-400cm | ±3mm | Low | Basic |
| JSN-SR04T | 25-450cm | ±1cm | Medium | Waterproof |
| MaxSonar | 0-765cm | ±1% | High | Multiple outputs |
| VL53L0X | 3-200cm | ±3% | Medium | Laser, I2C |

## Project Ideas

1. **Smart Trash Can**
   - Open lid when hand detected
   - Monitor fill level
   - Alert when full

2. **Water Tank Monitor**
   - Continuous level monitoring
   - Low level alerts
   - Usage tracking

3. **Garage Parking Aid**
   - Guide car to perfect position
   - Multiple sensors for alignment
   - Visual/audio feedback

4. **Blind Spot Detector**
   - Multiple sensors on vehicle
   - Alert driver to obstacles
   - Integration with mirrors

5. **3D Scanner**
   - Combine with 2-axis servo mount
   - Map room or objects
   - Export point cloud data

## Integration Examples

### With LCD Display
```python
lcd.write_line(f"Distance: {distance:.1f}cm", 0)
lcd.write_line(f"Status: {status}", 1)
```

### With LED Indicators
```python
if distance < 10:
    red_led.on()
elif distance < 30:
    yellow_led.on()
else:
    green_led.on()
```

### With Data Logging
```python
with open('distance_log.csv', 'a') as f:
    f.write(f"{timestamp},{distance}\n")
```

## Safety Notes

1. **Ultrasound Safety**
   - 40kHz is inaudible to humans
   - Safe for pets (above their range)
   - No health hazards

2. **Electrical Safety**
   - Use voltage divider for echo
   - Don't exceed 5V on sensor
   - Protect against short circuits

## Next Steps

After mastering ultrasonic sensors:
1. Build autonomous robot with obstacle avoidance
2. Create 3D mapping system
3. Develop gesture recognition
4. Implement multi-sensor fusion
5. Design custom PCB with multiple sensors

## Resources

- [HC-SR04 Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)
- [Ultrasonic Theory](https://www.microsonic.de/en/support/ultrasonic-technology/principle.htm)
- [Speed of Sound Calculator](https://www.nde-ed.org/Physics/Sound/tempandspeed.htm)
- [GPIO Zero Distance Sensor](https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor)