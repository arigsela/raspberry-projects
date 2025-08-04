# Ultrasonic Parking Sensor (Reversing Alarm)

Advanced proximity detection system with graduated alerts, multiple warning zones, and customizable alert modes for safe parking and reversing assistance.

## What You'll Learn
- Ultrasonic distance measurement and calibration
- Multi-zone proximity detection algorithms
- Graduated alert systems with audio/visual feedback
- Real-time signal processing and smoothing
- Multiple alert mode implementation
- Emergency stop simulation
- Sensor calibration techniques
- Statistical tracking and logging

## Hardware Requirements
- Raspberry Pi 5
- HC-SR04 ultrasonic distance sensor
- 16x2 LCD display with I2C backpack
- 4x LEDs (Green, Yellow, Orange, Red with PWM)
- 2x Buzzers (main alert + speaker for tones)
- 3x Push buttons for control
- ADC0834 for sensitivity adjustment
- 10kΩ potentiometer
- Jumper wires
- Breadboard
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)

## Circuit Diagram

```
Ultrasonic Parking Sensor System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ HC-SR04 Ultrasonic Sensor:                                 │
│ VCC ────── 5V                                              │
│ Trig ───── GPIO23                                          │
│ Echo ───── GPIO24                                          │
│ GND ────── GND                                             │
│                                                             │
│ LED Indicators:                                             │
│ GREEN LED ────── GPIO17 (Safe zone)                        │
│ YELLOW LED ───── GPIO27 (Caution zone)                     │
│ ORANGE LED ───── GPIO22 (Warning zone)                     │
│ RED LED ──────── GPIO18 (Danger zone, PWM)                 │
│                                                             │
│ Audio Output:                                               │
│ MAIN BUZZER ──── GPIO25                                     │
│ SPEAKER ──────── GPIO8 (For tones)                         │
│                                                             │
│ Control Buttons:                                            │
│ MODE BTN ─────── GPIO19                                     │
│ MUTE BTN ─────── GPIO20                                     │
│ CALIBRATE BTN ── GPIO26                                     │
│                                                             │
│ ADC0834 (Sensitivity Control):                              │
│ CS ──────────── GPIO5                                      │
│ CLK ─────────── GPIO6                                      │
│ DI ──────────── GPIO16                                     │
│ DO ──────────── GPIO12                                     │
│                                                             │
│ I2C LCD Display:                                           │
│ SDA ─────────── GPIO2                                      │
│ SCL ─────────── GPIO3                                      │
│ VCC ─────────── 5V                                         │
│ GND ─────────── GND                                         │
└─────────────────────────────────────────────────────────────┘

Distance Zones Configuration:
┌─────────────────────────────────────────────────────────────┐
│                  DETECTION ZONES                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  0m ──┬── 0.1m ──┬── 0.3m ──┬── 0.5m ──┬── 1.0m ──┬── 2.0m │
│       │          │          │          │          │        │
│    CRITICAL   DANGER    WARNING    CAUTION     SAFE       │
│       │          │          │          │          │        │
│    🚨 ████    ☢ ███     ⚠ ██      ! █       ✓ ░        │
│       │          │          │          │          │        │
│  Continuous  Fast beep  Med beep  Slow beep   No beep     │
│    alarm                                                    │
│                                                             │
│ LED Patterns:                                               │
│ CRITICAL: All LEDs, Red flashing rapidly                    │
│ DANGER:   Orange + Red pulsing                              │
│ WARNING:  Yellow + Orange steady                            │
│ CAUTION:  Green + Yellow steady                             │
│ SAFE:     Green only                                        │
└─────────────────────────────────────────────────────────────┘

HC-SR04 Ultrasonic Sensor:
┌─────────────────┐
│     HC-SR04     │
├─────────────────┤
│ VCC ── 5V       │  (5V power required)
│ Trig ─ GPIO23   │  (Trigger pulse)
│ Echo ─ GPIO24   │  (Echo response)
│ GND ── GND      │
└─────────────────┘

LED Connections (with 220Ω resistors):
GREEN:  GPIO17 ── 220Ω ── LED ── GND
YELLOW: GPIO27 ── 220Ω ── LED ── GND
ORANGE: GPIO22 ── 220Ω ── LED ── GND
RED:    GPIO18 ── 220Ω ── LED ── GND (PWM capable)

Button Connections (with internal pull-up):
MODE:      GPIO19 ── Button ── GND
MUTE:      GPIO20 ── Button ── GND
CALIBRATE: GPIO26 ── Button ── GND

ADC0834 with Potentiometer:
┌─────────────────┐    ┌─────────────────┐
│     ADC0834     │    │  10kΩ Pot       │
├─────────────────┤    ├─────────────────┤
│ VCC ── 5V       │    │ Pin 1 ── 5V     │
│ CS ──  GPIO5    │    │ Pin 2 ── ADC CH0│
│ CLK ── GPIO6    │    │ Pin 3 ── GND    │
│ DI ──  GPIO16   │    └─────────────────┘
│ DO ──  GPIO12   │    (Sensitivity control)
│ CH0 ── Pot Pin2 │
│ GND ── GND      │
└─────────────────┘
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and hardware control
pip install gpiozero numpy

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/06-reversing-alarm
python ultrasonic-parking-sensor.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Parking simulation
make test     # Test all components
make calibrate # Calibrate sensor
make setup    # Install dependencies
```

