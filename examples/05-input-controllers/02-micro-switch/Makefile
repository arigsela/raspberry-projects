# Makefile for Micro Switch project

.PHONY: all run test counter game morse deps clean help

# Default target
all: help

# Run the micro switch examples
run:
	@echo "Starting Micro Switch Examples..."
	@echo "Switch GPIO: 17 (with pull-up)"
	@echo "LED GPIO: 18 (optional)"
	@echo "Select demo from menu"
	@echo "Press Ctrl+C to stop"
	@python3 micro-switch.py

# Test switch detection
test:
	@echo "Testing micro switch detection..."
	@echo "Press the switch to test"
	@echo "Press Ctrl+C to exit"
	@python3 -c "from gpiozero import Button; \
	import signal; \
	switch = Button(17, bounce_time=0.01); \
	print('Switch configured with 10ms debounce'); \
	print('Waiting for presses...'); \
	press_count = 0; \
	def count(): \
	    global press_count; \
	    press_count += 1; \
	    print(f'Press detected! Count: {press_count}'); \
	switch.when_pressed = count; \
	try: \
	    signal.pause(); \
	except KeyboardInterrupt: \
	    print(f'\\nTotal presses: {press_count}'); \
	finally: \
	    switch.close()"

# Simple press counter
counter:
	@echo "Button Press Counter"
	@echo "=================="
	@echo "Press the button to increment counter"
	@echo "Press Ctrl+C to see total"
	@python3 -c "from gpiozero import Button, LED; \
	import signal; \
	switch = Button(17, bounce_time=0.01); \
	try: led = LED(18); has_led = True; \
	except: has_led = False; \
	count = 0; \
	def increment(): \
	    global count; \
	    count += 1; \
	    print(f'\\rCount: {count:4d}', end=''); \
	    if has_led: led.blink(0.1, 0.1, n=1); \
	switch.when_pressed = increment; \
	print('Count:    0', end=''); \
	try: \
	    signal.pause(); \
	except KeyboardInterrupt: \
	    print(f'\\n\\nFinal count: {count}'); \
	finally: \
	    switch.close(); \
	    if has_led: led.close()"

# Reaction time game
game:
	@echo "Reaction Time Game!"
	@echo "=================="
	@echo "Press the button as fast as possible when prompted"
	@python3 -c "from gpiozero import Button, LED; \
	import time, random; \
	switch = Button(17, bounce_time=0.01); \
	try: led = LED(18); has_led = True; \
	except: has_led = False; \
	total_time = 0; \
	for round in range(3): \
	    print(f'\\nRound {round+1}/3'); \
	    print('Get ready...'); \
	    time.sleep(random.uniform(2, 5)); \
	    if has_led: led.on(); \
	    print('PRESS NOW!'); \
	    start = time.time(); \
	    switch.wait_for_press(); \
	    reaction = time.time() - start; \
	    if has_led: led.off(); \
	    print(f'Reaction time: {reaction*1000:.0f}ms'); \
	    total_time += reaction; \
	    time.sleep(1); \
	avg_time = total_time / 3; \
	print(f'\\nAverage: {avg_time*1000:.0f}ms'); \
	if avg_time < 0.2: print('Excellent!'); \
	elif avg_time < 0.3: print('Good!'); \
	else: print('Keep practicing!'); \
	switch.close(); \
	if has_led: led.close()"

# Morse code demo
morse:
	@echo "Morse Code Input"
	@echo "================"
	@echo "Short press = dot (.)"
	@echo "Long press = dash (-)"
	@echo "Common letters:"
	@echo "  E: .     T: -"
	@echo "  A: .-    N: -."
	@echo "  I: ..    M: --"
	@echo "  S: ...   O: ---"
	@echo ""
	@echo "Press button to input code"
	@echo "Wait 2 seconds between letters"
	@echo "Press Ctrl+C to exit"
	@python3 -c "from gpiozero import Button; \
	import time, signal; \
	switch = Button(17, bounce_time=0.01); \
	morse = {'.-':'A', '-...':'B', '-.-.':'C', '-..':'D', '.':'E', \
	         '..-.':'F', '--.':'G', '....':'H', '..':'I', '.---':'J', \
	         '-.-':'K', '.-..':'L', '--':'M', '-.':'N', '---':'O', \
	         '.--.':'P', '--.-':'Q', '.-.':'R', '...':'S', '-':'T', \
	         '..-':'U', '...-':'V', '.--':'W', '-..-':'X', '-.--':'Y', \
	         '--..':'Z'}; \
	code = ''; \
	last_time = 0; \
	def process_press(): \
	    global code, last_time; \
	    current = time.time(); \
	    if current - last_time > 2 and code: \
	        if code in morse: \
	            print(f' = {morse[code]}'); \
	        else: \
	            print(f' = Unknown: {code}'); \
	        code = ''; \
	    press_start = time.time(); \
	    switch.wait_for_release(); \
	    duration = time.time() - press_start; \
	    if duration < 0.3: \
	        code += '.'; \
	        print('.', end='', flush=True); \
	    else: \
	        code += '-'; \
	        print('-', end='', flush=True); \
	    last_time = time.time(); \
	switch.when_pressed = process_press; \
	print('Start typing Morse code:'); \
	try: \
	    signal.pause(); \
	except KeyboardInterrupt: \
	    if code and code in morse: \
	        print(f' = {morse[code]}'); \
	finally: \
	    switch.close(); \
	    print('\\nGoodbye!')"

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
	@echo "Micro Switch Input Examples"
	@echo "=========================="
	@echo "Available targets:"
	@echo "  make run     - Run interactive demos menu"
	@echo "  make test    - Test switch detection"
	@echo "  make counter - Simple press counter"
	@echo "  make game    - Reaction time game"
	@echo "  make morse   - Morse code input demo"
	@echo "  make deps    - Install dependencies"
	@echo "  make clean   - Clean build files"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "Circuit connections:"
	@echo "  Switch pin 1 -> GPIO17 (Pin 11)"
	@echo "  Switch pin 2 -> GND (Pin 9)"
	@echo "  LED anode    -> GPIO18 (Pin 12) [optional]"
	@echo "  LED cathode  -> 220Ω -> GND"
	@echo ""
	@echo "Note: GPIO17 uses internal pull-up resistor"