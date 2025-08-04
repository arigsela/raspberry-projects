# Makefile for Multi-Sensor Alarm System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := multi-sensor-alarm-system.py

# Phony targets
.PHONY: run test demo sensors zones modes alerts arm disarm panic glass smoke setup install clean help status events

# Run the main program
run:
	@echo "Starting Multi-Sensor Alarm System..."
	@$(PYTHON) $(PROGRAM)

# Run alarm system demo
demo:
	@echo "Running alarm system demo..."
	@$(PYTHON) $(PROGRAM) demo

# Test all components
test:
	@echo "Testing alarm system hardware..."
	@echo "1. Testing motion sensors..."
	@$(MAKE) test-motion
	@echo "2. Testing door/window sensors..."
	@$(MAKE) test-contacts
	@echo "3. Testing alarm outputs..."
	@$(MAKE) test-alarms
	@echo "4. Testing indicators..."
	@$(MAKE) test-indicators
	@echo "5. Testing LCD display..."
	@$(MAKE) test-lcd

# Test motion sensors
test-motion:
	@echo "Testing PIR motion sensors..."
	@$(PYTHON) -c "from gpiozero import MotionSensor; import time; \
	sensors = { \
		'Living Room': MotionSensor(17), \
		'Kitchen': MotionSensor(27), \
		'Bedroom': MotionSensor(22), \
		'Garage': MotionSensor(23) \
	}; \
	print('Wave hand in front of sensors (20 seconds)...'); \
	start = time.time(); \
	while time.time() - start < 20: \
		for name, sensor in sensors.items(): \
			if sensor.motion_detected: \
				print(f'  ✓ Motion detected: {name}'); \
				time.sleep(1); \
		time.sleep(0.1); \
	[s.close() for s in sensors.values()]; \
	print('✓ Motion sensor test complete')" 2>/dev/null || echo "❌ Motion test failed"

# Test door/window contacts
test-contacts:
	@echo "Testing magnetic contact sensors..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	contacts = { \
		'Front Door': Button(24, pull_up=True), \
		'Back Door': Button(25, pull_up=True), \
		'Window 1': Button(8, pull_up=True), \
		'Window 2': Button(7, pull_up=True) \
	}; \
	print('Current status:'); \
	for name, contact in contacts.items(): \
		status = 'Closed' if contact.is_pressed else 'Open'; \
		print(f'  {name}: {status}'); \
	print('\\nOpen/close doors and windows (15 seconds)...'); \
	start = time.time(); \
	last_state = {name: contact.is_pressed for name, contact in contacts.items()}; \
	while time.time() - start < 15: \
		for name, contact in contacts.items(): \
			if contact.is_pressed != last_state[name]: \
				status = 'Closed' if contact.is_pressed else 'Opened'; \
				print(f'  {name} {status}'); \
				last_state[name] = contact.is_pressed; \
		time.sleep(0.1); \
	[c.close() for c in contacts.values()]; \
	print('✓ Contact sensor test complete')" 2>/dev/null || echo "❌ Contact test failed"

# Test alarm outputs
test-alarms:
	@echo "Testing alarm outputs..."
	@$(PYTHON) -c "from gpiozero import OutputDevice, PWMLED, Buzzer; import time; \
	siren = OutputDevice(19); \
	strobe = PWMLED(26); \
	buzzer = Buzzer(21); \
	print('Testing siren (1 second)...'); \
	siren.on(); \
	time.sleep(1); \
	siren.off(); \
	print('Testing strobe light...'); \
	strobe.pulse(fade_in_time=0.2, fade_out_time=0.2); \
	time.sleep(3); \
	strobe.off(); \
	print('Testing buzzer patterns...'); \
	print('  Entry delay beep...'); \
	buzzer.beep(0.2, 0.3, n=5); \
	time.sleep(2); \
	print('  Exit delay beep...'); \
	buzzer.beep(0.1, 0.9, n=3); \
	time.sleep(3); \
	print('  Alarm sound...'); \
	buzzer.beep(0.5, 0.5, n=3); \
	siren.close(); \
	strobe.close(); \
	buzzer.close(); \
	print('✓ Alarm output test complete')" 2>/dev/null || echo "❌ Alarm test failed"

