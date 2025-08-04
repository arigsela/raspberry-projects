# Makefile for Temperature-Controlled Smart Fan

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := temperature-controlled-fan.py

# Configuration file
CONFIG_FILE := fan_config.json

# Phony targets
.PHONY: run test demo modes calibrate monitor temp fan lcd leds buttons adc rpm setup install status clean reset help

# Run the main program
run:
	@echo "Starting Temperature-Controlled Smart Fan..."
	@$(PYTHON) $(PROGRAM)

# Test all hardware components
test:
	@echo "Testing smart fan hardware..."
	@echo "1. Testing temperature sensor..."
	@$(MAKE) temp
	@echo "2. Testing fan control..."
	@$(MAKE) fan
	@echo "3. Testing LCD display..."
	@$(MAKE) lcd
	@echo "4. Testing LEDs..."
	@$(MAKE) leds
	@echo "5. Testing buttons..."
	@$(MAKE) buttons
	@echo "6. Testing ADC..."
	@$(MAKE) adc

# Run temperature demonstration
demo:
	@echo "Running temperature control demo..."
	@$(PYTHON) $(PROGRAM) demo

# Test operating modes
modes:
	@echo "Testing all operating modes..."
	@$(PYTHON) $(PROGRAM) modes

# Calibrate temperature sensor
calibrate:
	@echo "Temperature sensor calibration..."
	@echo "Place thermistor in ice water (0°C) and press Enter"
	@read dummy
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	readings = [adc.read(0) for _ in range(10)]; \
	ice_point = sum(readings) / len(readings); \
	print(f'Ice point ADC value: {ice_point:.1f}'); \
	print('Place thermistor in boiling water (100°C) and press Enter'); \
	input(); \
	readings = [adc.read(0) for _ in range(10)]; \
	boil_point = sum(readings) / len(readings); \
	print(f'Boiling point ADC value: {boil_point:.1f}'); \
	print(f'Calibration range: {ice_point:.1f} to {boil_point:.1f}')" || echo "Calibration failed"

# Monitor temperature readings
monitor:
	@echo "Monitoring temperature (Ctrl+C to stop)..."
	@$(PYTHON) -c "import sys, os, time, math; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	print('Temperature monitoring active...'); \
	try: \
		while True: \
			adc_value = adc.read(0); \
			if adc_value > 0: \
				resistance = 10000 / (255.0 / adc_value - 1.0); \
				steinhart = resistance / 10000; \
				steinhart = math.log(steinhart); \
				steinhart /= 3950; \
				steinhart += 1.0 / 298.15; \
				steinhart = 1.0 / steinhart; \
				temp_c = steinhart - 273.15; \
				bar = '█' * int(temp_c); \
				print(f'\\rTemp: {temp_c:5.1f}°C  ADC: {adc_value:3d}  [{bar:<40}]', end=''); \
			time.sleep(0.5); \
	except KeyboardInterrupt: \
		print('\\nMonitoring stopped')" || echo "Temperature monitoring failed"

# Test temperature sensor
temp:
	@echo "Testing temperature sensor..."
	@$(PYTHON) -c "import sys, os, time, math; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	print('Taking 10 temperature readings...'); \
	for i in range(10): \
		adc_value = adc.read(0); \
		if adc_value > 0: \
			resistance = 10000 / (255.0 / adc_value - 1.0); \
			steinhart = resistance / 10000; \
			steinhart = math.log(steinhart); \
			steinhart /= 3950; \
			steinhart += 1.0 / 298.15; \
			steinhart = 1.0 / steinhart; \
			temp_c = steinhart - 273.15; \
			print(f'  Reading {i+1}: {temp_c:.1f}°C (ADC: {adc_value})'); \
		time.sleep(0.5); \
	print('✓ Temperature sensor test complete')" 2>/dev/null || echo "❌ Temperature sensor test failed"

