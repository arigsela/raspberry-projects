# Makefile for PWM LED Control Example
# For Python PWM implementation on Raspberry Pi 5

# Python interpreter
PYTHON = python3

# Main scripts
MAIN_SCRIPT = pwm-control.py
SIMPLE_SCRIPT = simple-pwm.py

# Default target
all: check

# Check scripts are executable
check:
	@chmod +x $(MAIN_SCRIPT) $(SIMPLE_SCRIPT)
	@echo "Scripts are ready to run"

# Run the main program
run: check
	sudo $(PYTHON) $(MAIN_SCRIPT)

# Run simple version
run-simple: check
	sudo $(PYTHON) $(SIMPLE_SCRIPT)

# Clean Python cache
clean:
	rm -rf __pycache__
	rm -f *.pyc

# Install dependencies
deps:
	@echo "Installing Python dependencies..."
	sudo apt update
	sudo apt install -y python3-pip python3-gpiod
	pip3 install gpiod

# Check code quality
lint:
	@which pylint > /dev/null || echo "Install pylint: pip3 install pylint"
	@which pylint > /dev/null && pylint $(MAIN_SCRIPT) $(SIMPLE_SCRIPT) || true

# Help target
help:
	@echo "PWM LED Control Makefile"
	@echo "======================="
	@echo "Available targets:"
	@echo "  make         - Check scripts are ready"
	@echo "  make run     - Run main PWM program"
	@echo "  make run-simple - Run simple PWM demo"
	@echo "  make clean   - Remove Python cache"
	@echo "  make deps    - Install dependencies"
	@echo "  make lint    - Check code quality"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - python3-gpiod"
	@echo "  - Python 3.7+"

.PHONY: all check run run-simple clean deps lint help