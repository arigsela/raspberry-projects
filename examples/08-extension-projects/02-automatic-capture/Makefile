# Makefile for Automatic Motion Capture System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := automatic-motion-capture.py

# Phony targets
.PHONY: run test demo interactive security auto photo video burst timelapse setup install status clean help

# Run the main program
run:
	@echo "Starting Automatic Motion Capture System..."
	@$(PYTHON) $(PROGRAM)

# Test hardware components
test:
	@echo "Testing motion capture hardware..."
	@echo "1. Testing PIR motion sensors..."
	@$(PYTHON) -c "from gpiozero import MotionSensor; import time; pir = MotionSensor(27); print('Primary PIR sensor initialized'); print('Wave your hand in front of sensor...'); start=time.time(); while time.time()-start<10: print('Motion detected!' if pir.motion_detected else 'No motion', end='\r'); time.sleep(0.5); pir.close(); print('\nPIR test complete')" || echo "PIR sensor test failed"
	@echo "2. Testing camera connection..."
	@libcamera-hello --timeout 2000 || echo "Camera test failed - check connections"
	@echo "3. Testing LED indicators..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; leds = [LED(24), LED(26), LED(19), PWMLED(25)]; [led.on() for led in leds]; time.sleep(1); [led.off() for led in leds]; [led.close() for led in leds]; print('LED test complete')" || echo "LED test failed"
	@echo "4. Testing buzzer..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; buzzer = Buzzer(13); buzzer.beep(0.1, 0.1, n=3); buzzer.close(); print('Buzzer test complete')" || echo "Buzzer test failed"

# Run interactive demo
demo:
	@echo "Running motion capture demo..."
	@$(PYTHON) -c "from automatic_motion_capture import interactive_demo; interactive_demo()"

# Interactive mode
interactive:
	@echo "Starting interactive motion capture..."
	@$(PYTHON) -c "from automatic_motion_capture import interactive_demo; interactive_demo()"

# Security monitoring mode
security:
	@echo "Starting security monitoring mode..."
	@$(PYTHON) -c "from automatic_motion_capture import security_monitoring; security_monitoring()"

# Automatic demonstration
auto:
	@echo "Running automatic demonstration..."
	@$(PYTHON) -c "from automatic_motion_capture import automatic_demo; automatic_demo()"

# Test photo capture mode
photo:
	@echo "Testing photo capture mode..."
	@$(PYTHON) -c "from automatic_motion_capture import MotionCaptureSystem; import time; sys = MotionCaptureSystem(); sys.current_mode = 0; print('Photo mode active - trigger motion or wait for simulation...'); time.sleep(10); sys._trigger_capture(); time.sleep(2); sys.cleanup()"

# Test video capture mode
video:
	@echo "Testing video capture mode..."
	@$(PYTHON) -c "from automatic_motion_capture import MotionCaptureSystem; import time; sys = MotionCaptureSystem(); sys.current_mode = 1; print('Video mode active - triggering capture...'); sys._trigger_capture(); time.sleep(12); sys.cleanup()"

# Test burst capture mode
burst:
	@echo "Testing burst capture mode..."
	@$(PYTHON) -c "from automatic_motion_capture import MotionCaptureSystem; import time; sys = MotionCaptureSystem(); sys.current_mode = 3; print('Burst mode active - triggering capture...'); sys._trigger_capture(); time.sleep(5); sys.cleanup()"

# Test timelapse mode
timelapse:
	@echo "Testing timelapse mode (30 second demo)..."
	@$(PYTHON) -c "from automatic_motion_capture import MotionCaptureSystem; import time; sys = MotionCaptureSystem(); sys.current_mode = 2; sys.timelapse_duration = 30; print('Timelapse mode active - triggering capture...'); sys._trigger_capture(); time.sleep(35; sys.cleanup()"

# Setup hardware interfaces and dependencies
setup:
	@echo "Setting up motion capture system..."
	@echo "Enabling camera interface..."
	@sudo raspi-config nonint do_camera 0 || echo "Camera setup may require manual configuration"
	@echo "Installing Python libraries..."
	@pip install picamera2 gpiozero
	@echo "Testing camera detection..."
	@libcamera-hello --list-cameras || echo "⚠ No cameras detected - check connections and enable camera"
	@echo "Creating output directory..."
	@mkdir -p motion_captures
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install picamera2 gpiozero

