# Makefile for LED Traffic Light Control System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := led-traffic-light-system.py

# Phony targets
.PHONY: run test demo timing lights pedestrian emergency modes lcd buttons cycle setup install status clean help

# Run the main program
run:
	@echo "Starting LED Traffic Light System..."
	@$(PYTHON) $(PROGRAM)

# Test all hardware components
test:
	@echo "Testing traffic light hardware..."
	@echo "1. Testing traffic lights..."
	@$(MAKE) lights
	@echo "2. Testing pedestrian system..."
	@$(MAKE) pedestrian
	@echo "3. Testing emergency system..."
	@$(MAKE) emergency
	@echo "4. Testing LCD display..."
	@$(MAKE) lcd
	@echo "5. Testing control buttons..."
	@$(MAKE) buttons

# Run traffic pattern demonstration
demo:
	@echo "Running traffic pattern demo..."
	@$(PYTHON) $(PROGRAM) demo

# Test individual lights
lights:
	@echo "Testing individual traffic lights..."
	@$(PYTHON) $(PROGRAM) test

# Test timing sequences
timing:
	@echo "Testing timing sequences..."
	@$(PYTHON) -c "import time; \
	sequences = [ \
		('Green', 30), \
		('Yellow', 3), \
		('All Red', 2) \
	]; \
	print('Standard timing sequence:'); \
	for phase, duration in sequences: \
		print(f'  {phase}: {duration} seconds'); \
		start = time.time(); \
		time.sleep(duration); \
		actual = time.time() - start; \
		error = abs(actual - duration); \
		status = '✓' if error < 0.1 else '✗'; \
		print(f'    {status} Actual: {actual:.2f}s (error: {error:.3f}s)'); \
	print('✓ Timing test complete')" || echo "Timing test failed"

# Test pedestrian crossing system
pedestrian:
	@echo "Testing pedestrian crossing system..."
	@$(PYTHON) -c "from gpiozero import LED, Buzzer, Button; import time; \
	ped_red = LED(20); \
	ped_green = LED(16); \
	ped_buzzer = Buzzer(18); \
	print('Testing pedestrian signals...'); \
	print('  Don\\'t Walk (Red)...'); \
	ped_red.on(); \
	ped_green.off(); \
	time.sleep(1); \
	print('  Walk (Green)...'); \
	ped_red.off(); \
	ped_green.on(); \
	time.sleep(1); \
	print('  Audio signal...'); \
	for i in range(5): \
		ped_buzzer.beep(0.1, 0.4, n=1); \
		time.sleep(0.5); \
	print('  Flashing warning...'); \
	for _ in range(3): \
		ped_green.off(); \
		time.sleep(0.3); \
		ped_green.on(); \
		time.sleep(0.3); \
	ped_red.on(); \
	ped_green.off(); \
	ped_red.close(); \
	ped_green.close(); \
	ped_buzzer.close(); \
	print('✓ Pedestrian system test complete')" 2>/dev/null || echo "❌ Pedestrian test failed"

# Test emergency system
emergency:
	@echo "Testing emergency system..."
	@$(PYTHON) -c "from gpiozero import PWMLED, Button; import time; \
	emergency_led = PWMLED(15); \
	print('Testing emergency indicator...'); \
	print('  Emergency LED pulsing...'); \
	emergency_led.pulse(fade_in_time=0.2, fade_out_time=0.2); \
	time.sleep(3); \
	print('  Emergency LED flashing...'); \
	emergency_led.blink(on_time=0.2, off_time=0.2); \
	time.sleep(3); \
	emergency_led.off(); \
	emergency_led.close(); \
	print('✓ Emergency system test complete')" 2>/dev/null || echo "❌ Emergency test failed"

# Test operating modes
modes:
	@echo "Testing operating modes..."
	@$(PYTHON) -c "from led_traffic_light_system import TrafficMode; \
	print('Available traffic modes:'); \
	for mode in TrafficMode: \
		print(f'  - {mode.value}'); \
		if mode == TrafficMode.STANDARD: \
			print('    Equal timing all directions'); \
		elif mode == TrafficMode.PEAK_HOURS: \
			print('    Optimized for rush hour'); \
		elif mode == TrafficMode.NIGHT_MODE: \
			print('    Reduced timing, faster cycles'); \
		elif mode == TrafficMode.MAINTENANCE: \
			print('    All yellows flashing'); \
	print('✓ Mode test complete')" || echo "Mode test failed"

