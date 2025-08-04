# Makefile for Slide Switch project

.PHONY: all run test mode safety power state deps clean help

# Default target
all: help

# Run the slide switch examples
run:
	@echo "Starting Slide Switch Examples..."
	@echo "Switch GPIO: 17 (COM to GPIO, one side to GND)"
	@echo "LED GPIOs: 18, 27 (optional indicators)"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 slide-switch.py

# Test switch position
test:
	@echo "Testing slide switch position..."
	@echo "Move switch to see position changes"
	@echo "Press Ctrl+C to exit"
	@python3 -c "from gpiozero import Button; \
	import time; \
	switch = Button(17, pull_up=True); \
	print('Switch configured with internal pull-up'); \
	print('Position 1: Switch connects GPIO to GND'); \
	print('Position 2: Switch open (pulled high)'); \
	print(''); \
	last = switch.is_pressed; \
	print(f'Initial: Position {1 if last else 2}'); \
	try: \
	    while True: \
	        current = switch.is_pressed; \
	        if current != last: \
	            print(f'Changed to: Position {1 if current else 2}'); \
	            last = current; \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\nTest complete'); \
	finally: \
	    switch.close()"

# Mode selector demo
mode:
	@echo "Mode Selector Demo"
	@echo "================="
	@echo "Position 1: Normal Mode"
	@echo "Position 2: Advanced Mode"
	@echo ""
	@python3 -c "from gpiozero import Button, LED; \
	import time; \
	switch = Button(17, pull_up=True); \
	try: led1 = LED(18); led2 = LED(27); has_leds = True; \
	except: has_leds = False; \
	modes = {True: 'Normal', False: 'Advanced'}; \
	last_mode = None; \
	print('Switch position selects mode:'); \
	try: \
	    while True: \
	        mode = switch.is_pressed; \
	        if mode != last_mode: \
	            print(f'\\nMode: {modes[mode]}'); \
	            if has_leds: \
	                if mode: led1.on(); led2.off(); \
	                else: led1.off(); led2.on(); \
	            last_mode = mode; \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\nExiting'); \
	finally: \
	    switch.close(); \
	    if has_leds: led1.close(); led2.close()"

# Safety interlock demo
safety:
	@echo "Safety Interlock System"
	@echo "======================"
	@echo "Switch must be in Position 1 for operation"
	@echo "Press 's' to start, 'x' to stop operation"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time, sys, select; \
	switch = Button(17, pull_up=True); \
	active = False; \
	print('System ready'); \
	try: \
	    while True: \
	        if select.select([sys.stdin], [], [], 0.01)[0]: \
	            cmd = sys.stdin.read(1); \
	            if cmd == 's' and switch.is_pressed: \
	                active = True; \
	                print('\\nOperation STARTED'); \
	            elif cmd == 's' and not switch.is_pressed: \
	                print('\\nBLOCKED - Safety not enabled!'); \
	            elif cmd == 'x': \
	                active = False; \
	                print('\\nOperation STOPPED'); \
	        if active and not switch.is_pressed: \
	            active = False; \
	            print('\\nEMERGENCY STOP - Safety disabled!'); \
	        status = f'\\rSafety: {"ON" if switch.is_pressed else "OFF":3s} | Operation: {"ACTIVE" if active else "STOPPED":7s}'; \
	        print(status, end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\n\\nShutdown'); \
	finally: \
	    switch.close()"

# Power mode demo
power:
	@echo "Power Mode Selector"
	@echo "=================="
	@echo "Position 1: Normal Power"
	@echo "Position 2: Power Save"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time; \
	switch = Button(17, pull_up=True); \
	components = {'CPU': (100, 40), 'WiFi': (30, 0), 'Display': (50, 10), 'Sensors': (20, 5)}; \
	try: \
	    while True: \
	        normal = switch.is_pressed; \
	        print(f'\\n{"Normal Mode" if normal else "Power Save Mode"}'); \
	        print('-' * 25); \
	        total = 0; \
	        for name, (norm, save) in components.items(): \
	            power = norm if normal else save; \
	            total += power; \
	            status = 'OFF' if power == 0 else f'{power}mA'; \
	            print(f'{name:8s}: {status:>6s}'); \
	        print('-' * 25); \
	        print(f'Total:    {total:>6d}mA'); \
	        time.sleep(2 if not normal else 1); \
	except KeyboardInterrupt: \
	    print('\\nExiting'); \
	finally: \
	    switch.close()"

# State machine demo
state:
	@echo "State Machine Demo"
	@echo "================="
	@echo "Switch controls state transitions"
	@echo "Position changes trigger state changes"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time; \
	switch = Button(17, pull_up=True); \
	states = ['IDLE', 'READY', 'ACTIVE', 'COMPLETE']; \
	current = 0; \
	last_pos = switch.is_pressed; \
	print(f'Initial state: {states[current]}'); \
	try: \
	    while True: \
	        pos = switch.is_pressed; \
	        if pos != last_pos: \
	            if pos: \
	                current = min(current + 1, len(states) - 1); \
	            else: \
	                current = max(current - 1, 0); \
	            print(f'State: {states[current]}'); \
	            last_pos = pos; \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\nExiting'); \
	finally: \
	    switch.close()"

# Install dependencies
deps:
	@echo "Installing dependencies..."
	sudo apt update
	sudo apt install -y python3-gpiozero
	@echo "Dependencies installed"

# Clean (nothing to clean for Python)
clean:
	@echo "Nothing to clean"

# Help target
help:
	@echo "Slide Switch Control Examples"
	@echo "============================"
	@echo "Available targets:"
	@echo "  make run    - Run interactive demos menu"
	@echo "  make test   - Test switch position detection"
	@echo "  make mode   - Mode selector demo"
	@echo "  make safety - Safety interlock demo"
	@echo "  make power  - Power mode selector"
	@echo "  make state  - State machine demo"
	@echo "  make deps   - Install dependencies"
	@echo "  make clean  - Clean build files"
	@echo "  make help   - Show this help message"
	@echo ""
	@echo "Circuit connections:"
	@echo "  Switch COM   -> GPIO17 (Pin 11)"
	@echo "  Switch NO/NC -> GND (Pin 9)"
	@echo "  LED1 anode   -> GPIO18 (Pin 12) [optional]"
	@echo "  LED2 anode   -> GPIO27 (Pin 13) [optional]"
	@echo "  LED cathodes -> 220Ω -> GND"
	@echo ""
	@echo "Note: Only connect one switch terminal to GND"