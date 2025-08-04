# LED Traffic Light Control System

Comprehensive traffic light simulation with realistic timing sequences, pedestrian crossing support, emergency vehicle priority, and multiple operating modes.

## What You'll Learn
- Traffic light state machine design
- Timing sequence programming
- Multi-direction control logic
- Pedestrian crossing integration
- Emergency priority systems
- Mode-based operation
- Traffic flow simulation
- Safety interlock implementation

## Hardware Requirements
- Raspberry Pi 5
- 12x LEDs for traffic lights (3 per direction: Red, Yellow, Green)
- 2x LEDs for pedestrian signals (Red "Don't Walk", Green "Walk")
- 1x LED for emergency indicator
- 4x Push buttons (Pedestrian, Emergency, Mode, Manual)
- Buzzer for pedestrian audio signal
- 16x2 LCD display with I2C backpack
- Current limiting resistors (220Ω for all LEDs)
- Pull-up resistors (10kΩ for buttons)
- Jumper wires and breadboard

## Circuit Diagram

```
LED Traffic Light Control System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ North Direction:                                            │
│ RED ─────────── GPIO17                                     │
│ YELLOW ──────── GPIO27                                     │
│ GREEN ───────── GPIO22                                     │
│                                                             │
│ South Direction:                                            │
│ RED ─────────── GPIO23                                     │
│ YELLOW ──────── GPIO24                                     │
│ GREEN ───────── GPIO25                                     │
│                                                             │
│ East Direction:                                             │
│ RED ─────────── GPIO5                                      │
│ YELLOW ──────── GPIO6                                      │
│ GREEN ───────── GPIO13                                     │
│                                                             │
│ West Direction:                                             │
│ RED ─────────── GPIO19                                     │
│ YELLOW ──────── GPIO26                                     │
│ GREEN ───────── GPIO21                                     │
│                                                             │
│ Pedestrian Signals:                                         │
│ PED RED ─────── GPIO20 (Don't Walk)                       │
│ PED GREEN ───── GPIO16 (Walk)                             │
│ PED BUTTON ──── GPIO12 (Request crossing)                 │
│ PED BUZZER ──── GPIO18 (Audio signal)                     │
│                                                             │
│ System Control:                                             │
│ EMERGENCY BTN ─ GPIO14 (Emergency vehicle)                │
│ EMERGENCY LED ─ GPIO15 (Flashing indicator)               │
│ MODE BTN ────── GPIO8  (Change mode)                      │
│ MANUAL BTN ──── GPIO7  (Manual control)                   │
│                                                             │
│ LCD Display:                                                │
│ SDA ─────────── GPIO2  (I2C Data)                         │
│ SCL ─────────── GPIO3  (I2C Clock)                        │
└─────────────────────────────────────────────────────────────┘

Traffic Light Layout:
┌─────────────────────────────────────────────────────────────┐
│                   INTERSECTION LAYOUT                       │
│                                                             │
│                        NORTH                                │
│                     ┌─────────┐                            │
│                     │ R Y G │                              │
│                     └─────────┘                            │
│                          │                                  │
│         WEST        ─────┼─────        EAST               │
│      ┌─────────┐         │         ┌─────────┐            │
│      │ R Y G │          │         │ R Y G │              │
│      └─────────┘         │         └─────────┘            │
│                          │                                  │
│                     ┌─────────┐                            │
│                     │ R Y G │                              │
│                     └─────────┘                            │
│                        SOUTH                                │
│                                                             │
│     🚶 Pedestrian Crossing (All directions)                │
└─────────────────────────────────────────────────────────────┘

Traffic Light Timing Sequence:
┌─────────────────────────────────────────────────────────────┐
│                    STANDARD CYCLE                           │
├─────────────────────────────────────────────────────────────┤
│ Phase 1: N-S Green  (30s) │ E-W Red                       │
│ Phase 2: N-S Yellow (3s)  │ E-W Red                       │
│ Phase 3: All Red    (2s)  │ Safety clearance             │
│ Phase 4: E-W Green  (30s) │ N-S Red                       │
│ Phase 5: E-W Yellow (3s)  │ N-S Red                       │
│ Phase 6: All Red    (2s)  │ Safety clearance             │
│                                                             │
│ Total Cycle Time: 70 seconds                               │
└─────────────────────────────────────────────────────────────┘

LED Connections (all with 220Ω resistors):
North:  Red=GPIO17, Yellow=GPIO27, Green=GPIO22
South:  Red=GPIO23, Yellow=GPIO24, Green=GPIO25
East:   Red=GPIO5,  Yellow=GPIO6,  Green=GPIO13
West:   Red=GPIO19, Yellow=GPIO26, Green=GPIO21

Pedestrian: Red=GPIO20, Green=GPIO16
Emergency:  LED=GPIO15 (PWM for flashing)

Button Connections (with internal pull-up):
PED_REQUEST: GPIO12 ── Button ── GND
EMERGENCY:   GPIO14 ── Button ── GND
MODE:        GPIO8  ── Button ── GND
MANUAL:      GPIO7  ── Button ── GND
```

