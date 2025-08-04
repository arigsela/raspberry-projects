# Makefile for Relay Control project

.PHONY: all run test on off toggle timer deps clean help

# Default target
all: help

# Run the relay control examples
run:
	@echo "Starting Relay Control Examples..."
	@echo "⚠️  WARNING: High voltage safety required for AC loads!"
	@echo "Relay GPIO pins: 17, 18, 27, 22"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 relay-control.py

# Test relay operation
test:
	@echo "Testing relay module..."
	@echo "Relay will click on/off 3 times"
	@echo "Listen for clicking sound"
	@python3 -c "from gpiozero import OutputDevice; \
	import time; \
	relay = OutputDevice(17, active_high=True); \
	print('If relay is active-low, you may need to set active_high=False'); \
	for i in range(3): \
	    print(f'Relay ON (click {i+1})'); \
	    relay.on(); \
	    time.sleep(1); \
	    print('Relay OFF'); \
	    relay.off(); \
	    time.sleep(1); \
	relay.close(); \
	print('Test complete!')"

# Turn relay ON
on:
	@echo "Turning relay ON..."
	@echo "Press Ctrl+C to turn OFF and exit"
	@python3 -c "from gpiozero import OutputDevice; \
	import signal; \
	relay = OutputDevice(17, active_high=True); \
	print('Relay ON'); \
	relay.on(); \
	try: signal.pause(); \
	except KeyboardInterrupt: pass; \
	finally: \
	    relay.off(); \
	    relay.close(); \
	    print('\\nRelay OFF')"

# Turn relay OFF
off:
	@echo "Turning relay OFF..."
	@python3 -c "from gpiozero import OutputDevice; \
	relay = OutputDevice(17, active_high=True); \
	relay.off(); \
	relay.close(); \
	print('Relay OFF')"

# Toggle relay state
toggle:
	@echo "Toggling relay every 2 seconds..."
	@echo "Press Ctrl+C to stop"
	@python3 -c "from gpiozero import OutputDevice; \
	import time; \
	relay = OutputDevice(17, active_high=True); \
	state = False; \
	try: \
	    while True: \
	        state = not state; \
	        relay.value = state; \
	        print(f'\\rRelay: {\"ON \" if state else \"OFF\"}', end=''); \
	        time.sleep(2); \
	except KeyboardInterrupt: pass; \
	finally: \
	    relay.off(); \
	    relay.close(); \
	    print('\\nRelay OFF')"

# Simple timer
timer:
	@echo "Relay Timer (60 seconds)..."
	@python3 -c "from gpiozero import OutputDevice; \
	import time; \
	relay = OutputDevice(17, active_high=True); \
	duration = 60; \
	print(f'Relay ON for {duration} seconds...'); \
	relay.on(); \
	try: \
	    for i in range(duration, 0, -1): \
	        print(f'\\rTime remaining: {i:3d}s', end=''); \
	        time.sleep(1); \
	    print('\\nTime up!'); \
	except KeyboardInterrupt: \
	    print('\\nTimer cancelled'); \
	finally: \
	    relay.off(); \
	    relay.close(); \
	    print('Relay OFF')"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	@echo ""
	@echo "⚠️  ELECTRICAL SAFETY WARNING:"
	@echo "   - Always disconnect power before wiring"
	@echo "   - Use proper insulation and enclosures"
	@echo "   - Follow local electrical codes"
	@echo "   - Consider hiring an electrician for AC wiring"
	@echo ""
	@echo "Dependencies installed"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "Relay Control Project"
	@echo "===================="
	@echo "Available targets:"
	@echo "  make run    - Run interactive relay demos"
	@echo "  make test   - Test relay clicking"
	@echo "  make on     - Turn relay ON (Ctrl+C to stop)"
	@echo "  make off    - Turn relay OFF"
	@echo "  make toggle - Toggle relay every 2 seconds"
	@echo "  make timer  - Run relay for 60 seconds"
	@echo "  make deps   - Install dependencies"
	@echo "  make clean  - Clean build files"
	@echo "  make help   - Show this help message"
	@echo ""
	@echo "Relay Module Wiring (Low Voltage Side):"
	@echo "  VCC  -> 5V (Pin 2)"
	@echo "  IN1  -> GPIO17 (Pin 11)"
	@echo "  IN2  -> GPIO18 (Pin 12)"
	@echo "  IN3  -> GPIO27 (Pin 13)"
	@echo "  IN4  -> GPIO22 (Pin 15)"
	@echo "  GND  -> GND (Pin 6)"
	@echo ""
	@echo "Load Wiring (HIGH VOLTAGE - DANGER!):"
	@echo "  COM  -> Power source"
	@echo "  NO   -> Load (normally open)"
	@echo "  NC   -> Load (normally closed)"
	@echo ""
	@echo "⚠️  HIGH VOLTAGE WARNING:"
	@echo "   Mains voltage can be FATAL!"
	@echo "   Professional installation recommended!"