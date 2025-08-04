# Makefile for Morse Code Communicator

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := morse-code-communicator.py

# Phony targets
.PHONY: run test demo chart translator decoder trainer game beacon alphabet prosigns speed clean setup install help

# Run the main program
run:
	@echo "Starting Morse Code Communicator..."
	@$(PYTHON) $(PROGRAM)

# Run morse code demo
demo:
	@echo "Running Morse code demonstrations..."
	@$(PYTHON) $(PROGRAM) demo

# Test all components
test:
	@echo "Testing Morse code hardware..."
	@echo "1. Testing LED output..."
	@$(MAKE) test-led
	@echo "2. Testing buzzer output..."
	@$(MAKE) test-buzzer
	@echo "3. Testing key input..."
	@$(MAKE) test-key
	@echo "4. Testing control buttons..."
	@$(MAKE) test-buttons
	@echo "5. Testing LCD display..."
	@$(MAKE) test-lcd

# Test LED output
test-led:
	@echo "Testing Morse LED..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	led = LED(17); \
	print('Transmitting SOS...'); \
	for _ in range(3): led.on(); time.sleep(0.1); led.off(); time.sleep(0.1); \
	time.sleep(0.3); \
	for _ in range(3): led.on(); time.sleep(0.3); led.off(); time.sleep(0.1); \
	time.sleep(0.3); \
	for _ in range(3): led.on(); time.sleep(0.1); led.off(); time.sleep(0.1); \
	led.close(); \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test buzzer output
test-buzzer:
	@echo "Testing Morse buzzer..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	buzzer = Buzzer(27); \
	print('Playing Morse tones...'); \
	for i in range(3): \
		buzzer.on(); time.sleep(0.1); buzzer.off(); time.sleep(0.2); \
	buzzer.close(); \
	print('✓ Buzzer test complete')" 2>/dev/null || echo "❌ Buzzer test failed"

# Test telegraph key
test-key:
	@echo "Testing telegraph key input..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	key = Button(22, pull_up=True); \
	print('Press the telegraph key (5 seconds)...'); \
	start = time.time(); \
	presses = 0; \
	def pressed(): \
		global presses; \
		presses += 1; \
		print(f'  Key pressed (count: {presses})'); \
	key.when_pressed = pressed; \
	while time.time() - start < 5: \
		time.sleep(0.1); \
	key.close(); \
	print(f'✓ Key test complete. Total presses: {presses}')" 2>/dev/null || echo "❌ Key test failed"

# Test control buttons
test-buttons:
	@echo "Testing control buttons..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = {'Mode': Button(23), 'Speed Up': Button(24), 'Speed Down': Button(25)}; \
	print('Press control buttons (10 seconds)...'); \
	for name, btn in buttons.items(): \
		btn.when_pressed = lambda n=name: print(f'  {n} button pressed'); \
	time.sleep(10); \
	[b.close() for b in buttons.values()]; \
	print('✓ Button test complete')" 2>/dev/null || echo "❌ Button test failed"

# Test LCD display
test-lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Morse Code'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Display Morse code chart
chart:
	@echo "International Morse Code Chart"
	@echo "=============================="
	@$(PYTHON) -c "chart = { \
		'A': '·−', 'B': '−···', 'C': '−·−·', 'D': '−··', 'E': '·', \
		'F': '··−·', 'G': '−−·', 'H': '····', 'I': '··', 'J': '·−−−', \
		'K': '−·−', 'L': '·−··', 'M': '−−', 'N': '−·', 'O': '−−−', \
		'P': '·−−·', 'Q': '−−·−', 'R': '·−·', 'S': '···', 'T': '−', \
		'U': '··−', 'V': '···−', 'W': '·−−', 'X': '−··−', 'Y': '−·−−', \
		'Z': '−−··', \
		'0': '−−−−−', '1': '·−−−−', '2': '··−−−', '3': '···−−', \
		'4': '····−', '5': '·····', '6': '−····', '7': '−−···', \
		'8': '−−−··', '9': '−−−−·' \
	}; \
	for i, (char, morse) in enumerate(chart.items()): \
		print(f'{char}: {morse:<8}', end='  '); \
		if (i + 1) % 5 == 0: print(); \
	print(); \
	print('\\nPunctuation:'); \
	punct = { \
		'.': '·−·−·−', ',': '−−··−−', '?': '··−−··', \
		"'": '·−−−−·', '!': '−·−·−−', '/': '−··−·' \
	}; \
	for char, morse in punct.items(): \
		print(f'{char}: {morse}')" || echo "Chart display failed"

# Mode demonstrations
translator:
	@echo "Starting Translator Mode Demo..."
	@$(PYTHON) -c "print('Translator Mode: Type text to convert to Morse'); \
	print('Example: HELLO → ···· · ·−·· ·−·· −−−'); \
	print('The system would transmit this via LED and buzzer')" || echo "Demo failed"

decoder:
	@echo "Starting Decoder Mode Demo..."
	@$(PYTHON) -c "print('Decoder Mode: Input Morse via telegraph key'); \
	print('Example: ··· −−− ··· → SOS'); \
	print('System decodes your key presses in real-time')" || echo "Demo failed"

