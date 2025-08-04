# Makefile for Passive Buzzer project

.PHONY: all run scale melody effects test deps clean help

# Default target
all: help

# Run the passive buzzer examples
run:
	@echo "Starting Passive Buzzer Examples..."
	@echo "Buzzer connected to GPIO18 (Pin 12) - PWM0"
	@echo "Select example from menu"
	@echo "Press Ctrl+C to stop"
	@python3 passive-buzzer.py

# Play a musical scale
scale:
	@echo "Playing C Major Scale..."
	@python3 -c "from gpiozero import PWMOutputDevice; \
	import time; \
	buzzer = PWMOutputDevice(18); \
	notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]; \
	print('C D E F G A B C'); \
	for freq in notes: \
	    buzzer.frequency = freq; \
	    buzzer.value = 0.5; \
	    time.sleep(0.3); \
	    buzzer.value = 0; \
	    time.sleep(0.05); \
	buzzer.close(); \
	print('Scale complete!')"

# Play a simple melody
melody:
	@echo "Playing 'Mary Had a Little Lamb'..."
	@python3 -c "from gpiozero import PWMOutputDevice; \
	import time; \
	buzzer = PWMOutputDevice(18); \
	notes = {'E': 329.63, 'D': 293.66, 'C': 261.63, 'G': 392.00}; \
	melody = [('E',0.5),('D',0.5),('C',0.5),('D',0.5),('E',0.5),('E',0.5),('E',1.0), \
	         ('D',0.5),('D',0.5),('D',1.0),('E',0.5),('G',0.5),('G',1.0)]; \
	for note, dur in melody: \
	    buzzer.frequency = notes[note]; \
	    buzzer.value = 0.5; \
	    time.sleep(dur * 0.8); \
	    buzzer.value = 0; \
	    time.sleep(dur * 0.2); \
	buzzer.close(); \
	print('Melody complete!')"

# Sound effects demo
effects:
	@echo "Sound Effects Demo..."
	@python3 -c "from gpiozero import PWMOutputDevice; \
	import time; \
	buzzer = PWMOutputDevice(18); \
	print('1. Siren'); \
	for _ in range(2): \
	    for freq in range(400, 800, 20): \
	        buzzer.frequency = freq; buzzer.value = 0.5; time.sleep(0.01); \
	    for freq in range(800, 400, -20): \
	        buzzer.frequency = freq; buzzer.value = 0.5; time.sleep(0.01); \
	buzzer.value = 0; \
	time.sleep(0.5); \
	print('2. Laser'); \
	for freq in range(2000, 100, -50): \
	    buzzer.frequency = freq; buzzer.value = 0.5; time.sleep(0.01); \
	buzzer.value = 0; \
	buzzer.close(); \
	print('Effects complete!')"

# Test buzzer with 440Hz tone
test:
	@echo "Testing passive buzzer with A4 (440Hz) tone..."
	@python3 -c "from gpiozero import PWMOutputDevice; \
	import time; \
	buzzer = PWMOutputDevice(18); \
	print('Playing 440Hz tone for 1 second...'); \
	buzzer.frequency = 440; \
	buzzer.value = 0.5; \
	time.sleep(1); \
	buzzer.value = 0; \
	buzzer.close(); \
	print('If you heard a musical note, the buzzer is working!')"

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
	@echo "Passive Buzzer Music Project"
	@echo "============================"
	@echo "Available targets:"
	@echo "  make run     - Run interactive buzzer examples"
	@echo "  make scale   - Play C major scale"
	@echo "  make melody  - Play simple melody"
	@echo "  make effects - Sound effects demo"
	@echo "  make test    - Test with 440Hz tone"
	@echo "  make deps    - Install dependencies"
	@echo "  make clean   - Clean build files"
	@echo "  make help    - Show this help message"
	@echo ""
	@echo "Passive Buzzer Wiring:"
	@echo "  Buzzer (+) -> GPIO18 (Pin 12) - PWM0"
	@echo "  Buzzer (-) -> GND (Pin 14)"
	@echo ""
	@echo "Note: Passive buzzers require PWM signal"
	@echo "      They can play different frequencies/notes"
	@echo "      GPIO18 is hardware PWM capable"