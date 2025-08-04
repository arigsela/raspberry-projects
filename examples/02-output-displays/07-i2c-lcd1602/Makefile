# Makefile for I2C LCD1602 Display project

.PHONY: all run clock test scan deps help

# Default target
all: help

# Run the LCD display demo
run:
	@echo "Starting LCD1602 Display Demo..."
	@echo "Make sure I2C is enabled and LCD is connected"
	@echo "Press Ctrl+C to stop"
	@python3 lcd-display.py

# Run the clock application
clock:
	@echo "Starting LCD Clock Application..."
	@echo "Features: Clock, Timer, Stopwatch"
	@python3 lcd-clock.py

# Test I2C connection
test:
	@echo "Testing I2C LCD connection..."
	@python3 -c "import sys, os; \
	sys.path.insert(0, '../../'); \
	from _shared.lcd1602 import LCD1602; \
	lcd = LCD1602(); \
	lcd.clear(); \
	lcd.write_line('LCD Test OK!', 0); \
	lcd.write_line('Address: 0x27', 1); \
	import time; time.sleep(3); \
	lcd.cleanup(); \
	print('Test successful!')"

# Scan I2C bus
scan:
	@echo "Scanning I2C bus for devices..."
	@echo "Look for your LCD address (usually 27 or 3F)"
	@sudo i2cdetect -y 1

# Install dependencies
deps:
	@echo "Installing dependencies..."
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0
	@echo "Installing packages..."
	@sudo apt update
	@sudo apt install -y i2c-tools python3-smbus2
	@pip3 install smbus2
	@echo "Dependencies installed!"
	@echo "You may need to reboot for I2C to work"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "I2C LCD1602 Display Project"
	@echo "=========================="
	@echo "Available targets:"
	@echo "  make run   - Run LCD display demo"
	@echo "  make clock - Run clock application"
	@echo "  make test  - Test LCD connection"
	@echo "  make scan  - Scan I2C bus for devices"
	@echo "  make deps  - Install dependencies and enable I2C"
	@echo "  make clean - Clean build files"
	@echo "  make help  - Show this help message"
	@echo ""
	@echo "LCD Wiring:"
	@echo "  VCC -> 5V (Pin 2)"
	@echo "  GND -> GND (Pin 6)"
	@echo "  SDA -> GPIO2/SDA1 (Pin 3)"
	@echo "  SCL -> GPIO3/SCL1 (Pin 5)"