# Test fan control
fan:
	@echo "Testing fan control..."
	@$(PYTHON) -c "from gpiozero import PWMLED, LED; import time; \
	fan_pwm = PWMLED(18); \
	fan_enable = LED(27); \
	print('Testing fan speeds...'); \
	speeds = [0, 30, 60, 100]; \
	for speed in speeds: \
		print(f'  Fan speed: {speed}%'); \
		if speed > 0: \
			fan_enable.on(); \
			fan_pwm.value = speed / 100.0; \
		else: \
			fan_pwm.value = 0; \
			fan_enable.off(); \
		time.sleep(2); \
	fan_pwm.value = 0; \
	fan_enable.off(); \
	fan_pwm.close(); \
	fan_enable.close(); \
	print('✓ Fan control test complete')" 2>/dev/null || echo "❌ Fan control test failed"

# Test LCD display
lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Smart Fan Test'); \
	lcd.write(1, 0, 'LCD OK'); \
	print('✓ LCD test message displayed'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test status LEDs
leds:
	@echo "Testing status LEDs..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; \
	leds = {'COOL': LED(22), 'NORMAL': LED(23), 'WARM': LED(24), 'HOT': PWMLED(25)}; \
	print('Testing each LED...'); \
	for name, led in leds.items(): \
		print(f'  {name} LED'); \
		led.on(); \
		time.sleep(0.5); \
		led.off(); \
	print('Testing HOT LED pulse...'); \
	leds['HOT'].pulse(); \
	time.sleep(2); \
	[led.close() for led in leds.values()]; \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test control buttons
buttons:
	@echo "Testing control buttons (press each button, 10 seconds)..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = {'MODE': Button(19), 'UP': Button(20), 'DOWN': Button(21), 'POWER': Button(26)}; \
	print('Press each button:'); \
	start = time.time(); \
	pressed_buttons = set(); \
	while time.time() - start < 10: \
		for name, btn in buttons.items(): \
			if btn.is_pressed and name not in pressed_buttons: \
				print(f'  ✓ {name} button pressed'); \
				pressed_buttons.add(name); \
		if len(pressed_buttons) == 4: \
			break; \
		time.sleep(0.1); \
	[btn.close() for btn in buttons.values()]; \
	if len(pressed_buttons) < 4: \
		print(f'  ⚠ Only {len(pressed_buttons)}/4 buttons tested'); \
	else: \
		print('✓ All buttons tested')" 2>/dev/null || echo "❌ Button test failed"

# Test ADC channels
adc:
	@echo "Testing ADC channels..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; import time; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	print('ADC channel readings:'); \
	print('  CH0 (Temperature): Turn potentiometer to test'); \
	print('  CH1 (Setpoint): Adjust potentiometer'); \
	start = time.time(); \
	while time.time() - start < 10: \
		ch0 = adc.read(0); \
		ch1 = adc.read(1); \
		temp_estimate = 15 + (ch1 / 255) * 20; \
		print(f'\\rCH0: {ch0:3d}  CH1: {ch1:3d} ({temp_estimate:.1f}°C)  ', end=''); \
		time.sleep(0.1); \
	print('\\n✓ ADC test complete')" 2>/dev/null || echo "❌ ADC test failed"

# Test RPM measurement
rpm:
	@echo "Testing fan RPM measurement..."
	@echo "Note: Requires fan to be running"
	@$(PYTHON) -c "import RPi.GPIO as GPIO; from gpiozero import PWMLED, LED; import time; \
	GPIO.setmode(GPIO.BCM); \
	GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); \
	fan_pwm = PWMLED(18); \
	fan_enable = LED(27); \
	pulses = 0; \
	def count_pulse(channel): \
		global pulses; \
		pulses += 1; \
	GPIO.add_event_detect(17, GPIO.FALLING, callback=count_pulse); \
	print('Starting fan at 50% speed...'); \
	fan_enable.on(); \
	fan_pwm.value = 0.5; \
	print('Measuring RPM for 5 seconds...'); \
	for i in range(5): \
		pulses = 0; \
		time.sleep(1); \
		rpm = (pulses * 60) // 2; \
		print(f'  {i+1}s: {rpm} RPM ({pulses} pulses)'); \
	fan_pwm.value = 0; \
	fan_enable.off(); \
	GPIO.cleanup(); \
	fan_pwm.close(); \
	fan_enable.close(); \
	print('✓ RPM test complete')" 2>/dev/null || echo "❌ RPM test failed"

