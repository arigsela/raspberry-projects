# Project 04-01: DC Motor - Speed and Direction Control

Control DC motors with variable speed and direction using the L293D motor driver IC for robotics, automation, and motion projects.

## What You'll Learn

- DC motor principles and operation
- H-bridge motor drivers (L293D)
- PWM speed control
- Direction control
- Motor driver protection
- Power supply considerations

## Hardware Requirements

- Raspberry Pi 5
- 1x L293D motor driver IC
- 1-2x DC motors (3-12V)
- External power supply for motors
- Optional: Push buttons for control
- Optional: Potentiometer for speed control
- Optional: MCP3008 ADC
- Jumper wires
- Breadboard

## Understanding DC Motors

### Motor Basics
- **DC Motor**: Converts electrical energy to mechanical rotation
- **Speed**: Proportional to applied voltage
- **Direction**: Determined by voltage polarity
- **Current**: Increases with load (torque)

### Motor Specifications
| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Voltage | Operating voltage | 3V, 6V, 12V |
| Current | No-load current | 50-200mA |
| Stall Current | Maximum current | 500mA-2A |
| RPM | Rotations per minute | 100-10,000 |
| Torque | Rotational force | 10-100 g·cm |

## L293D Motor Driver

### IC Overview
```
L293D Pinout (16-pin DIP):
        ┌─────◡─────┐
Enable1 │1        16│ VCC1 (+5V logic)
     A1 │2        15│ A4
     Y1 │3        14│ Y4
    GND │4        13│ GND
    GND │5        12│ GND
     Y2 │6        11│ Y3
     A2 │7        10│ A3
   VCC2 │8         9│ Enable2
        └───────────┘

A = Input, Y = Output to motor
VCC1 = Logic supply (5V)
VCC2 = Motor supply (up to 36V)
```

### Truth Table
| Enable | IN1 | IN2 | Motor Action |
|--------|-----|-----|--------------|
| 0 | X | X | Stop (coast) |
| 1 | 0 | 0 | Brake |
| 1 | 0 | 1 | Reverse |
| 1 | 1 | 0 | Forward |
| 1 | 1 | 1 | Brake |

## Circuit Diagram

```
L293D Motor Driver Connection:

                        L293D
                    ┌─────────────┐
    GPIO17 ────────►│1  Enable1 16│◄──── 5V (Logic)
    GPIO27 ────────►│2  IN1     15│────► Motor 2 IN2 ◄── GPIO25
    Motor 1 (−) ◄───│3  OUT1    14│───► Motor 2 (−)
    GND ───────────►│4  GND     13│◄──── GND
    GND ───────────►│5  GND     12│◄──── GND
    Motor 1 (+) ◄───│6  OUT2    11│───► Motor 2 (+)
    GPIO22 ────────►│7  IN2     10│────► Motor 2 IN1 ◄── GPIO24
    Motor VCC ─────►│8  VCC2     9│◄──── Enable2 ◄── GPIO23
                    └─────────────┘

Motor Connection:
    Motor 1: Between OUT1 (pin 3) and OUT2 (pin 6)
    Motor 2: Between OUT3 (pin 11) and OUT4 (pin 14)

Power Supply:
    VCC1 (pin 16): 5V from Raspberry Pi
    VCC2 (pin 8): External motor supply (6-12V)
    
    ⚠️ IMPORTANT: Connect all GND pins together!

Optional Controls:
    Buttons: GPIO5, GPIO6 with pull-up resistors
    Potentiometer: Via MCP3008 ADC
```

## Pin Connections

### Motor A (Primary)
| L293D Pin | Connection | Purpose |
|-----------|------------|---------|
| Enable1 (1) | GPIO17 | Speed control (PWM) |
| IN1 (2) | GPIO27 | Direction control |
| IN2 (7) | GPIO22 | Direction control |
| OUT1 (3) | Motor (-) | Motor terminal |
| OUT2 (6) | Motor (+) | Motor terminal |

### Motor B (Secondary)
| L293D Pin | Connection | Purpose |
|-----------|------------|---------|
| Enable2 (9) | GPIO23 | Speed control (PWM) |
| IN3 (10) | GPIO24 | Direction control |
| IN4 (15) | GPIO25 | Direction control |
| OUT3 (11) | Motor (-) | Motor terminal |
| OUT4 (14) | Motor (+) | Motor terminal |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero
sudo apt install -y python3-gpiozero

