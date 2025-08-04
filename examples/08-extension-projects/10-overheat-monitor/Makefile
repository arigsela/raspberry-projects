# Makefile for Overheat Monitoring System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := overheat-monitoring-system.py

# Phony targets
.PHONY: run test demo cooling zones trends alerts setup install clean help status stats

# Run the main program
run:
	@echo "Starting Overheat Monitoring System..."
	@$(PYTHON) $(PROGRAM)

# Run temperature scenario demo
demo:
	@echo "Running temperature scenario demo..."
	@$(PYTHON) $(PROGRAM) demo

# Test cooling system
cooling:
	@echo "Testing cooling system..."
	@$(PYTHON) $(PROGRAM) cooling

# Test all components
test:
	@echo "Testing overheat monitoring hardware..."
	@echo "1. Testing temperature sensors..."
	@$(MAKE) test-sensors
	@echo "2. Testing status LEDs..."
	@$(MAKE) test-leds
	@echo "3. Testing cooling systems..."
	@$(MAKE) test-cooling
	@echo "4. Testing alarms..."
	@$(MAKE) test-alarms
	@echo "5. Testing LCD display..."
	@$(MAKE) test-lcd

# Test temperature sensors
test-sensors:
	@echo "Testing temperature sensors via ADC..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; import time; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	print('Reading all temperature zones:'); \
	zones = ['Zone 1 (CPU/Main)', 'Zone 2 (Ambient)', 'Zone 3 (Power)', 'Zone 4 (Exhaust)']; \
	for i in range(4): \
		value = adc.read(i); \
		print(f'  {zones[i]}: ADC={value} ({value/255*100:.1f}%)'); \
		time.sleep(0.5); \
	print('✓ Temperature sensor test complete')" 2>/dev/null || echo "❌ Sensor test failed"

# Test LED indicators
test-leds:
	@echo "Testing status LEDs..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; \
	leds = { \
		'Normal': LED(17), \
		'Warning': LED(27), \
		'Critical': LED(22), \
		'Alarm': PWMLED(23) \
	}; \
	print('Testing status indicators:'); \
	for name, led in leds.items(): \
		print(f'  {name} LED...'); \
		if name == 'Alarm': \
			led.pulse(fade_in_time=0.2, fade_out_time=0.2); \
			time.sleep(2); \
		else: \
			led.on(); \
			time.sleep(1); \
		led.off(); \
	[led.close() for led in leds.values()]; \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test cooling systems
test-cooling:
	@echo "Testing cooling systems..."
	@$(PYTHON) -c "from gpiozero import PWMLED, LED; import time; \
	fan1 = PWMLED(18); \
	fan2 = PWMLED(19); \
	pump = LED(26); \
	print('Testing cooling devices:'); \
	print('  Fan 1 (Primary):'); \
	for speed in [0.3, 0.6, 1.0]: \
		print(f'    Speed {int(speed*100)}%'); \
		fan1.value = speed; \
		time.sleep(1); \
	fan1.off(); \
	print('  Fan 2 (Secondary):'); \
	for speed in [0.5, 1.0]: \
		print(f'    Speed {int(speed*100)}%'); \
		fan2.value = speed; \
		time.sleep(1); \
	fan2.off(); \
	print('  Water pump:'); \
	pump.on(); \
	time.sleep(2); \
	pump.off(); \
	fan1.close(); \
	fan2.close(); \
	pump.close(); \
	print('✓ Cooling test complete')" 2>/dev/null || echo "❌ Cooling test failed"

# Test alarm system
test-alarms:
	@echo "Testing alarm system..."
	@$(PYTHON) -c "from gpiozero import Buzzer, Button; import time; \
	buzzer = Buzzer(21); \
	print('Testing alarm patterns:'); \
	print('  Warning alarm...'); \
	buzzer.beep(0.3, 0.7, n=2); \
	time.sleep(2); \
	print('  Critical alarm...'); \
	buzzer.beep(0.2, 0.3, n=3); \
	time.sleep(2); \
	print('  Overheat alarm...'); \
	buzzer.beep(0.1, 0.1, n=5); \
	time.sleep(2); \
	buzzer.close(); \
	print('✓ Alarm test complete')" 2>/dev/null || echo "❌ Alarm test failed"

