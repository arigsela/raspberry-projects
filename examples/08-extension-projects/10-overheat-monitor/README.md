# Overheat Monitoring System

Multi-zone temperature monitoring system with intelligent alerts, automatic cooling control, predictive analysis, and comprehensive data logging for equipment protection.

## What You'll Learn
- Multi-zone temperature monitoring
- Thermistor-based temperature sensing
- Alert level management
- Automatic cooling control strategies
- Temperature trend analysis
- Predictive overheat detection
- Data logging and statistics
- Multi-threaded monitoring systems

## Hardware Requirements
- Raspberry Pi 5
- 4x 10K NTC thermistors for temperature sensing
- ADC0834 analog-to-digital converter
- 4x LEDs for status indicators (Normal, Warning, Critical, Alarm)
- 4x LEDs for zone indicators
- 2x PWM fans for cooling
- 1x Water pump relay (optional)
- Buzzer for alarms
- 3x Push buttons (Reset, Mode, Silence)
- 16x2 LCD display with I2C backpack
- 4x 10kΩ resistors (for thermistor dividers)
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- Jumper wires and breadboard

## Circuit Diagram

```
Overheat Monitoring System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Temperature Sensors (via ADC0834):                          │
│ ADC CS ────── GPIO5                                        │
│ ADC CLK ───── GPIO6                                        │
│ ADC DI ────── GPIO16                                       │
│ ADC DO ────── GPIO12                                       │
│ ADC CH0 ───── Zone 1 thermistor (CPU/Main)                │
│ ADC CH1 ───── Zone 2 thermistor (Ambient)                 │
│ ADC CH2 ───── Zone 3 thermistor (Power)                   │
│ ADC CH3 ───── Zone 4 thermistor (Exhaust)                 │
│                                                             │
│ Status Indicators:                                          │
│ NORMAL LED ─── GPIO17 (Green - Normal temp)               │
│ WARNING LED ── GPIO27 (Yellow - Warning level)             │
│ CRITICAL LED ─ GPIO22 (Red - Critical temp)               │
│ ALARM LED ──── GPIO23 (Red PWM - Overheat alarm)          │
│                                                             │
│ Zone Indicators:                                            │
│ ZONE1 LED ──── GPIO24 (CPU/Main zone)                     │
│ ZONE2 LED ──── GPIO25 (Ambient zone)                      │
│ ZONE3 LED ──── GPIO8  (Power zone)                        │
│ ZONE4 LED ──── GPIO7  (Exhaust zone)                      │
│                                                             │
│ Cooling Control:                                            │
│ FAN1 PWM ───── GPIO18 (Primary cooling)                   │
│ FAN2 PWM ───── GPIO19 (Secondary cooling)                 │
│ PUMP RELAY ─── GPIO26 (Water cooling)                     │
│                                                             │
│ Controls:                                                   │
│ BUZZER ─────── GPIO21 (Alert sounds)                      │
│ RESET BTN ──── GPIO20 (Reset alerts)                      │
│ MODE BTN ───── GPIO13 (Display mode)                      │
│ SILENCE BTN ── GPIO14 (Silence alarm)                     │
│                                                             │
│ LCD Display:                                                │
│ SDA ────────── GPIO2  (I2C Data)                          │
│ SCL ────────── GPIO3  (I2C Clock)                         │
└─────────────────────────────────────────────────────────────┘

Temperature Zones Layout:
┌─────────────────────────────────────────────────────────────┐
│                    MONITORING ZONES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Zone 1: CPU/Main Equipment                                │
│  - Primary heat source                                      │
│  - Most critical monitoring                                 │
│  - Thresholds: Normal<40°C, Warn>60°C, Critical>75°C      │
│                                                             │
│  Zone 2: Ambient Environment                                │
│  - Room/enclosure temperature                               │
│  - Affects overall cooling                                  │
│  - Thresholds: Normal<35°C, Warn>50°C, Critical>65°C      │
│                                                             │
│  Zone 3: Power Supply                                       │
│  - PSU temperature monitoring                               │
│  - Early failure indicator                                  │
│  - Thresholds: Normal<45°C, Warn>65°C, Critical>80°C      │
│                                                             │
│  Zone 4: Exhaust/Output                                     │
│  - Cooling effectiveness indicator                          │
│  - Airflow verification                                     │
│  - Thresholds: Normal<40°C, Warn>55°C, Critical>70°C      │
└─────────────────────────────────────────────────────────────┘

Thermistor Circuit (repeat for each zone):
┌─────────────────────────────────────────────────────────────┐
│     3.3V ──┬── 10kΩ Resistor ──┬── ADC Channel            │
│            │                    │                           │
│            └── 10kΩ Thermistor ─┴── GND                    │
└─────────────────────────────────────────────────────────────┘

Cooling Control Logic:
┌─────────────────────────────────────────────────────────────┐
│ Temp Range  │ Fan1 │ Fan2 │ Pump │ Alert Level            │
├─────────────┼──────┼──────┼──────┼────────────────────────┤
│ < 40°C      │  0%  │  0%  │ OFF  │ Normal                 │
│ 40-60°C     │ 0-50%│  0%  │ OFF  │ Normal-Warning         │
│ 60-75°C     │ 50-80%│ 0-60%│ OFF  │ Warning-Critical       │
│ > 75°C      │ 100% │ 100% │ ON   │ Critical-Overheat      │
└─────────────────────────────────────────────────────────────┘

ADC0834 Connections:
┌─────────────────┐
│     ADC0834     │
├─────────────────┤
│ VCC ── 3.3V     │
│ CS ──  GPIO5    │
│ CLK ── GPIO6    │
│ DI ──  GPIO16   │
│ DO ──  GPIO12   │
│ CH0-3 ─ Sensors │
│ GND ── GND      │
└─────────────────┘
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and hardware control
pip install gpiozero

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/10-overheat-monitor
python overheat-monitoring-system.py
```

