# Makefile for Photoresistor project

.PHONY: all run test nightlight logger alarm deps clean help

# Default target
all: help

# Run the photoresistor examples
run:
	@echo "Starting Photoresistor Examples..."
	@echo "Using MCP3008 ADC on SPI0"
	@echo "Photoresistor on channel 0"
	@echo "Select example from menu"
	@echo "Press Ctrl+C to stop"
	@python3 photoresistor.py

# Test photoresistor connection
test:
	@echo "Testing photoresistor connection..."
	@python3 -c "from gpiozero import MCP3008; \
	import time; \
	try: \
	    ldr = MCP3008(channel=0); \
	    print('Photoresistor detected!'); \
	    print('Cover/uncover the sensor to test...'); \
	    for i in range(10): \
	        value = ldr.value; \
	        level = 'DARK' if value < 0.3 else 'NORMAL' if value < 0.7 else 'BRIGHT'; \
	        bar = '█' * int(value * 20) + '░' * (20 - int(value * 20)); \
	        print(f'[{bar}] {value*100:5.1f}% - {level}'); \
	        time.sleep(0.5); \
	    print('Test successful!'); \
	except Exception as e: \
	    print(f'Error: {e}'); \
	    print('Check SPI is enabled and wiring is correct')"

# Automatic night light demo
nightlight:
	@echo "Automatic Night Light Demo..."
	@echo "Connect LED to GPIO17"
	@echo "LED will turn on in darkness"
	@python3 -c "from gpiozero import MCP3008, LED; \
	import time; \
	ldr = MCP3008(0); \
	led = LED(17); \
	print('Press Ctrl+C to stop'); \
	threshold = 0.3; \
	try: \
	    while True: \
	        light = ldr.value; \
	        if light < threshold: \
	            led.on(); \
	            status = 'ON '; \
	        else: \
	            led.off(); \
	            status = 'OFF'; \
	        print(f'\\rLight: {light*100:5.1f}% | LED: {status}', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    pass; \
	finally: \
	    led.close(); \
	    print('\\nDemo stopped')"

# Light level logger
logger:
	@echo "Light Level Logger (30 seconds)..."
	@python3 -c "from gpiozero import MCP3008; \
	import time; \
	ldr = MCP3008(0); \
	data = []; \
	print('Logging for 30 seconds...'); \
	start = time.time(); \
	while time.time() - start < 30: \
	    value = ldr.value; \
	    data.append(value); \
	    print(f'\\rSamples: {len(data)} | Current: {value*100:5.1f}%', end=''); \
	    time.sleep(0.5); \
	print(f'\\n\\nSummary:'); \
	print(f'Samples: {len(data)}'); \
	print(f'Average: {sum(data)/len(data)*100:.1f}%'); \
	print(f'Min: {min(data)*100:.1f}%'); \
	print(f'Max: {max(data)*100:.1f}%')"

# Light change alarm
alarm:
	@echo "Light Change Alarm..."
	@echo "Connect buzzer to GPIO22 (optional)"
	@echo "Alerts on sudden light changes"
	@python3 -c "from gpiozero import MCP3008, Buzzer; \
	import time; \
	ldr = MCP3008(0); \
	try: buzzer = Buzzer(22); \
	except: buzzer = None; print('No buzzer connected'); \
	last = ldr.value; \
	threshold = 0.3; \
	print('Press Ctrl+C to stop'); \
	try: \
	    while True: \
	        current = ldr.value; \
	        change = abs(current - last); \
	        if change > threshold: \
	            print(f'\\n⚠️  ALERT! Light changed by {change*100:.1f}%'); \
	            if buzzer: buzzer.beep(0.1, 0.1, n=3); \
	        last = current; \
	        bar = '█' * int(current * 20) + '░' * (20 - int(current * 20)); \
	        print(f'\\r[{bar}] {current*100:5.1f}%', end=''); \
	        time.sleep(0.1); \
	except KeyboardInterrupt: \
	    pass; \
	finally: \
	    if buzzer: buzzer.close(); \
	    print('\\nAlarm stopped')"

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
	@echo "Photoresistor Light Sensor Project"
	@echo "=================================="
	@echo "Available targets:"
	@echo "  make run        - Run interactive examples"
	@echo "  make test       - Test photoresistor"
	@echo "  make nightlight - Automatic night light demo"
	@echo "  make logger     - Log light levels (30s)"
	@echo "  make alarm      - Light change alarm"
	@echo "  make deps       - Install dependencies"
	@echo "  make clean      - Clean build files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Photoresistor Circuit:"
	@echo "  3.3V → 10kΩ → Junction → MCP3008 CH0"
	@echo "                   ↓"
	@echo "                  LDR"
	@echo "                   ↓"
	@echo "                  GND"
	@echo ""
	@echo "MCP3008 connections same as potentiometer project"