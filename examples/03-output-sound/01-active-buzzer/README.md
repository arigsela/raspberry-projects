# Project 03-01: Active Buzzer - Simple Sound Output

Generate alerts, alarms, and notification sounds using an active buzzer for audio feedback in your projects.

## What You'll Learn

- Active vs passive buzzer differences
- Basic sound generation
- Alarm and notification patterns
- Morse code implementation
- Timer and alert systems
- Interactive sound triggers

## Hardware Requirements

- Raspberry Pi 5
- 1x Active buzzer (5V)
- Optional: 1x Push button
- Optional: 1x NPN transistor (2N2222) for louder sound
- Jumper wires
- Breadboard

## Active vs Passive Buzzers

| Feature | Active Buzzer | Passive Buzzer |
|---------|---------------|----------------|
| Built-in oscillator | Yes | No |
| Voltage | Apply DC voltage | Requires PWM signal |
| Sound variety | Single tone | Multiple tones |
| Ease of use | Very simple | More complex |
| Cost | Slightly higher | Lower |
| Current draw | ~30mA | ~10-20mA |

### How to Identify
- **Active**: Has internal circuit (taller), makes sound with DC
- **Passive**: Looks like a speaker, requires frequency signal

## Circuit Diagram

```
Basic Active Buzzer Connection:

    Active Buzzer
    ┌─────────┐
    │    +    │ (Longer leg/Red wire)
    │  BUZZ   │
    │    -    │ (Shorter leg/Black wire)
    └────┬────┘
         │
         ├──── GPIO17 (Pin 11)
         │
         └──── GND (Pin 6)

With Transistor for Higher Volume (Optional):

    5V (Pin 2) ────┬──── Buzzer (+)
                   │
                   │     Buzzer (-)
                   │         │
                   └─────────┤
                            │├─ 2N2222 (Collector)
                            ─┤
                            │├─ 2N2222 (Base)
                             │
                   GPIO17 ───┴───[1kΩ]───┘
                             │
                            │├─ 2N2222 (Emitter)
                             │
                            GND

Optional Button for Doorbell:
    GPIO18 (Pin 12) ──── Button ──── GND
    (Internal pull-up enabled)
```

## Pin Connections

| Component | Pin | GPIO | Purpose |
|-----------|-----|------|---------|
| Buzzer + | Pin 11 | GPIO17 | Control signal |
| Buzzer - | Pin 6 | GND | Ground |
| Button (optional) | Pin 12 | GPIO18 | Trigger |

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
cd ~/raspberry-projects/examples/03-output-sound/01-active-buzzer

# Run the active buzzer examples
python3 active-buzzer.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Control

1. **Simple On/Off**
   ```python
   from gpiozero import Buzzer
   
   buzzer = Buzzer(17)
   buzzer.on()   # Make sound
   buzzer.off()  # Stop sound
   ```

2. **Beep Patterns**
   ```python
   # Short beep
   buzzer.on()
   time.sleep(0.1)
   buzzer.off()
   ```

3. **Using Built-in Methods**
   ```python
   buzzer.beep()  # Default beep pattern
   buzzer.beep(on_time=0.1, off_time=0.1, n=3)
   ```

### Morse Code Implementation

```python
morse_code = {
    'A': '.-',   'B': '-...', 'C': '-.-.',
    # ... more letters
}

DOT = 0.1    # Short beep
DASH = 0.3   # Long beep

for symbol in morse_code[letter]:
    if symbol == '.':
        buzzer.on()
        time.sleep(DOT)
    elif symbol == '-':
        buzzer.on()
        time.sleep(DASH)
    buzzer.off()
    time.sleep(0.1)
```

## Key Concepts

### Sound Generation
- Active buzzers contain an internal oscillator
- Apply voltage = produce sound at fixed frequency
- Typical frequency: 2-4 kHz
- Cannot change pitch (use passive buzzer for that)

### Timing Patterns
```python
# Fire alarm pattern
def fire_alarm():
    while True:
        buzzer.on()
        time.sleep(0.5)
        buzzer.off()
        time.sleep(0.5)

# Burglar alarm pattern
def burglar_alarm():
    for _ in range(10):
        buzzer.on()
        time.sleep(0.1)
        buzzer.off()
        time.sleep(0.1)
    time.sleep(1)  # Pause
```

### Power Considerations
- Direct GPIO: Limited to ~16mA
- With transistor: Can use full buzzer current
- Multiple buzzers: Use transistor circuit

## Common Applications

### 1. Alarm Systems
- Intrusion detection
- Fire/smoke alarms
- Temperature warnings
- Water level alerts

### 2. User Feedback
- Button press confirmation
- Error notifications
- Success indicators
- Menu navigation sounds

### 3. Timers
- Kitchen timers
- Pomodoro timers
- Countdown alerts
- Reminder systems

### 4. Games
- Score notifications
- Game over sounds
- Level completion
- Player actions

### 5. IoT Devices
- Connection status
- Data received indicator
- Low battery warning
- System status

## Alarm Pattern Examples

