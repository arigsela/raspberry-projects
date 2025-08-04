# Object Counting Device

Intelligent object detection and counting system using ultrasonic sensors with directional analysis, multiple counting modes, LCD display, and comprehensive statistics.

## What You'll Learn
- Ultrasonic sensor arrays for object detection
- Directional movement analysis algorithms
- Multi-sensor fusion and correlation
- Real-time display systems with I2C LCD
- Statistical analysis and data logging
- False positive filtering techniques
- Calibration and sensitivity adjustment
- Multi-threaded real-time processing

## Hardware Requirements
- Raspberry Pi 5
- 3x Ultrasonic sensors (HC-SR04) for entrance, exit, and reference
- 16x2 LCD display with I2C backpack
- ADC0834 for sensitivity adjustment (potentiometer)
- 10kΩ potentiometer for sensitivity control
- 4x Push buttons for control
- 4x LEDs for status indication (including 2 PWM LEDs)
- 2x Buzzers for audio feedback
- Jumper wires
- Breadboard or perfboard
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)

## Circuit Diagram

```
Object Counting Device System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Ultrasonic Sensors (HC-SR04):                              │
│ Entrance Sensor:  Trig=GPIO23, Echo=GPIO24                 │
│ Exit Sensor:      Trig=GPIO25, Echo=GPIO8                  │
│ Reference Sensor: Trig=GPIO7,  Echo=GPIO1                  │
│                                                             │
│ I2C LCD Display:  SDA=GPIO2, SCL=GPIO3                     │
│ LCD I2C Address:  0x27 (typical)                           │
│                                                             │
│ ADC0834 for Sensitivity Control:                           │
│ CS=GPIO5, CLK=GPIO6, DI=GPIO16, DO=GPIO26                  │
│ Channel 0: Connected to 10kΩ potentiometer                 │
│                                                             │
│ Control Buttons:                                            │
│ RESET=GPIO17, MODE=GPIO18, CALIBRATE=GPIO27, SETTINGS=GPIO22│
│                                                             │
│ Status LEDs:                                                │
│ COUNT=GPIO26 (PWM), DIRECTION=GPIO19, STATUS=GPIO20 (PWM)  │
│ ERROR=GPIO21                                                │
│                                                             │
│ Audio Feedback:                                             │
│ COUNT_BUZZER=GPIO13, ALERT_BUZZER=GPIO12                   │
│                                                             │
│ Power: 5V for sensors, 3.3V for logic                     │
└─────────────────────────────────────────────────────────────┘

Physical Installation Layout:
┌─────────────────────────────────────────────────────────────┐
│                 Counting Zone Layout                        │
│                                                             │
│    [Reference Sensor] ← Mounted high for calibration       │
│           │                                                 │
│           ▼                                                 │
│    ┌─────────────────┐                                     │
│    │                 │ ← Object path                       │
│ [Entrance] ──→ [Exit] │                                     │
│  Sensor      Sensor   │                                     │
│    │                 │                                     │
│    └─────────────────┘                                     │
│                                                             │
│ Entrance Sensor: Detects objects entering the zone         │
│ Exit Sensor:     Detects objects leaving the zone          │
│ Reference:       Provides baseline for calibration         │
│                                                             │
│ Optimal sensor spacing: 20-50cm apart                      │
│ Mounting height: 10-30cm above object path                 │
│ Detection range: 2cm - 200cm (typical HC-SR04)            │
└─────────────────────────────────────────────────────────────┘

HC-SR04 Ultrasonic Sensor Connections:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Entrance Sensor │    │  Exit Sensor    │    │Reference Sensor │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ VCC ── 5V       │    │ VCC ── 5V       │    │ VCC ── 5V       │
│ Trig ── GPIO23  │    │ Trig ── GPIO25  │    │ Trig ── GPIO7   │
│ Echo ── GPIO24  │    │ Echo ── GPIO8   │    │ Echo ── GPIO1   │
│ GND ── GND      │    │ GND ── GND      │    │ GND ── GND      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

I2C LCD Display (16x2 with I2C backpack):
┌─────────────────┐
│   LCD Display   │
├─────────────────┤
│ VCC ── 5V       │
│ GND ── GND      │
│ SDA ── GPIO2    │
│ SCL ── GPIO3    │
└─────────────────┘

ADC0834 and Potentiometer:
┌─────────────────┐    ┌─────────────────┐
│     ADC0834     │    │ 10kΩ Pot (Sens) │
├─────────────────┤    ├─────────────────┤
│ VCC ── 5V       │    │ Pin 1 ── 5V     │
│ GND ── GND      │    │ Pin 2 ── ADC CH0│
│ CS ──  GPIO5    │    │ Pin 3 ── GND    │
│ CLK ── GPIO6    │    └─────────────────┘
│ DI ──  GPIO16   │
│ DO ──  GPIO26   │
│ CH0 ── Pot Pin2 │
└─────────────────┘

Button Connections (with 10kΩ pull-up resistors):
RESET Button:     GPIO17 ── Button ── GND
MODE Button:      GPIO18 ── Button ── GND
CALIBRATE Button: GPIO27 ── Button ── GND
SETTINGS Button:  GPIO22 ── Button ── GND

LED Connections (with 220Ω current limiting resistors):
COUNT LED:        GPIO26 ── 220Ω ── LED ── GND (PWM for effects)
DIRECTION LED:    GPIO19 ── 220Ω ── LED ── GND
STATUS LED:       GPIO20 ── 220Ω ── LED ── GND (PWM for breathing)
ERROR LED:        GPIO21 ── 220Ω ── LED ── GND

Buzzers:
COUNT_BUZZER:     GPIO13 ── Buzzer ── GND
ALERT_BUZZER:     GPIO12 ── Buzzer ── GND
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and hardware control
pip install gpiozero

# I2C communication for LCD
sudo apt install python3-smbus
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/04-counting-device
python object-counting-device.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Automatic demonstration
make test     # Test all components
make calibrate # Run calibration sequence
make setup    # Install dependencies
```

