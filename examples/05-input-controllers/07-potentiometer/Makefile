# Makefile for Potentiometer project

.PHONY: all run test led servo calibrate deps clean help

# Default target
all: help

# Run the potentiometer examples
run:
	@echo "Starting Potentiometer Examples..."
	@echo "Using MCP3008 ADC on SPI0"
	@echo "Potentiometer on channel 0"
	@echo "Select example from menu"
	@echo "Press Ctrl+C to stop"
	@python3 potentiometer.py

# Test ADC connection
test:
	@echo "Testing MCP3008 ADC connection..."
	@python3 -c "from gpiozero import MCP3008; \
	import time; \
	try: \
	    pot = MCP3008(channel=0); \
	    print('MCP3008 detected!'); \
	    print('Reading potentiometer (5 samples):'); \
	    for i in range(5): \
	        value = pot.value; \
	        voltage = value * 3.3; \
	        print(f'  Reading {i+1}: {value:.3f} ({voltage:.2f}V)'); \
	        time.sleep(0.5); \
	    print('Test successful!'); \
	except Exception as e: \
	    print(f'Error: {e}'); \
	    print('Check SPI is enabled and wiring is correct')"

# LED brightness demo
led:
	@echo "LED Brightness Control Demo..."
	@echo "Connect LED to GPIO17"
	@echo "Rotate potentiometer to control brightness"
	@python3 -c "from gpiozero import MCP3008, PWMLED; \
	import time; \
	pot = MCP3008(0); \
	led = PWMLED(17); \
	print('Press Ctrl+C to stop'); \
	try: \
	    while True: \
	        led.value = pot.value; \
	        print(f'\\rBrightness: {int(pot.value*100)}%  ', end=''); \
	        time.sleep(0.01); \
	except KeyboardInterrupt: \
	    pass; \
	finally: \
	    led.close(); \
	    print('\\nDemo stopped')"

# Servo control demo
servo:
	@echo "Servo Position Control Demo..."
	@echo "Connect servo to GPIO22"
	@echo "Rotate potentiometer to control position"
	@python3 -c "from gpiozero import MCP3008, Servo; \
	import time; \
	pot = MCP3008(0); \
	servo = Servo(22); \
	print('Press Ctrl+C to stop'); \
	try: \
	    while True: \
	        servo.value = (pot.value * 2) - 1; \
	        angle = int(pot.value * 180); \
	        print(f'\\rAngle: {angle:3d}°  ', end=''); \
	        time.sleep(0.02); \
	except KeyboardInterrupt: \
	    pass; \
	finally: \
	    servo.close(); \
	    print('\\nDemo stopped')"

# Calibration utility
calibrate:
	@echo "Potentiometer Calibration Utility"
	@python3 -c "from gpiozero import MCP3008; \
	import time; \
	pot = MCP3008(0); \
	print('Rotate potentiometer to find limits...'); \
	print('Press Ctrl+C when done'); \
	min_val = 1.0; \
	max_val = 0.0; \
	try: \
	    while True: \
	        val = pot.value; \
	        if val < min_val: min_val = val; \
	        if val > max_val: max_val = val; \
	        print(f'\\rCurrent: {val:.3f}  Min: {min_val:.3f}  Max: {max_val:.3f}  Range: {(max_val-min_val):.3f}', end=''); \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nCalibration complete!'); \
	    print(f'Usable range: {(max_val-min_val)*100:.1f}%'); \
	    print(f'Dead zone at min: {min_val*100:.1f}%'); \
	    print(f'Dead zone at max: {(1-max_val)*100:.1f}%')"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero python3-spidev
	@echo ""
	@echo "Enabling SPI interface..."
	sudo raspi-config nonint do_spi 0 || echo "SPI may already be enabled"
	@echo ""
	@echo "Verifying SPI devices..."
	ls -la /dev/spi* || echo "No SPI devices found - reboot may be required"
	@echo ""
	@echo "Dependencies installed"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "Potentiometer Input Project"
	@echo "==========================="
	@echo "Available targets:"
	@echo "  make run       - Run interactive examples"
	@echo "  make test      - Test MCP3008 connection"
	@echo "  make led       - LED brightness control demo"
	@echo "  make servo     - Servo position control demo"
	@echo "  make calibrate - Calibration utility"
	@echo "  make deps      - Install dependencies"
	@echo "  make clean     - Clean build files"
	@echo "  make help      - Show this help message"
	@echo ""
	@echo "MCP3008 Wiring:"
	@echo "  VDD  -> 3.3V (Pin 1)"
	@echo "  VREF -> 3.3V (Pin 1)"
	@echo "  AGND -> GND  (Pin 6)"
	@echo "  CLK  -> GPIO11/SCLK (Pin 23)"
	@echo "  DOUT -> GPIO9/MISO  (Pin 21)"
	@echo "  DIN  -> GPIO10/MOSI (Pin 19)"
	@echo "  CS   -> GPIO8/CE0   (Pin 24)"
	@echo "  DGND -> GND  (Pin 6)"
	@echo ""
	@echo "Potentiometer Wiring:"
	@echo "  Terminal 1 -> 3.3V"
	@echo "  Terminal 2 (Wiper) -> MCP3008 CH0"
	@echo "  Terminal 3 -> GND"