### Continuous Alarm
```python
# Steady tone
buzzer.on()
time.sleep(duration)
buzzer.off()
```

### Pulsing Alarm
```python
# Repeating beeps
for _ in range(count):
    buzzer.on()
    time.sleep(0.2)
    buzzer.off()
    time.sleep(0.2)
```

### Escalating Alarm
```python
# Increasing urgency
for delay in [0.5, 0.3, 0.1]:
    for _ in range(5):
        buzzer.on()
        time.sleep(delay)
        buzzer.off()
        time.sleep(delay)
```

### SOS Pattern
```python
# ... --- ...
def sos():
    # S
    for _ in range(3):
        short_beep()
    letter_gap()
    # O
    for _ in range(3):
        long_beep()
    letter_gap()
    # S
    for _ in range(3):
        short_beep()
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No sound | Check polarity, verify active buzzer |
| Very quiet | Use transistor circuit, check voltage |
| Continuous sound | Check code logic, GPIO cleanup |
| Clicking only | Wrong buzzer type (passive), check connections |
| Interference | Add flyback diode with inductive loads |

## Advanced Techniques

### Non-Blocking Patterns
```python
import threading

class AlarmController:
    def __init__(self, buzzer):
        self.buzzer = buzzer
        self.running = False
        self.thread = None
    
    def start_alarm(self, pattern_func):
        self.running = True
        self.thread = threading.Thread(target=self._run_pattern, args=(pattern_func,))
        self.thread.start()
    
    def stop_alarm(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _run_pattern(self, pattern_func):
        while self.running:
            pattern_func(self.buzzer)
```

### Multiple Alert Levels
```python
class AlertSystem:
    def __init__(self, buzzer):
        self.buzzer = buzzer
        self.alert_levels = {
            'info': lambda: self.beep(1, 0.1),
            'warning': lambda: self.beep(2, 0.2),
            'error': lambda: self.beep(3, 0.3),
            'critical': lambda: self.continuous(1)
        }
    
    def alert(self, level):
        if level in self.alert_levels:
            self.alert_levels[level]()
```

### Pattern Queue
```python
from queue import Queue

class SoundQueue:
    def __init__(self, buzzer):
        self.buzzer = buzzer
        self.queue = Queue()
        self.playing = False
    
    def add_sound(self, pattern):
        self.queue.put(pattern)
        if not self.playing:
            self._play_next()
    
    def _play_next(self):
        if not self.queue.empty():
            self.playing = True
            pattern = self.queue.get()
            # Play pattern
            self.playing = False
            self._play_next()
```

## Performance Optimization

### Minimize GPIO Operations
```python
# Bad: Multiple GPIO calls
for _ in range(100):
    buzzer.on()
    buzzer.off()

# Better: Use beep method
buzzer.beep(on_time=0.01, off_time=0.01, n=100)
```

### Efficient Timing
```python
# Use monotonic time for accuracy
import time

start = time.monotonic()
while time.monotonic() - start < duration:
    # Precise timing
    pass
```

## Integration Examples

### With Motion Sensor
```python
from gpiozero import MotionSensor, Buzzer

pir = MotionSensor(4)
buzzer = Buzzer(17)

pir.when_motion = buzzer.on
pir.when_no_motion = buzzer.off
```

### With Temperature Sensor
```python
def check_temperature():
    if temperature > threshold:
        # Overheat alarm
        for _ in range(5):
            buzzer.beep(0.1, 0.1, n=3)
            time.sleep(1)
```

### With Network Events
```python
def network_monitor():
    if ping_failed():
        # Connection lost alarm
        buzzer.beep(on_time=1, off_time=0.5, n=3)
```

## Project Ideas

1. **Smart Doorbell**
   - Multiple chime patterns
   - Quiet hours mode
   - Visual indicator sync

2. **Parking Sensor**
   - Distance-based beep rate
   - Continuous when too close
   - Different patterns for objects

3. **Medicine Reminder**
   - Scheduled alarms
   - Acknowledgment required
   - Escalating alerts

4. **Game Console**
   - Menu sounds
   - Score notifications
   - Timer warnings

5. **Security System**
   - Entry/exit delays
   - Zone-specific sounds
   - Panic button

## Safety Notes

1. **Hearing Protection**
   - Buzzers can be loud
   - Limit exposure time
   - Consider volume control

2. **Electrical Safety**
   - Check voltage ratings
   - Use appropriate resistors
   - Proper insulation

## Next Steps

After mastering active buzzers:
1. Try passive buzzers for melodies
2. Combine with LED indicators
3. Build complete alarm systems
4. Add wireless triggers
5. Create IoT notifications

## Resources

- [GPIO Zero Buzzer](https://gpiozero.readthedocs.io/en/stable/api_output.html#buzzer)
- [Morse Code Reference](https://morsecode.world/international/morse.html)
- [Sound Pattern Design](https://www.nngroup.com/articles/sound-in-user-interfaces/)
- [Buzzer Types Guide](https://www.electronics-tutorials.ws/io/io_7.html)