# Test LCD display
lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Traffic Control'); \
	lcd.write(1, 0, 'System Test'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear(); \
	lcd.write(0, 0, 'Mode: Standard'); \
	lcd.write(1, 0, 'N-S GREEN 30s'); \
	print('✓ Status display test'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test control buttons
buttons:
	@echo "Testing control buttons (press each button, 15 seconds)..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = { \
		'PEDESTRIAN': Button(12), \
		'EMERGENCY': Button(14), \
		'MODE': Button(8), \
		'MANUAL': Button(7) \
	}; \
	print('Press each button:'); \
	start = time.time(); \
	pressed = set(); \
	while time.time() - start < 15: \
		for name, btn in buttons.items(): \
			if btn.is_pressed and name not in pressed: \
				print(f'  ✓ {name} button pressed'); \
				pressed.add(name); \
		if len(pressed) == 4: \
			break; \
		time.sleep(0.1); \
	[btn.close() for btn in buttons.values()]; \
	if len(pressed) < 4: \
		print(f'  ⚠ Only {len(pressed)}/4 buttons tested'); \
	else: \
		print('✓ All buttons tested')" 2>/dev/null || echo "❌ Button test failed"

# Test complete traffic cycle
cycle:
	@echo "Testing complete traffic cycle..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	# Define all lights \
	lights = { \
		'north': {'red': LED(17), 'yellow': LED(27), 'green': LED(22)}, \
		'south': {'red': LED(23), 'yellow': LED(24), 'green': LED(25)}, \
		'east': {'red': LED(5), 'yellow': LED(6), 'green': LED(13)}, \
		'west': {'red': LED(19), 'yellow': LED(26), 'green': LED(21)} \
	}; \
	print('Running abbreviated traffic cycle...'); \
	# All red \
	print('  All RED (safety)'); \
	for direction in lights.values(): \
		direction['red'].on(); \
		direction['yellow'].off(); \
		direction['green'].off(); \
	time.sleep(1); \
	# N-S Green \
	print('  North-South GREEN'); \
	lights['north']['red'].off(); \
	lights['north']['green'].on(); \
	lights['south']['red'].off(); \
	lights['south']['green'].on(); \
	time.sleep(2); \
	# N-S Yellow \
	print('  North-South YELLOW'); \
	lights['north']['green'].off(); \
	lights['north']['yellow'].on(); \
	lights['south']['green'].off(); \
	lights['south']['yellow'].on(); \
	time.sleep(1); \
	# All red \
	print('  All RED (transition)'); \
	for direction in lights.values(): \
		direction['red'].on(); \
		direction['yellow'].off(); \
		direction['green'].off(); \
	time.sleep(1); \
	# E-W Green \
	print('  East-West GREEN'); \
	lights['east']['red'].off(); \
	lights['east']['green'].on(); \
	lights['west']['red'].off(); \
	lights['west']['green'].on(); \
	time.sleep(2); \
	# E-W Yellow \
	print('  East-West YELLOW'); \
	lights['east']['green'].off(); \
	lights['east']['yellow'].on(); \
	lights['west']['green'].off(); \
	lights['west']['yellow'].on(); \
	time.sleep(1); \
	# Final all red \
	print('  All RED (final)'); \
	for direction in lights.values(): \
		direction['red'].on(); \
		direction['yellow'].off(); \
		direction['green'].off(); \
	# Cleanup \
	for direction in lights.values(): \
		for led in direction.values(): \
			led.close(); \
	print('✓ Traffic cycle test complete')" 2>/dev/null || echo "❌ Cycle test failed"

# Simulate rush hour
rushhour:
	@echo "Simulating rush hour traffic..."
	@$(PYTHON) -c "print('Rush Hour Simulation'); \
	print('=================='); \
	print('North-South: Main arterial road'); \
	print('East-West: Side streets'); \
	print(''); \
	print('Peak hour timing:'); \
	print('  N-S Green: 45 seconds (150% normal)'); \
	print('  E-W Green: 25 seconds (83% normal)'); \
	print('  Total cycle: 78 seconds'); \
	print(''); \
	print('Traffic flow optimization:'); \
	print('  - Longer green for main road'); \
	print('  - Shorter cycles for side streets'); \
	print('  - Reduced pedestrian crossing time'); \
	print('  - Emergency vehicle priority enabled')" || echo "Simulation failed"

