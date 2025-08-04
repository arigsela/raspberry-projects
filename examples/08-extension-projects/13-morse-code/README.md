# Morse Code Communicator

Interactive Morse code learning and communication system with multiple operating modes, adjustable speed, and educational features.

## What You'll Learn
- Morse code encoding and decoding
- Timing-based signal processing
- Multi-threaded input/output handling
- Interactive learning systems
- State machine implementation
- Real-time signal analysis
- Educational game design
- Audio-visual feedback systems

## Hardware Requirements
- Raspberry Pi 5
- LED for visual Morse output
- Buzzer for audio Morse output
- Push button for telegraph key input
- 3x Push buttons for controls (Mode, Speed Up, Speed Down)
- 3x Status LEDs (Power, Transmit, Receive)
- 16x2 LCD display with I2C backpack
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- Jumper wires and breadboard

## Circuit Diagram

```
Morse Code Communicator:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Output Devices:                                             │
│ MORSE LED ────── GPIO17 (Visual output)                   │
│ MORSE BUZZER ─── GPIO27 (Audio output)                    │
│                                                             │
│ Input Controls:                                             │
│ KEY BUTTON ───── GPIO22 (Telegraph key)                   │
│ MODE BUTTON ──── GPIO23 (Change mode)                     │
│ SPEED UP ─────── GPIO24 (Increase WPM)                    │
│ SPEED DOWN ───── GPIO25 (Decrease WPM)                    │
│                                                             │
│ Status Indicators:                                          │
│ POWER LED ────── GPIO5  (Green - System ready)            │
│ TX LED ───────── GPIO6  (Red - Transmitting)              │
│ RX LED ───────── GPIO13 (Blue - Receiving)                │
│                                                             │
│ LCD Display:                                                │
│ SDA ─────────── GPIO2  (I2C Data)                         │
│ SCL ─────────── GPIO3  (I2C Clock)                        │
└─────────────────────────────────────────────────────────────┘

Morse Code Timing Diagram:
┌─────────────────────────────────────────────────────────────┐
│                    MORSE CODE TIMING                        │
│                                                             │
│  Dot (·):      ▄ (1 unit)                                 │
│  Dash (−):     ▄▄▄ (3 units)                              │
│                                                             │
│  Intra-character gap: _ (1 unit)                           │
│  Inter-character gap: ___ (3 units)                        │
│  Inter-word gap:      _______ (7 units)                    │
│                                                             │
│  Example: "SOS" = ··· −−− ···                             │
│  Signal:  ▄ ▄ ▄ ___ ▄▄▄ ▄▄▄ ▄▄▄ ___ ▄ ▄ ▄                │
│                                                             │
│  WPM Calculation: 1 unit = 1200 / WPM milliseconds         │
└─────────────────────────────────────────────────────────────┘

International Morse Code Chart:
┌─────────────────────────────────────────────────────────────┐
│ A: ·−      N: −·      0: −−−−−    .: ·−·−·−              │
│ B: −···    O: −−−     1: ·−−−−    ,: −−··−−              │
│ C: −·−·    P: ·−−·    2: ··−−−    ?: ··−−··              │
│ D: −··     Q: −−·−    3: ···−−    ': ·−−−−·              │
│ E: ·       R: ·−·     4: ····−    !: −·−·−−              │
│ F: ··−·    S: ···     5: ·····    /: −··−·               │
│ G: −−·     T: −       6: −····    (: −·−−·               │
│ H: ····    U: ··−     7: −−···    ): −·−−·−              │
│ I: ··      V: ···−    8: −−−··    &: ·−···               │
│ J: ·−−−    W: ·−−     9: −−−−·    :: −−−···              │
│ K: −·−     X: −··−                ;: −·−·−·              │
│ L: ·−··    Y: −·−−                =: −···−               │
│ M: −−      Z: −−··                +: ·−·−·               │
└─────────────────────────────────────────────────────────────┘

Button Connections:
All buttons connect between GPIO pin and GND
(Internal pull-up resistors are used)

LED Connections:
GPIO → 220Ω resistor → LED anode → LED cathode → GND

Buzzer Connection:
GPIO → Buzzer positive → Buzzer negative → GND
```

