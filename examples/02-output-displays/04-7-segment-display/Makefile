# Makefile for 7-Segment Display project

.PHONY: all run test count dice timer deps clean help

# Default target
all: help

# Run the 7-segment display examples
run:
	@echo "Starting 7-Segment Display Examples..."
	@echo "GPIO connections:"
	@echo "  a=GPIO17, b=GPIO18, c=GPIO27, d=GPIO22"
	@echo "  e=GPIO23, f=GPIO24, g=GPIO25, dp=GPIO4"
	@echo "Select example from menu"
	@echo "Press Ctrl+C to stop"
	@python3 seven-segment.py

# Test all segments
test:
	@echo "Testing 7-segment display..."
	@python3 -c "from gpiozero import LED; \
	import time; \
	pins = {'a':17,'b':18,'c':27,'d':22,'e':23,'f':24,'g':25,'dp':4}; \
	print('Testing each segment...'); \
	for name, pin in pins.items(): \
	    led = LED(pin); \
	    print(f'Segment {name} ON'); \
	    led.on(); \
	    time.sleep(0.5); \
	    led.off(); \
	    led.close(); \
	print('All segments tested!')"

# Simple counter demo
count:
	@echo "Counter Demo (0-9)..."
	@python3 -c "from gpiozero import LED; \
	import time; \
	segs = {'a':LED(17),'b':LED(18),'c':LED(27),'d':LED(22),'e':LED(23),'f':LED(24),'g':LED(25)}; \
	digits = { \
	    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', \
	    '4': 'bcfg', '5': 'acdfg', '6': 'acdefg', '7': 'abc', \
	    '8': 'abcdefg', '9': 'abcdfg' \
	}; \
	try: \
	    for i in range(10): \
	        for s in segs.values(): s.off(); \
	        for seg in digits[str(i)]: segs[seg].on(); \
	        print(f'\\rDisplaying: {i}', end=''); \
	        time.sleep(0.5); \
	except KeyboardInterrupt: pass; \
	finally: \
	    for s in segs.values(): s.close(); \
	    print('\\nCounter stopped')"

# Dice simulator
dice:
	@echo "Dice Roll Simulator..."
	@echo "Press Enter to roll, Ctrl+C to exit"
	@python3 -c "from gpiozero import LED; \
	import time, random; \
	segs = {'a':LED(17),'b':LED(18),'c':LED(27),'d':LED(22),'e':LED(23),'f':LED(24),'g':LED(25)}; \
	digits = { \
	    '1': 'bc', '2': 'abdeg', '3': 'abcdg', \
	    '4': 'bcfg', '5': 'acdfg', '6': 'acdefg' \
	}; \
	try: \
	    while True: \
	        input('Press Enter to roll...'); \
	        for _ in range(10): \
	            n = str(random.randint(1,6)); \
	            for s in segs.values(): s.off(); \
	            for seg in digits[n]: segs[seg].on(); \
	            time.sleep(0.1); \
	        result = random.randint(1,6); \
	        for s in segs.values(): s.off(); \
	        for seg in digits[str(result)]: segs[seg].on(); \
	        print(f'You rolled: {result}!'); \
	except KeyboardInterrupt: pass; \
	finally: \
	    for s in segs.values(): s.close(); \
	    print('\\nDice simulator stopped')"

# Simple timer (counts down from 9)
timer:
	@echo "Countdown Timer (9 to 0)..."
	@python3 -c "from gpiozero import LED, Buzzer; \
	import time; \
	segs = {'a':LED(17),'b':LED(18),'c':LED(27),'d':LED(22),'e':LED(23),'f':LED(24),'g':LED(25)}; \
	digits = { \
	    '0': 'abcdef', '1': 'bc', '2': 'abdeg', '3': 'abcdg', \
	    '4': 'bcfg', '5': 'acdfg', '6': 'acdefg', '7': 'abc', \
	    '8': 'abcdefg', '9': 'abcdfg' \
	}; \
	try: \
	    for i in range(9, -1, -1): \
	        for s in segs.values(): s.off(); \
	        for seg in digits[str(i)]: segs[seg].on(); \
	        print(f'\\rCountdown: {i}', end=''); \
	        time.sleep(1); \
	    print('\\nTime\\'s up!'); \
	    for _ in range(5): \
	        for s in segs.values(): s.toggle(); \
	        time.sleep(0.2); \
	except KeyboardInterrupt: pass; \
	finally: \
	    for s in segs.values(): s.close(); \
	    print('\\nTimer stopped')"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	@echo "Dependencies installed"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "7-Segment Display Project"
	@echo "========================"
	@echo "Available targets:"
	@echo "  make run   - Run interactive examples"
	@echo "  make test  - Test each segment"
	@echo "  make count - Simple counter (0-9)"
	@echo "  make dice  - Dice roll simulator"
	@echo "  make timer - Countdown timer"
	@echo "  make deps  - Install dependencies"
	@echo "  make clean - Clean build files"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "7-Segment Display Pinout:"
	@echo "     aaaa"
	@echo "    f    b"
	@echo "     gggg"
	@echo "    e    c"
	@echo "     dddd  dp"
	@echo ""
	@echo "GPIO Connections:"
	@echo "  a -> GPIO17 (Pin 11) with 220Ω resistor"
	@echo "  b -> GPIO18 (Pin 12) with 220Ω resistor"
	@echo "  c -> GPIO27 (Pin 13) with 220Ω resistor"
	@echo "  d -> GPIO22 (Pin 15) with 220Ω resistor"
	@echo "  e -> GPIO23 (Pin 16) with 220Ω resistor"
	@echo "  f -> GPIO24 (Pin 18) with 220Ω resistor"
	@echo "  g -> GPIO25 (Pin 22) with 220Ω resistor"
	@echo "  dp-> GPIO4  (Pin 7)  with 220Ω resistor"
	@echo "  Common -> GND (common cathode) or 3.3V (common anode)"