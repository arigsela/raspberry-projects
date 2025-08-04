# Makefile for Object Counting Device

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := object-counting-device.py

# Phony targets
.PHONY: run test demo interactive auto calibrate sensors lcd buttons leds i2c setup install status clean help

# Run the main program
run:
	@echo "Starting Object Counting Device..."
	@$(PYTHON) $(PROGRAM)

# Test all hardware components
test:
	@echo "Testing object counting hardware..."
	@echo "1. Testing ultrasonic sensors..."
	@$(PYTHON) -c "from gpiozero import DistanceSensor; import time; sensors = [('Entrance', DistanceSensor(echo=24, trigger=23)), ('Exit', DistanceSensor(echo=8, trigger=25)), ('Reference', DistanceSensor(echo=1, trigger=7))]; print('Testing sensors (10 seconds):'); start=time.time(); while time.time()-start<10: readings = [(name, f'{sensor.distance:.2f}m') for name, sensor in sensors]; print('  '.join([f'{name}:{dist}' for name, dist in readings]), end='\r'); time.sleep(0.5); [sensor.close() for _, sensor in sensors]; print('\nSensor test complete')" || echo "Ultrasonic sensor test failed"
	@$(MAKE) lcd
	@$(MAKE) buttons
	@$(MAKE) leds

# Run interactive demo
demo:
	@echo "Running object counting demo..."
	@$(PYTHON) -c "from object_counting_device import interactive_demo; interactive_demo()"

# Interactive counting mode
interactive:
	@echo "Starting interactive object counting..."
	@$(PYTHON) -c "from object_counting_device import interactive_demo; interactive_demo()"

# Automatic demonstration
auto:
	@echo "Running automatic demonstration..."
	@$(PYTHON) -c "from object_counting_device import automatic_demo; automatic_demo()"

# Calibration sequence
calibrate:
	@echo "Starting sensor calibration..."
	@$(PYTHON) -c "from object_counting_device import ObjectCountingDevice; import time; device = ObjectCountingDevice(); print('Calibration starting in 3 seconds...'); time.sleep(3); device._start_calibration(); time.sleep(2); device.cleanup()"

# Test individual sensor readings
sensors:
	@echo "Testing individual ultrasonic sensors..."
	@echo "Keep objects away from sensors during test"
	@$(PYTHON) -c "from gpiozero import DistanceSensor; import time; print('Sensor readings (20 seconds):'); entrance = DistanceSensor(echo=24, trigger=23, max_distance=2); exit_sensor = DistanceSensor(echo=8, trigger=25, max_distance=2); reference = DistanceSensor(echo=1, trigger=7, max_distance=2); start = time.time(); while time.time() - start < 20: print(f'\rEntrance: {entrance.distance:.2f}m | Exit: {exit_sensor.distance:.2f}m | Reference: {reference.distance:.2f}m | Time: {time.time()-start:.0f}s', end=''); time.sleep(0.2); entrance.close(); exit_sensor.close(); reference.close(); print('\nSensor test complete')" || echo "Individual sensor test failed"

# Test LCD display
lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); from lcd1602 import LCD1602; import time; lcd = LCD1602(0x27); lcd.clear(); lcd.write(0, 0, 'LCD Test OK'); lcd.write(1, 0, 'Display Works!'); print('LCD test message displayed'); time.sleep(3); lcd.clear(); print('LCD test complete')" || echo "LCD test failed - check I2C connection"

# Test control buttons  
buttons:
	@echo "Testing control buttons..."
	@$(PYTHON) -c "from gpiozero import Button; import time; buttons = {'RESET': Button(17), 'MODE': Button(18), 'CALIBRATE': Button(27), 'SETTINGS': Button(22)}; print('Press each button (10 seconds):'); start=time.time(); while time.time()-start<10: pressed = [name for name, btn in buttons.items() if btn.is_pressed]; print(f'Pressed: {pressed if pressed else \"None\"}', end='\r'); time.sleep(0.1); [btn.close() for btn in buttons.values()]; print('\nButton test complete')" || echo "Button test failed"

