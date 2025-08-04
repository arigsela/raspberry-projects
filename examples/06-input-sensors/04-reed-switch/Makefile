# Makefile for Reed Switch project

.PHONY: all run test door security rpm counter level field deps clean help

# Default target
all: help

# Run the reed switch examples
run:
	@echo "Starting Reed Switch Examples..."
	@echo "Reed Switch GPIO: 17"
	@echo "LED GPIO: 18 (optional)"
	@echo "Buzzer GPIO: 22 (optional)"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 reed-switch.py

# Test magnetic detection
test:
	@echo "Testing reed switch detection..."
	@echo "Bring magnet close to reed switch"
	@echo "Press Ctrl+C to exit"
	@python3 -c "from gpiozero import Button; \
	import time; \
	reed = Button(17, pull_up=True); \
	print('Reed switch configured'); \
	print('OPEN: No magnet detected'); \
	print('CLOSED: Magnet detected'); \
	print(''); \
	last = reed.is_pressed; \
	print(f'Initial: {\"CLOSED\" if last else \"OPEN\"}'); \
	try: \
	    while True: \
	        current = reed.is_pressed; \
	        if current != last: \
	            print(f'Status: {\"CLOSED - Magnet detected\" if current else \"OPEN - No magnet\"}'); \
	            last = current; \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    print('\\nTest complete'); \
	finally: \
	    reed.close()"

# Door sensor demo
door:
	@echo "Door/Window Sensor Demo"
	@echo "======================"
	@echo "Simulates door sensor operation"
	@echo "Door is CLOSED when magnet is detected"
	@echo ""
	@python3 -c "from gpiozero import Button, LED; \
	from datetime import datetime; \
	import time; \
	reed = Button(17, pull_up=True); \
	try: led = LED(18); has_led = True; \
	except: has_led = False; \
	count = 0; last_opened = None; \
	def opened(): \
	    global count, last_opened; \
	    count += 1; \
	    last_opened = datetime.now(); \
	    print(f'\\n⚠️  DOOR OPENED at {last_opened.strftime(\"%H:%M:%S\")}'); \
	    if has_led: led.on(); \
	def closed(): \
	    if last_opened: \
	        duration = (datetime.now() - last_opened).total_seconds(); \
	        print(f'\\n✓ Door CLOSED (open for {duration:.1f}s)'); \
	    else: \
	        print('\\n✓ Door CLOSED'); \
	    if has_led: led.off(); \
	reed.when_released = opened; \
	reed.when_pressed = closed; \
	if reed.is_pressed: \
	    print('Door is: CLOSED'); \
	    if has_led: led.off(); \
	else: \
	    print('Door is: OPEN'); \
	    if has_led: led.on(); \
	print('Monitoring...'); \
	try: \
	    import signal; \
	    signal.pause(); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nTotal openings: {count}'); \
	finally: \
	    reed.close(); \
	    if has_led: led.close()"

# Security system demo
security:
	@echo "Security System Demo"
	@echo "==================="
	@echo "Commands: 'a' = arm, 'd' = disarm, 's' = status"
	@echo ""
	@python3 -c "from gpiozero import Button, Buzzer; \
	import sys, select, time; \
	reed = Button(17, pull_up=True); \
	try: buzzer = Buzzer(22); has_buzzer = True; \
	except: has_buzzer = False; \
	armed = False; alarm = False; \
	print('System ready'); \
	try: \
	    while True: \
	        if select.select([sys.stdin], [], [], 0.01)[0]: \
	            cmd = sys.stdin.read(1).lower(); \
	            if cmd == 'a': \
	                if reed.is_pressed: \
	                    armed = True; alarm = False; \
	                    print('\\nSystem ARMED'); \
	                else: \
	                    print('\\nCannot arm - door is OPEN'); \
	            elif cmd == 'd': \
	                armed = False; alarm = False; \
	                if has_buzzer: buzzer.off(); \
	                print('\\nSystem DISARMED'); \
	            elif cmd == 's': \
	                door = 'Secure' if reed.is_pressed else 'OPEN'; \
	                print(f'\\nDoor: {door}'); \
	                print(f'System: {\"ARMED\" if armed else \"DISARMED\"}'); \
	        if armed and not reed.is_pressed and not alarm: \
	            alarm = True; \
	            print('\\n🚨 ALARM! Door opened!'); \
	            if has_buzzer: buzzer.beep(0.2, 0.2); \
	        status = 'ARMED' if armed else 'DISARMED'; \
	        door = 'Secure' if reed.is_pressed else 'OPEN'; \
	        print(f'\\rSystem: {status} | Door: {door}     ', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\n\\nShutdown'); \
	finally: \
	    reed.close(); \
	    if has_buzzer: buzzer.close()"

# RPM measurement
rpm:
	@echo "RPM Measurement"
	@echo "==============="
	@echo "Attach magnet to rotating object"
	@echo "Position reed switch to detect each rotation"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time; \
	reed = Button(17, pull_up=True, bounce_time=0.01); \
	pulse_times = []; rpm = 0; max_rpm = 0; \
	def pulse(): \
	    global rpm, max_rpm; \
	    current = time.time(); \
	    pulse_times.append(current); \
	    pulse_times[:] = [t for t in pulse_times if current - t < 2.0]; \
	    if len(pulse_times) >= 2: \
	        duration = pulse_times[-1] - pulse_times[0]; \
	        if duration > 0: \
	            rpm = (len(pulse_times) - 1) / duration * 60; \
	            max_rpm = max(max_rpm, rpm); \
	reed.when_pressed = pulse; \
	print('Rotate object with magnet...'); \
	try: \
	    while True: \
	        bar_len = int(rpm / 10); \
	        bar = '█' * min(bar_len, 50) + '░' * (50 - min(bar_len, 50)); \
	        print(f'\\rRPM: {rpm:6.1f} [{bar}] Max: {max_rpm:6.1f}', end=''); \
	        if pulse_times and time.time() - pulse_times[-1] > 0.5: \
	            rpm *= 0.9; \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nMax RPM: {max_rpm:.1f}'); \
	finally: \
	    reed.close()"

