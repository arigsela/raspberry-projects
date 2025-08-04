# Reaction Time Challenge Game

Test your reflexes with multiple game modes including the classic 10-second timer challenge, reaction tests, memory sequences, and competitive multiplayer modes.

## What You'll Learn
- Reaction time measurement
- Multi-threaded game design
- Event queue processing
- State machine implementation
- Timing precision
- Memory game algorithms
- Pattern recognition
- Multiplayer coordination
- Score persistence
- Statistical analysis

## Hardware Requirements
- Raspberry Pi 5
- 4x Colored push buttons (Red, Green, Blue, Yellow)
- 2x Control buttons (Start, Mode)
- 4x Colored LEDs matching buttons
- 3x Status LEDs (Ready, Active, Record)
- 1x Buzzer for audio feedback
- 16x2 LCD display with I2C backpack
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- Jumper wires and breadboard

## Circuit Diagram

```
Reaction Time Game Circuit:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Game Buttons (Colored):                                     │
│ RED BUTTON ────── GPIO17                                  │
│ GREEN BUTTON ──── GPIO27                                  │
│ BLUE BUTTON ───── GPIO22                                  │
│ YELLOW BUTTON ─── GPIO23                                  │
│                                                             │
│ Control Buttons:                                            │
│ START BUTTON ──── GPIO24 (Start/Stop/Select)              │
│ MODE BUTTON ───── GPIO25 (Change game mode)               │
│                                                             │
│ LED Indicators (Match button colors):                       │
│ RED LED ───────── GPIO5                                    │
│ GREEN LED ─────── GPIO6                                    │
│ BLUE LED ──────── GPIO13                                   │
│ YELLOW LED ────── GPIO19                                   │
│                                                             │
│ Status LEDs:                                                │
│ READY LED ─────── GPIO16 (White - System ready)           │
│ ACTIVE LED ────── GPIO20 (Orange - Game active)          │
│ RECORD LED ────── GPIO21 (Purple - New record)           │
│                                                             │
│ Audio Output:                                               │
│ BUZZER ────────── GPIO26 (Game sounds)                    │
│                                                             │
│ LCD Display:                                                │
│ SDA ──────────── GPIO2  (I2C Data)                       │
│ SCL ──────────── GPIO3  (I2C Clock)                      │
└─────────────────────────────────────────────────────────────┘

Game Layout:
┌─────────────────────────────────────────────────────────────┐
│                    BUTTON LAYOUT                            │
│                                                             │
│              🔴 RED           🟡 YELLOW                    │
│                •                 •                          │
│                                                             │
│              🟢 GREEN         🔵 BLUE                      │
│                •                 •                          │
│                                                             │
│         [START]                      [MODE]                 │
│                                                             │
│ Status: ⚪ Ready  🟠 Active  🟣 Record                      │
└─────────────────────────────────────────────────────────────┘

10-Second Timer Challenge:
┌─────────────────────────────────────────────────────────────┐
│                 10-SECOND SCORING                           │
│                                                             │
│  Time Difference    Result        Score                     │
│  ──────────────────────────────────────────              │
│  < 0.05s           PERFECT!       1000                      │
│  < 0.10s           Excellent!     500                       │
│  < 0.50s           Good!          100                       │
│  < 1.00s           OK             50                        │
│  > 1.00s           Try again      10                        │
│                                                             │
│  Example: 10.043s = 0.043s diff = PERFECT! (1000 pts)      │
└─────────────────────────────────────────────────────────────┘

Button Connections:
All buttons connect between GPIO pin and GND
(Internal pull-up resistors are used)

LED Connections:
GPIO → 220Ω resistor → LED anode → LED cathode → GND
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
cd examples/08-extension-projects/15-game-10-seconds
python reaction-time-game.py
```

Or use the Makefile:
```bash
make          # Run the game
make demo     # Hardware demonstration
make test     # Test all components
make scores   # View high scores
make setup    # Install dependencies
```

