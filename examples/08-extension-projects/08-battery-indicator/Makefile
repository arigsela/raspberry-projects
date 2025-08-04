# Makefile for Battery Voltage Monitor

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := battery-voltage-monitor.py

# Configuration file
CONFIG_FILE := battery_monitor_config.json

# Log file
LOG_FILE := battery_log.json

# Phony targets
.PHONY: run test demo discharge calibrate monitor voltage leds lcd buttons adc graph types setup install status clean reset help

# Run the main program
run:
	@echo "Starting Battery Voltage Monitor..."
	@$(PYTHON) $(PROGRAM)

# Test all hardware components
test:
	@echo "Testing battery monitor hardware..."
	@echo "1. Testing voltage measurement..."
	@$(MAKE) voltage
	@echo "2. Testing LED bar graph..."
	@$(MAKE) leds
	@echo "3. Testing LCD display..."
	@$(MAKE) lcd
	@echo "4. Testing buttons..."
	@$(MAKE) buttons
	@echo "5. Testing ADC..."
	@$(MAKE) adc

# Run battery level demonstration
demo:
	@echo "Running battery level demo..."
	@$(PYTHON) $(PROGRAM) demo

# Test discharge rate calculation
discharge:
	@echo "Testing discharge rate calculation..."
	@$(PYTHON) $(PROGRAM) discharge

# Calibrate voltage reading
calibrate:
	@echo "Voltage Calibration Procedure"
	@echo "============================="
	@echo "1. Connect a known voltage source to the voltage divider"
	@echo "2. Measure the actual voltage with a multimeter"
	@echo "3. Note the displayed voltage reading"
	@echo ""
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; import time; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	VOLTAGE_DIVIDER_RATIO = 4.03; \
	ADC_REFERENCE_VOLTAGE = 3.3; \
	print('Taking 20 voltage readings...'); \
	readings = []; \
	for i in range(20): \
		adc_value = adc.read(0); \
		adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE; \
		actual_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO; \
		readings.append(actual_voltage); \
		print(f'\\rReading {i+1}/20: {actual_voltage:.3f}V  ', end=''); \
		time.sleep(0.1); \
	avg_voltage = sum(readings) / len(readings); \
	print(f'\\nAverage reading: {avg_voltage:.3f}V'); \
	print('\\nTo calibrate, calculate offset = Actual_Voltage - Displayed_Voltage')" || echo "Calibration failed"

# Monitor voltage readings
monitor:
	@echo "Monitoring battery voltage (Ctrl+C to stop)..."
	@$(PYTHON) -c "import sys, os, time; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	VOLTAGE_DIVIDER_RATIO = 4.03; \
	ADC_REFERENCE_VOLTAGE = 3.3; \
	print('Voltage monitoring active...'); \
	print('Connect battery through voltage divider!'); \
	try: \
		while True: \
			adc_value = adc.read(0); \
			adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE; \
			actual_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO; \
			bar_length = int((actual_voltage / 15) * 40); \
			bar = '█' * min(bar_length, 40); \
			print(f'\\r{actual_voltage:5.2f}V  ADC:{adc_value:3d}  [{bar:<40}]', end=''); \
			time.sleep(0.2); \
	except KeyboardInterrupt: \
		print('\\nMonitoring stopped')" || echo "Voltage monitoring failed"

# Test voltage measurement
voltage:
	@echo "Testing voltage measurement..."
	@$(PYTHON) -c "import sys, os, time; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	VOLTAGE_DIVIDER_RATIO = 4.03; \
	ADC_REFERENCE_VOLTAGE = 3.3; \
	print('Taking 10 voltage readings...'); \
	for i in range(10): \
		adc_value = adc.read(0); \
		adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE; \
		actual_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO; \
		print(f'  Reading {i+1}: {actual_voltage:.3f}V (ADC: {adc_value})'); \
		time.sleep(0.5); \
	print('✓ Voltage measurement test complete')" 2>/dev/null || echo "❌ Voltage test failed"

# Test LED bar graph
leds:
	@echo "Testing LED bar graph..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	pins = [17, 18, 27, 22, 23, 24, 25, 8, 7, 1]; \
	leds = [LED(pin) for pin in pins]; \
	print('Testing bar graph animation...'); \
	for i in range(11): \
		percent = i * 10; \
		leds_on = i; \
		print(f'  {percent}% - {\"█\" * leds_on}{\"░\" * (10-leds_on)}'); \
		for j, led in enumerate(leds): \
			if j < leds_on: led.on(); \
			else: led.off(); \
		time.sleep(0.5); \
	[led.off() for led in leds]; \
	print('Testing individual LEDs...'); \
	for i, led in enumerate(leds): \
		print(f'  LED {i+1} ({(i+1)*10}%)'); \
		led.on(); \
		time.sleep(0.2); \
		led.off(); \
	[led.close() for led in leds]; \
	print('✓ LED bar graph test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test LCD display
lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Battery Monitor'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD test message displayed'); \
	time.sleep(2); \
	lcd.clear(); \
	lcd.write(0, 0, '12.6V  100%'); \
	lcd.write(1, 0, '████████████████'); \
	print('✓ Battery display test'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test control buttons
buttons:
	@echo "Testing control buttons (press each button, 10 seconds)..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = {'MODE': Button(26), 'CALIBRATE': Button(13)}; \
	print('Press each button:'); \
	print('  MODE: Short press = cycle display, Long press = battery type'); \
	print('  CALIBRATE: Calibrate voltage reading'); \
	start = time.time(); \
	pressed_buttons = set(); \
	held = False; \
	def on_hold(): \
		global held; \
		held = True; \
		print('  ✓ MODE button held (battery type)'); \
	buttons['MODE'].when_held = on_hold; \
	while time.time() - start < 10: \
		for name, btn in buttons.items(): \
			if btn.is_pressed and name not in pressed_buttons: \
				print(f'  ✓ {name} button pressed'); \
				pressed_buttons.add(name); \
		if len(pressed_buttons) == 2 and held: \
			break; \
		time.sleep(0.1); \
	[btn.close() for btn in buttons.values()]; \
	print('✓ Button test complete')" 2>/dev/null || echo "❌ Button test failed"

# Test ADC channels
adc:
	@echo "Testing ADC..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; import time; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	print('Reading ADC channel 0 (battery voltage)...'); \
	readings = []; \
	for i in range(20): \
		value = adc.read(0); \
		readings.append(value); \
		voltage = (value / 255.0) * 3.3; \
		print(f'\\rADC: {value:3d}  Voltage: {voltage:.3f}V  ', end=''); \
		time.sleep(0.1); \
	avg = sum(readings) / len(readings); \
	print(f'\\nAverage ADC value: {avg:.1f}'); \
	print('✓ ADC test complete')" 2>/dev/null || echo "❌ ADC test failed"

# Live voltage graph
graph:
	@echo "Live Voltage Graph (Ctrl+C to stop)"
	@echo "==================================="
	@$(PYTHON) -c "import sys, os, time; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	VOLTAGE_DIVIDER_RATIO = 4.03; \
	ADC_REFERENCE_VOLTAGE = 3.3; \
	history = []; \
	try: \
		while True: \
			adc_value = adc.read(0); \
			adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE; \
			voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO; \
			history.append(voltage); \
			if len(history) > 50: history.pop(0); \
			if len(history) > 1: \
				v_min = min(history[-30:]); \
				v_max = max(history[-30:]); \
				v_range = v_max - v_min if v_max > v_min else 1; \
				graph = ''.join(['▁▂▃▄▅▆▇█'[min(7, int((v - v_min) / v_range * 8))] for v in history[-30:]]); \
				print(f'\\r{voltage:5.2f}V [{graph:<30}]', end=''); \
			time.sleep(0.2); \
	except KeyboardInterrupt: \
		print('\\nGraph stopped')" || echo "Graph failed"

# Show battery types
types:
	@echo "Supported Battery Types"
	@echo "======================="
	@$(PYTHON) -c "from battery_voltage_monitor import BATTERY_PROFILES; \
	print('Type          | Nominal | Empty | Full  | Cells'); \
	print('--------------|---------|-------|-------|------'); \
	for name, profile in BATTERY_PROFILES.items(): \
		print(f'{name:13s} | {profile[\"nominal\"]:6.1f}V | {profile[\"empty\"]:5.1f}V | {profile[\"full\"]:5.1f}V | {profile[\"cells\"]:5d}')" || echo "Failed to show battery types"

# Voltage divider calculator
divider:
	@echo "Voltage Divider Calculator"
	@echo "=========================="
	@$(PYTHON) -c "print('For safe measurement of higher voltages'); \
	print('Current divider: R1=10kΩ, R2=3.3kΩ'); \
	print('Ratio: 4.03:1'); \
	print('Max input: 13.3V (for 3.3V ADC)'); \
	print(''); \
	voltages = [5, 12, 24, 36, 48]; \
	print('Recommended dividers for common voltages:'); \
	for v in voltages: \
		r2 = 3.3; \
		r1 = r2 * (v / 3.3 - 1); \
		ratio = (r1 + r2) / r2; \
		print(f'  {v}V: R1={r1:.1f}kΩ, R2={r2}kΩ, Ratio={ratio:.2f}:1')" || echo "Calculator failed"

# Setup system and dependencies
setup:
	@echo "Setting up battery voltage monitor..."
	@echo "Installing Python libraries..."
	@pip install gpiozero numpy smbus2
	@echo "Installing system packages..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ Package installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating initial configuration..."
	@test -f $(CONFIG_FILE) || echo '{"battery_type": "LiPo_3S", "calibration_offset": 0.0}' > $(CONFIG_FILE)
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero numpy smbus2

# System status check
status:
	@echo "Battery Monitor Status"
	@echo "====================="
	@echo "Configuration:"
	@if [ -f "$(CONFIG_FILE)" ]; then \
		echo "  ✓ Configuration file exists"; \
		$(PYTHON) -c "import json; config = json.load(open('$(CONFIG_FILE)')); \
		print(f'    Battery type: {config.get(\"battery_type\", \"Unknown\")}'); \
		print(f'    Calibration: {config.get(\"calibration_offset\", 0.0):+.3f}V'); \
		print(f'    Low threshold: {config.get(\"low_threshold\", 20)}%'); \
		print(f'    Critical: {config.get(\"critical_threshold\", 10)}%')" 2>/dev/null || echo "    Error reading config"; \
	else \
		echo "  ⚪ No configuration file"; \
	fi
	@echo "Data Logging:"
	@if [ -f "$(LOG_FILE)" ]; then \
		lines=$$(wc -l < $(LOG_FILE)); \
		echo "  ✓ Log file exists ($$lines entries)"; \
		tail -1 $(LOG_FILE) | $(PYTHON) -c "import sys, json; \
		try: \
			data = json.loads(sys.stdin.read()); \
			print(f'    Last entry: {data[\"timestamp\"]}'); \
			print(f'    Voltage: {data[\"voltage\"]}V ({data[\"percentage\"]}%)'); \
		except: pass" 2>/dev/null || echo "    Error reading log"; \
	else \
		echo "  ⚪ No log file"; \
	fi
	@echo "Hardware:"
	@test -e /dev/i2c-1 && echo "  ✓ I2C interface enabled" || echo "  ❌ I2C interface disabled"
	@i2cdetect -y 1 2>/dev/null | grep -q "27" && echo "  ✓ LCD detected at 0x27" || echo "  ⚪ No LCD detected"

# Show battery statistics
stats:
	@echo "Battery Statistics"
	@echo "=================="
	@if [ -f "$(LOG_FILE)" ]; then \
		$(PYTHON) -c "import json; \
		voltages = []; \
		percentages = []; \
		with open('$(LOG_FILE)') as f: \
			for line in f: \
				if line.strip(): \
					data = json.loads(line); \
					voltages.append(data['voltage']); \
					percentages.append(data['percentage']); \
		if voltages: \
			print(f'Total samples: {len(voltages)}'); \
			print(f'Voltage range: {min(voltages):.2f}V - {max(voltages):.2f}V'); \
			print(f'Average voltage: {sum(voltages)/len(voltages):.2f}V'); \
			print(f'Average percentage: {sum(percentages)/len(percentages):.1f}%'); \
			if len(voltages) > 10: \
				recent_avg = sum(voltages[-10:]) / 10; \
				older_avg = sum(voltages[-20:-10]) / 10; \
				discharge = (older_avg - recent_avg) * 6; \
				print(f'Est. discharge rate: {discharge:.3f} V/hour')" 2>/dev/null || echo "Error analyzing statistics"; \
	else \
		echo "No data available"; \
	fi

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
	@echo "Battery Voltage Monitor"
	@echo "======================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run       - Run the battery monitor (default)"
	@echo "  make test      - Test all hardware components"
	@echo "  make demo      - Run battery level demonstration"
	@echo "  make discharge - Test discharge rate calculation"
	@echo "  make calibrate - Calibrate voltage reading"
	@echo "  make monitor   - Live voltage monitoring"
	@echo ""
	@echo "Hardware Testing:"
	@echo "  make voltage   - Test voltage measurement"
	@echo "  make leds      - Test LED bar graph"
	@echo "  make lcd       - Test LCD display"
	@echo "  make buttons   - Test control buttons"
	@echo "  make adc       - Test ADC readings"
	@echo ""
	@echo "Features:"
	@echo "  make graph     - Live voltage graph"
	@echo "  make types     - Show battery types"
	@echo "  make divider   - Voltage divider calculator"
	@echo "  make stats     - Show battery statistics"
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
	@echo "  - ADC0834 ADC converter"
	@echo "  - 10x LEDs for bar graph"
	@echo "  - 3x Status LEDs"
	@echo "  - 2x Control buttons"
	@echo "  - 16x2 LCD with I2C"
	@echo "  - Voltage divider (10kΩ + 3.3kΩ)"
	@echo "  - Buzzer for alerts"
	@echo ""
	@echo "Pin Connections:"
	@echo "  ADC: CS=GPIO5, CLK=GPIO6, DI=GPIO16, DO=GPIO12"
	@echo "  Bar LEDs: GPIO17,18,27,22,23,24,25,8,7,1"
	@echo "  Status: Charge=GPIO19, Low=GPIO20, Critical=GPIO21"
	@echo "  Buttons: Mode=GPIO26, Calibrate=GPIO13"
	@echo "  LCD: SDA=GPIO2, SCL=GPIO3 (I2C)"
	@echo "  Buzzer: GPIO14"
	@echo ""
	@echo "Battery Types:"
	@echo "  LiPo: 1S (3.7V), 2S (7.4V), 3S (11.1V)"
	@echo "  Lead Acid: 12V"
	@echo "  NiMH: 4-cell (4.8V)"
	@echo "  Alkaline: 4-cell (6.0V)"