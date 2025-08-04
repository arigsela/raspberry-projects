# Multi-Sensor Alarm System

Comprehensive home security system with motion detection, door/window monitoring, glass break detection, smoke alarm integration, and intelligent alert management.

## What You'll Learn
- Multi-zone security systems
- PIR motion sensor integration
- Magnetic contact sensors
- Glass break detection
- Alarm state machines
- Entry/exit delays
- Zone bypassing
- Alert prioritization
- Notification systems

## Hardware Requirements
- Raspberry Pi 5
- 4x PIR motion sensors
- 2x Magnetic door sensors
- 2x Magnetic window sensors
- 1x Glass break sensor (or microphone + ADC)
- 1x Smoke detector interface
- 1x Siren (12V with relay)
- 1x Strobe light
- 1x Interior buzzer
- 3x Status LEDs (Armed, Ready, Alert)
- 3x Control buttons (Arm, Panic, Test)
- 16x2 LCD display with I2C backpack
- ADC0834 for analog sensors
- Relay modules for siren/strobe
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- Jumper wires and breadboard

## Circuit Diagram

```
Multi-Sensor Alarm System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Motion Sensors (PIR):                                       │
│ ZONE 1 PIR ───── GPIO17 (Living Room)                     │
│ ZONE 2 PIR ───── GPIO27 (Kitchen)                         │
│ ZONE 3 PIR ───── GPIO22 (Bedroom)                         │
│ ZONE 4 PIR ───── GPIO23 (Garage)                          │
│                                                             │
│ Door/Window Sensors (Magnetic):                            │
│ FRONT DOOR ───── GPIO24 (N.C. contact)                    │
│ BACK DOOR ────── GPIO25 (N.C. contact)                    │
│ WINDOW 1 ─────── GPIO8  (N.C. contact)                    │
│ WINDOW 2 ─────── GPIO7  (N.C. contact)                    │
│                                                             │
│ Glass Break Sensor (via ADC0834):                          │
│ ADC CS ────────── GPIO5                                    │
│ ADC CLK ───────── GPIO6                                    │
│ ADC DI ────────── GPIO16                                   │
│ ADC DO ────────── GPIO12                                   │
│ ADC CH0 ───────── Glass break sensor                      │
│                                                             │
│ Special Sensors:                                            │
│ SMOKE ALARM ───── GPIO13 (Interface circuit)              │
│                                                             │
│ Alert Outputs:                                              │
│ SIREN RELAY ───── GPIO19 (12V siren)                      │
│ STROBE LIGHT ──── GPIO26 (PWM control)                    │
│ INTERIOR BUZZER ─ GPIO21 (Warning sounds)                 │
│                                                             │
│ Status Indicators:                                          │
│ ARMED LED ─────── GPIO20 (Red - System armed)             │
│ READY LED ─────── GPIO14 (Green - Ready to arm)           │
│ ALERT LED ─────── GPIO15 (Yellow - Alert/trouble)         │
│                                                             │
│ Control Panel:                                              │
│ ARM BUTTON ────── GPIO18 (Arm/disarm)                     │
│ PANIC BUTTON ──── GPIO9  (Emergency alarm)                │
│ TEST BUTTON ───── GPIO10 (System test)                    │
│                                                             │
│ LCD Display:                                                │
│ SDA ───────────── GPIO2  (I2C Data)                       │
│ SCL ───────────── GPIO3  (I2C Clock)                      │
└─────────────────────────────────────────────────────────────┘

Security Zone Layout:
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY ZONES                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Perimeter Zone:                                            │
│  - All doors and windows                                    │
│  - Active in all armed modes                               │
│  - Entry/exit delays apply                                 │
│                                                             │
│  Interior Zone:                                             │
│  - Motion sensors                                           │
│  - Active in Away mode only                                │
│  - Can be bypassed for Stay mode                          │
│                                                             │
│  24-Hour Zone:                                              │
│  - Smoke/fire detectors                                    │
│  - Panic buttons                                            │
│  - Always active (even when disarmed)                      │
│                                                             │
│  Instant Zone:                                              │
│  - Glass break sensors                                     │
│  - No entry delay                                          │
│  - Immediate alarm                                         │
└─────────────────────────────────────────────────────────────┘

PIR Motion Sensor Connection:
┌─────────────────────────────────────────────────────────────┐
│     PIR Sensor                                              │
│     ┌─────────┐                                            │
│     │ VCC OUT │                                            │
│     │  │   │  │                                            │
│     └──┼───┼──┘                                            │
│        │   │                                               │
│     3.3V   └── GPIO (Active HIGH when motion detected)     │
│     GND                                                     │
└─────────────────────────────────────────────────────────────┘

Magnetic Contact Connection:
┌─────────────────────────────────────────────────────────────┐
│     Door/Window Sensor                                      │
│     ┌─────────┐                                            │
│     │ NO C NC │  (Use NC - Normally Closed)               │
│     └──┬───┬──┘                                            │
│        │   │                                               │
│     GPIO   GND   (Closed = Secure, Open = Triggered)      │
│      ↑                                                      │
│   Pull-up resistor (internal or 10kΩ external)            │
└─────────────────────────────────────────────────────────────┘

Glass Break Detection:
┌─────────────────────────────────────────────────────────────┐
│ Microphone → Amplifier → ADC → Raspberry Pi                │
│                                                             │
│ Detection: Sudden high-frequency spike (breaking glass)    │
│ Baseline: Continuous ambient noise level                   │
│ Threshold: Baseline + defined offset                       │
└─────────────────────────────────────────────────────────────┘
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and sensor control
pip install gpiozero

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/12-alarm-bell
python multi-sensor-alarm-system.py
```