## Game Modes

### 1. 10-Second Timer
The classic challenge - stop the timer at exactly 10 seconds:
- Press START to begin timing
- Press START again to stop
- Scoring based on accuracy
- Perfect timing = 1000 points

### 2. Reaction Time
Test your reflexes:
- Wait for random LED to light up
- Press matching button quickly
- 5 rounds per game
- Average reaction time calculated

### 3. Memory Sequence
Simon Says style memory game:
- Watch the LED pattern
- Repeat the sequence
- Pattern grows each round
- Miss one = lose a life

### 4. Pattern Match
Copy shown patterns:
- 4-button patterns displayed
- Match them exactly
- Build combos for bonus points
- 10 rounds per game

### 5. Speed Test
Hit targets as fast as possible:
- Random LEDs light up
- Press matching buttons
- 20 targets total
- Timed for speed

### 6. Endurance Mode
How long can you last?
- Increasing difficulty
- Targets appear faster
- One mistake = game over
- Score based on survival time

### 7. 2-Player VS
Competitive reaction test:
- Players alternate turns
- Best of 5 rounds
- Reaction times compared
- Winner takes all!

## Code Walkthrough

### Event Queue System
Non-blocking button handling:
```python
def _handle_game_button(self, button_index):
    # Add to event queue with timestamp
    self.event_queue.put(('button', button_index, time.time()))
    
def _process_events(self):
    while not self.event_queue.empty():
        event = self.event_queue.get_nowait()
        if event[0] == 'button':
            self._process_button_press(event[1], event[2])
```

### Precision Timing
High-accuracy time measurement:
```python
def _stop_timer(self):
    elapsed = time.time() - self.start_time
    difference = abs(elapsed - TEN_SECOND_TARGET)
    
    # Score based on accuracy
    if difference < 0.05:
        score = 1000  # PERFECT!
    elif difference < 0.1:
        score = 500   # Excellent
```

### Memory Sequence Algorithm
Progressive difficulty:
```python
def _sequence_game_loop(self):
    while self.lives > 0:
        # Add new color to sequence
        self.sequence.append(random.randint(0, 3))
        
        # Show sequence with timing
        for color in self.sequence:
            self.leds[color].on()
            time.sleep(SEQUENCE_SHOW_TIME)
            self.leds[color].off()
            time.sleep(SEQUENCE_GAP_TIME)
```

### Multi-threaded Game Loops
Separate threads for each mode:
```python
def _init_reaction(self):
    self.game_thread = threading.Thread(
        target=self._reaction_game_loop, 
        daemon=True
    )
    self.game_thread.start()
```

### Statistical Analysis
Track and analyze performance:
```python
def _reaction_game_over(self):
    if self.reaction_times:
        avg_time = statistics.mean(self.reaction_times)
        best_time = min(self.reaction_times)
        
        # Score based on average reaction time
        self.current_score = int(10000 / avg_time)
```

## Features

### Game Features
- 7 unique game modes
- Progressive difficulty
- High score tracking
- Combo system
- Lives system
- Time limits
- Multiplayer support

### Feedback Systems
- Colored LED indicators
- Audio feedback tones
- LCD status display
- Victory celebrations
- New record alerts
- Real-time scoring

### Performance Tracking
- Reaction time statistics
- Best/average calculations
- Score persistence
- Mode-specific records
- Session statistics
- Player profiles

### User Interface
- Simple button controls
- Clear LCD messages
- LED status indicators
- Audio cues
- Mode selection
- Quick restart

## Available Demos

1. **Button Test**: Test all colored buttons
2. **LED Patterns**: Show LED sequences
3. **Reaction Demo**: Sample reaction test
4. **Memory Demo**: Short sequence example
5. **Sound Demo**: Audio feedback samples

## Troubleshooting

