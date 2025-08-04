# Magnetic Door Alarm System

Comprehensive door and window monitoring system using magnetic reed switches with intelligent alarm logic, multiple security zones, and detailed activity logging.

## What You'll Learn
- Magnetic reed switch interfacing
- Multi-zone security system design
- Intelligent alarm triggering logic
- Entry/exit delay timing systems
- Event logging and statistics
- Background monitoring threads
- Hardware interrupt handling
- Security system state management

## Hardware Requirements
- Raspberry Pi 5
- 2-4 Magnetic reed switches (door/window sensors)
- 2-4 Magnets for reed switches
- 3x Push buttons for control
- 4x LEDs for status indication (including 2 PWM LEDs)
- 2x Buzzers (alarm and status)
- Optional: PIR motion sensor for enhanced security
- Jumper wires
- Breadboard or perfboard
- Pull-up resistors (10kΩ)
- Current limiting resistors (220Ω for LEDs)

## Circuit Diagram

```
Magnetic Door Alarm System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Door/Window Sensors (Reed Switches):                       │
│ GPIO17 ── Reed Switch 1 (Front Door) ── GND               │
│ GPIO18 ── Reed Switch 2 (Back Door) ── GND                │
│ GPIO27 ── Reed Switch 3 (Side Door) ── GND                │
│ GPIO22 ── Reed Switch 4 (Window) ── GND                   │
│                                                             │
│ Control Buttons:                                            │
│ GPIO23 ── ARM Button ── GND                               │
│ GPIO24 ── MUTE Button ── GND                              │
│ GPIO25 ── TEST Button ── GND                              │
│                                                             │
│ Status LEDs:                                                │
│ GPIO26 ── 220Ω ── ARMED LED ── GND                        │
│ GPIO19 ── 220Ω ── ALARM LED ── GND (PWM)                  │
│ GPIO20 ── 220Ω ── STATUS LED ── GND (PWM)                 │
│ GPIO21 ── 220Ω ── DOOR LED ── GND                         │
│                                                             │
│ Audio Alerts:                                               │
│ GPIO13 ── ALARM Buzzer ── GND                             │
│ GPIO12 ── STATUS Buzzer ── GND                            │
│                                                             │
│ Optional Motion Sensor:                                     │
│ GPIO6 ── PIR Motion Sensor ── 5V/GND                      │
│                                                             │
│ 3.3V ── Pull-up resistors for reed switches               │
│ GND ─── Common ground for all components                   │
└─────────────────────────────────────────────────────────────┘

Reed Switch Installation:
┌─────────────────────────────────────────────────────────────┐
│                     Door Frame                              │
│  ┌─────────────┐              ┌─────────────┐              │
│  │ Reed Switch │◄─── 5mm ────►│   Magnet    │              │
│  │ (on frame)  │              │ (on door)   │              │
│  └─────────────┘              └─────────────┘              │
│         │                           │                      │
│      To GPIO                    Moves with door            │
│                                                             │
│  When door is CLOSED: Reed switch CLOSED (circuit complete)│
│  When door is OPEN:   Reed switch OPEN (circuit broken)   │
└─────────────────────────────────────────────────────────────┘

Wiring Details:
Reed Switch Connection (per sensor):
┌─────────────────┐
│   Reed Switch   │
├─────────────────┤
│ Pin 1 ── GPIO   │  (with 10kΩ pull-up to 3.3V)
│ Pin 2 ── GND    │
└─────────────────┘

Button Connections (with internal pull-up):
ARM Button:     GPIO23 ── Button ── GND
MUTE Button:    GPIO24 ── Button ── GND  
TEST Button:    GPIO25 ── Button ── GND

LED Connections (with 220Ω current limiting):
ARMED LED:    GPIO26 ── 220Ω ── LED ── GND
ALARM LED:    GPIO19 ── 220Ω ── LED ── GND (PWM capable)
STATUS LED:   GPIO20 ── 220Ω ── LED ── GND (PWM capable)
DOOR LED:     GPIO21 ── 220Ω ── LED ── GND

Note: Reed switches are normally closed when magnet is near
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and hardware control
pip install gpiozero

# Optional: pigpio for precise timing (recommended)
sudo apt install pigpio python3-pigpio
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

## Running the Program

```bash
cd examples/08-extension-projects/03-door-alarm
python magnetic-door-alarm.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Interactive demonstration
make security # Security monitoring mode
make test     # Test all components
make setup    # Install dependencies
```

## Code Walkthrough

### Reed Switch Detection
Initialize door sensors with proper debouncing:
```python
def __init__(self):
    for config in self.door_configs:
        if config['enabled']:
            # Reed switch is normally closed, open when door opens
            sensor = Button(config['pin'], pull_up=True, bounce_time=0.1)
            
            # Setup event callbacks
            sensor.when_pressed = lambda door=config['name']: self._on_door_opened(door)
            sensor.when_released = lambda door=config['name']: self._on_door_closed(door)
