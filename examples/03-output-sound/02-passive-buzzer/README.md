# Project 03-02: Passive Buzzer - Musical Tones and Melodies

Create musical notes, melodies, and sound effects using a passive buzzer with PWM control for audio projects.

## What You'll Learn

- Passive buzzer operation with PWM
- Musical note generation
- Frequency control and pitch
- Creating melodies and scales
- Sound effect synthesis
- Real-time tone control

## Hardware Requirements

- Raspberry Pi 5
- 1x Passive buzzer
- Optional: 1x NPN transistor (2N2222) for louder output
- Optional: 100Ω resistor for current limiting
- Jumper wires
- Breadboard

## Active vs Passive Buzzers

| Feature | Active Buzzer | Passive Buzzer |
|---------|---------------|----------------|
| Built-in oscillator | Yes | No |
| Control method | On/Off (DC) | PWM (frequency) |
| Sound variety | Single tone | Any frequency |
| Musical notes | No | Yes |
| Complexity | Simple | More complex |
| Applications | Alarms, beeps | Music, effects |

## Circuit Diagram

```
Basic Passive Buzzer Connection:

    Passive Buzzer
    ┌─────────┐
    │    +    │ 
    │ BUZZER  │
    │    -    │ 
    └────┬────┘
         │
         ├──── GPIO18 (Pin 12) - PWM0
         │
         └──── GND (Pin 14)

With Current Limiting Resistor:

    GPIO18 ──[100Ω]──┬──── Buzzer (+)
                     │
                     └──── Buzzer (-)
                            │
                           GND

With Transistor for Louder Output:

    3.3V ─────────────┬──── Buzzer (+)
                      │
                      │     Buzzer (-)
                      │         │
                      └─────────┤
                               │├─ 2N2222 (Collector)
                               ─┤
                               │├─ 2N2222 (Base)
                                │
                      GPIO18 ───┴───[1kΩ]───┘
                                │
                               │├─ 2N2222 (Emitter)
                                │
                               GND
```

## Pin Connections

| Component | Pin | GPIO | Purpose |
|-----------|-----|------|---------|
| Buzzer + | Pin 12 | GPIO18 | PWM signal |
| Buzzer - | Pin 14 | GND | Ground |

Note: GPIO18 is PWM0 channel, hardware PWM capable

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
cd ~/raspberry-projects/examples/03-output-sound/02-passive-buzzer

# Run the passive buzzer examples
python3 passive-buzzer.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Tone Generation

1. **PWM Control**
   ```python
   from gpiozero import PWMOutputDevice
   
   buzzer = PWMOutputDevice(18)
   buzzer.frequency = 440  # A4 note (440 Hz)
   buzzer.value = 0.5      # 50% duty cycle
   ```

2. **Playing Notes**
   ```python
   def play_tone(frequency, duration):
       buzzer.frequency = frequency
       buzzer.value = 0.5
       time.sleep(duration)
       buzzer.value = 0  # Stop
   ```

3. **Musical Notes**
   ```python
   NOTES = {
       'C4': 261.63, 'D4': 293.66, 'E4': 329.63,
       'F4': 349.23, 'G4': 392.00, 'A4': 440.00,
       'B4': 493.88, 'C5': 523.25
   }
   ```

### Creating Melodies

```python
melody = [
    ('C4', 0.5), ('D4', 0.5), ('E4', 0.5), ('F4', 0.5),
    ('G4', 1.0), ('A4', 0.5), ('B4', 0.5), ('C5', 1.0)
]

for note, duration in melody:
    play_note(note, duration)
```

## Key Concepts

### Sound and Frequency
- **Frequency**: Vibrations per second (Hz)
- **Pitch**: Higher frequency = higher pitch
- **Musical notes**: Specific frequencies
- **Octaves**: Doubling frequency = next octave

### PWM for Audio
```
PWM Signal:
  ┌─┐ ┌─┐ ┌─┐ ┌─┐
──┘ └─┘ └─┘ └─┘ └─
  <--> Period = 1/frequency
```

- **Frequency**: Controls pitch
- **Duty cycle**: Controls volume (typically 50%)
- **Period**: 1/frequency seconds

### Musical Note Frequencies

| Note | Frequency (Hz) | Note | Frequency (Hz) |
|------|----------------|------|----------------|
| C4 | 261.63 | C5 | 523.25 |
| D4 | 293.66 | D5 | 587.33 |
| E4 | 329.63 | E5 | 659.25 |
| F4 | 349.23 | F5 | 698.46 |
| G4 | 392.00 | G5 | 783.99 |
| A4 | 440.00 | A5 | 880.00 |
| B4 | 493.88 | B5 | 987.77 |

### Musical Timing
- **Whole note**: 1 beat
- **Half note**: 0.5 beat
- **Quarter note**: 0.25 beat
- **Tempo**: Beats per minute (BPM)

## Common Applications

### 1. Musical Instruments
- Electronic pianos
- Synthesizers
- Music boxes
- Toy instruments

### 2. Game Sound Effects
- Jump sounds
- Coin collection
- Power-ups
- Game over melodies

### 3. Notification Tones
- Custom ringtones
- Alert melodies
- Reminder chimes
- Success/error sounds

### 4. Educational Tools
- Music theory demos
- Frequency experiments
- Audio feedback
- Ear training

### 5. Art Installations
- Interactive sound
- Motion-triggered music
- Ambient soundscapes
- Musical sculptures

## Sound Effect Examples

### Siren Effect
```python
def siren():
    for _ in range(5):
        # Sweep up
        for freq in range(400, 800, 10):
            play_tone(freq, 0.01)
        # Sweep down
        for freq in range(800, 400, -10):
            play_tone(freq, 0.01)
```

