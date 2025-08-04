# RFID Welcome System

Personalized greeting system using RFID cards with multi-mode greetings, user tracking, LCD display, and optional text-to-speech capabilities.

## What You'll Learn
- RFID card reading and authentication
- User database management
- Personalized greeting generation
- Multi-mode system design
- Visit tracking and statistics
- LCD display integration
- Audio feedback patterns
- Text-to-speech integration

## Hardware Requirements
- Raspberry Pi 5
- MFRC522 RFID reader module
- MIFARE Classic 1K RFID cards/tags
- 16x2 LCD display with I2C backpack
- 4x LEDs for status indication (including 2 PWM LEDs)
- 2x Buzzers for audio feedback
- 3x Push buttons for control
- Jumper wires
- Breadboard
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)

## Circuit Diagram

```
RFID Welcome System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ MFRC522 RFID Reader (SPI):                                 │
│ SDA (CE0) ── GPIO8                                         │
│ SCK ────── GPIO11 (SPI Clock)                              │
│ MOSI ───── GPIO10 (SPI MOSI)                               │
│ MISO ───── GPIO9  (SPI MISO)                               │
│ RST ────── GPIO22                                          │
│ 3.3V ───── 3.3V                                            │
│ GND ────── GND                                             │
│                                                             │
│ I2C LCD Display:                                           │
│ SDA ────── GPIO2 (I2C Data)                                │
│ SCL ────── GPIO3 (I2C Clock)                               │
│ VCC ────── 5V                                              │
│ GND ────── GND                                             │
│                                                             │
│ Status LEDs:                                                │
│ SCAN LED ──── GPIO17 (PWM, breathing effect)               │
│ SUCCESS LED ─ GPIO18                                       │
│ ERROR LED ─── GPIO27                                       │
│ GREETING LED ─ GPIO23 (PWM, pulse effect)                  │
│                                                             │
│ Audio Feedback:                                             │
│ WELCOME BUZZER ─ GPIO24                                     │
│ ALERT BUZZER ─── GPIO25                                     │
│                                                             │
│ Control Buttons:                                            │
│ REGISTER BTN ─ GPIO26                                       │
│ MODE BTN ───── GPIO19                                       │
│ MUTE BTN ───── GPIO20                                       │
└─────────────────────────────────────────────────────────────┘

MFRC522 RFID Reader Connections:
┌─────────────────┐
│   MFRC522       │
├─────────────────┤
│ SDA ── GPIO8    │  (SPI Chip Enable 0)
│ SCK ── GPIO11   │  (SPI Clock)
│ MOSI ─ GPIO10   │  (SPI Master Out Slave In)
│ MISO ─ GPIO9    │  (SPI Master In Slave Out)
│ IRQ ── NC       │  (Not connected)
│ GND ── GND      │
│ RST ── GPIO22   │  (Reset)
│ 3.3V ─ 3.3V     │  (IMPORTANT: 3.3V only!)
└─────────────────┘

LCD Display (16x2 with I2C backpack):
┌─────────────────┐
│   LCD Display   │
├─────────────────┤
│ VCC ── 5V       │
│ GND ── GND      │
│ SDA ── GPIO2    │  (I2C Data)
│ SCL ── GPIO3    │  (I2C Clock)
└─────────────────┘

LED Connections (with 220Ω resistors):
SCAN LED:     GPIO17 ── 220Ω ── LED ── GND (PWM)
SUCCESS LED:  GPIO18 ── 220Ω ── LED ── GND
ERROR LED:    GPIO27 ── 220Ω ── LED ── GND
GREETING LED: GPIO23 ── 220Ω ── LED ── GND (PWM)

Buzzer Connections:
WELCOME:      GPIO24 ── Buzzer ── GND
ALERT:        GPIO25 ── Buzzer ── GND

Button Connections (with internal pull-up):
REGISTER:     GPIO26 ── Button ── GND
MODE:         GPIO19 ── Button ── GND
MUTE:         GPIO20 ── Button ── GND

WARNING: MFRC522 operates at 3.3V logic level!
Do NOT connect to 5V or damage will occur.
```

## Software Dependencies

Install required libraries:
```bash
# SPI and GPIO control
pip install spidev gpiozero

# I2C for LCD
pip install smbus2

# Enable SPI and I2C interfaces
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
# Navigate to: Interface Options → I2C → Enable

# Optional: Text-to-speech
sudo apt install espeak
```