# Proximity counter
counter:
	@echo "Proximity Counter"
	@echo "================="
	@echo "Counts objects with magnets passing by"
	@echo "Press 'r' to reset counter"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	from datetime import datetime; \
	import sys, select, time; \
	reed = Button(17, pull_up=True, bounce_time=0.1); \
	count = 0; last_time = None; \
	def detected(): \
	    global count, last_time; \
	    count += 1; \
	    last_time = datetime.now(); \
	    print(f'\\nObject #{count} at {last_time.strftime(\"%H:%M:%S\")}'); \
	reed.when_pressed = detected; \
	start = datetime.now(); \
	try: \
	    while True: \
	        if select.select([sys.stdin], [], [], 0.01)[0]: \
	            if sys.stdin.read(1).lower() == 'r': \
	                count = 0; \
	                start = datetime.now(); \
	                print('\\nCounter reset'); \
	        elapsed = (datetime.now() - start).total_seconds(); \
	        rate = (count / elapsed * 3600) if elapsed > 0 else 0; \
	        last_str = last_time.strftime('%H:%M:%S') if last_time else 'None'; \
	        print(f'\\rCount: {count:4d} | Rate: {rate:5.1f}/hr | Last: {last_str}', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nTotal: {count} in {elapsed/60:.1f} minutes'); \
	    print(f'Average rate: {rate:.1f} per hour'); \
	finally: \
	    reed.close()"

# Liquid level demo
level:
	@echo "Liquid Level Sensor"
	@echo "=================="
	@echo "Simulates float switch for tank monitoring"
	@echo "Magnet = Full, No magnet = Empty"
	@echo ""
	@python3 -c "from gpiozero import Button, Buzzer; \
	import time; \
	reed = Button(17, pull_up=True); \
	try: buzzer = Buzzer(22); has_buzzer = True; \
	except: has_buzzer = False; \
	alert_sent = False; \
	try: \
	    while True: \
	        if reed.is_pressed: \
	            level = 100; status = 'FULL'; \
	            alert_sent = False; \
	            if has_buzzer: buzzer.off(); \
	        else: \
	            level = 0; status = 'EMPTY'; \
	            if not alert_sent: \
	                alert_sent = True; \
	                print('\\n⚠️  Low level alert!'); \
	                if has_buzzer: buzzer.beep(0.5, 0.5, n=3); \
	        bar_len = int(level / 2); \
	        bar = '█' * bar_len + '░' * (50 - bar_len); \
	        print(f'\\rLevel: {status:6s} [{bar}] {level:3d}%', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    print('\\n\\nMonitoring stopped'); \
	finally: \
	    reed.close(); \
	    if has_buzzer: buzzer.close()"

# Magnetic field strength
field:
	@echo "Magnetic Field Strength"
	@echo "======================"
	@echo "Move magnet closer/farther to test"
	@echo "Estimates strength by activation frequency"
	@echo ""
	@python3 -c "from gpiozero import Button; \
	import time; \
	reed = Button(17, pull_up=True, bounce_time=0.001); \
	samples = []; max_str = 0; \
	try: \
	    while True: \
	        acts = 0; start = time.time(); \
	        while time.time() - start < 0.1: \
	            if reed.is_pressed: \
	                acts += 1; \
	                while reed.is_pressed and time.time() - start < 0.1: \
	                    time.sleep(0.001); \
	        strength = min(100, acts * 10); \
	        samples.append(strength); \
	        if len(samples) > 10: samples.pop(0); \
	        avg = sum(samples) / len(samples); \
	        max_str = max(max_str, avg); \
	        if avg == 0: level = 'No field'; \
	        elif avg < 20: level = 'Weak'; \
	        elif avg < 50: level = 'Moderate'; \
	        elif avg < 80: level = 'Strong'; \
	        else: level = 'Very strong'; \
	        bar_len = int(avg / 2); \
	        bar = '█' * bar_len + '░' * (50 - bar_len); \
	        print(f'\\rField: {level:11s} [{bar}] {avg:3.0f}% (Max: {max_str:3.0f}%)', end=''); \
	        time.sleep(0.05); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nMax field strength: {max_str:.0f}%'); \
	finally: \
	    reed.close()"

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
	@echo "Reed Switch Magnetic Detection"
	@echo "============================="
	@echo "Available targets:"
	@echo "  make run     - Run interactive demos menu"
	@echo "  make test    - Test magnetic detection"
	@echo "  make door    - Door/window sensor demo"
	@echo "  make security- Security system with alarm"
	@echo "  make rpm     - RPM/speed measurement"
	@echo "  make counter - Proximity object counter"
	@echo "  make level   - Liquid level sensor demo"
	@echo "  make field   - Magnetic field strength"
	@echo "  make deps    - Install dependencies"
	@echo "  make clean   - Clean build files"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "Circuit connections:"
	@echo "  Reed switch pin 1 -> GPIO17 (Pin 11)"
	@echo "  Reed switch pin 2 -> GND (Pin 9)"
	@echo "  LED anode        -> GPIO18 (Pin 12) [optional]"
	@echo "  LED cathode      -> 220Ω -> GND"
	@echo "  Buzzer +         -> GPIO22 (Pin 15) [optional]"
	@echo "  Buzzer -         -> GND"
	@echo ""
	@echo "Note: Reed switch closes when magnet is near"