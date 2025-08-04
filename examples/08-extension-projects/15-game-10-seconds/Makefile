# Makefile for Reaction Time Challenge Game

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := reaction-time-game.py

# Phony targets
.PHONY: run test demo scores stats modes tensec reaction sequence pattern speed challenge clean setup install help

# Run the main game
run:
	@echo "Starting Reaction Time Challenge..."
	@$(PYTHON) $(PROGRAM)

# Run hardware demonstration
demo:
	@echo "Running reaction game demonstrations..."
	@$(PYTHON) $(PROGRAM) demo

# Test all components
test:
	@echo "Testing game hardware..."
	@echo "1. Testing colored buttons..."
	@$(MAKE) test-buttons
	@echo "2. Testing colored LEDs..."
	@$(MAKE) test-leds
	@echo "3. Testing status LEDs..."
	@$(MAKE) test-status
	@echo "4. Testing buzzer..."
	@$(MAKE) test-buzzer
	@echo "5. Testing LCD..."
	@$(MAKE) test-lcd

# Test game buttons
test-buttons:
	@echo "Testing colored game buttons..."
	@$(PYTHON) -c "from gpiozero import Button; import time; \
	buttons = { \
		'RED': Button(17), \
		'GREEN': Button(27), \
		'BLUE': Button(22), \
		'YELLOW': Button(23), \
		'START': Button(24), \
		'MODE': Button(25) \
	}; \
	print('Press each button (15 seconds)...'); \
	for name, btn in buttons.items(): \
		btn.when_pressed = lambda n=name: print(f'  {n} button pressed'); \
	time.sleep(15); \
	[b.close() for b in buttons.values()]; \
	print('✓ Button test complete')" 2>/dev/null || echo "❌ Button test failed"

# Test colored LEDs
test-leds:
	@echo "Testing colored LED indicators..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	leds = { \
		'RED': LED(5), \
		'GREEN': LED(6), \
		'BLUE': LED(13), \
		'YELLOW': LED(19) \
	}; \
	for name, led in leds.items(): \
		print(f'  Testing {name} LED...'); \
		led.on(); \
		time.sleep(0.5); \
		led.off(); \
		time.sleep(0.2); \
	print('  Pattern test...'); \
	for _ in range(2): \
		for led in leds.values(): \
			led.on(); \
			time.sleep(0.1); \
			led.off(); \
	[led.close() for led in leds.values()]; \
	print('✓ LED test complete')" 2>/dev/null || echo "❌ LED test failed"

# Test status LEDs
test-status:
	@echo "Testing status indicators..."
	@$(PYTHON) -c "from gpiozero import LED; import time; \
	status = { \
		'READY (White)': LED(16), \
		'ACTIVE (Orange)': LED(20), \
		'RECORD (Purple)': LED(21) \
	}; \
	for name, led in status.items(): \
		print(f'  Testing {name} LED...'); \
		led.on(); \
		time.sleep(0.5); \
		led.off(); \
	[led.close() for led in status.values()]; \
	print('✓ Status LED test complete')" 2>/dev/null || echo "❌ Status test failed"

# Test buzzer
test-buzzer:
	@echo "Testing buzzer sounds..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; \
	buzzer = Buzzer(26); \
	print('Game sounds:'); \
	print('  Beep...'); \
	buzzer.beep(0.1, 0, n=1); \
	time.sleep(0.5); \
	print('  Success...'); \
	for _ in range(2): \
		buzzer.on(); time.sleep(0.05); \
		buzzer.off(); time.sleep(0.05); \
	time.sleep(0.5); \
	print('  Fanfare...'); \
	for duration in [0.1, 0.1, 0.1, 0.2]: \
		buzzer.on(); time.sleep(duration); \
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
	lcd.write(0, 0, 'Reaction Game'); \
	lcd.write(1, 0, 'LCD Test OK'); \
	print('✓ LCD initialized'); \
	time.sleep(2); \
	lcd.clear(); \
	lcd.write(0, 0, '10 Second Timer'); \
	lcd.write(1, 0, 'Ready!'); \
	time.sleep(2); \
	lcd.clear()" 2>/dev/null || echo "❌ LCD test failed"