Or use the Makefile:
```bash
make          # Run the monitoring system
make demo     # Temperature scenario demo
make test     # Test all components
make cooling  # Test cooling system
make setup    # Install dependencies
```

## Code Walkthrough

### Multi-Zone Temperature Monitoring
Individual zone tracking with history:
```python
class TemperatureZone:
    def update_temperature(self, temp):
        self.current_temp = temp
        self.history.append({
            'temp': temp,
            'time': datetime.now()
        })
        
        # Determine alert level
        if temp >= TEMP_THRESHOLDS['shutdown']:
            self.alert_level = AlertLevel.SHUTDOWN
        elif temp >= TEMP_THRESHOLDS['critical']:
            self.alert_level = AlertLevel.CRITICAL
```

### Temperature Trend Analysis
Predictive monitoring for early warnings:
```python
def get_trend(self):
    # Calculate temperature change rate
    recent = list(self.history)[-30:]
    time_diff = (recent[-1]['time'] - recent[0]['time']).total_seconds()
    
    if time_diff > 0:
        temp_diff = recent[-1]['temp'] - recent[0]['temp']
        return (temp_diff / time_diff) * 60  # °C/minute
```

### Automatic Cooling Control
Intelligent fan and pump management:
```python
def _set_cooling_level(self, level):
    # Primary fan (runs above 20%)
    if self.cooling_level > 20:
        self.fan1.value = self.cooling_level / 100.0
    
    # Secondary fan (runs above 50%)
    if self.cooling_level > 50:
        self.fan2.value = (self.cooling_level - 50) / 50.0
    
    # Water pump (runs above 80%)
    if self.cooling_level > 80:
        self.pump.on()
```

### Alert Level Management
Multi-level alert system:
```python
def _update_system_alert(self, alert_level):
    if alert_level == AlertLevel.NORMAL:
        self.led_normal.on()
        self.alarm_active = False
    elif alert_level == AlertLevel.WARNING:
        self.led_warning.on()
        self.alarm_active = True
    elif alert_level == AlertLevel.CRITICAL:
        self.led_critical.on()
        self.led_alarm.pulse()
        self.alarm_active = True
```

### Predictive Analysis
Early warning for temperature rises:
```python
def _check_temperature_trends(self):
    for zone_name, zone in self.zones.items():
        trend = zone.get_trend()
        
        if trend > self.trend_threshold:
            # Predict future temperature
            predicted_temp = zone.current_temp + (trend * self.prediction_window / 60)
            
            if predicted_temp > TEMP_THRESHOLDS['critical']:
                print(f"⚠️  Rapid rise in {zone.name}: {trend:.1f}°C/min")
```

## Display Modes

### 1. All Zones Mode
Overview of all temperature zones:
- Cycles through zone pairs
- Shows current temperature
- Alert indicators for each zone
- Quick system overview

### 2. Zone Detail Mode
Detailed single zone information:
- Current temperature
- Temperature trend
- Alert status
- Cooling level

### 3. Statistics Mode
System performance metrics:
- Runtime duration
- Total alert count
- Overheat events
- Maximum temperatures

### 4. Trend Mode
Temperature change analysis:
- Fastest changing zone
- Rate of change
- Predictive warnings
- Cooling effectiveness

### 5. Alerts Mode
Active alert summary:
- Number of active alerts
- Highest alert level
- Zone-specific alerts
- System response

## Alert Levels

### Normal (Green)
- All temperatures within safe range
- No cooling required
- System operating optimally

### Warning (Yellow)
- Temperature approaching limits
- Moderate cooling activated
- Increased monitoring frequency

### Critical (Red)
- Temperature at dangerous levels
- Maximum cooling engaged
- Audible alarms active

