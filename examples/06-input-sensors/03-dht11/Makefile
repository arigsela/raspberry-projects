# Makefile for DHT11 Temperature & Humidity Sensor project

.PHONY: all run display test log deps clean help

# Default target
all: help

# Run the DHT11 monitor
run:
	@echo "Starting DHT11 Environmental Monitor..."
	@echo "Sensor on GPIO17"
	@echo "Press Ctrl+C to stop"
	@python3 dht11-monitor.py

# Run with LCD display
display:
	@echo "Starting DHT11 + LCD Display..."
	@echo "DHT11 on GPIO17, LCD on I2C"
	@echo "Press Ctrl+C to stop"
	@python3 dht11-display.py

# Test sensor connection
test:
	@echo "Testing DHT11 sensor..."
	@python3 -c "import sys; sys.path.insert(0, '../../'); \
	from _shared.dht11 import DHT11; \
	sensor = DHT11(17); \
	print('Reading sensor...'); \
	h, t = sensor.read_retry(); \
	if h and t: \
	    print(f'Success! Temp: {t}°C, Humidity: {h}%'); \
	else: \
	    print('Failed to read sensor'); \
	sensor.cleanup()"

# Start data logging
log:
	@echo "Starting DHT11 Data Logger..."
	@echo "Logging to dht11_log.csv"
	@echo "Press Ctrl+C to stop"
	@python3 -c "import dht11_monitor; \
	from _shared.dht11 import DHT11; \
	sensor = DHT11(17); \
	dht11_monitor.data_logger_mode(sensor)"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-rpi.gpio python3-smbus2
	pip3 install pandas matplotlib

# Clean log files
clean:
	@echo "Cleaning log files..."
	@rm -f dht11_log.csv *.log
	@echo "Log files removed"

# Help target
help:
	@echo "DHT11 Temperature & Humidity Sensor Project"
	@echo "=========================================="
	@echo "Available targets:"
	@echo "  make run     - Run environmental monitor"
	@echo "  make display - Run with LCD display"
	@echo "  make test    - Test sensor connection"
	@echo "  make log     - Start data logging mode"
	@echo "  make deps    - Install dependencies"
	@echo "  make clean   - Remove log files"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "DHT11 Wiring:"
	@echo "  VCC  -> 5V (Pin 2)"
	@echo "  DATA -> GPIO17 (Pin 11) with 10kΩ pull-up"
	@echo "  GND  -> GND (Pin 6)"