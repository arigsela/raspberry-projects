# Project 05-02: Micro Switch - Momentary Contact Detection

Detect momentary button presses using micro switches with proper debouncing for reliable input detection.

## What You'll Learn

- Micro switch operation principles
- Software debouncing techniques
- Event-driven vs polling input methods
- Switch bounce characteristics
- Pull-up resistor usage
- Input state detection

## Hardware Requirements

- Raspberry Pi 5
- Micro switch (momentary contact)
- LED (optional for visual feedback)
- 220-330Ω resistor for LED
- Pull-up resistor (10kΩ) if not using internal
- Jumper wires
- Breadboard

## Understanding Micro Switches

### What is a Micro Switch?
A micro switch is a momentary contact switch that makes electrical connection only while being pressed. When released, it returns to its open state.

### Switch Bounce
```
Ideal Switch Behavior:
    Press                Release
     ↓                    ↓
─────┘                    └─────
     Single transition    Single transition

Real Switch Behavior (Bounce):
    Press                Release
     ↓                    ↓
─┘─┘─┘                    └─└─└─
 Multiple transitions     Multiple transitions
```

## Circuit Diagram

```
Micro Switch Connection:

    3.3V ──┐
           │
          ╱ │ 10kΩ (internal pull-up)
           │
    GPIO17 ├────────┤ │──── GND
           │         ↓
           │    Micro Switch
           │
    GPIO18 ├──[220Ω]──┤►├─── GND
                      LED
                   (optional)

Switch States:
- Not Pressed: GPIO reads HIGH (3.3V via pull-up)
- Pressed: GPIO reads LOW (connected to GND)
```

## Pin Connections

| Component | GPIO Pin | Purpose |
|-----------|----------|---------|
| Micro Switch | GPIO17 | Input with pull-up |
| LED Anode | GPIO18 | Visual feedback |
| LED Cathode | GND | Ground |
| Switch Terminal 1 | GPIO17 | Signal |
| Switch Terminal 2 | GND | Ground |

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
cd ~/raspberry-projects/examples/05-input-controllers/02-micro-switch

# Run the micro switch examples
python3 micro-switch.py

# Run specific demos directly
make run        # Interactive menu
make test       # Test switch detection
make counter    # Count button presses
make game       # Reaction time game
```

## Code Walkthrough

### Basic Switch Detection

1. **Setup with Pull-up**
   ```python
   from gpiozero import Button
   
   # Create button with internal pull-up and debouncing
   switch = Button(17, bounce_time=0.01)
   ```

2. **Polling Method**
   ```python
   while True:
       if switch.is_pressed:
           print("Pressed")
           switch.wait_for_release()
           print("Released")
   ```

3. **Event-Driven Method**
   ```python
   def button_pressed():
       print("Button pressed!")
   
   switch.when_pressed = button_pressed
   signal.pause()  # Wait for events
   ```

## Key Concepts

### Debouncing

Debouncing prevents multiple detections from mechanical bounce:

```python
# Hardware debounce: Add capacitor
# Software debounce: Use bounce_time parameter
Button(pin, bounce_time=0.01)  # 10ms debounce
```

### Pull-up Resistors

```
Why Pull-ups?
- Define default state (HIGH)
- Prevent floating input
- Provide current path

Internal vs External:
- Internal: Convenient, ~50kΩ
- External: Customizable, typically 10kΩ
```

### Event Detection Methods

| Method | Use Case | CPU Usage |
|--------|----------|------------|
| Polling | Simple programs | Higher |
| Events | Complex programs | Lower |
| Interrupts | Time-critical | Lowest |

## Common Applications

### 1. User Interface
- Menu navigation
- Mode selection
- Parameter adjustment
- Reset buttons

### 2. Limit Switches
- End stops for motors
- Door open/close detection
- Position sensing
- Safety switches

### 3. Counting Applications
- Event counting
- People counting
- Production counting
- Score keeping

### 4. Trigger Systems
- Camera shutter
- Data logging start/stop
- Alarm activation
- Process control

## Advanced Techniques

### Multiple Button Handling
```python
buttons = {
    'up': Button(17),
    'down': Button(27),
    'select': Button(22)
}

