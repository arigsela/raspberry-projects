# Project 02: GPIO Interrupts - Event-Driven Programming

Advanced GPIO example demonstrating interrupt-style event detection on Raspberry Pi 5 using Python.

## What You'll Learn

- Event-driven GPIO programming (similar to interrupts)
- Edge detection (rising/falling edges)
- Monitoring multiple GPIO inputs simultaneously
- Non-blocking I/O with select()
- Using file descriptors for GPIO events
- Proper timestamp handling

## Hardware Requirements

- Raspberry Pi 5
- 1x LED (any color)
- 1x 330Ω resistor (for LED)
- 2x Push buttons
- Jumper wires
- Breadboard

## Circuit Diagram

```
GPIO17 (Pin 11) ----[330Ω]----[LED]---- GND

GPIO27 (Pin 13) ----[Button 1]---- GND
GPIO22 (Pin 15) ----[Button 2]---- GND

(Both buttons use internal pull-ups)
```

## Key Differences from Basic Example

| Feature | Project 01 (Polling) | Project 02 (Events) |
|---------|---------------------|---------------------|
| CPU Usage | Higher (continuous loop) | Lower (event-driven) |
| Response Time | Depends on loop delay | Immediate |
| Multiple Inputs | Sequential checking | Simultaneous monitoring |
| Code Complexity | Simple | More advanced |

## Software Dependencies

```bash
# Install dependencies
make deps
# Or manually:
sudo apt install python3-pip python3-gpiod
pip3 install gpiod
```

## Running the Program

```bash
# Run the program
make run

# Or directly:
sudo python3 gpio-interrupts.py

# Check code quality (optional)
make lint
```

## Code Highlights

### Event Detection Setup
```python
# Configure for both edge detection (press and release)
button_line.request(consumer="gpio-interrupts",
                   type=gpiod.LINE_REQ_EV_BOTH_EDGES,
                   flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
```

### Event Waiting with select()
```python
# Wait for events on multiple file descriptors
readable, _, _ = select.select([button1_fd, button2_fd], [], [], 0.1)
```

### Event Handling
```python
# Read event with timestamp
event = button_line.event_read()
timestamp = event.timestamp  # Hardware timestamp in nanoseconds
```

## Advanced Concepts Demonstrated

1. **File Descriptors**: Linux treats GPIO events as file events
2. **select() System Call**: Monitor multiple inputs simultaneously
3. **Hardware Timestamps**: Nanosecond precision event timing
4. **Edge Types**: Rising (release) and falling (press) detection
5. **Clean Architecture**: Separation of concerns with event handlers

## Performance Considerations

- Event-driven approach uses less CPU than polling
- Linux kernel handles the low-level interrupt management
- Suitable for most applications except hard real-time
- For microsecond-precision timing, consider Raspberry Pi Pico

## Extending This Example

Ideas for enhancement:
- Add debouncing logic using timestamps
- Implement long-press detection
- Create a state machine for complex button sequences
- Add PWM LED control for visual feedback
- Log events to a file with timestamps

## Troubleshooting

- **No events detected**: Check wiring and pull-up configuration
- **Multiple events per press**: Add software debouncing
- **High CPU usage**: Ensure using event wait, not busy polling

## Next Steps

This example provides a foundation for:
- Interrupt-driven sensor reading
- Real-time data acquisition
- Complex user interfaces
- Event logging systems