# Makefile for MPU6050 6-Axis Sensor

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := mpu6050.py

# Phony targets
.PHONY: run test demo motion tilt orient log calibrate gesture install setup clean help

# Run the main program
run:
	@echo "Starting MPU6050 sensor..."
	@$(PYTHON) $(PROGRAM)

# Test basic sensor reading
test:
	@echo "Testing basic sensor reading..."
	@$(PYTHON) -c "from mpu6050 import basic_sensor_reading; basic_sensor_reading()"

# Run demo sequence
demo:
	@echo "Running MPU6050 demos..."
	@echo "1. Basic reading (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from mpu6050 import basic_sensor_reading; basic_sensor_reading()" || true
	@echo "2. Motion detector (10 seconds)..."
	@timeout 10 $(PYTHON) -c "from mpu6050 import motion_detector; motion_detector()" || true

# Motion detection demo
motion:
	@echo "Running motion detector..."
	@$(PYTHON) -c "from mpu6050 import motion_detector; motion_detector()"

# Tilt indicator demo
tilt:
	@echo "Running tilt indicator..."
	@$(PYTHON) -c "from mpu6050 import tilt_indicator; tilt_indicator()"

# Orientation monitor
orient:
	@echo "Running orientation monitor..."
	@$(PYTHON) -c "from mpu6050 import orientation_monitor; orientation_monitor()"

# Data logger
log:
	@echo "Starting data logger..."
	@$(PYTHON) -c "from mpu6050 import data_logger; data_logger()"

# Calibration wizard
calibrate:
	@echo "Starting calibration wizard..."
	@$(PYTHON) -c "from mpu6050 import calibration_wizard; calibration_wizard()"

# Gesture recognition
gesture:
	@echo "Running gesture recognition..."
	@$(PYTHON) -c "from mpu6050 import gesture_recognition; gesture_recognition()"

# Setup I2C and dependencies
setup:
	@echo "Setting up I2C and dependencies..."
	@echo "Enabling I2C interface..."
	@sudo raspi-config nonint do_i2c 0 || echo "I2C setup may require manual configuration"
	@echo "Installing Python libraries..."
	@pip install smbus2 gpiozero
	@echo "Testing I2C connection..."
	@sudo i2cdetect -y 1 | grep -q "68" && echo "✓ MPU6050 detected at 0x68" || echo "⚠ MPU6050 not detected - check connections"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install smbus2 gpiozero

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "mpu6050_log_*.csv" -delete

# Help
help:
	@echo "MPU6050 6-Axis Accelerometer and Gyroscope"
	@echo "=========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive menu (default)"
	@echo "  make test       - Test basic sensor reading"
	@echo "  make demo       - Run demo sequence"
	@echo "  make motion     - Run motion detector"
	@echo "  make tilt       - Run tilt indicator"
	@echo "  make orient     - Run orientation monitor"
	@echo "  make log        - Start data logger"
	@echo "  make calibrate  - Run calibration wizard"
	@echo "  make gesture    - Run gesture recognition"
	@echo "  make setup      - Setup I2C and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make clean      - Clean up cache and log files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - I2C must be enabled: sudo raspi-config → Interface → I2C"
	@echo "  - Connect MPU6050: VCC→3.3V, GND→GND, SDA→GPIO3, SCL→GPIO5"
	@echo "  - Test connection: sudo i2cdetect -y 1"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time setup"
	@echo "  make test        # Test sensor connection"
	@echo "  make motion      # Detect motion and taps"
	@echo "  make calibrate   # Calibrate sensor offsets"