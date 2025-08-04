# Makefile for Keypad Security System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := keypad-security-system.py

# Phony targets
.PHONY: run test demo keypad codes users access lockout emergency setup install clean help status logs

# Run the main program
run:
	@echo "Starting Keypad Security System..."
	@$(PYTHON) $(PROGRAM)

# Run security features demo
demo:
	@echo "Running security system demo..."
	@$(PYTHON) $(PROGRAM) demo

# Test all components
test:
	@echo "Testing security system hardware..."
	@echo "1. Testing keypad..."
	@$(MAKE) test-keypad
	@echo "2. Testing indicators..."
	@$(MAKE) test-indicators
	@echo "3. Testing lock..."
	@$(MAKE) test-lock
	@echo "4. Testing LCD..."
	@$(MAKE) test-lcd
	@echo "5. Testing alarm..."
	@$(MAKE) test-alarm

# Test keypad scanning
test-keypad:
	@echo "Testing 4x4 matrix keypad..."
	@$(PYTHON) -c "from gpiozero import OutputDevice, Button; import time; \
	print('Testing keypad matrix scanning...'); \
	rows = [OutputDevice(p) for p in [17, 27, 22, 23]]; \
	cols = [Button(p, pull_up=True) for p in [24, 25, 8, 7]]; \
	keys = [['1','2','3','A'], ['4','5','6','B'], ['7','8','9','C'], ['*','0','#','D']]; \
	print('Press keys on keypad (15 seconds)...'); \
	start = time.time(); \
	while time.time() - start < 15: \
		for r_idx, row in enumerate(rows): \
			row.off(); \
			for c_idx, col in enumerate(cols): \
				if not col.is_pressed: \
					print(f'  Key pressed: {keys[r_idx][c_idx]}'); \
					time.sleep(0.3); \
			row.on(); \
		time.sleep(0.05); \
	[r.close() for r in rows]; \
	[c.close() for c in cols]; \
	print('✓ Keypad test complete')" 2>/dev/null || echo "❌ Keypad test failed"

# Test LED indicators
test-indicators:
	@echo "Testing security indicators..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	leds = {'Locked': LED(5), 'Unlocked': LED(6), 'Alert': LED(13)}; \
	for name, led in leds.items(): \
		print(f'  Testing {name} LED...'); \
		led.on(); \
		time.sleep(1); \
		led.off(); \
	[led.close() for led in leds.values()]; \
	print('✓ Indicator test complete')" 2>/dev/null || echo "❌ Indicator test failed"

# Test lock relay
test-lock:
	@echo "Testing electronic lock..."
	@$(PYTHON) -c "from gpiozero import OutputDevice; import time; \
	lock = OutputDevice(19); \
	print('Testing lock relay...'); \
	print('  Lock engaged (relay off)...'); \
	lock.off(); \
	time.sleep(2); \
	print('  Lock released (relay on)...'); \
	lock.on(); \
	time.sleep(2); \
	print('  Lock engaged (relay off)...'); \
	lock.off(); \
	lock.close(); \
	print('✓ Lock test complete')" 2>/dev/null || echo "❌ Lock test failed"

# Test LCD display
test-lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Security System'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear(); \
	lcd.write(0, 0, 'Enter Code:'); \
	lcd.write(1, 0, '****'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test alarm buzzer
test-alarm:
	@echo "Testing alarm system..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	buzzer = Buzzer(26); \
	print('Testing alarm patterns...'); \
	print('  Key press beep...'); \
	buzzer.beep(0.05, 0, n=1); \
	time.sleep(1); \
	print('  Access denied...'); \
	buzzer.beep(0.2, 0.2, n=2); \
	time.sleep(2); \
	print('  Access granted...'); \
	buzzer.beep(0.1, 0.1, n=3); \
	time.sleep(2); \
	print('  Emergency alarm...'); \
	buzzer.beep(0.5, 0.5, n=3); \
	time.sleep(3); \
	buzzer.close(); \
	print('✓ Alarm test complete')" 2>/dev/null || echo "❌ Alarm test failed"

# Test keypad input
keypad:
	@echo "Keypad Input Test"
	@echo "================="
	@echo "Keys:"
	@echo "  0-9: Numbers"
	@echo "  *:   Clear"
	@echo "  #:   Enter"
	@echo "  A-D: Functions"
	@echo ""
	@echo "Press Ctrl+C to exit"

