# Project 03: PWM LED Brightness Control

Learn Pulse Width Modulation (PWM) by controlling LED brightness with software-generated PWM signals on Raspberry Pi 5.

## What You'll Learn

- **PWM Fundamentals**: Frequency, duty cycle, and period
- **Software PWM Implementation**: Using Python threading for timing
- **Thread Programming**: Python threading and synchronization
- **Animation Patterns**: Breathing, sine wave, and strobe effects
- **Real-time Constraints**: Understanding timing accuracy in Python

## Hardware Requirements

- Raspberry Pi 5
- 1x LED (any color)
- 1x 330Ω resistor
- 1x Push button (optional, for mode switching)
- Jumper wires
- Breadboard
- Oscilloscope (optional, for PWM visualization)

## Circuit Diagram

```
GPIO17 (Pin 11) ----[330Ω]----[LED+]----[LED-]---- GND
                                 |
                               (Anode)   (Cathode)

GPIO27 (Pin 13) ----[Button]---- GND
                 (Optional: for mode switching)
```

### Detailed Connections:
1. **LED Circuit**:
   - GPIO17 → 330Ω resistor → LED anode (long leg)
   - LED cathode (short leg) → GND
   - The resistor limits current to ~5mA (safe for Pi and LED)

2. **Button Circuit** (Optional):
   - GPIO27 → One side of button
   - Other side of button → GND
   - Internal pull-up enabled in software

## PWM Theory

### What is PWM?

Pulse Width Modulation creates an analog-like signal using digital outputs by rapidly switching between HIGH and LOW states.

```
100% Duty Cycle: ████████████████ (Always HIGH)
 75% Duty Cycle: ████████████░░░░ 
 50% Duty Cycle: ████████░░░░░░░░
 25% Duty Cycle: ████░░░░░░░░░░░░
  0% Duty Cycle: ░░░░░░░░░░░░░░░░ (Always LOW)
```

### Key Parameters:

1. **Frequency (f)**: How many complete cycles per second (Hz)
   - Our example: 1000 Hz (1 kHz)
   - Too low (<100 Hz): Visible flicker
   - Good for LEDs: 500 Hz - 5 kHz

2. **Period (T)**: Time for one complete cycle
   - T = 1/f = 1ms at 1 kHz

3. **Duty Cycle (D)**: Percentage of time the signal is HIGH
   - 0% = OFF, 100% = Full brightness
   - Average voltage = Vcc × (D/100)

### Why PWM Works for LEDs:

- LED brightness is proportional to average current
- Human eye perceives average brightness (persistence of vision)
- At >100 Hz, flicker becomes invisible

## Software Dependencies

```bash
# Install Python GPIO library
make deps
# Or manually:
sudo apt install python3-pip python3-gpiod
pip3 install gpiod
```

## Running the Programs

```bash
# Navigate to project
cd examples/03-pwm-control

# Run main PWM program with animations
make run

# Or run simple version
make run-simple

# Or run directly
sudo python3 pwm-control.py
```

## Code Walkthrough

### 1. **Threading Architecture**
```python
# PWM controller class with dedicated thread
class PWMController:
    def _pwm_loop(self):
        while self.active:
            # Calculate timing
            on_time = self.period * (duty / 100.0)
            off_time = self.period - on_time
            
            # Generate PWM signal
            if duty > 0:
                self.line.set_value(1)
                time.sleep(on_time)
```

### 2. **Thread-Safe Updates**
```python
# Using threading.Lock for synchronization
def set_duty_cycle(self, duty_cycle):
    with self.lock:
        self.duty_cycle = duty_cycle
```

### 3. **Animation Functions**
```python
# State persistence using function attributes
def breathing_animation(pwm):
    if not hasattr(breathing_animation, 'brightness'):
        breathing_animation.brightness = 0
    # Smooth brightness transitions
```

## Animation Modes

Press the button to cycle through:

1. **Manual Mode**: Fixed 50% brightness
2. **Breathing**: Smooth fade in/out (meditation light)
3. **Sine Wave**: Mathematical sine function brightness
4. **Strobe**: Rapid on/off switching

## Measurements with Oscilloscope

If you have an oscilloscope, measure:

1. **PWM Frequency**: Should be ~1 kHz
2. **Duty Cycle**: Verify percentage matches code
3. **Rise/Fall Times**: Check signal quality
4. **Jitter**: Timing consistency

Expected measurements:
- Frequency: 1000 Hz ± 5%
- Voltage levels: 0V (LOW), 3.3V (HIGH)
- Rise time: <1 μs

## Software PWM vs Hardware PWM

### Software PWM (This Example)
**Pros:**
- Works on any GPIO pin
- Flexible frequency/resolution
- Multiple independent channels

**Cons:**
- CPU intensive
- Timing jitter
- Limited by OS scheduling

### Hardware PWM (Pi 5 Specific Pins)
**Pros:**
- No CPU usage
- Precise timing
- Higher frequencies possible

**Cons:**
- Limited pins (GPIO12, 13, 18, 19)
- Fixed frequencies
- More complex setup

## Extending This Project

### 1. **RGB LED Control**
```c
// Control 3 PWM channels for RGB
pwm_init(&red_pwm, red_line);
pwm_init(&green_pwm, green_line);
pwm_init(&blue_pwm, blue_line);
```

### 2. **Servo Motor Control**
```c
// Servos use 50 Hz PWM (20ms period)
// 1-2ms pulse width for 0-180° position
#define SERVO_FREQUENCY 50
#define SERVO_MIN_PULSE_MS 1.0
#define SERVO_MAX_PULSE_MS 2.0
```

### 3. **Music Generation**
```c
// Generate tones by varying PWM frequency
// A4 = 440 Hz, C5 = 523 Hz, etc.
void play_note(int frequency) {
    set_pwm_frequency(frequency);
    set_duty_cycle(50);  // Square wave
}
```

## Troubleshooting

### LED Flickers Visibly
- Increase PWM frequency (try 2-5 kHz)
- Check for other CPU-intensive processes
- Consider using hardware PWM pins

### Inconsistent Brightness
- Add small capacitor (0.1μF) across LED
- Ensure stable power supply
- Check for loose connections

### High CPU Usage
- Normal for software PWM (~5-10% per channel)
- Reduce frequency if acceptable
- Use hardware PWM for production

### Program Hangs
- Ensure proper thread cleanup
- Check mutex deadlocks
- Add timeout to thread joins

## Learning Exercises

1. **Measure Actual Frequency**
   - Use oscilloscope or logic analyzer
   - Compare to theoretical value
   - Calculate timing error

2. **Create Color Mixer**
   - Add two more LEDs (RGB)
   - Mix colors using different duty cycles
   - Create color fade animations

3. **Optimize Performance**
   - Profile CPU usage
   - Try different timer methods
   - Implement hardware PWM version

## Theory Connection: MIT 6.002

This project relates to:
- **Lecture 22-23**: Energy and Power
  - Average power = V²/R × Duty Cycle
- **RC Circuits**: Adding capacitor creates low-pass filter
- **Digital Abstraction**: PWM bridges digital/analog

## Next Steps

- Proceed to Project 04: SPI Temperature Sensor
- Or explore: Hardware PWM implementation
- Advanced: Multi-channel PWM for robotics