## Code Walkthrough

### Multi-Sensor Detection System
Initialize ultrasonic sensor array:
```python
def __init__(self):
    # Initialize sensor array with different purposes
    self.entrance_sensor = DistanceSensor(echo=ENTRANCE_ECHO_PIN, trigger=ENTRANCE_TRIG_PIN, 
                                        max_distance=2.0, threshold_distance=0.3)
    self.exit_sensor = DistanceSensor(echo=EXIT_ECHO_PIN, trigger=EXIT_TRIG_PIN,
                                    max_distance=2.0, threshold_distance=0.3) 
    self.reference_sensor = DistanceSensor(echo=REFERENCE_ECHO_PIN, trigger=REFERENCE_TRIG_PIN,
                                         max_distance=2.0, threshold_distance=0.3)
```

### Directional Movement Analysis
Analyze sensor sequences to determine object direction:
```python
def _analyze_direction_pattern(self, sequence):
    # Extract sensor events in chronological order
    events = [(event['sensor'], event['action'], event['timestamp']) for event in sequence]
    events.sort(key=lambda x: x[2])  # Sort by timestamp
    
    # Pattern analysis for entering: entrance triggered first, then exit
    first_trigger = None
    for sensor, action, timestamp in events:
        if action == 'triggered' and first_trigger is None:
            first_trigger = sensor
    
    if first_trigger == 'entrance':
        if any(event[0] == 'exit' and event[1] == 'triggered' for event in events):
            return 'entering'
    elif first_trigger == 'exit':
        if any(event[0] == 'entrance' and event[1] == 'triggered' for event in events):
            return 'exiting'
    
    return 'unknown'
```

### Stable Detection Algorithm
Filter noise and ensure reliable object detection:
```python
def _is_stable_detection(self, readings, threshold):
    if len(readings) < 3:
        return False
    
    # Check if recent readings consistently indicate object presence
    recent_readings = readings[-3:]
    return all(reading < threshold for reading in recent_readings)
```

### Real-Time Display Management
Multi-threaded display updates with rotating information:
```python
def _display_loop(self):
    display_cycle = 0
    
    while self.monitoring_active:
        # Cycle through different display modes
        if display_cycle % 60 == 0:          # Current count
            self._update_display()
        elif display_cycle % 120 == 60:      # Statistics
            self._show_statistics_display()
        elif display_cycle % 180 == 120:     # Mode info
            self._show_mode_display()
        
        display_cycle = (display_cycle + 1) % 180
        time.sleep(0.05)
```