# Show access codes info
codes:
	@echo "Access Code Management"
	@echo "====================="
	@echo "Default Codes (⚠️  CHANGE THESE!):"
	@echo "  Master: 1234"
	@echo "  Admin:  9876"
	@echo ""
	@echo "Code Requirements:"
	@echo "  - Minimum 4 digits"
	@echo "  - Maximum 8 digits"
	@echo "  - No repeated sequences"
	@echo "  - Change regularly"
	@echo ""
	@echo "Special Codes:"
	@echo "  - Ending in 99: Duress alarm"
	@echo "  - Temporary: Auto-expire after 5 min"

# User management demo
users:
	@echo "User Management Demo"
	@echo "==================="
	@$(PYTHON) -c "from enum import Enum; \
	class SecurityLevel(Enum): \
		USER = 'User'; \
		ADMIN = 'Admin'; \
		MASTER = 'Master'; \
		TEMP = 'Temporary'; \
	print('Security Levels:'); \
	for level in SecurityLevel: \
		print(f'  {level.value}:'); \
		if level == SecurityLevel.USER: \
			print('    - Basic access'); \
			print('    - Change own password'); \
		elif level == SecurityLevel.ADMIN: \
			print('    - Add/remove users'); \
			print('    - Create temp codes'); \
			print('    - View access logs'); \
		elif level == SecurityLevel.MASTER: \
			print('    - Full system control'); \
			print('    - Factory reset'); \
			print('    - Security settings'); \
		elif level == SecurityLevel.TEMP: \
			print('    - Time-limited access'); \
			print('    - Auto-expire'); \
			print('    - Single use option')" || echo "User demo failed"

# Access control demo
access:
	@echo "Access Control Features"
	@echo "======================"
	@echo "Login Process:"
	@echo "  1. Enter access code"
	@echo "  2. Press # to submit"
	@echo "  3. System verifies code"
	@echo "  4. Lock releases if valid"
	@echo ""
	@echo "Security Features:"
	@echo "  ✓ SHA-256 password hashing"
	@echo "  ✓ No plaintext storage"
	@echo "  ✓ Brute force protection"
	@echo "  ✓ Auto-lock timeout"
	@echo "  ✓ Access logging"
	@echo "  ✓ Duress code support"

# Lockout demonstration
lockout:
	@echo "Lockout Protection Demo"
	@echo "======================"
	@$(PYTHON) -c "import time; \
	print('Simulating failed login attempts...'); \
	for i in range(1, 4): \
		print(f'\\nAttempt {i}: Wrong code entered'); \
		print(f'  Access DENIED'); \
		if i < 3: \
			print(f'  {3-i} attempts remaining'); \
		else: \
			print('  SYSTEM LOCKED OUT'); \
			print('  Lockout duration: 300 seconds'); \
		time.sleep(1); \
	print('\\nLockout features:'); \
	print('  - 3 failed attempts trigger lockout'); \
	print('  - 5 minute lockout period'); \
	print('  - Emergency override available'); \
	print('  - All attempts logged')" || echo "Lockout demo failed"

# Emergency procedures
emergency:
	@echo "Emergency Procedures"
	@echo "==================="
	@echo "Emergency Unlock:"
	@echo "  - Press hidden emergency button"
	@echo "  - Immediate unlock"
	@echo "  - Alarm sounds"
	@echo "  - Auto-relock after 60s"
	@echo ""
	@echo "Duress Code:"
	@echo "  - Any code ending in 99"
	@echo "  - Appears to unlock normally"
	@echo "  - Silent alarm triggered"
	@echo "  - Alert logged"
	@echo ""
	@echo "Factory Reset:"
	@echo "  - Hold reset button 10 seconds"
	@echo "  - All users deleted"
	@echo "  - Returns to defaults"
	@echo "  - Logs cleared"

# Setup system and dependencies
setup:
	@echo "Setting up Keypad Security System..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Installing system packages..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ Package installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating default config..."
	@echo '{"users": [], "settings": {"auto_lock": true}}' > security_config.json
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero smbus2

