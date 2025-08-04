# Project 05-04: Slide Switch - State Selection Control

Detect slide switch positions for mode selection, configuration settings, and state-based control systems.

## What You'll Learn

- SPDT/DPDT switch operation
- State detection vs edge detection
- Mode selection techniques
- Pull-up resistor configuration
- State machine implementation
- Power management applications

## Hardware Requirements

- Raspberry Pi 5
- SPDT slide switch (or DPDT)
- 2 LEDs for state indication
- RGB LED (optional)
- 220-330Ω resistors for LEDs
- 10kΩ pull-up resistor (if not using internal)
- Jumper wires
- Breadboard

## Understanding Slide Switches

### Switch Types

```
SPDT (Single Pole Double Throw):
         COM (Common)
           │
      ┌────┼────┐
      │    │    │
     NO    │    NC
(Normally │ (Normally
  Open)   │  Closed)
          │
    Position A  Position B

DPDT (Double Pole Double Throw):
    COM1      COM2
      │        │
  ┌───┼───┐┌───┼───┐
  │   │   ││   │   │
 NO1  │  NC1 NO2│  NC2
      │        │
  Pole 1    Pole 2
```

### Switch States
- **Position A**: COM connected to NO
- **Position B**: COM connected to NC
- No intermediate/floating state

## Circuit Diagram

```
Basic SPDT Connection:

    3.3V ──┐
           │
          ╱ │ 10kΩ (internal pull-up)
           │
    GPIO17 ├──────┬─── COM (Center pin)
           │      │
           │     ╱ ╲  Slide Switch
           │    ╱   ╲
           │   NO    NC
           │   │      │
           │   └──────┴─── GND
           │
LED Indicators:
    GPIO18 ├──[220Ω]──╢▶├── GND (LED1)
           │
    GPIO27 ├──[220Ω]──╢▶├── GND (LED2)

Note: Only one side needs GND connection
```

## Pin Connections

| Component | GPIO Pin | Purpose |
|-----------|----------|---------|
| Switch COM | GPIO17 | Input with pull-up |
| Switch NO/NC | GND | Ground connection |
| LED1 Anode | GPIO18 | Position 1 indicator |
| LED2 Anode | GPIO27 | Position 2 indicator |
| RGB Red | GPIO22 | RGB mode indicator |
| RGB Green | GPIO23 | RGB mode indicator |
| RGB Blue | GPIO24 | RGB mode indicator |

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
cd ~/raspberry-projects/examples/05-input-controllers/04-slide-switch

# Run the slide switch examples
python3 slide-switch.py

# Run specific demos
make run       # Interactive menu
make test      # Test switch detection
make mode      # Mode selection demo
make safety    # Safety interlock demo
```

## Code Walkthrough

### Basic Position Detection

1. **Setup**
   ```python
   from gpiozero import Button
   
   # Switch connects GPIO to GND when in position
   switch = Button(17, pull_up=True)
   ```

2. **Read Position**
   ```python
   if switch.is_pressed:
       print("Position 1")
   else:
       print("Position 2")
   ```

3. **Detect Changes**
   ```python
   last_state = switch.is_pressed
   
   while True:
       current_state = switch.is_pressed
       if current_state != last_state:
           print(f"Switch moved to position {1 if current_state else 2}")
           last_state = current_state
   ```

## Key Concepts

### State vs Edge Detection

| Type | Use Case | Example |
|------|----------|----------|
| State | Current position matters | Power mode selection |
| Edge | Change detection matters | Counter increment |
| Both | Complex state machines | Safety systems |

### Pull-up Configuration

```python
# Internal pull-up (convenient)
switch = Button(pin, pull_up=True)

# External pull-up (customizable)
switch = Button(pin, pull_up=False)
```

### Debouncing

Slide switches typically don't need debouncing:
- Mechanical design prevents bounce
- Sliding action is deliberate
- State changes are intentional

## Common Applications

### 1. Mode Selection
- Normal/Expert mode
- Manual/Auto control
- Indoor/Outdoor settings
- Language selection

### 2. Power Management
- On/Standby modes
- Performance profiles
- Battery saver
- Screen brightness

### 3. Safety Systems
- Enable/Disable
- Lock/Unlock
- Armed/Disarmed
- Test/Operate

### 4. Configuration
- USB/Bluetooth
- Master/Slave
- Input source
- Output routing

### 5. Gaming
- Difficulty levels
- Player selection
- Game modes
- Control schemes

## Advanced Techniques

### Multi-State with Single SPDT

```python
# Simulate 3 positions with timing
def detect_center_position():
    # Quick toggle = center position
    changes = []
    for _ in range(10):
        changes.append(switch.is_pressed)
        time.sleep(0.05)
    
    if len(set(changes)) > 1:  # Multiple changes
        return "center"
    elif changes[0]:
        return "left"
    else:
        return "right"
