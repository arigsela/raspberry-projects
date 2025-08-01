# Makefile for Hello World GPIO Example
# For Python scripts on Raspberry Pi 5

# Python interpreter
PYTHON = python3

# Main script
SCRIPT = hello-world.py

# Default target
all: check

# Check if script is executable
check:
	@chmod +x $(SCRIPT)
	@echo "Script is ready to run"

# Run the program (requires sudo for GPIO access)
run: check
	sudo $(PYTHON) $(SCRIPT)

# Clean any Python cache
clean:
	rm -rf __pycache__
	rm -f *.pyc

# Install dependencies
deps:
	@echo "Installing Python GPIO dependencies..."
	sudo apt update
	sudo apt install -y python3-pip python3-gpiod
	pip3 install gpiod

# Help target - shows available commands
help:
	@echo "Available targets:"
	@echo "  make        - Check script is ready"
	@echo "  make run    - Run with sudo"
	@echo "  make clean  - Remove Python cache files"
	@echo "  make deps   - Install required packages"
	@echo "  make help   - Show this help message"

.PHONY: all check run clean deps help