# Test LED indicators
test-indicators:
	@echo "Testing status indicators..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	leds = { \
		'Armed (Red)': LED(20), \
		'Ready (Green)': LED(14), \
		'Alert (Yellow)': LED(15) \
	}; \
	for name, led in leds.items(): \
		print(f'  Testing {name} LED...'); \
		led.on(); \
		time.sleep(1); \
		led.off(); \
	[led.close() for led in leds.values()]; \
	print('✓ Indicator test complete')" 2>/dev/null || echo "❌ Indicator test failed"

# Test LCD display
test-lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Alarm System'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear(); \
	lcd.write(0, 0, 'ARMED AWAY'); \
	lcd.write(1, 0, 'All Secure'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Show all sensors
sensors:
	@echo "Security Sensor Configuration"
	@echo "============================="
	@echo "Motion Sensors (PIR):"
	@echo "  Zone 1: Living Room (GPIO17)"
	@echo "  Zone 2: Kitchen (GPIO27)"
	@echo "  Zone 3: Bedroom (GPIO22)"
	@echo "  Zone 4: Garage (GPIO23)"
	@echo ""
	@echo "Door/Window Sensors:"
	@echo "  Front Door (GPIO24)"
	@echo "  Back Door (GPIO25)"
	@echo "  Living Room Window (GPIO8)"
	@echo "  Bedroom Window (GPIO7)"
	@echo ""
	@echo "Special Sensors:"
	@echo "  Glass Break (ADC CH0)"
	@echo "  Smoke Detector (GPIO13)"

# Show zone configuration
zones:
	@echo "Security Zone Configuration"
	@echo "==========================="
	@$(PYTHON) -c "print('Zone Types:'); \
	print(''); \
	print('1. Perimeter Zone:'); \
	print('   - All doors and windows'); \
	print('   - Active in all armed modes'); \
	print('   - Entry/exit delays apply'); \
	print(''); \
	print('2. Interior Zone:'); \
	print('   - Motion sensors'); \
	print('   - Active in Away mode only'); \
	print('   - Bypassed in Stay/Night modes'); \
	print(''); \
	print('3. 24-Hour Zone:'); \
	print('   - Smoke/fire detectors'); \
	print('   - Panic buttons'); \
	print('   - Always active'); \
	print(''); \
	print('4. Instant Zone:'); \
	print('   - Glass break sensors'); \
	print('   - No entry delay'); \
	print('   - Immediate alarm')" || echo "Zone display failed"

# Show operating modes
modes:
	@echo "Alarm System Operating Modes"
	@echo "============================"
	@echo "Available Modes:"
	@echo ""
	@echo "1. DISARMED:"
	@echo "   - Only 24-hour zones active"
	@echo "   - Free movement allowed"
	@echo ""
	@echo "2. ARMED STAY (Home):"
	@echo "   - Perimeter protection only"
	@echo "   - Interior motion bypassed"
	@echo "   - For when you're home"
	@echo ""
	@echo "3. ARMED AWAY:"
	@echo "   - All zones active"
	@echo "   - Full protection"
	@echo "   - Entry/exit delays"
	@echo ""
	@echo "4. ARMED NIGHT (Sleep):"
	@echo "   - Perimeter active"
	@echo "   - Selected interior active"
	@echo "   - Bedroom motion bypassed"

