# Makefile for Active Buzzer project

.PHONY: all run test morse timer deps clean help

# Default target
all: help

# Run the active buzzer examples
run:
	@echo "Starting Active Buzzer Examples..."
	@echo "Buzzer connected to GPIO17 (Pin 11)"
	@echo "Optional button on GPIO18 (Pin 12)"
	@echo "Select example from menu"
	@echo "Press Ctrl+C to stop"
	@python3 active-buzzer.py

# Quick Morse code demo
morse:
	@echo "Morse Code Quick Demo - Sending SOS..."
	@python3 -c "from gpiozero import Buzzer; \
	import time; \
	buzzer = Buzzer(17); \
	dot = 0.1; dash = 0.3; \
	print('S'); \
	for _ in range(3): buzzer.on(); time.sleep(dot); buzzer.off(); time.sleep(dot); \
	time.sleep(0.2); \
	print('O'); \
	for _ in range(3): buzzer.on(); time.sleep(dash); buzzer.off(); time.sleep(dot); \
	time.sleep(0.2); \
	print('S'); \
	for _ in range(3): buzzer.on(); time.sleep(dot); buzzer.off(); time.sleep(dot); \
	buzzer.close(); \
	print('SOS sent!')"

# Quick timer demo (10 seconds)
timer:
	@echo "10 Second Timer Demo..."
	@python3 -c "from gpiozero import Buzzer; \
	import time; \
	buzzer = Buzzer(17); \
	print('Timer started - 10 seconds'); \
	time.sleep(9); \
	print('Get ready...'); \
	for i in range(5, 0, -1): \
	    print(f'{i}...'); \
	    buzzer.on(); time.sleep(0.05); buzzer.off(); \
	    time.sleep(0.95); \
	print('TIME UP!'); \
	for _ in range(5): \
	    buzzer.on(); time.sleep(0.3); buzzer.off(); time.sleep(0.1); \
	buzzer.close()"

# Test buzzer connection
test:
	@echo "Testing active buzzer..."
	@python3 -c "from gpiozero import Buzzer; \
	import time; \
	buzzer = Buzzer(17); \
	print('If you hear a beep, the buzzer is working!'); \
	buzzer.on(); \
	time.sleep(0.5); \
	buzzer.off(); \
	print('Test complete!'); \
	buzzer.close()"

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
	@echo "Active Buzzer Sound Project"
	@echo "==========================="
	@echo "Available targets:"
	@echo "  make run   - Run interactive buzzer examples"
	@echo "  make morse - Quick Morse code demo (SOS)"
	@echo "  make timer - Quick 10-second timer demo"
	@echo "  make test  - Test buzzer connection"
	@echo "  make deps  - Install dependencies"
	@echo "  make clean - Clean build files"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "Active Buzzer Wiring:"
	@echo "  Buzzer (+) -> GPIO17 (Pin 11)"
	@echo "  Buzzer (-) -> GND (Pin 6)"
	@echo ""
	@echo "Optional Button Wiring:"
	@echo "  Button -> GPIO18 (Pin 12)"
	@echo "  Button -> GND"
	@echo ""
	@echo "Note: Active buzzers make sound when voltage is applied"
	@echo "      They have a built-in oscillator circuit"