### Laser Sound
```python
def laser():
    for freq in range(2000, 100, -50):
        play_tone(freq, 0.01)
```

### Phone Ring
```python
def phone_ring():
    for _ in range(3):
        play_tone(1000, 0.1)
        play_tone(800, 0.1)
        time.sleep(0.3)
```

### Robot Voice
```python
def robot_talk():
    import random
    for _ in range(20):
        freq = random.choice([200, 250, 300, 350])
        play_tone(freq, random.uniform(0.05, 0.15))
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No sound | Check connections, verify passive buzzer |
| Wrong pitch | Verify frequency calculations |
| Distorted sound | Check PWM frequency limits |
| Quiet sound | Use transistor circuit, check power |
| Clicking only | Wrong buzzer type (active) |

## Advanced Techniques

### Polyphonic Simulation
```python
# Rapid alternation for chord effect
def play_chord(notes, duration):
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        note = notes[i % len(notes)]
        play_tone(NOTES[note], 0.01)
        i += 1
```

### Volume Control
```python
def play_with_volume(frequency, duration, volume):
    buzzer.frequency = frequency
    buzzer.value = volume * 0.5  # 0-50% duty cycle
    time.sleep(duration)
    buzzer.value = 0
```

### Envelope Control
```python
def play_with_envelope(frequency, duration):
    # Attack
    for v in range(0, 50, 5):
        buzzer.frequency = frequency
        buzzer.value = v / 100
        time.sleep(0.01)
    
    # Sustain
    time.sleep(duration - 0.2)
    
    # Release
    for v in range(50, 0, -5):
        buzzer.value = v / 100
        time.sleep(0.01)
```

### Music Parser
```python
def parse_music(notation):
    """Parse simple music notation
    Example: "C4:4 D4:4 E4:2 REST:4 G4:1"
    """
    notes = notation.split()
    for item in notes:
        note, beats = item.split(':')
        duration = float(beats) * 0.25  # Quarter note = 0.25s
        if note == 'REST':
            time.sleep(duration)
        else:
            play_note(note, duration)
```

## Performance Optimization

### Hardware PWM
- Use hardware PWM pins (GPIO18, GPIO13)
- More accurate frequency
- Less CPU usage

### Frequency Limits
```python
# Raspberry Pi PWM limits
MIN_FREQ = 10      # Hz
MAX_FREQ = 8000    # Hz (reliable)

def safe_play_tone(frequency, duration):
    freq = max(MIN_FREQ, min(MAX_FREQ, frequency))
    play_tone(freq, duration)
```

### Non-Blocking Audio
```python
import threading

class AudioPlayer:
    def __init__(self, buzzer):
        self.buzzer = buzzer
        self.playing = False
    
    def play_async(self, melody):
        thread = threading.Thread(target=self._play, args=(melody,))
        thread.start()
    
    def _play(self, melody):
        self.playing = True
        for note, duration in melody:
            if not self.playing:
                break
            play_note(note, duration)
        self.playing = False
```

## Musical Theory

### Scales
```python
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11, 12],
    'minor': [0, 2, 3, 5, 7, 8, 10, 12],
    'pentatonic': [0, 2, 4, 7, 9, 12],
    'blues': [0, 3, 5, 6, 7, 10, 12]
}

def play_scale(root_note, scale_type):
    root_freq = NOTES[root_note]
    for interval in SCALES[scale_type]:
        freq = root_freq * (2 ** (interval / 12))
        play_tone(freq, 0.5)
```

### Tempo Control
```python
class MusicPlayer:
    def __init__(self, tempo=120):
        self.tempo = tempo
        self.beat_duration = 60 / tempo
    
    def play_note(self, note, beats):
        duration = beats * self.beat_duration
        play_note(note, duration)
```

## Project Ideas

1. **Music Box**
   - Pre-programmed melodies
   - Speed control
   - Song selection

2. **Simon Game**
   - Memory sequence game
   - Each button plays note
   - Increasing difficulty

3. **Theremin Simulator**
   - Distance sensor input
   - Frequency based on distance
   - Volume control

4. **Morse Code Trainer**
   - Learn Morse code
   - Adjustable speed
   - Practice mode

5. **Musical Alarm Clock**
   - Wake to melodies
   - Gradual volume increase
   - Snooze function

## Integration Examples

### With Buttons (Piano)
```python
button_notes = {
    button1: 'C4',
    button2: 'D4',
    button3: 'E4',
    # ... more buttons
}

for button, note in button_notes.items():
    button.when_pressed = lambda n=note: play_note(n, 0.2)
```

### With Sensors
```python
# Light-controlled theremin
light_level = photoresistor.value
frequency = 200 + (light_level * 1000)
play_tone(frequency, 0.1)
```

### With Motion
```python
# Motion-triggered melody
if motion_detected:
    play_melody(doorbell_tune)
```

## Safety Notes

1. **Hearing Protection**
   - High frequencies can be uncomfortable
   - Limit volume and duration
   - Test at low volumes first

2. **Component Protection**
   - Use current limiting resistors
   - Check voltage ratings
   - Avoid continuous high-frequency operation

## Next Steps

After mastering passive buzzers:
1. Build musical instruments
2. Create game soundtracks
3. Develop audio feedback systems
4. Combine with displays for music visualizers
5. Build MIDI interfaces

## Resources

- [Musical Note Frequencies](https://pages.mtu.edu/~suits/notefreqs.html)
- [PWM Audio on Raspberry Pi](https://www.raspberrypi.org/documentation/usage/audio/)
- [Music Theory Basics](https://www.musictheory.net/)
- [GPIO Zero PWM](https://gpiozero.readthedocs.io/en/stable/api_output.html#pwmoutputdevice)