## Running the Program

```bash
cd examples/08-extension-projects/05-welcome
python rfid-welcome-system.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Registration demo
make test     # Test all components
make users    # Manage user database
make setup    # Install dependencies
```

## Code Walkthrough

### RFID Reader Initialization
Custom MFRC522 driver implementation:
```python
class MFRC522:
    def __init__(self, spi_device=0, spi_bus=0):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000
        self._init_device()
    
    def _init_device(self):
        self._reset()
        self._write_register(TModeReg, 0x8D)
        self._write_register(TPrescalerReg, 0x3E)
        self._antenna_on()
```

### Card Detection and Reading
Continuous scanning for RFID cards:
```python
def _scanning_loop(self):
    while self.scanning_active:
        # Request card
        (status, tag_type) = self.rfid.request()
        
        if status == 0:
            # Get card UID
            (status, uid) = self.rfid.anticoll()
            
            if status == 0:
                # Convert UID to string
                card_id = ''.join([f'{byte:02X}' for byte in uid])
                self._process_card_scan(card_id)
```

### User Recognition System
Check registered users and track visits:
```python
def _process_card_scan(self, card_id):
    if card_id in self.users:
        user = self.users[card_id]
        user['visits'] += 1
        user['last_seen'] = datetime.now().isoformat()
        
        print(f"👤 Card recognized: {user['name']}")
        self._greet_user(user)
    else:
        print(f"❓ Unknown card: {card_id}")
        self._handle_unknown_card(card_id)
```

### Personalized Greeting Generation
Multiple greeting modes with customization:
```python
def _generate_greeting(self, name, custom_greeting, visits, last_seen):
    mode = self.greeting_modes[self.current_mode]
    
    if mode == "time_based":
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return f"Good morning, {name}!"
        elif 12 <= hour < 17:
            return f"Good afternoon, {name}!"
        elif 17 <= hour < 21:
            return f"Good evening, {name}!"
        else:
            return f"Good night, {name}!"
    
    elif mode == "custom" and custom_greeting:
        return custom_greeting.replace("{name}", name)
```

### Audio Feedback Patterns
Different sound patterns for different users:
```python
def _play_greeting_sound(self, pattern="default"):
    patterns = {
        'default': [(0.1, 0.1), (0.1, 0.1), (0.2, 0.0)],
        'vip': [(0.1, 0.05)] * 5 + [(0.3, 0.0)],
        'simple': [(0.2, 0.0)],
        'melody': [(0.1, 0.1), (0.15, 0.1), (0.1, 0.1), (0.2, 0.0)]
    }
    
    pattern_sequence = patterns.get(pattern, patterns['default'])
    for duration, pause in pattern_sequence:
        self.welcome_buzzer.beep(duration, pause, n=1)
```

## Greeting Modes

### 1. Standard Mode
Simple welcome message:
- **Format**: "Welcome, [Name]!"
- **Use Case**: Basic greeting for all users
- **Customization**: None

### 2. Time-Based Mode
Greetings based on time of day:
- **Morning**: "Good morning, [Name]!"
- **Afternoon**: "Good afternoon, [Name]!"
- **Evening**: "Good evening, [Name]!"
- **Night**: "Good night, [Name]!"

### 3. Custom Mode
User-specific custom greetings:
- **Format**: User-defined with {name} placeholder
- **Examples**: "Welcome aboard, Captain {name}!"
- **Use Case**: VIP users, special roles

### 4. Silent Mode
Visual acknowledgment only:
- **No audio**: Muted greeting sounds
- **LCD only**: Display name and visit count
- **Use Case**: Quiet environments

## User Management Features

### Registration Process
- Press REGISTER button to enter registration mode
- Scan new RFID card within 30 seconds
- System automatically assigns default profile
- Customize user settings via JSON file

### User Data Structure
```json
{
  "A1B2C3D4": {
    "name": "Alice",
    "greeting": "Welcome back, {name}! Have a great day!",
    "registered": "2024-01-15T10:30:00",
    "last_seen": "2024-01-15T14:22:30",
    "visits": 23,
    "sound_pattern": "vip",
    "tts_enabled": true
  }
}
```

### Visit Tracking
- Automatic visit counting
- Last seen timestamp
- Daily activity statistics
- Success rate monitoring

## Available Demos

