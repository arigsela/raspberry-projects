# Makefile for PIR Motion Sensor project

.PHONY: all run security clean deps help test log-view

# Default target
all: help

# Run basic motion detector
run:
	@echo "Starting PIR Motion Detector..."
	@echo "LED Colors: Blue=Idle, Yellow=Motion, Red=Continuous"
	@echo "Press Ctrl+C to stop"
	@python3 pir-motion-detector.py

# Run security system
security:
	@echo "Starting PIR Security System..."
	@echo "Press button to arm/disarm"
	@echo "Check security_log.txt for events"
	@echo "Press Ctrl+C to stop"
	@python3 pir-security-system.py

# Test PIR sensor
test:
	@echo "Testing PIR sensor..."
	@echo "Move in front of sensor to test"
	@python3 -c "from gpiozero import MotionSensor; \
	import time; \
	pir = MotionSensor(17); \
	print('PIR Test - Move to trigger'); \
	for i in range(30): \
	    if pir.motion_detected: \
	        print('MOTION DETECTED!'); \
	    else: \
	        print('No motion...'); \
	    time.sleep(1)"

# View security log
log-view:
	@if [ -f security_log.txt ]; then \
		echo "=== Recent Security Events ==="; \
		tail -20 security_log.txt; \
	else \
		echo "No security log found. Run 'make security' first."; \
	fi

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero

# Clean log files
clean:
	@echo "Cleaning log files..."
	@rm -f security_log.txt
	@echo "Log files removed"

# Help target
help:
	@echo "PIR Motion Sensor Project"
	@echo "========================"
	@echo "Available targets:"
	@echo "  make run      - Run basic motion detector with LED"
	@echo "  make security - Run full security system"
	@echo "  make test     - Test PIR sensor functionality"
	@echo "  make log-view - View recent security events"
	@echo "  make deps     - Install required dependencies"
	@echo "  make clean    - Remove log files"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "PIR Sensor Wiring:"
	@echo "  VCC -> 5V (Pin 2)"
	@echo "  OUT -> GPIO17 (Pin 11)"
	@echo "  GND -> GND (Pin 6)"