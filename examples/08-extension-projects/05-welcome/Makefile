# Makefile for RFID Welcome System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := rfid-welcome-system.py

# User database file
USER_DB := rfid_users.json

# Phony targets
.PHONY: run test demo register stats users spi lcd buttons leds audio setup install clean help

# Run the main program
run:
	@echo "Starting RFID Welcome System..."
	@$(PYTHON) $(PROGRAM)

# Test all hardware components
test:
	@echo "Testing RFID welcome system hardware..."
	@echo "1. Testing SPI interface..."
	@ls /dev/spi* >/dev/null 2>&1 && echo "✓ SPI interface available" || echo "❌ SPI not enabled"
	@$(MAKE) lcd
	@$(MAKE) buttons
	@$(MAKE) leds
	@$(MAKE) audio

# Run registration demo
demo:
	@echo "Running RFID registration demo..."
	@$(PYTHON) -c "from rfid_welcome_system import RFIDWelcomeSystem; import time; system = RFIDWelcomeSystem(); print('Demo: Simulating card registration...'); time.sleep(1); system._enter_registration_mode(); time.sleep(2); print('Demo: Registration complete'); system.cleanup()"

# Interactive registration
register:
	@echo "Starting RFID card registration..."
	@echo "Press REGISTER button on the device or Ctrl+C to cancel"
	@$(PYTHON) -c "from rfid_welcome_system import RFIDWelcomeSystem; system = RFIDWelcomeSystem(); print('System ready. Press REGISTER button to add new cards.'); system.run()"

# View system statistics
stats:
	@echo "RFID Welcome System Statistics"
	@echo "=============================="
	@if [ -f "$(USER_DB)" ]; then \
		$(PYTHON) -c "import json; users = json.load(open('$(USER_DB)')); \
		total_users = len(users); \
		total_visits = sum(user.get('visits', 0) for user in users.values()); \
		print(f'Total registered users: {total_users}'); \
		print(f'Total visits: {total_visits}'); \
		print(f'Average visits per user: {total_visits/total_users if total_users > 0 else 0:.1f}'); \
		print('\nTop visitors:'); \
		sorted_users = sorted(users.items(), key=lambda x: x[1].get('visits', 0), reverse=True)[:5]; \
		[print(f'  {user[\"name\"]}: {user.get(\"visits\", 0)} visits') for _, user in sorted_users]" 2>/dev/null || echo "Error reading user database"; \
	else \
		echo "No user database found"; \
	fi

# Manage users
users:
	@echo "Registered Users"
	@echo "================"
	@if [ -f "$(USER_DB)" ]; then \
		$(PYTHON) -c "import json; users = json.load(open('$(USER_DB)')); \
		print(f'Total users: {len(users)}\\n'); \
		for card_id, user in sorted(users.items(), key=lambda x: x[1]['name']): \
			print(f'Card ID: {card_id}'); \
			print(f'  Name: {user[\"name\"]}'); \
			print(f'  Visits: {user.get(\"visits\", 0)}'); \
			print(f'  Last seen: {user.get(\"last_seen\", \"Never\")}'); \
			print(f'  Sound: {user.get(\"sound_pattern\", \"default\")}'); \
			print(f'  TTS: {\"Enabled\" if user.get(\"tts_enabled\", False) else \"Disabled\"}'); \
			print()" 2>/dev/null || echo "Error reading user database"; \
	else \
		echo "No users registered yet"; \
	fi

# Test SPI interface
spi:
	@echo "Testing SPI interface..."
	@ls /dev/spi* >/dev/null 2>&1 && echo "✓ SPI devices found:" || echo "❌ No SPI devices found"
	@ls /dev/spi* 2>/dev/null || true
	@$(PYTHON) -c "import spidev; spi = spidev.SpiDev(); print('✓ spidev module available'); spi.open(0, 0); print('✓ SPI bus 0, device 0 accessible'); spi.close()" 2>/dev/null || echo "❌ SPI test failed - check if SPI is enabled"

# Test LCD display
lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); from lcd1602 import LCD1602; import time; lcd = LCD1602(0x27); lcd.clear(); lcd.write(0, 0, 'RFID Welcome'); lcd.write(1, 0, 'System Ready'); print('✓ LCD test message displayed'); time.sleep(2); lcd.clear()" 2>/dev/null || echo "❌ LCD test failed - check I2C connection"

