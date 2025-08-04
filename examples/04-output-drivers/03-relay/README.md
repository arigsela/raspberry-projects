# Project 04-03: Relay Module - High-Power Device Control

Control high-voltage/high-current devices safely using relay modules for home automation, industrial control, and power management.

## What You'll Learn

- Relay principles and operation
- Electrical isolation concepts
- Safe high-voltage switching
- Relay module types
- Protection circuits
- Home automation basics

## Hardware Requirements

- Raspberry Pi 5
- 1-4 channel relay module (5V)
- High-power devices to control (lamps, motors, etc.)
- Optional: Push button for manual control
- Optional: PIR sensor for automation
- Jumper wires
- **IMPORTANT**: Proper electrical safety equipment

## Understanding Relays

### What is a Relay?
A relay is an electrically operated switch that uses a small control signal to switch much larger voltages and currents.

### Relay Components
```
Relay Internal Structure:
                    
    Control Side    │    Load Side
                    │
    Coil Terminal 1 │    Common (COM)
         ┌──────┐   │      ┌─────
    ═════╬      ╬═══│══════┤
         └──────┘   │      └─────
    Coil Terminal 2 │    Normally Open (NO)
                    │      ┌─────
                    │      ┤
                    │      └─────
                    │    Normally Closed (NC)
                    │
    Low Voltage     │    High Voltage
    (5V DC)         │    (120/240V AC)
```

### Relay Specifications
| Parameter | Description | Typical Values |
|-----------|-------------|----------------|
| Coil Voltage | Control voltage | 5V, 12V, 24V DC |
| Coil Current | Current to activate | 20-80mA |
| Contact Rating | Max switched power | 10A @ 250VAC |
| Contact Type | NO, NC, or SPDT | SPDT common |
| Isolation | Control/Load separation | 1000V+ |

## Circuit Diagram

```
Relay Module Connection:

Raspberry Pi Side (Low Voltage):
    3.3V/5V ─────────┐
                     │
    GPIO17 ──────────┤ Relay Module
                     │ ┌─────────────┐
    GND ─────────────┤ │ IN1    VCC  │
                       │             │
                       │ IN2    GND  │
                       │             │
                       │ IN3    JD-VCC│ ← Jumper for isolation
                       │             │
                       │ IN4         │
                       └─────────────┘
                              │││
                              │││ Relay Contacts
                              ▼▼▼
Load Side (High Voltage) - DANGER:
                        
    AC Hot ─────────────┤COM│ Relay 1
                        │   │
    To Load ────────────┤NO │ (Normally Open)
                        │   │
    (Not Used) ─────────┤NC │ (Normally Closed)
                        
    ⚠️ WARNING: High voltage - Professional installation required!

Optional Controls:
    Button: GPIO23 → GND (with internal pull-up)
    PIR Sensor: GPIO24 ← Motion detection
```

## Pin Connections

### Control Side (Safe, Low Voltage)
| Connection | GPIO Pin | Purpose |
|------------|----------|---------|
| IN1 | GPIO17 | Relay 1 control |
| IN2 | GPIO18 | Relay 2 control |
| IN3 | GPIO27 | Relay 3 control |
| IN4 | GPIO22 | Relay 4 control |
| VCC | 5V | Module power |
| GND | GND | Common ground |
| JD-VCC | Jumper | Optical isolation |

### Load Side (Dangerous, High Voltage)
| Terminal | Connection | Purpose |
|----------|------------|---------|
| COM | Power source | Common contact |
| NO | Load | Normally open |
| NC | Load (alt) | Normally closed |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero
sudo apt install -y python3-gpiozero

# No additional dependencies needed
```

## Running the Examples

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/04-output-drivers/03-relay

# Run the relay control examples
python3 relay-control.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Relay Control

1. **Initialization**
   ```python
   from gpiozero import OutputDevice
   
   # For active-high relay modules
   relay = OutputDevice(17, active_high=True)
   
   # For active-low modules (common)
   relay = OutputDevice(17, active_high=False)
   ```

2. **Control Commands**
   ```python
   relay.on()   # Activate relay
   relay.off()  # Deactivate relay
   relay.toggle()  # Switch state
   ```

3. **Timed Control**
   ```python
   # Turn on for 5 seconds
   relay.on()
   time.sleep(5)
   relay.off()
   ```

## Key Concepts

### Relay Types

1. **Mechanical Relay**
   - Physical contacts
   - Audible click
   - Complete isolation
   - Slower switching (10-20ms)

2. **Solid State Relay (SSR)**
   - No moving parts
   - Silent operation
   - Faster switching
   - More expensive

### Contact Configurations
```
SPST (Single Pole Single Throw):
    COM ──┤ ├── NO
    
SPDT (Single Pole Double Throw):
    NC ──┤   
    COM ──┤ ├── NO
    
DPDT (Double Pole Double Throw):
    NC1 ──┤     NC2 ──┤
    COM1 ──┤ ├── NO1  COM2 ──┤ ├── NO2
```

### Active High vs Active Low
- **Active High**: Relay ON when GPIO HIGH (3.3V)
- **Active Low**: Relay ON when GPIO LOW (0V)
- Most modules are active low with optocouplers

## Safety Considerations

### ⚠️ HIGH VOLTAGE WARNING
Working with mains voltage (120V/240V AC) can be FATAL. Always:

1. **Turn off power** at the breaker before wiring
2. **Use proper insulation** and enclosures
3. **Follow local electrical codes**
4. **Consider hiring a licensed electrician**
5. **Never work on live circuits**
6. **Use appropriate safety equipment**

### Isolation
```
Optocoupler Isolation:
    
