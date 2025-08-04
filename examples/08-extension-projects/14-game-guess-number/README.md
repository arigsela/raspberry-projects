# Number Guessing Game

Interactive number guessing game with multiple difficulty modes, LED feedback, progressive hints, and high score tracking.

## What You'll Learn
- Game state management
- User interface design
- Difficulty progression
- Score tracking systems
- LED feedback patterns
- Audio feedback design
- Button input handling
- Statistical analysis
- File persistence
- Timer implementation

## Hardware Requirements
- Raspberry Pi 5
- 4x Push buttons (Up, Down, Select, Mode)
- 3x LEDs (Hot/Red, Cold/Blue, Correct/Green)
- 1x Power LED (White)
- 1x Buzzer for audio feedback
- 16x2 LCD display with I2C backpack
- Optional: 7-segment display
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- Jumper wires and breadboard

## Circuit Diagram

```
Number Guessing Game Circuit:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Input Controls:                                             │
│ UP BUTTON ─────── GPIO17 (Increase guess)                 │
│ DOWN BUTTON ───── GPIO27 (Decrease guess)                 │
│ SELECT BUTTON ─── GPIO22 (Confirm guess)                  │
│ MODE BUTTON ───── GPIO23 (Change mode/hint)               │
│                                                             │
│ LED Indicators:                                             │
│ HOT LED ──────── GPIO5  (Red - Getting warmer)           │
│ COLD LED ─────── GPIO6  (Blue - Getting colder)          │
│ CORRECT LED ──── GPIO13 (Green - Correct guess)          │
│ POWER LED ────── GPIO19 (White - System ready)           │
│                                                             │
│ Audio Output:                                               │
│ BUZZER ────────── GPIO26 (Game sounds)                    │
│                                                             │
│ LCD Display:                                                │
│ SDA ──────────── GPIO2  (I2C Data)                       │
│ SCL ──────────── GPIO3  (I2C Clock)                      │
│                                                             │
│ Optional 7-Segment Display:                                 │
│ SEG A ─────────── GPIO16                                   │
│ SEG B ─────────── GPIO20                                   │
│ SEG C ─────────── GPIO21                                   │
│ SEG D ─────────── GPIO12                                   │
│ SEG E ─────────── GPIO25                                   │
│ SEG F ─────────── GPIO24                                   │
│ SEG G ─────────── GPIO18                                   │
│ SEG DP ────────── GPIO4                                    │
└─────────────────────────────────────────────────────────────┘

Game Flow Diagram:
┌─────────────────────────────────────────────────────────────┐
│                    GAME STATES                              │
│                                                             │
│    ┌──────┐     ┌─────────┐     ┌─────┐                  │
│    │ MENU │────▶│ PLAYING │────▶│ WON │                  │
│    └──────┘     └─────────┘     └─────┘                  │
│        ▲              │              │                      │
│        │              ▼              │                      │
│        │         ┌──────┐           │                      │
│        └─────────│ LOST │◀──────────┘                     │
│                  └──────┘                                   │
│                                                             │
│ Temperature Feedback:                                       │
│ • Previous guess distance: 50                              │
│ • Current guess distance: 30                               │
│ • Result: WARMER (Red LED on)                             │
│                                                             │
│ • Previous guess distance: 30                              │
│ • Current guess distance: 40                               │
│ • Result: COLDER (Blue LED on)                            │
└─────────────────────────────────────────────────────────────┘

Button Connections:
All buttons connect between GPIO pin and GND
(Internal pull-up resistors are used)

LED Connections:
GPIO → 220Ω resistor → LED anode → LED cathode → GND

7-Segment Display Truth Table:
┌─────────────────────────────────────────────────────────────┐
│ Digit │ A │ B │ C │ D │ E │ F │ G │ Display            │
├───────┼───┼───┼───┼───┼───┼───┼───┼────────────────────┤
│   0   │ 1 │ 1 │ 1 │ 1 │ 1 │ 1 │ 0 │  ▄▄▄              │
│   1   │ 0 │ 1 │ 1 │ 0 │ 0 │ 0 │ 0 │    ▐ ▐            │
│   2   │ 1 │ 1 │ 0 │ 1 │ 1 │ 0 │ 1 │  ▄▄▄              │
│   3   │ 1 │ 1 │ 1 │ 1 │ 0 │ 0 │ 1 │  ▄▄▄              │
│   4   │ 0 │ 1 │ 1 │ 0 │ 0 │ 1 │ 1 │    ▐ ▐            │
│   5   │ 1 │ 0 │ 1 │ 1 │ 0 │ 1 │ 1 │  ▄▄▄              │
│   6   │ 1 │ 0 │ 1 │ 1 │ 1 │ 1 │ 1 │  ▄▄▄              │
│   7   │ 1 │ 1 │ 1 │ 0 │ 0 │ 0 │ 0 │  ▄▄▄              │
│   8   │ 1 │ 1 │ 1 │ 1 │ 1 │ 1 │ 1 │  ▄▄▄              │
│   9   │ 1 │ 1 │ 1 │ 1 │ 0 │ 1 │ 1 │  ▄▄▄              │
└─────────────────────────────────────────────────────────────┘
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
cd examples/08-extension-projects/14-game-guess-number
python number-guessing-game.py
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

### 1. Easy Mode
- Range: 1-50
- Unlimited guesses
- Perfect for beginners
- Temperature feedback

### 2. Normal Mode
- Range: 1-100
- Unlimited guesses
- Hints after 5 guesses
- Standard difficulty

### 3. Hard Mode
- Range: 1-200
- Limited to 10 guesses
- No time limit
- Challenge mode

### 4. Extreme Mode
- Range: 1-500
- Limited to 15 guesses
- 60-second time limit
- Expert level

### 5. Custom Mode
- User-defined range
- Configurable limits
- Personalized difficulty

### 6. Binary Mode
- Range: 1-128
- 7 guesses (log₂(128))
- Binary search practice
- Educational mode

## Code Walkthrough

### Game State Management
State machine for game flow:
```python
class GameState(Enum):
    MENU = "Menu"          # Mode selection
    PLAYING = "Playing"    # Active game
    WON = "Won"           # Victory state
    LOST = "Lost"         # Defeat state
    PAUSED = "Paused"     # Game paused
    SETTINGS = "Settings"  # Configuration
