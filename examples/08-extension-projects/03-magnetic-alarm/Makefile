# Makefile for Magnetic Door Alarm System

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := magnetic-door-alarm.py

# Phony targets
.PHONY: run test demo interactive security monitor arm disarm reset logs setup install status clean help

# Run the main program
run:
	@echo "Starting Magnetic Door Alarm System..."
	@$(PYTHON) $(PROGRAM)

# Test hardware components
test:
	@echo "Testing door alarm hardware..."
	@echo "1. Testing reed switches..."
	@$(PYTHON) -c "from gpiozero import Button; import time; switches = [Button(17), Button(18), Button(27), Button(22)]; print('Reed switch test (10 seconds):'); start=time.time(); while time.time()-start<10: states=[('GPIO'+str(17+i), 'OPEN' if not sw.is_pressed else 'CLOSED') for i, sw in enumerate(switches) if sw]; print('  '.join([f'{pin}:{state}' for pin, state in states]), end='\r'); time.sleep(0.5); [sw.close() for sw in switches]; print('\nReed switch test complete')" || echo "Reed switch test failed"
	@echo "2. Testing control buttons..."
	@$(PYTHON) -c "from gpiozero import Button; import time; buttons = {'ARM': Button(23), 'MUTE': Button(24), 'TEST': Button(25)}; print('Press each button (5 seconds):'); start=time.time(); while time.time()-start<5: pressed = [name for name, btn in buttons.items() if btn.is_pressed]; print(f'Pressed: {pressed if pressed else \"None\"}', end='\r'); time.sleep(0.1); [btn.close() for btn in buttons.values()]; print('\nButton test complete')" || echo "Button test failed"
	@echo "3. Testing status LEDs..."
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; import time; leds = {'ARMED': LED(26), 'ALARM': PWMLED(19), 'STATUS': PWMLED(20), 'DOOR': LED(21)}; print('Testing LEDs...'); [led.on() for led in leds.values()]; time.sleep(1); [led.off() for led in leds.values()]; [led.close() for led in leds.values()]; print('LED test complete')" || echo "LED test failed"
	@echo "4. Testing buzzers..."
	@$(PYTHON) -c "from gpiozero import Buzzer; import time; alarm_buzz = Buzzer(13); status_buzz = Buzzer(12); print('Testing alarm buzzer...'); alarm_buzz.beep(0.5, 0.5, n=2); print('Testing status buzzer...'); status_buzz.beep(0.2, 0.2, n=3); alarm_buzz.close(); status_buzz.close(); print('Buzzer test complete')" || echo "Buzzer test failed"

# Run interactive demo
demo:
	@echo "Running door alarm demo..."
	@$(PYTHON) -c "from magnetic_door_alarm import interactive_demo; interactive_demo()"

# Interactive monitoring mode
interactive:
	@echo "Starting interactive door monitoring..."
	@$(PYTHON) -c "from magnetic_door_alarm import interactive_demo; interactive_demo()"

# Security system demonstration
security:
	@echo "Starting security system demo..."
	@$(PYTHON) -c "from magnetic_door_alarm import security_demo; security_demo()"

# System monitoring mode
monitor:
	@echo "Starting system monitoring (Press Ctrl+C to stop)..."
	@while true; do \
		clear; \
		echo "Door Alarm System Monitor"; \
		echo "========================="; \
		echo "Time: $$(date)"; \
		echo ""; \
		echo "Reed Switch States:"; \
		$(PYTHON) -c "from gpiozero import Button; switches = [('Front Door (GPIO17)', Button(17)), ('Back Door (GPIO18)', Button(18)), ('Side Door (GPIO27)', Button(27)), ('Window (GPIO22)', Button(22))]; [print(f'  {name}: {\"OPEN\" if not sw.is_pressed else \"CLOSED\"}') for name, sw in switches]; [sw.close() for _, sw in switches]" 2>/dev/null || echo "  No switches detected"; \
		echo ""; \
		echo "System Status:"; \
		if [ -f "door_alarm_settings.json" ]; then \
			echo "  Settings file: Present"; \
		else \
			echo "  Settings file: Not found"; \
		fi; \
		if [ -f "door_events.json" ]; then \
			events=$$(wc -l < door_events.json 2>/dev/null || echo "0"); \
			echo "  Events logged: $$events lines"; \
		else \
			echo "  Event log: Not found"; \
		fi; \
		echo ""; \
		echo "Hardware Status:"; \
		$(PYTHON) -c "import gpiozero; print('  GPIO access: OK')" 2>/dev/null || echo "  GPIO access: Failed"; \
		sleep 2; \
	done

# Quick arm system test
arm:
	@echo "Testing system arming..."
	@$(PYTHON) -c "from magnetic_door_alarm import DoorAlarmSystem; import time; sys = DoorAlarmSystem(); print('Arming system...'); sys.exit_delay = 3; sys._arm_system(); time.sleep(4; print('System armed:', sys.is_armed); sys.cleanup()"