Or use the Makefile:
```bash
make          # Run the alarm system
make demo     # Alarm features demo
make test     # Test all sensors
make zones    # Show zone configuration
make setup    # Install dependencies
```

## Code Walkthrough

### Multi-Zone Security Architecture
Organizing sensors into logical zones:
```python
class Zone:
    def __init__(self, name, zone_type="interior"):
        self.name = name
        self.zone_type = zone_type  # interior, perimeter, 24hour
        self.sensors = []
        self.enabled = True
        
    def is_secure(self):
        return all(sensor.is_secure() for sensor in self.sensors)
```

### Sensor Management
Unified sensor interface:
```python
class SecuritySensor:
    def __init__(self, name, sensor_type, pin):
        if sensor_type == SensorType.MOTION:
            self.sensor = MotionSensor(pin)
            self.sensor.when_motion = self._motion_detected
        elif sensor_type in [SensorType.DOOR, SensorType.WINDOW]:
            self.sensor = Button(pin, pull_up=True)
            self.sensor.when_pressed = self._contact_opened
```

### Alarm State Machine
Managing system states:
```python
class AlarmMode(Enum):
    DISARMED = "Disarmed"
    ARMED_STAY = "Armed Stay"     # Home mode
    ARMED_AWAY = "Armed Away"     # Away mode
    ARMED_NIGHT = "Armed Night"   # Sleep mode
    ENTRY_DELAY = "Entry Delay"
    EXIT_DELAY = "Exit Delay"
    ALARM_TRIGGERED = "ALARM"
```

### Entry/Exit Delays
Graceful arming and disarming:
```python
def _start_entry_delay(self, sensor):
    self.mode = AlarmMode.ENTRY_DELAY
    self.buzzer.beep(0.2, 0.3, n=None, background=True)
    
    # Start countdown timer
    self.entry_timer = threading.Timer(
        self.config['entry_delay'], 
        lambda: self._trigger_alarm(f"Entry timeout")
    )
    self.entry_timer.start()
```

### Glass Break Detection
Audio spike detection algorithm:
```python
def _glass_break_monitor(self):
    baseline = None
    samples = deque(maxlen=10)
    
    while self.running:
        value = self.adc.read(GLASS_SENSOR_CHANNEL)
        samples.append(value)
        
        if baseline is None and len(samples) == 10:
            baseline = sum(samples) / len(samples)
            
        # Detect sudden spike
        if baseline and value > baseline + GLASS_THRESHOLD:
            self._trigger_alarm("Glass Break", AlertPriority.HIGH)
```

## Operating Modes

### 1. Disarmed
- All zones inactive except 24-hour
- System ready indicators
- Full access allowed

### 2. Armed Stay (Home)
- Perimeter zones active
- Interior motion sensors bypassed
- For when occupants are home

### 3. Armed Away
- All zones active
- Full protection
- Entry/exit delays enabled

### 4. Armed Night (Sleep)
- Perimeter active
- Selected interior zones active
- Bedroom motion bypassed

### 5. Entry Delay
- Temporary state after entry
- Warning beeps
- Must disarm before timeout

### 6. Exit Delay
- Time to leave after arming
- Progressive beep warnings
- Auto-arms after countdown

## Alert Priority System

### Priority Levels
1. **LOW**: System events, status changes
2. **MEDIUM**: Zone faults, troubles
3. **HIGH**: Security breaches
4. **CRITICAL**: Multiple zones triggered
5. **EMERGENCY**: Fire, panic, duress

### Notification Methods
- Local siren and strobe
- Email notifications
- SMS alerts (via service)
- Monitoring station
- Event logging

## Features

