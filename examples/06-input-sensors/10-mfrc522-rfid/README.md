# MFRC522 RFID Reader/Writer

Read and write RFID/NFC cards and tags using the MFRC522 module with SPI communication.

## What You'll Learn
- RFID/NFC technology principles
- SPI communication protocol
- MIFARE Classic card structure
- Card authentication and security
- Access control system design
- Data storage on RFID cards
- Anti-collision algorithms

## Hardware Requirements
- Raspberry Pi 5
- MFRC522 RFID reader module
- MIFARE Classic 1K cards/tags (13.56MHz)
- Optional: LEDs for status indication
- Optional: Buzzer for audio feedback
- Optional: Button for mode selection
- Jumper wires

## Circuit Diagram

```
MFRC522 RFID Module:
┌─────────────────────────────┐
│     MFRC522 Module          │
│  ┌─────────────────────┐    │  13.56MHz RFID
│  │    Antenna Coil     │    │  Reader/Writer
│  │                     │    │
│  └─────────────────────┘    │
├─────────────────────────────┤
│SDA SCK MOSI MISO IRQ GND RST│
└─┬───┬────┬────┬────┬───┬───┬┘
  │   │    │    │    │   │   │
  │   │    │    │    │   │   └── GPIO22 (Reset)
  │   │    │    │    │   └────── GND
  │   │    │    │    └────────── Not used (IRQ)
  │   │    │    └─────────────── GPIO9 (MISO - SPI RX)
  │   │    └──────────────────── GPIO10 (MOSI - SPI TX)
  │   └───────────────────────── GPIO11 (SCK - SPI Clock)
  └───────────────────────────── GPIO8 (SDA - SPI CS)

Power: 3.3V (connect to 3.3V pin)

Note: Enable SPI: sudo raspi-config → Interface → SPI

Optional Indicators:
Status LED:   GPIO23 → 220Ω → LED → GND
Buzzer:       GPIO24 → Buzzer → GND
Mode Button:  GPIO25 → Button → GND (with pull-up)
```

## Software Dependencies

Install required libraries:
```bash
# SPI library
pip install spidev

# GPIO library
pip install gpiozero

# Enable SPI interface
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
```

## Running the Program

```bash
cd examples/06-input-sensors/10-mfrc522-rfid
python mfrc522-rfid.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test basic card reading
make access   # Run access control demo
make register # Run card registration
make install  # Install dependencies
```

## Code Walkthrough

### SPI Communication
Initialize SPI interface for MFRC522:
```python
def __init__(self):
    self.spi = spidev.SpiDev()
    self.spi.open(spi_bus, spi_device)
    self.spi.max_speed_hz = 1000000
    
    # Initialize reset pin
    self.reset_pin = OutputDevice(rst_pin)
```

### Card Detection
Wait for and detect RFID cards:
```python
def wait_for_card(self, timeout=None):
    while True:
        # Request card
        (status, TagType) = self.reader.request(PICC_REQIDL)
        
        if status == MI_OK:
            # Get UID
            (status, uid) = self.reader.anticoll()
            if status == MI_OK:
                uid_string = "-".join([f"{x:02X}" for x in uid[:4]])
                return uid_string
```

### Authentication and Data Access
Authenticate with card and read/write data:
```python
def read_card_data(self, uid_string, block=4):
    uid = [int(x, 16) for x in uid_string.split("-")]
    
    # Select card
    if not self.reader.select_tag(uid):
        return None
    
    # Authenticate with default key
    status = self.reader.auth(PICC_AUTHENT1A, block, self.default_key, uid)
    if status != MI_OK:
        return None
    
    # Read block
    data = self.reader.read(block)
    return data
```

### Database Management
Store and manage card information:
```python
def register_card(self, uid_string, name, access_level="user"):
    self.card_database[uid_string] = {
        'name': name,
        'access_level': access_level,
        'registered': datetime.now().isoformat(),
        'use_count': 0
    }
    self.save_database()
```

## Key Concepts

### RFID Technology
- **Frequency**: 13.56MHz (HF band)
- **Range**: 3-10cm depending on antenna size
- **Power**: Passive tags powered by reader field
- **Standards**: ISO14443 Type A (MIFARE)

### MIFARE Classic Structure
- **1K cards**: 1024 bytes total storage
- **Sectors**: 16 sectors of 64 bytes each
- **Blocks**: 4 blocks per sector (16 bytes each)
- **Access control**: Each sector has access keys

### Memory Layout
```
Sector 0: Manufacturer data (read-only)
├─ Block 0: UID + BCC + Manufacturer data
├─ Block 1: User data
├─ Block 2: User data  
└─ Block 3: Access keys + Access bits

Sectors 1-15: User data
├─ Block 0-2: User data (48 bytes per sector)
└─ Block 3: Access keys + Access bits
```