## Code Walkthrough

### Distance Measurement with Smoothing
Reliable distance detection with noise filtering:
```python
def _sensor_monitoring_loop(self):
    while self.monitoring_active:
        # Get raw distance reading
        raw_distance = self.ultrasonic.distance
        
        # Apply calibration offset
        distance = raw_distance + self.calibration_offset
        
        # Add to history for smoothing
        self.distance_history.append(distance)
        if len(self.distance_history) > self.smoothing_window:
            self.distance_history.pop(0)
        
        # Use median for noise reduction
        if len(self.distance_history) >= 3:
            smoothed_distance = median(self.distance_history)
        else:
            smoothed_distance = distance
```

### Multi-Zone Detection System
Graduated zones for progressive warnings:
```python
def _get_distance_zone(self, distance):
    if distance <= ZONE_CRITICAL:    # < 0.1m
        return DistanceZone.CRITICAL
    elif distance <= ZONE_DANGER:     # < 0.3m
        return DistanceZone.DANGER
    elif distance <= ZONE_WARNING:    # < 0.5m
        return DistanceZone.WARNING
    elif distance <= ZONE_CAUTION:    # < 1.0m
        return DistanceZone.CAUTION
    else:                            # > 2.0m
        return DistanceZone.SAFE
```

### Dynamic Alert Patterns
Zone-based alert timing:
```python
BEEP_PATTERNS = {
    'safe': None,                              # No beep
    'caution': {'on': 0.5, 'off': 1.0},       # Slow
    'warning': {'on': 0.3, 'off': 0.5},       # Medium
    'danger': {'on': 0.2, 'off': 0.2},        # Fast
    'critical': {'on': 0.1, 'off': 0.05}      # Very fast
}
```

### LED Indicator Control
Progressive visual feedback:
```python
def _update_led_indicators(self, zone):
    self._all_leds_off()
    
    if zone == DistanceZone.SAFE:
        self.led_green.on()
    elif zone == DistanceZone.CAUTION:
        self.led_green.on()
        self.led_yellow.on()
    elif zone == DistanceZone.WARNING:
        self.led_yellow.on()
        self.led_orange.on()
    elif zone == DistanceZone.DANGER:
        self.led_orange.on()
        self.led_red.pulse(fade_in_time=0.2, fade_out_time=0.2)
    elif zone == DistanceZone.CRITICAL:
        # Emergency pattern
        self.led_yellow.on()
        self.led_orange.on()
        self.led_red.blink(on_time=0.1, off_time=0.1)
```

### Automatic Calibration
Environmental adaptation:
```python
def _calibrate_sensor(self):
    # Take multiple readings
    readings = []
    for i in range(20):
        distance = self.ultrasonic.distance
        readings.append(distance)
        time.sleep(0.1)
    
    # Calculate calibration offset
    avg_distance = mean(readings)
    
    # Assume clear area should read as max distance
    self.calibration_offset = self.max_detection_distance - avg_distance
```

## Alert Modes

### 1. Standard Mode
Traditional beeping alerts with zone-based timing:
- **Safe**: No alert
- **Caution**: Slow beep (0.5s on, 1s off)
- **Warning**: Medium beep (0.3s on, 0.5s off)
- **Danger**: Fast beep (0.2s on, 0.2s off)
- **Critical**: Very fast beep (0.1s on, 0.05s off)

### 2. Voice Mode
Simulated voice announcements:
- Different beep patterns simulate speech
- Would use text-to-speech in production
- Zone-specific "announcements"

### 3. Tone Mode
Musical tones for different zones:
- Each zone has a different frequency
- More pleasant than standard beeping
- Easier to distinguish zones

### 4. Visual Only Mode
Silent operation with LED indicators only:
- For quiet environments
- Relies on visual feedback
- All audio alerts disabled

### 5. Emergency Mode
Enhanced alerts for critical situations:
- Continuous alarm in critical zone
- Emergency stop simulation
- All LEDs flash in critical zone

## Features

### Real-Time Display
- Current distance and zone
- Mode and sensitivity settings
- Statistics and alert count
- Rotating information display

### Sensitivity Control
- Potentiometer-based adjustment
- Real-time sensitivity changes
- Affects detection thresholds

