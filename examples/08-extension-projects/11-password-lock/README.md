# Keypad Security System

Advanced password lock system with 4x4 matrix keypad, multiple user accounts, security levels, temporary access codes, and comprehensive access logging.

## What You'll Learn
- Matrix keypad scanning techniques
- Multi-user authentication systems
- Password hashing and security
- Access control implementation
- Temporary code generation
- Security logging and auditing
- Anti-tampering measures
- Emergency access procedures

## Hardware Requirements
- Raspberry Pi 5
- 4x4 Matrix Keypad
- 3x LEDs (Red for locked, Green for unlocked, Yellow for alert)
- Electronic lock relay or solenoid
- Buzzer for audio feedback
- 2x Hidden buttons (Reset and Emergency)
- 16x2 LCD display with I2C backpack
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ) for keypad if needed
- 5V relay module for lock control
- Jumper wires and breadboard

## Circuit Diagram

```
Keypad Security System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ 4x4 Matrix Keypad:                                          │
│ ROW1 ─────────── GPIO17                                    │
│ ROW2 ─────────── GPIO27                                    │
│ ROW3 ─────────── GPIO22                                    │
│ ROW4 ─────────── GPIO23                                    │
│ COL1 ─────────── GPIO24                                    │
│ COL2 ─────────── GPIO25                                    │
│ COL3 ─────────── GPIO8                                     │
│ COL4 ─────────── GPIO7                                     │
│                                                             │
│ Security Indicators:                                        │
│ LOCKED LED ───── GPIO5  (Red - System locked)             │
│ UNLOCKED LED ─── GPIO6  (Green - Access granted)          │
│ ALERT LED ────── GPIO13 (Yellow - Warning/Alert)          │
│                                                             │
│ Access Control:                                             │
│ LOCK RELAY ───── GPIO19 (Electronic lock control)         │
│ ALARM BUZZER ─── GPIO26 (Audio feedback/alarm)            │
│                                                             │
│ Hidden Controls:                                            │
│ RESET BUTTON ─── GPIO20 (Factory reset - hold 10s)        │
│ EMERGENCY BTN ── GPIO21 (Emergency unlock)                │
│                                                             │
│ LCD Display:                                                │
│ SDA ─────────── GPIO2  (I2C Data)                         │
│ SCL ─────────── GPIO3  (I2C Clock)                        │
└─────────────────────────────────────────────────────────────┘

4x4 Matrix Keypad Layout:
┌─────────────────────────────────────────────────────────────┐
│                    KEYPAD LAYOUT                            │
│                                                             │
│                 ┌─────┬─────┬─────┬─────┐                 │
│                 │  1  │  2  │  3  │  A  │                 │
│                 ├─────┼─────┼─────┼─────┤                 │
│                 │  4  │  5  │  6  │  B  │                 │
│                 ├─────┼─────┼─────┼─────┤                 │
│                 │  7  │  8  │  9  │  C  │                 │
│                 ├─────┼─────┼─────┼─────┤                 │
│                 │  *  │  0  │  #  │  D  │                 │
│                 └─────┴─────┴─────┴─────┘                 │
│                                                             │
│ Key Functions:                                              │
│ 0-9: Numeric input                                          │
│ *:   Clear input                                            │
│ #:   Submit code                                            │
│ A:   Add user (Admin only)                                  │
│ B:   Change password                                        │
│ C:   Create temp code (Admin only)                          │
│ D:   Lock system                                            │
└─────────────────────────────────────────────────────────────┘

Matrix Keypad Connection:
┌─────────────────────────────────────────────────────────────┐
│ Keypad scanning works by setting each row LOW sequentially │
│ and reading which column goes LOW when a key is pressed    │
│                                                             │
│ ROW pins: Output (GPIO17, 27, 22, 23)                     │
│ COL pins: Input with pull-up (GPIO24, 25, 8, 7)           │
└─────────────────────────────────────────────────────────────┘

Lock Relay Connection:
┌─────────────────────────────────────────────────────────────┐
│     GPIO19 ──┬── Relay Module ── Lock Power               │
│              │                                              │
│              └── LED indicator (optional)                   │
│                                                             │
│ Relay energized = Door unlocked                            │
│ Relay de-energized = Door locked (fail-secure)            │
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
cd examples/08-extension-projects/11-password-lock
python keypad-security-system.py
```

Or use the Makefile:
```bash
make          # Run the security system
make demo     # Security features demo
make test     # Test all components
make users    # Show user management
make setup    # Install dependencies
```

## Default Access Codes

⚠️ **IMPORTANT**: Change these immediately!
- Master: `1234`
- Admin: `9876`

## Code Walkthrough

### Matrix Keypad Scanning
Efficient row-column scanning technique:
```python
class MatrixKeypad:
    def scan(self):
        for row_idx, row in enumerate(self.rows):
            # Set current row low
            row.off()
            
            # Check each column
            for col_idx, col in enumerate(self.cols):
                if not col.is_pressed:  # Active low
                    key = self.KEYS[row_idx][col_idx]
                    break
            
            # Set row back to high
            row.on()
```

### Secure Password Storage
Using SHA-256 hashing:
```python
def verify_code(self, code):
    # Never store plaintext passwords
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    return code_hash == self.code_hash
```

### Multi-Level Access Control
User permission system:
```python
class SecurityLevel(Enum):
    USER = "User"        # Basic access
    ADMIN = "Admin"      # User management
    MASTER = "Master"    # Full control
    TEMPORARY = "Temp"   # Time-limited
    EMERGENCY = "Emergency"
```

