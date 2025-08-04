# Project 02-01: Blinking LED - Basic GPIO Output Control

Your first LED control project demonstrating fundamental GPIO output operations using Python and the gpiozero library.

## What You'll Learn

- Setting up GPIO pins as outputs
- Controlling LED states (on/off)
- Basic timing control with sleep()
- Clean signal handling for program exit
- GPIO Zero library fundamentals
- Current limiting with resistors

## Hardware Requirements

- Raspberry Pi 5
- 1x LED (any color)
- 1x 220Ω resistor (red-red-brown)
- 2x Jumper wires
- Breadboard
- GPIO Extension Board (optional but recommended)

## Circuit Diagram

```
Raspberry Pi GPIO          Breadboard Circuit
                          
GPIO17 (Pin 11) --------- [220Ω] ----- LED(+) ----- LED(-) ----- GND
                          Resistor      Anode        Cathode
                                       (long leg)   (short leg)

Alternative ASCII diagram:
    GPIO17 ----[220Ω]----►|---- GND
                         LED
```

## Pin Connections

| Component | Pin/Connection | Notes |
|-----------|---------------|-------|
| LED Anode (+) | Through 220Ω to GPIO17 | Longer leg of LED |
| LED Cathode (-) | GND | Shorter leg of LED |
| Resistor | Between GPIO17 and LED | Current limiting |

## Software Dependencies

Install on your Raspberry Pi:
```bash
# Update package list
sudo apt update

# Install Python GPIO Zero library
sudo apt install python3-gpiozero
```

## Running the Program

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/02-output-displays/01-blinking-led

# Run the program
python3 blinking-led.py

# To stop, press Ctrl+C
```

## Code Walkthrough

The program demonstrates:

1. **GPIO Initialization**
   ```python
   led = LED(LED_PIN)
   ```
   - Creates an LED object on GPIO17
   - Automatically configures pin as output

2. **LED Control**
   ```python
   led.on()   # Turn LED on
   led.off()  # Turn LED off
   ```
   - Simple, intuitive control methods
   - No need for manual HIGH/LOW states

3. **Main Loop**
   - Alternates LED state every 0.5 seconds
   - Prints status to console
   - Continues until interrupted

4. **Clean Exit**
   - Signal handler catches Ctrl+C
   - Ensures graceful program termination
   - GPIO Zero automatically cleans up on exit

## Key Concepts

### Current Limiting Resistor
- **Purpose**: Protects LED from excessive current
- **Calculation**: R = (Vsupply - Vled) / Iled
- **Example**: (3.3V - 2.0V) / 0.02A = 65Ω minimum
- **We use 220Ω**: Safe for all LED colors

### LED Polarity
- **Anode (+)**: Longer leg, connects to positive
- **Cathode (-)**: Shorter leg, flat side, connects to ground
- **Mnemonic**: "Add" more length to Anode

### GPIO Zero Advantages
- Automatic pin configuration
- Built-in cleanup on program exit
- Intuitive method names
- Works great with Raspberry Pi 5's RP1 chip

## Variations to Try

1. **Change Blink Rate**
   - Modify sleep values for faster/slower blinking
   - Try asymmetric timing (on longer than off)

2. **Multiple LEDs**
   - Add more LEDs on different GPIO pins
   - Create patterns or sequences

3. **Brightness Control**
   - Use PWMLED instead of LED for brightness control
   - Fade in/out effects

## Troubleshooting

| Problem | Solution |
|---------|----------|
| LED doesn't light | Check polarity - long leg to positive |
| Permission denied | Run with `python3` (not sudo on Pi 5) |
| No module named 'gpiozero' | Install with `sudo apt install python3-gpiozero` |
| LED very dim | Check resistor value (should be 220Ω, not 2.2kΩ) |
| LED always on | Check connections, ensure good ground connection |

## Understanding the Code

### Why 0.5 seconds?
- Fast enough to see clear blinking
- Slow enough to observe state changes
- Standard for testing and demos

### Why GPIO17?
- Conveniently located on pin header
- No special functions that might interfere
- Standard choice in many tutorials

## Next Steps

Once you've mastered basic LED control:
1. Try Project 02-02: RGB LED for color mixing
2. Explore PWM for brightness control
3. Create LED patterns and sequences
4. Move on to button input control

## Resources

- [GPIO Zero Documentation](https://gpiozero.readthedocs.io/)
- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [LED Current Calculations](https://www.electronics-tutorials.ws/diode/diode_8.html)