# Live temperature graph
graph:
	@echo "Live Temperature Graph (Ctrl+C to stop)"
	@echo "===================================="
	@$(PYTHON) -c "import sys, os, time, math; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from adc0834 import ADC0834; \
	adc = ADC0834(cs=5, clk=6, di=16, do=12); \
	history = []; \
	try: \
		while True: \
			adc_value = adc.read(0); \
			if adc_value > 0: \
				resistance = 10000 / (255.0 / adc_value - 1.0); \
				steinhart = resistance / 10000; \
				steinhart = math.log(steinhart); \
				steinhart /= 3950; \
				steinhart += 1.0 / 298.15; \
				steinhart = 1.0 / steinhart; \
				temp_c = steinhart - 273.15; \
				history.append(temp_c); \
				if len(history) > 50: history.pop(0); \
				graph = ''.join(['▁▂▃▄▅▆▇█'[min(7, int((t-15)*0.3))] for t in history[-30:]]); \
				print(f'\\r{temp_c:5.1f}°C [{graph:<30}]', end=''); \
			time.sleep(0.5); \
	except KeyboardInterrupt: \
		print('\\nGraph stopped')" || echo "Graph failed"

# Setup system and dependencies
setup:
	@echo "Setting up smart fan system..."
	@echo "Installing Python libraries..."
	@pip install gpiozero RPi.GPIO smbus2
	@echo "Installing system packages..."
	@sudo apt update && sudo apt install -y python3-smbus i2c-tools || echo "⚠ Package installation failed"
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating initial configuration..."
	@test -f $(CONFIG_FILE) || echo '{"mode": "Auto", "target_temp": 25.0}' > $(CONFIG_FILE)
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero RPi.GPIO smbus2

# System status check
status:
	@echo "Smart Fan System Status"
	@echo "======================="
	@echo "Hardware:"
	@$(PYTHON) -c "import RPi.GPIO; print('  ✓ RPi.GPIO available')" 2>/dev/null || echo "  ❌ RPi.GPIO not available"
	@test -e /dev/i2c-1 && echo "  ✓ I2C interface enabled" || echo "  ❌ I2C interface disabled"
	@i2cdetect -y 1 2>/dev/null | grep -q "27" && echo "  ✓ LCD detected at 0x27" || echo "  ⚪ No LCD detected"
	@echo "Configuration:"
	@if [ -f "$(CONFIG_FILE)" ]; then \
		echo "  ✓ Configuration file exists"; \
		$(PYTHON) -c "import json; config = json.load(open('$(CONFIG_FILE)')); \
		print(f'    Mode: {config.get(\"mode\", \"Unknown\")}'); \
		print(f'    Target: {config.get(\"target_temp\", 25)}°C')" 2>/dev/null || echo "    Error reading config"; \
	else \
		echo "  ⚪ No configuration file"; \
	fi

# Fan curve visualization
curves:
	@echo "Fan Speed Curves"
	@echo "================"
	@$(PYTHON) -c "from temperature_controlled_fan import TemperatureControlledFan; \
	fan = TemperatureControlledFan(); \
	print('Temperature vs Fan Speed:'); \
	print('Temp(°C) | Auto | Eco | Turbo | Silent'); \
	print('---------+------+-----+-------+-------'); \
	for temp in range(15, 41, 2): \
		fan.current_temp = temp; \
		fan.target_temp = 25; \
		auto = fan._auto_fan_curve(temp); \
		eco = fan._eco_fan_curve(temp); \
		turbo = fan._turbo_fan_curve(temp); \
		silent = fan._silent_fan_curve(temp); \
		print(f'{temp:8d} | {auto:4.0f}% | {eco:3.0f}% | {turbo:5.0f}% | {silent:6.0f}%'); \
	fan.cleanup()" || echo "Curve visualization failed"

