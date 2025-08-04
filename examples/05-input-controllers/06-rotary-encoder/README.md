# Rotary Encoder Position and Direction Detection

Read rotational position, direction, and speed from a rotary encoder with push button.

## What You'll Learn
- Quadrature encoder signal processing
- Direction detection using phase relationships
- Position tracking with interrupts
- Speed and acceleration measurement
- Debouncing rotary encoder signals
- Event-driven programming with callbacks

## Hardware Requirements
- Raspberry Pi 5
- Rotary encoder module (KY-040 or similar)
- Optional: LEDs for direction indication
- Optional: Buzzer for audio feedback
- Optional: PWM LED for brightness control
- Jumper wires

## Circuit Diagram

```
Rotary Encoder Module (KY-040):
┌─────────────────┐
│      ┌─┐        │
│    ┌─┤ ├─┐      │  Encoder with
│    │ └─┘ │      │  push button
│    └─────┘      │
├─────────────────┤
│ GND VCC SW DT CLK│
└──┬───┬──┬──┬───┬┘
   │   │  │  │   │
   │   │  │  │   └── GPIO17 (CLK - Channel A)
   │   │  │  └────── GPIO18 (DT - Channel B)
   │   │  └───────── GPIO27 (SW - Switch)
   │   └──────────── 3.3V
   └──────────────── GND

Optional indicators:
LED (CW):     GPIO23 → 220Ω → LED → GND
LED (CCW):    GPIO24 → 220Ω → LED → GND
PWM LED:      GPIO22 → 220Ω → LED → GND
Buzzer:       GPIO25 → Buzzer → GND
```

## Software Dependencies

Install required libraries:
```bash
pip install gpiozero
```

## Running the Program

```bash
cd examples/05-input-controllers/06-rotary-encoder
python rotary-encoder.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test encoder functionality
make demo     # Run all demos
make install  # Install dependencies
```

## Code Walkthrough

### Quadrature Signal Processing
Rotary encoders generate two signals (A and B) 90° out of phase:
```python
def _on_rotation(self):
    """Handle rotation detection"""
    current_clk = self.clk.is_pressed
    current_dt = self.dt.is_pressed
    
    if current_clk != self.last_clk_state:
        if current_clk == current_dt:
            # Counter-clockwise
            self.position -= 1
            self.direction = -1
        else:
            # Clockwise
            self.position += 1
            self.direction = 1
```

### Speed Calculation
Track rotation timing for speed measurement:
```python
def get_speed(self):
    """Get rotation speed (rotations per second)"""
    if len(self.rotation_times) < 2:
        return 0
    
    avg_time = sum(self.rotation_times) / len(self.rotation_times)
    if avg_time > 0:
        return 1.0 / avg_time
    return 0
```

### Event Callbacks
Register functions to handle rotation and button events:
```python
encoder.set_rotation_callback(on_rotation)
encoder.set_button_callback(on_button)

def on_rotation(position, direction):
    print(f"Position: {position}, Direction: {direction}")
```

## Key Concepts

### Quadrature Encoding
- **Two channels**: A and B signals 90° apart
- **Direction detection**: Phase relationship determines direction
- **Resolution**: Typically 20-30 pulses per revolution
- **Gray code**: Only one signal changes at a time

### Signal Processing
- **Edge detection**: Monitor rising/falling edges
- **Debouncing**: Handle mechanical switch bounce
- **Interrupt-driven**: React immediately to changes
- **State machine**: Track previous states

### Applications
- **Volume controls**: Audio equipment
- **Menu navigation**: User interfaces  
- **Motor control**: Position feedback
- **Measurement**: Angle and distance sensing

## Available Demos

1. **Basic Position Tracking**: Show position and direction
2. **LED Direction Indicator**: Visual direction feedback
3. **Brightness Control**: PWM LED brightness adjustment
4. **Menu Navigation**: Navigate through menu items
5. **Volume Control**: Simulate audio volume control
6. **Step Counter**: Configurable step counting
7. **Speed Monitor**: Real-time speed measurement
8. **Encoder Calibration**: Test accuracy and linearity

## Troubleshooting

### No response from encoder
- Check all 5 connections (GND, VCC, CLK, DT, SW)
- Verify 3.3V power supply
- Ensure pull-up resistors are enabled

### Wrong direction detection
- Swap CLK and DT connections
- Check signal timing and debouncing
- Verify encoder type (some have inverted logic)

### Erratic counting
- Add hardware debouncing (capacitors)
- Increase software bounce time
- Check for electrical noise

### Button not working
- Verify SW pin connection
- Check pull-up configuration
- Test button continuity

## Advanced Usage

### Multiple Encoders
Handle multiple encoders with shared code:
```python
encoder1 = RotaryEncoder(17, 18, 27)
encoder2 = RotaryEncoder(19, 20, 21)

def handle_encoder1(pos, dir):
    print(f"Encoder 1: {pos}")

encoder1.set_rotation_callback(handle_encoder1)
```

### Acceleration Detection
Track rapid movements:
```python
def detect_acceleration():
    times = encoder.rotation_times
    if len(times) >= 3:
        recent_avg = sum(times[-2:]) / 2
        older_avg = sum(times[-4:-2]) / 2
        acceleration = (older_avg - recent_avg) / recent_avg
        return acceleration > 0.5  # 50% speed increase
```

### Position Limits
Implement software limits:
```python
def on_rotation(position, direction):
    if position < 0:
        encoder.position = 0
    elif position > 100:
        encoder.position = 100
```

### Custom Step Sizes
Non-linear step progression:
```python
STEP_SIZES = [1, 2, 5, 10, 25, 50, 100]

def adaptive_step(speed):
    if speed > 5:
        return STEP_SIZES[-1]  # Large steps for fast rotation
    else:
        return STEP_SIZES[0]   # Small steps for slow rotation
```

## Performance Considerations

### Interrupt Handling
- Keep interrupt handlers short
- Use flags for complex processing
- Avoid blocking operations in callbacks

### Timing Sensitivity
- Use appropriate bounce times
- Consider hardware filtering for noisy environments
- Monitor CPU usage with high-speed rotation

## Next Steps
- Try creating a digital combination lock
- Implement encoder-controlled servo positioning
- Build a rotary menu system for other projects
- Create an encoder-based measurement tool