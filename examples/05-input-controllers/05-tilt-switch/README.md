# Project 05-05: Tilt Switch - Orientation and Motion Detection

Detect tilt, orientation changes, and vibration using mercury or ball-type tilt switches for security and motion sensing applications.

## What You'll Learn

- Tilt switch operating principles
- Mercury vs ball switch types
- Orientation detection techniques
- Vibration sensing methods
- Security system implementation
- Motion pattern recognition

## Hardware Requirements

- Raspberry Pi 5
- Tilt switch (mercury or ball type)
- LED for visual feedback
- Active buzzer (optional)
- 220-330Ω resistor for LED
- 10kΩ pull-up resistor (if not using internal)
- Jumper wires
- Breadboard

## Understanding Tilt Switches

### Types of Tilt Switches

```
Mercury Tilt Switch:
     ┌────────────┐
     │   Mercury   │
     │  ███████   │  Upright: Open circuit
     │ Contact Contact
     └────────────┘

     ┌────────────┐
     │Contact       │
     │█████████████│  Tilted: Closed circuit
     │Contact Mercury│
     └────────────┘

Ball Tilt Switch:
     ┌────────────┐
     │    Ball  ●  │  Upright: Ball away from contacts
     │ Contact Contact
     └────────────┘

     ┌────────────┐
     │Contact  ●    │  Tilted: Ball bridges contacts
     │Contact Ball  │
     └────────────┘
```

### Operating Characteristics

| Feature | Mercury Switch | Ball Switch |
|---------|----------------|-------------|
| Response Time | Fast (~1ms) | Moderate (~10ms) |
| Sensitivity | Very high | Adjustable |
| Angle Range | 10-15° typical | 15-45° typical |
| Bounce | Minimal | More pronounced |
| Safety | Contains mercury | Non-toxic |
| Cost | Higher | Lower |

## Circuit Diagram

```
Basic Tilt Switch Connection:

    3.3V ──┐
           │
          ╱ │ 10kΩ (internal pull-up)
           │
    GPIO17 ├────────┤ ├──── GND
           │        Tilt Switch
           │
Optional Outputs:
    GPIO18 ├──[220Ω]──╢▶├── GND (LED)
           │
    GPIO22 ├────────╢+├── GND
                    Buzzer

Dual-Axis Detection:
    GPIO17 ├────────┤ ├── GND (X-axis)
    GPIO27 ├────────┤ ├── GND (Y-axis)
```

## Pin Connections

| Component | GPIO Pin | Purpose |
|-----------|----------|---------|
| Tilt Switch 1 | GPIO17 | Primary tilt input |
| Tilt Switch 2 | GPIO27 | Secondary axis (optional) |
| LED Anode | GPIO18 | Visual indicator |
| Buzzer + | GPIO22 | Audio alert |
| All GND | GND | Common ground |

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
cd ~/raspberry-projects/examples/05-input-controllers/05-tilt-switch

# Run the tilt switch examples
python3 tilt-switch.py

# Run specific demos
make run       # Interactive menu
make test      # Test tilt detection
make alarm     # Security alarm demo
make game      # Balance game
make vibration # Vibration detector
```

## Code Walkthrough

### Basic Tilt Detection

1. **Setup**
   ```python
   from gpiozero import Button
   
   # Tilt switch closes circuit when tilted
   tilt = Button(17, pull_up=True)
   ```

2. **Read State**
   ```python
   if tilt.is_pressed:
       print("TILTED")
   else:
       print("UPRIGHT")
   ```

3. **Event Detection**
   ```python
   def on_tilt():
       print("Tilt detected!")
   
   tilt.when_pressed = on_tilt
   ```

## Key Concepts

### Tilt Angle Sensitivity

```
Tilt Detection Angles:

         0° (Upright)
           |
    -45° --+-- +45°
           |
         ±90° (Horizontal)

Typical activation: 15-30° from vertical
```

### Vibration Detection

Tilt switches can detect vibration by counting state changes:

```python
def detect_vibration(sample_time=1.0):
    changes = 0
    
    def count_change():
        nonlocal changes
        changes += 1
    
    tilt.when_pressed = count_change
    tilt.when_released = count_change
    
    time.sleep(sample_time)
    return changes
```

### Multi-Axis Detection

```
4-Direction Detection:

     Forward
       |
  Left-+-Right
       |
    Backward

Requires 2 tilt switches mounted perpendicular
```

## Common Applications

### 1. Security Systems
- Motion alarms
- Tamper detection
- Door/window sensors
- Safe monitoring

### 2. Gaming
- Tilt controls
- Balance games
- Maze games
- Motion input

### 3. Robotics
- Orientation sensing
- Fall detection
- Self-righting mechanisms
- Terrain detection

### 4. Automotive
- Parking sensors
- Rollover detection
- Headlight leveling
- Alarm systems

### 5. Industrial
- Machine tilt monitoring
- Conveyor alignment
- Level detection
- Safety shutoffs

## Advanced Techniques

### Angle Measurement

```python
# Estimate tilt angle using time-based sampling
def estimate_angle(samples=100):
    tilted_count = 0
    
    for _ in range(samples):
        if tilt.is_pressed:
            tilted_count += 1
        time.sleep(0.01)
    
    # Rough angle estimate
    tilt_ratio = tilted_count / samples
    
    if tilt_ratio < 0.1:
        return "0-15°"
    elif tilt_ratio < 0.5:
        return "15-45°"
    elif tilt_ratio < 0.9:
        return "45-75°"
    else:
        return "75-90°"
