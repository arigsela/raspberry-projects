# Makefile for Tilt Switch project

.PHONY: all run test alarm game vibration balance drop deps clean help

# Default target
all: help

# Run the tilt switch examples
run:
	@echo "Starting Tilt Switch Examples..."
	@echo "Tilt Switch GPIO: 17"
	@echo "LED GPIO: 18 (optional)"
	@echo "Buzzer GPIO: 22 (optional)"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 tilt-switch.py

# Test tilt detection
test:
	@echo "Testing tilt switch detection..."
	@echo "Tilt the sensor to see state changes"
	@echo "Press Ctrl+C to exit"
	@python3 -c "from gpiozero import Button; \
	import time; \
	tilt = Button(17, pull_up=True); \
	print('Tilt switch configured'); \
	print('UPRIGHT: Switch open (pulled high)'); \
	print('TILTED: Switch closed (connected to GND)'); \
	print(''); \
	last = tilt.is_pressed; \
	print(f'Initial: {"TILTED" if last else "UPRIGHT"}'); \
	try: \
	    while True: \
	        current = tilt.is_pressed; \
	        if current != last: \
	            print(f'Status: {"TILTED" if current else "UPRIGHT"}'); \
	            last = current; \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    print('\\nTest complete'); \
	finally: \
	    tilt.close()"

# Security alarm demo
alarm:
	@echo "Security Alarm System"
	@echo "===================="
	@echo "Press 'a' to arm, 'd' to disarm"
	@echo "System alerts on tilt/movement"
	@echo ""
	@python3 -c "from gpiozero import Button, LED; \
	import sys, select, time; \
	tilt = Button(17, pull_up=True); \
	try: led = LED(18); has_led = True; \
	except: has_led = False; \
	armed = False; alarm = False; \
	print('System ready'); \
	try: \
	    while True: \
	        if select.select([sys.stdin], [], [], 0.01)[0]: \
	            cmd = sys.stdin.read(1).lower(); \
	            if cmd == 'a': \
	                armed = True; alarm = False; \
	                print('\\nSystem ARMED'); \
	                if has_led: led.blink(0.5, 0.5); \
	            elif cmd == 'd': \
	                armed = False; alarm = False; \
	                print('\\nSystem DISARMED'); \
	                if has_led: led.off(); \
	        if armed and tilt.is_pressed and not alarm: \
	            alarm = True; \
	            print('\\n⚠️  ALARM! Movement detected!'); \
	            if has_led: led.blink(0.1, 0.1); \
	        status = 'ARMED' if armed else 'DISARMED'; \
	        alert = ' - ALARM!' if alarm else ''; \
	        print(f'\\rStatus: {status}{alert}   ', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\n\\nShutdown'); \
	finally: \
	    tilt.close(); \
	    if has_led: led.close()"

# Balance game
game:
	@echo "Balance Game!"
	@echo "============="
	@echo "Keep the device level as long as possible"
	@echo "Game starts in 3 seconds..."
	@python3 -c "from gpiozero import Button, LED; \
	import time; \
	tilt = Button(17, pull_up=True); \
	try: led = LED(18); has_led = True; \
	except: has_led = False; \
	for i in range(3, 0, -1): \
	    print(f'{i}...'); \
	    if has_led: led.on(); time.sleep(0.2); led.off(); time.sleep(0.8); \
	    else: time.sleep(1); \
	print('GO! Keep it level!'); \
	start = time.time(); best = 0; attempts = 0; \
	try: \
	    while True: \
	        if not tilt.is_pressed: \
	            elapsed = time.time() - start; \
	            if has_led: led.on(); \
	            print(f'\\rLevel time: {elapsed:.1f}s', end=''); \
	        else: \
	            elapsed = time.time() - start; \
	            if elapsed > 0.5: \
	                attempts += 1; \
	                print(f'\\n\\nTilted! Score: {elapsed:.1f}s'); \
	                if elapsed > best: \
	                    best = elapsed; \
	                    print('★ New best!'); \
	                print(f'Best: {best:.1f}s | Attempts: {attempts}'); \
	                time.sleep(3); \
	                print('\\nGO!'); \
	            if has_led: led.off(); \
	            start = time.time(); \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nBest: {best:.1f}s in {attempts} attempts'); \
	finally: \
	    tilt.close(); \
	    if has_led: led.close()"

