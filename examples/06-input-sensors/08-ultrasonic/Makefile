# Makefile for HC-SR04 Ultrasonic Sensor project

.PHONY: all run radar test deps clean help

# Default target
all: help

# Run the distance measurement demos
run:
	@echo "Starting Ultrasonic Distance Sensor..."
	@echo "Trigger: GPIO23, Echo: GPIO24"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 ultrasonic-distance.py

# Run the radar system (requires servo)
radar:
	@echo "Starting Ultrasonic Radar System..."
	@echo "Ultrasonic: Trigger=GPIO23, Echo=GPIO24"
	@echo "Servo: GPIO18"
	@echo "Press Ctrl+C to stop"
	@python3 ultrasonic-radar.py

# Test sensor connection
test:
	@echo "Testing ultrasonic sensor..."
	@python3 -c "from gpiozero import DistanceSensor; \
	import time; \
	sensor = DistanceSensor(echo=24, trigger=23); \
	print('Reading distance...'); \
	for i in range(5): \
	    d = sensor.distance * 100; \
	    print(f'Distance: {d:.1f} cm'); \
	    time.sleep(1); \
	print('Test complete!')"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	pip3 install numpy matplotlib
	@echo "Dependencies installed"

# Clean (nothing to clean)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "HC-SR04 Ultrasonic Sensor Project"
	@echo "================================="
	@echo "Available targets:"
	@echo "  make run   - Run distance measurement demos"
	@echo "  make radar - Run radar system (needs servo)"
	@echo "  make test  - Test sensor connection"
	@echo "  make deps  - Install dependencies"
	@echo "  make clean - Clean build files"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "HC-SR04 Wiring:"
	@echo "  VCC     -> 5V (Pin 2)"
	@echo "  Trigger -> GPIO23 (Pin 16)"
	@echo "  Echo    -> GPIO24 (Pin 18) *"
	@echo "  GND     -> GND (Pin 6)"
	@echo ""
	@echo "* Echo pin outputs 5V - use voltage divider:"
	@echo "  Echo --[1kΩ]--●--[2kΩ]-- GND"
	@echo "                 │"
	@echo "              GPIO24"