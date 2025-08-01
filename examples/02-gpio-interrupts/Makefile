# Makefile for GPIO Interrupts Example
# For Python event-driven GPIO programming

# Python interpreter
PYTHON = python3

# Main script
SCRIPT = gpio-interrupts.py

# Default target
all: check

# Check if script is executable
check:
	@chmod +x $(SCRIPT)
	@echo "Script is ready to run"

# Run the program
run: check
	sudo $(PYTHON) $(SCRIPT)

# Clean Python cache
clean:
	rm -rf __pycache__
	rm -f *.pyc

# Install dependencies
deps:
	@echo "Installing Python GPIO dependencies..."
	sudo apt update
	sudo apt install -y python3-pip python3-gpiod
	pip3 install gpiod

# Check code with pylint (optional)
lint:
	@which pylint > /dev/null || echo "Install pylint for code analysis: pip3 install pylint"
	@which pylint > /dev/null && pylint $(SCRIPT) || true

# Help
help:
	@echo "Available targets:"
	@echo "  make         - Check script is ready"
	@echo "  make run     - Run with sudo"
	@echo "  make clean   - Remove Python cache"
	@echo "  make deps    - Install dependencies"
	@echo "  make lint    - Run code analysis"
	@echo "  make help    - Show this help message"

.PHONY: all check run clean deps lint help