# View high scores
scores:
	@echo "High Scores"
	@echo "==========="
	@if [ -f reaction_scores.json ]; then \
		$(PYTHON) -c "import json; \
		with open('reaction_scores.json') as f: \
			data = json.load(f); \
			for mode, scores in data.items(): \
				if scores: \
					print(f'\\n{mode}:'); \
					for i, score in enumerate(scores[:5], 1): \
						print(f'  {i}. {score}')"; \
	else \
		echo "No high scores yet. Play some games!"; \
	fi

# View game statistics
stats:
	@echo "Game Statistics"
	@echo "==============="
	@if [ -f reaction_config.json ]; then \
		$(PYTHON) -c "import json; \
		with open('reaction_config.json') as f: \
			config = json.load(f); \
			print(f'Player: {config.get(\"player_name\", \"Player1\")}'); \
			print(f'Sound: {config.get(\"sound\", True)}'); \
			print(f'Difficulty: {config.get(\"difficulty\", \"Normal\")}'); \
			if 'last_played' in config: \
				print(f'Last played: {config[\"last_played\"][:10]}')"; \
	else \
		echo "No saved configuration"; \
	fi

# Show game modes
modes:
	@echo "Available Game Modes"
	@echo "==================="
	@echo "1. 10 SECOND TIMER"
	@echo "   Stop at exactly 10 seconds"
	@echo "   Perfect timing = 1000 points"
	@echo ""
	@echo "2. REACTION TIME"
	@echo "   Test your reflexes"
	@echo "   5 rounds, average calculated"
	@echo ""
	@echo "3. MEMORY SEQUENCE"
	@echo "   Simon Says style"
	@echo "   Pattern grows each round"
	@echo ""
	@echo "4. PATTERN MATCH"
	@echo "   Copy shown patterns"
	@echo "   Build combos for bonus"
	@echo ""
	@echo "5. SPEED TEST"
	@echo "   Hit 20 targets fast"
	@echo "   Timed for speed"
	@echo ""
	@echo "6. ENDURANCE"
	@echo "   How long can you last?"
	@echo "   Increasing difficulty"
	@echo ""
	@echo "7. 2 PLAYER VS"
	@echo "   Competitive mode"
	@echo "   Best of 5 rounds"

# 10-second timer tips
tensec:
	@echo "10-Second Timer Challenge"
	@echo "========================="
	@echo "Goal: Stop the timer at exactly 10.000 seconds"
	@echo ""
	@echo "Scoring:"
	@echo "  < 0.05s off = PERFECT! (1000 pts)"
	@echo "  < 0.10s off = Excellent (500 pts)"
	@echo "  < 0.50s off = Good (100 pts)"
	@echo "  < 1.00s off = OK (50 pts)"
	@echo "  > 1.00s off = Try again (10 pts)"
	@echo ""
	@echo "Tips:"
	@echo "  - Count steadily in your head"
	@echo "  - Use a consistent rhythm"
	@echo "  - Practice makes perfect"
	@echo "  - Don't watch a clock!"

# Reaction time demo
reaction:
	@echo "Reaction Time Test"
	@echo "=================="
	@$(PYTHON) -c "import random, time; \
	print('Simulating reaction test...'); \
	print(''); \
	for i in range(3): \
		print(f'Round {i+1}: Ready...'); \
		delay = random.uniform(1.5, 3.5); \
		time.sleep(delay); \
		print('  GO! Press the button!'); \
		reaction = random.uniform(180, 300); \
		time.sleep(reaction/1000); \
		print(f'  Reaction time: {reaction:.0f}ms'); \
		print(''); \
	avg = 230; \
	print(f'Average: {avg}ms'); \
	print(f'Score: {int(10000/avg)}')" || echo "Demo failed"

# Sequence memory demo
sequence:
	@echo "Memory Sequence Demo"
	@echo "==================="
	@echo "Watch the pattern:"
	@echo ""
	@echo "Round 1: 🔴"
	@echo "Round 2: 🔴 🟢"
	@echo "Round 3: 🔴 🟢 🔵"
	@echo "Round 4: 🔴 🟢 🔵 🟡"
	@echo "Round 5: 🔴 🟢 🔵 🟡 🔴"
	@echo ""
	@echo "Repeat the pattern exactly!"
	@echo "Each round adds one more color"
	@echo "Maximum sequence: 20 colors"