```

### Intelligent Alarm Logic
Multi-zone security with different response priorities:
```python
def _handle_armed_door_opening(self, door_name, door_state):
    priority = door_state['config']['priority']
    
    if priority == 'high':          # Entry doors
        if self.entry_delay > 0:
            self.entry_timer = threading.Timer(self.entry_delay, self._trigger_alarm)
            self.entry_timer.start()
        else:
            self._trigger_alarm()
    
    elif priority == 'medium':      # Secondary doors
        delay = self.entry_delay * 1.5
        self.entry_timer = threading.Timer(delay, self._trigger_alarm)
        self.entry_timer.start()
    
    elif priority == 'low':         # Windows - immediate alarm
        self._trigger_alarm()
```

### Entry/Exit Delay System
Proper delay management for user convenience:
```python
def _arm_system(self):
    # Check for open doors before arming
    open_doors = [name for name, state in self.door_states.items() if state['is_open']]
    
    if open_doors:
        print(f"⚠ Cannot arm - doors open: {', '.join(open_doors)}")
        return
    
    # Exit delay countdown
    if self.exit_delay > 0:
        def complete_arming():
            self.is_armed = True
            print("🛡️ System ARMED")
        
        self.exit_timer = threading.Timer(self.exit_delay, complete_arming)
        self.exit_timer.start()
```

### Event Logging System
Comprehensive activity tracking:
```python
def _on_door_opened(self, door_name):
    # Log event with full context
    event = {
        'timestamp': datetime.now().isoformat(),
        'door': door_name,
        'action': 'opened',
        'armed': self.is_armed,
        'priority': door_state['config']['priority']
    }
    self.event_log.append(event)
    
    # Update daily statistics
    self._update_daily_stats(door_name, 'opened')
```

### Alarm Pattern Generation
Multi-stage alarm with audio patterns:
```python
def _trigger_alarm(self):
    def alarm_pattern():
        while self.alarm_active and not self.alarm_muted:
            # Pattern: 3 short beeps, 1 long beep, repeat
            self.alarm_buzzer.beep(0.2, 0.1, n=3)
            time.sleep(0.5)
            self.alarm_buzzer.beep(1.0, 0.5, n=1)
            time.sleep(1.0)
    
    alarm_thread = threading.Thread(target=alarm_pattern, daemon=True)
    alarm_thread.start()
