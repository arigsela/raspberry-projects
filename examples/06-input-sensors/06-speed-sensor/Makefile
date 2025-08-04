# Makefile for Speed Sensor

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := speed-sensor.py

# Phony targets
.PHONY: run test demo tach alarm log control calibrate analyze install clean help

# Run the main program
run:
	@echo "Starting Speed Sensor..."
	@$(PYTHON) $(PROGRAM)

# Test basic speed measurement
test:
	@echo "Testing basic speed measurement..."
	@$(PYTHON) -c "from speed_sensor import basic_speed_measurement; basic_speed_measurement()"

# Run demo sequence
demo:
	@echo "Running speed sensor demos..."
	@echo "1. Basic measurement (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from speed_sensor import basic_speed_measurement; basic_speed_measurement()" || true
	@echo "2. Visual tachometer (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from speed_sensor import visual_tachometer; visual_tachometer()" || true

# Visual tachometer
tach:
	@echo "Running visual tachometer..."
	@$(PYTHON) -c "from speed_sensor import visual_tachometer; visual_tachometer()"

# Speed alarm system
alarm:
	@echo "Running speed alarm system..."
	@$(PYTHON) -c "from speed_sensor import speed_alarm; speed_alarm()"

# Data logger
log:
	@echo "Starting RPM data logger..."
	@$(PYTHON) -c "from speed_sensor import rpm_data_logger; rpm_data_logger()"

# Speed control simulation
control:
	@echo "Running speed control simulation..."
	@$(PYTHON) -c "from speed_sensor import speed_control_simulation; speed_control_simulation()"

# Calibrate pulses per revolution
calibrate:
	@echo "Starting calibration..."
	@$(PYTHON) -c "from speed_sensor import multi_pulse_calibration; multi_pulse_calibration()"

# Frequency analysis
analyze:
	@echo "Running frequency analysis..."
	@$(PYTHON) -c "from speed_sensor import frequency_analysis; frequency_analysis()"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install gpiozero

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "speed_log_*.csv" -delete

# Help
help:
	@echo "Speed Sensor - Rotation Speed Measurement"
	@echo "========================================"
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive menu (default)"
	@echo "  make test       - Test basic speed measurement"
	@echo "  make demo       - Run demo sequence"
	@echo "  make tach       - Run visual tachometer"
	@echo "  make alarm      - Run speed alarm system"
	@echo "  make log        - Start data logger"
	@echo "  make control    - Run speed control simulation"
	@echo "  make calibrate  - Calibrate pulses per revolution"
	@echo "  make analyze    - Run frequency analysis"
	@echo "  make install    - Install required dependencies"
	@echo "  make clean      - Clean up cache and log files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make             # Run main program"
	@echo "  make tach        # Visual speed display"
	@echo "  make alarm       # Speed monitoring with alarms"
	@echo "  make log         # Log speed data to CSV file"