# Test LCD display
test-lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Temp Monitor'); \
	lcd.write(1, 0, 'System Test'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear(); \
	lcd.write(0, 0, 'Zone 1: 45.2C'); \
	lcd.write(1, 0, 'Alert: WARNING'); \
	print('✓ Temperature display test'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test zone monitoring
zones:
	@echo "Testing zone monitoring..."
	@$(PYTHON) -c "print('Temperature Zone Configuration:'); \
	print('====================================='); \
	zones = [ \
		('Zone 1', 'CPU/Main Equipment', 'Primary heat source', '40/60/75°C'), \
		('Zone 2', 'Ambient Environment', 'Room temperature', '35/50/65°C'), \
		('Zone 3', 'Power Supply', 'PSU monitoring', '45/65/80°C'), \
		('Zone 4', 'Exhaust/Output', 'Cooling effectiveness', '40/55/70°C') \
	]; \
	for name, desc, purpose, thresholds in zones: \
		print(f'\\n{name}: {desc}'); \
		print(f'  Purpose: {purpose}'); \
		print(f'  Thresholds (Normal/Warn/Critical): {thresholds}'); \
	print('\\n✓ Zone configuration displayed')" || echo "Zone display failed"

# Test trend analysis
trends:
	@echo "Testing temperature trend analysis..."
	@$(PYTHON) -c "import random; import time; \
	print('Simulating temperature trends:'); \
	print('=============================='); \
	base_temp = 40; \
	for minute in range(5): \
		trend = random.choice([2, -1, 3, 0, -2]); \
		base_temp += trend; \
		print(f'Minute {minute+1}: {base_temp}°C (trend: {trend:+d}°C/min)'); \
		if trend > 2: \
			print('  ⚠️  Rapid temperature rise detected!'); \
		time.sleep(0.5); \
	print('\\n✓ Trend analysis complete')" || echo "Trend test failed"

# Test alert levels
alerts:
	@echo "Testing alert level system..."
	@$(PYTHON) -c "from enum import Enum; \
	class AlertLevel(Enum): \
		NORMAL = 'Normal'; \
		WARNING = 'Warning'; \
		CRITICAL = 'Critical'; \
		OVERHEAT = 'Overheat'; \
		SHUTDOWN = 'Shutdown'; \
	print('Alert Level Demonstration:'); \
	print('========================='); \
	temps = [35, 45, 62, 78, 88]; \
	for temp in temps: \
		if temp < 40: level = AlertLevel.NORMAL; \
		elif temp < 60: level = AlertLevel.WARNING; \
		elif temp < 75: level = AlertLevel.CRITICAL; \
		elif temp < 85: level = AlertLevel.OVERHEAT; \
		else: level = AlertLevel.SHUTDOWN; \
		print(f'{temp}°C: {level.value}'); \
	print('\\n✓ Alert system test complete')" || echo "Alert test failed"

# Setup system and dependencies
setup:
	@echo "Setting up Overheat Monitoring System..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Installing system packages..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ Package installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero smbus2

# System status check
status:
	@echo "Overheat Monitoring System Status"
	@echo "================================="
	@echo "Hardware Configuration:"
	@echo "  Temperature Sensors: 4 zones via ADC0834"
	@echo "  Status LEDs: Normal, Warning, Critical, Alarm"
	@echo "  Zone LEDs: 4 indicators"
	@echo "  Cooling: 2 PWM fans + 1 pump relay"
	@echo "  Controls: Reset, Mode, Silence buttons"
	@echo "  Display: 16x2 I2C LCD"
	@echo ""
	@echo "Monitoring Zones:"
	@echo "  Zone 1: CPU/Main Equipment (Critical)"
	@echo "  Zone 2: Ambient Environment"
	@echo "  Zone 3: Power Supply"
	@echo "  Zone 4: Exhaust/Output"
	@echo ""
	@echo "Features:"
	@echo "  ✓ Multi-zone monitoring"
	@echo "  ✓ Automatic cooling control"
	@echo "  ✓ Predictive analysis"
	@echo "  ✓ Data logging"
	@echo "  ✓ Multiple display modes"
	@echo "  ✓ Alert escalation"

