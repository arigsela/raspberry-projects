# Makefile for Advanced Camera Control System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := advanced-camera-control.py

# Phony targets
.PHONY: run test demo manual auto patrol record calibrate setup install clean help

# Run the main program
run:
	@echo "Starting Advanced Camera Control System..."
	@$(PYTHON) $(PROGRAM)

# Test hardware components
test:
	@echo "Testing hardware components..."
	@echo "1. Testing ADC connection..."
	@$(PYTHON) -c "import sys, os; sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared')); from adc0834 import ADC0834; adc = ADC0834(17, 18, 27, 22); print('ADC test:', adc.read_channel(0)); adc.cleanup()" || echo "ADC test failed"
	@echo "2. Testing servo connections..."
	@$(PYTHON) -c "from gpiozero import Servo; import time; pan = Servo(20); tilt = Servo(21); print('Moving servos...'); pan.value = 0.5; tilt.value = 0.5; time.sleep(1); pan.value = 0; tilt.value = 0; pan.close(); tilt.close(); print('Servo test complete')" || echo "Servo test failed"
	@echo "3. Testing camera connection..."
	@libcamera-hello --timeout 2000 || echo "Camera test failed - check connections"

# Run demo sequence
demo:
	@echo "Running camera control demos..."
	@echo "Note: Demo requires hardware setup and user interaction"
	@$(PYTHON) -c "from advanced_camera_control import automatic_demo; automatic_demo()"

# Manual control mode
manual:
	@echo "Starting manual control mode..."
	@$(PYTHON) -c "from advanced_camera_control import CameraController; import time; c = CameraController(); print('Manual mode active - use joystick'); time.sleep(30); c.cleanup()"

# Automatic positioning demo
auto:
	@echo "Running automatic positioning demo..."
	@$(PYTHON) -c "from advanced_camera_control import manual_demo_sequence, CameraController; c = CameraController(); manual_demo_sequence(c); c.cleanup()"

# Patrol mode demo
patrol:
	@echo "Starting patrol mode demo..."
	@$(PYTHON) -c "from advanced_camera_control import patrol_demo_sequence, CameraController; c = CameraController(); patrol_demo_sequence(c); c.cleanup()"

# Recording demo
record:
	@echo "Running recording demo..."
	@$(PYTHON) -c "from advanced_camera_control import recording_demo_sequence, CameraController; c = CameraController(); recording_demo_sequence(c); c.cleanup()" || echo "Recording demo requires camera module"

# Joystick calibration
calibrate:
	@echo "Starting joystick calibration..."
	@$(PYTHON) -c "from advanced_camera_control import CameraController; c = CameraController(); c.calibrate_joystick(); c.cleanup()"

# Setup hardware interfaces and dependencies
setup:
	@echo "Setting up camera control system..."
	@echo "Enabling camera interface..."
	@sudo raspi-config nonint do_camera 0 || echo "Camera setup may require manual configuration"
	@echo "Enabling SPI interface..."
	@sudo raspi-config nonint do_spi 0 || echo "SPI setup may require manual configuration"
	@echo "Installing Python libraries..."
	@pip install picamera2 gpiozero spidev
	@echo "Testing hardware interfaces..."
	@ls /dev/spi* 2>/dev/null && echo "✓ SPI devices found" || echo "⚠ No SPI devices found - check SPI enable"
	@libcamera-hello --list-cameras || echo "⚠ No cameras detected - check connections and enable camera"
	@echo "Hardware setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install picamera2 gpiozero spidev

# Status check
status:
	@echo "Camera Control System Status"
	@echo "============================"
	@echo "Camera interface:"
	@libcamera-hello --list-cameras 2>/dev/null | head -5 || echo "  ❌ Camera not detected"
	@echo "SPI interface:"
	@ls /dev/spi* 2>/dev/null && echo "  ✓ SPI enabled" || echo "  ❌ SPI not enabled"
	@echo "GPIO access:"
	@$(PYTHON) -c "from gpiozero import LED; LED(26).close(); print('  ✓ GPIO access working')" 2>/dev/null || echo "  ❌ GPIO access failed"
	@echo "Dependencies:"
	@$(PYTHON) -c "import picamera2; print('  ✓ picamera2 installed')" 2>/dev/null || echo "  ❌ picamera2 not installed"
	@$(PYTHON) -c "import gpiozero; print('  ✓ gpiozero installed')" 2>/dev/null || echo "  ❌ gpiozero not installed"
	@$(PYTHON) -c "import spidev; print('  ✓ spidev installed')" 2>/dev/null || echo "  ❌ spidev not installed"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "camera_presets.json" -delete
	find . -type f -name "*.h264" -delete
	find . -type f -name "*.jpg" -delete

# Help
help:
	@echo "Advanced Camera Control System"
	@echo "==============================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive control system (default)"
	@echo "  make test       - Test all hardware components"
	@echo "  make demo       - Run automatic demonstration"
	@echo "  make manual     - Manual joystick control mode"
	@echo "  make auto       - Automatic positioning demo"
	@echo "  make patrol     - Patrol mode demonstration"
	@echo "  make record     - Recording demonstration"
	@echo "  make calibrate  - Calibrate joystick center position"
	@echo "  make setup      - Setup interfaces and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make status     - Check system status"
	@echo "  make clean      - Clean up cache and recording files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - Raspberry Pi Camera Module connected to camera connector"
	@echo "  - 2x Servo motors (SG90) for pan/tilt mechanism"
	@echo "  - Analog joystick module with ADC0834"
	@echo "  - Control buttons and status LEDs"
	@echo "  - Adequate power supply (3A+ recommended for servos)"
	@echo ""
	@echo "Pin Connections:"
	@echo "  ADC0834:  CS=GPIO17, CLK=GPIO18, DI=GPIO27, DO=GPIO22"
	@echo "  Servos:   Pan=GPIO20, Tilt=GPIO21"
	@echo "  Buttons:  Record=GPIO23, Mode=GPIO24, Preset=GPIO25"
	@echo "  LEDs:     Status=GPIO26, Record=GPIO19"
	@echo "  Buzzer:   GPIO13"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Camera enabled: sudo raspi-config → Interface → Camera"
	@echo "  - SPI enabled: sudo raspi-config → Interface → SPI"
	@echo "  - Adequate power supply for servo motors"
	@echo "  - Fast SD card for video recording (Class 10+)"
	@echo ""
	@echo "Control Modes:"
	@echo "  1. MANUAL - Direct joystick control"
	@echo "  2. PRESET - Save/recall positions"
	@echo "  3. AUTO_TRACK - Simulated tracking"
	@echo "  4. PATROL - Automatic patrol sequence"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time setup"
	@echo "  make test        # Test all hardware"
	@echo "  make calibrate   # Calibrate joystick"
	@echo "  make demo        # Full demonstration"
	@echo "  make manual      # Manual control test"
	@echo ""
	@echo "Recording Notes:"
	@echo "  - H.264 videos saved in current directory"
	@echo "  - Use ffmpeg to convert: ffmpeg -i video.h264 -c copy video.mp4"
	@echo "  - Monitor disk space during long recordings"
	@echo "  - 1080p30 ≈ 400MB per 10 minutes"