# Pattern matching demo
pattern:
	@echo "Pattern Matching Examples"
	@echo "========================="
	@echo "Sequential:  🔴 🟢 🔵 🟡"
	@echo "Cross:       🔴 🔵 🟢 🟡"
	@echo "Doubles:     🔴 🔴 🟢 🟢"
	@echo "Alternating: 🔴 🟢 🔴 🟢"
	@echo "Reverse:     🟡 🔵 🟢 🔴"
	@echo "Up & Back:   🔴 🟢 🔵 🟢"
	@echo "Diagonal:    🔴 🟡 🟢 🔵"
	@echo ""
	@echo "Match patterns to build combos!"

# Speed test challenge
speed:
	@echo "Speed Test Challenge"
	@echo "==================="
	@echo "Hit 20 targets as fast as possible!"
	@echo ""
	@echo "Strategy:"
	@echo "  - Keep fingers on all buttons"
	@echo "  - Watch for the LED"
	@echo "  - React immediately"
	@echo "  - Don't guess!"
	@echo ""
	@echo "Good time: < 15 seconds"
	@echo "Excellent: < 12 seconds"
	@echo "Expert: < 10 seconds"

# Test your reflexes
challenge:
	@echo "Quick Reflex Challenge!"
	@echo "======================"
	@$(PYTHON) -c "import time, random; \
	print('Get ready...'); \
	time.sleep(2); \
	print('3...'); time.sleep(1); \
	print('2...'); time.sleep(1); \
	print('1...'); time.sleep(1); \
	delay = random.uniform(0.5, 2.5); \
	time.sleep(delay); \
	print(''); \
	print('████ PRESS NOW! ████'); \
	start = time.time(); \
	input(); \
	elapsed = (time.time() - start) * 1000; \
	print(f''); \
	print(f'Your reaction time: {elapsed:.0f}ms'); \
	if elapsed < 200: print('🏆 Excellent reflexes!'); \
	elif elapsed < 300: print('👍 Good reaction time!'); \
	elif elapsed < 400: print('👌 Average reaction time'); \
	else: print('🐌 Keep practicing!')" 2>/dev/null || echo "Press Enter when you see PRESS NOW!"

# Setup system and dependencies
setup:
	@echo "Setting up Reaction Time Game..."
	@echo "Installing Python libraries..."
	@pip install gpiozero smbus2
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "⚠ I2C may need manual configuration"
	@echo "Creating default config..."
	@echo '{"sound": true, "difficulty": "Normal", "player_name": "Player1"}' > reaction_config.json
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
	rm -f reaction_config.json
	rm -f reaction_scores.json
	@echo "✓ Cleanup complete"

# Help
help:
	@echo "Reaction Time Challenge Game"
	@echo "============================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run       - Play the game (default)"
	@echo "  make demo      - Run hardware demo"
	@echo "  make test      - Test all components"
	@echo ""
	@echo "Component Testing:"
	@echo "  make test-buttons - Test all buttons"
	@echo "  make test-leds    - Test colored LEDs"
	@echo "  make test-status  - Test status LEDs"
	@echo "  make test-buzzer  - Test buzzer"
	@echo "  make test-lcd     - Test LCD display"
	@echo ""
	@echo "Game Information:"
	@echo "  make scores    - View high scores"
	@echo "  make stats     - View statistics"
	@echo "  make modes     - Show all game modes"
	@echo ""
	@echo "Mode Details:"
	@echo "  make tensec    - 10-second timer tips"
	@echo "  make reaction  - Reaction test demo"
	@echo "  make sequence  - Memory sequence info"
	@echo "  make pattern   - Pattern examples"
	@echo "  make speed     - Speed test tips"
	@echo ""
	@echo "Interactive:"
	@echo "  make challenge - Test your reflexes!"
	@echo ""
	@echo "System Management:"
	@echo "  make setup     - Complete setup"
	@echo "  make install   - Install dependencies"
	@echo "  make clean     - Clean data files"
	@echo "  make help      - Show this help"
	@echo ""
	@echo "Controls:"
	@echo "  Colored buttons: Game input"
	@echo "  START: Begin/Select/Stop"
	@echo "  MODE: Change game mode"
	@echo ""
	@echo "LEDs:"
	@echo "  Colored: Match button colors"
	@echo "  White: System ready"
	@echo "  Orange: Game active"
	@echo "  Purple: New record!"