### Automatic Calibration System
Intelligent baseline establishment:
```python
def _start_calibration(self):
    # Take multiple readings for stability
    calibration_readings = {'entrance': [], 'exit': [], 'reference': []}
    
    for i in range(20):
        calibration_readings['entrance'].append(self.entrance_sensor.distance)
        calibration_readings['exit'].append(self.exit_sensor.distance)
        calibration_readings['reference'].append(self.reference_sensor.distance)
        time.sleep(0.1)
    
    # Calculate baseline distances using median for noise immunity
    self.baseline_distance = statistics.median(calibration_readings['reference'])
    
    # Update detection threshold based on calibration
    self.detection_threshold = min(0.3, self.baseline_distance * 0.8)
```

## Counting Modes

### 1. Bidirectional Mode
Counts objects moving in both directions:
- **Use Case**: Doorway monitoring, two-way traffic
- **Display**: Shows separate in/out counts
- **Logic**: Tracks net occupancy (in - out)

### 2. Entrance Only Mode
Counts only objects entering the zone:
- **Use Case**: Visitor counting, entry monitoring
- **Display**: Shows total entries and rate
- **Logic**: Ignores exit detections

### 3. Exit Only Mode
Counts only objects leaving the zone:
- **Use Case**: Production line output, exit monitoring
- **Display**: Shows total exits and rate
- **Logic**: Ignores entrance detections

### 4. Presence Mode
Detects object presence without directional counting:
- **Use Case**: Occupancy detection, presence sensing
- **Display**: Shows current presence status
- **Logic**: Simple presence/absence detection

### 5. Batch Mode
Groups detections for batch counting:
- **Use Case**: Inventory counting, grouped items
- **Display**: Shows batch counts and totals
- **Logic**: Accumulates detections in batches

## Advanced Features

### False Positive Filtering
- **Duration Analysis**: Filters detections too short to be real objects
- **Size Validation**: Ensures detected objects are within expected size range
- **Pattern Recognition**: Learns common false positive patterns
- **Multi-Sensor Correlation**: Requires multiple sensors for confirmation

### Intelligent Sensitivity Adjustment
- **Automatic Calibration**: Establishes baseline distances automatically
- **Environmental Adaptation**: Adjusts to lighting and temperature changes
- **Manual Override**: Potentiometer for manual sensitivity control
- **Learning Mode**: Adapts sensitivity based on historical accuracy

### Comprehensive Statistics
- **Real-Time Rate Calculation**: Objects per hour/minute
- **Hourly Breakdown**: Activity patterns throughout the day
- **Accuracy Metrics**: False positive rates and detection reliability
- **Historical Trends**: Long-term counting patterns

## Available Demos

1. **Interactive Counting**: Real-time object detection with live display
2. **Automatic Demo**: Simulated object movements through all modes
3. **Calibration Test**: Sensor calibration and sensitivity adjustment
4. **Statistics Review**: Historical data analysis and reporting

## Troubleshooting

### Sensors not detecting objects
- Check 5V power supply to sensors
- Verify trigger and echo pin connections
- Ensure sensors are not too close to walls
- Test individual sensors with multimeter
- Check mounting stability (vibration affects readings)

### Inaccurate direction detection
- Verify sensor spacing (20-50cm optimal)
- Check sensor alignment (parallel mounting)
- Calibrate sensors in clean environment
- Adjust detection stability requirements
- Ensure objects pass through both sensor zones

### LCD display issues
- Verify I2C connections (SDA/SCL)
- Check I2C address with `i2cdetect -y 1`
- Ensure I2C is enabled in raspi-config
- Test with 5V power to LCD backpack
- Check for I2C address conflicts

### False positive detections
- Increase detection stability requirements
- Enable false positive filtering
- Adjust detection threshold (increase)
- Improve sensor mounting stability
- Shield sensors from environmental interference

### Count drift over time
- Regular calibration recommended
- Check for sensor mounting movement
- Monitor temperature compensation
- Enable environmental adaptation
- Review detection pattern analysis

## Advanced Usage