# Display statistics
stats:
	@echo "Temperature Monitoring Statistics"
	@echo "================================"
	@$(PYTHON) -c "import random; import json; from datetime import datetime, timedelta; \
	# Simulate session data \
	runtime = random.randint(3600, 14400); \
	alerts = random.randint(5, 50); \
	overheats = random.randint(0, 3); \
	max_temp = random.uniform(75, 92); \
	print(f'Session Duration: {runtime//3600}h {(runtime%3600)//60}m'); \
	print(f'Total Alerts: {alerts}'); \
	print(f'Overheat Events: {overheats}'); \
	print(f'Maximum Temperature: {max_temp:.1f}°C'); \
	print(f'Cooling Efficiency: {random.uniform(85, 95):.1f}%'); \
	print(''); \
	print('Zone Statistics:'); \
	for i in range(1, 5): \
		avg = random.uniform(35, 55); \
		max_zone = avg + random.uniform(10, 25); \
		print(f'  Zone {i}: Avg={avg:.1f}°C, Max={max_zone:.1f}°C'); \
	# Save sample log \
	log_entry = { \
		'timestamp': datetime.now().isoformat(), \
		'zones': {f'zone{i}': {'temp': random.uniform(30, 50), 'alert': 'Normal'} for i in range(1, 5)}, \
		'cooling_level': random.randint(0, 100) \
	}; \
	with open('overheat_log.json', 'a') as f: \
		json.dump(log_entry, f); \
		f.write('\\n'); \
	print('\\n✓ Log entry created')" || echo "Statistics generation failed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f overheat_config.json
	rm -f overheat_log.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "Overheat Monitoring System"
	@echo "=========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run      - Run the monitoring system (default)"
	@echo "  make demo     - Run temperature scenario demo"
	@echo "  make cooling  - Test cooling system response"
	@echo "  make test     - Test all hardware components"
	@echo ""
	@echo "Component Testing:"
	@echo "  make test-sensors - Test temperature sensors"
	@echo "  make test-leds    - Test status indicators"
	@echo "  make test-cooling - Test fans and pump"
	@echo "  make test-alarms  - Test alarm patterns"
	@echo "  make test-lcd     - Test LCD display"
	@echo ""
	@echo "Analysis & Features:"
	@echo "  make zones    - Show zone configuration"
	@echo "  make trends   - Demonstrate trend analysis"
	@echo "  make alerts   - Show alert level system"
	@echo "  make stats    - Display monitoring statistics"
	@echo ""
	@echo "System Management:"
	@echo "  make setup    - Complete system setup"
	@echo "  make install  - Install dependencies only"
	@echo "  make status   - Check system configuration"
	@echo "  make clean    - Clean cache and log files"
	@echo "  make help     - Show this help"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - 4x 10K thermistors"
	@echo "  - ADC0834 converter"
	@echo "  - 8x LEDs (4 status + 4 zone)"
	@echo "  - 2x PWM fans"
	@echo "  - 1x Water pump relay"
	@echo "  - 3x Push buttons"
	@echo "  - 1x Buzzer"
	@echo "  - 16x2 I2C LCD"
	@echo ""
	@echo "Alert Levels:"
	@echo "  Normal:   < 40°C (Green LED)"
	@echo "  Warning:  40-60°C (Yellow LED)"
	@echo "  Critical: 60-75°C (Red LED)"
	@echo "  Overheat: 75-85°C (Flashing Red)"
	@echo "  Shutdown: > 85°C (Rapid Flash)"