# Test status LEDs
leds:
	@echo "Testing status LEDs..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; leds = {'COUNT': PWMLED(26), 'DIRECTION': LED(19), 'STATUS': PWMLED(20), 'ERROR': LED(21)}; print('Testing LEDs...'); [led.on() for led in leds.values()]; time.sleep(1); [led.off() for led in leds.values()]; print('Testing PWM effects...'); leds['COUNT'].pulse(); leds['STATUS'].pulse(); time.sleep(2); [led.close() for led in leds.values()]; print('LED test complete')" || echo "LED test failed"

# Test I2C devices
i2c:
	@echo "Scanning for I2C devices..."
	@i2cdetect -y 1 || echo "I2C tools not available"
	@echo "Expected devices:"
	@echo "  0x27: LCD Display (typical address)"
	@echo "If LCD not found, check connections and power"

# Live sensor monitoring
monitor:
	@echo "Live sensor monitoring (Press Ctrl+C to stop)..."
	@$(PYTHON) -c "from gpiozero import DistanceSensor; import time; entrance = DistanceSensor(echo=24, trigger=23, max_distance=2); exit_sensor = DistanceSensor(echo=8, trigger=25, max_distance=2); reference = DistanceSensor(echo=1, trigger=7, max_distance=2); threshold = 0.3; print('Live monitoring - wave objects near sensors:'); try: \
		while True: \
			e_dist = entrance.distance; \
			x_dist = exit_sensor.distance; \
			r_dist = reference.distance; \
			e_detect = '🔴' if e_dist < threshold else '⚫'; \
			x_detect = '🔴' if x_dist < threshold else '⚫'; \
			print(f'\rEntrance: {e_detect} {e_dist:.2f}m | Exit: {x_detect} {x_dist:.2f}m | Ref: {r_dist:.2f}m', end=''); \
			time.sleep(0.1); \
	except KeyboardInterrupt: \
		print('\nMonitoring stopped'); \
	finally: \
		entrance.close(); exit_sensor.close(); reference.close()" || echo "Live monitoring failed"

# Count simulation
simulate:
	@echo "Simulating object counting..."
	@$(PYTHON) -c "from object_counting_device import ObjectCountingDevice; import time; device = ObjectCountingDevice(); print('Simulating objects for 30 seconds...'); start_time = time.time(); count = 0; while time.time() - start_time < 30: device._on_entrance_triggered(); time.sleep(0.3); device._on_exit_triggered(); time.sleep(0.3); device._on_entrance_cleared(); time.sleep(0.3); device._on_exit_cleared(); device._process_detection_sequence(); count += 1; print(f'Simulated {count} objects'); time.sleep(2); device.cleanup()" || echo "Simulation failed"

# Setup system and dependencies
setup:
	@echo "Setting up object counting device..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Installing I2C tools..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ I2C tools installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C setup may require manual configuration"
	@echo "Testing I2C bus..."
	@i2cdetect -y 1 2>/dev/null | grep -q "27" && echo "✓ LCD device detected at 0x27" || echo "⚠ No LCD detected - check connections"
	@echo "Testing GPIO access..."
	@$(PYTHON) -c "from gpiozero import LED; led = LED(26); led.off(); led.close(); print('✓ GPIO access working')" 2>/dev/null || echo "⚠ GPIO access test failed"
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero smbus2