trainer:
	@echo "Starting Trainer Mode Demo..."
	@$(PYTHON) -c "print('Trainer Mode: Learn Morse code interactively'); \
	print('System transmits a character, you echo it back'); \
	print('Tracks accuracy and progress')" || echo "Demo failed"

game:
	@echo "Starting Game Mode Demo..."
	@$(PYTHON) -c "print('Game Mode: Random Morse challenges'); \
	print('Listen to transmitted words and decode them'); \
	print('Score points for correct answers')" || echo "Demo failed"

beacon:
	@echo "Starting Beacon Mode Demo..."
	@$(PYTHON) -c "print('Beacon Mode: Automatic repeating transmission'); \
	print('Default message: CQ CQ CQ DE RASPI'); \
	print('Transmits every 30 seconds')" || echo "Demo failed"

# Transmit the alphabet
alphabet:
	@echo "Transmitting Morse alphabet..."
	@$(PYTHON) -c "from gpiozero import LED, Buzzer; import time; \
	led = LED(17); buzzer = Buzzer(27); \
	morse = {'A': '.-', 'B': '-...', 'C': '-.-.'}; \
	for char, code in morse.items(): \
		print(f'{char} = {code}'); \
		for symbol in code: \
			led.on(); buzzer.on(); \
			time.sleep(0.1 if symbol == '.' else 0.3); \
			led.off(); buzzer.off(); \
			time.sleep(0.1); \
		time.sleep(0.5); \
	led.close(); buzzer.close()" 2>/dev/null || echo "❌ Alphabet transmission failed"

# Show prosigns
prosigns:
	@echo "Morse Code Prosigns (Procedural Signals)"
	@echo "========================================"
	@echo "AR (·−·−·)  - End of message"
	@echo "AS (·−···)  - Wait/Stand by"
	@echo "BT (−···−)  - Break/New paragraph"
	@echo "SK (···−·−) - End of contact"
	@echo "SOS (···−−−···) - Distress call"
	@echo "ERROR (········) - Mistake/correction"
	@echo ""
	@echo "Common Abbreviations:"
	@echo "CQ  - Calling any station"
	@echo "DE  - From/This is"
	@echo "73  - Best regards"
	@echo "88  - Love and kisses"

# Speed demonstration
speed:
	@echo "Demonstrating different Morse speeds..."
	@$(PYTHON) -c "from gpiozero import LED, Buzzer; import time; \
	led = LED(17); buzzer = Buzzer(27); \
	speeds = [5, 10, 15, 20, 25]; \
	for wpm in speeds: \
		unit = 60.0 / (wpm * 50); \
		print(f'\\nSpeed: {wpm} WPM (unit time: {unit*1000:.0f}ms)'); \
		print('Sending E (·)...'); \
		led.on(); buzzer.on(); \
		time.sleep(unit); \
		led.off(); buzzer.off(); \
		time.sleep(1); \
	led.close(); buzzer.close()" 2>/dev/null || echo "❌ Speed demo failed"

# Setup system and dependencies
setup:
	@echo "Setting up Morse Code Communicator..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating default config..."
	@echo '{"wpm": 10, "beacon_message": "CQ CQ CQ DE RASPI", "beacon_interval": 30}' > morse_config.json
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero smbus2

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f morse_config.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "Morse Code Communicator"
	@echo "======================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run       - Run the communicator (default)"
	@echo "  make demo      - Run feature demonstrations"
	@echo "  make test      - Test all hardware components"
	@echo ""
	@echo "Component Testing:"
	@echo "  make test-led     - Test LED output"
	@echo "  make test-buzzer  - Test buzzer output"
	@echo "  make test-key     - Test telegraph key"
	@echo "  make test-buttons - Test control buttons"
	@echo "  make test-lcd     - Test LCD display"
	@echo ""
	@echo "Information:"
	@echo "  make chart     - Display Morse code chart"
	@echo "  make prosigns  - Show prosigns and abbreviations"
	@echo ""
	@echo "Mode Demos:"
	@echo "  make translator - Translator mode info"
	@echo "  make decoder    - Decoder mode info"
	@echo "  make trainer    - Trainer mode info"
	@echo "  make game       - Game mode info"
	@echo "  make beacon     - Beacon mode info"
	@echo ""
	@echo "Feature Demos:"
	@echo "  make alphabet  - Transmit A-B-C"
	@echo "  make speed     - Speed demonstration"
	@echo ""
	@echo "System Management:"
	@echo "  make setup     - Complete system setup"
	@echo "  make install   - Install dependencies only"
	@echo "  make clean     - Clean cache and configs"
	@echo "  make help      - Show this help"
	@echo ""
	@echo "Operating Instructions:"
	@echo "  KEY button: Input Morse code"
	@echo "  MODE button: Cycle through modes"
	@echo "  SPEED UP: Increase WPM"
	@echo "  SPEED DOWN: Decrease WPM"
	@echo ""
	@echo "Default Settings:"
	@echo "  Speed: 10 WPM"
	@echo "  Beacon: CQ CQ CQ DE RASPI"
	@echo "  Beacon interval: 30 seconds"