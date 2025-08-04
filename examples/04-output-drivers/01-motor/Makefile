# Makefile for DC Motor Control project

.PHONY: all run test forward reverse ramp deps clean help

# Default target
all: help

# Run the motor control examples
run:
	@echo "Starting DC Motor Control..."
	@echo "Using L293D motor driver"
	@echo "Motor A: Enable=GPIO17, IN1=GPIO27, IN2=GPIO22"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 motor-control.py

# Test motor connections
test:
	@echo "Testing motor connections..."
	@echo "Motor will run forward for 2s, stop, then reverse for 2s"
	@python3 -c "from gpiozero import Motor; \
	import time; \
	motor = Motor(forward=27, backward=22, enable=17); \
	print('Forward...'); \
	motor.forward(0.7); \
	time.sleep(2); \
	print('Stop...'); \
	motor.stop(); \
	time.sleep(1); \
	print('Reverse...'); \
	motor.backward(0.7); \
	time.sleep(2); \
	motor.stop(); \
	motor.close(); \
	print('Test complete!')"

# Simple forward motion
forward:
	@echo "Running motor forward at 70% speed..."
	@echo "Press Ctrl+C to stop"
	@python3 -c "from gpiozero import Motor; \
	import signal; \
	motor = Motor(forward=27, backward=22, enable=17); \
	print('Motor running forward...'); \
	motor.forward(0.7); \
	try: signal.pause(); \
	except KeyboardInterrupt: pass; \
	finally: motor.stop(); motor.close(); print('\\nMotor stopped')"

# Simple reverse motion
reverse:
	@echo "Running motor reverse at 70% speed..."
	@echo "Press Ctrl+C to stop"
	@python3 -c "from gpiozero import Motor; \
	import signal; \
	motor = Motor(forward=27, backward=22, enable=17); \
	print('Motor running reverse...'); \
	motor.backward(0.7); \
	try: signal.pause(); \
	except KeyboardInterrupt: pass; \
	finally: motor.stop(); motor.close(); print('\\nMotor stopped')"

# Speed ramp demo
ramp:
	@echo "Speed ramp demonstration..."
	@python3 -c "from gpiozero import Motor; \
	import time; \
	motor = Motor(forward=27, backward=22, enable=17); \
	print('Ramping up...'); \
	for speed in range(0, 101, 10): \
	    motor.forward(speed/100); \
	    print(f'Speed: {speed}%'); \
	    time.sleep(0.5); \
	print('\\nRamping down...'); \
	for speed in range(100, -1, -10): \
	    motor.forward(speed/100); \
	    print(f'Speed: {speed}%'); \
	    time.sleep(0.5); \
	motor.stop(); \
	motor.close(); \
	print('Demo complete!')"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	@echo ""
	@echo "For potentiometer control:"
	sudo apt install -y python3-spidev
	@echo ""
	@echo "⚠️  IMPORTANT: L293D requires external power for motors!"
	@echo "   Do not power motors from Raspberry Pi 5V pin"
	@echo ""
	@echo "Dependencies installed"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "DC Motor Control Project"
	@echo "======================="
	@echo "Available targets:"
	@echo "  make run     - Run interactive motor demos"
	@echo "  make test    - Test motor connections"
	@echo "  make forward - Run motor forward continuously"
	@echo "  make reverse - Run motor reverse continuously"
	@echo "  make ramp    - Speed ramp demonstration"
	@echo "  make deps    - Install dependencies"
	@echo "  make clean   - Clean build files"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "L293D Wiring:"
	@echo "  Enable1 (Pin 1)  -> GPIO17 (PWM speed control)"
	@echo "  IN1 (Pin 2)      -> GPIO27"
	@echo "  OUT1 (Pin 3)     -> Motor (-)"
	@echo "  GND (Pins 4,5)   -> Ground"
	@echo "  OUT2 (Pin 6)     -> Motor (+)"
	@echo "  IN2 (Pin 7)      -> GPIO22"
	@echo "  VCC2 (Pin 8)     -> Motor Power Supply (6-12V)"
	@echo "  VCC1 (Pin 16)    -> 5V (logic power)"
	@echo ""
	@echo "⚠️  Connect motor power supply to VCC2, not Raspberry Pi!"