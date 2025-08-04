# Project 02-02: RGB LED - Color Mixing with PWM

Learn to control RGB LEDs and create millions of colors using Pulse Width Modulation (PWM) on Raspberry Pi 5.

## What You'll Learn

- RGB color theory and mixing
- PWM (Pulse Width Modulation) control
- Using the RGBLED class in GPIO Zero
- Color transitions and effects
- Common cathode vs common anode LEDs
- Creating custom colors programmatically

## Hardware Requirements

- Raspberry Pi 5
- 1x RGB LED (common cathode)
- 3x 220Ω resistors
- 4x Jumper wires
- Breadboard
- GPIO Extension Board (optional but recommended)

## Circuit Diagram

```
RGB LED Pinout (Common Cathode):
    R G C B
    | | | |
    1 2 3 4

Pin connections:
1. Red Anode    → 220Ω → GPIO17
2. Green Anode  → 220Ω → GPIO18  
3. Common Cathode → GND
4. Blue Anode   → 220Ω → GPIO27

ASCII Circuit:
GPIO17 ----[220Ω]----R|
GPIO18 ----[220Ω]----G|--RGB LED
GPIO27 ----[220Ω]----B|
                  GND-C|
```

## Pin Connections

| RGB LED Pin | Connection | GPIO Pin | Notes |
|-------------|------------|----------|-------|
| Red (R) | Through 220Ω | GPIO17 (Pin 11) | Red channel |
| Green (G) | Through 220Ω | GPIO18 (Pin 12) | Green channel |
| Blue (B) | Through 220Ω | GPIO27 (Pin 13) | Blue channel |
| Common (-) | Direct to GND | GND | Longest pin |

## RGB LED Types

### Common Cathode (Used Here)
- Longest pin connects to GND
- Apply positive voltage to color pins
- More common in hobbyist kits

### Common Anode
- Longest pin connects to 3.3V
- Apply ground to color pins
- Requires `active_high=False` in code

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero library
sudo apt install python3-gpiozero
```

## Running the Program

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/02-output-displays/02-rgb-led

# Run the automatic color demo
python3 rgb-led.py

# Or try the interactive version
python3 rgb-led-interactive.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Color Control (rgb-led.py)

1. **RGB LED Initialization**
   ```python
   led = RGBLED(red=RED_PIN, green=GREEN_PIN, blue=BLUE_PIN)
   ```
   - Creates RGBLED object with three PWM channels
   - Automatically handles PWM frequency

2. **Setting Colors**
   ```python
   led.color = (1, 0, 0)  # Red
   led.color = (0, 1, 0)  # Green
   led.color = (0, 0, 1)  # Blue
   ```
   - Values range from 0 (off) to 1 (full brightness)
   - Mix values for custom colors

3. **Color Transitions**
   ```python
   for i in range(101):
       led.color = (1 - i/100, i/100, 0)
   ```
   - Smooth fade between colors
   - Creates gradient effects

### Interactive Control (rgb-led-interactive.py)

1. **Preset Colors**
   - Quick access to common colors
   - Numbered menu for easy selection

2. **Custom Colors**
   - Input RGB values (0-100)
   - Real-time color preview

3. **Effects**
   - Pulse: Fade in/out
   - Blink: On/off pattern
   - Rainbow: Continuous color cycle

## Key Concepts

### Color Mixing Theory

| Color | Red | Green | Blue | Hex |
|-------|-----|-------|------|-----|
| Red | 100% | 0% | 0% | #FF0000 |
| Green | 0% | 100% | 0% | #00FF00 |
| Blue | 0% | 0% | 100% | #0000FF |
| Yellow | 100% | 100% | 0% | #FFFF00 |
| Cyan | 0% | 100% | 100% | #00FFFF |
| Magenta | 100% | 0% | 100% | #FF00FF |
| White | 100% | 100% | 100% | #FFFFFF |
| Orange | 100% | 50% | 0% | #FF8000 |
| Purple | 50% | 0% | 50% | #800080 |

### PWM (Pulse Width Modulation)
- **Principle**: Rapidly switch LED on/off
- **Duty Cycle**: Percentage of time ON
- **Frequency**: How fast it switches (typically 100Hz+)
- **Result**: Appears dimmed to human eye

### Current Limiting
- Each color channel needs its own resistor
- 220Ω suitable for 3.3V GPIO
- Protects both LED and Raspberry Pi

## Common Color Formulas

```python
# Warm white (reduces blue)
led.color = (1, 0.8, 0.6)

# Cool white (more blue)
led.color = (0.9, 0.9, 1)

# Sunrise orange
led.color = (1, 0.4, 0.1)

# Sky blue
led.color = (0.5, 0.8, 1)

# Pink
led.color = (1, 0.7, 0.8)
```

## Variations to Try

1. **Breathing Effect**
   ```python
   led.pulse(fade_in_time=2, fade_out_time=2)
   ```

2. **Color Temperature**
   - Simulate sunrise/sunset
   - Warm to cool white transitions

3. **Music Reactive**
   - Change colors based on sound input
   - Create light shows

4. **Status Indicator**
   - Green = OK
   - Yellow = Warning
   - Red = Error

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Wrong colors | Check pin connections, verify RGB order |
| Dim colors | Check resistor values (220Ω, not 2.2kΩ) |
| No blue/red/green | Test individual channels, check connections |
| Flickering | Ensure solid connections, check power supply |
| All colors dim | Common pin might be on wrong rail |

## Advanced Topics

### Common Anode RGB LED
```python
# For common anode, invert the logic
led = RGBLED(red=17, green=18, blue=27, active_high=False)
```

### Custom PWM Frequency
```python
# Higher frequency for video recording
led = RGBLED(17, 18, 27, pwm_frequency=1000)
```

### Gamma Correction
```python
# Correct for human eye perception
def gamma_correct(value, gamma=2.2):
    return pow(value, gamma)
```

## Project Ideas

1. **Mood Lamp**
   - Slow color transitions
   - Adjustable speed and colors

2. **Weather Indicator**
   - Blue = Cold
   - Green = Nice
   - Red = Hot

3. **Notification Light**
   - Different colors for different alerts
   - Pulse patterns for urgency

4. **Game Status**
   - Health indicator (green to red)
   - Power-ups (flashing colors)

## Understanding PWM Values

### Brightness Perception
- Human eyes don't perceive brightness linearly
- 50% PWM ≠ 50% perceived brightness
- Use gamma correction for natural dimming

### Color Depth
- 8-bit per channel = 256 levels
- Total colors = 256³ = 16,777,216
- GPIO Zero uses float (0-1) for flexibility

## Next Steps

After mastering RGB LEDs:
1. Try Project 02-03: LED Bar Graph for multiple LED control
2. Explore Project 03-02: Passive Buzzer for sound + light
3. Build mood lighting projects
4. Create interactive color games

## Resources

- [GPIO Zero RGBLED Documentation](https://gpiozero.readthedocs.io/en/stable/api_output.html#rgbled)
- [PWM Explanation](https://learn.sparkfun.com/tutorials/pulse-width-modulation)
- [Color Theory Basics](https://www.colormatters.com/color-and-design/basic-color-theory)
- [RGB Color Picker](https://www.w3schools.com/colors/colors_picker.asp)