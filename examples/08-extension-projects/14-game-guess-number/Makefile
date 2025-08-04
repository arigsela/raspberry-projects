# Makefile for Number Guessing Game

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := number-guessing-game.py

# Phony targets
.PHONY: run test demo scores stats modes hints leds sounds perfect strategy clean setup install help

# Run the main game
run:
	@echo "Starting Number Guessing Game..."
	@$(PYTHON) $(PROGRAM)

# Run hardware demonstration
demo:
	@echo "Running game demonstrations..."
	@$(PYTHON) $(PROGRAM) demo

# Test all components
test:
	@echo "Testing game hardware..."
	@echo "1. Testing buttons..."
	@$(MAKE) test-buttons
	@echo "2. Testing LEDs..."
	@$(MAKE) test-leds
	@echo "3. Testing buzzer..."
	@$(MAKE) test-buzzer
	@echo "4. Testing LCD..."
	@$(MAKE) test-lcd
	@echo "5. Testing 7-segment (if available)..."
	@$(MAKE) test-segment

# Test buttons
test-buttons:
	@echo "Testing control buttons..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = { \
		'UP': Button(17), \
		'DOWN': Button(27), \
		'SELECT': Button(22), \
		'MODE': Button(23) \
	}; \
	print('Press each button (10 seconds)...'); \
	for name, btn in buttons.items(): \
		btn.when_pressed = lambda n=name: print(f'  {n} pressed'); \
	time.sleep(10); \
	[b.close() for b in buttons.values()]; \
	print('✓ Button test complete')" 2>/dev/null || echo "❌ Button test failed"

# Test LEDs
test-leds:
	@echo "Testing LED indicators..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	leds = { \
		'HOT (Red)': LED(5), \
		'COLD (Blue)': LED(6), \
		'CORRECT (Green)': LED(13), \
		'POWER (White)': LED(19) \
	}; \
	for name, led in leds.items(): \
		print(f'  Testing {name} LED...'); \
		led.on(); \
		time.sleep(0.5); \
		led.off(); \
	[led.close() for led in leds.values()]; \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test buzzer
test-buzzer:
	@echo "Testing buzzer sounds..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	buzzer = Buzzer(26); \
	print('Button press beep...'); \
	buzzer.beep(0.05, 0, n=1); \
	time.sleep(0.5); \
	print('Wrong guess beep...'); \
	buzzer.beep(0.1, 0.1, n=2); \
	time.sleep(0.5); \
	print('Victory sound...'); \
	for _ in range(4): \
		buzzer.on(); time.sleep(0.1); \
		buzzer.off(); time.sleep(0.05); \
	buzzer.close(); \
	print('✓ Buzzer test complete')" 2>/dev/null || echo "❌ Buzzer test failed"

# Test LCD
test-lcd:
	@echo "Testing LCD display..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); \
	from lcd1602 import LCD1602; import time; \
	lcd = LCD1602(0x27); \
	lcd.clear(); \
	lcd.write(0, 0, 'Number Guess'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# Test 7-segment display
test-segment:
	@echo "Testing 7-segment display..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	segments = [LED(16), LED(20), LED(21), LED(12), LED(25), LED(24), LED(18)]; \
	print('Displaying 0-9...'); \
	patterns = [ \
		[1,1,1,1,1,1,0], [0,1,1,0,0,0,0], [1,1,0,1,1,0,1], \
		[1,1,1,1,0,0,1], [0,1,1,0,0,1,1], [1,0,1,1,0,1,1], \
		[1,0,1,1,1,1,1], [1,1,1,0,0,0,0], [1,1,1,1,1,1,1], \
		[1,1,1,1,0,1,1] \
	]; \
	for digit, pattern in enumerate(patterns): \
		for i, state in enumerate(pattern): \
			if state: segments[i].on(); \
			else: segments[i].off(); \
		time.sleep(0.3); \
	[s.close() for s in segments]; \
	print('✓ 7-segment test complete')" 2>/dev/null || echo "⚠ 7-segment not available"

