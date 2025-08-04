# Project 04-02: Servo Motor - Precise Position Control

Master servo motor control for precise angular positioning using PWM signals on Raspberry Pi 5.

## What You'll Learn

- Servo motor principles and control
- PWM signal generation for servos
- Angle-to-pulse width conversion
- Servo calibration techniques
- Smooth motion programming
- Power considerations for motors

## Hardware Requirements

- Raspberry Pi 5
- 1x Servo motor (SG90 or similar)
- 3x Jumper wires
- External 5V power supply (recommended for multiple servos)
- Breadboard (optional)
- GPIO Extension Board (optional)

## Circuit Diagram

```
Servo Wire Colors (Standard):
- Orange/Yellow: Signal (PWM)
- Red: Power (+5V)
- Brown/Black: Ground (GND)

Basic Connection:
Raspberry Pi          Servo Motor
GPIO18 (Pin 12) ---- Signal (Orange)
5V (Pin 2) --------- Power (Red)
GND (Pin 6) -------- Ground (Brown)

With External Power (Recommended):
GPIO18 -------- Signal
                  |
External 5V --- Power
                  |
External GND -- Ground
      |
Pi GND (Common ground required!)
```

## Pin Connections

| Servo Wire | Connection | Notes |
|------------|------------|-------|
| Signal (Orange/Yellow) | GPIO18 | PWM control signal |
| Power (Red) | 5V or External | See power notes below |
| Ground (Brown/Black) | GND | Common ground with Pi |

## Power Considerations

### Single Small Servo (SG90)
- Can be powered from Pi's 5V pin
- Current draw: ~100-200mA when moving
- Acceptable for testing and light use

### Multiple or Large Servos
- **Must use external 5V power supply**
- Pi's 5V rail limited to ~1.5A total
- Always connect grounds together
- Use capacitor (1000µF) to smooth power

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero library
sudo apt install python3-gpiozero

# For advanced servo control (optional)
pip3 install pigpio
```

## Running the Program

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/04-output-drivers/02-servo

# Run the automatic demo
python3 servo-control.py

# Or try interactive control
python3 servo-interactive.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Servo Control (servo-control.py)

1. **Servo Initialization**
   ```python
   servo = Servo(SERVO_PIN, 
                 min_pulse_width=0.5/1000,
                 max_pulse_width=2.5/1000)
   ```
   - Configure PWM pin
   - Set pulse width range for your servo

2. **Position Control**
   ```python
   servo.min()    # 0° position
   servo.mid()    # 90° position
   servo.max()    # 180° position
   servo.value = 0.5  # Specific position
   ```

3. **Angle Conversion**
   ```python
   def angle_to_value(angle):
       return (angle / 90.0) - 1
   ```
   - Convert 0-180° to -1 to 1 range

### Interactive Control (servo-interactive.py)

- Fine position adjustments
- Smooth sweep demonstrations
- Real-time angle feedback
- Servo detach/attach control

## Key Concepts

### How Servos Work
1. **Control Signal**: 50Hz PWM (20ms period)
2. **Pulse Width**: 0.5-2.5ms determines position
3. **Feedback**: Internal potentiometer maintains position
4. **Holding Torque**: Actively maintains position

### PWM Signal Timing
| Position | Pulse Width | Duty Cycle |
|----------|-------------|------------|
| 0° (left) | 0.5ms | 2.5% |
| 90° (center) | 1.5ms | 7.5% |
| 180° (right) | 2.5ms | 12.5% |

### Servo Types

#### Standard Servo (180°)
- Range: 0-180 degrees
- Common: SG90, MG90S
- Used in this project

#### Continuous Rotation
- No position control
- Speed and direction control only
- Modified standard servos

#### High-Torque Servos
- Metal gears
- Higher current draw
- Better precision

## Calibration

### Finding Your Servo's Range
```python
# Test minimum pulse width
servo = Servo(18, min_pulse_width=0.5/1000)
# Gradually increase if it doesn't reach 0°

# Test maximum pulse width  
servo = Servo(18, max_pulse_width=2.5/1000)
# Gradually decrease if it overshoots 180°
```

### Common Servo Specifications

| Model | Voltage | Torque | Speed | Range |
|-------|---------|--------|-------|-------|
| SG90 | 4.8-6V | 1.8kg/cm | 0.1s/60° | 180° |
| MG90S | 4.8-6V | 2.2kg/cm | 0.1s/60° | 180° |
| MG995 | 4.8-7.2V | 10kg/cm | 0.2s/60° | 180° |

## Smooth Motion Techniques

### Linear Sweep
```python
for angle in range(0, 181):
    servo.value = angle_to_value(angle)
    sleep(0.01)
```

### Ease In/Out
```python
# Accelerate and decelerate
import math
for i in range(100):
    t = i / 100.0
    # Ease in-out curve
    angle = 180 * (0.5 - 0.5 * math.cos(math.pi * t))
    servo.value = angle_to_value(angle)
    sleep(0.02)
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Servo jitters | Check power supply, add capacitor |
| Limited range | Adjust pulse width parameters |
| No movement | Verify connections, check servo power |
| Servo hums | Normal, but check if mechanically blocked |
| Erratic movement | Common ground issue or insufficient power |
| Gets hot | Reduce load or duty cycle |

## Project Applications

1. **Pan-Tilt Camera Mount**
   - Two servos for X/Y control
   - Face tracking possibilities

2. **Robot Arm**
   - Multiple servos for joints
   - Inverse kinematics

3. **Door Lock**
   - Servo-controlled deadbolt
   - Remote access control

4. **Gauge Display**
   - Analog-style indicators
   - Weather station display

## Advanced Techniques

### Multiple Servo Control
```python
from gpiozero import Servo

servos = {
    'pan': Servo(17),
    'tilt': Servo(18),
    'grip': Servo(27)
}

# Control all servos
for name, servo in servos.items():
    servo.mid()
```

### Servo Speed Control
```python
def move_servo_slowly(servo, target_angle, duration):
    start_angle = value_to_angle(servo.value)
    steps = 100
    
    for i in range(steps + 1):
        current = start_angle + (target_angle - start_angle) * i / steps
        servo.value = angle_to_value(current)
        sleep(duration / steps)
```

### Save Power - Detach When Idle
```python
# Stop sending PWM signal
servo.detach()

# Resume control
servo.value = angle_to_value(90)
```

## Safety Notes

1. **Never force servo beyond limits**
   - Can damage gears
   - Draws excessive current

2. **Use appropriate power supply**
   - Servos can draw 500mA+ when stalled
   - Voltage spikes can reset Pi

3. **Include mechanical stops**
   - Prevent damage in projects
   - Emergency cutoff switches

## Servo vs Stepper Motors

| Feature | Servo | Stepper |
|---------|-------|---------|
| Position Feedback | Yes | No |
| Precision | Good | Excellent |
| Speed | Fast | Slower |
| Power at Rest | Yes | Optional |
| Cost | Low | Higher |
| Control | Simple | Complex |

## Next Steps

After mastering servo control:
1. Build a pan-tilt mechanism
2. Create a robotic arm project
3. Try Project 04-01: DC Motor for continuous rotation
4. Explore Project 06-07: PIR sensor for motion-activated servos
5. Combine with camera for tracking projects

## Resources

- [GPIO Zero Servo Documentation](https://gpiozero.readthedocs.io/en/stable/api_output.html#servo)
- [Servo Motor Basics](https://learn.sparkfun.com/tutorials/servo-motor-control)
- [PWM Theory](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-8-using-a-servo-motor)
- [Servo Specifications Database](https://servodatabase.com/)