## Software Dependencies

Install required libraries:
```bash
# GPIO control
pip install gpiozero

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/13-morse-code
python morse-code-communicator.py
```

Or use the Makefile:
```bash
make          # Run the communicator
make demo     # Morse code demonstration
make test     # Test all components
make chart    # Display Morse code chart
make setup    # Install dependencies
```

## Operating Modes

### 1. Translator Mode
Type text to convert and transmit as Morse code:
- Enter message via keyboard
- See Morse representation
- Automatic transmission
- Visual and audio output

### 2. Decoder Mode  
Decode Morse code input from the telegraph key:
- Press button for dots and dashes
- Automatic timing detection
- Real-time decoding
- Display decoded text

### 3. Trainer Mode
Interactive Morse code learning:
- Sequential character training
- Listen and repeat exercises
- Progress tracking
- Accuracy scoring

### 4. Game Mode
Practice with random challenges:
- Random word transmission
- Decode and respond
- Score tracking
- Increasing difficulty

### 5. Beacon Mode
Automatic repeating transmission:
- Configurable message
- Adjustable interval
- Continuous operation
- Station identification

## Code Walkthrough

### Morse Code Encoding
Text to Morse conversion:
```python
class MorseCode:
    MORSE_CODE = {
        'A': '.-',    'B': '-...',  'C': '-.-.',
        'D': '-..',   'E': '.',     'F': '..-.',
        # ... complete alphabet, numbers, punctuation
    }
    
    @staticmethod
    def encode(text):
        morse = []
        for char in text.upper():
            if char in MorseCode.MORSE_CODE:
                morse.append(MorseCode.MORSE_CODE[char])
        return ' '.join(morse)
```

### Precise Timing Control
WPM-based timing calculation:
```python
def _calculate_unit_time(self, wpm):
    # PARIS standard: 50 units per word
    # WPM = words per minute
    return 60.0 / (wpm * 50)

def transmit_dot(self):
    self.led.on()
    self.buzzer.on()
    time.sleep(self.unit_time * DOT_TIME)
    self.led.off()
    self.buzzer.off()
```

### Real-time Decoding
Button timing analysis:
```python
def _key_up(self):
    duration = time.time() - self.key_down_time
    
    # Determine dot or dash based on duration
    if duration < self.unit_time * 2:
        self.current_symbol.append('.')
    else:
        self.current_symbol.append('-')
    
    # Check for character/word boundaries
    gap = time.time() - self.last_activity
    if gap > self.unit_time * INTER_WORD_GAP:
        self._finish_word()
```

### Interactive Training
Adaptive learning system:
```python
def _trainer_mode(self):
    char = self.training_chars[self.training_index]
    morse = MorseCode.MORSE_CODE[char]
    
    # Transmit example
    print(f"Learn: {char} = {morse}")
    self.transmitter.transmit_character(morse)
    
    # Wait for user to echo
    received = self.decoder.get_decoded_message()
    if char in received:
        self.training_score += 1
        print("✅ Correct!")
```

### Multi-threaded Architecture
Concurrent operation handling:
```python
def run(self):
    # Start decoder thread
    self.decoder.start_decoding()
    
    # Start mode-specific thread
    if self.mode == MorseMode.TRANSLATOR:
        threading.Thread(target=self._translator_mode).start()
    elif self.mode == MorseMode.DECODER:
        threading.Thread(target=self._decoder_mode).start()
    # ... other modes
```

## Features

### Educational Features
- Progressive learning curve
- Character-by-character training
- Immediate feedback
- Accuracy tracking
- Customizable speed

### Communication Features
- Bidirectional translation
- Real-time encoding/decoding
- Adjustable WPM (5-30)
- Standard timing ratios
- Prosign support

### User Interface
- LCD status display
- LED indicators
- Audio feedback
- Button controls
- Console output

### System Features
- Configuration persistence
- Session statistics
- Error handling
- Mode switching
- Clean shutdown

## Available Demos