```

## Security Zones and Priorities

### High Priority (Entry Doors)
- Front door, main entrance
- **Response**: Entry delay before alarm
- **Typical Delay**: 10-30 seconds
- **Use Case**: Allow legitimate entry

### Medium Priority (Secondary Doors)
- Back door, side entrances
- **Response**: Extended entry delay
- **Typical Delay**: 15-45 seconds
- **Use Case**: Secondary access points

### Low Priority (Windows/Emergency)
- Windows, emergency exits
- **Response**: Immediate alarm
- **Typical Delay**: None
- **Use Case**: Unexpected breach points

## System States

### Disarmed Mode
- Door monitoring active (logging only)
- No alarms triggered
- Status LED breathing pattern
- All doors can open freely

### Arming Mode
- Exit delay countdown active
- Warning beeps during countdown
- Cannot be triggered during exit delay
- Automatically cancels if door opens

### Armed Mode
- Full security monitoring active
- Entry delays active for high/medium priority
- Status LED solid on
- Ready to trigger alarms

### Alarm Mode
- Audio and visual alarms active
- Continuous until manually stopped
- Auto-stop after maximum duration
- Logs all trigger events

## Advanced Features

### Intelligent False Positive Prevention
- Bounce time filtering for mechanical switches
- Multiple trigger threshold options
- Time-based sensitivity adjustment
- Pattern learning for common false alarms

### Automatic System Management
- Auto-rearm after all doors close
- Scheduled arming/disarming
- Battery level monitoring (future)
- Remote monitoring capability (future)

### Comprehensive Statistics
- Daily door usage patterns
- Total open time tracking
- Alarm frequency analysis
- System uptime monitoring

## Available Demos

1. **Interactive Monitoring**: Real-time door status display
2. **Security System Demo**: Full armed system simulation
3. **Component Testing**: Verify all hardware connections

## Troubleshooting

### Reed switches not responding
- Check magnet alignment (within 5mm)
- Verify pull-up resistor connections
- Test switch continuity with multimeter
- Ensure magnet strength is adequate
- Check for loose connections

### False alarms occurring
- Adjust bounce time in software
- Improve magnet mounting stability
- Check for vibration sources
- Increase entry delay times
- Enable intelligent filtering

### Buzzer not working
- Check buzzer polarity
- Verify GPIO pin assignments
- Test with multimeter for continuity
- Ensure adequate power supply
- Check for hardware conflicts

### LEDs not illuminating
- Verify current limiting resistors
- Check LED polarity (anode to GPIO)
- Test GPIO output with multimeter
- Ensure common ground connections
- Check for blown LEDs

## Advanced Usage

### Multiple Door Configuration
Configure different door types and priorities:
```python
door_configs = [
    {'name': 'Front Door', 'pin': 17, 'priority': 'high', 'entry_delay': 15},
    {'name': 'Back Door', 'pin': 18, 'priority': 'high', 'entry_delay': 20},
    {'name': 'Garage Door', 'pin': 27, 'priority': 'medium', 'entry_delay': 30},
    {'name': 'Window', 'pin': 22, 'priority': 'low', 'entry_delay': 0}
]
```

### Time-Based Automation
Different behavior for different times:
```python
def get_time_based_settings(self):
    current_hour = datetime.now().hour
    
    if 22 <= current_hour or current_hour <= 6:  # Night mode
        return {
            'entry_delay': 5,    # Shorter delay at night
            'sensitivity': 'high',
            'auto_arm': True
        }
    else:  # Day mode
        return {
            'entry_delay': 15,
            'sensitivity': 'medium', 
            'auto_arm': False
        }
```

### Remote Notifications
Send alerts to mobile devices:
```python
import smtplib
from email.mime.text import MIMEText

def send_alarm_notification(self, door_name):
    message = f"SECURITY ALERT: {door_name} opened while system armed"
    
    msg = MIMEText(message)
    msg['Subject'] = 'Home Security Alert'
    msg['From'] = 'alarm@yourhome.com'
    msg['To'] = 'your@email.com'
    
    # Send via SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('username', 'password')
        server.send_message(msg)
```

### Data Analytics
Analyze usage patterns:
```python
def analyze_door_patterns(self):
    # Group events by hour of day
    hourly_activity = {}
    for event in self.event_log:
        hour = datetime.fromisoformat(event['timestamp']).hour
        hourly_activity[hour] = hourly_activity.get(hour, 0) + 1
    
    # Find peak usage times
    peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
    return peak_hours[:5]  # Top 5 busy hours
```

### Integration with Home Automation
Connect to home automation systems:
```python
import requests

def notify_home_automation(self, event_type, door_name):
    # Home Assistant webhook example
    webhook_url = "http://homeassistant.local:8123/api/webhook/door_alarm"
    
    payload = {
        'event': event_type,
        'door': door_name,
        'timestamp': datetime.now().isoformat(),
        'armed': self.is_armed
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"✓ Home automation notified: {event_type}")
    except Exception as e:
        print(f"Home automation notification failed: {e}")
```

## Performance Optimization

### Hardware Considerations
- Use quality reed switches for reliability
- Ensure stable power supply for consistent operation
- Implement proper EMI filtering for industrial environments
- Use shielded cables for long sensor runs

### Software Optimization
- Implement efficient event logging with rotation
- Use hardware interrupts for precise timing
- Optimize thread usage for background monitoring
- Implement graceful degradation for hardware failures

### Power Management
- Implement low-power modes during inactive periods
- Use wake-on-interrupt for battery operation
- Monitor and report battery levels
- Optimize LED brightness for power saving

## Integration Ideas

### Smart Home Integration
- Connect to smart locks for automatic locking
- Integration with security cameras for visual verification
- Automated lighting control on door events
- HVAC system integration for energy savings

### Professional Security
- Connection to professional monitoring services
- Dual-path communication (cellular backup)
- Tamper detection for sensors
- Battery backup with low-battery alerts

### Access Control
- RFID card reader integration
- Keypad entry with user codes
- Smartphone app for remote control
- Guest access with time limitations

## Next Steps
- Add cellular connectivity for remote monitoring
- Implement machine learning for pattern recognition
- Create mobile app for system control
- Add camera integration for visual verification
- Develop professional monitoring interface
- Integrate with existing security systems
- Add GPS tracking for portable applications