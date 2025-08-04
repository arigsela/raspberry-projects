# Makefile for Matrix Keypad project

.PHONY: all run lock test clean deps help

# Default target
all: help

# Run the keypad scanner demo
run:
	@echo "Starting Keypad Scanner..."
	@echo "Select demo from menu using keypad"
	@echo "Press Ctrl+C to stop"
	@python3 keypad-scanner.py

# Run the security lock system
lock:
	@echo "Starting Keypad Lock System..."
	@echo "Default codes: 1234, 5678, 0000"
	@echo "Master code: 999999"
	@echo "Press Ctrl+C to stop"
	@python3 keypad-lock.py

# Test keypad connections
test:
	@echo "Testing keypad connections..."
	@echo "Press each key to verify mapping"
	@python3 -c "from keypad_scanner import Keypad, ROW_PINS, COL_PINS, KEYS; \
	import time; \
	keypad = Keypad(ROW_PINS, COL_PINS, KEYS); \
	print('Press keys to test (Ctrl+C to stop)'); \
	try: \
	    while True: \
	        key = keypad.get_key(); \
	        if key: print(f'Key: {key}'); \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    keypad.cleanup()"

# Clean log and config files
clean:
	@echo "Cleaning log and config files..."
	@rm -f access_log.txt access_codes.json
	@echo "Files removed"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	@echo "Dependencies installed"

# Help target
help:
	@echo "Matrix Keypad Project"
	@echo "===================="
	@echo "Available targets:"
	@echo "  make run   - Run keypad scanner with demos"
	@echo "  make lock  - Run security lock system"
	@echo "  make test  - Test keypad connections"
	@echo "  make clean - Remove log and config files"
	@echo "  make deps  - Install dependencies"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "Keypad Layout:"
	@echo "  ┌───┬───┬───┬───┐"
	@echo "  │ 1 │ 2 │ 3 │ A │"
	@echo "  ├───┼───┼───┼───┤"
	@echo "  │ 4 │ 5 │ 6 │ B │"
	@echo "  ├───┼───┼───┼───┤"
	@echo "  │ 7 │ 8 │ 9 │ C │"
	@echo "  ├───┼───┼───┼───┤"
	@echo "  │ * │ 0 │ # │ D │"
	@echo "  └───┴───┴───┴───┘"