### Custom Detection Zones
Configure detection areas for specific applications:
```python
# Define custom detection parameters
detection_zones = {
    'entrance': {
        'threshold': 0.15,    # 15cm detection threshold
        'stability': 5,       # 5 consecutive readings
        'timeout': 2.0        # 2 second timeout
    },
    'exit': {
        'threshold': 0.20,    # 20cm detection threshold  
        'stability': 3,       # 3 consecutive readings
        'timeout': 3.0        # 3 second timeout
    }
}
```

### Environmental Compensation
Adjust for temperature and humidity effects:
```python
def compensate_for_environment(self, temperature, humidity):
    # Speed of sound varies with temperature and humidity
    temp_compensation = 1 + (temperature - 20) * 0.0017
    humidity_compensation = 1 + (humidity - 50) * 0.0001
    
    total_compensation = temp_compensation * humidity_compensation
    
    # Apply compensation to all distance readings
    for sensor in [self.entrance_sensor, self.exit_sensor, self.reference_sensor]:
        sensor.compensation_factor = total_compensation
```

### Machine Learning Integration
Add pattern recognition for improved accuracy:
```python
import sklearn.ensemble

class MLDetectionFilter:
    def __init__(self):
        self.classifier = sklearn.ensemble.RandomForestClassifier()
        self.features = []  # Distance, duration, pattern features
        self.labels = []    # True positive / false positive labels
    
    def extract_features(self, detection_sequence):
        # Extract relevant features from detection sequence
        duration = detection_sequence[-1]['timestamp'] - detection_sequence[0]['timestamp']
        sensor_count = len(set(event['sensor'] for event in detection_sequence))
        
        return [duration, sensor_count, len(detection_sequence)]
    
    def is_valid_detection(self, detection_sequence):
        features = self.extract_features(detection_sequence)
        return self.classifier.predict([features])[0] == 1
```

### Network Integration
Send counting data to remote systems:
```python
import requests
import json

def send_count_update(self, count_data):
    endpoint = "http://your-server.com/api/counts"
    
    payload = {
        'device_id': 'counter_001',
        'timestamp': datetime.now().isoformat(),
        'total_count': count_data['total_count'],
        'in_count': count_data['in_count'],
        'out_count': count_data['out_count'],
        'mode': count_data['mode']
    }
    
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        if response.status_code == 200:
            print("✓ Count data uploaded successfully")
    except Exception as e:
        print(f"Upload failed: {e}")
```

### Database Integration
Store counting data in local database:
```python
import sqlite3
from datetime import datetime

class CountingDatabase:
    def __init__(self, db_path='counting_data.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                direction TEXT NOT NULL,
                mode TEXT NOT NULL,
                total_count INTEGER NOT NULL
            )
        ''')
        self.conn.commit()
    
    def log_detection(self, direction, mode, total_count):
        self.conn.execute('''
            INSERT INTO detections (timestamp, direction, mode, total_count)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), direction, mode, total_count))
        self.conn.commit()
```

## Performance Optimization

### Sensor Timing Optimization
- Use hardware interrupts for precise timing
- Implement sensor reading queues for high-speed objects
- Optimize sensor polling frequency based on expected object speed
- Use sensor power management for battery operation

### Processing Efficiency
- Implement circular buffers for sensor data
- Use efficient algorithms for pattern matching
- Optimize LCD update frequency to reduce I2C traffic
- Implement smart caching for display data

### Power Management
- Sleep sensors when not in use
- Implement motion-triggered wake-up
- Optimize LED brightness for power saving
- Use low-power modes during inactive periods

## Integration Ideas

### Industrial Applications
- Production line counting and quality control
- Inventory management with automated tracking
- Warehouse entry/exit monitoring
- Assembly line productivity measurement

### Retail and Commercial
- Customer traffic analysis
- Store occupancy monitoring
- Queue length management
- Product display interaction tracking

### Smart Building Integration
- Room occupancy for HVAC control
- Automatic lighting based on presence
- Security monitoring with access logging
- Energy management optimization

### Research and Analytics
- Behavioral pattern analysis
- Traffic flow studies
- Space utilization research
- Long-term trend analysis

## Next Steps
- Add computer vision integration for object classification
- Implement wireless connectivity (WiFi/Bluetooth)
- Create mobile app for remote monitoring
- Add cloud analytics and reporting
- Integrate with existing building management systems
- Develop machine learning models for pattern recognition
- Add support for multiple counting zones