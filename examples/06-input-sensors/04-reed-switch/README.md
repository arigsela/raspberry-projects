# Project 06-04: Reed Switch - Magnetic Field Detection

Detect magnetic fields for security systems, position sensing, proximity detection, and speed measurement applications.

## What You'll Learn

- Reed switch operating principles
- Magnetic field detection
- Security system implementation
- Position and speed sensing
- Proximity detection techniques
- Multi-sensor systems

## Hardware Requirements

- Raspberry Pi 5
- Reed switch(es)
- Small magnet(s)
- LED for visual feedback
- Active buzzer (optional)
- 220-330Ω resistor for LED
- 10kΩ pull-up resistor (if not using internal)
- Jumper wires
- Breadboard

## Understanding Reed Switches

### How Reed Switches Work

```
No Magnetic Field:
     Glass Envelope
    ┌─────────────────┐
    │  ╱         ╲    │  Contacts Open
    │ ┤           ├   │  No current flow
    │  ╲         ╱    │
    └─────────────────┘
      Ferromagnetic
        Contacts

With Magnetic Field:
    ┌─────────────────┐
    │  ╱─────────╲    │  Contacts Closed
    │ ┤═══════════├   │  Current flows
    │  ╲─────────╱    │  
    └─────────────────┘
      Magnetic field
      pulls contacts
        together
```

### Reed Switch Characteristics

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| Switching Time | 0.5-1ms | Very fast response |
| Bounce Time | 0.5-2ms | Minimal contact bounce |
| Operating Distance | 10-40mm | Depends on magnet strength |
| Life Cycles | 10⁸-10⁹ | Extremely reliable |
| Current Rating | 0.5-3A | Varies by model |
| Voltage Rating | 100-200V | AC/DC capable |

## Circuit Diagram

```
Basic Reed Switch Connection:

    3.3V ──┐
           │
          ╱ │ 10kΩ (internal pull-up)
           │
    GPIO17 ├─────────┤ ├───── GND
           │       Reed Switch
           │       + Magnet
           │
With LED Indicator:
    GPIO18 ├──[220Ω]──┤►├──── GND
           │         LED
           │
With Buzzer:
    GPIO22 ├──────────┤+├──── GND
                    Buzzer

Multiple Sensors (Security System):
    GPIO17 ├─────────┤ ├───── GND (Front door)
    GPIO27 ├─────────┤ ├───── GND (Back door)
    GPIO23 ├─────────┤ ├───── GND (Window 1)
    GPIO24 ├─────────┤ ├───── GND (Window 2)
```

## Pin Connections

| Component | GPIO Pin | Purpose |
|-----------|----------|---------|
| Reed Switch 1 | GPIO17 | Primary sensor |
| Reed Switch 2 | GPIO27 | Secondary sensor |
| Reed Switch 3 | GPIO23 | Additional zone |
| Reed Switch 4 | GPIO24 | Additional zone |
| LED Anode | GPIO18 | Status indicator |
| Buzzer + | GPIO22 | Audio alert |

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
cd ~/raspberry-projects/examples/06-input-sensors/04-reed-switch

# Run the reed switch examples
python3 reed-switch.py

# Run specific demos
make run       # Interactive menu
make test      # Test magnetic detection
make door      # Door sensor demo
make security  # Multi-zone security
make rpm       # RPM measurement
make counter   # Proximity counter
```

## Code Walkthrough

### Basic Detection

1. **Setup**
   ```python
   from gpiozero import Button
   
   # Reed switch closes when magnet is near
   reed = Button(17, pull_up=True)
   ```

2. **Read State**
   ```python
   if reed.is_pressed:
       print("Magnet detected")
   else:
       print("No magnet")
   ```

3. **Event Detection**
   ```python
   reed.when_pressed = lambda: print("Magnet approached")
   reed.when_released = lambda: print("Magnet removed")
   ```

## Key Concepts

### Magnetic Field Detection Range

```
Detection Pattern:

    N ═══ S     Detection zone
      │ │       ┌─────────┐
      │ │       │░░░░░░░░░│
      │ │       │░░░░░░░░░│
    Magnet      │░░Reed░░░│
                │░░░░░░░░░│
                │░░░░░░░░░│
                └─────────┘
                
Typical range: 10-40mm
Depends on magnet strength
```

### Security Applications

```python
# Door/Window monitoring
class SecurityZone:
    def __init__(self, pin, name):
        self.sensor = Button(pin, pull_up=True)
        self.name = name
        self.secure = self.sensor.is_pressed
    
    def is_breached(self):
        return not self.sensor.is_pressed
```

### Position Encoding

```
Linear Position Detection:

    Magnet on moving part
         ↓
    ═════●═════════════
         │ │ │ │
         R1 R2 R3 R4    Reed switches
         
Binary encoding possible:
00 = Position 1
01 = Position 2  
10 = Position 3
11 = Position 4
```

## Common Applications

### 1. Security Systems
- Door/window sensors
- Safe monitoring
- Tamper detection
- Perimeter security

### 2. Position Sensing
- Linear actuators
- Valve positions
- Drawer/cabinet sensing
- Limit switches

### 3. Speed Measurement
- Bicycle speedometers
- Motor RPM
- Anemometers
- Tachometers

### 4. Level Detection
- Float switches
- Tank monitoring
- Liquid level alarms
- Overflow protection

### 5. Proximity Detection
- Object counting
- Presence detection
- Access control
- Automation triggers

## Advanced Techniques

### Pulse Counting for RPM

```python
def calculate_rpm(pulse_times):
    if len(pulse_times) < 2:
        return 0
    
    # Time between first and last pulse
    duration = pulse_times[-1] - pulse_times[0]
    pulses = len(pulse_times) - 1
    
    # RPM = pulses per second × 60
    rpm = (pulses / duration) * 60
    return rpm