# System status check
status:
	@echo "Motion Capture System Status"
	@echo "============================="
	@echo "Camera interface:"
	@libcamera-hello --list-cameras 2>/dev/null | head -3 || echo "  ❌ Camera not detected"
	@echo "GPIO access:"
	@$(PYTHON) -c "from gpiozero import LED; LED(26).close(); print('  ✓ GPIO access working')" 2>/dev/null || echo "  ❌ GPIO access failed"
	@echo "Dependencies:"
	@$(PYTHON) -c "import picamera2; print('  ✓ picamera2 installed')" 2>/dev/null || echo "  ❌ picamera2 not installed"
	@$(PYTHON) -c "import gpiozero; print('  ✓ gpiozero installed')" 2>/dev/null || echo "  ❌ gpiozero not installed"
	@echo "Output directory:"
	@test -d motion_captures && echo "  ✓ motion_captures directory exists" || echo "  ❌ motion_captures directory missing"
	@echo "Disk space:"
	@df -h . | tail -1 | awk '{print "  Available: " $$4 " (" $$5 " used)"}'
	@echo "Recent captures:"
	@ls -la motion_captures/ 2>/dev/null | tail -5 || echo "  No captures found"

# View recent captures
recent:
	@echo "Recent Motion Captures"
	@echo "======================"
	@if [ -d "motion_captures" ]; then \
		echo "Photos and videos in motion_captures/:"; \
		ls -lth motion_captures/ | head -10; \
		echo ""; \
		echo "Storage usage:"; \
		du -sh motion_captures/; \
	else \
		echo "No captures directory found"; \
	fi

# Clean up files and cache
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "motion_capture_settings.json" -delete
	find . -type f -name "motion_log.json" -delete
	@echo "Note: Captured photos and videos preserved in motion_captures/"

# Archive old captures
archive:
	@echo "Archiving old captures..."
	@if [ -d "motion_captures" ]; then \
		timestamp=$$(date +%Y%m%d_%H%M%S); \
		archive_name="motion_archive_$$timestamp.tar.gz"; \
		echo "Creating archive: $$archive_name"; \
		tar -czf "$$archive_name" motion_captures/; \
		echo "Archive created: $$archive_name"; \
		echo "To restore: tar -xzf $$archive_name"; \
	else \
		echo "No captures directory found"; \
	fi

