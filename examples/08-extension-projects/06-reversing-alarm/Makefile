# Makefile for Ultrasonic Parking Sensor

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := ultrasonic-parking-sensor.py

# Configuration file
CONFIG_FILE := parking_sensor_config.json

# Log file
LOG_FILE := parking_sensor_log.json

# Phony targets
.PHONY: run test demo calibrate monitor zones sensor lcd leds audio buttons adc setup install status clean reset help

# Run the main program
run:
	@echo "Starting Ultrasonic Parking Sensor..."
	@$(PYTHON) $(PROGRAM)

# Test all hardware components
test:
	@echo "Testing parking sensor hardware..."
	@echo "1. Testing ultrasonic sensor..."
	@$(MAKE) sensor
	@echo "2. Testing LCD display..."
	@$(MAKE) lcd
	@echo "3. Testing LEDs..."
	@$(MAKE) leds
	@echo "4. Testing audio..."
	@$(MAKE) audio
	@echo "5. Testing buttons..."
	@$(MAKE) buttons
	@echo "6. Testing ADC..."
	@$(MAKE) adc

# Run parking demonstration
demo:
	@echo "Running parking sensor demo..."
	@$(PYTHON) $(PROGRAM) demo

# Run calibration procedure
calibrate:
	@echo "Running calibration test..."
	@$(PYTHON) $(PROGRAM) calibrate

# Monitor distance readings
monitor:
	@echo "Monitoring ultrasonic sensor (Ctrl+C to stop)..."
	@$(PYTHON) -c "from gpiozero import DistanceSensor; import time; \
	sensor = DistanceSensor(echo=24, trigger=23, max_distance=4.0); \
	print('Distance monitoring active...'); \
	try: \
		while True: \
			dist = sensor.distance; \
			bar = '█' * int(dist * 10); \
			print(f'\\rDistance: {dist:.2f}m [{bar:<40}]', end=''); \
			time.sleep(0.1); \
	except KeyboardInterrupt: \
		print('\\nMonitoring stopped'); \
	finally: \
		sensor.close()" || echo "Sensor monitoring failed"

# Test zone detection
zones:
	@echo "Testing zone detection..."
	@$(PYTHON) -c "from ultrasonic_parking_sensor import UltrasonicParkingSensor, DistanceZone; \
	print('Zone thresholds:'); \
	print('  CRITICAL: < 0.1m'); \
	print('  DANGER:   < 0.3m'); \
	print('  WARNING:  < 0.5m'); \
	print('  CAUTION:  < 1.0m'); \
	print('  SAFE:     > 2.0m'); \
	print('\\nTest distances:'); \
	sensor = UltrasonicParkingSensor(); \
	test_distances = [0.05, 0.2, 0.4, 0.7, 1.5, 3.0]; \
	for dist in test_distances: \
		zone = sensor._get_distance_zone(dist); \
		print(f'  {dist}m -> {zone.value}'); \
	sensor.cleanup()" || echo "Zone test failed"

# Test ultrasonic sensor
sensor:
	@echo "Testing ultrasonic sensor..."
	@$(PYTHON) -c "from gpiozero import DistanceSensor; import time; \
	sensor = DistanceSensor(echo=24, trigger=23, max_distance=4.0); \
	print('Taking 10 readings...'); \
	for i in range(10): \
		dist = sensor.distance; \
		print(f'  Reading {i+1}: {dist:.3f}m'); \
		time.sleep(0.5); \
	sensor.close(); \
	print('✓ Sensor test complete')" 2>/dev/null || echo "❌ Sensor test failed"

