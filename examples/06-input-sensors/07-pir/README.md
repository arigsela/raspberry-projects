# Project 06-07: PIR Motion Sensor - Motion Detection and Security

Build motion-activated systems using Passive Infrared (PIR) sensors for security, automation, and energy saving.

## What You'll Learn

- PIR sensor principles and operation
- Motion detection techniques
- Event-driven sensor programming
- Security system design
- False trigger prevention
- Sensor placement strategies

## Hardware Requirements

- Raspberry Pi 5
- 1x PIR Motion Sensor Module (HC-SR501 or similar)
- 1x RGB LED (for status indication)
- 3x 220Ω resistors (for RGB LED)
- 1x Buzzer (optional, for security system)
- 1x Button (optional, for arm/disarm)
- Jumper wires
- Breadboard

## Circuit Diagram

```
Basic PIR + RGB LED Setup:
PIR Sensor          Raspberry Pi
VCC --------------- 5V (Pin 2)
OUT --------------- GPIO17 (Pin 11)
GND --------------- GND (Pin 6)

RGB LED            Raspberry Pi
Red ---[220Ω]------ GPIO18 (Pin 12)
Green -[220Ω]------ GPIO27 (Pin 13)
Blue --[220Ω]------ GPIO22 (Pin 15)
Common ------------ GND

Advanced Security System (adds):
Buzzer (+) -------- GPIO23 (Pin 16)
Buzzer (-) -------- GND
Button ------------ GPIO24 (Pin 18)
Button ------------ GND
```

## PIR Sensor Adjustments

Most PIR modules have two potentiometers:
- **Sensitivity (Sx)**: Detection range (3-7 meters)
- **Time Delay (Tx)**: Output duration (3-300 seconds)

And one jumper:
- **Trigger Mode**: 
  - H (Repeatable): Continuous triggering
  - L (Non-repeatable): Single trigger per motion

## Pin Connections

| Component | Pin | GPIO | Notes |
|-----------|-----|------|-------|
| PIR VCC | Pin 2 | 5V | Must be 5V |
| PIR OUT | Pin 11 | GPIO17 | 3.3V logic safe |
| PIR GND | Pin 6 | GND | Common ground |
| RGB Red | Pin 12 | GPIO18 | Through 220Ω |
| RGB Green | Pin 13 | GPIO27 | Through 220Ω |
| RGB Blue | Pin 15 | GPIO22 | Through 220Ω |
| Buzzer | Pin 16 | GPIO23 | Optional |
| Button | Pin 18 | GPIO24 | Optional |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero library
sudo apt install python3-gpiozero

# For advanced features (optional)
pip3 install requests  # For notifications
```

## Running the Programs

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/06-input-sensors/07-pir

# Run basic motion detector with LED feedback
python3 pir-motion-detector.py

# Or run full security system
python3 pir-security-system.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Motion Detector (pir-motion-detector.py)

1. **PIR Initialization**
   ```python
   pir = MotionSensor(PIR_PIN)
   ```
   - Configures GPIO as input
   - Handles signal processing

2. **Motion Callbacks**
   ```python
   pir.when_motion = motion_detected
   pir.when_no_motion = no_motion
   ```
   - Event-driven approach
   - No polling required

3. **Visual Feedback**
   - Blue: No motion (idle)
   - Yellow: Motion detected
   - Red: Continuous motion alert

### Security System (pir-security-system.py)

1. **State Machine**
   - DISARMED: Green LED, no alerts
   - ARMING: Orange LED, exit delay
   - ARMED: Blue LED, monitoring
   - TRIGGERED: Red LED, alarm active

2. **Features**
   - Exit/entry delays
   - Event logging
   - Button control
   - Audio alerts

## Key Concepts

### How PIR Sensors Work

1. **Pyroelectric Effect**
   - Detects infrared radiation changes
   - Human body emits ~9-10μm wavelength
   - Sensor has two sensing elements

2. **Fresnel Lens**
   - Focuses IR radiation
   - Creates detection zones
   - Increases range and sensitivity

3. **Differential Detection**
   - Compares two sensor halves
   - Detects moving heat sources
   - Ignores ambient changes

### Detection Characteristics

| Factor | Effect on Detection |
|--------|-------------------|
| Temperature | Better in cool environments |
| Movement Speed | Optimal: 0.5-1.5 m/s |
| Direction | Best: across field of view |
| Size | Larger objects easier to detect |
| Distance | Decreases with square of distance |

## Optimal Placement

### DO:
- Mount 2-3 meters high
- Angle slightly downward
- Place in corner for wide coverage
- Avoid direct sunlight
- Keep away from heat sources

### DON'T:
- Point at windows
- Place near air vents
- Mount near bright lights
- Aim at reflective surfaces
- Install outdoors (unless weatherproof)

## False Trigger Prevention

1. **Environmental**
   - Avoid drafts and air currents
   - Shield from direct sunlight
   - Keep away from heating vents

2. **Electronic**
   - Use queue_len parameter:
   ```python
   pir = MotionSensor(17, queue_len=3)
   ```
   - Adjust sensitivity potentiometer
   - Add software debouncing

3. **Physical**
   - Use lens masks to limit field
   - Create detection zones
   - Strategic placement

## Advanced Features

### Motion Logging
```python
def log_motion_event():
    timestamp = datetime.now()
    with open('motion_log.csv', 'a') as f:
        f.write(f"{timestamp},{location}\n")