# View high scores
scores:
	@echo "High Scores"
	@echo "==========="
	@if [ -f high_scores.json ]; then \
		$(PYTHON) -c "import json; \
		with open('high_scores.json') as f: \
			scores = json.load(f); \
			for mode, guesses in sorted(scores.items()): \
				print(f'{mode:<15} {guesses:>3} guesses')"; \
	else \
		echo "No high scores yet. Play some games!"; \
	fi

# View game statistics
stats:
	@echo "Game Statistics"
	@echo "==============="
	@if [ -f game_config.json ]; then \
		$(PYTHON) -c "import json; \
		try: \
			with open('game_config.json') as f: \
				config = json.load(f); \
				print(f'Sound: {config.get(\"sound\", True)}'); \
				print(f'Hints: {config.get(\"hints\", True)}'); \
				print(f'Difficulty: {config.get(\"difficulty\", \"Normal\")}'); \
		except: pass"; \
	else \
		echo "No saved configuration"; \
	fi

# Show game modes
modes:
	@echo "Available Game Modes"
	@echo "==================="
	@echo "1. EASY"
	@echo "   Range: 1-50"
	@echo "   Unlimited guesses"
	@echo "   Perfect for beginners"
	@echo ""
	@echo "2. NORMAL"
	@echo "   Range: 1-100"
	@echo "   Unlimited guesses"
	@echo "   Hints after 5 guesses"
	@echo ""
	@echo "3. HARD"
	@echo "   Range: 1-200"
	@echo "   Limited to 10 guesses"
	@echo "   Challenge mode"
	@echo ""
	@echo "4. EXTREME"
	@echo "   Range: 1-500"
	@echo "   15 guesses, 60s time limit"
	@echo "   Expert level"
	@echo ""
	@echo "5. BINARY"
	@echo "   Range: 1-128"
	@echo "   7 guesses (log₂ 128)"
	@echo "   Binary search practice"
	@echo ""
	@echo "6. CUSTOM"
	@echo "   User-defined range"
	@echo "   Configurable settings"

# Show hint system
hints:
	@echo "Hint System"
	@echo "==========="
	@echo "Hints are available after 5 guesses:"
	@echo ""
	@echo "Distance-based hints:"
	@echo "  < 5%  range: Very close! 🔥🔥🔥"
	@echo "  < 10% range: Getting warm! 🔥🔥"
	@echo "  < 20% range: Warmer... 🔥"
	@echo "  < 30% range: Cold ❄️"
	@echo "  > 30% range: Very cold! ❄️❄️"
	@echo ""
	@echo "Additional clues:"
	@echo "  - Even/Odd indicator"
	@echo "  - Divisibility hints"
	@echo "  - Range narrowing"

# LED feedback demo
leds:
	@echo "LED Feedback System"
	@echo "=================="
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	led_hot = LED(5); led_cold = LED(6); led_correct = LED(13); \
	print('Temperature feedback:'); \
	print('  Getting warmer...'); \
	led_hot.on(); time.sleep(1); led_hot.off(); \
	print('  Getting colder...'); \
	led_cold.on(); time.sleep(1); led_cold.off(); \
	print('  Correct guess!'); \
	led_correct.on(); time.sleep(1); led_correct.off(); \
	led_hot.close(); led_cold.close(); led_correct.close()" 2>/dev/null || echo "❌ LED demo failed"

# Sound effects demo
sounds:
	@echo "Sound Effects Demo"
	@echo "================="
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	buzzer = Buzzer(26); \
	print('1. Button press'); \
	buzzer.beep(0.05, 0, n=1); time.sleep(0.5); \
	print('2. Too low'); \
	buzzer.beep(0.1, 0.1, n=1); time.sleep(0.5); \
	print('3. Too high'); \
	buzzer.beep(0.2, 0.1, n=1); time.sleep(0.5); \
	print('4. Victory!'); \
	for _ in range(4): \
		buzzer.on(); time.sleep(0.1); \
		buzzer.off(); time.sleep(0.05); \
	buzzer.close()" 2>/dev/null || echo "❌ Sound demo failed"