### Temporary Access Codes
Time-limited access generation:
```python
def set_temporary_code(self, code, duration=300):
    self.temp_code_hash = hashlib.sha256(code.encode()).hexdigest()
    self.temp_code_expires = datetime.now() + timedelta(seconds=duration)
```

### Anti-Brute Force Protection
Lockout after failed attempts:
```python
if self.failed_attempts >= MAX_ATTEMPTS:
    self.lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_TIME)
    # System locked for 5 minutes
```

## Security Features

### 1. User Management
- Multiple user accounts
- Different security levels
- Individual access tracking
- Password change capability

### 2. Access Control
- Secure password hashing
- No plaintext storage
- Session timeout
- Auto-lock feature

### 3. Temporary Codes
- One-time or time-limited access
- Automatic expiration
- Guest access capability
- Contractor/service access

### 4. Security Measures
- Brute force protection
- Failed attempt lockout
- Tamper detection
- Duress code support

### 5. Emergency Features
- Emergency unlock button
- Duress alarm (silent)
- Factory reset option
- Fail-secure design

### 6. Logging & Audit
- All access attempts logged
- User activity tracking
- Time-stamped events
- JSON log export

## Operating Modes

### Normal Operation
1. Enter access code
2. Press # to submit
3. System unlocks if valid
4. Auto-locks after timeout

### Admin Functions
After login, admins can:
- Press A: Add new user
- Press B: Change password
- Press C: Create temp code
- Press D: Lock system

### Emergency Procedures
- Emergency button: Immediate unlock
- Duress code: Code ending in '99' triggers silent alarm
- Factory reset: Hold reset button 10 seconds

## Available Demos

1. **Security Demo**: Shows all security states
2. **Access Demo**: Demonstrates login process
3. **Lockout Demo**: Shows brute force protection
4. **Admin Demo**: User management features

## Troubleshooting

### Keypad not responding
- Check row/column connections
- Verify GPIO pin assignments
- Test with multimeter
- Check pull-up resistors
- Verify power supply

### Code not accepted
- Verify code length (4-8 digits)
- Check caps lock isn't on
- Ensure not in lockout
- Verify user exists
- Check system time

### LCD display issues
- Check I2C address (0x27)
- Verify I2C connections
- Enable I2C interface
- Run i2cdetect
- Check power supply

### Lock not operating
- Test relay module
- Check relay power
- Verify GPIO output
- Test with LED first
- Check lock voltage

### System lockouts
- Wait for timeout period
- Use emergency unlock
- Perform factory reset
- Check system logs

## Advanced Usage

### Custom Security Policies
Implement organization-specific rules:
```python
# Require longer passwords
CODE_MIN_LENGTH = 6
CODE_MAX_LENGTH = 12

# Shorter lockout time
LOCKOUT_TIME = 180  # 3 minutes

# More login attempts
MAX_ATTEMPTS = 5
```

### Integration with Access Systems
Connect to existing infrastructure:
```python
def verify_with_ldap(self, username, code):
    # Integrate with LDAP/Active Directory
    import ldap
    # Authentication code here
    
def sync_users_from_database(self):
    # Sync with central database
    import mysql.connector
    # Database sync code here
```

### Remote Management
Web interface for administration:
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    return jsonify([
        {'name': u.name, 'level': u.level.value}
        for u in system.users.values()
    ])

@app.route('/api/access-log')
def get_access_log():
    return jsonify(list(system.access_log))
```

### Biometric Integration
Add fingerprint authentication:
```python
class BiometricAuth:
    def __init__(self, sensor_pin):
        self.sensor = FingerprintSensor(sensor_pin)
    
    def verify_fingerprint(self):
        template = self.sensor.read_fingerprint()
        return self.match_template(template)
```

### Time-Based Access
Schedule-based permissions:
```python
def check_time_restriction(self, user):
    current_hour = datetime.now().hour
    
    # Business hours only (9 AM - 6 PM)
    if user.level == SecurityLevel.USER:
        return 9 <= current_hour < 18
    
    # Admins have 24/7 access
    return True
```

## Security Best Practices

### Password Policy
- Minimum 6 characters
- Change default codes immediately
- Regular password rotation
- No sequential numbers
- No repeated digits

### Physical Security
- Hide emergency buttons
- Secure wiring
- Tamper-evident enclosure
- Camera integration
- Motion detection

### Operational Security
- Regular log review
- User access audits
- Remove unused accounts
- Test emergency procedures
- Update firmware

## Integration Ideas

### Smart Home Integration
- Home automation systems
- Voice assistant control
- Mobile app access
- Remote monitoring
- Automation triggers

### Office Security
- Time and attendance
- Room access control
- Equipment protection
- Visitor management
- Compliance logging

### Industrial Applications
- Machine lockout
- Hazardous area control
- Shift-based access
- Safety interlocks
- Maintenance mode

### Educational Projects
- Locker systems
- Lab access control
- Equipment checkout
- Study room booking
- Project storage

## Performance Optimization

### Keypad Responsiveness
- Optimize scan rate
- Implement interrupts
- Debounce in hardware
- Priority queuing

### Database Efficiency
- Index access logs
- Periodic log rotation
- Compressed storage
- Efficient queries

### Power Management
- Sleep mode when idle
- Wake on keypress
- Low power indicators
- Battery backup

## Next Steps
- Add RFID card support for two-factor authentication
- Implement facial recognition with camera
- Create mobile app for remote management
- Add SMS/email notifications for access events
- Integrate with building management systems
- Implement blockchain-based audit trail
- Add voice code entry for accessibility
