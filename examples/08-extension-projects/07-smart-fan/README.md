# Temperature-Controlled Smart Fan

Intelligent fan control system with automatic speed adjustment based on temperature, multiple operating modes, and comprehensive monitoring capabilities.

## What You'll Learn
- Temperature sensing with thermistors
- PWM fan speed control
- Fan RPM measurement with tachometer
- Temperature-based control algorithms
- Multiple operating mode implementation
- Energy-efficient cooling strategies
- Real-time monitoring and statistics
- Scheduled temperature control

## Hardware Requirements
- Raspberry Pi 5
- 10K NTC thermistor for temperature sensing
- ADC0834 analog-to-digital converter
- 4-wire PWM computer fan (with tachometer)
- 16x2 LCD display with I2C backpack
- 4x Status LEDs (Cool, Normal, Warm, Hot)
- 4x Push buttons for control
- 10kΩ potentiometer for manual setpoint
- Buzzer for alerts
- 10kΩ resistor (for thermistor voltage divider)
- Jumper wires and breadboard
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- External 12V power supply for fan

## Circuit Diagram

```
Temperature-Controlled Smart Fan System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Temperature Sensing (via ADC0834):                          │
│ ADC CS ────── GPIO5                                        │
│ ADC CLK ───── GPIO6                                        │
│ ADC DI ────── GPIO16                                       │
│ ADC DO ────── GPIO12                                       │
│ ADC CH0 ───── Thermistor circuit                          │
│ ADC CH1 ───── Setpoint potentiometer                      │
│                                                             │
│ Fan Control:                                                │
│ FAN PWM ───── GPIO18 (PWM control)                        │
│ FAN TACH ──── GPIO17 (RPM feedback)                       │
│ FAN ENABLE ── GPIO27 (On/Off control)                     │
│                                                             │
│ Status LEDs:                                                │
│ COOL LED ──── GPIO22 (Blue - Below 20°C)                  │
│ NORMAL LED ── GPIO23 (Green - 20-25°C)                    │
│ WARM LED ──── GPIO24 (Yellow - 25-30°C)                   │
│ HOT LED ───── GPIO25 (Red - Above 30°C, PWM)              │
│                                                             │
│ Control Buttons:                                            │
│ MODE BTN ──── GPIO19 (Cycle operating modes)              │
│ UP BTN ────── GPIO20 (Increase target temp)               │
│ DOWN BTN ──── GPIO21 (Decrease target temp)               │
│ POWER BTN ─── GPIO26 (Fan on/off)                         │
│                                                             │
│ Alert Buzzer: GPIO13                                        │
│                                                             │
│ I2C LCD Display:                                           │
│ SDA ────────── GPIO2                                       │
│ SCL ────────── GPIO3                                       │
└─────────────────────────────────────────────────────────────┘

Temperature Sensing Circuit:
┌─────────────────────────────────────────────────────────────┐
│                   Thermistor Circuit                        │
│                                                             │
│     3.3V ──┬── 10kΩ Resistor ──┬── ADC CH0                │
│            │                    │                           │
│            └── 10kΩ Thermistor ─┴── GND                    │
│                                                             │
│  Voltage divider creates variable voltage based on temp    │
└─────────────────────────────────────────────────────────────┘

Fan Connection (4-wire PWM Fan):
┌─────────────────┐
│   4-Wire Fan    │
├─────────────────┤
│ Red   ── +12V   │  (External power supply)
│ Black ── GND    │  (Common ground with Pi)
│ Yellow── GPIO17 │  (Tachometer signal)
│ Blue  ── GPIO18 │  (PWM control)
└─────────────────┘

Operating Modes and Fan Curves:
┌─────────────────────────────────────────────────────────────┐
│                    FAN SPEED CURVES                         │
├─────────────────────────────────────────────────────────────┤
│ 100%│         TURBO    ╱─────                             │
│     │              ╱─────                                   │
│  80%│         ╱────  AUTO                                  │
│     │     ╱────  ╱────                                      │
│  60%│ ╱────  ╱────     ECO                                 │
│     │    ╱────    ╱────                                     │
│  40%│╱────   ╱────      SILENT                             │
│     │   ╱────        ╱────                                  │
│  20%│────        ╱────    ╱────                            │
│     │       ╱────    ╱────                                  │
│   0%└────────────────────────────────────────────→         │
│     Target-5  Target  Target+5  Target+10     Temperature  │
└─────────────────────────────────────────────────────────────┘

ADC0834 Connections:
┌─────────────────┐    ┌─────────────────┐
│     ADC0834     │    │  10kΩ Pot       │
├─────────────────┤    ├─────────────────┤
│ VCC ── 3.3V     │    │ Pin 1 ── 3.3V   │
│ CS ──  GPIO5    │    │ Pin 2 ── ADC CH1│
│ CLK ── GPIO6    │    │ Pin 3 ── GND    │
│ DI ──  GPIO16   │    └─────────────────┘
│ DO ──  GPIO12   │    (Manual setpoint)
│ CH0 ── Thermistor│
│ CH1 ── Pot Pin2 │
│ GND ── GND      │
└─────────────────┘

LED Connections (with 220Ω resistors):
COOL:   GPIO22 ── 220Ω ── LED ── GND (Blue)
NORMAL: GPIO23 ── 220Ω ── LED ── GND (Green)
WARM:   GPIO24 ── 220Ω ── LED ── GND (Yellow)
HOT:    GPIO25 ── 220Ω ── LED ── GND (Red, PWM)

Button Connections (with internal pull-up):
MODE:   GPIO19 ── Button ── GND
UP:     GPIO20 ── Button ── GND
DOWN:   GPIO21 ── Button ── GND
POWER:  GPIO26 ── Button ── GND
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and hardware control
pip install gpiozero RPi.GPIO

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/07-smart-fan
python temperature-controlled-fan.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Temperature simulation
make test     # Test all components
make modes    # Test operating modes
make setup    # Install dependencies
```