# For potentiometer control (optional)
sudo apt install -y python3-spidev
```

## Running the Examples

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/04-output-drivers/01-motor

# Run the motor control examples
python3 motor-control.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Motor Control

1. **Motor Initialization**
   ```python
   from gpiozero import Motor
   
   motor = Motor(forward=27, backward=22, enable=17)
   ```

2. **Direction Control**
   ```python
   motor.forward()   # Forward rotation
   motor.backward()  # Reverse rotation
   motor.stop()      # Stop motor
   ```

3. **Speed Control**
   ```python
   motor.forward(0.5)  # Forward at 50% speed
   motor.backward(0.7) # Reverse at 70% speed
   ```

### PWM Speed Control
```python
# PWM controls average voltage
# Duty Cycle = Speed percentage
# 0% = Stop, 100% = Full speed

for speed in range(0, 101, 10):
    motor.forward(speed / 100)
    time.sleep(0.5)
```

## Key Concepts

### H-Bridge Operation
```
Forward:                 Reverse:
  VCC ──┬── VCC           VCC ──┬── VCC
        │                        │
      ┌─┴─┐                    ┌─┴─┐
   ON │ S1│ OFF            OFF │ S1│ ON
      └─┬─┘                    └─┬─┘
        │                        │
        M  Motor                 M  Motor
        │                        │
      ┌─┴─┐                    ┌─┴─┐
  OFF │ S2│ ON              ON │ S2│ OFF
      └─┬─┘                    └─┬─┘
        │                        │
       GND                      GND

Current flows left→right    Current flows right→left
```

### PWM Speed Control
```
100% Speed (Always ON):
████████████████████████

50% Speed (50% duty cycle):
████    ████    ████    

25% Speed (25% duty cycle):
██      ██      ██      
```

### Power Calculations
- **Motor Power**: P = V × I
- **PWM Average Voltage**: V_avg = V_supply × duty_cycle
- **Speed**: RPM ≈ k × V_avg (k = motor constant)

## Common Applications

### 1. Robotics
- Wheeled robots
- Robot arms
- Line followers
- Maze solvers

### 2. Automation
- Conveyor belts
- Door openers
- Window blinds
- Pet feeders

### 3. Vehicles
- RC cars
- Drones
- Boats
- Model trains

### 4. Tools
- Drills
- Fans
- Pumps
- Mixers

### 5. Camera Control
- Pan/tilt mechanisms
- Sliders
- Focus pullers
- Gimbals

## Motor Control Techniques

### Smooth Acceleration
```python
def smooth_accelerate(motor, target_speed, duration):
    steps = 50
    current_speed = 0
    
    for i in range(steps):
        speed = current_speed + (target_speed - current_speed) * i / steps
        motor.forward(speed)
        time.sleep(duration / steps)
```

### Position Control (Open Loop)
```python
def rotate_degrees(motor, degrees, rpm=60):
    # Approximate timing
    seconds_per_rotation = 60 / rpm
    duration = (degrees / 360) * seconds_per_rotation
    
    motor.forward(1.0)
    time.sleep(duration)
    motor.stop()
```

### Current Limiting
```python
class CurrentLimitedMotor:
    def __init__(self, motor, max_duty_cycle=0.8):
        self.motor = motor
        self.max_duty = max_duty_cycle
    
    def forward(self, speed):
        limited_speed = min(speed, self.max_duty)
        self.motor.forward(limited_speed)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Motor doesn't run | Check power supply, verify connections |
| Motor runs slowly | Increase voltage, check load |
| Motor gets hot | Reduce load, add cooling, check voltage |
| Direction wrong | Swap motor wires or IN1/IN2 logic |
| Erratic behavior | Add capacitors, check ground connections |

## Advanced Techniques

### Feedback Control
```python
# Using encoder for closed-loop control
class MotorWithEncoder:
    def __init__(self, motor, encoder_pin):
        self.motor = motor
        self.encoder = Button(encoder_pin)
        self.pulse_count = 0
        self.encoder.when_pressed = self._count_pulse
    
    def _count_pulse(self):
        self.pulse_count += 1
    
    def rotate_pulses(self, target_pulses, speed=0.5):
        self.pulse_count = 0
        self.motor.forward(speed)
        
        while self.pulse_count < target_pulses:
            time.sleep(0.01)
        
        self.motor.stop()
```

