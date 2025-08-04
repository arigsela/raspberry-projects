# Makefile for Raspberry Pi Camera Module project

.PHONY: all run booth timelapse test deps info clean help

# Default target
all: help

# Run the camera capture demos
run:
	@echo "Starting Camera Photo Capture..."
	@echo "Photos will be saved to ~/Pictures/raspberry-pi-camera"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 camera-capture.py

# Run the photo booth with hardware
booth:
	@echo "Starting Photo Booth..."
	@echo "Button: GPIO18, Flash LED: GPIO17"
	@echo "RGB Status LED: GPIO22,27,23"
	@echo "Photos will be saved to ~/Pictures/photo-booth"
	@echo "Press Ctrl+C to stop"
	@python3 camera-trigger.py

# Quick timelapse mode
timelapse:
	@echo "Starting Quick Timelapse (1 minute, 10s interval)..."
	@python3 -c "from picamera2 import Picamera2; \
	import time, os; \
	from datetime import datetime; \
	picam2 = Picamera2(); \
	picam2.start(); \
	dir = os.path.expanduser('~/Pictures/timelapse_' + datetime.now().strftime('%Y%m%d_%H%M%S')); \
	os.makedirs(dir); \
	for i in range(6): \
	    picam2.capture_file(f'{dir}/frame_{i:04d}.jpg'); \
	    print(f'Frame {i+1}/6 captured'); \
	    time.sleep(10); \
	picam2.stop(); \
	print(f'Timelapse saved to: {dir}')"

# Test camera connection
test:
	@echo "Testing camera module..."
	@python3 -c "from picamera2 import Picamera2; \
	picam2 = Picamera2(); \
	print('Camera detected!'); \
	print(f\"Model: {picam2.camera_properties.get('Model', 'Unknown')}\"); \
	print(f\"Resolution: {picam2.camera_properties.get('PixelArraySize', 'Unknown')}\"); \
	picam2.close()"
	@echo "Camera test complete!"

# Show camera information
info:
	@echo "Camera Information:"
	@libcamera-hello --list-cameras || echo "libcamera-hello not found"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	@echo "Checking/enabling camera..."
	@sudo raspi-config nonint do_camera 0 || echo "Camera already enabled"
	@echo "Installing packages..."
	@sudo apt update
	@sudo apt install -y python3-picamera2 python3-libcamera
	@sudo apt install -y python3-opencv python3-pil
	@pip3 install numpy pillow
	@echo "For video creation from timelapse:"
	@sudo apt install -y ffmpeg
	@echo "Dependencies installed"

# Clean up test photos
clean:
	@echo "Cleaning test photos..."
	@rm -f test_*.jpg effect_*.jpg res_*.jpg
	@echo "Test photos removed (keeping saved photos in ~/Pictures)"

# Help target
help:
	@echo "Raspberry Pi Camera Module Project"
	@echo "=================================="
	@echo "Available targets:"
	@echo "  make run       - Run camera capture demos"
	@echo "  make booth     - Run photo booth (needs hardware)"
	@echo "  make timelapse - Quick 1-minute timelapse"
	@echo "  make test      - Test camera connection"
	@echo "  make info      - Show camera information"
	@echo "  make deps      - Install dependencies"
	@echo "  make clean     - Clean test photos"
	@echo "  make help      - Show this help message"
	@echo ""
	@echo "Camera Connection:"
	@echo "  Connect camera ribbon cable to CAM0 or CAM1 port"
	@echo "  Blue/silver side faces ethernet/USB ports"
	@echo ""
	@echo "Photo Booth Wiring:"
	@echo "  Button -------- GPIO18 (Pin 12)"
	@echo "  Button -------- GND"
	@echo "  Flash LED ----- GPIO17 (Pin 11) ---[220Ω]--- GND"
	@echo "  RGB Red ------- GPIO22 (Pin 15) ---[220Ω]--- GND"
	@echo "  RGB Green ----- GPIO27 (Pin 13) ---[220Ω]--- GND"
	@echo "  RGB Blue ------ GPIO23 (Pin 16) ---[220Ω]--- GND"