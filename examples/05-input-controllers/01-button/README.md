# Project 05-01: Button-Controlled LED - Basic GPIO Input/Output

Learn to read button states and control outputs with event-driven programming on Raspberry Pi 5.

## What You'll Learn

- Reading digital input from buttons
- Controlling outputs based on inputs
- Event-driven programming with callbacks
- Pull-up resistor configuration
- Debouncing in GPIO Zero
- Polling vs. event-driven approaches

## Hardware Requirements

- Raspberry Pi 5
- 1x Push button (momentary switch)
- 1x LED (any color)
- 1x 220Ω resistor (for LED)
- 4x Jumper wires
- Breadboard
- GPIO Extension Board (optional but recommended)

## Circuit Diagram

```
Button Circuit:
GPIO18 (Pin 12) ----[Button]---- GND
                 (Internal pull-up enabled)

LED Circuit:
GPIO17 (Pin 11) ----[220Ω]----[LED+]----[LED-]---- GND

Combined ASCII diagram:
    GPIO18 ----[Button]---- GND
                  |
                  ↓ (controls)
    GPIO17 ----[220Ω]----►|---- GND
                         LED
```

## Pin Connections

| Component | Pin/Connection | Notes |
|-----------|---------------|-------|
| Button Side 1 | GPIO18 (Pin 12) | Either side works |
| Button Side 2 | GND | Opposite corner from Side 1 |
| LED Anode (+) | Through 220Ω to GPIO17 | Longer leg |
| LED Cathode (-) | GND | Shorter leg |

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero library (usually pre-installed)
sudo apt install python3-gpiozero
```

## Running the Program

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/05-input-controllers/01-button

# Run the event-driven version (recommended)
python3 button-led.py

# Or try the polling version
python3 button-polling.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Event-Driven Approach (button-led.py)

1. **Component Initialization**
   ```python
   led = LED(LED_PIN)
   button = Button(BUTTON_PIN)
   ```
   - LED configured as output
   - Button configured with internal pull-up

2. **Event Binding**
   ```python
   button.when_pressed = led.on
   button.when_released = led.off
   ```
   - Directly bind LED methods to button events
   - Clean, efficient, no polling needed

3. **Custom Callbacks**
   ```python
   def button_pressed():
       led.on()
       print("Button pressed - LED ON")
   ```
   - Add custom actions beyond LED control
   - Useful for debugging and complex logic

### Polling Approach (button-polling.py)

1. **State Tracking**
   ```python
   last_state = False
   current_state = button.is_pressed
   ```
   - Manually track button state changes
   - Detect transitions, not just states

2. **Continuous Checking**
   ```python
   while True:
       if current_state != last_state:
           # Handle state change
   ```
   - Check button state in a loop
   - Less efficient but sometimes necessary

## Key Concepts

### Pull-up Resistors
- **Internal Pull-up**: GPIO Zero enables by default
- **Purpose**: Ensures defined state when button not pressed
- **Logic**: Button pressed = LOW (0V), Released = HIGH (3.3V)

### Button Debouncing
- **Hardware Issue**: Mechanical contacts "bounce"
- **Software Solution**: GPIO Zero handles automatically
- **Default**: 100ms debounce time
- **Custom**: `Button(pin, bounce_time=0.2)`

### Event-Driven vs Polling

| Aspect | Event-Driven | Polling |
|--------|--------------|---------|
| CPU Usage | Low | Higher |
| Response Time | Immediate | Depends on sleep |
| Code Complexity | Simple | More complex |
| Best For | Most cases | Special requirements |

## Common Button Types

1. **Momentary Push Button** (Used here)
   - Returns to original state when released
   - Most common for user input

2. **Latching Button**
   - Stays in position until pressed again
   - Good for power switches

3. **Tactile Button**
   - Provides physical feedback
   - Popular in keyboards

## Variations to Try

1. **Toggle Mode**
   ```python
   # Press to toggle LED state
   button.when_pressed = led.toggle
   ```

2. **Hold Detection**
   ```python
   # Different actions for short/long press
   if button.is_held:
       led.blink()
   ```

3. **Multiple Buttons**
   - Control different LEDs
   - Implement button combinations

## Troubleshooting

| Problem | Solution |
|---------|----------|
| LED always on | Check button wiring, test with multimeter |
| No response | Verify GPIO pins, check connections |
| Erratic behavior | Button may be faulty, try another |
| LED flickers | Debounce issue, increase bounce_time |
| Permission error | Run with python3, not sudo |

## Advanced Topics

### Custom Debouncing
```python
button = Button(18, bounce_time=0.1)  # 100ms debounce
```

### Hold Time Detection
```python
button = Button(18, hold_time=2)  # 2 second hold
button.when_held = special_function
```

### Pull-up/Pull-down Control
```python
button = Button(18, pull_up=True)   # Explicit pull-up
button = Button(18, pull_up=False)  # External pull-up
```

## Project Extensions

1. **Multi-Color Control**
   - Use RGB LED with multiple buttons
   - Each button controls different color

2. **Pattern Generator**
   - Multiple buttons create LED patterns
   - Record and playback sequences

3. **Reaction Game**
   - LED turns on randomly
   - Measure button press time

## Next Steps

After mastering button input:
1. Try Project 02-02: RGB LED for color control
2. Explore Project 05-06: Rotary Encoder for analog-style input
3. Build Project 05-08: Keypad for multiple inputs
4. Combine with sensors for interactive projects

## Code Comparison

### Why Events Over Polling?
- **Power Efficiency**: CPU sleeps between events
- **Responsiveness**: Instant reaction to button press
- **Cleaner Code**: No manual state tracking
- **Scalability**: Easy to add more buttons

### When to Use Polling?
- Integration with existing loops
- Complex state machines
- Non-standard timing requirements
- Learning/debugging purposes

## Resources

- [GPIO Zero Button Documentation](https://gpiozero.readthedocs.io/en/stable/api_input.html#button)
- [Pull-up Resistor Explanation](https://learn.sparkfun.com/tutorials/pull-up-resistors)
- [Debouncing Guide](https://www.allaboutcircuits.com/technical-articles/switch-bounce-how-to-deal-with-it/)