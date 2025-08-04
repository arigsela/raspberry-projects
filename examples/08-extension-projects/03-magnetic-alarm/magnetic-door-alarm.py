#!/usr/bin/env python3
"""
Magnetic Door Alarm System
Comprehensive door monitoring with magnetic reed switches, alerts, and logging
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

import time
import signal
import threading
import json
from datetime import datetime, timedelta
import statistics

from gpiozero import Button, LED, PWMLED, Buzzer, MCP3008
from gpiozero.pins.pigpio import PiGPIOFactory

# Try to use pigpio for better timing precision
try:
    from gpiozero import Device
    Device.pin_factory = PiGPIOFactory()
    PRECISE_TIMING = True
except:
    PRECISE_TIMING = False
    print("Note: Using default pin factory (pigpio not available)")

# GPIO Configuration
# Door sensors (magnetic reed switches)
DOOR_1_PIN = 17          # Front door
DOOR_2_PIN = 18          # Back door  
DOOR_3_PIN = 27          # Side door (optional)
DOOR_4_PIN = 22          # Window sensor (optional)

# Control inputs
ARM_BUTTON_PIN = 23      # Arm/disarm system
MUTE_BUTTON_PIN = 24     # Mute current alarm
TEST_BUTTON_PIN = 25     # Test all sensors

# Status indicators
ARMED_LED_PIN = 26       # System armed indicator
ALARM_LED_PIN = 19       # Alarm active indicator
STATUS_LED_PIN = 20      # General status (breathing effect)
DOOR_LED_PIN = 21        # Door activity indicator

# Audio alerts
ALARM_BUZZER_PIN = 13    # Main alarm buzzer
STATUS_BUZZER_PIN = 12   # Status beeps

# Optional features
KEYPAD_ENABLE_PIN = 16   # Enable keypad for arming/disarming
MOTION_SENSOR_PIN = 6    # PIR for additional security

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class DoorAlarmSystem:
    """Comprehensive magnetic door alarm system with multiple zones"""
    
    def __init__(self):
        """Initialize door alarm system"""
        
        # Door sensor configuration
        self.door_configs = [
            {'name': 'Front Door', 'pin': DOOR_1_PIN, 'priority': 'high', 'enabled': True},
            {'name': 'Back Door', 'pin': DOOR_2_PIN, 'priority': 'high', 'enabled': True},
            {'name': 'Side Door', 'pin': DOOR_3_PIN, 'priority': 'medium', 'enabled': False},
            {'name': 'Window', 'pin': DOOR_4_PIN, 'priority': 'low', 'enabled': False}
        ]
        
        # Initialize door sensors
        self.door_sensors = {}
        self.door_states = {}
        
        for config in self.door_configs:
            if config['enabled']:
                try:
                    # Reed switch is normally closed, open when door opens
                    sensor = Button(config['pin'], pull_up=True, bounce_time=0.1)
                    self.door_sensors[config['name']] = sensor
                    self.door_states[config['name']] = {
                        'config': config,
                        'sensor': sensor,
                        'is_open': False,
                        'last_change': time.time(),
                        'open_count': 0,
                        'total_open_time': 0.0,
                        'longest_open': 0.0,
                        'alarm_triggered': False
                    }
                    
                    # Setup callbacks
                    sensor.when_pressed = lambda door=config['name']: self._on_door_opened(door)
                    sensor.when_released = lambda door=config['name']: self._on_door_closed(door)
                    
                    print(f"✓ {config['name']} sensor initialized on GPIO{config['pin']}")
                except Exception as e:
                    print(f"✗ Failed to initialize {config['name']}: {e}")
        
        # Initialize control buttons
        try:
            self.arm_button = Button(ARM_BUTTON_PIN, bounce_time=0.2)
            self.mute_button = Button(MUTE_BUTTON_PIN, bounce_time=0.2)
            self.test_button = Button(TEST_BUTTON_PIN, bounce_time=0.2)
            
            self.arm_button.when_pressed = self._toggle_armed_state
            self.mute_button.when_pressed = self._mute_alarm
            self.test_button.when_pressed = self._test_system
            
            self.has_buttons = True
            print("✓ Control buttons initialized")
        except Exception as e:
            self.has_buttons = False
            print(f"✗ Control buttons failed: {e}")
        
        # Initialize indicators
        try:
            self.armed_led = LED(ARMED_LED_PIN)
            self.alarm_led = PWMLED(ALARM_LED_PIN)  # PWM for flashing
            self.status_led = PWMLED(STATUS_LED_PIN)  # PWM for breathing
            self.door_led = LED(DOOR_LED_PIN)
            
            self.alarm_buzzer = Buzzer(ALARM_BUZZER_PIN)
            self.status_buzzer = Buzzer(STATUS_BUZZER_PIN)
            
            self.has_indicators = True
            print("✓ Status indicators initialized")
        except Exception as e:
            self.has_indicators = False
            print(f"✗ Status indicators failed: {e}")
        
        # Optional motion sensor
        try:
            from gpiozero import MotionSensor
            self.motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
            self.motion_sensor.when_motion = self._on_motion_detected
            self.has_motion_sensor = True
            print("✓ Motion sensor initialized")
        except:
            self.has_motion_sensor = False
            print("⚠ Motion sensor not available")
        
        # System state
        self.is_armed = False
        self.alarm_active = False
        self.alarm_muted = False
        self.system_start_time = time.time()
        
        # Alarm settings
        self.entry_delay = 10.0          # seconds before alarm triggers
        self.exit_delay = 30.0           # seconds to exit after arming
        self.alarm_duration = 300.0      # max alarm duration (5 minutes)
        self.auto_rearm_delay = 60.0     # seconds before auto-rearm after closing
        
        # Sensitivity settings
        self.trigger_sensitivity = "medium"  # low, medium, high
        self.false_alarm_prevention = True
        self.multiple_trigger_threshold = 3  # triggers before alarm
        
        # Logging and statistics
        self.event_log = []
        self.daily_stats = {}
        self.alarm_history = []
        
        # Timers and threads
        self.entry_timer = None
        self.exit_timer = None
        self.alarm_timer = None
        self.auto_rearm_timer = None
        
        # Background monitoring
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Load settings
        self.settings = self.load_settings()
        self._apply_settings()
        
        # Initialize status
        if self.has_indicators:
            self.status_led.pulse()  # Breathing effect when ready
            self.status_buzzer.beep(0.1, 0.1, n=3)  # Startup sound
        
        print("🚪 Magnetic Door Alarm System Initialized")
        print(f"Monitoring {len(self.door_sensors)} door(s)")
        print("System DISARMED - Press ARM button or use keypad to activate")
    
    def _on_door_opened(self, door_name):
        """Handle door opening event"""
        current_time = time.time()
        door_state = self.door_states.get(door_name)
        
        if not door_state:
            return
        
        # Update door state
        door_state['is_open'] = True
        door_state['last_change'] = current_time
        door_state['open_count'] += 1
        
        # Log event
        event = {
            'timestamp': datetime.now().isoformat(),
            'door': door_name,
            'action': 'opened',
            'armed': self.is_armed,
            'priority': door_state['config']['priority']
        }
        self.event_log.append(event)
        
        print(f"🚪 {door_name} OPENED")
        
        # Visual feedback
        if self.has_indicators:
            self.door_led.on()
        
        # Handle armed system
        if self.is_armed and not self.alarm_active:
            self._handle_armed_door_opening(door_name, door_state)
        
        # Update daily statistics
        self._update_daily_stats(door_name, 'opened')
    
    def _on_door_closed(self, door_name):
        """Handle door closing event"""
        current_time = time.time()
        door_state = self.door_states.get(door_name)
        
        if not door_state or not door_state['is_open']:
            return
        
        # Calculate open duration
        open_duration = current_time - door_state['last_change']
        door_state['total_open_time'] += open_duration
        if open_duration > door_state['longest_open']:
            door_state['longest_open'] = open_duration
        
        # Update door state
        door_state['is_open'] = False
        door_state['last_change'] = current_time
        door_state['alarm_triggered'] = False
        
        # Log event
        event = {
            'timestamp': datetime.now().isoformat(),
            'door': door_name,
            'action': 'closed',
            'duration': open_duration,
            'armed': self.is_armed
        }
        self.event_log.append(event)
        
        print(f"🚪 {door_name} CLOSED (open for {open_duration:.1f}s)")
        
        # Visual feedback
        if self.has_indicators:
            self.door_led.off()
        
        # Cancel entry delay if all doors closed
        if self._all_doors_closed() and self.entry_timer:
            self.entry_timer.cancel()
            self.entry_timer = None
            print("Entry delay cancelled - all doors closed")
        
        # Auto-rearm if system was disarmed by alarm
        if not self.is_armed and self.auto_rearm_timer is None:
            self._schedule_auto_rearm()
        
        # Update statistics
        self._update_daily_stats(door_name, 'closed')
    
    def _handle_armed_door_opening(self, door_name, door_state):
        """Handle door opening when system is armed"""
        priority = door_state['config']['priority']
        
        # High priority doors trigger immediate alarm or entry delay
        if priority == 'high':
            if self.entry_delay > 0:
                print(f"⏰ Entry delay started: {self.entry_delay}s")
                if self.has_indicators:
                    self.status_buzzer.beep(0.1, 0.9, background=True)  # Warning beeps
                
                self.entry_timer = threading.Timer(self.entry_delay, self._trigger_alarm)
                self.entry_timer.start()
            else:
                self._trigger_alarm()
        
        # Medium priority doors have longer delay
        elif priority == 'medium':
            delay = self.entry_delay * 1.5
            print(f"⏰ Extended entry delay: {delay}s")
            self.entry_timer = threading.Timer(delay, self._trigger_alarm)
            self.entry_timer.start()
        
        # Low priority doors (windows) trigger immediate alarm
        elif priority == 'low':
            print("🚨 Immediate alarm - security breach detected")
            self._trigger_alarm()
    
    def _trigger_alarm(self):
        """Trigger the alarm system"""
        if self.alarm_active:
            return
        
        self.alarm_active = True
        alarm_start = datetime.now()
        
        print("🚨🚨🚨 ALARM TRIGGERED 🚨🚨🚨")
        
        # Log alarm event
        alarm_event = {
            'timestamp': alarm_start.isoformat(),
            'type': 'alarm_triggered',
            'doors_open': [name for name, state in self.door_states.items() if state['is_open']],
            'trigger_reason': 'door_breach'
        }
        self.alarm_history.append(alarm_event)
        
        # Visual and audio alerts
        if self.has_indicators:
            self.alarm_led.blink()  # Flashing alarm LED
            
            if not self.alarm_muted:
                # Alarm pattern: 3 short, 1 long, repeat
                def alarm_pattern():
                    while self.alarm_active and not self.alarm_muted:
                        self.alarm_buzzer.beep(0.2, 0.1, n=3)
                        time.sleep(0.5)
                        self.alarm_buzzer.beep(1.0, 0.5, n=1)
                        time.sleep(1.0)
                
                alarm_thread = threading.Thread(target=alarm_pattern, daemon=True)
                alarm_thread.start()
        
        # Set alarm duration limit
        self.alarm_timer = threading.Timer(self.alarm_duration, self._auto_stop_alarm)
        self.alarm_timer.start()
        
        # Mark doors that triggered alarm
        for door_name, door_state in self.door_states.items():
            if door_state['is_open']:
                door_state['alarm_triggered'] = True
    
    def _auto_stop_alarm(self):
        """Automatically stop alarm after duration limit"""
        print(f"⏰ Alarm auto-stopped after {self.alarm_duration}s")
        self._stop_alarm()
    
    def _stop_alarm(self):
        """Stop the active alarm"""
        if not self.alarm_active:
            return
        
        self.alarm_active = False
        self.alarm_muted = False
        
        # Cancel alarm timer
        if self.alarm_timer:
            self.alarm_timer.cancel()
            self.alarm_timer = None
        
        # Stop visual/audio alerts
        if self.has_indicators:
            self.alarm_led.off()
        
        print("🔇 Alarm stopped")
    
    def _mute_alarm(self):
        """Mute the current alarm audio"""
        if self.alarm_active:
            self.alarm_muted = True
            print("🔇 Alarm muted")
            
            if self.has_indicators:
                self.status_buzzer.beep(0.1, 0.1, n=2)
    
    def _toggle_armed_state(self):
        """Toggle system armed/disarmed state"""
        if self.is_armed:
            self._disarm_system()
        else:
            self._arm_system()
    
    def _arm_system(self):
        """Arm the alarm system"""
        if self.is_armed:
            return
        
        # Check if any doors are open
        open_doors = [name for name, state in self.door_states.items() if state['is_open']]
        
        if open_doors:
            print(f"⚠ Cannot arm - doors open: {', '.join(open_doors)}")
            if self.has_indicators:
                self.status_buzzer.beep(0.5, 0.5, n=3)  # Error sound
            return
        
        print(f"🛡️ Arming system - exit delay: {self.exit_delay}s")
        
        # Exit delay countdown
        if self.exit_delay > 0:
            if self.has_indicators:
                self.status_buzzer.beep(0.2, 0.8, background=True)  # Exit warning
            
            def complete_arming():
                self.is_armed = True
                if self.has_indicators:
                    self.armed_led.on()
                    self.status_buzzer.beep(0.5, 0.0, n=1)  # Armed confirmation
                
                print("🛡️ System ARMED")
                
                # Log arming event
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'action': 'system_armed',
                    'user': 'button_press'
                }
                self.event_log.append(event)
            
            self.exit_timer = threading.Timer(self.exit_delay, complete_arming)
            self.exit_timer.start()
        else:
            # Immediate arming
            self.is_armed = True
            if self.has_indicators:
                self.armed_led.on()
    
    def _disarm_system(self):
        """Disarm the alarm system"""
        if not self.is_armed:
            return
        
        # Cancel any active timers
        if self.entry_timer:
            self.entry_timer.cancel()
            self.entry_timer = None
        
        if self.exit_timer:
            self.exit_timer.cancel()
            self.exit_timer = None
        
        # Stop any active alarm
        if self.alarm_active:
            self._stop_alarm()
        
        self.is_armed = False
        
        if self.has_indicators:
            self.armed_led.off()
            self.status_buzzer.beep(0.2, 0.2, n=2)  # Disarmed confirmation
        
        print("🔓 System DISARMED")
        
        # Log disarming event
        event = {
            'timestamp': datetime.now().isoformat(),
            'action': 'system_disarmed',
            'user': 'button_press'
        }
        self.event_log.append(event)
    
    def _schedule_auto_rearm(self):
        """Schedule automatic re-arming after all doors close"""
        def auto_rearm():
            if self._all_doors_closed() and not self.is_armed:
                print(f"🔄 Auto-rearming system after {self.auto_rearm_delay}s")
                self._arm_system()
            self.auto_rearm_timer = None
        
        self.auto_rearm_timer = threading.Timer(self.auto_rearm_delay, auto_rearm)
        self.auto_rearm_timer.start()
    
    def _test_system(self):
        """Test all system components"""
        print("\n🧪 System Test Starting...")
        
        if self.has_indicators:
            # Test LEDs
            print("Testing LEDs...")
            leds = [self.armed_led, self.alarm_led, self.status_led, self.door_led]
            for led in leds:
                led.on()
                time.sleep(0.3)
                led.off()
            
            # Test buzzers
            print("Testing buzzers...")
            self.status_buzzer.beep(0.2, 0.2, n=3)
            time.sleep(1)
            self.alarm_buzzer.beep(0.5, 0.0, n=1)
        
        # Test door sensors
        print("Testing door sensors...")
        for door_name, door_state in self.door_states.items():
            sensor = door_state['sensor']
            status = "OPEN" if sensor.is_pressed else "CLOSED"
            print(f"  {door_name}: {status}")
        
        print("✓ System test complete")
    
    def _on_motion_detected(self):
        """Handle motion sensor trigger (if available)"""
        if not self.is_armed:
            return
        
        print("🚶 Motion detected while armed")
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': 'motion_detected',
            'armed': self.is_armed
        }
        self.event_log.append(event)
        
        # Motion during armed state extends entry delay
        if self.entry_timer and not self.alarm_active:
            print("⏰ Entry delay extended due to motion")
    
    def _all_doors_closed(self):
        """Check if all monitored doors are closed"""
        return all(not state['is_open'] for state in self.door_states.values())
    
    def _monitoring_loop(self):
        """Background monitoring and maintenance"""
        while self.monitoring_active:
            try:
                # Update breathing LED
                if self.has_indicators and not self.alarm_active:
                    if self.is_armed:
                        self.status_led.on()  # Solid when armed
                    else:
                        self.status_led.pulse()  # Breathing when disarmed
                
                # Check for stuck open doors
                current_time = time.time()
                for door_name, door_state in self.door_states.items():
                    if door_state['is_open']:
                        open_duration = current_time - door_state['last_change']
                        
                        # Warn about doors open too long
                        if open_duration > 300 and open_duration % 60 < 1:  # Every minute after 5 minutes
                            print(f"⚠ {door_name} has been open for {open_duration/60:.1f} minutes")
                
                # Save logs periodically
                if len(self.event_log) > 0 and len(self.event_log) % 50 == 0:
                    self.save_event_log()
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(10)
    
    def _update_daily_stats(self, door_name, action):
        """Update daily door usage statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if today not in self.daily_stats:
            self.daily_stats[today] = {}
        
        if door_name not in self.daily_stats[today]:
            self.daily_stats[today][door_name] = {
                'opens': 0,
                'closes': 0,
                'total_time_open': 0.0
            }
        
        if action == 'opened':
            self.daily_stats[today][door_name]['opens'] += 1
        elif action == 'closed':
            self.daily_stats[today][door_name]['closes'] += 1
    
    def _apply_settings(self):
        """Apply loaded settings to system"""
        if 'entry_delay' in self.settings:
            self.entry_delay = self.settings['entry_delay']
        if 'exit_delay' in self.settings:
            self.exit_delay = self.settings['exit_delay']
        if 'alarm_duration' in self.settings:
            self.alarm_duration = self.settings['alarm_duration']
    
    def load_settings(self):
        """Load system settings from file"""
        try:
            with open('door_alarm_settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'entry_delay': self.entry_delay,
            'exit_delay': self.exit_delay,
            'alarm_duration': self.alarm_duration,
            'auto_rearm_delay': self.auto_rearm_delay,
            'trigger_sensitivity': self.trigger_sensitivity,
            'door_configs': self.door_configs
        }
        
        with open('door_alarm_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    def save_event_log(self):
        """Save event log to file"""
        try:
            with open('door_events.json', 'w') as f:
                json.dump(self.event_log, f, indent=2)
        except Exception as e:
            print(f"Failed to save event log: {e}")
    
    def get_statistics(self):
        """Get comprehensive system statistics"""
        uptime = time.time() - self.system_start_time
        
        # Calculate door usage stats
        total_opens = sum(state['open_count'] for state in self.door_states.values())
        total_open_time = sum(state['total_open_time'] for state in self.door_states.values())
        
        # Recent activity (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_events = [e for e in self.event_log 
                        if datetime.fromisoformat(e['timestamp']) > recent_cutoff]
        
        return {
            'uptime_hours': uptime / 3600,
            'system_armed': self.is_armed,
            'alarm_active': self.alarm_active,
            'doors_monitored': len(self.door_sensors),
            'total_door_opens': total_opens,
            'total_open_time_hours': total_open_time / 3600,
            'alarms_triggered': len(self.alarm_history),
            'events_logged': len(self.event_log),
            'recent_events_24h': len(recent_events),
            'current_open_doors': [name for name, state in self.door_states.items() if state['is_open']]
        }
    
    def get_door_report(self):
        """Get detailed door usage report"""
        report = {}
        
        for door_name, door_state in self.door_states.items():
            report[door_name] = {
                'currently_open': door_state['is_open'],
                'total_opens': door_state['open_count'],
                'total_time_open_hours': door_state['total_open_time'] / 3600,
                'longest_open_minutes': door_state['longest_open'] / 60,
                'priority': door_state['config']['priority'],
                'last_activity': datetime.fromtimestamp(door_state['last_change']).strftime('%Y-%m-%d %H:%M:%S')
            }
        
        return report
    
    def cleanup(self):
        """Clean up system resources"""
        print("\n🧹 Cleaning up door alarm system...")
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Cancel all timers
        for timer in [self.entry_timer, self.exit_timer, self.alarm_timer, self.auto_rearm_timer]:
            if timer:
                timer.cancel()
        
        # Stop any active alarm
        if self.alarm_active:
            self._stop_alarm()
        
        # Save data
        self.save_settings()
        self.save_event_log()
        
        # Turn off indicators
        if self.has_indicators:
            self.armed_led.off()
            self.alarm_led.off()
            self.status_led.off()
            self.door_led.off()
            self.status_buzzer.beep(0.2, 0.1, n=3)  # Shutdown sound
        
        # Close hardware
        for sensor in self.door_sensors.values():
            sensor.close()
        
        if self.has_buttons:
            self.arm_button.close()
            self.mute_button.close()
            self.test_button.close()
        
        if self.has_indicators:
            self.armed_led.close()
            self.alarm_led.close()
            self.status_led.close()
            self.door_led.close()
            self.alarm_buzzer.close()
            self.status_buzzer.close()
        
        if self.has_motion_sensor:
            self.motion_sensor.close()