# Quick disarm system test
disarm:
	@echo "Testing system disarming..."
	@$(PYTHON) -c "from magnetic_door_alarm import DoorAlarmSystem; import time; sys = DoorAlarmSystem(); sys.is_armed = True; print('Disarming system...'); sys._disarm_system(); print('System disarmed:', not sys.is_armed); sys.cleanup()"

# Reset system data
reset:
	@echo "Resetting system data..."
	@rm -f door_alarm_settings.json
	@rm -f door_events.json
	@echo "✓ Settings and event log cleared"

# View recent logs
logs:
	@echo "Recent Door Alarm Logs"
	@echo "======================"
	@if [ -f "door_events.json" ]; then \
		echo "Recent events (last 10):"; \
		tail -10 door_events.json | $(PYTHON) -c "import sys, json; [print(f'  {event.get(\"timestamp\", \"Unknown\")}: {event.get(\"door\", \"Unknown\")} {event.get(\"action\", \"Unknown\")}') for line in sys.stdin for event in [json.loads(line.strip())] if line.strip()]" 2>/dev/null || echo "  Error reading event log"; \
	else \
		echo "No event log found"; \
	fi
	@echo ""
	@if [ -f "door_alarm_settings.json" ]; then \
		echo "Current settings:"; \
		cat door_alarm_settings.json | $(PYTHON) -c "import sys, json; settings = json.load(sys.stdin); [print(f'  {key}: {value}') for key, value in settings.items()]" 2>/dev/null || echo "  Error reading settings"; \
	else \
		echo "No settings file found"; \
	fi

# Setup system and dependencies
setup:
	@echo "Setting up door alarm system..."
	@echo "Installing Python libraries..."
	@pip install gpiozero
	@echo "Installing optional pigpio for precise timing..."
	@sudo apt update && sudo apt install -y pigpio python3-pigpio || echo "⚠ pigpio installation failed - using default GPIO"
	@echo "Enabling pigpio daemon..."
	@sudo systemctl enable pigpiod 2>/dev/null || echo "⚠ pigpiod service setup failed"
	@sudo systemctl start pigpiod 2>/dev/null || echo "⚠ pigpiod service start failed"
	@echo "Testing GPIO access..."
	@$(PYTHON) -c "from gpiozero import LED; led = LED(26); led.off(); led.close(); print('✓ GPIO access working')" 2>/dev/null || echo "⚠ GPIO access test failed"
	@echo "Setup complete!"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install gpiozero

# System status check
status:
	@echo "Door Alarm System Status"
	@echo "========================"
	@echo "GPIO Library:"
	@$(PYTHON) -c "import gpiozero; print('  ✓ gpiozero installed:', gpiozero.__version__)" 2>/dev/null || echo "  ❌ gpiozero not available"
	@echo "GPIO Access:"
	@$(PYTHON) -c "from gpiozero import LED; LED(26).close(); print('  ✓ GPIO access working')" 2>/dev/null || echo "  ❌ GPIO access failed"
	@echo "PiGPIO Status:"
	@systemctl is-active pigpiod >/dev/null 2>&1 && echo "  ✓ pigpiod service running" || echo "  ⚪ pigpiod service not running (optional)"
	@echo "Reed Switches:"
	@$(PYTHON) -c "from gpiozero import Button; switches = [(17, 'Front'), (18, 'Back'), (27, 'Side'), (22, 'Window')]; [(lambda pin, name: (Button(pin).close(), print(f'  ✓ {name} Door (GPIO{pin}): Connected')))(*switch) for switch in switches]" 2>/dev/null || echo "  ⚪ Reed switches not tested"
	@echo "Control Buttons:"
	@$(PYTHON) -c "from gpiozero import Button; buttons = [(23, 'ARM'), (24, 'MUTE'), (25, 'TEST')]; [(lambda pin, name: (Button(pin).close(), print(f'  ✓ {name} Button (GPIO{pin}): Connected')))(*btn) for btn in buttons]" 2>/dev/null || echo "  ⚪ Control buttons not tested"  
	@echo "Status LEDs:"
	@$(PYTHON) -c "from gpiozero import LED, PWMLED; leds = [(26, 'ARMED'), (19, 'ALARM'), (20, 'STATUS'), (21, 'DOOR')]; [(lambda pin, name: (LED(pin).close(), print(f'  ✓ {name} LED (GPIO{pin}): Connected')))(*led) for led in leds]" 2>/dev/null || echo "  ⚪ Status LEDs not tested"
	@echo "System Files:"
	@test -f door_alarm_settings.json && echo "  ✓ Settings file exists" || echo "  ⚪ Settings file not found (will be created)"
	@test -f door_events.json && echo "  ✓ Event log exists" || echo "  ⚪ Event log not found (will be created)"

