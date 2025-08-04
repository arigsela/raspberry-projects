#!/usr/bin/env python3
"""
LED Traffic Light Control System

Realistic traffic light simulation with multiple modes including
standard operation, pedestrian crossing, emergency vehicle priority,
and programmable timing sequences.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from gpiozero import LED, PWMLED, Button, Buzzer
import random

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602

# Hardware Pin Definitions
# Traffic Light LEDs
NORTH_RED_PIN = 17
NORTH_YELLOW_PIN = 27
NORTH_GREEN_PIN = 22

SOUTH_RED_PIN = 23
SOUTH_YELLOW_PIN = 24
SOUTH_GREEN_PIN = 25

EAST_RED_PIN = 5
EAST_YELLOW_PIN = 6
EAST_GREEN_PIN = 13

WEST_RED_PIN = 19
WEST_YELLOW_PIN = 26
WEST_GREEN_PIN = 21

# Pedestrian Crossing
PED_RED_PIN = 20      # Don't Walk
PED_GREEN_PIN = 16    # Walk
PED_BUTTON_PIN = 12   # Request button
PED_BUZZER_PIN = 18   # Audio signal

# Emergency Override
EMERGENCY_BUTTON_PIN = 14
EMERGENCY_LED_PIN = 15    # Flashing indicator

# System Control
MODE_BUTTON_PIN = 8
MANUAL_BUTTON_PIN = 7

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Timing Constants (seconds)
GREEN_TIME_DEFAULT = 30
YELLOW_TIME_DEFAULT = 3
ALL_RED_TIME = 2  # Safety period between changes
PED_CROSSING_TIME = 20
EMERGENCY_CLEAR_TIME = 10

class TrafficMode(Enum):
    """Traffic light operating modes"""
    STANDARD = "Standard"
    PEAK_HOURS = "Peak Hours"
    NIGHT_MODE = "Night Mode"
    PEDESTRIAN = "Pedestrian"
    EMERGENCY = "Emergency"
    MANUAL = "Manual"
    MAINTENANCE = "Maintenance"

class Direction(Enum):
    """Traffic directions"""
    NORTH_SOUTH = "N-S"
    EAST_WEST = "E-W"
    ALL_RED = "Stop"
    
class TrafficLight:
    """Individual traffic light control"""
    def __init__(self, red_pin, yellow_pin, green_pin, name):
        self.red = LED(red_pin)
        self.yellow = LED(yellow_pin)
        self.green = LED(green_pin)
        self.name = name
        self.state = "RED"
        
    def set_red(self):
        """Set light to red"""
        self.red.on()
        self.yellow.off()
        self.green.off()
        self.state = "RED"
        
    def set_yellow(self):
        """Set light to yellow"""
        self.red.off()
        self.yellow.on()
        self.green.off()
        self.state = "YELLOW"
        
    def set_green(self):
        """Set light to green"""
        self.red.off()
        self.yellow.off()
        self.green.on()
        self.state = "GREEN"
        
    def all_off(self):
        """Turn off all lights"""
        self.red.off()
        self.yellow.off()
        self.green.off()
        self.state = "OFF"
        
    def cleanup(self):
        """Clean up GPIO resources"""
        self.red.close()
        self.yellow.close()
        self.green.close()

class LEDTrafficLightSystem:
    """Main traffic light control system"""
    
    def __init__(self):
        print("🚦 Initializing LED Traffic Light System...")
        
        # Initialize traffic lights
        self._init_traffic_lights()
        self._init_pedestrian_system()
        self._init_controls()
        self._init_display()
        
        # System state
        self.mode = TrafficMode.STANDARD
        self.current_direction = Direction.ALL_RED
        self.emergency_active = False
        self.pedestrian_request = False
        self.manual_override = False
        
        # Timing configuration
        self.timing_config = {
            TrafficMode.STANDARD: {
                'green': 30,
                'yellow': 3,
                'all_red': 2
            },
            TrafficMode.PEAK_HOURS: {
                'green_ns': 45,  # Favor N-S during peak
                'green_ew': 25,
                'yellow': 3,
                'all_red': 2
            },
            TrafficMode.NIGHT_MODE: {
                'green': 20,
                'yellow': 3,
                'all_red': 1
            }
        }
        
        # Statistics
        self.cycle_count = 0
        self.session_start = datetime.now()
        self.emergency_count = 0
        self.pedestrian_count = 0
        self.violation_count = 0
        
        # Threading
        self.running = False
        self.control_queue = queue.Queue()
        self.cycle_thread = None
        
        # Load configuration
        self._load_configuration()
        
        print("✅ Traffic light system initialized")
    
    def _init_traffic_lights(self):
        """Initialize traffic light objects"""
        self.lights = {
            'north': TrafficLight(NORTH_RED_PIN, NORTH_YELLOW_PIN, NORTH_GREEN_PIN, "North"),
            'south': TrafficLight(SOUTH_RED_PIN, SOUTH_YELLOW_PIN, SOUTH_GREEN_PIN, "South"),
            'east': TrafficLight(EAST_RED_PIN, EAST_YELLOW_PIN, EAST_GREEN_PIN, "East"),
            'west': TrafficLight(WEST_RED_PIN, WEST_YELLOW_PIN, WEST_GREEN_PIN, "West")
        }
        
        # Set all to red initially
        for light in self.lights.values():
            light.set_red()
            
        print("✓ Traffic lights initialized")
    
    def _init_pedestrian_system(self):
        """Initialize pedestrian crossing system"""
        self.ped_red = LED(PED_RED_PIN)
        self.ped_green = LED(PED_GREEN_PIN)
        self.ped_buzzer = Buzzer(PED_BUZZER_PIN)
        self.ped_button = Button(PED_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Set initial state
        self.ped_red.on()
        self.ped_green.off()
        
        # Button callback
        self.ped_button.when_pressed = self._request_pedestrian_crossing
        
        print("✓ Pedestrian system initialized")
    
    def _init_controls(self):
        """Initialize control buttons"""
        self.mode_button = Button(MODE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.manual_button = Button(MANUAL_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.emergency_button = Button(EMERGENCY_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.emergency_led = PWMLED(EMERGENCY_LED_PIN)
        
        # Button callbacks
        self.mode_button.when_pressed = self._cycle_mode
        self.manual_button.when_pressed = self._toggle_manual
        self.emergency_button.when_pressed = self._activate_emergency
        
        print("✓ Controls initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Traffic Control")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load saved configuration"""
        config_file = "traffic_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Load custom timing if available
                    if 'timing' in config:
                        self.timing_config.update(config['timing'])
                    print("✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def run(self):
        """Main system loop"""
        print("\n🚦 Traffic Light System Active!")
        print("MODE: Change operating mode")
        print("MANUAL: Toggle manual control")
        print("EMERGENCY: Activate emergency mode")
        print("Press Ctrl+C to exit\n")
        
        self.running = True
        
        # Start traffic cycle thread
        self.cycle_thread = threading.Thread(target=self._traffic_cycle_loop, daemon=True)
        self.cycle_thread.start()
        
        # Start display update thread
        display_thread = threading.Thread(target=self._display_update_loop, daemon=True)
        display_thread.start()
        
        try:
            while True:
                # Process control commands
                self._process_control_queue()
                
                # Check for violations (simulation)
                if random.random() < 0.001:  # 0.1% chance per loop
                    self._simulate_violation()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down traffic light system...")
            self.running = False
            self._all_red()
            time.sleep(1)
    
    def _traffic_cycle_loop(self):
        """Main traffic light cycle control"""
        while self.running:
            try:
                if self.emergency_active:
                    self._handle_emergency_mode()
                elif self.manual_override:
                    # Manual mode - wait for commands
                    time.sleep(0.5)
                elif self.pedestrian_request:
                    self._handle_pedestrian_crossing()
                else:
                    # Normal traffic cycle
                    self._normal_traffic_cycle()
                    
            except Exception as e:
                print(f"⚠ Traffic cycle error: {e}")
                self._all_red()
                time.sleep(5)
    
    def _normal_traffic_cycle(self):
        """Standard traffic light cycle"""
        # Get timing for current mode
        if self.mode == TrafficMode.STANDARD:
            green_time = self.timing_config[self.mode]['green']
            yellow_time = self.timing_config[self.mode]['yellow']
            all_red_time = self.timing_config[self.mode]['all_red']
        elif self.mode == TrafficMode.PEAK_HOURS:
            # Peak hours - different timing for each direction
            pass  # Implemented in direction-specific code
        elif self.mode == TrafficMode.NIGHT_MODE:
            green_time = self.timing_config[self.mode]['green']
            yellow_time = self.timing_config[self.mode]['yellow']
            all_red_time = self.timing_config[self.mode]['all_red']
        else:
            green_time = GREEN_TIME_DEFAULT
            yellow_time = YELLOW_TIME_DEFAULT
            all_red_time = ALL_RED_TIME
        
        # North-South green
        self._set_direction_green(Direction.NORTH_SOUTH)
        self._update_display("N-S GREEN", green_time)
        
        # Wait for green time
        for i in range(green_time):
            if not self._check_interrupts():
                return
            self._update_countdown(green_time - i)
            time.sleep(1)
        
        # North-South yellow
        self._set_direction_yellow(Direction.NORTH_SOUTH)
        self._update_display("N-S YELLOW", yellow_time)
        
        for i in range(yellow_time):
            if not self._check_interrupts():
                return
            time.sleep(1)
        
        # All red (safety period)
        self._all_red()
        self._update_display("ALL RED", all_red_time)
        time.sleep(all_red_time)
        
        # East-West green
        self._set_direction_green(Direction.EAST_WEST)
        self._update_display("E-W GREEN", green_time)
        
        for i in range(green_time):
            if not self._check_interrupts():
                return
            self._update_countdown(green_time - i)
            time.sleep(1)
        
        # East-West yellow
        self._set_direction_yellow(Direction.EAST_WEST)
        self._update_display("E-W YELLOW", yellow_time)
        
        for i in range(yellow_time):
            if not self._check_interrupts():
                return
            time.sleep(1)
        
        # All red (safety period)
        self._all_red()
        self._update_display("ALL RED", all_red_time)
        time.sleep(all_red_time)
        
        # Increment cycle count
        self.cycle_count += 1
    
    def _set_direction_green(self, direction):
        """Set specified direction to green"""
        if direction == Direction.NORTH_SOUTH:
            self.lights['north'].set_green()
            self.lights['south'].set_green()
            self.lights['east'].set_red()
            self.lights['west'].set_red()
        elif direction == Direction.EAST_WEST:
            self.lights['north'].set_red()
            self.lights['south'].set_red()
            self.lights['east'].set_green()
            self.lights['west'].set_green()
        
        self.current_direction = direction
    
    def _set_direction_yellow(self, direction):
        """Set specified direction to yellow"""
        if direction == Direction.NORTH_SOUTH:
            self.lights['north'].set_yellow()
            self.lights['south'].set_yellow()
        elif direction == Direction.EAST_WEST:
            self.lights['east'].set_yellow()
            self.lights['west'].set_yellow()
    
    def _all_red(self):
        """Set all lights to red"""
        for light in self.lights.values():
            light.set_red()
        self.current_direction = Direction.ALL_RED
    
    def _handle_pedestrian_crossing(self):
        """Handle pedestrian crossing request"""
        print("👥 Pedestrian crossing activated")
        self.pedestrian_count += 1
        
        # Stop all traffic
        self._all_red()
        self._update_display("PED CROSSING", PED_CROSSING_TIME)
        time.sleep(ALL_RED_TIME)
        
        # Activate pedestrian signal
        self.ped_red.off()
        self.ped_green.on()
        
        # Audio signal for crossing
        for i in range(PED_CROSSING_TIME):
            if i < PED_CROSSING_TIME - 5:
                # Normal crossing beep
                self.ped_buzzer.beep(0.1, 0.9, n=1)
            else:
                # Faster beep for last 5 seconds
                self.ped_buzzer.beep(0.1, 0.4, n=1)
            
            self._update_countdown(PED_CROSSING_TIME - i)
            
            if not self.running:
                break
        
        # Flash before ending
        for _ in range(3):
            self.ped_green.off()
            time.sleep(0.5)
            self.ped_green.on()
            time.sleep(0.5)
        
        # Reset pedestrian signal
        self.ped_green.off()
        self.ped_red.on()
        self.pedestrian_request = False
        
        print("✓ Pedestrian crossing complete")
    
    def _handle_emergency_mode(self):
        """Handle emergency vehicle priority"""
        print("🚨 Emergency mode active")
        self.emergency_count += 1
        
        # Flash all red lights
        self.emergency_led.pulse(fade_in_time=0.2, fade_out_time=0.2)
        
        # All directions red with flashing
        for _ in range(EMERGENCY_CLEAR_TIME):
            self._all_red()
            time.sleep(0.5)
            
            # Flash yellows as warning
            for light in self.lights.values():
                light.yellow.on()
            time.sleep(0.5)
            for light in self.lights.values():
                light.yellow.off()
            
            if not self.running:
                break
        
        # Clear emergency mode
        self.emergency_active = False
        self.emergency_led.off()
        print("✓ Emergency mode cleared")
    
    def _request_pedestrian_crossing(self):
        """Handle pedestrian button press"""
        if not self.pedestrian_request and not self.emergency_active:
            self.pedestrian_request = True
            print("👥 Pedestrian crossing requested")
            
            # Visual confirmation
            self.ped_buzzer.beep(0.1, 0, n=1)
            
            if self.lcd:
                self.lcd.write(1, 0, "PED WAIT        ")
    
    def _activate_emergency(self):
        """Activate emergency vehicle priority"""
        if not self.emergency_active:
            self.emergency_active = True
            print("🚨 Emergency vehicle detected!")
            self.control_queue.put({'type': 'emergency'})
    
    def _cycle_mode(self):
        """Cycle through operating modes"""
        modes = [TrafficMode.STANDARD, TrafficMode.PEAK_HOURS, 
                TrafficMode.NIGHT_MODE, TrafficMode.MAINTENANCE]
        
        current_index = modes.index(self.mode) if self.mode in modes else 0
        new_index = (current_index + 1) % len(modes)
        self.mode = modes[new_index]
        
        print(f"🚦 Mode: {self.mode.value}")
        
        # Special handling for maintenance mode
        if self.mode == TrafficMode.MAINTENANCE:
            self._maintenance_mode()
    
    def _toggle_manual(self):
        """Toggle manual control mode"""
        self.manual_override = not self.manual_override
        
        if self.manual_override:
            print("🎮 Manual control activated")
            self.mode = TrafficMode.MANUAL
        else:
            print("🔄 Automatic control resumed")
            self.mode = TrafficMode.STANDARD
    
    def _maintenance_mode(self):
        """Flash all yellow lights for maintenance"""
        print("🔧 Maintenance mode - flashing yellows")
        
        # Turn off all lights first
        for light in self.lights.values():
            light.all_off()
        
        # Flash yellows
        while self.mode == TrafficMode.MAINTENANCE and self.running:
            for light in self.lights.values():
                light.yellow.on()
            time.sleep(0.5)
            
            for light in self.lights.values():
                light.yellow.off()
            time.sleep(0.5)
    
    def _check_interrupts(self):
        """Check for system interrupts"""
        return (self.running and 
                not self.emergency_active and 
                not self.pedestrian_request and
                not self.manual_override and
                self.mode not in [TrafficMode.MAINTENANCE, TrafficMode.EMERGENCY])
    
    def _update_display(self, status, duration=None):
        """Update LCD display"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # First line - mode and status
            mode_short = self.mode.value[:4]
            self.lcd.write(0, 0, f"{mode_short}: {status}")
            
            # Second line - timing or info
            if duration:
                self.lcd.write(1, 0, f"Time: {duration}s")
            else:
                runtime = (datetime.now() - self.session_start).total_seconds() / 60
                self.lcd.write(1, 0, f"Run: {runtime:.0f}m C:{self.cycle_count}")
                
        except Exception as e:
            print(f"⚠ Display error: {e}")
    
    def _update_countdown(self, seconds):
        """Update countdown on display"""
        if self.lcd and seconds <= 9:
            try:
                self.lcd.write(1, 14, f"{seconds} ")
            except:
                pass
    
    def _display_update_loop(self):
        """Background display update thread"""
        while self.running:
            try:
                if not self.emergency_active and not self.pedestrian_request:
                    # Update general status
                    runtime = (datetime.now() - self.session_start).total_seconds() / 60
                    
                    if self.lcd and runtime > 0:
                        # Show statistics periodically
                        if int(runtime) % 30 == 0:  # Every 30 seconds
                            self.lcd.clear()
                            self.lcd.write(0, 0, f"Cycles: {self.cycle_count}")
                            self.lcd.write(1, 0, f"Ped: {self.pedestrian_count}")
                            time.sleep(3)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠ Display update error: {e}")
    
    def _process_control_queue(self):
        """Process control commands"""
        try:
            while not self.control_queue.empty():
                command = self.control_queue.get_nowait()
                
                if command['type'] == 'emergency':
                    # Emergency takes priority
                    pass  # Handled in main loop
                    
        except queue.Empty:
            pass
    
    def _simulate_violation(self):
        """Simulate traffic violation detection"""
        self.violation_count += 1
        print(f"📸 Traffic violation detected! Total: {self.violation_count}")
        
        # In real system, would trigger camera and logging
    
    def get_statistics(self):
        """Get system statistics"""
        runtime = (datetime.now() - self.session_start).total_seconds()
        
        stats = {
            'runtime_seconds': runtime,
            'cycle_count': self.cycle_count,
            'emergency_count': self.emergency_count,
            'pedestrian_count': self.pedestrian_count,
            'violation_count': self.violation_count,
            'average_cycle_time': runtime / self.cycle_count if self.cycle_count > 0 else 0
        }
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop operation
        self.running = False
        
        # All lights red for safety
        self._all_red()
        
        # Turn off pedestrian signals
        self.ped_green.off()
        self.ped_red.on()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
        
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Runtime: {stats['runtime_seconds']/60:.1f} minutes")
        print(f"  Traffic cycles: {stats['cycle_count']}")
        print(f"  Emergency vehicles: {stats['emergency_count']}")
        print(f"  Pedestrian crossings: {stats['pedestrian_count']}")
        print(f"  Violations detected: {stats['violation_count']}")
        print(f"  Average cycle time: {stats['average_cycle_time']:.1f} seconds")
        
        # Clean up hardware
        for light in self.lights.values():
            light.cleanup()
        
        self.ped_red.close()
        self.ped_green.close()
        self.ped_buzzer.close()
        self.ped_button.close()
        self.mode_button.close()
        self.manual_button.close()
        self.emergency_button.close()
        self.emergency_led.close()
        
        print("\n✅ Cleanup complete")


def traffic_demo():
    """Demonstrate traffic light patterns"""
    print("\n🎮 Traffic Light Demo")
    print("=" * 50)
    
    system = LEDTrafficLightSystem()
    
    try:
        print("\nDemonstrating traffic patterns...")
        
        # Demo 1: Normal cycle
        print("\n1. Normal traffic cycle")
        system._all_red()
        time.sleep(1)
        
        system._set_direction_green(Direction.NORTH_SOUTH)
        print("   North-South: GREEN")
        time.sleep(3)
        
        system._set_direction_yellow(Direction.NORTH_SOUTH)
        print("   North-South: YELLOW")
        time.sleep(2)
        
        system._all_red()
        print("   All: RED")
        time.sleep(1)
        
        system._set_direction_green(Direction.EAST_WEST)
        print("   East-West: GREEN")
        time.sleep(3)
        
        system._set_direction_yellow(Direction.EAST_WEST)
        print("   East-West: YELLOW")
        time.sleep(2)
        
        system._all_red()
        print("   All: RED")
        time.sleep(1)
        
        # Demo 2: Emergency mode
        print("\n2. Emergency vehicle mode")
        system.emergency_led.pulse()
        for _ in range(5):
            system._all_red()
            time.sleep(0.3)
            for light in system.lights.values():
                light.yellow.on()
            time.sleep(0.3)
            for light in system.lights.values():
                light.yellow.off()
        system.emergency_led.off()
        
        # Demo 3: Pedestrian crossing
        print("\n3. Pedestrian crossing")
        system._all_red()
        system.ped_red.off()
        system.ped_green.on()
        
        for _ in range(5):
            system.ped_buzzer.beep(0.1, 0.4, n=1)
            time.sleep(0.5)
        
        # Flash before ending
        for _ in range(3):
            system.ped_green.off()
            time.sleep(0.3)
            system.ped_green.on()
            time.sleep(0.3)
        
        system.ped_green.off()
        system.ped_red.on()
        
        # Demo 4: Maintenance mode
        print("\n4. Maintenance mode (flashing yellow)")
        for _ in range(5):
            for light in system.lights.values():
                light.yellow.on()
                light.red.off()
                light.green.off()
            time.sleep(0.5)
            for light in system.lights.values():
                light.yellow.off()
            time.sleep(0.5)
        
        print("\n✅ Demo complete!")
        
    finally:
        system.cleanup()


def light_test():
    """Test individual lights"""
    print("\n🔧 Traffic Light Test")
    print("=" * 50)
    
    system = LEDTrafficLightSystem()
    
    try:
        print("\nTesting each traffic light...")
        
        for name, light in system.lights.items():
            print(f"\n{name.capitalize()} light:")
            
            print("  Red...")
            light.set_red()
            time.sleep(1)
            
            print("  Yellow...")
            light.set_yellow()
            time.sleep(1)
            
            print("  Green...")
            light.set_green()
            time.sleep(1)
            
            light.set_red()
        
        print("\nTesting pedestrian signals...")
        print("  Don't Walk...")
        system.ped_red.on()
        system.ped_green.off()
        time.sleep(1)
        
        print("  Walk...")
        system.ped_red.off()
        system.ped_green.on()
        time.sleep(1)
        
        print("  Audio signal...")
        system.ped_buzzer.beep(0.1, 0.4, n=5)
        
        system.ped_red.on()
        system.ped_green.off()
        
        print("\n✅ Light test complete!")
        
    finally:
        system.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        traffic_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        light_test()
    else:
        # Normal operation
        system = LEDTrafficLightSystem()
        try:
            system.run()
        finally:
            system.cleanup()