# Test LCD display
lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Parking Sensor'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD test message displayed'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test LED indicators
leds:
	@echo "Testing LED indicators..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; \
	leds = {'GREEN': LED(17), 'YELLOW': LED(27), 'ORANGE': LED(22), 'RED': PWMLED(18)}; \
	print('Testing each LED...'); \
	for name, led in leds.items(): \
		print(f'  {name} LED on'); \
		led.on(); \
		time.sleep(0.5); \
		led.off(); \
	print('Testing red LED PWM effects...'); \
	leds['RED'].pulse(); \
	time.sleep(2); \
	[led.close() for led in leds.values()]; \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test audio output
audio:
	@echo "Testing audio output..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	buzzer = Buzzer(25); \
	speaker = Buzzer(8); \
	print('Testing main buzzer...'); \
	buzzer.beep(0.2, 0.2, n=3); \
	time.sleep(1); \
	print('Testing speaker...'); \
	speaker.beep(0.1, 0.1, n=5); \
	buzzer.close(); \
	speaker.close(); \
	print('✓ Audio test complete')" 2>/dev/null || echo "❌ Audio test failed"

# Test control buttons
buttons:
	@echo "Testing control buttons (press each button, 10 seconds)..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = {'MODE': Button(19), 'MUTE': Button(20), 'CALIBRATE': Button(26)}; \
	print('Press each button:'); \
	start = time.time(); \
	pressed_buttons = set(); \
	while time.time() - start < 10: \
		for name, btn in buttons.items(): \
			if btn.is_pressed and name not in pressed_buttons: \
				print(f'  ✓ {name} button pressed'); \
				pressed_buttons.add(name); \
		if len(pressed_buttons) == 3: \
			break; \
		time.sleep(0.1); \
	[btn.close() for btn in buttons.values()]; \
	if len(pressed_buttons) < 3: \
		print(f'  ⚠ Only {len(pressed_buttons)}/3 buttons tested'); \
	else: \
		print('✓ All buttons tested')" 2>/dev/null || echo "❌ Button test failed"

# Test ADC sensitivity control
adc:
	@echo "Testing ADC sensitivity control..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; import time; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	print('Reading potentiometer (10 seconds)...'); \
	print('Turn the potentiometer to test'); \
	start = time.time(); \
	last_value = -1; \
	while time.time() - start < 10: \
		value = adc.read(0); \
		sensitivity = 0.1 + (value / 255) * 0.9; \
		if abs(value - last_value) > 5: \
			print(f'\\rADC: {value:3d} | Sensitivity: {sensitivity*100:.0f}%  ', end=''); \
			last_value = value; \
		time.sleep(0.1); \
	print('\\n✓ ADC test complete')" 2>/dev/null || echo "❌ ADC test failed"

# Simulate parking scenarios
simulate:
	@echo "Simulating parking scenarios..."
	@$(PYTHON) -c "from ultrasonic_parking_sensor import UltrasonicParkingSensor; import time; \
	sensor = UltrasonicParkingSensor(); \
	scenarios = [ \
		('Parallel parking', [3.0, 2.0, 1.5, 1.0, 0.7, 0.5, 0.4, 0.3, 0.35, 0.4]), \
		('Reverse parking', [4.0, 3.0, 2.0, 1.0, 0.5, 0.3, 0.2, 0.15, 0.2, 0.5]), \
		('Emergency stop', [2.0, 1.0, 0.5, 0.2, 0.08, 0.05, 0.08, 0.5, 2.0]) \
	]; \
	for scenario_name, distances in scenarios: \
		print(f'\\n{scenario_name}:'); \
		for dist in distances: \
			zone = sensor._get_distance_zone(dist); \
			print(f'  {dist:.2f}m - {zone.value}'); \
			sensor.distance_history = [dist] * sensor.smoothing_window; \
			sensor.current_distance = dist; \
			sensor._handle_zone_change(zone, dist); \
			time.sleep(1); \
	sensor.cleanup()" || echo "Simulation failed"

