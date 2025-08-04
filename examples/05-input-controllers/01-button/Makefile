# Makefile for Button-Controlled LED project

.PHONY: all run run-poll clean deps help

# Default target
all: help

# Run the event-driven button program (recommended)
run:
	@echo "Starting Button-Controlled LED (Event-driven)..."
	@echo "Press the button to control the LED"
	@echo "Press Ctrl+C to stop"
	@python3 button-led.py

# Run the polling version
run-poll:
	@echo "Starting Button-Controlled LED (Polling)..."
	@echo "Press the button to control the LED"
	@echo "Press Ctrl+C to stop"
	@python3 button-polling.py

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
	@echo "Button-Controlled LED Project"
	@echo "============================"
	@echo "Available targets:"
	@echo "  make run      - Run event-driven version (recommended)"
	@echo "  make run-poll - Run polling version"
	@echo "  make deps     - Install required dependencies"
	@echo "  make clean    - Clean build files (none for Python)"
	@echo "  make help     - Show this help message"