# System status check
status:
	@echo "Security System Status"
	@echo "====================="
	@echo "Hardware Configuration:"
	@echo "  Keypad: 4x4 Matrix (16 keys)"
	@echo "  Display: 16x2 I2C LCD"
	@echo "  Lock: Electronic relay"
	@echo "  Indicators: 3 LEDs"
	@echo "  Audio: Buzzer alarm"
	@echo "  Controls: 2 hidden buttons"
	@echo ""
	@echo "Security Features:"
	@echo "  ✓ Multi-user support"
	@echo "  ✓ Access levels"
	@echo "  ✓ Temporary codes"
	@echo "  ✓ Anti-tampering"
	@echo "  ✓ Access logging"
	@echo "  ✓ Emergency unlock"
	@echo ""
	@if [ -f security_config.json ]; then \
		echo "Configuration: Found"; \
	else \
		echo "Configuration: Not found (run 'make setup')"; \
	fi

# View access logs
logs:
	@echo "Access Log Viewer"
	@echo "================="
	@if [ -f access_log_*.json ]; then \
		echo "Recent access attempts:"; \
		tail -n 10 access_log_*.json | $(PYTHON) -c "import sys, json; \
		for line in sys.stdin: \
			try: \
				entry = json.loads(line); \
				print(f\"{entry['timestamp']}: {entry['user']} - {entry['status']}\"); \
			except: pass"; \
	else \
		echo "No access logs found"; \
	fi

# Simulate access scenarios
scenarios:
	@echo "Access Scenarios Simulation"
	@echo "==========================="
	@$(PYTHON) -c "import random; from datetime import datetime, timedelta; \
	print('Simulating 24-hour access pattern:'); \
	users = ['john_doe', 'jane_smith', 'admin', 'temp_123', 'service_tech']; \
	statuses = ['Granted', 'Granted', 'Granted', 'Denied', 'Timeout']; \
	start = datetime.now() - timedelta(hours=24); \
	for i in range(20): \
		time = start + timedelta(minutes=random.randint(0, 1440)); \
		user = random.choice(users); \
		status = random.choices(statuses, weights=[60, 20, 10, 8, 2])[0]; \
		print(f'{time.strftime(\"%H:%M\")} - {user:<15} {status}'); \
	print('\\nStatistics:'); \
	print('  Total attempts: 20'); \
	print('  Success rate: 85%'); \
	print('  Peak hours: 08:00-10:00, 17:00-19:00')" || echo "Scenario simulation failed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f security_config.json
	rm -f access_log_*.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "Keypad Security System"
	@echo "====================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run      - Run the security system (default)"
	@echo "  make demo     - Run security features demo"
	@echo "  make test     - Test all hardware components"
	@echo ""
	@echo "Component Testing:"
	@echo "  make test-keypad     - Test matrix keypad"
	@echo "  make test-indicators - Test LED indicators"
	@echo "  make test-lock      - Test electronic lock"
	@echo "  make test-lcd       - Test LCD display"
	@echo "  make test-alarm     - Test alarm buzzer"
	@echo ""
	@echo "Features & Info:"
	@echo "  make keypad    - Keypad layout info"
	@echo "  make codes     - Access code management"
	@echo "  make users     - User security levels"
	@echo "  make access    - Access control features"
	@echo "  make lockout   - Lockout protection demo"
	@echo "  make emergency - Emergency procedures"
	@echo ""
	@echo "System Management:"
	@echo "  make setup     - Complete system setup"
	@echo "  make install   - Install dependencies only"
	@echo "  make status    - Check system status"
	@echo "  make logs      - View access logs"
	@echo "  make scenarios - Simulate access patterns"
	@echo "  make clean     - Clean cache and logs"
	@echo "  make help      - Show this help"
	@echo ""
	@echo "Default Access Codes:"
	@echo "  Master: 1234 (CHANGE THIS!)"
	@echo "  Admin:  9876 (CHANGE THIS!)"
	@echo ""
	@echo "Key Functions:"
	@echo "  0-9: Enter digits"
	@echo "  *:   Clear input"
	@echo "  #:   Submit code"
	@echo "  A:   Add user (admin)"
	@echo "  B:   Change password"
	@echo "  C:   Temp code (admin)"
	@echo "  D:   Lock system"