### Security Features
- **Authentication**: Key-based access control
- **Encryption**: CRYPTO1 stream cipher
- **Access bits**: Fine-grained permissions
- **Anti-collision**: Multiple card handling

## Available Demos

1. **Basic Card Reading**: Simple card detection and UID reading
2. **Access Control System**: Grant/deny access based on registered cards
3. **Card Registration**: Add/remove cards from system database
4. **Card Cloning Demo**: Read and write card data (educational)
5. **Attendance System**: Track check-in/check-out times

## Troubleshooting

### Reader not detected
- Check SPI connections (especially CS and RST pins)
- Verify SPI is enabled: `lsmod | grep spi`
- Check 3.3V power supply
- Ensure short, solid connections

### Cards not detected
- Verify card type (13.56MHz MIFARE Classic)
- Check antenna positioning (cards must be close)
- Test with known good cards
- Check for electromagnetic interference

### Authentication errors
- Verify card is MIFARE Classic compatible
- Check if card uses default keys (0xFF...)
- Some cards may have custom key schemes
- Ensure proper sector selection

### SPI communication errors
- Check SPI bus conflicts with other devices
- Verify SPI speed settings (max 10MHz)
- Ensure proper grounding
- Check cable length (keep short)

## Advanced Usage

### Custom Authentication Keys
Change default keys for better security:
```python
# Generate custom key
custom_key = [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC]

# Write new key to card (requires current key)
def change_sector_key(self, sector, old_key, new_key):
    # Authentication and key change logic
    pass
```

### Multiple Card Types
Support different card types:
```python
def detect_card_type(self, uid):
    # Send RATS command for ISO14443-4 cards
    # Check for MIFARE Ultralight, DESFire, etc.
    if self.is_mifare_classic(uid):
        return "MIFARE_CLASSIC"
    elif self.is_mifare_ultralight(uid):
        return "MIFARE_ULTRALIGHT"
    else:
        return "UNKNOWN"
```

### Secure Applications
Implement proper security measures:
```python
class SecureRFIDSystem:
    def __init__(self):
        # Use encrypted database
        # Implement key rotation
        # Add audit logging
        # Use hardware security module
        pass
    
    def secure_authenticate(self, uid):
        # Challenge-response authentication
        # Time-based tokens
        # Replay attack prevention
        pass
```

### High-Speed Reading
Optimize for multiple rapid card reads:
```python
def rapid_scan_mode(self):
    # Reduce timeouts
    # Cache authentication
    # Batch operations
    # Use interrupts for card detection
    pass
```

## Security Considerations

### MIFARE Classic Vulnerabilities
- **Known weaknesses**: CRYPTO1 algorithm has been broken
- **Cloning attacks**: Cards can be duplicated
- **Eavesdropping**: Communication can be intercepted
- **Rollback attacks**: Previous card states can be restored

### Best Practices
1. **Never rely solely on card UID** for security
2. **Use additional authentication** (PIN, biometrics)
3. **Implement server-side validation**
4. **Regular key rotation** and access audits
5. **Monitor for cloned cards** (usage patterns)

### Secure Implementation
```python
def secure_access_check(self, uid, pin=None):
    # Multi-factor authentication
    if not self.validate_uid(uid):
        return False
    
    if pin and not self.validate_pin(uid, pin):
        return False
    
    # Check against server database
    if not self.server_validate(uid):
        return False
    
    return True
```

## Performance Optimization

### Read/Write Speed
- **Batch operations**: Read/write multiple blocks
- **Authentication caching**: Avoid re-authentication
- **Proximity detection**: Quick presence checks
- **Interrupt-driven**: React to card presence

### Error Handling
- **Retry logic**: Handle transient failures
- **Timeout management**: Prevent hanging operations
- **Graceful degradation**: Fallback modes
- **Logging**: Track errors and performance

## Applications

### Access Control
- Building entry systems
- Computer login authentication
- Vehicle access control
- Equipment usage tracking

### Payment Systems
- Campus card systems
- Transit fare collection
- Vending machine payments
- Loyalty card programs

### Identification
- Employee ID badges
- Student identification
- Library card systems
- Event ticketing

### Asset Tracking
- Inventory management
- Tool tracking
- Document control
- Equipment checkout

## Legal and Ethical Considerations

### Responsible Use
- **Educational purposes**: Learning RFID technology
- **Authorization required**: Only test with owned cards
- **Privacy respect**: Don't clone personal cards
- **Legal compliance**: Follow local laws and regulations

### Legitimate Applications
- Security research and testing
- Backup of personal cards
- Educational demonstrations
- System development and testing

## Next Steps
- Implement advanced encryption schemes
- Add support for multiple card types
- Create a web-based management interface
- Integrate with external databases
- Develop mobile app integration
- Add biometric authentication
- Implement blockchain-based verification