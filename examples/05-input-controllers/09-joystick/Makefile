# Makefile for 2-Axis Analog Joystick

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := joystick.py

# Phony targets
.PHONY: run test demo position servo game cursor calibrate install clean help

# Run the main program
run:
	@echo "Starting Joystick Controller..."
	@$(PYTHON) $(PROGRAM)

# Test joystick functionality
test:
	@echo "Testing joystick position reading..."
	@$(PYTHON) -c "from joystick import basic_position_reading; basic_position_reading()"

# Run demo sequence
demo:
	@echo "Running joystick demos..."
	@echo "1. Position reading (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from joystick import basic_position_reading; basic_position_reading()" || true
	@echo "2. Direction LEDs (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from joystick import direction_leds; direction_leds()" || true

# Position reading demo
position:
	@echo "Running position reading demo..."
	@$(PYTHON) -c "from joystick import basic_position_reading; basic_position_reading()"

# Servo control demo
servo:
	@echo "Running servo control demo..."
	@$(PYTHON) -c "from joystick import servo_control; servo_control()"

# Reaction game
game:
	@echo "Starting reaction game..."
	@$(PYTHON) -c "from joystick import joystick_game; joystick_game()"

# Cursor control demo
cursor:
	@echo "Running cursor control demo..."
	@$(PYTHON) -c "from joystick import cursor_control; cursor_control()"

# Calibrate joystick
calibrate:
	@echo "Starting joystick calibration..."
	@$(PYTHON) -c "from joystick import joystick_calibration; joystick_calibration()"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install gpiozero

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Help
help:
	@echo "2-Axis Analog Joystick Controller"
	@echo "================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive menu (default)"
	@echo "  make test       - Test joystick functionality"
	@echo "  make demo       - Run demo sequence"
	@echo "  make position   - Run position reading demo"
	@echo "  make servo      - Run servo control demo"
	@echo "  make game       - Play reaction game"
	@echo "  make cursor     - Run cursor control demo"
	@echo "  make calibrate  - Calibrate joystick"
	@echo "  make install    - Install required dependencies"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make             # Run main program"
	@echo "  make position    # Test position reading"
	@echo "  make servo       # Control servos with joystick"
	@echo "  make game        # Play reaction game"