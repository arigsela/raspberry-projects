# Speed Sensor - Rotation Speed Measurement

Measure rotation speed (RPM) using infrared or hall effect sensors to detect pulses from rotating objects.

## What You'll Learn
- Pulse counting for speed measurement
- RPM and frequency calculations
- Interrupt-driven pulse detection
- Speed monitoring and alarm systems
- Data logging and analysis
- Control system feedback
- Statistical analysis of timing data

## Hardware Requirements
- Raspberry Pi 5
- Speed sensor (IR photointerrupter, hall effect sensor, or optical encoder)
- Rotating object with markers/magnets/slots
- Optional: LEDs for visual feedback
- Optional: Buzzer for alarms
- Optional: PWM LED for speed visualization
- Pull-up resistors (if not built into sensor module)
- Jumper wires

## Circuit Diagram

```
IR Photointerrupter Speed Sensor:
┌─────────────────────────┐
│    IR LED    ┌─┐   Photo│  Slotted disc or
│       │      │ │   trans.│  object with holes
│    ───┼──────┼─┼────────│  breaks IR beam
│       │      └─┘        │
├─────────────────────────┤
│ VCC  GND  OUT          │
└──┬────┬────┬───────────┘
   │    │    │
   │    │    └── GPIO17 (Signal)
   │    └─────── GND
   └──────────── 3.3V

Hall Effect Speed Sensor:
┌─────────────────────────┐
│                         │  Magnet on rotating
│    [Hall Sensor]        │  object triggers
│                         │  sensor each pass
├─────────────────────────┤
│ VCC  GND  OUT          │
└──┬────┬────┬───────────┘
   │    │    │
   │    │    └── GPIO17 (Signal)  
   │    └─────── GND
   └──────────── 3.3V

Optional Indicators:
Activity LED:  GPIO23 → 220Ω → LED → GND
PWM LED:       GPIO25 → 220Ω → LED → GND
Buzzer:        GPIO24 → Buzzer → GND
```

## Software Dependencies

Install required libraries:
```bash
pip install gpiozero
```

## Running the Program

```bash
cd examples/06-input-sensors/06-speed-sensor
python speed-sensor.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test basic speed measurement
make tach     # Run visual tachometer
make alarm    # Run speed alarm system
make install  # Install dependencies
```

## Code Walkthrough

### Pulse Detection
Detect pulses using interrupt-driven GPIO events:
```python
def _on_pulse(self):
    """Handle sensor pulse"""
    current_time = time.time()
    
    # Update counters
    self.pulse_count += 1
    self.total_pulses += 1
    
    # Calculate time interval
    if self.last_pulse_time > 0:
        interval = current_time - self.last_pulse_time
        self.pulse_times.append(interval)
```

### Speed Calculation
Convert pulse timing to RPM:
```python
def get_speed(self):
    """Calculate speed in RPM"""
    if len(self.pulse_times) >= 2:
        # Average recent pulse intervals
        avg_interval = statistics.mean(list(self.pulse_times)[-3:])
        
        if avg_interval > 0:
            # Frequency in Hz
            frequency = 1.0 / avg_interval
            
            # Convert to RPM
            rpm = (frequency / self.pulses_per_rev) * 60.0
            return rpm
    
    return 0.0
```

### Calibration System
Determine pulses per revolution:
```python
def calibrate_pulses_per_revolution(self):
    """Manual calibration of pulses per revolution"""
    print("Rotate object exactly one full revolution...")
    start_pulses = self.total_pulses
    
    input("Press Enter when complete...")
    end_pulses = self.total_pulses
    
    self.pulses_per_rev = end_pulses - start_pulses
```

## Key Concepts

### Speed Measurement Principles
- **Pulse counting**: Count events per unit time
- **Period measurement**: Measure time between pulses
- **Frequency calculation**: f = 1 / period
- **RPM conversion**: RPM = (Hz / pulses_per_rev) × 60

### Sensor Types
- **IR photointerrupters**: Optical sensing with slotted discs
- **Hall effect sensors**: Magnetic field detection
- **Optical encoders**: High-resolution position/speed
- **Mechanical switches**: Simple contact-based sensing