### Data Logging
- Zone changes logged to file
- Timestamp and distance records
- Session statistics tracking

### Emergency Stop Simulation
- Triggered in critical zone with emergency mode
- Visual alert with all LEDs
- Would engage brakes in real vehicle

## Available Demos

1. **Parking Simulation**: Step through all zones
2. **Calibration Test**: Test calibration procedure
3. **Alert Mode Demo**: Cycle through all alert modes
4. **Statistics Review**: View session statistics

## Troubleshooting

### Inaccurate distance readings
- Check sensor mounting (must be stable)
- Ensure clear path to target
- Verify 5V power to sensor
- Run calibration procedure
- Check for ultrasonic interference

### No detection or max distance always shown
- Verify trigger and echo connections
- Check sensor orientation
- Test with different target surfaces
- Ensure target is within range (2cm-4m)

### Erratic readings
- Increase smoothing window
- Check for vibrations
- Shield from wind/air currents
- Use median filtering
- Check power supply stability

### LCD display issues
- Verify I2C address with `i2cdetect -y 1`
- Check I2C connections
- Ensure I2C is enabled
- Test with different address (0x27 or 0x3F)

### Alert not working
- Check mute status
- Verify buzzer connections
- Test alert mode setting
- Check buzzer polarity
- Test with manual beep

## Advanced Usage

### Custom Zone Configuration
Adjust zones for specific applications:
```python
# Forklift application with tighter zones
ZONE_SAFE = 1.0      # > 1m
ZONE_CAUTION = 0.5   # 0.5-1m
ZONE_WARNING = 0.3   # 0.3-0.5m
ZONE_DANGER = 0.15   # 0.15-0.3m
ZONE_CRITICAL = 0.05 # < 0.05m
```

### Integration with Vehicle Systems
Connect to vehicle controls:
```python
def integrate_with_vehicle(self):
    # Connect to CAN bus
    self.can_interface = CANInterface()
    
    # Send distance data
    def send_distance_to_vehicle():
        if self.current_distance:
            self.can_interface.send_distance(self.current_distance)
            
            # Auto-brake in critical zone
            if self.current_zone == DistanceZone.CRITICAL:
                self.can_interface.engage_emergency_brake()
```

### Multiple Sensor Array
Use multiple sensors for full coverage:
```python
class MultiSensorParkingSystem:
    def __init__(self):
        self.sensors = {
            'center': DistanceSensor(echo=24, trigger=23),
            'left': DistanceSensor(echo=8, trigger=25),
            'right': DistanceSensor(echo=7, trigger=1)
        }
    
    def get_closest_distance(self):
        distances = [s.distance for s in self.sensors.values()]
        return min(distances)
```

### Obstacle Mapping
Create spatial map of obstacles:
```python
def create_obstacle_map(self):
    # Sweep sensor with servo
    obstacle_map = {}
    
    for angle in range(0, 180, 10):
        self.servo.angle = angle
        time.sleep(0.1)
        
        distance = self.ultrasonic.distance
        obstacle_map[angle] = distance
    
    return obstacle_map
```

### Network Integration
Send alerts to remote monitoring:
```python
import socket

def send_alert_to_network(self, zone, distance):
    alert_data = {
        'vehicle_id': 'TRUCK_001',
        'timestamp': datetime.now().isoformat(),
        'zone': zone.value,
        'distance': distance,
        'gps_location': self.get_gps_location()
    }
    
    # Send to monitoring server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(alert_data).encode(), 
                ('monitor.example.com', 9999))
```

## Performance Optimization

### Sensor Reading Optimization
- Use hardware interrupts for echo pin
- Implement timeout for stuck readings
- Cache readings when stationary
- Reduce polling frequency at safe distances

### Power Management
- Sleep mode when vehicle stopped
- Reduce LED brightness in daylight
- Disable unused alert modes
- Use PWM for power-efficient buzzers

### Response Time
- Minimize processing in critical path
- Use separate threads for alerts
- Pre-calculate alert patterns
- Optimize zone detection logic

## Integration Ideas

### Automotive Applications
- Car reversing sensors
- Truck blind spot monitoring
- Forklift collision prevention
- Parking assist systems

### Industrial Safety
- Loading dock positioning
- Crane proximity warnings
- Conveyor belt safety zones
- Robot workspace monitoring

### Smart Parking
- Garage parking guides
- Parallel parking assistance
- Parking space detection
- Multi-level parking systems

### Accessibility
- Assistance for visually impaired
- Wheelchair navigation aids
- Walking stick enhancement
- Doorway detection

## Next Steps
- Add multiple sensor support for 360° coverage
- Implement vehicle speed integration
- Add camera for visual confirmation
- Create smartphone app for configuration
- Integrate with vehicle CAN bus
- Add obstacle classification (wall vs. person)
- Implement predictive collision detection