# System status check
status:
	@echo "Object Counting Device Status"
	@echo "============================="
	@echo "Python Libraries:"
	@$(PYTHON) -c "import gpiozero; print('  ✓ gpiozero installed:', gpiozero.__version__)" 2>/dev/null || echo "  ❌ gpiozero not available"
	@$(PYTHON) -c "import smbus2; print('  ✓ smbus2 installed')" 2>/dev/null || echo "  ❌ smbus2 not available"
	@echo "GPIO Access:"
	@$(PYTHON) -c "from gpiozero import LED; LED(26).close(); print('  ✓ GPIO access working')" 2>/dev/null || echo "  ❌ GPIO access failed"
	@echo "I2C Interface:"
	@test -e /dev/i2c-1 && echo "  ✓ I2C interface enabled" || echo "  ❌ I2C interface disabled"
	@echo "I2C Devices:"
	@i2cdetect -y 1 2>/dev/null | grep -q "27" && echo "  ✓ LCD found at 0x27" || echo "  ⚪ No LCD detected at 0x27"
	@echo "Ultrasonic Sensors:"
	@$(PYTHON) -c "from gpiozero import DistanceSensor; sensors = [(23, 24, 'Entrance'), (25, 8, 'Exit'), (7, 1, 'Reference')]; [(lambda t, e, n: (DistanceSensor(echo=e, trigger=t, max_distance=1).close(), print(f'  ✓ {n} sensor (Trig:{t}, Echo:{e}): Connected')))(*sensor) for sensor in sensors]" 2>/dev/null || echo "  ⚪ Ultrasonic sensors not tested"
	@echo "Control Buttons:"
	@$(PYTHON) -c "from gpiozero import Button; buttons = [(17, 'RESET'), (18, 'MODE'), (27, 'CALIBRATE'), (22, 'SETTINGS')]; [(lambda pin, name: (Button(pin).close(), print(f'  ✓ {name} button (GPIO{pin}): Connected')))(*btn) for btn in buttons]" 2>/dev/null || echo "  ⚪ Control buttons not tested"
	@echo "Status LEDs:"
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; leds = [(26, 'COUNT'), (19, 'DIRECTION'), (20, 'STATUS'), (21, 'ERROR')]; [(lambda pin, name: (LED(pin).close(), print(f'  ✓ {name} LED (GPIO{pin}): Connected')))(*led) for led in leds]" 2>/dev/null || echo "  ⚪ Status LEDs not tested"
	@echo "System Files:"
	@test -f counting_device_settings.json && echo "  ✓ Settings file exists" || echo "  ⚪ Settings file not found (will be created)"
	@test -f detection_log.json && echo "  ✓ Detection log exists" || echo "  ⚪ Detection log not found (will be created)"

# View system logs and statistics
logs:
	@echo "Object Counting Device Logs"
	@echo "==========================="
	@if [ -f "detection_log.json" ]; then \
		echo "Recent detections (last 10):"; \
		tail -10 detection_log.json | $(PYTHON) -c "import sys, json; [print(f'  {event.get(\"timestamp\", \"Unknown\")}: {event.get(\"direction\", \"Unknown\")} - Total: {event.get(\"total_count\", 0)}') for line in sys.stdin for event in [json.loads(line.strip())] if line.strip()]" 2>/dev/null || echo "  Error reading detection log"; \
	else \
		echo "No detection log found"; \
	fi
	@echo ""
	@if [ -f "counting_device_settings.json" ]; then \
		echo "Current settings:"; \
		cat counting_device_settings.json | $(PYTHON) -c "import sys, json; settings = json.load(sys.stdin); [print(f'  {key}: {value}') for key, value in settings.items()]" 2>/dev/null || echo "  Error reading settings"; \
	else \
		echo "No settings file found"; \
	fi

# Reset system data
reset:
	@echo "Resetting system data..."
	@rm -f counting_device_settings.json
	@rm -f detection_log.json
	@echo "✓ Settings and detection log cleared"
	@echo "System will reinitialize on next run"

# Statistics and analysis
stats:
	@echo "Counting Device Statistics"
	@echo "=========================="
	@if [ -f "detection_log.json" ]; then \
		echo "Detection Statistics:"; \
		total_detections=$$(wc -l < detection_log.json); \
		echo "  Total detections: $$total_detections"; \
		echo "  Detection breakdown:"; \
		$(PYTHON) -c "import json; detections = [json.loads(line) for line in open('detection_log.json') if line.strip()]; directions = {}; [directions.update({event.get('direction', 'unknown'): directions.get(event.get('direction', 'unknown'), 0) + 1}) for event in detections]; [print(f'    {direction}: {count}') for direction, count in sorted(directions.items())]" 2>/dev/null || echo "    Error analyzing detections"; \
		echo "  Counting modes used:"; \
		$(PYTHON) -c "import json; detections = [json.loads(line) for line in open('detection_log.json') if line.strip()]; modes = {}; [modes.update({event.get('mode', 'unknown'): modes.get(event.get('mode', 'unknown'), 0) + 1}) for event in detections]; [print(f'    {mode}: {count} detections') for mode, count in sorted(modes.items(), key=lambda x: x[1], reverse=True)]" 2>/dev/null || echo "    Error analyzing modes"; \
	else \
		echo "No detection log found - run system to generate statistics"; \
	fi