# Test control buttons
buttons:
	@echo "Testing control buttons (press each button, 10 seconds)..."
	@$(PYTHON) -c "from gpiozero import Button; import time; buttons = {'REGISTER': Button(26), 'MODE': Button(19), 'MUTE': Button(20)}; print('Press each button:'); start = time.time(); \
	while time.time() - start < 10: \
		pressed = [name for name, btn in buttons.items() if btn.is_pressed]; \
		if pressed: print(f'  Pressed: {pressed}'); \
		time.sleep(0.1); \
	[btn.close() for btn in buttons.values()]; \
	print('Button test complete')" 2>/dev/null || echo "❌ Button test failed"

# Test status LEDs
leds:
	@echo "Testing status LEDs..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; \
	leds = {'SCAN': PWMLED(17), 'SUCCESS': LED(18), 'ERROR': LED(27), 'GREETING': PWMLED(23)}; \
	print('Testing LEDs...'); \
	[led.on() for led in leds.values()]; time.sleep(1); \
	[led.off() for led in leds.values()]; \
	print('Testing PWM effects...'); \
	leds['SCAN'].pulse(); leds['GREETING'].pulse(); time.sleep(2); \
	[led.close() for led in leds.values()]; \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test audio feedback
audio:
	@echo "Testing audio buzzers..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	welcome = Buzzer(24); alert = Buzzer(25); \
	print('Testing welcome buzzer...'); \
	welcome.beep(0.1, 0.1, n=3); time.sleep(1); \
	print('Testing alert buzzer...'); \
	alert.beep(0.2, 0.2, n=2); \
	welcome.close(); alert.close(); \
	print('✓ Audio test complete')" 2>/dev/null || echo "❌ Audio test failed"

# Setup system and dependencies
setup:
	@echo "Setting up RFID Welcome System..."
	@echo "Installing Python libraries..."
	@pip install spidev gpiozero smbus2
	@echo "Installing text-to-speech (optional)..."
	@sudo apt update && sudo apt install -y espeak || echo "⚠ TTS installation skipped"
	@echo "Enabling SPI and I2C interfaces..."
	@sudo raspi-config nonint do_spi 0 || echo "⚠ SPI may need manual configuration"
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating initial user database..."
	@test -f $(USER_DB) || echo '{}' > $(USER_DB)
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install spidev gpiozero smbus2

# Add a test user
adduser:
	@echo "Adding test user to database..."
	@$(PYTHON) -c "import json; \
	users = json.load(open('$(USER_DB)')) if os.path.exists('$(USER_DB)') else {}; \
	test_card = 'TEST1234'; \
	users[test_card] = { \
		'name': 'Test User', \
		'greeting': 'Welcome, {name}! This is a test.', \
		'registered': '2024-01-01T00:00:00', \
		'visits': 0, \
		'sound_pattern': 'vip', \
		'tts_enabled': True \
	}; \
	json.dump(users, open('$(USER_DB)', 'w'), indent=2); \
	print(f'✓ Test user added with card ID: {test_card}')" 2>/dev/null || echo "❌ Failed to add test user"

# Monitor RFID scanning
monitor:
	@echo "Monitoring RFID card scans (Ctrl+C to stop)..."
	@$(PYTHON) -c "from rfid_welcome_system import MFRC522; import time; \
	rfid = MFRC522(); \
	print('Place RFID card near reader...'); \
	try: \
		while True: \
			(status, tag_type) = rfid.request(); \
			if status == 0: \
				(status, uid) = rfid.anticoll(); \
				if status == 0: \
					card_id = ''.join([f'{byte:02X}' for byte in uid]); \
					print(f'Card detected: {card_id}'); \
					time.sleep(1); \
			time.sleep(0.1); \
	except KeyboardInterrupt: \
		print('\\nMonitoring stopped')" 2>/dev/null || echo "❌ RFID monitoring failed"

# Test text-to-speech
tts:
	@echo "Testing text-to-speech..."
	@which espeak >/dev/null 2>&1 && echo "✓ espeak installed" || echo "❌ espeak not found"
	@espeak "Welcome to the RFID system" 2>/dev/null && echo "✓ TTS working" || echo "❌ TTS test failed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Note: Keeping $(USER_DB) and scan_history.json"
	@echo "Use 'make reset' to clear all data"