# Energy statistics
energy:
	@echo "Energy Saving Analysis"
	@echo "====================="
	@$(PYTHON) -c "import time; \
	print('Comparing modes at 30°C:'); \
	speeds = {'Auto': 60, 'Eco': 30, 'Turbo': 100, 'Silent': 20}; \
	power_per_percent = 0.5; \
	for mode, speed in speeds.items(): \
		power = speed * power_per_percent / 100; \
		daily_kwh = power * 24 / 1000; \
		monthly_cost = daily_kwh * 30 * 0.15; \
		print(f'  {mode:7s}: {speed:3d}% = {power:4.1f}W, ${monthly_cost:.2f}/month'); \
	print('\\nEco mode saves ~50% vs Auto mode')" || echo "Energy calculation failed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Note: Keeping $(CONFIG_FILE)"
	@echo "Use 'make reset' to clear configuration"

# Reset configuration
reset:
	@echo "Resetting configuration..."
	@rm -f $(CONFIG_FILE)
	@echo "✓ Configuration cleared"

# Help
help:
	@echo "Temperature-Controlled Smart Fan"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run       - Run the smart fan system (default)"
	@echo "  make test      - Test all hardware components"
	@echo "  make demo      - Run temperature demonstration"
	@echo "  make modes     - Test all operating modes"
	@echo "  make calibrate - Calibrate temperature sensor"
	@echo "  make monitor   - Monitor temperature readings"
	@echo ""
	@echo "Hardware Testing:"
	@echo "  make temp      - Test temperature sensor"
	@echo "  make fan       - Test fan control"
	@echo "  make lcd       - Test LCD display"
	@echo "  make leds      - Test status LEDs"
	@echo "  make buttons   - Test control buttons"
	@echo "  make adc       - Test ADC channels"
	@echo "  make rpm       - Test RPM measurement"
	@echo ""
	@echo "Features:"
	@echo "  make graph     - Live temperature graph"
	@echo "  make curves    - Show fan speed curves"
	@echo "  make energy    - Energy usage analysis"
	@echo ""
	@echo "System Management:"
	@echo "  make setup     - Complete system setup"
	@echo "  make install   - Install dependencies only"
	@echo "  make status    - Check system status"
	@echo "  make clean     - Clean cache files"
	@echo "  make reset     - Reset configuration"
	@echo "  make help      - Show this help"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - 10K NTC thermistor"
	@echo "  - ADC0834 ADC converter"
	@echo "  - 4-wire PWM fan (12V)"
	@echo "  - 16x2 LCD with I2C"
	@echo "  - 4x Status LEDs"
	@echo "  - 4x Control buttons"
	@echo "  - 10kΩ potentiometer"
	@echo ""
	@echo "Pin Connections:"
	@echo "  ADC: CS=GPIO5, CLK=GPIO6, DI=GPIO16, DO=GPIO12"
	@echo "  Fan: PWM=GPIO18, TACH=GPIO17, ENABLE=GPIO27"
	@echo "  LEDs: Cool=GPIO22, Normal=GPIO23, Warm=GPIO24, Hot=GPIO25"
	@echo "  Buttons: Mode=GPIO19, Up=GPIO20, Down=GPIO21, Power=GPIO26"
	@echo "  LCD: SDA=GPIO2, SCL=GPIO3 (I2C)"
	@echo "  Buzzer: GPIO13"
	@echo ""
	@echo "Operating Modes:"
	@echo "  Auto:    Balanced cooling"
	@echo "  Manual:  User-controlled"
	@echo "  Eco:     Energy saving"
	@echo "  Turbo:   Maximum cooling"
	@echo "  Silent:  Quiet operation"
	@echo "  Schedule: Time-based control"