### Current Monitoring
```python
# Using ACS712 current sensor
def monitor_current(adc_channel):
    # Read current sensor
    voltage = adc_channel.value * 3.3
    # Convert to current (sensor specific)
    current = (voltage - 2.5) / 0.185  # For 5A version
    return abs(current)
```

### Regenerative Braking
```python
def regenerative_brake(motor, duration=0.5):
    # Short motor terminals (both inputs same)
    # Energy returns to power supply
    motor._enable.off()
    motor._forward.on()
    motor._backward.on()
    time.sleep(duration)
    motor.stop()
```

## Safety Considerations

### Protection Features
1. **Flyback Diodes**: Built into L293D
2. **Thermal Shutdown**: Automatic at 150°C
3. **Current Limiting**: 600mA continuous per channel
4. **Voltage Clamping**: Internal protection

### Best Practices
- Use separate power supply for motors
- Add heat sink for high current
- Include emergency stop button
- Implement soft start/stop
- Monitor motor temperature

### Power Supply Selection
```
Motor Current = Stall Current × Safety Factor
Power Supply = Motor Voltage × Total Current × 1.5

Example: 2 motors, 6V, 500mA stall each
Supply needed: 6V × (2 × 0.5A) × 1.5 = 9W minimum
```

## Performance Optimization

### Reduce Power Loss
- Use adequate wire gauge
- Minimize connection resistance
- Keep leads short
- Use proper connectors

### Improve Efficiency
```python
# Adjust PWM frequency for motor type
# Higher frequency = smoother but more losses
motor.frequency = 1000  # 1kHz typical
```

### Multi-Motor Synchronization
```python
def sync_motors(motor1, motor2, speed):
    # Start motors simultaneously
    motor1.forward(speed)
    motor2.forward(speed)
    
    # Fine-tune if encoders available
    # Adjust speeds to match RPM
```

## Project Ideas

1. **Line Following Robot**
   - Two motors for differential drive
   - IR sensors for line detection
   - PID control for smooth following

2. **Pan-Tilt Camera Mount**
   - Two motors for axes
   - Joystick control
   - Position presets

3. **Automated Blinds**
   - Motor with limit switches
   - Light sensor integration
   - Timer control

4. **Mini CNC Plotter**
   - X-Y motor control
   - Stepper or DC with encoders
   - G-code interpreter

5. **Remote Control Car**
   - Dual motor drive
   - Wireless control (Bluetooth/WiFi)
   - Speed and steering control

## Motor Types Comparison

| Type | Pros | Cons | Best For |
|------|------|------|----------|
| Brushed DC | Simple, cheap | Wear, noise | Basic projects |
| Brushless DC | Efficient, long life | Complex control | Drones, precision |
| Stepper | Precise position | Low speed | 3D printers, CNC |
| Servo | Position feedback | Limited rotation | Robotics |

## Integration Examples

### With Joystick
```python
# Tank drive control
def joystick_drive(x, y):
    # Convert X-Y to differential
    left_speed = y + x
    right_speed = y - x
    
    # Normalize to -1 to 1
    left_speed = max(-1, min(1, left_speed))
    right_speed = max(-1, min(1, right_speed))
    
    # Apply to motors
    set_motor_speed(motor_left, left_speed)
    set_motor_speed(motor_right, right_speed)
```

### With Distance Sensor
```python
# Obstacle avoidance
if distance < 20:  # cm
    motor.stop()
    time.sleep(0.5)
    motor.backward(0.5)
    time.sleep(1)
    # Turn
    motor_left.forward(0.5)
    motor_right.backward(0.5)
```

## Next Steps

After mastering DC motor control:
1. Add encoders for position feedback
2. Implement PID control
3. Try stepper motors for precision
4. Build multi-axis systems
5. Create autonomous robots

## Resources

- [L293D Datasheet](http://www.ti.com/lit/ds/symlink/l293.pdf)
- [DC Motor Basics](https://www.electronics-tutorials.ws/io/io_7.html)
- [H-Bridge Theory](https://www.build-electronic-circuits.com/h-bridge/)
- [GPIO Zero Motor Control](https://gpiozero.readthedocs.io/en/stable/api_output.html#motor)