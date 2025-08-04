#!/usr/bin/env python3
"""
Relay Control
Switch high-power devices on/off using relay modules
"""

from gpiozero import OutputDevice, Button, MotionSensor
import time
import signal
import sys
from datetime import datetime, timedelta

# GPIO Configuration
RELAY_1_PIN = 17  # Single relay or relay 1 of multi-channel
RELAY_2_PIN = 18  # Relay 2 (if using multi-channel)
RELAY_3_PIN = 27  # Relay 3
RELAY_4_PIN = 22  # Relay 4

# Input devices for automation (optional)
BUTTON_PIN = 23
PIR_PIN = 24
TEMP_THRESHOLD = 25  # Temperature threshold for demos

# Note: Some relay modules are "active low" (relay ON when GPIO is LOW)
# Set active_high=False if your relay works opposite to expected
ACTIVE_HIGH = True  # Set to False for active-low relay modules

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class RelayController:
    """Control a relay module"""
    
    def __init__(self, pin, name="Relay", active_high=True):
        """Initialize relay controller
        
        Args:
            pin: GPIO pin connected to relay
            name: Descriptive name for the relay
            active_high: True if relay activates on HIGH signal
        """
        self.relay = OutputDevice(pin, active_high=active_high)
        self.name = name
        self.state = False
    
    def on(self):
        """Turn relay ON"""
        self.relay.on()
        self.state = True
        print(f"{self.name} ON")
    
    def off(self):
        """Turn relay OFF"""
        self.relay.off()
        self.state = False
        print(f"{self.name} OFF")
    
    def toggle(self):
        """Toggle relay state"""
        if self.state:
            self.off()
        else:
            self.on()
    
    def pulse(self, on_time=1.0):
        """Turn on for specified time then off"""
        self.on()
        time.sleep(on_time)
        self.off()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.relay.close()

def basic_relay_control():
    """Basic relay on/off control"""
    print("\n=== Basic Relay Control ===")
    print("Testing relay switching...")
    
    relay = RelayController(RELAY_1_PIN, "Relay 1", ACTIVE_HIGH)
    
    try:
        # Simple on/off
        print("\nTurning relay ON")
        relay.on()
        time.sleep(2)
        
        print("Turning relay OFF")
        relay.off()
        time.sleep(1)
        
        # Multiple pulses
        print("\nPulsing relay 3 times")
        for i in range(3):
            print(f"Pulse {i+1}")
            relay.pulse(0.5)
            time.sleep(0.5)
        
        # Toggle demo
        print("\nToggle demonstration")
        for i in range(4):
            relay.toggle()
            time.sleep(1)
        
    finally:
        relay.cleanup()

def timer_control():
    """Timer-based relay control"""
    print("\n=== Timer Control ===")
    
    relay = RelayController(RELAY_1_PIN, "Timed Device", ACTIVE_HIGH)
    
    try:
        # Get timer duration
        minutes = input("Enter timer duration in minutes (default 1): ")
        minutes = float(minutes) if minutes else 1.0
        seconds = minutes * 60
        
        print(f"\nDevice will run for {minutes} minutes")
        print("Starting timer...")
        
        relay.on()
        start_time = time.time()
        
        # Countdown display
        while True:
            elapsed = time.time() - start_time
            remaining = seconds - elapsed
            
            if remaining <= 0:
                break
            
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            print(f"\rTime remaining: {mins:02d}:{secs:02d}", end='')
            
            time.sleep(0.1)
        
        print("\n\nTimer expired!")
        relay.off()
        
    except KeyboardInterrupt:
        print("\n\nTimer cancelled")
        relay.off()
    finally:
        relay.cleanup()

def scheduled_control():
    """Schedule relay on/off times"""
    print("\n=== Scheduled Control ===")
    print("Schedule relay to turn on/off at specific times")
    
    relay = RelayController(RELAY_1_PIN, "Scheduled Device", ACTIVE_HIGH)
    
    try:
        # Simple schedule (on for X seconds every Y seconds)
        on_duration = float(input("ON duration in seconds (default 5): ") or "5")
        off_duration = float(input("OFF duration in seconds (default 10): ") or "10")
        cycles = int(input("Number of cycles (default 5): ") or "5")
        
        print(f"\nSchedule: ON for {on_duration}s, OFF for {off_duration}s")
        print(f"Running {cycles} cycles...")
        
        for cycle in range(cycles):
            print(f"\nCycle {cycle + 1}/{cycles}")
            
            # ON period
            relay.on()
            for i in range(int(on_duration)):
                print(f"\rON: {i+1}/{int(on_duration)}s", end='')
                time.sleep(1)
            
            # OFF period
            relay.off()
            if cycle < cycles - 1:  # Skip last OFF period
                for i in range(int(off_duration)):
                    print(f"\rOFF: {i+1}/{int(off_duration)}s", end='')
                    time.sleep(1)
        
        print("\n\nSchedule complete!")
        
    except KeyboardInterrupt:
        print("\n\nSchedule cancelled")
    finally:
        relay.off()
        relay.cleanup()