```

### Multi-Zone Security

```python
class SecuritySystem:
    def __init__(self):
        self.zones = {
            "front_door": SecurityZone(17, "Front Door"),
            "back_door": SecurityZone(27, "Back Door"),
            "garage": SecurityZone(23, "Garage")
        }
        self.armed = False
    
    def arm(self):
        # Check all zones secure first
        breached = [z.name for z in self.zones.values() 
                   if z.is_breached()]
        if breached:
            return False, f"Cannot arm: {breached}"
        
        self.armed = True
        return True, "System armed"
```

### Magnetic Field Mapping

```python
# Map field strength by activation frequency
def measure_field_strength(reed, duration=1.0):
    activations = 0
    start = time.time()
    
    while time.time() - start < duration:
        if reed.is_pressed:
            activations += 1
            reed.wait_for_release()
    
    # More activations = stronger/closer field
    strength = min(100, activations * 10)
    return strength
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No detection | Check magnet polarity, increase magnet size |
| Always detected | Check for magnetic interference |
| Intermittent detection | Clean contacts, check connections |
| Short range | Use stronger magnet, check alignment |
| Multiple triggers | Add debouncing, check for vibration |

## Magnet Selection

### Magnet Types

| Type | Strength | Cost | Use Case |
|------|----------|------|----------|
| Ferrite | Low | Low | Basic detection |
| Alnico | Medium | Medium | General purpose |
| Neodymium | High | High | Long range/small size |
| Flexible | Low | Low | Conformable applications |

### Mounting Considerations

```
Door/Window Installation:

    Door Frame          Door
    ┌────────┐        ┌────────┐
    │  Reed  │        │ Magnet │
    │ Switch │←──────→│        │
    └────────┘  Gap   └────────┘
                <15mm
                
Alignment critical for reliability
```

## Power Consumption

### Low Power Design

```python
# Event-driven approach (low power)
def low_power_monitor():
    reed.when_pressed = wake_and_alert
    signal.pause()  # CPU sleeps

# vs Polling (higher power)
def high_power_monitor():
    while True:
        if reed.is_pressed:
            alert()
        time.sleep(0.1)  # CPU active
```

### Current Draw
- Reed switch: 0mA (passive)
- Pull-up current: ~0.3mA
- LED indicator: 10-20mA
- Total idle: <1mA

## Project Ideas

1. **Smart Mailbox**
   - Detect mail delivery
   - Send notifications
   - Track pickup times
   - Solar powered

2. **Bike Computer**
   - Speed measurement
   - Distance tracking
   - Cadence sensor
   - Wireless display

3. **Window Security**
   - Multi-zone monitoring
   - Smartphone alerts
   - Battery backup
   - Tamper detection

4. **Water Level Monitor**
   - Float switch system
   - Multiple level points
   - Pump control
   - Overflow protection

5. **Door Counter**
   - Bidirectional counting
   - Peak time analysis
   - Occupancy estimation
   - Data logging

## Integration Examples

### With SMS Alerts
```python
import requests

def send_sms_alert(message):
    # Using a service like Twilio
    api_url = "https://api.twilio.com/..."
    data = {
        "to": "+1234567890",
        "body": message
    }
    requests.post(api_url, data=data)

reed.when_released = lambda: send_sms_alert("Door opened!")
```

### With Database Logging
```python
import sqlite3
from datetime import datetime

def log_event(event_type):
    conn = sqlite3.connect('security.db')
    c = conn.cursor()
    c.execute("INSERT INTO events VALUES (?, ?, ?)",
              (datetime.now(), event_type, 'reed_switch'))
    conn.commit()
    conn.close()
```

### With Home Assistant
```python
import paho.mqtt.client as mqtt

def publish_state(state):
    client = mqtt.Client()
    client.connect("homeassistant.local")
    client.publish("home/security/door", 
                  "open" if state else "closed")
    client.disconnect()
```

## Best Practices

1. **Mount securely** - Vibration can cause false triggers
2. **Maintain alignment** - Critical for reliable operation
3. **Use proper gaps** - Too far = no detection, too close = always on
4. **Consider environment** - Temperature affects magnet strength
5. **Test regularly** - Magnets can lose strength over time
6. **Document positions** - Mark installation locations
7. **Use quality components** - Cheap reed switches fail quickly

## Safety Considerations

### Strong Magnets
- Keep away from magnetic storage
- Beware of pinch hazards
- May affect pacemakers
- Can damage electronics

### Installation
- Ensure proper insulation
- Avoid metal filings near switch
- Protect from moisture
- Use appropriate enclosures

## Performance Metrics

### Response Times
- Switch activation: <1ms
- Debounced detection: 5-10ms
- Event processing: <5ms
- Total latency: 10-20ms

### Reliability
- MTBF: >10 million operations
- Temperature range: -40°C to +150°C
- Hermetically sealed
- No power required

## Next Steps

After mastering reed switches:
1. Build complete security systems
2. Create speed measurement devices
3. Design position encoders
4. Implement proximity counters
5. Develop IoT sensor networks

## Resources

- [Reed Switch Basics](https://www.electronics-tutorials.ws/electromagnetism/magnetic-switch.html)
- [Security System Design](https://www.security.org/home-security-systems/diy/)
- [Magnetic Fields](https://en.wikipedia.org/wiki/Magnetic_field)
- [GPIO Zero Button](https://gpiozero.readthedocs.io/en/stable/api_input.html#button)