```

### State Machine Implementation

```python
class DeviceStateMachine:
    def __init__(self):
        self.states = ["OFF", "STANDBY", "ACTIVE"]
        self.current = 0
    
    def update(self, switch_position):
        if switch_position:  # Position 1
            if self.current < len(self.states) - 1:
                self.current += 1
        else:  # Position 2
            if self.current > 0:
                self.current -= 1
        
        return self.states[self.current]
```

### Persistent Settings

```python
import json

def save_mode(position):
    settings = {"mode": "advanced" if position else "basic"}
    with open("settings.json", "w") as f:
        json.dump(settings, f)

def load_mode():
    try:
        with open("settings.json", "r") as f:
            return json.load(f)["mode"]
    except:
        return "basic"
```

## Safety Interlock Example

```python
class SafetyInterlock:
    def __init__(self, safety_switch_pin, enable_pin):
        self.safety = Button(safety_switch_pin)
        self.enable = Button(enable_pin)
    
    def can_operate(self):
        # Both switches must be in correct position
        return self.safety.is_pressed and self.enable.is_pressed
    
    def get_status(self):
        if not self.safety.is_pressed:
            return "LOCKED - Safety switch OFF"
        elif not self.enable.is_pressed:
            return "DISABLED - Enable switch OFF"
        else:
            return "READY - System armed"
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Always reads same state | Check wiring, verify pull-up |
| Intermittent readings | Check connections, clean contacts |
| Wrong position detected | Verify NO/NC connections |
| No state changes | Test continuity with multimeter |
| LEDs don't match state | Check LED polarity and resistors |

## Power Consumption

### Low Power Design
```python
# Only check when needed
def power_efficient_monitor():
    # Use interrupts instead of polling
    switch.when_pressed = handle_position_1
    switch.when_released = handle_position_2
    
    # Sleep between checks
    signal.pause()
```

### Current Draw
- Switch with pull-up: ~0.3mA (3.3V/10kΩ)
- LED indicator: 10-20mA each
- Total: < 50mA typical

## Project Ideas

1. **Smart Light Switch**
   - Manual/Auto modes
   - Brightness presets
   - Motion activation toggle
   - Schedule enable/disable

2. **Security System Mode**
   - Home/Away modes
   - Test/Armed states
   - Silent/Audible alarm
   - Bypass sensors

3. **Audio Input Selector**
   - Multiple input sources
   - Gain settings
   - Filter modes
   - Output routing

4. **Robot Control Mode**
   - Manual/Autonomous
   - Speed settings
   - Sensor priority
   - Debug mode

5. **Display Settings**
   - Day/Night mode
   - Color schemes
   - Info display levels
   - Rotation lock

## Integration Examples

### With Configuration File
```python
config = {
    True: "config_a.json",
    False: "config_b.json"
}

def load_config_for_position():
    position = switch.is_pressed
    with open(config[position]) as f:
        return json.load(f)
```

### With OLED Display
```python
def update_display():
    mode = "Mode A" if switch.is_pressed else "Mode B"
    oled.text(f"Current: {mode}", 0, 0)
    oled.show()
```

### With Network Settings
```python
def configure_network():
    if switch.is_pressed:
        # WiFi mode
        enable_wifi()
        disable_ethernet()
    else:
        # Ethernet mode
        disable_wifi()
        enable_ethernet()
```

## Best Practices

1. **Label switch positions** clearly on enclosure
2. **Use consistent logic** (e.g., up = on)
3. **Provide visual feedback** for current state
4. **Document switch behavior** in user manual
5. **Test both positions** during startup
6. **Handle transitions** gracefully
7. **Save state** for power loss recovery

## DPDT Switch Usage

```python
# Use both poles for redundancy or dual function
class DPDTSwitch:
    def __init__(self, pole1_pin, pole2_pin):
        self.pole1 = Button(pole1_pin)
        self.pole2 = Button(pole2_pin)
    
    def get_position(self):
        # Both poles should agree
        if self.pole1.is_pressed == self.pole2.is_pressed:
            return self.pole1.is_pressed
        else:
            raise ValueError("Switch poles disagree!")
```

## Next Steps

After mastering slide switches:
1. Combine with rotary encoders for menu systems
2. Add multiple switches for complex configurations
3. Implement switch matrices for many options
4. Create professional control panels
5. Design custom PCBs with integrated switches

## Resources

- [Switch Types](https://www.electronics-tutorials.ws/switch/switch_2.html)
- [GPIO Zero Button](https://gpiozero.readthedocs.io/en/stable/api_input.html#button)
- [State Machines](https://en.wikipedia.org/wiki/Finite-state_machine)
- [Pull-up Resistors](https://learn.sparkfun.com/tutorials/pull-up-resistors)