### Buttons not registering
- Check GPIO connections
- Verify pull-up resistors
- Test bounce time settings
- Check event queue processing
- Monitor button callbacks

### Timing inaccuracy
- Use time.perf_counter() for precision
- Minimize processing delays
- Check system load
- Verify thread priorities
- Monitor event timestamps

### LED synchronization
- Check LED polarity
- Verify resistor values
- Test GPIO outputs
- Monitor power supply
- Check ground connections

### LCD display issues
- Verify I2C address
- Check SDA/SCL connections
- Enable I2C interface
- Test with i2cdetect
- Check contrast setting

### Game state problems
- Review state transitions
- Check thread safety
- Monitor event queue
- Verify state machine logic
- Debug with logging

## Advanced Usage

### Custom Game Modes
Create new challenges:
```python
class CustomMode:
    def __init__(self, game):
        self.game = game
        self.pattern_library = self._load_patterns()
        
    def run_challenge(self):
        # Custom game logic
        pattern = self._generate_adaptive_pattern()
        score = self._evaluate_performance()
        return score
```

### Adaptive Difficulty
Dynamic difficulty adjustment:
```python
class DifficultyManager:
    def __init__(self):
        self.player_skill = 0.5
        self.adjustment_rate = 0.1
        
    def adjust_difficulty(self, success_rate):
        if success_rate > 0.8:
            self.increase_difficulty()
        elif success_rate < 0.4:
            self.decrease_difficulty()
```

### Network Competition
Online multiplayer support:
```python
import asyncio
import websockets

class OnlineMultiplayer:
    async def host_game(self):
        async with websockets.serve(self.handle_player, "0.0.0.0", 8765):
            await self.game_session()
            
    async def join_game(self, host):
        async with websockets.connect(f"ws://{host}:8765") as websocket:
            await self.play_remote(websocket)
```

### Machine Learning Integration
Pattern prediction and analysis:
```python
from sklearn.neural_network import MLPClassifier

class PatternPredictor:
    def __init__(self):
        self.model = MLPClassifier(hidden_layer_sizes=(100, 50))
        self.training_data = []
        
    def predict_next_move(self, sequence):
        if len(self.training_data) > 100:
            features = self._extract_features(sequence)
            return self.model.predict([features])[0]
```

### Biometric Monitoring
Track player stress/focus:
```python
class BiometricTracker:
    def __init__(self):
        self.heart_rate_sensor = HeartRateSensor()
        self.baseline_hr = None
        
    def measure_stress_level(self):
        current_hr = self.heart_rate_sensor.read()
        if self.baseline_hr:
            stress = (current_hr - self.baseline_hr) / self.baseline_hr
            return min(max(stress, 0), 1)  # 0-1 scale
```

## Integration Ideas

### Educational Applications
- Reaction time studies
- Memory training programs
- Attention span testing
- Cognitive assessment
- Motor skill development

### Therapy and Rehabilitation
- Hand-eye coordination
- Cognitive therapy
- Reflex training
- Memory exercises
- Progress tracking

### Competitive Gaming
- Tournament system
- Online leaderboards
- Team competitions
- Seasonal challenges
- Achievement system

### Research Applications
- Reaction time studies
- Pattern recognition research
- Human performance analysis
- Fatigue detection
- Learning curve analysis

## Performance Optimization

### Timing Accuracy
- Use hardware interrupts
- Minimize Python overhead
- Implement C extensions
- Real-time thread priority
- Disable garbage collection

### Response Time
- Event-driven architecture
- Asynchronous processing
- Button debouncing
- Queue optimization
- Thread pooling

### Memory Management
- Limit history size
- Efficient data structures
- Garbage collection tuning
- Resource pooling
- Memory profiling

## Next Steps
- Add voice commands and audio feedback
- Implement AI opponents with learning
- Create mobile app companion
- Add haptic feedback support
- Integrate VR/AR displays
- Develop championship mode
- Add physiological monitoring