1. **Interactive System**: Real-time card scanning with live display
2. **Registration Demo**: Simulate user registration process
3. **Statistics Review**: View system usage statistics
4. **User Management**: Add, edit, or remove users

## Troubleshooting

### RFID reader not detecting cards
- Check SPI is enabled: `ls /dev/spi*`
- Verify 3.3V power (NOT 5V!)
- Check SPI connections (especially clock and data)
- Ensure antenna is properly connected
- Test with known working card

### Card read errors
- Clean card and reader surface
- Check card compatibility (MIFARE Classic)
- Increase scan distance (2-5cm optimal)
- Verify SPI speed settings
- Check for electromagnetic interference

### LCD display issues
- Verify I2C address: `i2cdetect -y 1`
- Check I2C connections (SDA/SCL)
- Ensure 5V power to LCD backpack
- Adjust contrast potentiometer
- Test with simple I2C script

### Audio not working
- Check buzzer polarity
- Verify GPIO pin connections
- Test buzzers individually
- Check audio mute status
- Ensure espeak is installed for TTS

## Advanced Usage

### Custom Sound Patterns
Create unique greeting sounds:
```python
# Add to patterns dictionary
'executive': [(0.05, 0.05)] * 8 + [(0.4, 0.0)],
'birthday': [(0.1, 0.1), (0.2, 0.1), (0.1, 0.1), (0.3, 0.0)],
'alarm': [(0.3, 0.1), (0.3, 0.1), (0.3, 0.0)]
```

### Multi-Language Support
Implement language-specific greetings:
```python
def _generate_multilingual_greeting(self, name, language='en'):
    greetings = {
        'en': f"Welcome, {name}!",
        'es': f"¡Bienvenido, {name}!",
        'fr': f"Bienvenue, {name}!",
        'de': f"Willkommen, {name}!",
        'jp': f"ようこそ、{name}さん！"
    }
    return greetings.get(language, greetings['en'])
```

### Access Control Integration
Use for door access with logging:
```python
def grant_access(self, user, door_id):
    access_log = {
        'timestamp': datetime.now().isoformat(),
        'user': user['name'],
        'card_id': self.last_scanned_card,
        'door': door_id,
        'granted': True
    }
    
    # Activate door lock relay
    door_relay.on()
    time.sleep(3)  # Keep door unlocked for 3 seconds
    door_relay.off()
    
    # Log access event
    self.access_history.append(access_log)
```

### Web Dashboard Integration
Display real-time statistics:
```python
from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'users': len(system.users),
        'scans_today': system.get_daily_scans(),
        'active_users': system.get_active_users(),
        'success_rate': system.get_statistics()['success_rate']
    })

@app.route('/api/recent_activity')
def recent_activity():
    return jsonify(system.scan_history[-10:])
```

### Database Backend
Store user data in SQLite:
```python
import sqlite3

class UserDatabase:
    def __init__(self, db_path='rfid_users.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                card_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                greeting TEXT,
                sound_pattern TEXT DEFAULT 'default',
                registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visits INTEGER DEFAULT 0,
                last_seen TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                action TEXT,
                FOREIGN KEY (card_id) REFERENCES users(card_id)
            )
        ''')
```

## Performance Optimization

### SPI Communication
- Optimize SPI clock speed for reliability
- Implement retry mechanism for failed reads
- Use hardware SPI for better performance
- Add timeout handling for stuck communications

### Memory Management
- Limit scan history size with circular buffer
- Implement log rotation for long-term operation
- Cache frequently accessed user data
- Use generators for large data processing

### Power Efficiency
- Reduce scan frequency during idle periods
- Implement sleep mode for night hours
- Use interrupt-driven card detection
- Optimize LED brightness for power saving

## Integration Ideas

### Office Environment
- Employee time tracking
- Meeting room access control
- Visitor management system
- Personalized workstation setup

### Smart Home
- Family member recognition
- Guest welcome messages
- Automated home settings
- Security integration

### Educational Settings
- Student attendance tracking
- Library access management
- Lab equipment checkout
- Personalized learning stations

### Retail Applications
- VIP customer recognition
- Staff time management
- Loyalty program integration
- Personalized shopping experience

## Next Steps
- Add facial recognition for dual-factor authentication
- Implement mobile app for remote user management
- Create cloud synchronization for multiple locations
- Add voice recognition for hands-free operation
- Integrate with existing access control systems
- Develop analytics dashboard for usage patterns
- Add support for multiple card types (NFC, etc.)