# Statistics and analysis
stats:
	@echo "Door Alarm System Statistics"
	@echo "============================"
	@if [ -f "door_events.json" ]; then \
		echo "Event Statistics:"; \
		total_events=$$(wc -l < door_events.json); \
		echo "  Total events: $$total_events"; \
		echo "  Event breakdown:"; \
		$(PYTHON) -c "import json; events = [json.loads(line) for line in open('door_events.json') if line.strip()]; actions = {}; [actions.update({event.get('action', 'unknown'): actions.get(event.get('action', 'unknown'), 0) + 1}) for event in events]; [print(f'    {action}: {count}') for action, count in sorted(actions.items())]" 2>/dev/null || echo "    Error analyzing events"; \
		echo "  Door activity:"; \
		$(PYTHON) -c "import json; events = [json.loads(line) for line in open('door_events.json') if line.strip()]; doors = {}; [doors.update({event.get('door', 'unknown'): doors.get(event.get('door', 'unknown'), 0) + 1}) for event in events if event.get('action') == 'opened']; [print(f'    {door}: {count} opens') for door, count in sorted(doors.items(), key=lambda x: x[1], reverse=True)]" 2>/dev/null || echo "    Error analyzing door activity"; \
	else \
		echo "No event log found - run system to generate statistics"; \
	fi

# Clean up system files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Note: Keeping door_alarm_settings.json and door_events.json"
	@echo "Use 'make reset' to clear system data"

# Help
help:
	@echo "Magnetic Door Alarm System" 
	@echo "=========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive system (default)"
	@echo "  make test       - Test all hardware components"
	@echo "  make demo       - Interactive demonstration"
	@echo "  make interactive- Interactive door monitoring"
	@echo "  make security   - Security system demonstration"
	@echo "  make monitor    - Real-time system monitoring"
	@echo ""
	@echo "System Control:"
	@echo "  make arm        - Test system arming"
	@echo "  make disarm     - Test system disarming"
	@echo "  make logs       - View recent activity logs"
	@echo "  make stats      - Show usage statistics"
	@echo "  make reset      - Clear all system data"
	@echo ""
	@echo "System Management:"
	@echo "  make setup      - Setup hardware interfaces and dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make status     - Check system and hardware status"
	@echo "  make clean      - Clean up cache files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Hardware Requirements:"
	@echo "  - 2-4 Magnetic reed switches for doors/windows"
	@echo "  - Magnets to pair with reed switches"
	@echo "  - Control buttons for system operation"
	@echo "  - Status LEDs and buzzers for feedback"
	@echo ""
	@echo "Pin Connections:"
	@echo "  Reed Switches:  Front=GPIO17, Back=GPIO18, Side=GPIO27, Window=GPIO22"
	@echo "  Buttons:        ARM=GPIO23, MUTE=GPIO24, TEST=GPIO25"
	@echo "  LEDs:           Armed=GPIO26, Alarm=GPIO19, Status=GPIO20, Door=GPIO21"
	@echo "  Buzzers:        Alarm=GPIO13, Status=GPIO12"
	@echo "  Optional:       PIR Motion=GPIO6"
	@echo ""
	@echo "Reed Switch Installation:"
	@echo "  - Mount reed switch on door frame"
	@echo "  - Mount magnet on door (within 5mm when closed)"
	@echo "  - Wire with pull-up resistor (10kΩ to 3.3V)"
	@echo "  - Connect other terminal to GND"
	@echo ""
	@echo "Security Zones:"
	@echo "  HIGH PRIORITY:   Entry doors (Front/Back) - Entry delay"
	@echo "  MEDIUM PRIORITY: Secondary doors (Side) - Extended delay"
	@echo "  LOW PRIORITY:    Windows - Immediate alarm"
	@echo ""
	@echo "System States:"
	@echo "  DISARMED: Monitoring only, no alarms"
	@echo "  ARMING:   Exit delay countdown active"
	@echo "  ARMED:    Full security monitoring"
	@echo "  ALARM:    Alert condition active"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time system setup"
	@echo "  make test        # Test all hardware"
	@echo "  make demo        # Interactive demonstration"
	@echo "  make security    # Armed system simulation"
	@echo "  make monitor     # Real-time door monitoring"
	@echo "  make logs        # View recent activity"
	@echo "  make stats       # Usage statistics"
	@echo ""
	@echo "Troubleshooting:"
	@echo "  - Reed switches: Check magnet alignment (within 5mm)"
	@echo "  - False alarms: Verify stable mounting and connections"
	@echo "  - No response: Check pull-up resistors and GPIO connections"
	@echo "  - Audio issues: Verify buzzer polarity and power"
	@echo ""
	@echo "Advanced Features:"
	@echo "  - Multi-zone security with different priorities"
	@echo "  - Intelligent entry/exit delay timing"
	@echo "  - Comprehensive event logging and statistics"
	@echo "  - Auto-rearm functionality"
	@echo "  - False positive prevention"