# Setup system and dependencies
setup:
	@echo "Setting up ultrasonic parking sensor..."
	@echo "Installing Python libraries..."
	@pip install gpiozero numpy smbus2
	@echo "Installing system packages..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ Package installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating initial configuration..."
	@test -f $(CONFIG_FILE) || echo '{"alert_mode": "Standard", "sensitivity": 0.5}' > $(CONFIG_FILE)
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero numpy smbus2

# System status check
status:
	@echo "Parking Sensor Status"
	@echo "===================="
	@echo "Hardware:"
	@$(PYTHON) -c "from gpiozero import DistanceSensor; DistanceSensor(echo=24, trigger=23).close(); print('  ✓ Ultrasonic sensor accessible')" 2>/dev/null || echo "  ❌ Ultrasonic sensor not accessible"
	@test -e /dev/i2c-1 && echo "  ✓ I2C interface enabled" || echo "  ❌ I2C interface disabled"
	@i2cdetect -y 1 2>/dev/null | grep -q "27" && echo "  ✓ LCD detected at 0x27" || echo "  ⚪ No LCD detected"
	@echo "Configuration:"
	@if [ -f "$(CONFIG_FILE)" ]; then \
		echo "  ✓ Configuration file exists"; \
		$(PYTHON) -c "import json; config = json.load(open('$(CONFIG_FILE)')); \
		print(f'    Mode: {config.get(\"alert_mode\", \"Unknown\")}'); \
		print(f'    Sensitivity: {config.get(\"sensitivity\", 0.5)*100:.0f}%'); \
		print(f'    Calibration: {config.get(\"calibration_offset\", 0.0):+.2f}m')" 2>/dev/null || echo "    Error reading config"; \
	else \
		echo "  ⚪ No configuration file"; \
	fi
	@echo "Logs:"
	@if [ -f "$(LOG_FILE)" ]; then \
		lines=$$(wc -l < $(LOG_FILE)); \
		echo "  ✓ Log file exists ($$lines entries)"; \
	else \
		echo "  ⚪ No log file"; \
	fi

# View recent alerts
alerts:
	@echo "Recent Parking Alerts"
	@echo "===================="
	@if [ -f "$(LOG_FILE)" ]; then \
		echo "Last 20 zone changes:"; \
		tail -20 $(LOG_FILE) | $(PYTHON) -c "import sys, json; \
		[print(f'  {json.loads(line)[\"timestamp\"]}: {json.loads(line)[\"zone\"]} at {json.loads(line)[\"distance\"]}m') \
		for line in sys.stdin if line.strip()]" 2>/dev/null || echo "  Error reading log"; \
	else \
		echo "No alerts logged yet"; \
	fi

# Show zone statistics
stats:
	@echo "Zone Statistics"
	@echo "==============="
	@if [ -f "$(LOG_FILE)" ]; then \
		$(PYTHON) -c "import json; \
		zones = {}; \
		with open('$(LOG_FILE)') as f: \
			for line in f: \
				if line.strip(): \
					entry = json.loads(line); \
					zone = entry.get('zone', 'Unknown'); \
					zones[zone] = zones.get(zone, 0) + 1; \
		total = sum(zones.values()); \
		print(f'Total zone changes: {total}'); \
		print('\\nZone distribution:'); \
		for zone, count in sorted(zones.items()): \
			percent = (count/total*100) if total > 0 else 0; \
			print(f'  {zone}: {count} ({percent:.1f}%)')" 2>/dev/null || echo "Error analyzing statistics"; \
	else \
		echo "No data available"; \
	fi