## Code Walkthrough

### Temperature Sensing with Thermistor
Convert ADC reading to temperature using Steinhart-Hart equation:
```python
def _adc_to_temperature(self, adc_value):
    # Convert ADC to resistance
    resistance = SERIES_RESISTOR / (255.0 / adc_value - 1.0)
    
    # Steinhart-Hart equation
    steinhart = resistance / THERMISTOR_NOMINAL
    steinhart = math.log(steinhart)
    steinhart /= B_COEFFICIENT
    steinhart += 1.0 / (TEMP_NOMINAL + 273.15)
    steinhart = 1.0 / steinhart
    steinhart -= 273.15  # Convert to Celsius
    
    return steinhart
```

### PWM Fan Control
Smooth fan speed control with minimum threshold:
```python
def _set_fan_speed(self, speed):
    # Apply minimum speed threshold
    if 0 < speed < self.min_fan_speed:
        speed = self.min_fan_speed
    
    # Smooth speed changes
    if abs(speed - self.fan_speed) > 5:
        step = 5 if speed > self.fan_speed else -5
        new_speed = self.fan_speed + step
    else:
        new_speed = speed
    
    # Set PWM duty cycle
    if self.fan_speed > 0:
        self.fan_enable.on()
        self.fan_pwm.value = self.fan_speed / 100.0
```

### RPM Measurement
Fan speed monitoring using tachometer:
```python
def _rpm_monitoring_loop(self):
    while self.monitoring_active:
        # Count pulses over 1 second
        self.rpm_pulses = 0
        time.sleep(1)
        
        # Calculate RPM (2 pulses per revolution)
        self.fan_rpm = (self.rpm_pulses * 60) // 2
```

### Automatic Fan Curve
Temperature-based speed control:
```python
def _auto_fan_curve(self, temp):
    if temp < self.target_temp - self.hysteresis:
        return FAN_OFF
    elif temp < self.target_temp:
        # Proportional control near target
        ratio = (temp - (self.target_temp - self.hysteresis)) / self.hysteresis
        return FAN_LOW * ratio
    elif temp < self.target_temp + 5:
        # Linear increase above target
        ratio = (temp - self.target_temp) / 5
        return FAN_LOW + (FAN_MEDIUM - FAN_LOW) * ratio
```

### LED Temperature Indicators
Visual temperature feedback:
```python
def _update_led_indicators(self, temp):
    self._all_leds_off()
    
    if temp < TEMP_COOL:        # < 20°C
        self.led_cool.on()
    elif temp < TEMP_NORMAL:    # 20-25°C
        self.led_normal.on()
    elif temp < TEMP_WARM:      # 25-30°C
        self.led_warm.on()
    else:                       # > 30°C
        self.led_hot.pulse()
```

## Operating Modes

### 1. Auto Mode
Balanced cooling with proportional control:
- Gradual speed increase based on temperature
- Hysteresis prevents oscillation
- Full range from off to maximum speed
- Optimal for general use

### 2. Manual Mode
Direct user control:
- Set target temperature with buttons/potentiometer
- Simple on/off control at target
- No automatic adjustment
- Good for consistent environments

### 3. Eco Mode
Energy-saving operation:
- Higher temperature tolerance
- Limited maximum speed (80%)
- Slower response to temperature changes
- Reduces power consumption by ~30%

### 4. Turbo Mode
Maximum cooling performance:
- Aggressive cooling curve
- Starts at medium speed
- Quickly ramps to maximum
- For rapid temperature reduction

### 5. Silent Mode
Quiet operation:
- Limited to 60% maximum speed
- Higher temperature threshold
- Prioritizes noise reduction
- Ideal for bedrooms/offices

### 6. Schedule Mode
Time-based temperature control:
- Different targets throughout the day
- Automatic adjustment based on time
- Energy efficient scheduling
- Customizable time slots