def button_control():
    """Control relay with button"""
    print("\n=== Button Control ===")
    print("Press button to toggle relay")
    print("Press Ctrl+C to exit")
    
    relay = RelayController(RELAY_1_PIN, "Button-Controlled Device", ACTIVE_HIGH)
    
    try:
        button = Button(BUTTON_PIN)
        
        # Toggle on button press
        button.when_pressed = relay.toggle
        
        # Keep running
        signal.pause()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure button is connected to GPIO23")
    finally:
        relay.cleanup()

def motion_activated():
    """Motion-activated relay control"""
    print("\n=== Motion-Activated Control ===")
    print("Relay activates on motion detection")
    print("Press Ctrl+C to exit")
    
    relay = RelayController(RELAY_1_PIN, "Motion Light", ACTIVE_HIGH)
    
    try:
        pir = MotionSensor(PIR_PIN)
        
        # Configuration
        ON_TIME = 30  # Seconds to stay on after motion
        
        def motion_detected():
            print(f"\nMotion detected at {datetime.now().strftime('%H:%M:%S')}")
            relay.on()
            
            # Use daemon thread for timer
            import threading
            timer = threading.Timer(ON_TIME, relay.off)
            timer.daemon = True
            timer.start()
        
        pir.when_motion = motion_detected
        
        print(f"System armed. Light will stay on for {ON_TIME}s after motion.")
        
        # Keep running
        signal.pause()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure PIR sensor is connected to GPIO24")
    finally:
        relay.cleanup()

def multi_relay_demo():
    """Control multiple relays"""
    print("\n=== Multi-Relay Control ===")
    print("Controlling 4 relays...")
    
    # Create relay objects
    relays = [
        RelayController(RELAY_1_PIN, "Relay 1", ACTIVE_HIGH),
        RelayController(RELAY_2_PIN, "Relay 2", ACTIVE_HIGH),
        RelayController(RELAY_3_PIN, "Relay 3", ACTIVE_HIGH),
        RelayController(RELAY_4_PIN, "Relay 4", ACTIVE_HIGH)
    ]
    
    try:
        # Sequential activation
        print("\nSequential activation")
        for relay in relays:
            relay.on()
            time.sleep(0.5)
        
        time.sleep(1)
        
        # Sequential deactivation
        print("\nSequential deactivation")
        for relay in relays:
            relay.off()
            time.sleep(0.5)
        
        # Pattern demo
        print("\nPattern demonstration")
        patterns = [
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1],
            [0, 1, 1, 0]
        ]
        
        for pattern in patterns:
            for i, state in enumerate(pattern):
                if state:
                    relays[i].on()
                else:
                    relays[i].off()
            time.sleep(0.5)
        
        # All off
        for relay in relays:
            relay.off()
        
    finally:
        for relay in relays:
            relay.cleanup()

def temperature_control():
    """Temperature-based relay control (simulated)"""
    print("\n=== Temperature Control ===")
    print("Simulating temperature-based relay control")
    print(f"Relay turns ON when temp > {TEMP_THRESHOLD}°C")
    
    relay = RelayController(RELAY_1_PIN, "Cooling Fan", ACTIVE_HIGH)
    
    try:
        # Simulate temperature readings
        import math
        
        for i in range(60):
            # Simulate temperature fluctuation
            temp = 20 + 10 * math.sin(i * 0.1) + 2 * math.sin(i * 0.3)
            
            # Control logic
            if temp > TEMP_THRESHOLD and not relay.state:
                print(f"\nTemp: {temp:.1f}°C - Fan ON")
                relay.on()
            elif temp <= TEMP_THRESHOLD - 2 and relay.state:  # Hysteresis
                print(f"\nTemp: {temp:.1f}°C - Fan OFF")
                relay.off()
            else:
                print(f"\rTemp: {temp:.1f}°C - Fan {'ON' if relay.state else 'OFF'}", end='')
            
            time.sleep(0.5)
        
    except KeyboardInterrupt:
        print("\n\nControl stopped")
    finally:
        relay.cleanup()