# Alert priority demo
alerts:
	@echo "Alert Priority System"
	@echo "===================="
	@$(PYTHON) -c "from enum import Enum; \
	class AlertPriority(Enum): \
		LOW = 1; \
		MEDIUM = 2; \
		HIGH = 3; \
		CRITICAL = 4; \
		EMERGENCY = 5; \
	print('Priority Levels:'); \
	print(''); \
	examples = [ \
		(AlertPriority.LOW, 'System armed/disarmed'), \
		(AlertPriority.MEDIUM, 'Zone fault, low battery'), \
		(AlertPriority.HIGH, 'Intrusion detected'), \
		(AlertPriority.CRITICAL, 'Multiple zones triggered'), \
		(AlertPriority.EMERGENCY, 'Fire, panic, medical') \
	]; \
	for priority, example in examples: \
		print(f'{priority.value}. {priority.name}:'); \
		print(f'   Example: {example}'); \
		print(f'   Response: ', end=''); \
		if priority.value >= 4: \
			print('Immediate notification + authorities'); \
		elif priority.value >= 3: \
			print('Siren + strobe + notifications'); \
		else: \
			print('Log event + optional notification'); \
		print('')" || echo "Alert demo failed"

# Simulate arming sequence
arm:
	@echo "Simulating Arm Sequence"
	@echo "======================="
	@$(PYTHON) -c "import time; \
	print('Checking all zones...'); \
	time.sleep(1); \
	print('✓ All zones secure'); \
	print(''); \
	print('Starting exit delay (60 seconds)...'); \
	for i in range(10, 0, -1): \
		print(f'  {i}...', end='', flush=True); \
		time.sleep(0.5); \
	print(''); \
	print(''); \
	print('🔒 System Armed!'); \
	print('Mode: Armed Away'); \
	print('All zones active')" || echo "Arm simulation failed"

# Simulate disarm sequence
disarm:
	@echo "Simulating Disarm Sequence"
	@echo "=========================="
	@$(PYTHON) -c "import time; \
	print('Entry detected...'); \
	print('Starting entry delay (30 seconds)...'); \
	print(''); \
	for i in range(5, 0, -1): \
		print(f'  Disarm now! {i}...', end='', flush=True); \
		time.sleep(0.5); \
	print(''); \
	print(''); \
	print('Code accepted'); \
	print('🔓 System Disarmed'); \
	print('Welcome home!')" || echo "Disarm simulation failed"

# Simulate panic alarm
panic:
	@echo "PANIC ALARM SIMULATION"
	@echo "====================="
	@$(PYTHON) -c "import time; \
	print('🆘 PANIC BUTTON PRESSED!'); \
	print(''); \
	for _ in range(3): \
		print('🚨 ALARM! 🚨', end='', flush=True); \
		time.sleep(0.5); \
		print('\\r          \\r', end='', flush=True); \
		time.sleep(0.5); \
	print(''); \
	print(''); \
	print('Actions taken:'); \
	print('  ✓ Siren activated'); \
	print('  ✓ Strobe flashing'); \
	print('  ✓ Monitoring station notified'); \
	print('  ✓ Emergency contacts alerted')" || echo "Panic simulation failed"

# Glass break detection demo
glass:
	@echo "Glass Break Detection Demo"
	@echo "=========================="
	@$(PYTHON) -c "import random; import time; \
	print('Monitoring audio levels...'); \
	print(''); \
	baseline = 50; \
	for i in range(20): \
		noise = baseline + random.randint(-5, 5); \
		if i == 15: \
			noise = baseline + 150; \
		bar = '#' * (noise // 10); \
		print(f'Level: {bar:<20} {noise}', end=''); \
		if noise > baseline + 100: \
			print(' 🔊 GLASS BREAK DETECTED!'); \
		else: \
			print(''); \
		time.sleep(0.2); \
	print(''); \
	print('Detection threshold: Baseline + 100')" || echo "Glass break demo failed"

# Smoke alarm test
smoke:
	@echo "Smoke Detector Test"
	@echo "==================="
	@echo "Smoke detectors are 24-hour zones"
	@echo "Always active regardless of arm state"
	@echo ""
	@echo "Test sequence:"
	@echo "  1. Press test button on smoke detector"
	@echo "  2. System receives alarm signal"
	@echo "  3. Immediate high-priority alert"
	@echo "  4. All outputs activated"
	@echo "  5. Fire department notified"

