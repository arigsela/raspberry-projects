#!/usr/bin/env python3
"""
PIR Security System with Multiple Zones
Advanced motion detection with logging and alert levels
"""

from gpiozero import MotionSensor, RGBLED, Buzzer, Button
from time import sleep, time
from datetime import datetime
import signal
import sys
import os

# GPIO Configuration
PIR_PIN = 17
RGB_RED_PIN = 18
RGB_GREEN_PIN = 27
RGB_BLUE_PIN = 22
BUZZER_PIN = 23
ARM_BUTTON_PIN = 24

# System states
STATE_DISARMED = 0
STATE_ARMING = 1
STATE_ARMED = 2
STATE_TRIGGERED = 3

# LED Colors for states
COLORS = {
    STATE_DISARMED: (0, 1, 0),    # Green - disarmed
    STATE_ARMING: (1, 0.5, 0),    # Orange - arming
    STATE_ARMED: (0, 0, 1),       # Blue - armed
    STATE_TRIGGERED: (1, 0, 0)    # Red - triggered
}

# Configuration
ARM_DELAY = 10  # Seconds to leave after arming
TRIGGER_DELAY = 5  # Seconds before full alarm
LOG_FILE = "security_log.txt"

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nShutting down security system...")
    sys.exit(0)

def log_event(event):
    """Log security events to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event}\n"
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
    
    print(log_entry.strip())

class SecuritySystem:
    def __init__(self):
        """Initialize security system components"""
        self.pir = MotionSensor(PIR_PIN, queue_len=3)
        self.led = RGBLED(red=RGB_RED_PIN, green=RGB_GREEN_PIN, blue=RGB_BLUE_PIN)
        self.buzzer = Buzzer(BUZZER_PIN)
        self.arm_button = Button(ARM_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        self.state = STATE_DISARMED
        self.arm_time = None
        self.trigger_time = None
        self.motion_count = 0
        
        # Set up button handler
        self.arm_button.when_pressed = self.toggle_arm_state
        
        # Set initial LED state
        self.update_led()
        
        log_event("Security system initialized")
    
    def update_led(self):
        """Update LED color based on system state"""
        self.led.color = COLORS[self.state]
    
    def toggle_arm_state(self):
        """Toggle between armed and disarmed states"""
        if self.state == STATE_DISARMED:
            self.start_arming()
        elif self.state == STATE_ARMED:
            self.disarm()
        elif self.state == STATE_TRIGGERED:
            self.disarm()
    
    def start_arming(self):
        """Begin arming sequence"""
        self.state = STATE_ARMING
        self.update_led()
        self.arm_time = time() + ARM_DELAY
        log_event(f"Arming system - {ARM_DELAY} seconds to exit")
        
        # Beep during arming
        for i in range(ARM_DELAY):
            self.buzzer.beep(on_time=0.1, off_time=0.9, n=1)
            sleep(1)
            
            # Check if disarmed during countdown
            if self.state != STATE_ARMING:
                return
        
        # Complete arming
        if self.state == STATE_ARMING:
            self.state = STATE_ARMED
            self.update_led()
            self.buzzer.beep(on_time=0.5, off_time=0, n=1)
            log_event("System ARMED")
    
    def disarm(self):
        """Disarm the system"""
        was_triggered = self.state == STATE_TRIGGERED
        self.state = STATE_DISARMED
        self.update_led()
        self.buzzer.off()
        self.trigger_time = None
        
        if was_triggered:
            log_event("System DISARMED - Alarm stopped")
        else:
            log_event("System DISARMED")
    
    def motion_detected(self):
        """Handle motion detection based on system state"""
        self.motion_count += 1
        
        if self.state == STATE_ARMED:
            if self.trigger_time is None:
                self.trigger_time = time()
                log_event(f"MOTION DETECTED! Alarm in {TRIGGER_DELAY} seconds")
                
                # Warning beeps before full alarm
                for i in range(TRIGGER_DELAY):
                    if self.state != STATE_ARMED:
                        return
                    
                    self.led.blink(on_time=0.2, off_time=0.2, n=2)
                    self.buzzer.beep(on_time=0.2, off_time=0.3, n=2)
                    sleep(1)
                
                # Trigger full alarm if still armed
                if self.state == STATE_ARMED:
                    self.trigger_alarm()
        
        elif self.state == STATE_DISARMED:
            # Just log motion when disarmed
            log_event(f"Motion detected (system disarmed) - Total: {self.motion_count}")
    
    def trigger_alarm(self):
        """Activate full alarm"""
        self.state = STATE_TRIGGERED
        self.update_led()
        log_event("ALARM TRIGGERED!")
        
        # Continuous alarm
        self.buzzer.on()
        self.led.blink(on_time=0.5, off_time=0.5)
    
    def run(self):
        """Main system loop"""
        print("\nPIR Security System")
        print("==================")
        print(f"Log file: {LOG_FILE}")
        print("\nControls:")
        print("- Press button to arm/disarm")
        print("- Blue LED = Armed")
        print("- Green LED = Disarmed")
        print("- Red LED = Triggered")
        print("\nWaiting for PIR to stabilize...")
        
        # PIR warm-up
        self.led.pulse(fade_in_time=1, fade_out_time=1)
        sleep(5)
        self.led.color = COLORS[STATE_DISARMED]
        
        print("System ready!\n")
        
        # Attach motion handler
        self.pir.when_motion = self.motion_detected
        
        # Main loop for status updates
        try:
            while True:
                sleep(10)
                
                # Print status
                status = ["DISARMED", "ARMING", "ARMED", "TRIGGERED"][self.state]
                motion_status = "Motion" if self.pir.motion_detected else "Clear"
                print(f"Status: {status} | {motion_status} | Events: {self.motion_count}")
                
        except KeyboardInterrupt:
            self.disarm()
            log_event("System shutdown")

def main():
    """Initialize and run security system"""
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w') as f:
            f.write("=== PIR Security System Log ===\n")
    
    # Run security system
    system = SecuritySystem()
    system.run()

if __name__ == "__main__":
    main()