### Signal Processing
- **Debouncing**: Handle mechanical bounce
- **Filtering**: Smooth noisy measurements
- **Edge detection**: Rising/falling edge triggering
- **Timeout handling**: Detect stopped rotation

## Available Demos

1. **Basic Speed Measurement**: Real-time RPM display
2. **Visual Tachometer**: LED bar and brightness feedback
3. **Speed Alarm System**: Min/max speed monitoring
4. **RPM Data Logger**: Log measurements to CSV file
5. **Speed Control Simulation**: Closed-loop control demo
6. **Calibration**: Determine pulses per revolution
7. **Frequency Analysis**: Statistical timing analysis

## Troubleshooting

### No pulse detection
- Check sensor power (3.3V, GND)
- Verify signal connection to GPIO
- Test sensor output with multimeter
- Ensure object has detectable features

### Erratic readings
- Add debouncing (increase bounce_time)
- Check for electrical noise
- Ensure consistent trigger spacing
- Verify stable power supply

### Wrong speed readings
- Calibrate pulses per revolution
- Check sensor alignment
- Verify trigger object spacing
- Account for multiple pulses per revolution

### Speed not updating
- Check timeout logic (stopped rotation)
- Verify sensor is detecting all pulses
- Ensure proper edge detection

## Advanced Usage

### Multiple Sensors
Monitor multiple rotating objects:
```python
wheel_sensor = SpeedSensor(17, pulses_per_rev=20)
motor_sensor = SpeedSensor(18, pulses_per_rev=1)

def compare_speeds():
    wheel_speed = wheel_sensor.get_speed()
    motor_speed = motor_sensor.get_speed()
    gear_ratio = motor_speed / wheel_speed if wheel_speed > 0 else 0
    return gear_ratio
```

### Speed Control
Implement closed-loop speed control:
```python
def speed_controller(target_rpm):
    current_rpm = sensor.get_speed()
    error = target_rpm - current_rpm
    
    # PID control
    output = kp * error + ki * integral + kd * derivative
    
    # Apply to motor control
    motor.value = max(0, min(1, output))
```

### Direction Detection
Use quadrature encoding for direction:
```python
class DirectionalSpeedSensor:
    def __init__(self, pin_a, pin_b):
        self.sensor_a = Button(pin_a)
        self.sensor_b = Button(pin_b)
        self.direction = 1  # 1 = forward, -1 = reverse
        
    def detect_direction(self):
        # Quadrature logic
        if self.sensor_a.is_pressed != self.sensor_b.is_pressed:
            self.direction = 1 if self.sensor_a.is_pressed else -1
```

### High-Speed Optimization
Handle high-frequency signals:
```python
# Use hardware interrupts for better timing
import RPi.GPIO as GPIO

def high_speed_counter(pin):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=pulse_handler)
    
    # Minimize processing in interrupt handler
    def pulse_handler(channel):
        global pulse_count, last_time
        pulse_count += 1
        last_time = time.time()
```

## Performance Considerations

### Timing Accuracy
- Use interrupt-driven detection for precision
- Minimize processing in interrupt handlers
- Consider hardware timers for critical applications

### Update Rates
- Balance responsiveness vs. stability
- Use moving averages for smooth readings
- Implement different update rates for display vs. control

### Resource Usage
- Limit history buffer sizes
- Use efficient data structures
- Consider memory usage for long-running applications

## Applications

### Industrial Monitoring
- Motor speed monitoring
- Conveyor belt speed control
- Pump rotation verification
- Fan speed regulation

### Automotive
- Wheel speed sensors (ABS)
- Engine RPM monitoring
- Transmission speed sensing
- Turbocharger speed measurement

### Robotics
- Wheel odometry
- Motor feedback control
- Servo position verification
- Gear ratio monitoring

## Next Steps
- Build a complete speed control system
- Implement advanced filtering algorithms
- Create a multi-sensor monitoring dashboard
- Add wireless data transmission
- Develop predictive maintenance algorithms