# Check which button was pressed
for name, button in buttons.items():
    if button.is_pressed:
        print(f"{name} pressed")
```

### Long Press Detection
```python
def check_long_press():
    if switch.is_pressed:
        start = time.time()
        switch.wait_for_release()
        duration = time.time() - start
        
        if duration > 2.0:
            print("Long press detected")
        else:
            print("Short press")
```

### Double Click Detection
```python
last_press_time = 0
DOUBLE_CLICK_TIME = 0.5

def detect_double_click():
    global last_press_time
    current_time = time.time()
    
    if current_time - last_press_time < DOUBLE_CLICK_TIME:
        print("Double click!")
        last_press_time = 0
    else:
        last_press_time = current_time
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Multiple detections per press | Increase bounce_time parameter |
| Switch not detected | Check wiring, verify pull-up resistor |
| Inconsistent behavior | Clean switch contacts, check connections |
| Always reads pressed | Check for short circuit to ground |
| Always reads not pressed | Verify pull-up resistor connection |

## Morse Code Implementation

The example includes a Morse code input system:

```python
# Short press = dot (.)
# Long press = dash (-)

Morse patterns:
A: .-    N: -.
B: -...  O: ---
C: -.-.  P: .--.
# ... etc
```

## Performance Considerations

### Response Time
- Human reaction: ~200-300ms
- Debounce time: 10-50ms
- GPIO read time: <1ms
- Total latency: ~10-50ms

### CPU Usage
```python
# High CPU (avoid):
while True:
    if switch.is_pressed:
        do_something()

# Low CPU (preferred):
switch.when_pressed = do_something
signal.pause()
```

## Project Ideas

1. **Digital Door Bell**
   - Play different tones
   - Log visitor times
   - Send notifications

2. **Quiz Buzzer System**
   - Multiple player buttons
   - First-press detection
   - Score tracking

3. **Morse Code Trainer**
   - Input practice
   - Decode messages
   - Speed adjustment

4. **Simple Game Controller**
   - Multiple buttons
   - Combination detection
   - Action mapping

5. **Industrial Counter**
   - Production counting
   - Rate calculation
   - Data logging

## Integration Examples

### With LCD Display
```python
# Show button press count on LCD
def update_display():
    lcd.clear()
    lcd.message = f"Count: {press_count}"

switch.when_pressed = lambda: [
    increment_counter(),
    update_display()
]
```

### With LED Patterns
```python
# Different LED patterns for press types
def handle_press():
    duration = measure_press_duration()
    
    if duration < 0.5:
        led.blink(0.1, 0.1, n=3)  # Short
    else:
        led.pulse()  # Long
```

### With Network
```python
# Send button press over network
import requests

def send_button_event():
    data = {'event': 'button_press', 'time': time.time()}
    requests.post('http://server/api/button', json=data)

switch.when_pressed = send_button_event
```

## Best Practices

1. **Always use debouncing** for mechanical switches
2. **Use internal pull-ups** when possible
3. **Handle cleanup** in signal handlers
4. **Consider power consumption** for battery projects
5. **Document expected behavior** for users
6. **Test edge cases** (rapid pressing, holding)

## Next Steps

After mastering micro switches:
1. Explore touch switches for modern interfaces
2. Try slide switches for state selection
3. Use rotary encoders for value adjustment
4. Combine multiple inputs for complex controls
5. Build complete user interface systems

## Resources

- [GPIO Zero Button](https://gpiozero.readthedocs.io/en/stable/api_input.html#button)
- [Switch Debouncing](https://www.ganssle.com/debouncing.htm)
- [Pull-up Resistors](https://learn.sparkfun.com/tutorials/pull-up-resistors)
- [Morse Code Reference](https://morsecode.world/international/morse2.html)