# Live distance graph
graph:
	@echo "Live Distance Graph (Ctrl+C to stop)"
	@echo "===================================="
	@$(PYTHON) -c "from gpiozero import DistanceSensor; import time; \
	sensor = DistanceSensor(echo=24, trigger=23, max_distance=4.0); \
	zones = {0.1: 'CRIT', 0.3: 'DNGR', 0.5: 'WARN', 1.0: 'CAUT', 2.0: 'SAFE'}; \
	try: \
		while True: \
			dist = sensor.distance; \
			zone_name = 'FAR'; \
			for threshold, name in zones.items(): \
				if dist <= threshold: \
					zone_name = name; \
					break; \
			bar_length = int(dist * 20); \
			bar = '█' * min(bar_length, 80); \
			print(f'\\r{dist:5.2f}m [{zone_name:4s}] {bar:<80}', end=''); \
			time.sleep(0.1); \
	except KeyboardInterrupt: \
		print('\\nGraph stopped'); \
	finally: \
		sensor.close()" || echo "Graph failed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Note: Keeping $(CONFIG_FILE) and $(LOG_FILE)"
	@echo "Use 'make reset' to clear all data"

# Reset all data
reset:
	@echo "Resetting all data..."
	@rm -f $(CONFIG_FILE) $(LOG_FILE)
	@echo "✓ Configuration and logs cleared"

# Help
help:
	@echo "Ultrasonic Parking Sensor"
	@echo "========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run       - Run the parking sensor (default)"
	@echo "  make test      - Test all hardware components"
	@echo "  make demo      - Run parking demonstration"
	@echo "  make calibrate - Run calibration procedure"
	@echo "  make monitor   - Monitor distance readings"
	@echo "  make zones     - Test zone detection"
	@echo ""
	@echo "Hardware Testing:"
	@echo "  make sensor    - Test ultrasonic sensor"
	@echo "  make lcd       - Test LCD display"
	@echo "  make leds      - Test LED indicators"
	@echo "  make audio     - Test buzzers"
	@echo "  make buttons   - Test control buttons"
	@echo "  make adc       - Test sensitivity control"
	@echo ""
	@echo "Features:"
	@echo "  make simulate  - Simulate parking scenarios"
	@echo "  make graph     - Live distance graph"
	@echo "  make alerts    - View recent alerts"
	@echo "  make stats     - Show zone statistics"
	@echo ""
	@echo "System Management:"
	@echo "  make setup     - Complete system setup"
	@echo "  make install   - Install dependencies only"
	@echo "  make status    - Check system status"
	@echo "  make clean     - Clean cache files"
	@echo "  make reset     - Clear all data"
	@echo "  make help      - Show this help"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - HC-SR04 ultrasonic sensor"
	@echo "  - 16x2 LCD with I2C backpack"
	@echo "  - 4x LEDs (Green, Yellow, Orange, Red)"
	@echo "  - 2x Buzzers"
	@echo "  - 3x Push buttons"
	@echo "  - ADC0834 with potentiometer"
	@echo ""
	@echo "Pin Connections:"
	@echo "  Ultrasonic: Trig=GPIO23, Echo=GPIO24"
	@echo "  LEDs: Green=GPIO17, Yellow=GPIO27, Orange=GPIO22, Red=GPIO18"
	@echo "  Audio: Buzzer=GPIO25, Speaker=GPIO8"
	@echo "  Buttons: Mode=GPIO19, Mute=GPIO20, Calibrate=GPIO26"
	@echo "  ADC: CS=GPIO5, CLK=GPIO6, DI=GPIO16, DO=GPIO12"
	@echo "  LCD: SDA=GPIO2, SCL=GPIO3 (I2C)"
	@echo ""
	@echo "Distance Zones:"
	@echo "  CRITICAL: < 0.1m (Continuous alarm)"
	@echo "  DANGER:   < 0.3m (Fast beep)"
	@echo "  WARNING:  < 0.5m (Medium beep)"
	@echo "  CAUTION:  < 1.0m (Slow beep)"
	@echo "  SAFE:     > 2.0m (No alert)"
	@echo ""
	@echo "Alert Modes:"
	@echo "  Standard:  Traditional beeping"
	@echo "  Voice:     Simulated announcements"
	@echo "  Tone:      Musical tones"
	@echo "  Visual:    LED indicators only"
	@echo "  Emergency: Enhanced critical alerts"