# Setup system and dependencies
setup:
	@echo "Setting up Multi-Sensor Alarm System..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Installing system packages..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ Package installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating default config..."
	@echo '{"entry_delay": 30, "exit_delay": 60, "alarm_duration": 300}' > alarm_config.json
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero smbus2

# System status check
status:
	@echo "Alarm System Status"
	@echo "=================="
	@echo "Hardware Configuration:"
	@echo "  Motion Sensors: 4 zones (PIR)"
	@echo "  Contact Sensors: 4 (2 doors, 2 windows)"
	@echo "  Special Sensors: Glass break, smoke"
	@echo "  Outputs: Siren, strobe, buzzer"
	@echo "  Display: 16x2 I2C LCD"
	@echo "  Controls: Arm, panic, test buttons"
	@echo ""
	@echo "System Features:"
	@echo "  ✓ Multi-zone protection"
	@echo "  ✓ Entry/exit delays"
	@echo "  ✓ Multiple arm modes"
	@echo "  ✓ 24-hour zones"
	@echo "  ✓ Glass break detection"
	@echo "  ✓ Event logging"
	@echo ""
	@if [ -f alarm_config.json ]; then \
		echo "Configuration: Found"; \
		$(PYTHON) -c "import json; \
		with open('alarm_config.json') as f: \
			config = json.load(f); \
			print(f'  Entry delay: {config.get(\"entry_delay\", 30)}s'); \
			print(f'  Exit delay: {config.get(\"exit_delay\", 60)}s'); \
			print(f'  Alarm duration: {config.get(\"alarm_duration\", 300)}s')"; \
	else \
		echo "Configuration: Not found (run 'make setup')"; \
	fi

# View event log
events:
	@echo "Recent System Events"
	@echo "==================="
	@if [ -f alarm_log_*.json ]; then \
		echo "Last 10 events:"; \
		tail -n 10 alarm_log_*.json | $(PYTHON) -c "import sys, json; \
		for line in sys.stdin: \
			try: \
				event = json.loads(line); \
				print(f\"{event['timestamp']}: {event['type']} - {event['details']}\"); \
			except: pass"; \
	else \
		echo "No event logs found"; \
	fi

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f alarm_config.json
	rm -f alarm_log_*.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "Multi-Sensor Alarm System"
	@echo "========================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run      - Run the alarm system (default)"
	@echo "  make demo     - Run alarm features demo"
	@echo "  make test     - Test all hardware components"
	@echo ""
	@echo "Component Testing:"
	@echo "  make test-motion   - Test PIR sensors"
	@echo "  make test-contacts - Test door/window sensors"
	@echo "  make test-alarms   - Test siren and strobe"
	@echo "  make test-indicators - Test LED indicators"
	@echo "  make test-lcd     - Test LCD display"
	@echo ""
	@echo "System Information:"
	@echo "  make sensors  - Show sensor configuration"
	@echo "  make zones    - Show zone types"
	@echo "  make modes    - Show operating modes"
	@echo "  make alerts   - Show alert priorities"
	@echo ""
	@echo "Simulations:"
	@echo "  make arm      - Simulate arming sequence"
	@echo "  make disarm   - Simulate disarm sequence"
	@echo "  make panic    - Simulate panic alarm"
	@echo "  make glass    - Glass break detection demo"
	@echo "  make smoke    - Smoke detector info"
	@echo ""
	@echo "System Management:"
	@echo "  make setup    - Complete system setup"
	@echo "  make install  - Install dependencies only"
	@echo "  make status   - Check system status"
	@echo "  make events   - View event log"
	@echo "  make clean    - Clean cache and logs"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Operating Instructions:"
	@echo "  ARM button: Toggle arm/disarm"
	@echo "  PANIC button: Immediate alarm"
	@echo "  TEST button: System test mode"
	@echo ""
	@echo "Default Timings:"
	@echo "  Entry delay: 30 seconds"
	@echo "  Exit delay: 60 seconds"
	@echo "  Alarm duration: 5 minutes"