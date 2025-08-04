# Makefile for RGB LED project

.PHONY: all run interactive clean deps help

# Default target
all: help

# Run the automatic RGB LED demo
run:
	@echo "Starting RGB LED Color Demo..."
	@echo "Watch the LED cycle through colors"
	@echo "Press Ctrl+C to stop"
	@python3 rgb-led.py

# Run the interactive version
interactive:
	@echo "Starting Interactive RGB LED Control..."
	@echo "Use menu commands to control the LED"
	@echo "Press 'q' to quit"
	@python3 rgb-led-interactive.py

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
	@echo "RGB LED Color Control Project"
	@echo "============================"
	@echo "Available targets:"
	@echo "  make run         - Run automatic color demo"
	@echo "  make interactive - Run interactive control"
	@echo "  make deps        - Install required dependencies"
	@echo "  make clean       - Clean build files (none for Python)"
	@echo "  make help        - Show this help message"