## Software Dependencies

Install required libraries:
```bash
# GPIO control
pip install gpiozero

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/09-traffic-light
python led-traffic-light-system.py
```

Or use the Makefile:
```bash
make          # Run the traffic light system
make demo     # Traffic pattern demonstration
make test     # Test individual lights
make timing   # Test timing sequences
make setup    # Install dependencies
```

## Code Walkthrough

### Traffic Light State Machine
Individual light control with state tracking:
```python
class TrafficLight:
    def set_red(self):
        self.red.on()
        self.yellow.off()
        self.green.off()
        self.state = "RED"
    
    def set_yellow(self):
        self.red.off()
        self.yellow.on()
        self.green.off()
        self.state = "YELLOW"
    
    def set_green(self):
        self.red.off()
        self.yellow.off()
        self.green.on()
        self.state = "GREEN"
```

### Direction Control
Coordinated multi-direction management:
```python
def _set_direction_green(self, direction):
    if direction == Direction.NORTH_SOUTH:
        self.lights['north'].set_green()
        self.lights['south'].set_green()
        self.lights['east'].set_red()
        self.lights['west'].set_red()
    elif direction == Direction.EAST_WEST:
        self.lights['north'].set_red()
        self.lights['south'].set_red()
        self.lights['east'].set_green()
        self.lights['west'].set_green()
```

### Traffic Cycle Timing
Configurable timing sequences:
```python
def _normal_traffic_cycle(self):
    # North-South green
    self._set_direction_green(Direction.NORTH_SOUTH)
    self._update_display("N-S GREEN", green_time)
    
    for i in range(green_time):
        if not self._check_interrupts():
            return
        self._update_countdown(green_time - i)
        time.sleep(1)
    
    # Yellow phase
    self._set_direction_yellow(Direction.NORTH_SOUTH)
    time.sleep(yellow_time)
    
    # All red safety period
    self._all_red()
    time.sleep(all_red_time)
```

### Pedestrian Crossing
Safe pedestrian signal control:
```python
def _handle_pedestrian_crossing(self):
    # Stop all traffic
    self._all_red()
    time.sleep(ALL_RED_TIME)
    
    # Activate walk signal
    self.ped_red.off()
    self.ped_green.on()
    
    # Audio signal with countdown
    for i in range(PED_CROSSING_TIME):
        if i < PED_CROSSING_TIME - 5:
            self.ped_buzzer.beep(0.1, 0.9, n=1)
        else:
            # Faster beep for last 5 seconds
            self.ped_buzzer.beep(0.1, 0.4, n=1)
```

### Emergency Vehicle Priority
Emergency override system:
```python
def _handle_emergency_mode(self):
    self.emergency_led.pulse()
    
    # Flash all reds with yellow warning
    for _ in range(EMERGENCY_CLEAR_TIME):
        self._all_red()
        time.sleep(0.5)
        
        # Flash yellows as warning
        for light in self.lights.values():
            light.yellow.on()
        time.sleep(0.5)
        for light in self.lights.values():
            light.yellow.off()
```

## Operating Modes

### 1. Standard Mode
Normal traffic flow with equal timing:
- 30 seconds green per direction
- 3 seconds yellow warning
- 2 seconds all-red safety
- Total cycle: 70 seconds

### 2. Peak Hours Mode
Optimized for rush hour traffic:
- North-South: 45 seconds (main route)
- East-West: 25 seconds (side streets)
- Adapts to traffic patterns
- Reduces congestion

### 3. Night Mode
Reduced timing for low traffic:
- 20 seconds green per direction
- Faster cycle times
- Energy efficient
- Quick response

### 4. Pedestrian Priority
Safe crossing mode:
- All traffic stopped
- 20 second crossing time
- Audio signals for accessibility
- Countdown warnings

### 5. Emergency Mode
Emergency vehicle priority:
- All directions red
- Flashing yellow warnings
- 10 second clearance
- Automatic resume