def safety_interlock():
    """Safety interlock system with multiple relays"""
    print("\n=== Safety Interlock System ===")
    print("Demonstrates safety interlocking between devices")
    
    # Create interlocked relays
    main_power = RelayController(RELAY_1_PIN, "Main Power", ACTIVE_HIGH)
    device_1 = RelayController(RELAY_2_PIN, "Device 1", ACTIVE_HIGH)
    device_2 = RelayController(RELAY_3_PIN, "Device 2", ACTIVE_HIGH)
    safety_lock = RelayController(RELAY_4_PIN, "Safety Lock", ACTIVE_HIGH)
    
    try:
        print("\n1. Enabling safety lock")
        safety_lock.on()
        time.sleep(1)
        
        print("\n2. Powering main system")
        main_power.on()
        time.sleep(1)
        
        print("\n3. Cannot start devices while safety lock is engaged")
        print("   Attempting to start Device 1...")
        time.sleep(1)
        print("   BLOCKED by safety interlock")
        
        print("\n4. Disabling safety lock")
        safety_lock.off()
        time.sleep(1)
        
        print("\n5. Now devices can be started")
        device_1.on()
        time.sleep(1)
        
        print("\n6. Device 2 cannot run simultaneously (interlock)")
        print("   Attempting to start Device 2...")
        time.sleep(1)
        print("   BLOCKED - Device 1 is running")
        
        print("\n7. Stopping Device 1")
        device_1.off()
        time.sleep(1)
        
        print("\n8. Now Device 2 can run")
        device_2.on()
        time.sleep(2)
        
        print("\n9. Shutting down system")
        device_2.off()
        time.sleep(0.5)
        main_power.off()
        
    finally:
        main_power.cleanup()
        device_1.cleanup()
        device_2.cleanup()
        safety_lock.cleanup()

def appliance_simulator():
    """Simulate home appliance control"""
    print("\n=== Home Appliance Control ===")
    
    appliances = {
        '1': RelayController(RELAY_1_PIN, "Living Room Light", ACTIVE_HIGH),
        '2': RelayController(RELAY_2_PIN, "Kitchen Light", ACTIVE_HIGH),
        '3': RelayController(RELAY_3_PIN, "Fan", ACTIVE_HIGH),
        '4': RelayController(RELAY_4_PIN, "Water Pump", ACTIVE_HIGH)
    }
    
    try:
        while True:
            print("\n\nHome Automation Control")
            print("=" * 30)
            
            # Show status
            for key, appliance in appliances.items():
                status = "ON" if appliance.state else "OFF"
                print(f"{key}. {appliance.name}: {status}")
            
            print("\nCommands:")
            print("1-4: Toggle appliance")
            print("a: All ON")
            print("o: All OFF")
            print("q: Quit")
            
            choice = input("\nEnter command: ").strip().lower()
            
            if choice in appliances:
                appliances[choice].toggle()
            elif choice == 'a':
                print("Turning all appliances ON")
                for appliance in appliances.values():
                    appliance.on()
                    time.sleep(0.2)
            elif choice == 'o':
                print("Turning all appliances OFF")
                for appliance in appliances.values():
                    appliance.off()
                    time.sleep(0.2)
            elif choice == 'q':
                break
            else:
                print("Invalid command")
        
    finally:
        print("\nShutting down all appliances...")
        for appliance in appliances.values():
            appliance.off()
            appliance.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Relay Control Examples")
    print("=====================")
    print("GPIO Pins:")
    print(f"  Relay 1: GPIO{RELAY_1_PIN}")
    print(f"  Relay 2: GPIO{RELAY_2_PIN}")
    print(f"  Relay 3: GPIO{RELAY_3_PIN}")
    print(f"  Relay 4: GPIO{RELAY_4_PIN}")
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic relay control")
        print("2. Timer control")
        print("3. Scheduled on/off")
        print("4. Button control")
        print("5. Motion activated")
        print("6. Multi-relay patterns")
        print("7. Temperature control (simulated)")
        print("8. Safety interlock demo")
        print("9. Home appliance control")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '1':
            basic_relay_control()
        elif choice == '2':
            timer_control()
        elif choice == '3':
            scheduled_control()
        elif choice == '4':
            button_control()
        elif choice == '5':
            motion_activated()
        elif choice == '6':
            multi_relay_demo()
        elif choice == '7':
            temperature_control()
        elif choice == '8':
            safety_interlock()
        elif choice == '9':
            appliance_simulator()
        elif choice == '0':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()