### Security Features
- Multi-zone protection
- Configurable delays
- Zone bypassing
- Chime mode
- Duress codes
- Tamper detection

### Smart Features
- Auto-arm scheduling
- Vacation mode
- Pet-immune sensors
- False alarm reduction
- Battery backup
- Remote management

### User Interface
- LCD status display
- LED indicators
- Audible feedback
- One-touch arming
- Panic button
- System test mode

### Monitoring
- Event logging
- Sensor statistics
- Alarm history
- Zone activity
- System health

## Available Demos

1. **Alarm Demo**: Shows all alarm states
2. **Sensor Test**: Individual sensor testing
3. **Zone Demo**: Zone configuration display
4. **Alert Demo**: Notification testing
5. **Entry Demo**: Entry/exit delay simulation

## Troubleshooting

### PIR sensor false triggers
- Adjust sensitivity potentiometer
- Check for heat sources
- Verify mounting height
- Use pet-immune sensors
- Check power stability

### Door sensor issues
- Verify magnet alignment
- Check gap distance (<1cm)
- Test with multimeter
- Check pull-up resistor
- Clean contacts

### System won't arm
- Check all zones secure
- Look for open sensors
- Verify sensor power
- Check for faults
- Review event log

### Glass break false alarms
- Adjust sensitivity threshold
- Filter background noise
- Check microphone placement
- Add frequency analysis
- Use dual-technology sensors

### Communication failures
- Check network connection
- Verify credentials
- Test email settings
- Check firewall rules
- Review error logs

## Advanced Usage

### Custom Zone Configuration
Define specialized zones:
```python
# Garage zone with different timing
garage_zone = Zone("Garage", "delayed")
garage_zone.entry_delay = 45  # Longer entry time
garage_zone.add_sensor(garage_door_sensor)
garage_zone.add_sensor(garage_motion_sensor)
```

### Integration with Smart Home
Home Assistant integration:
```python
import paho.mqtt.client as mqtt

def publish_status(self):
    client = mqtt.Client()
    client.connect("homeassistant.local", 1883)
    
    status = {
        "armed": self.mode != AlarmMode.DISARMED,
        "triggered": self.alarm_active,
        "zones": {z.name: z.is_secure() for z in self.zones.values()}
    }
    
    client.publish("alarm/status", json.dumps(status))
```

### Advanced Detection Algorithms
Pattern recognition for glass break:
```python
def analyze_audio_signature(self, samples):
    # FFT for frequency analysis
    frequencies = np.fft.fft(samples)
    
    # Glass break typically 3-5kHz
    glass_freq_range = frequencies[3000:5000]
    
    # Check for characteristic pattern
    if np.max(glass_freq_range) > threshold:
        return True
```

### Scheduling and Automation
Automatic arming schedule:
```python
class ArmingSchedule:
    def __init__(self, system):
        self.system = system
        self.schedule = [
            {"time": "22:00", "mode": AlarmMode.ARMED_NIGHT, "days": [0,1,2,3,4]},
            {"time": "08:00", "mode": AlarmMode.ARMED_AWAY, "days": [1,2,3,4,5]},
            {"time": "17:00", "mode": AlarmMode.DISARMED, "days": [1,2,3,4,5]}
        ]
```

### Machine Learning Integration
Anomaly detection:
```python
from sklearn.ensemble import IsolationForest

class SmartDetection:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
        self.training_data = []
        
    def detect_anomaly(self, sensor_pattern):
        # Detect unusual activity patterns
        prediction = self.model.predict([sensor_pattern])
        return prediction[0] == -1
```

## Integration Ideas

### Professional Security
- Central monitoring station
- Guard tour verification
- Video verification
- Two-way voice
- Cellular backup

### Home Automation
- Light control on alarm
- Door lock integration
- Camera activation
- HVAC shutdown
- Scene activation

### Business Applications
- Access control integration
- Time-based permissions
- Employee tracking
- Asset protection
- Compliance logging

### Neighborhood Watch
- Community alerts
- Shared camera feeds
- Incident mapping
- Response coordination
- Statistics sharing

## Performance Optimization

### Sensor Polling
- Use interrupts vs polling
- Optimize scan rates
- Batch sensor reads
- Priority queuing

### False Alarm Reduction
- Cross-zone verification
- Environmental compensation
- Pattern analysis
- Adaptive thresholds

### Power Management
- Sleep between checks
- Reduce LED brightness
- Optimize radio usage
- Battery monitoring

## Next Steps
- Add camera integration for visual verification
- Implement voice control with wake words
- Create mobile app for remote control
- Add AI-powered threat assessment
- Integrate with emergency services
- Implement blockchain audit trail
- Add biometric disarming