## Features

### Temperature Monitoring
- Real-time temperature sensing
- Historical data tracking
- Min/max/average statistics
- Temperature trend analysis

### Fan Control
- PWM speed control (0-100%)
- RPM monitoring with tachometer
- Smooth speed transitions
- Minimum speed threshold

### User Interface
- LCD display with rotating views
- LED temperature indicators
- Button controls for all functions
- Audible feedback for actions

### Energy Management
- Eco mode for power saving
- Runtime statistics
- Energy usage estimation
- Scheduled operation

## Available Demos

1. **Temperature Demo**: Simulate various temperatures
2. **Mode Test**: Compare all operating modes
3. **Fan Curve Test**: Visualize speed curves
4. **Schedule Demo**: Test scheduled operation

## Troubleshooting

### Incorrect temperature readings
- Check thermistor connections
- Verify series resistor value (10kΩ)
- Test ADC with known voltage
- Calibrate thermistor constants
- Shield from heat sources

### Fan not spinning
- Check 12V power supply
- Verify PWM signal with multimeter
- Test fan with direct 12V
- Check enable pin state
- Minimum speed may be too low

### No RPM reading
- Verify tachometer wire (usually yellow)
- Check pull-up on tach pin
- Test with oscilloscope
- Some fans need 5V pull-up
- Count pulses per revolution

### LCD display issues
- Verify I2C address (0x27 or 0x3F)
- Check I2C connections
- Enable I2C in raspi-config
- Test with i2cdetect -y 1

### Erratic fan behavior
- Increase speed smoothing
- Check for power supply noise
- Add capacitor on fan power
- Increase hysteresis value

## Advanced Usage

### Custom Fan Curves
Create application-specific curves:
```python
def custom_server_curve(self, temp):
    """Aggressive cooling for server room"""
    if temp < 20:
        return FAN_LOW
    elif temp < 25:
        return FAN_MEDIUM
    else:
        # Rapid increase above 25°C
        return min(FAN_MAX, FAN_MEDIUM + (temp - 25) * 10)
```

### Multi-Zone Control
Control multiple fans for different zones:
```python
class MultiZoneFanControl:
    def __init__(self):
        self.zones = {
            'cpu': {'fan_pin': 18, 'temp_channel': 0},
            'ambient': {'fan_pin': 19, 'temp_channel': 1},
            'exhaust': {'fan_pin': 20, 'temp_channel': 2}
        }
```

### PID Control Implementation
Advanced control algorithm:
```python
class PIDFanController:
    def __init__(self, kp=2.0, ki=0.5, kd=0.1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.last_error = 0
    
    def calculate(self, setpoint, current):
        error = current - setpoint
        self.integral += error
        derivative = error - self.last_error
        
        output = (self.kp * error + 
                 self.ki * self.integral + 
                 self.kd * derivative)
        
        self.last_error = error
        return max(0, min(100, output))
```

### Network Monitoring
Remote temperature monitoring:
```python
import flask

app = flask.Flask(__name__)

@app.route('/api/temperature')
def get_temperature():
    return {
        'current': fan.current_temp,
        'target': fan.target_temp,
        'fan_speed': fan.fan_speed,
        'mode': fan.mode.value,
        'timestamp': datetime.now().isoformat()
    }
```

### Data Logging
Long-term temperature logging:
```python
def log_temperature_data(self):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'temperature': self.current_temp,
        'target': self.target_temp,
        'fan_speed': self.fan_speed,
        'fan_rpm': self.fan_rpm,
        'mode': self.mode.value
    }
    
    with open('temperature_log.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        writer.writerow(log_entry)
```

## Performance Optimization

### Temperature Sampling
- Use median filtering for stability
- Adjust sampling rate based on thermal mass
- Implement change detection
- Cache readings when stable

### Fan Control
- Minimize PWM frequency changes
- Use lookup tables for curves
- Implement deadband control
- Optimize speed ramping

### Power Efficiency
- Sleep between readings
- Reduce LCD updates when stable
- Dim LEDs in low light
- Disable unused features

## Integration Ideas

### Home Automation
- MQTT integration for Home Assistant
- Voice control with Alexa/Google
- Smartphone app control
- Integration with HVAC systems

### Server Room Monitoring
- Multiple zone control
- Alert system for overheating
- Redundant fan control
- Remote monitoring dashboard

### Greenhouse Control
- Humidity compensation
- Day/night scheduling
- Multiple sensor integration
- Plant-specific profiles

### 3D Printer Enclosure
- Precise temperature control
- Material-specific profiles
- Cool-down scheduling
- Safety shutdown features

## Next Steps
- Add humidity sensing and control
- Implement multiple temperature zones
- Create web-based control interface
- Add predictive temperature control
- Integrate with weather API for optimization
- Develop mobile app for remote control
- Add air quality monitoring