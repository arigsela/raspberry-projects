# Makefile for Raspberry Pi Camera Video Recording

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := video-recording.py

# Phony targets
.PHONY: run test demo manual motion security timelapse setup install clean help

# Run the main program
run:
	@echo "Starting Video Recording System..."
	@$(PYTHON) $(PROGRAM)

# Test camera functionality
test:
	@echo "Testing camera functionality..."
	@echo "Taking test photo..."
	@libcamera-still -o test_photo.jpg --width 1920 --height 1080 --timeout 2000 || echo "libcamera-still not available, trying Python test..."
	@$(PYTHON) -c "from video_recording import VideoRecorder; r = VideoRecorder(); r.capture_still(); r.cleanup()" || echo "Camera test failed - check connections"

# Run demo sequence
demo:
	@echo "Running video recording demos..."
	@echo "Note: Demos require camera module and user interaction"
	@echo "Testing basic functionality..."
	@$(PYTHON) -c "from video_recording import VideoRecorder; r = VideoRecorder(); print('Camera initialized successfully'); r.cleanup()"

# Manual recording demo
manual:
	@echo "Starting manual recording mode..."
	@echo "Use keyboard commands: [s]tart/stop, [p]hoto, [l]ist, [q]uit"
	@$(PYTHON) -c "from video_recording import manual_recording; manual_recording()"

# Motion detection demo
motion:
	@echo "Starting motion-triggered recording..."
	@$(PYTHON) -c "from video_recording import motion_triggered_recording; motion_triggered_recording()"

# Security camera system
security:
	@echo "Starting security camera system..."
	@$(PYTHON) -c "from video_recording import security_camera_system; security_camera_system()"

# Timelapse demo
timelapse:
	@echo "Starting timelapse recording..."
	@$(PYTHON) -c "from video_recording import VideoRecorder; r = VideoRecorder(); r.start_timelapse_recording(60, 2.0); import time; time.sleep(65); r.cleanup()"

# Setup camera and dependencies
setup:
	@echo "Setting up camera and dependencies..."
	@echo "Enabling camera interface..."
	@sudo raspi-config nonint do_camera 0 || echo "Camera setup may require manual configuration"
	@echo "Installing Python libraries..."
	@pip install picamera2 gpiozero
	@echo "Installing optional tools..."
	@sudo apt update && sudo apt install -y ffmpeg v4l-utils || echo "Optional tools installation may have failed"
	@echo "Testing camera detection..."
	@libcamera-hello --list-cameras || echo "No cameras detected - check connections and enable camera in raspi-config"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install picamera2 gpiozero

# Convert H.264 files to MP4
convert:
	@echo "Converting H.264 files to MP4..."
	@if command -v ffmpeg >/dev/null 2>&1; then \
		for file in videos/*.h264; do \
			if [ -f "$$file" ]; then \
				mp4_file=$$(echo "$$file" | sed 's/\.h264$$/.mp4/'); \
				echo "Converting $$file to $$mp4_file"; \
				ffmpeg -i "$$file" -c copy "$$mp4_file" -y; \
			fi; \
		done; \
	else \
		echo "ffmpeg not installed. Install with: sudo apt install ffmpeg"; \
	fi

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "test_photo.jpg" -delete
	@echo "Video files preserved in videos/ directory"

# Show disk usage
usage:
	@echo "Disk usage for video files:"
	@if [ -d "videos" ]; then \
		du -sh videos/; \
		echo "Individual files:"; \
		du -h videos/* | sort -hr; \
	else \
		echo "No videos directory found"; \
	fi

# Help
help:
	@echo "Raspberry Pi Camera Video Recording System"
	@echo "=========================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive menu (default)"
	@echo "  make test       - Test camera functionality"
	@echo "  make demo       - Run demo sequence"
	@echo "  make manual     - Manual recording mode"
	@echo "  make motion     - Motion-triggered recording"
	@echo "  make security   - Security camera system"
	@echo "  make timelapse  - Timelapse recording demo"
	@echo "  make setup      - Setup camera and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make convert    - Convert H.264 files to MP4"
	@echo "  make usage      - Show video file disk usage"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Camera module connected to camera connector (not GPIO)"
	@echo "  - Camera enabled: sudo raspi-config → Interface → Camera"
	@echo "  - Adequate power supply (3A+ recommended)"
	@echo "  - Fast storage (Class 10+ SD card or USB 3.0)"
	@echo ""
	@echo "Hardware setup:"
	@echo "  - Connect camera via ribbon cable to camera connector"
	@echo "  - Optional: PIR sensor → GPIO27, 5V, GND"
	@echo "  - Optional: Record button → GPIO17, GND"
	@echo "  - Optional: Mode button → GPIO18, GND"
	@echo "  - Optional: Status LEDs → GPIO23/24 with 220Ω resistors"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time setup"
	@echo "  make test        # Test camera"
	@echo "  make manual      # Interactive recording"
	@echo "  make security    # Security monitoring"
	@echo "  make convert     # Convert recordings to MP4"
	@echo ""
	@echo "Storage notes:"
	@echo "  - 1080p30 H.264 ≈ 400MB per 10 minutes"
	@echo "  - Monitor disk space regularly"
	@echo "  - Use 'make usage' to check file sizes"