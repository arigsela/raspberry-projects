# Makefile for Rotary Encoder Controller

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := rotary-encoder.py

# Phony targets
.PHONY: run test demo position brightness menu volume speed install clean help

# Run the main program
run:
	@echo "Starting Rotary Encoder Controller..."
	@$(PYTHON) $(PROGRAM)

# Test encoder functionality
test:
	@echo "Testing encoder position tracking..."
	@$(PYTHON) -c "from rotary_encoder import basic_position_tracking; basic_position_tracking()"

# Run all demos
demo:
	@echo "Running encoder demos..."
	@echo "1. Position tracking (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from rotary_encoder import basic_position_tracking; basic_position_tracking()" || true
	@echo "2. LED direction indicator (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from rotary_encoder import led_direction_indicator; led_direction_indicator()" || true
	@echo "3. Brightness control (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from rotary_encoder import brightness_control; brightness_control()" || true

# Position tracking demo
position:
	@echo "Running position tracking demo..."
	@$(PYTHON) -c "from rotary_encoder import basic_position_tracking; basic_position_tracking()"

# Brightness control demo
brightness:
	@echo "Running brightness control demo..."
	@$(PYTHON) -c "from rotary_encoder import brightness_control; brightness_control()"

# Menu navigation demo
menu:
	@echo "Running menu navigation demo..."
	@$(PYTHON) -c "from rotary_encoder import menu_navigation; menu_navigation()"

# Volume control demo
volume:
	@echo "Running volume control demo..."
	@$(PYTHON) -c "from rotary_encoder import volume_control; volume_control()"

# Speed monitor demo
speed:
	@echo "Running speed monitor demo..."
	@$(PYTHON) -c "from rotary_encoder import speed_monitor; speed_monitor()"

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
	@echo "Rotary Encoder Controller"
	@echo "========================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive menu (default)"
	@echo "  make test       - Test encoder functionality"
	@echo "  make demo       - Run all demos in sequence"
	@echo "  make position   - Run position tracking demo"
	@echo "  make brightness - Run brightness control demo"
	@echo "  make menu       - Run menu navigation demo"
	@echo "  make volume     - Run volume control demo"
	@echo "  make speed      - Run speed monitor demo"
	@echo "  make install    - Install required dependencies"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make             # Run main program"
	@echo "  make position    # Test position tracking"
	@echo "  make brightness  # Control LED brightness"