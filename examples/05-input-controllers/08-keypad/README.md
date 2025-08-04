# Project 05-08: Matrix Keypad - Multi-Button Input Interface

Master matrix scanning techniques for efficient multi-button input using a 4x4 keypad.

## What You'll Learn

- Matrix keypad scanning principles
- Row-column multiplexing
- Software debouncing techniques
- Multi-key detection
- Security code implementation
- Event-driven keypad interfaces

## Hardware Requirements

- Raspberry Pi 5
- 1x 4x4 Matrix Keypad (or 3x4)
- 8x Jumper wires (4 rows + 4 columns)
- Optional: LEDs and buzzer for feedback
- Breadboard (optional)

## Circuit Diagram

```
4x4 Matrix Keypad Internal Connections:
     C1  C2  C3  C4
    ┌───┬───┬───┬───┐
R1 ─┤ 1 │ 2 │ 3 │ A │
    ├───┼───┼───┼───┤
R2 ─┤ 4 │ 5 │ 6 │ B │
    ├───┼───┼───┼───┤
R3 ─┤ 7 │ 8 │ 9 │ C │
    ├───┼───┼───┼───┤
R4 ─┤ * │ 0 │ # │ D │
    └───┴───┴───┴───┘

GPIO Connections:
Rows (Outputs):          Columns (Inputs with pull-up):
R1 ---- GPIO18 (Pin 12)  C1 ---- GPIO10 (Pin 19)
R2 ---- GPIO23 (Pin 16)  C2 ---- GPIO22 (Pin 15)
R3 ---- GPIO24 (Pin 18)  C3 ---- GPIO27 (Pin 13)
R4 ---- GPIO25 (Pin 22)  C4 ---- GPIO17 (Pin 11)

Optional Lock System:
Green LED --- GPIO5 (Pin 29) - Access granted
Red LED ----- GPIO6 (Pin 31) - Access denied
Buzzer ------ GPIO13 (Pin 33) - Feedback
Lock -------- GPIO19 (Pin 35) - Door lock control
```

## Pin Connections

| Keypad Pin | GPIO Pin | Type | Notes |
|------------|----------|------|-------|
| Row 1 | GPIO18 | Output | Scan line |
| Row 2 | GPIO23 | Output | Scan line |
| Row 3 | GPIO24 | Output | Scan line |
| Row 4 | GPIO25 | Output | Scan line |
| Col 1 | GPIO10 | Input | Pull-up enabled |
| Col 2 | GPIO22 | Input | Pull-up enabled |
| Col 3 | GPIO27 | Input | Pull-up enabled |
| Col 4 | GPIO17 | Input | Pull-up enabled |

## How Matrix Keypads Work

### Matrix Structure
- 16 keys arranged in 4×4 grid
- Only 8 connections needed (4+4) instead of 16
- Each key connects one row to one column

### Scanning Process
1. Set all rows HIGH (inactive)
2. Set one row LOW (active)
3. Read all column states
4. If column is LOW, key at [row,col] is pressed
5. Repeat for all rows

### Key Detection
```
Row 2 LOW, Column 3 LOW = Key '6' pressed
(Row 2, Column 3) → KEYS[1][2] → '6'
```

## Software Dependencies

```bash
# Update package list
sudo apt update

# Install Python GPIO Zero
sudo apt install -y python3-gpiozero

# For secure storage (optional)
pip3 install cryptography
```

## Running the Programs

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/05-input-controllers/08-keypad

# Run the keypad scanner with demos
python3 keypad-scanner.py

# Or run the security lock system
python3 keypad-lock.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Scanner (keypad-scanner.py)

1. **Matrix Scanning**
   ```python
   for row in rows:
       row.on()  # Activate row
       for col in cols:
           if not col.is_active:  # Check column
               key_pressed = keys[row][col]
   ```

2. **Debouncing**
   - Detect key press on transition
   - Ignore key while held
   - Detect key release

3. **Multiple Demos**
   - Basic scanner
   - Password entry
   - Calculator
   - Phone dialer

### Security Lock (keypad-lock.py)

1. **Access Control**
   - Multiple user codes
   - Master code for admin
   - Failed attempt tracking
   - Lockout after failures

2. **Security Features**
   - Code hashing
   - Access logging
   - Timeout protection
   - Admin functions

## Key Concepts

### Pull-up Resistors
- Column pins use internal pull-ups
- Default state: HIGH (3.3V)
- Pressed key: pulls column LOW