1. **Signal Demo**: Common Morse signals (SOS, OK, etc.)
2. **Alphabet Demo**: A-Z character transmission
3. **Speed Demo**: Different WPM demonstrations
4. **Prosign Demo**: Special Morse signals
5. **Interactive Demo**: Try encoding/decoding

## Troubleshooting

### LED/Buzzer not working
- Check GPIO connections
- Verify resistor values
- Test with simple on/off
- Check power supply
- Verify ground connection

### Timing issues
- Calibrate WPM setting
- Check button debouncing
- Verify system clock
- Adjust timing constants
- Test with known signals

### Decoding errors
- Practice consistent timing
- Start with slower speeds
- Check button responsiveness
- Verify gap detection
- Use training mode

### LCD display problems
- Check I2C address
- Verify connections
- Enable I2C interface
- Test with i2cdetect
- Check pull-up resistors

### Training difficulties
- Start with common letters (E, T, A)
- Reduce speed initially
- Focus on timing consistency
- Use visual + audio feedback
- Practice regularly

## Advanced Usage

### Custom Training Sets
Create specialized training sequences:
```python
# Amateur radio Q-codes
self.training_chars = ['QSO', 'QTH', 'QRM', 'QRT', 'QSL']

# Numbers only
self.training_chars = list('0123456789')

# Common words
self.training_words = ['THE', 'AND', 'FOR', 'ARE']
```

### Network Integration
Remote Morse communication:
```python
import socket

def network_transmit(self, message):
    morse = MorseCode.encode(message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(morse.encode(), ('remote_pi.local', 8888))
    
    # Also transmit locally
    self.transmitter.transmit_message(message)
```

### Automatic CW Keyer
Iambic paddle support:
```python
class IambicKeyer:
    def __init__(self, dit_pin, dah_pin):
        self.dit_paddle = Button(dit_pin)
        self.dah_paddle = Button(dah_pin)
        self.mode = 'A'  # Iambic A or B
        
    def generate_elements(self):
        # Iambic keying logic
        if self.dit_paddle.is_pressed:
            yield '.'
        if self.dah_paddle.is_pressed:
            yield '-'
```

### Signal Analysis
FFT for audio decoding:
```python
import numpy as np

def analyze_audio_morse(self, audio_samples):
    # FFT to find tone frequency
    fft = np.fft.fft(audio_samples)
    frequencies = np.fft.fftfreq(len(samples), 1/sample_rate)
    
    # Detect 600-800Hz CW tone
    tone_idx = np.where((frequencies > 600) & (frequencies < 800))
    tone_present = np.max(np.abs(fft[tone_idx])) > threshold
```

### Contest Mode
High-speed CW operation:
```python
class ContestMode:
    def __init__(self):
        self.qso_count = 0
        self.callsigns = []
        
    def quick_exchange(self, callsign, rst='599'):
        # Contest-style exchange
        message = f"{callsign} {rst} {self.qso_count:03d}"
        self.transmitter.transmit_message(message)
        self.qso_count += 1
```

## Performance Optimization

### Timing Accuracy
- Use high-resolution timers
- Compensate for processing delays
- Implement adaptive timing
- Buffer transmission queue

### Decoding Reliability
- Adaptive threshold detection
- Noise filtering
- Pattern recognition
- Error correction

### Training Efficiency
- Spaced repetition
- Adaptive difficulty
- Focus on problem characters
- Track learning curves

## Integration Ideas

### Amateur Radio Station
- CAT control integration
- Logging software interface
- Band/frequency display
- QSO management

### Emergency Communication
- Backup power system
- Weather alerts
- Emergency beacon
- Message relay

### Education System
- Classroom mode
- Progress tracking
- Multiplayer games
- Certificate generation

### Museum Display
- Historical messages
- Interactive exhibits
- Telegraph simulation
- Period-appropriate speeds

## Next Steps
- Add software-defined radio (SDR) integration
- Implement CW filter and decoder
- Create mobile app companion
- Add haptic feedback option
- Integrate with amateur radio transceivers
- Implement automatic CQ calling
- Add APRS beacon capability
