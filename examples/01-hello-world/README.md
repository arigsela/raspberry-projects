# Project 01: Hello World - Basic GPIO Control

Your first Raspberry Pi 5 project demonstrating basic GPIO input/output operations using Python.

## What You'll Learn

- Setting up GPIO pins as inputs and outputs
- Reading button states with pull-up resistors
- Controlling LEDs
- Python GPIO programming with gpiod library
- Event detection and handling
- Clean code structure with proper error handling

## Hardware Requirements

- Raspberry Pi 5
- 1x LED (any color)
- 1x 330Ω resistor (for LED)
- 1x Push button
- Jumper wires
- Breadboard

## Circuit Diagram

```
GPIO17 (Pin 11) ----[330Ω]----[LED]---- GND
                               (+) (-)

GPIO27 (Pin 13) ----[Button]---- GND
                 (Internal pull-up enabled)
```

## Software Dependencies

Install on your Raspberry Pi:
```bash
sudo apt update
sudo apt install python3-pip python3-gpiod
pip3 install gpiod

# Or use the Makefile:
make deps
```

## Running the Program

```bash
# Run using make (recommended)
make run

# Or run directly:
sudo python3 hello-world.py
```

## Code Walkthrough

The program demonstrates:

1. **GPIO Initialization**
   - Opens the GPIO chip (`gpiochip4` on Pi 5)
   - Configures pins for input/output

2. **Main Loop**
   - Continuously reads button state
   - Controls LED based on button press
   - Implements basic debouncing

3. **Cleanup**
   - Proper resource deallocation
   - Signal handling for graceful exit (Ctrl+C)

## Key Concepts

- **gpiod Library**: Modern GPIO control that works with Pi 5's new RP1 chip
- **Pull-up Resistors**: Configured in software using LINE_REQ_FLAG_BIAS_PULL_UP
- **Event Loop**: Polling-based with small sleep to prevent CPU spinning
- **Clean Resource Management**: Proper cleanup using try/except and signal handlers

## Troubleshooting

- **Permission Denied**: Run with `sudo` or add user to `gpio` group
- **"gpiochip4" not found**: Ensure you're on Pi 5 (Pi 4 uses different chip names)
- **LED doesn't light**: Check polarity - longer leg is positive

## Next Steps

Once comfortable with this example, move to Project 02 (gpio-interrupts) to learn event-driven GPIO programming.