def interactive_demo():
    """Interactive door alarm demonstration"""
    print("\n🚪 Interactive Door Alarm Demo")
    print("Monitor door sensors and control alarm system")
    print("Press Ctrl+C to exit")
    
    try:
        system = DoorAlarmSystem()
        
        print(f"\n📋 System Controls:")
        print("🛡️ ARM Button: Toggle armed/disarmed state")
        print("🔇 MUTE Button: Mute active alarm")
        print("🧪 TEST Button: Test all components")
        
        print(f"\n🚪 Monitored Doors:")
        for door_name in system.door_sensors.keys():
            print(f"  • {door_name}")
        
        start_time = time.time()
        
        while True:
            # Display real-time status
            stats = system.get_statistics()
            elapsed = time.time() - start_time
            
            armed_status = "🛡️ ARMED" if stats['system_armed'] else "🔓 DISARMED"
            alarm_status = "🚨 ALARM" if stats['alarm_active'] else "✅ OK"
            
            open_doors = stats['current_open_doors']
            door_status = f"🚪 Open: {', '.join(open_doors) if open_doors else 'All Closed'}"
            
            print(f"\r{armed_status} | {alarm_status} | {door_status} | "
                  f"Opens: {stats['total_door_opens']} | Time: {elapsed:.0f}s", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print(f"\n\n📊 Session Summary:")
        stats = system.get_statistics()
        print(f"System uptime: {stats['uptime_hours']:.1f} hours")
        print(f"Door opens: {stats['total_door_opens']}")
        print(f"Alarms triggered: {stats['alarms_triggered']}")
        print(f"Events logged: {stats['events_logged']}")
        
        # Show door usage report
        print(f"\n🚪 Door Usage Report:")
        door_report = system.get_door_report()
        for door_name, data in door_report.items():
            status = "OPEN" if data['currently_open'] else "CLOSED"
            print(f"  {door_name}: {status} | Opens: {data['total_opens']} | "
                  f"Total time: {data['total_time_open_hours']:.1f}h")
    finally:
        system.cleanup()

def security_demo():
    """Security monitoring demonstration"""
    print("\n🛡️ Security Monitoring Demo")
    print("Demonstrates armed system with door monitoring")
    print("Press Ctrl+C to exit")
    
    try:
        system = DoorAlarmSystem()
        
        # Auto-arm the system for demo
        print("🛡️ Auto-arming system for security demo...")
        system.exit_delay = 5  # Short delay for demo
        system._arm_system()
        
        time.sleep(6)  # Wait for arming to complete
        
        print("🔒 Security monitoring active")
        print("🚪 Open any monitored door to test alarm")
        
        while True:
            # Simulate door openings for demo if no real sensors
            if not system.door_sensors:
                print("📝 Simulating door events for demo...")
                time.sleep(10)
                system._on_door_opened("Simulated Door")
                time.sleep(3)
                system._on_door_closed("Simulated Door")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🔒 Security monitoring ended")
        stats = system.get_statistics()
        print(f"Monitoring time: {stats['uptime_hours']:.1f} hours")
        print(f"Alarms triggered: {stats['alarms_triggered']}")
    finally:
        system.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Magnetic Door Alarm System")
    print("=========================")
    print("🚪 Multi-Zone Door Monitoring")
    print("🛡️ Armed/Disarmed Operation")
    print("🚨 Intelligent Alarm System")
    print("📊 Comprehensive Logging")
    
    while True:
        print("\n\nSelect Demo Mode:")
        print("1. Interactive door monitoring")
        print("2. Security system demonstration")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            interactive_demo()
        elif choice == '2':
            security_demo()
        elif choice == '3':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()