# Setup system and dependencies
setup:
	@echo "Setting up LED Traffic Light System..."
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
	@echo "Traffic Light System Status"
	@echo "==========================="
	@echo "Hardware Configuration:"
	@echo "  Traffic Lights: 4 directions × 3 colors = 12 LEDs"
	@echo "  Pedestrian: 2 LEDs + 1 buzzer"
	@echo "  Control: 4 buttons"
	@echo "  Emergency: 1 LED"
	@echo ""
	@echo "GPIO Pin Usage:"
	@echo "  North: Red=17, Yellow=27, Green=22"
	@echo "  South: Red=23, Yellow=24, Green=25"
	@echo "  East:  Red=5,  Yellow=6,  Green=13"
	@echo "  West:  Red=19, Yellow=26, Green=21"
	@echo "  Pedestrian: Red=20, Green=16, Button=12, Buzzer=18"
	@echo "  Emergency: Button=14, LED=15"
	@echo "  Control: Mode=8, Manual=7"
	@echo ""
	@echo "System Features:"
	@echo "  ✓ Multi-direction control"
	@echo "  ✓ Pedestrian crossing"
	@echo "  ✓ Emergency vehicle priority"
	@echo "  ✓ Multiple operating modes"
	@echo "  ✓ LCD status display"
	@echo "  ✓ Safety interlocks"

# Traffic statistics
stats:
	@echo "Traffic Light Statistics"
	@echo "======================="
	@$(PYTHON) -c "import random; \
	# Simulate traffic data \
	cycles = 847; \
	runtime = cycles * 70 / 60; \
	pedestrians = int(cycles * 0.15); \
	emergencies = int(cycles * 0.02); \
	violations = int(cycles * 0.05); \
	print(f'Simulated statistics for {runtime:.0f} minutes:'); \
	print(f'  Traffic cycles: {cycles}'); \
	print(f'  Pedestrian crossings: {pedestrians}'); \
	print(f'  Emergency vehicles: {emergencies}'); \
	print(f'  Violations detected: {violations}'); \
	print(f'  Average cycle time: 70 seconds'); \
	print(f'  Green light efficiency: 85.7%'); \
	print(f'  Safety compliance: 98.5%')" || echo "Statistics generation failed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f traffic_config.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "LED Traffic Light Control System"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the traffic light system (default)"
	@echo "  make test       - Test all hardware components"
	@echo "  make demo       - Run traffic pattern demonstration"
	@echo "  make lights     - Test individual traffic lights"
	@echo "  make timing     - Test timing sequences"
	@echo ""
	@echo "Component Testing:"
	@echo "  make pedestrian - Test pedestrian crossing system"
	@echo "  make emergency  - Test emergency system"
	@echo "  make modes      - Show operating modes"
	@echo "  make lcd        - Test LCD display"
	@echo "  make buttons    - Test control buttons"
	@echo "  make cycle      - Test complete traffic cycle"
	@echo ""
	@echo "Features:"
	@echo "  make rushhour   - Simulate rush hour traffic"
	@echo "  make stats      - Show traffic statistics"
	@echo ""
	@echo "System Management:"
	@echo "  make setup      - Complete system setup"
	@echo "  make install    - Install dependencies only"
	@echo "  make status     - Check system configuration"
	@echo "  make clean      - Clean cache files"
	@echo "  make help       - Show this help"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - 12x LEDs for traffic lights (R/Y/G × 4)"
	@echo "  - 2x LEDs for pedestrian signals"
	@echo "  - 1x LED for emergency indicator"
	@echo "  - 4x Push buttons"
	@echo "  - 1x Buzzer"
	@echo "  - 16x2 LCD with I2C"
	@echo ""
	@echo "Operating Modes:"
	@echo "  Standard:    Equal timing all directions"
	@echo "  Peak Hours:  Optimized for main routes"
	@echo "  Night Mode:  Reduced timing, quick cycles"
	@echo "  Pedestrian:  Safe crossing priority"
	@echo "  Emergency:   All red with warnings"
	@echo "  Manual:      Direct control"
	@echo "  Maintenance: Flashing yellow caution"