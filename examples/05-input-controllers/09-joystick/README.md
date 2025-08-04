# 2-Axis Analog Joystick with Push Button

Read X and Y position and button state from an analog joystick module using ADC.

## What You'll Learn
- Analog-to-digital conversion for joystick input
- 2-axis position reading and calibration
- Dead zone implementation for stability
- Polar coordinate conversion (angle/magnitude)
- Servo control with joystick input
- Interactive user interfaces with analog input
- Game development with hardware controllers

## Hardware Requirements
- Raspberry Pi 5
- ADC0834 4-channel ADC chip
- Analog joystick module (2-axis with button)
- Optional: Servo motors for pan/tilt control
- Optional: LEDs for direction indication
- Jumper wires

## Circuit Diagram

```
ADC0834 Connections:
┌─────────────────┐
│     ADC0834     │
│  CS CLK DI DO   │
│  17 18  27 22   │ GPIO pins
└─┬───┬───┬──┬───┘
  │   │   │  │
  │   │   │  └── To joystick and other analog inputs
  │   │   └───── Data flow to/from Pi
  │   └───────── Clock signal
  └───────────── Chip select

Joystick Module:
┌─────────────────┐
│   ┌─────────┐   │
│   │    ○    │   │  Analog joystick
│   │    │    │   │  X and Y outputs
│   │    ●    │   │  Push button
│   └─────────┘   │
├─────────────────┤
│ GND VCC SW Y  X │
└──┬───┬──┬──┬──┬┘
   │   │  │  │  │
   │   │  │  │  └── ADC Channel 0 (X-axis)
   │   │  │  └───── ADC Channel 1 (Y-axis)
   │   │  └──────── GPIO23 (Switch)
   │   └─────────── 3.3V
   └─────────────── GND

Optional Direction LEDs:
Up LED:    GPIO24 → 220Ω → LED → GND
Down LED:  GPIO25 → 220Ω → LED → GND
Left LED:  GPIO26 → 220Ω → LED → GND
Right LED: GPIO19 → 220Ω → LED → GND

Optional Servos:
X Servo: GPIO20 (Pan)
Y Servo: GPIO21 (Tilt)
```

## Software Dependencies

Install required libraries:
```bash
pip install gpiozero
```

## Running the Program

```bash
cd examples/05-input-controllers/09-joystick
python joystick.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test joystick functionality
make servo    # Run servo control demo
make game     # Play reaction game
make install  # Install dependencies
```

## Code Walkthrough

### ADC Reading
Read raw analog values from X and Y axes:
```python
def read_raw(self):
    """Read raw ADC values"""
    x_raw = self.adc.read_channel(self.x_channel)
    y_raw = self.adc.read_channel(self.y_channel)
    return x_raw, y_raw
```

### Position Normalization
Convert raw ADC values to normalized -1.0 to 1.0 range:
```python
def read_position(self):
    x_raw, y_raw = self.read_raw()
    
    # Normalize based on calibrated center and range
    x_normalized = (x_raw - self.x_center) / (self.x_max - self.x_center)
    y_normalized = (y_raw - self.y_center) / (self.y_max - self.y_center)
    
    # Apply dead zone to prevent jitter
    if abs(x_normalized) < self.dead_zone:
        x_normalized = 0.0
    
    return x_normalized, y_normalized
```

### Polar Coordinates
Convert Cartesian (X,Y) to polar (angle, magnitude):
```python
def read_polar(self):
    x, y = self.read_position()
    
    angle = math.degrees(math.atan2(y, x))
    if angle < 0:
        angle += 360
    
    magnitude = math.sqrt(x*x + y*y)
    return angle, magnitude
```

### Calibration System
Auto-calibrate center position and movement range:
```python
def calibrate(self):
    # Step 1: Find center position
    input("Center joystick and press Enter...")
    self.x_center, self.y_center = self.read_raw()
    
    # Step 2: Find movement range
    print("Move joystick to all extremes for 5 seconds...")
    # Collect min/max values during movement
```

## Key Concepts

### Analog Joysticks
- **Potentiometers**: Variable resistors for X and Y axes
- **Center position**: ~50% of voltage range when centered
- **Movement range**: Full deflection gives 0-100% range
- **Non-linearity**: May not be perfectly linear across range

### Signal Processing
- **Calibration**: Account for manufacturing variations
- **Dead zone**: Prevent jitter near center position
- **Filtering**: Smooth out electrical noise
- **Scaling**: Convert to useful coordinate systems

### Applications
- **Gaming**: Controller input for games
- **Robotics**: Manual robot control
- **Camera control**: Pan/tilt camera systems
- **User interfaces**: Menu navigation

## Available Demos

1. **Basic Position Reading**: Show raw and normalized positions
2. **Direction LEDs**: Visual feedback with LEDs
3. **Servo Control**: Control pan/tilt servos with joystick
4. **Cursor Control**: ASCII screen cursor movement
5. **Reaction Game**: Test reflexes with directional prompts
6. **Analog Clock Control**: Set time with joystick
7. **Calibration**: Auto-calibrate joystick parameters

## Troubleshooting

### No joystick response
- Check ADC connections (CS, CLK, DI, DO)
- Verify joystick power (3.3V, GND)
- Test ADC channels with multimeter
- Ensure correct channel assignments

### Erratic readings
- Implement or increase dead zone
- Check power supply stability
- Add filtering capacitors near joystick
- Calibrate joystick center and range

### Button not working
- Verify switch pin connection and pull-up
- Check button contact continuity
- Test with multimeter

### Limited range
- Recalibrate joystick
- Check for mechanical obstructions
- Verify ADC reference voltage

## Advanced Usage

### Multi-axis Control
Control multiple parameters simultaneously:
```python
def update_system(self):
    x, y = joystick.read_position()
    
    # Control multiple outputs
    servo_pan.value = x
    servo_tilt.value = y
    led_brightness.value = abs(x)
    buzzer_frequency = 1000 + (y * 500)
```

### Velocity Control
Use joystick for velocity rather than position:
```python
def velocity_control(self):
    x, y = joystick.read_position()
    
    # Scale to velocity (pixels per second)
    vel_x = x * MAX_VELOCITY
    vel_y = y * MAX_VELOCITY
    
    # Update position based on velocity
    cursor_x += vel_x * dt
    cursor_y += vel_y * dt
```

### Gesture Recognition
Detect joystick movement patterns:
```python
def detect_gesture(self):
    # Record position history
    self.position_history.append(joystick.read_position())
    
    # Analyze for patterns (circles, swipes, etc.)
    if len(self.position_history) > 20:
        # Pattern matching logic
        pass
```

### Non-linear Response
Implement custom response curves:
```python
def apply_curve(self, value):
    # Exponential curve for fine control near center
    if abs(value) < 0.5:
        return value * 0.3  # Reduce sensitivity
    else:
        return math.copysign(0.3 + 0.7 * ((abs(value) - 0.5) / 0.5), value)
```

## Performance Considerations

### Sampling Rate
- ADC conversion time limits maximum sample rate
- Typical rates: 100-1000 Hz for interactive applications
- Balance responsiveness vs. CPU usage

### Filtering
- Moving average for smooth movement
- Low-pass filter for noise reduction
- Hysteresis for button-like behavior

## Next Steps
- Build a joystick-controlled robot
- Create more complex games with multiple inputs
- Implement advanced control algorithms (PID control)
- Add haptic feedback with vibration motors
- Design custom joystick-based user interfaces