```

### Drop Detection

```python
class DropDetector:
    def __init__(self, tilt_pin):
        self.tilt = Button(tilt_pin, bounce_time=0.001)
        self.last_changes = []
        self.drop_threshold = 10  # Changes per 100ms
    
    def detect_drop(self):
        changes = 0
        start = time.time()
        
        # Count rapid changes
        while time.time() - start < 0.1:
            if self.tilt.is_pressed != last_state:
                changes += 1
                last_state = self.tilt.is_pressed
        
        return changes > self.drop_threshold
```

### Orientation Tracking

```python
class OrientationTracker:
    def __init__(self):
        self.states = {
            "upright": 0,
            "tilted_left": 0,
            "tilted_right": 0,
            "inverted": 0
        }
    
    def update(self, x_tilt, y_tilt):
        if not x_tilt and not y_tilt:
            self.states["upright"] += 1
        # ... other orientations
    
    def get_primary_orientation(self):
        return max(self.states, key=self.states.get)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No detection | Check wiring, verify switch continuity |
| Constant triggering | Check for shorts, clean switch contacts |
| Erratic behavior | Add debouncing, check for vibration |
| Wrong orientation | Verify switch mounting angle |
| Slow response | Check bounce_time setting |

## Safety Considerations

### Mercury Switches
- **Contains toxic mercury** - handle with care
- Do not break or puncture
- Dispose properly as hazardous waste
- Consider ball switches as safer alternative

### Mounting
- Secure mounting prevents false triggers
- Consider vibration isolation
- Protect from physical damage
- Seal against moisture

## Calibration

### Sensitivity Adjustment

```python
class CalibratedTiltSensor:
    def __init__(self, pin, threshold=0.7):
        self.tilt = Button(pin)
        self.threshold = threshold  # 0-1 sensitivity
        self.samples = []
    
    def is_tilted(self):
        # Take multiple samples
        self.samples.append(self.tilt.is_pressed)
        if len(self.samples) > 10:
            self.samples.pop(0)
        
        # Return true if threshold exceeded
        tilt_ratio = sum(self.samples) / len(self.samples)
        return tilt_ratio > self.threshold
```

## Project Ideas

1. **Smart Mailbox**
   - Detect mail delivery
   - Send notifications
   - Track opening times
   - Battery powered

2. **Earthquake Detector**
   - Multi-axis sensing
   - Vibration logging
   - Alert system
   - Data upload

3. **Pinball Tilt Mechanism**
   - Game tilt detection
   - Anti-cheat system
   - Score penalty
   - Visual/audio alerts

4. **Motorcycle Alarm**
   - Tip-over detection
   - Movement alarm
   - GPS activation
   - Remote alerts

5. **Package Handler**
   - Drop detection
   - Orientation logging
   - Damage assessment
   - Shipping monitor

## Integration Examples

### With Accelerometer
```python
# Combine for precise orientation
def get_precise_orientation(tilt, accel):
    if tilt.is_pressed:
        # Use accelerometer for exact angle
        x, y, z = accel.get_values()
        angle = math.atan2(z, math.sqrt(x**2 + y**2))
        return math.degrees(angle)
    return 0  # Upright
```

### With Data Logging
```python
import csv
from datetime import datetime

def log_tilt_event():
    with open('tilt_log.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), "TILTED"])

tilt.when_pressed = log_tilt_event
```

### With IoT Platform
```python
import requests

def send_tilt_alert():
    data = {
        'device_id': 'tilt_sensor_01',
        'event': 'tilt_detected',
        'timestamp': time.time()
    }
    requests.post('https://iot-platform/api/events', json=data)
```

## Best Practices

1. **Mount securely** to prevent false triggers
2. **Use appropriate debouncing** for application
3. **Consider environmental factors** (vibration, temperature)
4. **Test in actual conditions** before deployment
5. **Implement failsafe mechanisms** for critical applications
6. **Regular maintenance** for mechanical switches
7. **Document orientation** relative to device

## Performance Metrics

### Response Times
- Detection: < 10ms typical
- Debounced: 10-50ms
- Event processing: < 1ms
- Total latency: 20-60ms

### Power Consumption
- Idle (pull-up): ~0.3mA
- Active monitoring: 1-5mA
- With LED: +10-20mA
- Sleep mode possible: <0.1mA

## Next Steps

After mastering tilt switches:
1. Combine with accelerometers for precise measurement
2. Build multi-sensor orientation systems
3. Create motion-activated projects
4. Develop security applications
5. Design custom tilt mechanisms

## Resources

- [Tilt Switch Types](https://www.electronics-tutorials.ws/switch/tilt-switch.html)
- [GPIO Zero Button](https://gpiozero.readthedocs.io/en/stable/api_input.html#button)
- [Mercury Switch Safety](https://www.epa.gov/mercury/mercury-switches-and-relays)
- [Vibration Sensing](https://www.allaboutcircuits.com/textbook/sensors/chpt-6/tilt-switches/)