```

### Temperature Feedback System
Visual feedback based on guess proximity:
```python
def _handle_low_guess(self):
    # Calculate distances
    distance_before = abs(self.guess_history[-2] - self.target_number) 
    distance_now = abs(self.current_guess - self.target_number)
    
    if distance_now < distance_before:
        # Getting warmer
        self.led_hot.on()
        self.led_cold.off()
    else:
        # Getting colder
        self.led_hot.off()
        self.led_cold.on()
```

### Difficulty Scaling
Dynamic difficulty parameters:
```python
if self.mode == GameMode.EXTREME:
    self.min_number = 1
    self.max_number = 500
    self.max_guesses = 15
    self.time_limit = TIME_LIMIT_SECONDS
    
    # Start countdown timer
    self.timer_thread = threading.Thread(
        target=self._timer_countdown, 
        daemon=True
    )
    self.timer_thread.start()
```

### Hint System
Progressive hints based on attempts:
```python
def _show_hint(self):
    distance = abs(self.current_guess - self.target_number)
    range_size = self.max_number - self.min_number
    
    # Distance-based hints
    if distance <= range_size * 0.05:
        hint = "Very close! 🔥🔥🔥"
    elif distance <= range_size * 0.1:
        hint = "Getting warm! 🔥🔥"
        
    # Additional clues
    if self.target_number % 2 == 0:
        hint += " (Even)"
    else:
        hint += " (Odd)"
```

### Score Tracking
Persistent high score system:
```python
# Check for perfect game (optimal guesses)
optimal_guesses = math.ceil(math.log2(self.max_number - self.min_number + 1))
if self.guess_count <= optimal_guesses:
    self.perfect_games += 1
    
# Update high score
if mode_name not in self.best_scores or \
   self.guess_count < self.best_scores[mode_name]:
    self.best_scores[mode_name] = self.guess_count
    self._save_high_scores()
