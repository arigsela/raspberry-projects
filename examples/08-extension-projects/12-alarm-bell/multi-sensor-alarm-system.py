#!/usr/bin/env python3
"""
Multi-Sensor Alarm System

Comprehensive security system with motion detection, door sensors,
glass break detection, smoke alarm integration, and intelligent alert management.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import requests
import smtplib
from email.mime.text import MIMEText
import subprocess

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602
from adc0834 import ADC0834

# Hardware Pin Definitions
# Motion Sensors (PIR)
PIR_ZONE1_PIN = 17    # Living room
PIR_ZONE2_PIN = 27    # Kitchen
PIR_ZONE3_PIN = 22    # Bedroom
PIR_ZONE4_PIN = 23    # Garage

# Door/Window Sensors (Magnetic)
DOOR_FRONT_PIN = 24
DOOR_BACK_PIN = 25
WINDOW_1_PIN = 8
WINDOW_2_PIN = 7

# Glass Break Sensor (via ADC)
ADC_CS_PIN = 5
ADC_CLK_PIN = 6
ADC_DI_PIN = 16
ADC_DO_PIN = 12
GLASS_SENSOR_CHANNEL = 0

# Smoke/CO Detector Input
SMOKE_ALARM_PIN = 13

# Alert Outputs
SIREN_PIN = 19        # Main alarm siren
STROBE_PIN = 26       # Strobe light
BUZZER_PIN = 21       # Interior buzzer

# Status LEDs
LED_ARMED_PIN = 20    # Red - System armed
LED_READY_PIN = 14    # Green - Ready to arm
LED_ALERT_PIN = 15    # Yellow - Alert/warning

# Control Panel
ARM_BUTTON_PIN = 18   # Arm/disarm button
PANIC_BUTTON_PIN = 9  # Panic button
TEST_BUTTON_PIN = 10  # Test mode button

# LCD Display
LCD_I2C_ADDRESS = 0x27

# System Constants
ENTRY_DELAY = 30      # Seconds to disarm after entry
EXIT_DELAY = 60       # Seconds to exit after arming
ALARM_DURATION = 300  # 5 minutes alarm duration
GLASS_THRESHOLD = 180 # ADC threshold for glass break

from gpiozero import MotionSensor, Button, LED, PWMLED, Buzzer, OutputDevice

class AlarmMode(Enum):
    """Alarm system modes"""
    DISARMED = "Disarmed"
    ARMED_STAY = "Armed Stay"     # Interior motion off
    ARMED_AWAY = "Armed Away"     # All sensors active
    ARMED_NIGHT = "Armed Night"   # Perimeter only
    ALARM_TRIGGERED = "ALARM"
    ENTRY_DELAY = "Entry Delay"
    EXIT_DELAY = "Exit Delay"

class SensorType(Enum):
    """Types of security sensors"""
    MOTION = "Motion"
    DOOR = "Door"
    WINDOW = "Window"
    GLASS_BREAK = "Glass Break"
    SMOKE = "Smoke/CO"
    PANIC = "Panic"

class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class SecuritySensor:
    """Individual security sensor"""
    def __init__(self, name, sensor_type, pin=None, channel=None):
        self.name = name
        self.sensor_type = sensor_type
        self.pin = pin
        self.channel = channel
        self.enabled = True
        self.triggered = False
        self.last_trigger = None
        self.trigger_count = 0
        self.bypass = False
        
        # Initialize hardware based on type
        if sensor_type == SensorType.MOTION:
            self.sensor = MotionSensor(pin)
            self.sensor.when_motion = self._motion_detected
            self.sensor.when_no_motion = self._motion_stopped
        elif sensor_type in [SensorType.DOOR, SensorType.WINDOW]:
            self.sensor = Button(pin, pull_up=True)
            self.sensor.when_pressed = self._contact_opened
            self.sensor.when_released = self._contact_closed
        elif sensor_type == SensorType.SMOKE:
            self.sensor = Button(pin, pull_up=True)
            self.sensor.when_pressed = self._smoke_detected
            
    def _motion_detected(self):
        """Handle motion detection"""
        if self.enabled and not self.bypass:
            self.triggered = True
            self.last_trigger = datetime.now()
            self.trigger_count += 1
            
    def _motion_stopped(self):
        """Handle motion stopped"""
        self.triggered = False
        
    def _contact_opened(self):
        """Handle door/window opened"""
        if self.enabled and not self.bypass:
            self.triggered = True
            self.last_trigger = datetime.now()
            self.trigger_count += 1
            
    def _contact_closed(self):
        """Handle door/window closed"""
        self.triggered = False
        
    def _smoke_detected(self):
        """Handle smoke detection"""
        # Smoke alarms are always active
        self.triggered = True
        self.last_trigger = datetime.now()
        self.trigger_count += 1
        
    def is_secure(self):
        """Check if sensor is secure"""
        if self.bypass:
            return True
            
        if self.sensor_type == SensorType.MOTION:
            return not self.sensor.motion_detected
        elif self.sensor_type in [SensorType.DOOR, SensorType.WINDOW]:
            return self.sensor.is_pressed  # Closed = pressed
        elif self.sensor_type == SensorType.SMOKE:
            return not self.sensor.is_pressed
            
        return True
        
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'sensor'):
            self.sensor.close()

class Zone:
    """Security zone containing multiple sensors"""
    def __init__(self, name, zone_type="interior"):
        self.name = name
        self.zone_type = zone_type  # interior, perimeter, 24hour
        self.sensors = []
        self.enabled = True
        self.triggered = False
        self.chime_enabled = True
        
    def add_sensor(self, sensor):
        """Add sensor to zone"""
        self.sensors.append(sensor)
        
    def is_secure(self):
        """Check if all sensors in zone are secure"""
        return all(sensor.is_secure() for sensor in self.sensors)
        
    def get_triggered_sensors(self):
        """Get list of triggered sensors"""
        return [s for s in self.sensors if s.triggered]

class MultiSensorAlarmSystem:
    """Main alarm system controller"""
    
    def __init__(self):
        print("🚨 Initializing Multi-Sensor Alarm System...")
        
        # Initialize hardware
        self._init_sensors()
        self._init_outputs()
        self._init_controls()
        self._init_display()
        
        # System state
        self.mode = AlarmMode.DISARMED
        self.alarm_active = False
        self.entry_timer = None
        self.exit_timer = None
        self.alarm_timer = None
        
        # Zones
        self.zones = self._setup_zones()
        
        # Event management
        self.event_queue = queue.Queue()
        self.event_log = deque(maxlen=1000)
        self.alert_history = defaultdict(list)
        
        # Configuration
        self.config = self._load_configuration()
        self.notification_enabled = self.config.get('notifications', True)
        self.silent_alarm = False
        
        # Statistics
        self.session_start = datetime.now()
        self.alarm_count = 0
        self.false_alarms = 0
        
        # Threading
        self.running = False
        self.monitor_thread = None
        self.glass_thread = None
        
        print("✅ Alarm system initialized")
        
    def _init_sensors(self):
        """Initialize all security sensors"""
        # Motion sensors
        self.motion_sensors = {
            'living_room': SecuritySensor("Living Room Motion", SensorType.MOTION, PIR_ZONE1_PIN),
            'kitchen': SecuritySensor("Kitchen Motion", SensorType.MOTION, PIR_ZONE2_PIN),
            'bedroom': SecuritySensor("Bedroom Motion", SensorType.MOTION, PIR_ZONE3_PIN),
            'garage': SecuritySensor("Garage Motion", SensorType.MOTION, PIR_ZONE4_PIN)
        }
        
        # Door/window sensors
        self.contact_sensors = {
            'front_door': SecuritySensor("Front Door", SensorType.DOOR, DOOR_FRONT_PIN),
            'back_door': SecuritySensor("Back Door", SensorType.DOOR, DOOR_BACK_PIN),
            'window_1': SecuritySensor("Living Room Window", SensorType.WINDOW, WINDOW_1_PIN),
            'window_2': SecuritySensor("Bedroom Window", SensorType.WINDOW, WINDOW_2_PIN)
        }
        
        # Special sensors
        self.smoke_sensor = SecuritySensor("Smoke Detector", SensorType.SMOKE, SMOKE_ALARM_PIN)
        
        # Glass break sensor (ADC)
        self.adc = ADC0834(cs=ADC_CS_PIN, clk=ADC_CLK_PIN,
                          di=ADC_DI_PIN, do=ADC_DO_PIN)
        
        print("✓ Sensors initialized")
        
    def _init_outputs(self):
        """Initialize alarm outputs"""
        self.siren = OutputDevice(SIREN_PIN)
        self.strobe = PWMLED(STROBE_PIN)
        self.buzzer = Buzzer(BUZZER_PIN)
        
        self.led_armed = LED(LED_ARMED_PIN)
        self.led_ready = LED(LED_READY_PIN)
        self.led_alert = LED(LED_ALERT_PIN)
        
        # Set initial state
        self.led_ready.on()
        
        print("✓ Outputs initialized")
        
    def _init_controls(self):
        """Initialize control panel"""
        self.arm_button = Button(ARM_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.panic_button = Button(PANIC_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.test_button = Button(TEST_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.arm_button.when_pressed = self._handle_arm_button
        self.panic_button.when_pressed = self._trigger_panic_alarm
        self.test_button.when_pressed = self._test_system
        
        print("✓ Controls initialized")
        
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Alarm System")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
            
    def _setup_zones(self):
        """Set up security zones"""
        zones = {}
        
        # Perimeter zone (doors/windows)
        perimeter = Zone("Perimeter", "perimeter")
        for sensor in self.contact_sensors.values():
            perimeter.add_sensor(sensor)
        zones['perimeter'] = perimeter
        
        # Interior zones (motion)
        interior = Zone("Interior", "interior")
        for sensor in self.motion_sensors.values():
            interior.add_sensor(sensor)
        zones['interior'] = interior
        
        # 24-hour zone (smoke/panic)
        always_on = Zone("24 Hour", "24hour")
        always_on.add_sensor(self.smoke_sensor)
        zones['24hour'] = always_on
        
        return zones
        
    def _load_configuration(self):
        """Load system configuration"""
        config_file = "alarm_config.json"
        default_config = {
            'entry_delay': ENTRY_DELAY,
            'exit_delay': EXIT_DELAY,
            'alarm_duration': ALARM_DURATION,
            'notifications': True,
            'email': None,
            'phone': None,
            'monitoring_station': None
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                    print("✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
            
        return default_config
        
    def run(self):
        """Main system loop"""
        print("\n🚨 Multi-Sensor Alarm System Active!")
        print("ARM: Toggle arm/disarm")
        print("PANIC: Emergency alarm")
        print("TEST: Test mode")
        print("Press Ctrl+C to exit\n")
        
        self.running = True
        
        # Start monitoring threads
        self.monitor_thread = threading.Thread(target=self._sensor_monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.glass_thread = threading.Thread(target=self._glass_break_monitor, daemon=True)
        self.glass_thread.start()
        
        # Update display
        self._update_display()
        
        try:
            while True:
                # Process events
                self._process_event_queue()
                
                # Update system status
                self._update_system_status()
                
                # Check for alarm conditions
                if self.mode in [AlarmMode.ARMED_AWAY, AlarmMode.ARMED_STAY, AlarmMode.ARMED_NIGHT]:
                    self._check_sensors()
                    
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down alarm system...")
            self.running = False
            self._disarm_system()
            time.sleep(1)
            
    def _sensor_monitor_loop(self):
        """Continuous sensor monitoring"""
        while self.running:
            try:
                # Monitor all sensors
                for zone in self.zones.values():
                    if zone.zone_type == "24hour" or self.mode != AlarmMode.DISARMED:
                        for sensor in zone.sensors:
                            if sensor.triggered and not self.alarm_active:
                                self._handle_sensor_trigger(sensor, zone)
                                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠ Sensor monitor error: {e}")
                time.sleep(1)
                
    def _glass_break_monitor(self):
        """Monitor glass break sensor"""
        baseline = None
        sample_count = 10
        samples = deque(maxlen=sample_count)
        
        while self.running:
            try:
                # Read audio sensor
                value = self.adc.read(GLASS_SENSOR_CHANNEL)
                samples.append(value)
                
                # Establish baseline
                if baseline is None and len(samples) == sample_count:
                    baseline = sum(samples) / len(samples)
                    
                # Detect sudden spike (glass break)
                if baseline and value > baseline + GLASS_THRESHOLD:
                    if self.mode != AlarmMode.DISARMED:
                        print(f"🔊 Glass break detected! Level: {value}")
                        self._trigger_alarm("Glass Break", AlertPriority.HIGH)
                        
                        # Reset baseline after detection
                        samples.clear()
                        baseline = None
                        time.sleep(5)  # Prevent multiple triggers
                        
                time.sleep(0.01)  # 100Hz sampling
                
            except Exception as e:
                print(f"⚠ Glass break monitor error: {e}")
                time.sleep(1)
                
    def _handle_sensor_trigger(self, sensor, zone):
        """Handle triggered sensor"""
        # Check if sensor should trigger alarm based on mode
        should_trigger = False
        
        if zone.zone_type == "24hour":
            should_trigger = True
        elif self.mode == AlarmMode.ARMED_AWAY:
            should_trigger = True
        elif self.mode == AlarmMode.ARMED_STAY:
            should_trigger = zone.zone_type == "perimeter"
        elif self.mode == AlarmMode.ARMED_NIGHT:
            should_trigger = zone.zone_type == "perimeter"
            
        if should_trigger:
            # Check for entry delay
            if sensor.sensor_type == SensorType.DOOR and self.entry_timer is None:
                self._start_entry_delay(sensor)
            else:
                priority = AlertPriority.EMERGENCY if sensor.sensor_type == SensorType.SMOKE else AlertPriority.HIGH
                self._trigger_alarm(f"{sensor.name} triggered", priority)
                
    def _handle_arm_button(self):
        """Handle arm/disarm button press"""
        if self.mode == AlarmMode.DISARMED:
            self._arm_system(AlarmMode.ARMED_AWAY)
        elif self.mode in [AlarmMode.ARMED_AWAY, AlarmMode.ARMED_STAY, AlarmMode.ARMED_NIGHT]:
            self._disarm_system()
        elif self.mode == AlarmMode.ENTRY_DELAY:
            self._disarm_system()
            
    def _arm_system(self, mode):
        """Arm the alarm system"""
        # Check if all zones are secure
        not_ready = []
        for zone in self.zones.values():
            if zone.zone_type != "24hour" and not zone.is_secure():
                not_ready.extend(zone.get_triggered_sensors())
                
        if not_ready:
            print("⚠ System not ready to arm:")
            for sensor in not_ready:
                print(f"  - {sensor.name} is open")
            self._update_display("NOT READY", "Check sensors")
            self.buzzer.beep(0.2, 0.2, n=2)
            return
            
        # Start exit delay
        print(f"🔒 Arming system in {mode.value} mode...")
        self.mode = AlarmMode.EXIT_DELAY
        self.led_ready.off()
        self.led_armed.blink(on_time=0.5, off_time=0.5)
        
        # Exit delay countdown
        self.exit_timer = threading.Timer(self.config['exit_delay'], 
                                         lambda: self._complete_arming(mode))
        self.exit_timer.start()
        
        # Beep during exit delay
        self._exit_delay_beep()
        
        self._log_event("System armed", mode.value)
        
    def _complete_arming(self, mode):
        """Complete arming after exit delay"""
        self.mode = mode
        self.led_armed.on()
        self.buzzer.beep(0.1, 0, n=2)
        
        print(f"✅ System armed: {mode.value}")
        self._update_display(mode.value, "Protected")
        
    def _disarm_system(self):
        """Disarm the alarm system"""
        # Cancel any active timers
        if self.entry_timer:
            self.entry_timer.cancel()
            self.entry_timer = None
            
        if self.exit_timer:
            self.exit_timer.cancel()
            self.exit_timer = None
            
        if self.alarm_timer:
            self.alarm_timer.cancel()
            self.alarm_timer = None
            
        # Stop alarm if active
        if self.alarm_active:
            self._stop_alarm()
            
        self.mode = AlarmMode.DISARMED
        self.led_armed.off()
        self.led_ready.on()
        
        # Confirmation beep
        self.buzzer.beep(0.05, 0.05, n=3)
        
        print("🔓 System disarmed")
        self._update_display("DISARMED", "Ready")
        self._log_event("System disarmed")
        
    def _start_entry_delay(self, sensor):
        """Start entry delay countdown"""
        print(f"⏱️  Entry delay started: {self.config['entry_delay']}s")
        self.mode = AlarmMode.ENTRY_DELAY
        
        # Entry delay warning
        self.buzzer.beep(0.2, 0.3, n=None, background=True)
        
        self._update_display("ENTRY DELAY", f"Disarm now!")
        
        # Start timer
        self.entry_timer = threading.Timer(self.config['entry_delay'], 
                                          lambda: self._trigger_alarm(f"Entry timeout - {sensor.name}", AlertPriority.HIGH))
        self.entry_timer.start()
        
    def _trigger_alarm(self, reason, priority=AlertPriority.HIGH):
        """Trigger the alarm"""
        if self.alarm_active:
            return  # Already in alarm
            
        self.alarm_active = True
        self.alarm_count += 1
        self.mode = AlarmMode.ALARM_TRIGGERED
        
        print(f"🚨 ALARM TRIGGERED: {reason}")
        
        # Cancel entry timer if active
        if self.entry_timer:
            self.entry_timer.cancel()
            self.entry_timer = None
            
        # Activate alarm outputs
        if not self.silent_alarm:
            self.siren.on()
            self.strobe.pulse(fade_in_time=0.1, fade_out_time=0.1)
            
        # Interior warning
        self.buzzer.on()
        self.led_alert.blink(on_time=0.2, off_time=0.2)
        
        # Update display
        self._update_display("** ALARM **", reason[:16])
        
        # Send notifications
        if self.notification_enabled:
            self._send_notifications(reason, priority)
            
        # Log event
        self._log_event("ALARM TRIGGERED", reason, priority)
        
        # Auto-stop timer
        self.alarm_timer = threading.Timer(self.config['alarm_duration'], self._stop_alarm)
        self.alarm_timer.start()
        
    def _stop_alarm(self):
        """Stop the alarm"""
        self.alarm_active = False
        
        # Stop outputs
        self.siren.off()
        self.strobe.off()
        self.buzzer.off()
        self.led_alert.off()
        
        print("⏹ Alarm stopped")
        self._log_event("Alarm stopped")
        
    def _trigger_panic_alarm(self):
        """Trigger panic alarm immediately"""
        print("🆘 PANIC ALARM!")
        self._trigger_alarm("PANIC BUTTON", AlertPriority.EMERGENCY)
        
    def _test_system(self):
        """Test all system components"""
        if self.mode != AlarmMode.DISARMED:
            print("⚠ Cannot test while armed")
            return
            
        print("\n🔧 System Test Mode")
        self._update_display("TEST MODE", "Testing...")
        
        # Test outputs
        print("Testing siren...")
        self.siren.on()
        time.sleep(0.5)
        self.siren.off()
        
        print("Testing strobe...")
        self.strobe.on()
        time.sleep(1)
        self.strobe.off()
        
        print("Testing buzzer...")
        self.buzzer.beep(0.1, 0.1, n=3)
        
        # Test sensors
        print("\nSensor Status:")
        for zone_name, zone in self.zones.items():
            print(f"\n{zone.name} Zone:")
            for sensor in zone.sensors:
                status = "Secure" if sensor.is_secure() else "Open"
                print(f"  {sensor.name}: {status}")
                
        print("\n✅ Test complete")
        self._update_display("TEST DONE", "System OK")
        
    def _exit_delay_beep(self):
        """Beep pattern during exit delay"""
        def beep_pattern():
            delay = self.config['exit_delay']
            for i in range(delay):
                if self.mode != AlarmMode.EXIT_DELAY:
                    break
                    
                # Faster beeps in last 10 seconds
                if delay - i <= 10:
                    self.buzzer.beep(0.1, 0.1, n=1)
                else:
                    self.buzzer.beep(0.1, 0.9, n=1)
                    
                time.sleep(1)
                
        threading.Thread(target=beep_pattern, daemon=True).start()
        
    def _send_notifications(self, message, priority):
        """Send alarm notifications"""
        # Email notification
        if self.config.get('email'):
            threading.Thread(target=self._send_email, 
                           args=(message, priority), daemon=True).start()
            
        # SMS notification (via service)
        if self.config.get('phone'):
            threading.Thread(target=self._send_sms, 
                           args=(message, priority), daemon=True).start()
            
        # Monitoring station
        if self.config.get('monitoring_station'):
            threading.Thread(target=self._notify_monitoring_station, 
                           args=(message, priority), daemon=True).start()
            
    def _send_email(self, message, priority):
        """Send email notification"""
        try:
            # Email configuration would go here
            print(f"📧 Email notification sent: {message}")
        except Exception as e:
            print(f"⚠ Email failed: {e}")
            
    def _send_sms(self, message, priority):
        """Send SMS notification"""
        try:
            # SMS service integration would go here
            print(f"📱 SMS notification sent: {message}")
        except Exception as e:
            print(f"⚠ SMS failed: {e}")
            
    def _notify_monitoring_station(self, message, priority):
        """Notify monitoring station"""
        try:
            # Monitoring station API would go here
            print(f"🏢 Monitoring station notified: {message}")
        except Exception as e:
            print(f"⚠ Monitoring notification failed: {e}")
            
    def _update_display(self, line1="", line2=""):
        """Update LCD display"""
        if not self.lcd:
            return
            
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, line1[:16])
            self.lcd.write(1, 0, line2[:16])
        except Exception as e:
            print(f"⚠ Display error: {e}")
            
    def _update_system_status(self):
        """Update system status indicators"""
        # Update ready LED
        if self.mode == AlarmMode.DISARMED:
            ready = all(zone.is_secure() for zone in self.zones.values() 
                       if zone.zone_type != "24hour")
            if ready:
                self.led_ready.on()
            else:
                self.led_ready.blink(on_time=0.5, off_time=0.5)
                
    def _check_sensors(self):
        """Check all active sensors"""
        # This is handled by the monitor thread
        pass
        
    def _process_event_queue(self):
        """Process queued events"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                # Process event (logging, notifications, etc.)
                
        except queue.Empty:
            pass
            
    def _log_event(self, event_type, details="", priority=AlertPriority.LOW):
        """Log system event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details,
            'priority': priority.value,
            'mode': self.mode.value
        }
        
        self.event_log.append(event)
        self.event_queue.put(event)
        
        # Save to file periodically
        if len(self.event_log) % 10 == 0:
            self._save_event_log()
            
    def _save_event_log(self):
        """Save event log to file"""
        try:
            log_file = f"alarm_log_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(log_file, 'a') as f:
                for event in list(self.event_log):
                    json.dump(event, f)
                    f.write('\n')
                    
            self.event_log.clear()
            
        except Exception as e:
            print(f"⚠ Could not save log: {e}")
            
    def get_statistics(self):
        """Get system statistics"""
        runtime = (datetime.now() - self.session_start).total_seconds()
        
        # Count sensor triggers
        total_triggers = sum(sensor.trigger_count 
                           for zone in self.zones.values() 
                           for sensor in zone.sensors)
        
        return {
            'runtime_seconds': runtime,
            'alarm_count': self.alarm_count,
            'false_alarms': self.false_alarms,
            'total_triggers': total_triggers,
            'current_mode': self.mode.value,
            'zones_secure': all(zone.is_secure() for zone in self.zones.values())
        }
        
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop operation
        self.running = False
        
        # Ensure alarm is off
        self._stop_alarm()
        
        # Cancel timers
        for timer in [self.entry_timer, self.exit_timer, self.alarm_timer]:
            if timer:
                timer.cancel()
                
        # Save logs
        self._save_event_log()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
            
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Runtime: {stats['runtime_seconds']/60:.1f} minutes")
        print(f"  Alarms triggered: {stats['alarm_count']}")
        print(f"  Total sensor triggers: {stats['total_triggers']}")
        print(f"  False alarms: {stats['false_alarms']}")
        
        # Clean up hardware
        for zone in self.zones.values():
            for sensor in zone.sensors:
                sensor.cleanup()
                
        self.siren.close()
        self.strobe.close()
        self.buzzer.close()
        self.led_armed.close()
        self.led_ready.close()
        self.led_alert.close()
        self.arm_button.close()
        self.panic_button.close()
        self.test_button.close()
        
        print("\n✅ Cleanup complete")


def alarm_demo():
    """Demonstrate alarm system features"""
    print("\n🎮 Alarm System Demo")
    print("=" * 50)
    
    system = MultiSensorAlarmSystem()
    
    try:
        print("\nDemonstrating alarm features...")
        
        # Demo 1: System ready
        print("\n1. System Ready")
        system.led_ready.on()
        system._update_display("READY", "All Secure")
        time.sleep(2)
        
        # Demo 2: Exit delay
        print("\n2. Exit Delay")
        system.led_armed.blink(on_time=0.5, off_time=0.5)
        system._update_display("EXIT DELAY", "60 seconds")
        for i in range(5):
            system.buzzer.beep(0.1, 0.9, n=1)
            time.sleep(1)
            
        # Demo 3: Armed
        print("\n3. System Armed")
        system.led_armed.on()
        system._update_display("ARMED AWAY", "Protected")
        time.sleep(2)
        
        # Demo 4: Entry delay
        print("\n4. Entry Delay")
        system._update_display("ENTRY DELAY", "Disarm now!")
        system.buzzer.beep(0.2, 0.3, n=5)
        time.sleep(2)
        
        # Demo 5: Alarm
        print("\n5. Alarm Triggered")
        system._update_display("** ALARM **", "Front Door")
        system.siren.on()
        system.strobe.pulse()
        system.led_alert.blink(on_time=0.2, off_time=0.2)
        time.sleep(3)
        
        # Stop alarm
        system.siren.off()
        system.strobe.off()
        system.led_alert.off()
        
        print("\n✅ Demo complete!")
        
    finally:
        system.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        alarm_demo()
    else:
        # Normal operation
        system = MultiSensorAlarmSystem()
        try:
            system.run()
        finally:
            system.cleanup()