# Convert H.264 videos to MP4
convert:
	@echo "Converting H.264 videos to MP4..."
	@if command -v ffmpeg >/dev/null 2>&1; then \
		if [ -d "motion_captures" ]; then \
			for file in motion_captures/*.h264; do \
				if [ -f "$$file" ]; then \
					mp4_file=$$(echo "$$file" | sed 's/\.h264$$/.mp4/'); \
					echo "Converting $$file to $$mp4_file"; \
					ffmpeg -i "$$file" -c copy "$$mp4_file" -y 2>/dev/null; \
				fi; \
			done; \
			echo "Conversion complete"; \
		else \
			echo "No motion_captures directory found"; \
		fi; \
	else \
		echo "ffmpeg not installed. Install with: sudo apt install ffmpeg"; \
	fi

# Monitor system performance
monitor:
	@echo "Monitoring system performance..."
	@echo "Press Ctrl+C to stop monitoring"
	@while true; do \
		clear; \
		echo "Motion Capture System Monitor"; \
		echo "============================="; \
		echo "Time: $$(date)"; \
		echo ""; \
		echo "CPU Usage:"; \
		top -bn1 | grep "Cpu(s)" | awk '{print "  " $$2 " " $$3 " " $$4}'; \
		echo ""; \
		echo "Memory Usage:"; \
		free -h | grep "Mem:" | awk '{print "  Used: " $$3 " / " $$2 " (" $$3*100/$$2 "%)"}'; \
		echo ""; \
		echo "Disk Usage:"; \
		df -h . | tail -1 | awk '{print "  Used: " $$3 " / " $$2 " (" $$5 ")"}'; \
		echo ""; \
		echo "Temperature:"; \
		vcgencmd measure_temp 2>/dev/null | awk -F'=' '{print "  CPU: " $$2}' || echo "  Temperature not available"; \
		echo ""; \
		echo "Recent Activity:"; \
		if [ -d "motion_captures" ]; then \
			ls -lt motion_captures/ | head -3 | tail -2 | awk '{print "  " $$9 " (" $$6 " " $$7 " " $$8 ")"}'; \
		else \
			echo "  No captures directory"; \
		fi; \
		sleep 5; \
	done

# Help
help:
	@echo "Automatic Motion Capture System"
	@echo "==============================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive system (default)"
	@echo "  make test       - Test all hardware components"
	@echo "  make demo       - Interactive demonstration"
	@echo "  make interactive- Interactive motion capture mode"
	@echo "  make security   - Security monitoring mode"
	@echo "  make auto       - Automatic demonstration"
	@echo ""
	@echo "Capture Mode Tests:"
	@echo "  make photo      - Test photo capture mode"
	@echo "  make video      - Test video capture mode"
	@echo "  make burst      - Test burst capture mode"
	@echo "  make timelapse  - Test timelapse mode (30s demo)"
	@echo ""
	@echo "System Management:"
	@echo "  make setup      - Setup interfaces and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make status     - Check system status"
	@echo "  make recent     - View recent captures"
	@echo "  make convert    - Convert H.264 videos to MP4"
	@echo "  make archive    - Archive old captures"
	@echo "  make monitor    - Monitor system performance"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - Raspberry Pi Camera Module connected to camera connector"
	@echo "  - PIR motion sensor (HC-SR501) connected to GPIO27"
	@echo "  - Optional: Second PIR sensor on GPIO22 for dual-zone detection"
	@echo "  - Control buttons and status LEDs"
	@echo "  - Buzzer for audio feedback"
	@echo ""
	@echo "Pin Connections:"
	@echo "  PIR Sensors:  Primary=GPIO27, Secondary=GPIO22 (optional)"
	@echo "  Buttons:      Capture=GPIO17, Mode=GPIO18, Settings=GPIO23"
	@echo "  LEDs:         Motion=GPIO24, Capture=GPIO25, Status=GPIO26, Power=GPIO19"
	@echo "  Buzzer:       GPIO13"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Camera enabled: sudo raspi-config → Interface → Camera"
	@echo "  - Adequate power supply (PIR sensors need stable 5V)"
	@echo "  - Fast storage (Class 10+ SD card for video recording)"
	@echo "  - PIR sensor warm-up time: 30-60 seconds after power-on"
	@echo ""
	@echo "Capture Modes:"
	@echo "  1. PHOTO - Single high-quality photo (3280x2464)"
	@echo "  2. VIDEO - Motion-triggered video recording (1920x1080)"
	@echo "  3. BURST - Rapid sequence of photos"
	@echo "  4. TIMELAPSE - Motion-triggered timelapse sequence"
	@echo "  5. SECURITY - Continuous monitoring with recording"
	@echo ""
	@echo "Advanced Features:"
	@echo "  - Intelligent false positive filtering"
	@echo "  - Automatic storage management"
	@echo "  - Dual-sensor motion detection"
	@echo "  - Time-based sensitivity adjustment"
	@echo "  - Motion pattern learning"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time setup"
	@echo "  make test        # Test all hardware"
	@echo "  make demo        # Interactive demonstration"
	@echo "  make security    # Start security monitoring"
	@echo "  make status      # Check system health"
	@echo "  make convert     # Convert videos to MP4"
	@echo ""
	@echo "Troubleshooting:"
	@echo "  - PIR not triggering: Check power, allow warm-up time"
	@echo "  - False positives: Adjust PIR sensitivity pot, enable filtering"
	@echo "  - Storage full: Use 'make archive' and 'make clean'"
	@echo "  - Camera issues: Check cable, enable in raspi-config"