### Debouncing
- Mechanical switches "bounce"
- Multiple readings per press
- Software filtering required

### Security Considerations
1. **Never store plain text passwords**
2. **Implement attempt limits**
3. **Add time delays after failures**
4. **Log all access attempts**
5. **Use secure code generation**

## Common Keypad Types

### 4×4 Keypad (16 keys)
- Numbers 0-9
- Letters A-D
- Symbols * and #
- Most common type

### 3×4 Keypad (12 keys)
- Numbers 0-9
- Symbols * and #
- Simpler, phone-style

### Custom Layouts
- Membrane keypads
- Mechanical keypads
- Capacitive touch

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No keys detected | Check row/column connections |
| Wrong keys detected | Verify pin mapping matches code |
| Multiple keys detected | Check for shorts between pins |
| Intermittent detection | Clean keypad contacts |
| Keys stuck | Mechanical issue with keypad |

## Advanced Features

### Multi-Key Detection
```python
def scan_all_keys():
    pressed_keys = []
    for row_num, row in enumerate(rows):
        row.on()
        for col_num, col in enumerate(cols):
            if not col.is_active:
                pressed_keys.append(keys[row_num][col_num])
        row.off()
    return pressed_keys
```

### Key Hold Detection
```python
if key and time.time() - key_down_time > HOLD_TIME:
    return (key, True)  # Key is being held
```

### Custom Key Mapping
```python
# Phone-style letters
PHONE_KEYS = {
    '2': 'ABC', '3': 'DEF', '4': 'GHI',
    '5': 'JKL', '6': 'MNO', '7': 'PQRS',
    '8': 'TUV', '9': 'WXYZ'
}
```

## Project Applications

1. **Door Lock System**
   - Access codes
   - User management
   - Entry logging
   - Temporary codes

2. **Calculator**
   - Basic arithmetic
   - Memory functions
   - Scientific modes

3. **Phone Interface**
   - Number entry
   - Contact shortcuts
   - Speed dial

4. **Menu Navigation**
   - Settings control
   - Parameter input
   - Mode selection

5. **Game Controller**
   - D-pad functionality
   - Action buttons
   - Combo detection

## Security Best Practices

### Code Storage
```python
# Use hashing for codes
import hashlib
hashed = hashlib.sha256(code.encode()).hexdigest()
```

### Brute Force Protection
```python
# Exponential backoff
lockout_time = 30 * (2 ** failed_attempts)
```

### Secure Code Generation
```python
import secrets
new_code = ''.join(secrets.choice('0123456789') for _ in range(6))
```

## Performance Optimization

### Scan Rate
- Balance between responsiveness and CPU usage
- Typical: 20-50 scans per second
- Add sleep(0.02) in main loop

### Interrupt-Driven Scanning
- Use column pins as interrupts
- Scan only when key pressed
- More efficient for battery operation

## Integration Examples

### With LCD Display
```python
lcd.write_line("Enter Code:", 0)
lcd.write_line("*" * len(entered_code), 1)
```

### With RFID
```python
# Dual authentication
if rfid_valid and keypad_code_valid:
    grant_access()
```

### With Network
```python
# Remote code management
def update_codes_from_server():
    response = requests.get(SERVER_URL)
    new_codes = response.json()
```

## Keypad Maintenance

1. **Cleaning**
   - Use isopropyl alcohol
   - Clean between keys
   - Check for debris

2. **Contact Enhancement**
   - Conductive pen for traces
   - Replace worn membranes
   - Check solder joints

3. **Testing**
   - Continuity test each key
   - Measure contact resistance
   - Check for ghosting

## Next Steps

After mastering keypads:
1. Build complete security system
2. Add biometric authentication
3. Implement wireless keypads
4. Create custom protocols
5. Design PCB interfaces

## Common Applications

- Security systems
- Industrial control panels
- Vending machines
- ATM interfaces
- Access control
- Home automation
- Musical instruments
- Gaming devices

## Resources

- [Matrix Keypad Theory](https://www.circuitbasics.com/how-to-set-up-a-keypad-on-an-arduino/)
- [Keypad Scanning Techniques](https://www.embeddedrelated.com/showarticle/519.php)
- [Security Best Practices](https://owasp.org/www-project-iot-security/)
- [Membrane Keypad Design](https://www.allaboutcircuits.com/projects/use-a-keypad-with-your-arduino/)