```

## Features

### Game Features
- Multiple difficulty modes
- Temperature-based feedback
- Progressive hint system
- Time-limited challenges
- Custom range settings
- Binary search practice

### Feedback Systems
- LED temperature indicators
- Audio feedback
- LCD status display
- 7-segment digit display
- Victory celebrations
- Progress tracking

### Educational Features
- Binary search mode
- Optimal guess tracking
- Strategy hints
- Performance analysis
- Learning statistics

### Persistence
- High score tracking
- Configuration saving
- Statistics logging
- Session history
- Player profiles

## Available Demos

1. **LED Demo**: Temperature indicator patterns
2. **Sound Demo**: Audio feedback examples
3. **Mode Demo**: All difficulty modes
4. **Perfect Game**: Optimal guessing strategy
5. **Stats Demo**: Performance analytics

## Troubleshooting

### Buttons not responding
- Check pull-up resistor configuration
- Verify GPIO connections
- Test with multimeter
- Check bounce time settings
- Clean button contacts

### LEDs not lighting
- Verify resistor values (220Ω)
- Check LED polarity
- Test GPIO pins
- Verify ground connections
- Check power supply

### LCD display issues
- Check I2C address
- Verify SDA/SCL connections
- Enable I2C interface
- Run i2cdetect -y 1
- Check pull-up resistors

### Buzzer problems
- Check polarity
- Verify GPIO pin
- Test with simple beep
- Check volume setting
- Verify power supply

### Score not saving
- Check file permissions
- Verify JSON format
- Check disk space
- Test write access
- Review error logs

## Advanced Usage

### Custom Difficulty Curves
Create progressive difficulty:
```python
class AdaptiveDifficulty:
    def __init__(self):
        self.player_skill = 0.5  # 0-1 scale
        
    def adjust_range(self, won, guesses, optimal):
        if won and guesses <= optimal:
            self.player_skill += 0.1
        elif not won:
            self.player_skill -= 0.05
            
        # Scale difficulty
        return int(100 * (1 + self.player_skill))
```

### Network Multiplayer
Compete with other players:
```python
import socket

class NetworkGame:
    def broadcast_guess(self, guess):
        message = {
            'player': self.player_name,
            'guess': guess,
            'timestamp': time.time()
        }
        self.socket.send(json.dumps(message).encode())
        
    def receive_opponent_guess(self):
        data = self.socket.recv(1024)
        opponent = json.loads(data.decode())
        self._display_opponent_progress(opponent)
```

### AI Opponent
Compete against AI strategies:
```python
class AIOpponent:
    def __init__(self, strategy="binary_search"):
        self.strategy = strategy
        self.low = 1
        self.high = 100
        
    def make_guess(self):
        if self.strategy == "binary_search":
            return (self.low + self.high) // 2
        elif self.strategy == "random":
            return random.randint(self.low, self.high)
        elif self.strategy == "sequential":
            return self.low
```

### Voice Control
Add speech recognition:
```python
import speech_recognition as sr

class VoiceControl:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
    def get_voice_guess(self):
        with self.microphone as source:
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio)
            return int(''.join(filter(str.isdigit, text)))
        except:
            return None
```

### Statistical Analysis
Track and analyze performance:
```python
class GameAnalytics:
    def analyze_session(self, games):
        stats = {
            'average_guesses': np.mean([g.guesses for g in games]),
            'guess_distribution': self._calculate_distribution(games),
            'improvement_rate': self._calculate_improvement(games),
            'optimal_ratio': self._calculate_optimal_ratio(games)
        }
        
        # Generate performance report
        self._plot_performance_graph(stats)
        return stats
```

## Integration Ideas

### Educational Platform
- Math learning integration
- Binary search teaching
- Probability lessons
- Strategy development
- Performance tracking

### Party Game System
- Multiple player support
- Tournament brackets
- Team challenges
- Leaderboards
- Prize integration

### Accessibility Features
- Audio-only mode
- Braille display support
- Voice commands
- Haptic feedback
- Adjustable timing

### Gamification
- Achievement system
- Experience points
- Unlockable modes
- Daily challenges
- Seasonal events

## Performance Optimization

### Response Time
- Debounce button inputs
- Optimize display updates
- Cache calculations
- Minimize I/O operations

### Memory Usage
- Limit history size
- Clear old sessions
- Optimize data structures
- Garbage collection

### Power Efficiency
- LED duty cycling
- Display sleep mode
- Reduced polling rates
- Smart wake detection

## Next Steps
- Add machine learning difficulty adjustment
- Implement online leaderboards
- Create mobile app companion
- Add pattern recognition hints
- Integrate with educational curriculum
- Develop tournament system
- Add augmented reality overlay