# Perfect game strategy
perfect:
	@echo "Perfect Game Strategy (Binary Search)"
	@echo "====================================="
	@echo "For a range of 1-100:"
	@echo ""
	@echo "Optimal guesses: ⌈log₂(100)⌉ = 7"
	@echo ""
	@echo "Strategy:"
	@echo "1. First guess: 50 (middle)"
	@echo "2. If too high: guess 25"
	@echo "   If too low:  guess 75"
	@echo "3. Continue halving the range"
	@echo ""
	@echo "Example (target=67):"
	@echo "  Guess 1: 50 (too low)  → Range: 51-100"
	@echo "  Guess 2: 75 (too high) → Range: 51-74"
	@echo "  Guess 3: 63 (too low)  → Range: 64-74"
	@echo "  Guess 4: 69 (too high) → Range: 64-68"
	@echo "  Guess 5: 66 (too low)  → Range: 67-68"
	@echo "  Guess 6: 67 (correct!) ✓"

# Strategy tips
strategy:
	@echo "Guessing Strategies"
	@echo "=================="
	@echo "1. Binary Search (Optimal)"
	@echo "   - Always guess the middle"
	@echo "   - Guarantees win in ⌈log₂(n)⌉ guesses"
	@echo ""
	@echo "2. Linear Search"
	@echo "   - Guess sequentially (1,2,3...)"
	@echo "   - Simple but inefficient"
	@echo ""
	@echo "3. Random Guessing"
	@echo "   - Unpredictable"
	@echo "   - Fun but not optimal"
	@echo ""
	@echo "4. Pattern Recognition"
	@echo "   - Use hints effectively"
	@echo "   - Learn from temperature feedback"
	@echo ""
	@echo "5. Psychological Strategy"
	@echo "   - Common numbers: 7, 42, 69"
	@echo "   - Round numbers: 50, 100"

# Setup system and dependencies
setup:
	@echo "Setting up Number Guessing Game..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating default config..."
	@echo '{"sound": true, "hints": true, "difficulty": "Normal"}' > game_config.json
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
	rm -f game_config.json
	rm -f high_scores.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "Number Guessing Game"
	@echo "==================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run       - Play the game (default)"
	@echo "  make demo      - Run hardware demo"
	@echo "  make test      - Test all components"
	@echo ""
	@echo "Component Testing:"
	@echo "  make test-buttons - Test control buttons"
	@echo "  make test-leds    - Test LED indicators"
	@echo "  make test-buzzer  - Test buzzer sounds"
	@echo "  make test-lcd     - Test LCD display"
	@echo "  make test-segment - Test 7-segment display"
	@echo ""
	@echo "Game Information:"
	@echo "  make scores    - View high scores"
	@echo "  make stats     - View game statistics"
	@echo "  make modes     - Show game modes"
	@echo "  make hints     - Explain hint system"
	@echo ""
	@echo "Demonstrations:"
	@echo "  make leds      - LED feedback demo"
	@echo "  make sounds    - Sound effects demo"
	@echo ""
	@echo "Strategy:"
	@echo "  make perfect   - Perfect game example"
	@echo "  make strategy  - Guessing strategies"
	@echo ""
	@echo "System Management:"
	@echo "  make setup     - Complete system setup"
	@echo "  make install   - Install dependencies only"
	@echo "  make clean     - Clean cache and data"
	@echo "  make help      - Show this help"
	@echo ""
	@echo "Controls:"
	@echo "  UP/DOWN: Change guess value"
	@echo "  SELECT: Confirm guess"
	@echo "  MODE: Change mode or show hint"
	@echo ""
	@echo "LED Indicators:"
	@echo "  Red: Getting warmer"
	@echo "  Blue: Getting colder"
	@echo "  Green: Correct guess"
	@echo "  White: Power on"