```

### Email Notifications
```python
import smtplib
def send_alert():
    # Configure with your email settings
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.send_message(alert_message)
```

### Multiple Sensors
```python
sensors = {
    'front': MotionSensor(17),
    'back': MotionSensor(27),
    'garage': MotionSensor(22)
}
```

## Project Ideas

1. **Automatic Lighting**
   - Turn lights on when entering room
   - Adjust brightness based on time
   - Energy saving system

2. **Pet Detector**
   - Mount low for pet detection
   - Different alerts for different heights
   - Pet vs human discrimination

3. **Visitor Counter**
   - Count people entering/leaving
   - Peak time analysis
   - Occupancy monitoring

4. **Smart Doorbell**
   - Detect approach before bell press
   - Take photo when motion detected
   - Send notifications

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No detection | Check 5V power, adjust sensitivity |
| Constant triggering | Reduce sensitivity, check for heat sources |
| Delayed response | Reduce time delay pot, check trigger mode |
| Random triggers | Add shielding, check for EMI |
| Works intermittently | Check connections, power supply stability |

## PIR Specifications (HC-SR501)

| Parameter | Value |
|-----------|-------|
| Operating Voltage | 4.5-20V |
| Current Draw | <65mA |
| Output | 3.3V / 0V |
| Detection Range | 3-7m (adjustable) |
| Detection Angle | ~120° |
| Trigger Time | 0.3-300s (adjustable) |
| Working Temp | -15°C to +70°C |

## Security System Enhancements

1. **Zone Control**
   - Different areas with different rules
   - Partial arming (e.g., only perimeter)
   - Pet-immune zones

2. **Integration Options**
   - SMS/Email alerts
   - Camera triggering
   - Smart home integration
   - Remote monitoring

3. **Advanced Detection**
   - Combine with door/window sensors
   - Add glass break detectors
   - Implement AI for pattern recognition

## Power Saving Tips

- PIR sensors use very little power (~65mA)
- Implement sleep modes between detections
- Use LED indicators efficiently
- Consider battery backup for security

## Next Steps

After mastering PIR sensors:
1. Combine with camera modules for recording
2. Add network connectivity for IoT
3. Build complete home security system
4. Create motion-activated art installations
5. Develop wildlife monitoring systems

## Common Applications

- Security systems
- Automatic doors
- Energy management
- Wildlife cameras
- Interactive displays
- Occupancy sensing
- Halloween props
- Museum exhibits

## Resources

- [PIR Sensor Datasheet](https://www.mpja.com/download/31227sc.pdf)
- [GPIO Zero Motion Sensor](https://gpiozero.readthedocs.io/en/stable/api_input.html#motionsensor)
- [Security System Design](https://www.security.org/home-security-systems/diy/)
- [Motion Detection Theory](https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor)