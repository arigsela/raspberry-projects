# Makefile for Servo Motor Control project

.PHONY: all run interactive clean deps help test-range

# Default target
all: help

# Run the automatic servo demo
run:
	@echo "Starting Servo Motor Demo..."
	@echo "The servo will move through various positions"
	@echo "Press Ctrl+C to stop"
	@python3 servo-control.py

# Run interactive servo control
interactive:
	@echo "Starting Interactive Servo Control..."
	@echo "Use keyboard commands to control the servo"
	@echo "Type 'q' to quit"
	@python3 servo-interactive.py

# Test servo range (calibration)
test-range:
	@echo "Testing servo range..."
	@echo "This will help you find the correct pulse widths"
	@python3 -c "from gpiozero import Servo; import time; \
	s = Servo(18); \
	print('Testing min position...'); s.min(); time.sleep(2); \
	print('Testing mid position...'); s.mid(); time.sleep(2); \
	print('Testing max position...'); s.max(); time.sleep(2); \
	s.detach(); print('Test complete')"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "Servo Motor Control Project"
	@echo "=========================="
	@echo "Available targets:"
	@echo "  make run         - Run automatic servo demo"
	@echo "  make interactive - Run interactive control"
	@echo "  make test-range  - Test servo min/max positions"
	@echo "  make deps        - Install required dependencies"
	@echo "  make clean       - Clean build files (none for Python)"
	@echo "  make help        - Show this help message"
	@echo ""
	@echo "Servo Wiring:"
	@echo "  Orange/Yellow wire -> GPIO18 (Pin 12)"
	@echo "  Red wire         -> 5V (Pin 2)"
	@echo "  Brown/Black wire -> GND (Pin 6)"