# Reset all data
reset:
	@echo "Resetting all user data..."
	@rm -f $(USER_DB) scan_history.json
	@echo "✓ User database and scan history cleared"

# System status
status:
	@echo "RFID Welcome System Status"
	@echo "=========================="
	@echo "Hardware:"
	@ls /dev/spi* >/dev/null 2>&1 && echo "  ✓ SPI interface enabled" || echo "  ❌ SPI interface disabled"
	@test -e /dev/i2c-1 && echo "  ✓ I2C interface enabled" || echo "  ❌ I2C interface disabled"
	@i2cdetect -y 1 2>/dev/null | grep -q "27" && echo "  ✓ LCD detected at 0x27" || echo "  ⚪ No LCD detected"
	@echo "Software:"
	@$(PYTHON) -c "import spidev; print('  ✓ spidev installed')" 2>/dev/null || echo "  ❌ spidev not available"
	@$(PYTHON) -c "import gpiozero; print('  ✓ gpiozero installed')" 2>/dev/null || echo "  ❌ gpiozero not available"
	@$(PYTHON) -c "import smbus2; print('  ✓ smbus2 installed')" 2>/dev/null || echo "  ❌ smbus2 not available"
	@which espeak >/dev/null 2>&1 && echo "  ✓ espeak (TTS) installed" || echo "  ⚪ espeak not installed (optional)"
	@echo "Data:"
	@test -f $(USER_DB) && echo "  ✓ User database exists" || echo "  ⚪ No user database"
	@if [ -f "$(USER_DB)" ]; then \
		users=$$($(PYTHON) -c "import json; print(len(json.load(open('$(USER_DB)'))))" 2>/dev/null || echo "0"); \
		echo "  → $$users registered users"; \
	fi

# Help
help:
	@echo "RFID Welcome System"
	@echo "==================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run      - Run the main program (default)"
	@echo "  make test     - Test all hardware components"
	@echo "  make demo     - Run registration demo"
	@echo "  make register - Interactive card registration"
	@echo "  make stats    - View system statistics"
	@echo "  make users    - List all registered users"
	@echo ""
	@echo "Hardware Testing:"
	@echo "  make spi      - Test SPI interface"
	@echo "  make lcd      - Test LCD display"
	@echo "  make buttons  - Test control buttons"
	@echo "  make leds     - Test status LEDs"
	@echo "  make audio    - Test audio buzzers"
	@echo "  make monitor  - Monitor RFID card scans"
	@echo "  make tts      - Test text-to-speech"
	@echo ""
	@echo "System Management:"
	@echo "  make setup    - Complete system setup"
	@echo "  make install  - Install dependencies only"
	@echo "  make adduser  - Add a test user"
	@echo "  make status   - Check system status"
	@echo "  make clean    - Clean up cache files"
	@echo "  make reset    - Clear all user data"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - MFRC522 RFID reader (SPI interface)"
	@echo "  - MIFARE Classic cards/tags"
	@echo "  - 16x2 LCD with I2C backpack"
	@echo "  - 4x LEDs (2 with PWM support)"
	@echo "  - 2x Buzzers for audio"
	@echo "  - 3x Push buttons"
	@echo ""
	@echo "Pin Connections:"
	@echo "  RFID Reader:"
	@echo "    SDA=GPIO8, SCK=GPIO11, MOSI=GPIO10, MISO=GPIO9"
	@echo "    RST=GPIO22, 3.3V power (NOT 5V!)"
	@echo "  LCD: SDA=GPIO2, SCL=GPIO3 (I2C)"
	@echo "  LEDs: SCAN=GPIO17, SUCCESS=GPIO18, ERROR=GPIO27, GREETING=GPIO23"
	@echo "  Buzzers: WELCOME=GPIO24, ALERT=GPIO25"
	@echo "  Buttons: REGISTER=GPIO26, MODE=GPIO19, MUTE=GPIO20"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - SPI enabled: sudo raspi-config → Interface → SPI"
	@echo "  - I2C enabled: sudo raspi-config → Interface → I2C"
	@echo "  - espeak installed for TTS (optional)"
	@echo ""
	@echo "Usage Examples:"
	@echo "  make setup    # First-time setup"
	@echo "  make test     # Verify hardware"
	@echo "  make run      # Start the system"
	@echo "  make register # Add new cards"
	@echo "  make stats    # View statistics"