# Clean up system files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Note: Keeping counting_device_settings.json and detection_log.json"
	@echo "Use 'make reset' to clear system data"

# Help
help:
	@echo "Object Counting Device"
	@echo "======================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive system (default)"
	@echo "  make test       - Test all hardware components"
	@echo "  make demo       - Interactive demonstration"
	@echo "  make interactive- Interactive counting mode"
	@echo "  make auto       - Automatic demonstration"
	@echo "  make calibrate  - Run sensor calibration"
	@echo ""
	@echo "Hardware Testing:"
	@echo "  make sensors    - Test ultrasonic sensors individually"
	@echo "  make lcd        - Test LCD display"
	@echo "  make buttons    - Test control buttons"
	@echo "  make leds       - Test status LEDs"
	@echo "  make i2c        - Scan I2C devices"
	@echo "  make monitor    - Live sensor monitoring"
	@echo "  make simulate   - Simulate object counting"
	@echo ""
	@echo "System Management:"
	@echo "  make setup      - Setup interfaces and dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make status     - Check system and hardware status"
	@echo "  make logs       - View recent activity logs"
	@echo "  make stats      - Show counting statistics"
	@echo "  make reset      - Clear all system data"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - 3x HC-SR04 ultrasonic sensors"
	@echo "  - 16x2 LCD display with I2C backpack"
	@echo "  - ADC0834 with potentiometer for sensitivity"
	@echo "  - Control buttons and status LEDs"
	@echo "  - Audio feedback buzzers"
	@echo ""
	@echo "Pin Connections:"
	@echo "  Ultrasonic Sensors:"
	@echo "    Entrance: Trig=GPIO23, Echo=GPIO24"
	@echo "    Exit:     Trig=GPIO25, Echo=GPIO8"
	@echo "    Reference:Trig=GPIO7,  Echo=GPIO1"
	@echo "  LCD Display: SDA=GPIO2, SCL=GPIO3 (I2C)"
	@echo "  ADC0834: CS=GPIO5, CLK=GPIO6, DI=GPIO16, DO=GPIO26"
	@echo "  Buttons: RESET=GPIO17, MODE=GPIO18, CALIBRATE=GPIO27, SETTINGS=GPIO22"
	@echo "  LEDs: COUNT=GPIO26, DIRECTION=GPIO19, STATUS=GPIO20, ERROR=GPIO21"
	@echo "  Buzzers: COUNT=GPIO13, ALERT=GPIO12"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - I2C enabled: sudo raspi-config → Interface → I2C"
	@echo "  - Stable 5V power supply for sensors"
	@echo "  - Proper sensor mounting (20-50cm spacing)"
	@echo "  - Clear detection zone without obstacles"
	@echo ""
	@echo "Counting Modes:"
	@echo "  1. BIDIRECTIONAL - Count objects in both directions"
	@echo "  2. ENTRANCE_ONLY - Count only entering objects"
	@echo "  3. EXIT_ONLY     - Count only exiting objects"
	@echo "  4. PRESENCE      - Detect object presence"
	@echo "  5. BATCH         - Group counting mode"
	@echo ""
	@echo "Detection Features:"
	@echo "  - Directional movement analysis"
	@echo "  - False positive filtering"
	@echo "  - Automatic calibration"
	@echo "  - Real-time statistics"
	@echo "  - Multi-sensor correlation"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time system setup"
	@echo "  make test        # Test all hardware"
	@echo "  make calibrate   # Calibrate sensors"
	@echo "  make demo        # Interactive demonstration"
	@echo "  make monitor     # Live sensor monitoring"
	@echo "  make stats       # View counting statistics"
	@echo ""
	@echo "Troubleshooting:"
	@echo "  - Sensors not detecting: Check 5V power, connections"
	@echo "  - Inaccurate direction: Verify sensor spacing/alignment"
	@echo "  - LCD not working: Check I2C address with i2cdetect"
	@echo "  - False positives: Increase stability, enable filtering"
	@echo "  - Count drift: Regular calibration, stable mounting"