### 6. Manual Mode
Direct control for testing:
- Button-controlled changes
- Override automatic timing
- Maintenance operations
- Traffic direction

### 7. Maintenance Mode
Service and testing:
- All yellows flashing
- Indicates caution
- System active but manual
- Safety warning

## Features

### Safety Systems
- All-red clearance periods
- Yellow warning timing
- Pedestrian countdown
- Emergency override
- Fail-safe defaults

### Traffic Management
- Configurable timing
- Multi-mode operation
- Peak hour optimization
- Pedestrian integration
- Emergency priority

### Monitoring
- Cycle counting
- Violation detection
- Usage statistics
- Performance metrics
- System diagnostics

### User Interface
- LCD status display
- Mode indicators
- Countdown timers
- Button controls
- Audio feedback

## Available Demos

1. **Traffic Pattern Demo**: Shows all light sequences
2. **Light Test**: Individual light verification
3. **Timing Test**: Verify timing accuracy
4. **Emergency Demo**: Emergency override demonstration
5. **Pedestrian Demo**: Crossing sequence test

## Troubleshooting

### Lights not working
- Check LED polarity
- Verify resistor values (220Ω)
- Test individual GPIO pins
- Check power connections
- Verify ground connections

### Timing issues
- Check sleep accuracy
- Verify interrupt handling
- Test system clock
- Check thread synchronization
- Monitor CPU usage

### Button not responding
- Verify pull-up configuration
- Check debounce timing
- Test GPIO input
- Check button connections
- Verify ground connection

### LCD display issues
- Check I2C address (0x27)
- Verify I2C connections
- Enable I2C interface
- Test with i2cdetect
- Check power supply

### Pedestrian signal problems
- Test buzzer separately
- Check audio connections
- Verify timing sequences
- Test button interrupt
- Check LED connections

## Advanced Usage

### Custom Timing Profiles
Create traffic-specific timing:
```python
self.timing_config['SCHOOL_ZONE'] = {
    'green': 40,      # Longer for school crossing
    'yellow': 4,      # Extra warning time
    'all_red': 3,     # Extra safety clearance
    'pedestrian': 30  # Extended crossing time
}
```

### Traffic Flow Optimization
Adaptive timing based on sensors:
```python
def adaptive_timing(self, traffic_density):
    if traffic_density['north_south'] > traffic_density['east_west']:
        # Favor north-south direction
        return {
            'ns_green': 40,
            'ew_green': 20
        }
```

### Network Control
Remote traffic management:
```python
import socket

def remote_control_server(self):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8888))
    
    while True:
        client, addr = server.accept()
        command = client.recv(1024).decode()
        
        if command == "EMERGENCY":
            self._activate_emergency()
        elif command == "NORMAL":
            self.mode = TrafficMode.STANDARD
```

### Vehicle Detection
Integration with sensors:
```python
def vehicle_triggered_green(self):
    # Extend green if vehicles detected
    if self.vehicle_sensor.detected():
        return self.green_time + 10
    return self.green_time
```

### Data Logging
Traffic pattern analysis:
```python
def log_traffic_event(self, event_type, direction):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'event': event_type,
        'direction': direction,
        'mode': self.mode.value,
        'cycle': self.cycle_count
    }
    
    with open('traffic_log.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        writer.writerow(log_entry)
```

## Performance Optimization

### Timing Accuracy
- Use high-resolution timers
- Compensate for processing delays
- Implement phase-locked loops
- Monitor drift over time

### Response Time
- Interrupt-driven buttons
- Priority queue for events
- Minimal processing in loops
- Efficient state machines

### Reliability
- Watchdog timers
- Fail-safe states
- Error recovery
- Redundant controls

## Integration Ideas

### Smart City Systems
- Connected infrastructure
- Traffic flow optimization
- Emergency vehicle routing
- Public transport priority

### Traffic Monitoring
- Vehicle counting
- Violation detection
- Congestion analysis
- Pattern recognition

### Accessibility Features
- Audio signals for blind
- Extended crossing times
- Vibration feedback
- Mobile app integration

### Environmental Monitoring
- Pollution-based timing
- Weather adaptations
- Energy optimization
- Solar power integration

## Next Steps
- Add vehicle detection sensors
- Implement adaptive timing algorithms
- Create web-based control interface
- Add camera for violation detection
- Integrate with city traffic system
- Implement machine learning for optimization
- Add wireless emergency vehicle detection