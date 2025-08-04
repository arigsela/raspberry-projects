# Makefile for Blinking LED project

.PHONY: all run clean deps help

# Default target
all: help

# Run the blinking LED program
run:
	@echo "Starting Blinking LED program..."
	@echo "Press Ctrl+C to stop"
	@python3 blinking-led.py

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
	@echo "Blinking LED Project"
	@echo "==================="
	@echo "Available targets:"
	@echo "  make run   - Run the blinking LED program"
	@echo "  make deps  - Install required dependencies"
	@echo "  make clean - Clean build files (none for Python)"
	@echo "  make help  - Show this help message"