# Vibration detector
vibration:
	@echo "Vibration Detector"
	@echo "================="
	@echo "Monitoring vibration levels..."
	@echo "Tap or shake to test"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time; \
	tilt = Button(17, pull_up=True, bounce_time=0.001); \
	count = 0; samples = []; \
	def detect(): \
	    global count; \
	    count += 1; \
	tilt.when_pressed = detect; \
	tilt.when_released = detect; \
	last_time = time.time(); \
	try: \
	    while True: \
	        current = time.time(); \
	        if current - last_time >= 1.0: \
	            samples.append(count); \
	            if len(samples) > 10: samples.pop(0); \
	            avg = sum(samples) / len(samples); \
	            if count == 0: level = 'STABLE'; bar = '─' * 10; \
	            elif count < 5: level = 'LOW'; bar = '█' * 2 + '─' * 8; \
	            elif count < 15: level = 'MEDIUM'; bar = '█' * 5 + '─' * 5; \
	            elif count < 30: level = 'HIGH'; bar = '█' * 8 + '─' * 2; \
	            else: level = 'EXTREME'; bar = '█' * 10; \
	            print(f'\\rVibration: {level:8s} [{bar}] Rate: {count:3d}/s | Avg: {avg:5.1f}', end=''); \
	            count = 0; \
	            last_time = current; \
	        time.sleep(0.01); \
	except KeyboardInterrupt: \
	    print('\\n\\nMonitoring stopped'); \
	finally: \
	    tilt.close()"

# Balance test
balance:
	@echo "Balance Test"
	@echo "============"
	@echo "Check how steady you can hold the device"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time; \
	tilt = Button(17, pull_up=True); \
	tilts = 0; upright = 0; tilted = 0; \
	print('Monitoring for 10 seconds...'); \
	start = time.time(); \
	try: \
	    while time.time() - start < 10: \
	        if tilt.is_pressed: \
	            tilted += 0.05; \
	            if upright > 0.1: tilts += 1; upright = 0; \
	        else: \
	            upright += 0.05; \
	        progress = int((time.time() - start) * 5); \
	        bar = '█' * progress + '░' * (50 - progress); \
	        print(f'\\r[{bar}]', end=''); \
	        time.sleep(0.05); \
	    score = 100 - (tilts * 5) - int(tilted); \
	    print(f'\\n\\nScore: {max(0, score)}/100'); \
	    print(f'Tilts: {tilts}'); \
	    print(f'Upright: {upright:.1f}s ({upright/10*100:.0f}%)'); \
	    print(f'Tilted: {tilted:.1f}s ({tilted/10*100:.0f}%)'); \
	    if score > 90: print('Excellent balance!'); \
	    elif score > 70: print('Good balance!'); \
	    elif score > 50: print('Average balance'); \
	    else: print('Keep practicing!'); \
	except KeyboardInterrupt: \
	    print('\\n\\nTest cancelled'); \
	finally: \
	    tilt.close()"

# Drop detector
drop:
	@echo "Package Drop Detector"
	@echo "===================="
	@echo "Monitoring for drops and rough handling"
	@echo "Press 'r' to reset counters"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time, sys, select; \
	tilt = Button(17, pull_up=True, bounce_time=0.01); \
	drops = 0; tilts = 0; last_event = 0; \
	start = time.time(); \
	def handle_tilt(): \
	    global tilts, drops, last_event; \
	    current = time.time(); \
	    tilts += 1; \
	    if last_event and (current - last_event) < 0.1: \
	        drops += 1; \
	        print(f'\\n⚠️  DROP DETECTED! Total: {drops}'); \
	    last_event = current; \
	tilt.when_pressed = handle_tilt; \
	try: \
	    while True: \
	        if select.select([sys.stdin], [], [], 0.01)[0]: \
	            if sys.stdin.read(1).lower() == 'r': \
	                drops = tilts = 0; \
	                start = time.time(); \
	                print('\\nCounters reset'); \
	        elapsed = time.time() - start; \
	        mins = int(elapsed // 60); \
	        secs = int(elapsed % 60); \
	        print(f'\\rTime: {mins:02d}:{secs:02d} | Tilts: {tilts:3d} | Drops: {drops:2d}', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nMonitoring time: {elapsed/60:.1f} minutes'); \
	    print(f'Total tilts: {tilts}'); \
	    print(f'Detected drops: {drops}'); \
	finally: \
	    tilt.close()"

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
	@echo "Tilt Switch Detection Examples"
	@echo "============================="
	@echo "Available targets:"
	@echo "  make run       - Run interactive demos menu"
	@echo "  make test      - Test tilt detection"
	@echo "  make alarm     - Security alarm system"
	@echo "  make game      - Balance game"
	@echo "  make vibration - Vibration level detector"
	@echo "  make balance   - Balance steadiness test"
	@echo "  make drop      - Package drop detector"
	@echo "  make deps      - Install dependencies"
	@echo "  make clean     - Clean build files"
	@echo "  make help      - Show this help message"
	@echo ""
	@echo "Circuit connections:"
	@echo "  Tilt switch pin 1 -> GPIO17 (Pin 11)"
	@echo "  Tilt switch pin 2 -> GND (Pin 9)"
	@echo "  LED anode        -> GPIO18 (Pin 12) [optional]"
	@echo "  LED cathode      -> 220Ω -> GND"
	@echo "  Buzzer +         -> GPIO22 (Pin 15) [optional]"
	@echo "  Buzzer -         -> GND"
	@echo ""
	@echo "Note: Tilt switch closes circuit when tilted"