GPIO →──[LED]──┐  ┌──[Phototransistor]──→ Relay Coil
               │  │
              ═╬  ╬═  (No electrical connection)
               │  │
GND ───────────┘  └────────────────────── Relay GND

Complete electrical isolation between control and load
```

## Common Applications

### 1. Home Automation
- Light control
- Appliance scheduling
- Smart outlets
- Garage door openers

### 2. Industrial Control
- Motor starters
- Solenoid valves
- Process control
- Safety interlocks

### 3. Garden/Agriculture
- Irrigation systems
- Grow lights
- Ventilation fans
- Pump control

### 4. Security Systems
- Door locks
- Alarm sirens
- Access control
- Emergency lighting

### 5. Energy Management
- Load shedding
- Peak demand control
- Solar switching
- Battery management

## Relay Module Features

### Built-in Protection
- **Optocoupler**: Electrical isolation
- **Flyback diode**: Protects against coil inductance
- **LED indicators**: Visual status
- **Screw terminals**: Secure connections

### Module Selection
| Channels | Use Case | Current per Channel |
|----------|----------|---------------------|
| 1 | Single device | 10A typical |
| 2 | Paired devices | 10A each |
| 4 | Multiple zones | 10A each |
| 8 | Home automation | 10A each |
| 16 | Industrial | 10A each |

## Advanced Techniques

### Soft Start for Motors
```python
def soft_start_motor(relay, pwm_pin):
    """Gradually start motor to reduce inrush current"""
    # Use SSR with PWM for soft start
    pwm = PWMOutputDevice(pwm_pin)
    
    # Gradually increase power
    for duty in range(0, 101, 5):
        pwm.value = duty / 100
        time.sleep(0.1)
    
    # Switch to full power with mechanical relay
    relay.on()
    pwm.off()
```

### Zero-Crossing Detection (AC)
```python
# For SSRs - switch at AC zero crossing
# Reduces electrical noise and stress
def zero_cross_switch(relay, zero_cross_pin):
    zc_detector = Button(zero_cross_pin)
    zc_detector.wait_for_press()  # Wait for zero crossing
    relay.on()  # Switch at optimal time
```

### Load Monitoring
```python
# Monitor current with ACS712 sensor
def monitor_load_current(adc_channel):
    # Read current sensor
    current = read_current_sensor(adc_channel)
    
    if current > MAX_CURRENT:
        relay.off()  # Protection
        alert("Overcurrent detected!")
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Relay won't activate | Check power supply, verify GPIO output |
| Relay clicks but load doesn't work | Check load connections, test with multimeter |
| Relay stays on | Check for active high/low setting |
| Rapid clicking | Insufficient power supply current |
| No isolation | Check JD-VCC jumper position |

## Power Calculations

### Load Power
```
Power (Watts) = Voltage × Current
Current = Power / Voltage

Example: 100W bulb at 120V
Current = 100W / 120V = 0.83A (well within 10A rating)
```

### Derating
- Continuous loads: Use 80% of rated capacity
- Inductive loads: Derate by 50% (motors, transformers)
- Incandescent bulbs: High inrush current (10x rated)

## Project Ideas

1. **Smart Power Strip**
   - Individual outlet control
   - Power monitoring
   - Scheduling
   - Remote control

2. **Garden Irrigation**
   - Zone control
   - Moisture sensors
   - Rain detection
   - Timer scheduling

3. **Home Security**
   - Door locks
   - Lighting control
   - Siren activation
   - Camera power

4. **Temperature Control**
   - Heater/cooler switching
   - Fan control
   - Thermostat logic
   - Zone management

5. **Solar Power Switch**
   - Battery/grid switching
   - Load management
   - Charge control
   - Power routing

## Integration Examples

### With Temperature Sensor
```python
def thermostat_control(temp_sensor, relay):
    temperature = temp_sensor.read()
    
    if temperature < SET_POINT - HYSTERESIS:
        relay.on()  # Turn on heater
    elif temperature > SET_POINT + HYSTERESIS:
        relay.off()  # Turn off heater
```

### With Web Interface
```python
# Flask web control
@app.route('/relay/<int:relay_id>/<action>')
def control_relay(relay_id, action):
    if action == 'on':
        relays[relay_id].on()
    elif action == 'off':
        relays[relay_id].off()
    return f"Relay {relay_id} {action}"
```

### With Voice Control
```python
# Integration with voice assistant
def handle_voice_command(command):
    if "lights on" in command:
        relay_lights.on()
    elif "lights off" in command:
        relay_lights.off()
```

## Best Practices

1. **Always use isolation** between control and load circuits
2. **Label all connections** clearly
3. **Use appropriate wire gauge** for current
4. **Include manual override** switches
5. **Implement failsafe** defaults
6. **Log all switching events**
7. **Test with low voltage** first

## Electrical Safety

### Wire Gauge Selection
| Current | Wire Gauge (AWG) |
|---------|------------------|
| 10A | 14 AWG |
| 15A | 12 AWG |
| 20A | 10 AWG |

### Protection Devices
- **Fuses**: One-time protection
- **Circuit breakers**: Resettable protection
- **GFCI**: Ground fault protection
- **Surge suppressors**: Voltage spike protection

## Next Steps

After mastering relay control:
1. Build complete home automation system
2. Add current/power monitoring
3. Implement voice/app control
4. Create scheduling system
5. Design custom PCBs with safety features

## Resources

- [Relay Basics](https://www.electronics-tutorials.ws/io/io_5.html)
- [Electrical Safety](https://www.osha.gov/electrical)
- [Home Automation Standards](https://www.home-assistant.io/)
- [GPIO Zero OutputDevice](https://gpiozero.readthedocs.io/en/stable/api_output.html#outputdevice)