### Overheat (Flashing Red)
- Temperature exceeds safe limits
- Emergency cooling mode
- Continuous alarms
- Consider shutdown

### Shutdown (Rapid Flash)
- Immediate action required
- System damage imminent
- Maximum cooling insufficient
- Manual intervention needed

## Features

### Intelligent Monitoring
- Multi-zone temperature tracking
- Historical data analysis
- Trend calculation
- Predictive warnings

### Automatic Response
- Progressive cooling control
- Multi-stage fan management
- Emergency pump activation
- Alert escalation

### User Interface
- Multi-mode LCD display
- Zone-specific LEDs
- Alert status indicators
- Control buttons

### Data Management
- Continuous logging
- Statistics tracking
- Alert history
- Performance metrics

## Available Demos

1. **Temperature Demo**: Simulates various temperature scenarios
2. **Cooling Test**: Tests cooling system response
3. **Alert Demo**: Demonstrates alert levels
4. **Trend Analysis**: Shows predictive features

## Troubleshooting

### Incorrect temperature readings
- Check thermistor connections
- Verify voltage divider resistors
- Test ADC with known voltage
- Calibrate thermistor constants
- Check for thermal coupling

### Cooling not activating
- Verify fan power connections
- Check PWM signal output
- Test fans independently
- Verify temperature thresholds
- Check cooling logic

### False alerts
- Adjust temperature thresholds
- Increase averaging samples
- Check for electrical noise
- Verify sensor placement
- Calibrate alert hysteresis

### LCD display issues
- Check I2C address
- Verify I2C connections
- Enable I2C interface
- Test with i2cdetect
- Check pull-up resistors

### Trend calculation errors
- Ensure sufficient history data
- Check timestamp accuracy
- Verify calculation window
- Test with stable temperature

## Advanced Usage

### Custom Temperature Zones
Add application-specific zones:
```python
self.zones['gpu'] = TemperatureZone("GPU", ADC_CHANNEL_4, GPIO_PIN_X)
self.zones['gpu'].thresholds = {
    'warning': 70,
    'critical': 85,
    'shutdown': 95
}
```

### Advanced Cooling Curves
Non-linear cooling response:
```python
def custom_cooling_curve(self, temp):
    # Exponential cooling response
    if temp < 40:
        return 0
    else:
        return min(100, int(math.exp((temp - 40) / 10) * 10))
```

### Network Monitoring
Remote temperature monitoring:
```python
import requests

def send_temperature_data(self):
    data = {
        'device_id': 'overheat_001',
        'zones': {name: zone.current_temp for name, zone in self.zones.items()},
        'alerts': [zone.name for zone in self.zones.values() 
                  if zone.alert_level != AlertLevel.NORMAL],
        'cooling': self.cooling_level
    }
    
    requests.post('http://monitor.example.com/api/temperature', json=data)
```

### Machine Learning Integration
Predictive failure analysis:
```python
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
        self.training_data = []
    
    def detect_anomaly(self, zone_temps):
        # Detect unusual temperature patterns
        prediction = self.model.predict([zone_temps])
        return prediction[0] == -1  # Anomaly detected
```

### Automated Shutdown
Safe system shutdown on overheat:
```python
def emergency_shutdown(self):
    if any(zone.alert_level == AlertLevel.SHUTDOWN 
           for zone in self.zones.values()):
        print("🚨 EMERGENCY SHUTDOWN INITIATED")
        
        # Save system state
        self.save_emergency_log()
        
        # Graceful service shutdown
        os.system("sudo systemctl stop critical-service")
        
        # Maximum cooling
        self._set_cooling_level(100)
        
        # System halt after delay
        os.system("sudo shutdown -h +2")
```

## Performance Optimization

### Sampling Strategies
- Adaptive sampling rates
- Priority-based monitoring
- Event-driven updates
- Efficient data structures

### Thermal Management
- Preemptive cooling
- Thermal mass modeling
- Airflow optimization
- Heat dissipation patterns

### Alert Optimization
- Debouncing algorithms
- Intelligent thresholds
- Context-aware alerts
- Predictive warnings

## Integration Ideas

### Server Room Monitoring
- Rack temperature mapping
- Hot spot detection
- Cooling efficiency
- Failure prediction

### Industrial Equipment
- Motor temperature monitoring
- Bearing failure detection
- Process optimization
- Maintenance scheduling

### 3D Printer Monitoring
- Hot-end temperature
- Bed temperature uniformity
- Chamber temperature
- Thermal runaway protection

### Solar Panel Systems
- Panel temperature monitoring
- Efficiency optimization
- Cooling activation
- Performance tracking

## Next Steps
- Add humidity monitoring for complete environmental control
- Implement PID control for cooling systems
- Create web dashboard for remote monitoring
- Add email/SMS alerts for critical events
- Integrate with building management systems
- Develop mobile app for notifications
- Add thermal imaging camera support