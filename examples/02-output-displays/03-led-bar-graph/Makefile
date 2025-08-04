# Makefile for LED Bar Graph project

.PHONY: all run test deps clean help

# Default target
all: help

# Run the LED bar graph examples
run:
	@echo "Starting LED Bar Graph Display..."
	@echo "Using GPIO pins: 17,18,27,22,23,24,25,8,7,12"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 led-bar-graph.py

# Test LED connections
test:
	@echo "Testing LED bar graph connections..."
	@python3 -c "from gpiozero import LEDBarGraph; \
	import time; \
	pins = [17,18,27,22,23,24,25,8,7,12]; \
	print('Creating bar graph on pins:', pins); \
	graph = LEDBarGraph(*pins); \
	print('Testing each LED...'); \
	for i in range(10): \
	    graph.leds[i].on(); \
	    print(f'LED {i+1} ON'); \
	    time.sleep(0.2); \
	    graph.leds[i].off(); \
	print('Testing full bar...'); \
	graph.value = 1; \
	time.sleep(1); \
	graph.off(); \
	print('Test complete!'); \
	graph.close()"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	@echo "For potentiometer control (optional):"
	pip3 install adafruit-circuitpython-mcp3xxx
	@echo "Dependencies installed"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "LED Bar Graph Display Project"
	@echo "============================="
	@echo "Available targets:"
	@echo "  make run   - Run the LED bar graph examples"
	@echo "  make test  - Test LED connections"
	@echo "  make deps  - Install dependencies"
	@echo "  make clean - Clean build files"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "LED Bar Graph Wiring:"
	@echo "  LED 1  -> GPIO17 (Pin 11) with 220Ω resistor"
	@echo "  LED 2  -> GPIO18 (Pin 12) with 220Ω resistor"
	@echo "  LED 3  -> GPIO27 (Pin 13) with 220Ω resistor"
	@echo "  LED 4  -> GPIO22 (Pin 15) with 220Ω resistor"
	@echo "  LED 5  -> GPIO23 (Pin 16) with 220Ω resistor"
	@echo "  LED 6  -> GPIO24 (Pin 18) with 220Ω resistor"
	@echo "  LED 7  -> GPIO25 (Pin 22) with 220Ω resistor"
	@echo "  LED 8  -> GPIO8  (Pin 24) with 220Ω resistor"
	@echo "  LED 9  -> GPIO7  (Pin 26) with 220Ω resistor"
	@echo "  LED 10 -> GPIO12 (Pin 32) with 220Ω resistor"
	@echo "  Common -> GND (if common cathode)"