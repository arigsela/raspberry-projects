#!/usr/bin/env python3
"""
Object Counting Device
Intelligent object detection and counting system using ultrasonic sensors
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

from lcd1602 import LCD1602
from adc0834 import ADC0834
import time
import signal
import threading
import json
from datetime import datetime, timedelta
import statistics
import math

from gpiozero import DistanceSensor, Button, LED, PWMLED, Buzzer

# GPIO Configuration
# Ultrasonic sensors for counting zones
ENTRANCE_TRIG_PIN = 23       # Entrance sensor trigger
ENTRANCE_ECHO_PIN = 24       # Entrance sensor echo
EXIT_TRIG_PIN = 25           # Exit sensor trigger  
EXIT_ECHO_PIN = 8            # Exit sensor echo
REFERENCE_TRIG_PIN = 7       # Reference/calibration sensor
REFERENCE_ECHO_PIN = 1       # Reference sensor echo

# LCD Display (I2C)
LCD_I2C_ADDRESS = 0x27       # I2C address for LCD

# Control inputs
COUNT_RESET_PIN = 17         # Reset count button
MODE_BUTTON_PIN = 18         # Mode selection button
CALIBRATE_BUTTON_PIN = 27    # Calibration button
SETTINGS_BUTTON_PIN = 22     # Settings adjustment

# Status indicators
COUNT_LED_PIN = 26           # Object detected LED
DIRECTION_LED_PIN = 19       # Direction indicator (in/out)
STATUS_LED_PIN = 20          # System status LED
ERROR_LED_PIN = 21           # Error condition LED

# Audio feedback
COUNT_BUZZER_PIN = 13        # Count confirmation buzzer
ALERT_BUZZER_PIN = 12        # Alert/error buzzer

# ADC for sensitivity adjustment (potentiometer)
ADC_CS_PIN = 5
ADC_CLK_PIN = 6
ADC_DI_PIN = 16
ADC_DO_PIN = 26

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class ObjectCountingDevice:
    """Intelligent object counting system with directional detection"""
    
    def __init__(self):
        """Initialize object counting system"""
        
        # Initialize ultrasonic sensors
        try:
            self.entrance_sensor = DistanceSensor(echo=ENTRANCE_ECHO_PIN, trigger=ENTRANCE_TRIG_PIN, 
                                                max_distance=2.0, threshold_distance=0.3)
            self.exit_sensor = DistanceSensor(echo=EXIT_ECHO_PIN, trigger=EXIT_TRIG_PIN,
                                            max_distance=2.0, threshold_distance=0.3) 
            self.reference_sensor = DistanceSensor(echo=REFERENCE_ECHO_PIN, trigger=REFERENCE_TRIG_PIN,
                                                 max_distance=2.0, threshold_distance=0.3)
            self.has_sensors = True
            print("✓ Ultrasonic sensors initialized")
        except Exception as e:
            self.has_sensors = False
            print(f"✗ Ultrasonic sensors failed: {e}")
        
        # Initialize LCD display
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Object Counter")
            self.lcd.write(1, 0, "Initializing...")
            self.has_lcd = True
            print("✓ LCD display initialized")
        except Exception as e:
            self.has_lcd = False
            print(f"✗ LCD display failed: {e}")
        
        # Initialize ADC for sensitivity control
        try:
            self.adc = ADC0834(ADC_CS_PIN, ADC_CLK_PIN, ADC_DI_PIN, ADC_DO_PIN)
            self.has_adc = True
            print("✓ ADC initialized")
        except Exception as e:
            self.has_adc = False
            print(f"✗ ADC failed: {e}")
        
        # Initialize control buttons
        try:
            self.reset_button = Button(COUNT_RESET_PIN, bounce_time=0.2)
            self.mode_button = Button(MODE_BUTTON_PIN, bounce_time=0.2)
            self.calibrate_button = Button(CALIBRATE_BUTTON_PIN, bounce_time=0.2)
            self.settings_button = Button(SETTINGS_BUTTON_PIN, bounce_time=0.2)
            
            # Setup button callbacks
            self.reset_button.when_pressed = self._reset_count
            self.mode_button.when_pressed = self._cycle_mode
            self.calibrate_button.when_pressed = self._start_calibration
            self.settings_button.when_pressed = self._adjust_settings
            
            self.has_buttons = True
            print("✓ Control buttons initialized")
        except Exception as e:
            self.has_buttons = False
            print(f"✗ Control buttons failed: {e}")
        
        # Initialize status indicators
        try:
            self.count_led = PWMLED(COUNT_LED_PIN)      # PWM for brightness effects
            self.direction_led = LED(DIRECTION_LED_PIN)
            self.status_led = PWMLED(STATUS_LED_PIN)    # PWM for breathing effect
            self.error_led = LED(ERROR_LED_PIN)
            
            self.count_buzzer = Buzzer(COUNT_BUZZER_PIN)
            self.alert_buzzer = Buzzer(ALERT_BUZZER_PIN)
            
            self.has_indicators = True
            print("✓ Status indicators initialized")
        except Exception as e:
            self.has_indicators = False
            print(f"✗ Status indicators failed: {e}")
        
        # Counting system state
        self.total_count = 0
        self.in_count = 0                # Objects entering
        self.out_count = 0               # Objects exiting
        self.net_count = 0               # Net count (in - out)
        
        # Detection state
        self.entrance_triggered = False
        self.exit_triggered = False
        self.detection_sequence = []     # Track detection sequence for direction
        self.last_detection_time = 0
        self.detection_timeout = 3.0     # seconds
        
        # Operating modes
        self.counting_modes = ["bidirectional", "entrance_only", "exit_only", "presence", "batch"]
        self.current_mode = 0
        
        # Calibration and settings
        self.baseline_distance = 1.0     # meters - no object present
        self.detection_threshold = 0.2   # meters - object detection sensitivity
        self.min_object_size = 0.05      # meters - minimum object size
        self.max_object_size = 0.5       # meters - maximum object size
        self.detection_stability = 3     # consecutive readings required
        
        # Advanced detection parameters
        self.false_positive_filter = True
        self.size_filtering = True
        self.speed_analysis = True
        self.multi_object_detection = True
        
        # Statistics and logging
        self.session_start_time = time.time()
        self.hourly_counts = {}
        self.daily_totals = {}
        self.detection_history = []
        self.false_positive_count = 0
        
        # Background monitoring
        self.monitoring_active = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        
        # Load saved settings
        self.settings = self.load_settings()
        self._apply_settings()
        
        # Setup sensor callbacks if available
        if self.has_sensors:
            self.entrance_sensor.when_in_range = self._on_entrance_triggered
            self.entrance_sensor.when_out_of_range = self._on_entrance_cleared
            self.exit_sensor.when_in_range = self._on_exit_triggered
            self.exit_sensor.when_out_of_range = self._on_exit_cleared
        
        # Start background processes
        self.detection_thread.start()
        self.display_thread.start()
        
        # Initialize display and indicators
        self._update_display()
        if self.has_indicators:
            self.status_led.pulse()  # Breathing effect when ready
            self.count_buzzer.beep(0.1, 0.1, n=3)  # Startup sound
        
        print("🔢 Object Counting Device Initialized")
        print(f"Mode: {self.counting_modes[self.current_mode].upper()}")
        print("Ready to count objects!")
    
    def _detection_loop(self):
        """Main object detection and analysis loop"""
        consecutive_detections = {'entrance': 0, 'exit': 0}
        detection_buffer = {'entrance': [], 'exit': [], 'reference': []}
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                if self.has_sensors:
                    # Read all sensors
                    entrance_dist = self.entrance_sensor.distance
                    exit_dist = self.exit_sensor.distance  
                    reference_dist = self.reference_sensor.distance
                    
                    # Update detection buffers for stability analysis
                    detection_buffer['entrance'].append(entrance_dist)
                    detection_buffer['exit'].append(exit_dist)
                    detection_buffer['reference'].append(reference_dist)
                    
                    # Keep buffer size manageable
                    for key in detection_buffer:
                        if len(detection_buffer[key]) > 10:
                            detection_buffer[key].pop(0)
                    
                    # Analyze entrance sensor
                    if self._is_stable_detection(detection_buffer['entrance'], self.detection_threshold):
                        consecutive_detections['entrance'] += 1
                    else:
                        consecutive_detections['entrance'] = 0
                    
                    # Analyze exit sensor
                    if self._is_stable_detection(detection_buffer['exit'], self.detection_threshold):
                        consecutive_detections['exit'] += 1
                    else:
                        consecutive_detections['exit'] = 0
                    
                    # Check for confirmed detections
                    if (consecutive_detections['entrance'] >= self.detection_stability and 
                        not self.entrance_triggered):
                        self._on_entrance_triggered()
                    elif (consecutive_detections['entrance'] == 0 and self.entrance_triggered):
                        self._on_entrance_cleared()
                    
                    if (consecutive_detections['exit'] >= self.detection_stability and 
                        not self.exit_triggered):
                        self._on_exit_triggered()
                    elif (consecutive_detections['exit'] == 0 and self.exit_triggered):
                        self._on_exit_cleared()
                    
                    # Clean up old detection sequences
                    if (current_time - self.last_detection_time > self.detection_timeout and 
                        self.detection_sequence):
                        self._process_detection_sequence()
                
                # Update sensitivity from potentiometer
                if self.has_adc:
                    sensitivity_raw = self.adc.read_channel(0)
                    # Map ADC reading (0-255) to threshold (0.05-0.5m)
                    self.detection_threshold = 0.05 + (sensitivity_raw / 255.0) * 0.45
                
                time.sleep(0.05)  # 20Hz update rate
                
            except Exception as e:
                print(f"Detection loop error: {e}")
                time.sleep(1)
    
    def _is_stable_detection(self, readings, threshold):
        """Check if readings indicate stable object detection"""
        if len(readings) < 3:
            return False
        
        # Check if recent readings are below threshold
        recent_readings = readings[-3:]
        return all(reading < threshold for reading in recent_readings)
    
    def _on_entrance_triggered(self):
        """Handle entrance sensor triggering"""
        if self.entrance_triggered:
            return
        
        self.entrance_triggered = True
        self.last_detection_time = time.time()
        
        # Add to detection sequence
        self.detection_sequence.append({
            'sensor': 'entrance',
            'action': 'triggered',
            'timestamp': self.last_detection_time
        })
        
        # Visual feedback
        if self.has_indicators:
            self.count_led.on()
        
        print("📍 Entrance sensor triggered")
    
    def _on_entrance_cleared(self):
        """Handle entrance sensor clearing"""
        if not self.entrance_triggered:
            return
        
        self.entrance_triggered = False
        self.last_detection_time = time.time()
        
        # Add to detection sequence
        self.detection_sequence.append({
            'sensor': 'entrance',
            'action': 'cleared',
            'timestamp': self.last_detection_time
        })
        
        # Visual feedback
        if self.has_indicators:
            self.count_led.off()
        
        print("📍 Entrance sensor cleared")
    
    def _on_exit_triggered(self):
        """Handle exit sensor triggering"""
        if self.exit_triggered:
            return
        
        self.exit_triggered = True
        self.last_detection_time = time.time()
        
        # Add to detection sequence
        self.detection_sequence.append({
            'sensor': 'exit',
            'action': 'triggered',
            'timestamp': self.last_detection_time
        })
        
        # Visual feedback
        if self.has_indicators:
            self.direction_led.on()
        
        print("📍 Exit sensor triggered")
    
    def _on_exit_cleared(self):
        """Handle exit sensor clearing"""
        if not self.exit_triggered:
            return
        
        self.exit_triggered = False
        self.last_detection_time = time.time()
        
        # Add to detection sequence
        self.detection_sequence.append({
            'sensor': 'exit',
            'action': 'cleared',
            'timestamp': self.last_detection_time
        })
        
        # Visual feedback
        if self.has_indicators:
            self.direction_led.off()
        
        print("📍 Exit sensor cleared")
    
    def _process_detection_sequence(self):
        """Analyze detection sequence to determine object movement"""
        if len(self.detection_sequence) < 2:
            self.detection_sequence.clear()
            return
        
        # Analyze sequence for direction patterns
        direction = self._analyze_direction_pattern(self.detection_sequence)
        
        if direction == 'entering':
            self._count_object_entering()
        elif direction == 'exiting':
            self._count_object_exiting()
        elif direction == 'false_positive':
            self.false_positive_count += 1
            print("⚠ False positive detection filtered")
        
        # Clear sequence for next detection
        self.detection_sequence.clear()
    
    def _analyze_direction_pattern(self, sequence):
        """Analyze sensor sequence to determine object direction"""
        if len(sequence) < 2:
            return 'unknown'
        
        # Extract sensor events in chronological order
        events = [(event['sensor'], event['action'], event['timestamp']) for event in sequence]
        events.sort(key=lambda x: x[2])  # Sort by timestamp
        
        # Pattern analysis for entering: entrance triggered first, then exit
        # Pattern analysis for exiting: exit triggered first, then entrance
        
        first_trigger = None
        last_clear = None
        
        for sensor, action, timestamp in events:
            if action == 'triggered' and first_trigger is None:
                first_trigger = sensor
            if action == 'cleared':
                last_clear = sensor
        
        # Determine direction based on pattern
        if first_trigger == 'entrance':
            if any(event[0] == 'exit' and event[1] == 'triggered' for event in events):
                return 'entering'
        elif first_trigger == 'exit':
            if any(event[0] == 'entrance' and event[1] == 'triggered' for event in events):
                return 'exiting'
        
        # Check for false positives (very short duration, single sensor)
        duration = events[-1][2] - events[0][2] if len(events) > 1 else 0
        if duration < 0.1:  # Very quick detection
            return 'false_positive'
        
        # Single sensor trigger without clear direction
        sensors_involved = set(event[0] for event in events)
        if len(sensors_involved) == 1:
            return 'unknown'
        
        return 'unknown'
    
    def _count_object_entering(self):
        """Count object entering the monitored area"""
        mode = self.counting_modes[self.current_mode]
        
        if mode in ['bidirectional', 'entrance_only']:
            self.in_count += 1
            self.total_count += 1
            self.net_count = self.in_count - self.out_count
            
            # Log the event
            self._log_detection_event('entering')
            
            # Audio/visual feedback
            if self.has_indicators:
                self.count_buzzer.beep(0.1, 0.0, n=1)  # Single beep for entering
                self.count_led.blink(on_time=0.2, off_time=0.2, n=3)
            
            print(f"➡️ Object ENTERING - Count: {self.total_count}")
            self._update_display()
    
    def _count_object_exiting(self):
        """Count object exiting the monitored area"""
        mode = self.counting_modes[self.current_mode]
        
        if mode in ['bidirectional', 'exit_only']:
            self.out_count += 1
            if mode == 'bidirectional':
                self.total_count += 1
            elif mode == 'exit_only':
                self.total_count += 1
            
            self.net_count = self.in_count - self.out_count
            
            # Log the event
            self._log_detection_event('exiting')
            
            # Audio/visual feedback
            if self.has_indicators:
                self.count_buzzer.beep(0.1, 0.1, n=2)  # Double beep for exiting
                self.direction_led.blink(on_time=0.2, off_time=0.2, n=3)
            
            print(f"⬅️ Object EXITING - Count: {self.total_count}")
            self._update_display()
    
    def _log_detection_event(self, direction):
        """Log detection event with timestamp and context"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'direction': direction,
            'mode': self.counting_modes[self.current_mode],
            'total_count': self.total_count,
            'in_count': self.in_count,
            'out_count': self.out_count,
            'net_count': self.net_count
        }
        
        self.detection_history.append(event)
        
        # Update hourly statistics
        current_hour = datetime.now().hour
        if current_hour not in self.hourly_counts:
            self.hourly_counts[current_hour] = {'in': 0, 'out': 0, 'total': 0}
        
        if direction == 'entering':
            self.hourly_counts[current_hour]['in'] += 1
        elif direction == 'exiting':
            self.hourly_counts[current_hour]['out'] += 1
        
        self.hourly_counts[current_hour]['total'] += 1
    
    def _display_loop(self):
        """Background display update loop"""
        display_cycle = 0
        
        while self.monitoring_active:
            try:
                if self.has_lcd:
                    # Cycle through different display modes every 3 seconds
                    if display_cycle % 60 == 0:  # Every 3 seconds (60 * 0.05s)
                        self._update_display()
                    elif display_cycle % 120 == 60:  # Show stats
                        self._show_statistics_display()
                    elif display_cycle % 180 == 120:  # Show mode info
                        self._show_mode_display()
                    
                    display_cycle += 1
                    if display_cycle >= 180:
                        display_cycle = 0
                
                time.sleep(0.05)
                
            except Exception as e:
                print(f"Display loop error: {e}")
                time.sleep(1)
    
    def _update_display(self):
        """Update LCD with current count information"""
        if not self.has_lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Line 1: Current count and mode indicator
            mode_char = {
                'bidirectional': '⇄',
                'entrance_only': '→',
                'exit_only': '←',
                'presence': '●',
                'batch': '#'
            }.get(self.counting_modes[self.current_mode], '?')
            
            line1 = f"Count: {self.total_count:4d} {mode_char}"
            self.lcd.write(0, 0, line1)
            
            # Line 2: Direction counts or net count
            if self.counting_modes[self.current_mode] == 'bidirectional':
                line2 = f"In:{self.in_count:3d} Out:{self.out_count:3d}"
            else:
                uptime_hours = (time.time() - self.session_start_time) / 3600
                rate = self.total_count / uptime_hours if uptime_hours > 0 else 0
                line2 = f"Rate: {rate:4.1f}/hr"
            
            self.lcd.write(1, 0, line2)
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def _show_statistics_display(self):
        """Show statistics on LCD"""
        if not self.has_lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Calculate session statistics
            uptime_hours = (time.time() - self.session_start_time) / 3600
            avg_rate = self.total_count / uptime_hours if uptime_hours > 0 else 0
            
            line1 = f"Rate:{avg_rate:5.1f}/hr"
            line2 = f"Time:{uptime_hours:5.1f}hr"
            
            self.lcd.write(0, 0, line1)
            self.lcd.write(1, 0, line2)
            
        except Exception as e:
            print(f"Statistics display error: {e}")
    
    def _show_mode_display(self):
        """Show current mode on LCD"""
        if not self.has_lcd:
            return
        
        try:
            self.lcd.clear()
            
            mode_name = self.counting_modes[self.current_mode]
            line1 = f"Mode: {mode_name[:10]}"
            
            # Show detection sensitivity
            threshold_cm = self.detection_threshold * 100
            line2 = f"Sens: {threshold_cm:3.0f}cm"
            
            self.lcd.write(0, 0, line1)
            self.lcd.write(1, 0, line2)
            
        except Exception as e:
            print(f"Mode display error: {e}")
    
    def _reset_count(self):
        """Reset all counters"""
        print("🔄 Resetting counters...")
        
        self.total_count = 0
        self.in_count = 0
        self.out_count = 0
        self.net_count = 0
        
        # Save reset event
        reset_event = {
            'timestamp': datetime.now().isoformat(),
            'action': 'count_reset',
            'previous_total': self.total_count
        }
        self.detection_history.append(reset_event)
        
        # Audio/visual feedback
        if self.has_indicators:
            self.alert_buzzer.beep(0.2, 0.2, n=3)
            # Flash all LEDs
            for led in [self.count_led, self.direction_led, self.error_led]:
                led.blink(on_time=0.1, off_time=0.1, n=5, background=True)
        
        self._update_display()
        print("✅ Counters reset to zero")
    
    def _cycle_mode(self):
        """Cycle through counting modes"""
        self.current_mode = (self.current_mode + 1) % len(self.counting_modes)
        mode_name = self.counting_modes[self.current_mode]
        
        print(f"🔄 Mode: {mode_name.upper()}")
        
        # Audio feedback - beeps indicate mode number
        if self.has_indicators:
            self.count_buzzer.beep(0.1, 0.1, n=self.current_mode + 1)
        
        self._update_display()
    
    def _start_calibration(self):
        """Start sensor calibration process"""
        print("\n🎯 Starting calibration...")
        
        if not self.has_sensors:
            print("❌ No sensors available for calibration")
            return
        
        if self.has_lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Calibrating...")
            self.lcd.write(1, 0, "Keep area clear")
        
        # Calibrate baseline distances
        calibration_readings = {'entrance': [], 'exit': [], 'reference': []}
        
        # Take multiple readings for stability
        print("📏 Taking baseline measurements...")
        for i in range(20):
            calibration_readings['entrance'].append(self.entrance_sensor.distance)
            calibration_readings['exit'].append(self.exit_sensor.distance)
            calibration_readings['reference'].append(self.reference_sensor.distance)
            time.sleep(0.1)
        
        # Calculate baseline distances
        self.baseline_distance = statistics.median(calibration_readings['reference'])
        entrance_baseline = statistics.median(calibration_readings['entrance'])
        exit_baseline = statistics.median(calibration_readings['exit'])
        
        print(f"✅ Calibration complete:")
        print(f"   Reference distance: {self.baseline_distance:.2f}m")
        print(f"   Entrance baseline: {entrance_baseline:.2f}m")
        print(f"   Exit baseline: {exit_baseline:.2f}m")
        
        # Update detection threshold based on calibration
        self.detection_threshold = min(0.3, self.baseline_distance * 0.8)
        
        if self.has_indicators:
            self.count_buzzer.beep(0.5, 0.0, n=1)  # Success sound
        
        self._update_display()
    
    def _adjust_settings(self):
        """Adjust detection settings"""
        settings = ['sensitivity', 'stability', 'timeout']
        current_setting = getattr(self, '_current_setting', 0)
        
        if settings[current_setting] == 'sensitivity':
            # Cycle sensitivity levels
            sensitivities = [0.05, 0.1, 0.2, 0.3, 0.5]
            current_index = sensitivities.index(self.detection_threshold) if self.detection_threshold in sensitivities else 2
            next_index = (current_index + 1) % len(sensitivities)
            self.detection_threshold = sensitivities[next_index]
            print(f"🎛️ Sensitivity: {self.detection_threshold:.2f}m")
            
        elif settings[current_setting] == 'stability':
            # Cycle stability requirements
            stabilities = [1, 2, 3, 5, 8]
            current_index = stabilities.index(self.detection_stability) if self.detection_stability in stabilities else 2
            next_index = (current_index + 1) % len(stabilities)
            self.detection_stability = stabilities[next_index]
            print(f"🎛️ Stability: {self.detection_stability} readings")
            
        elif settings[current_setting] == 'timeout':
            # Cycle timeout values
            timeouts = [1.0, 2.0, 3.0, 5.0, 10.0]
            current_index = timeouts.index(self.detection_timeout) if self.detection_timeout in timeouts else 2
            next_index = (current_index + 1) % len(timeouts)
            self.detection_timeout = timeouts[next_index]
            print(f"🎛️ Timeout: {self.detection_timeout:.1f}s")
        
        # Cycle to next setting
        self._current_setting = (current_setting + 1) % len(settings)
        
        if self.has_indicators:
            self.count_buzzer.beep(0.05, 0.05, n=current_setting + 1)
    
    def _apply_settings(self):
        """Apply loaded settings"""
        if 'detection_threshold' in self.settings:
            self.detection_threshold = self.settings['detection_threshold']
        if 'detection_stability' in self.settings:
            self.detection_stability = self.settings['detection_stability']
        if 'detection_timeout' in self.settings:
            self.detection_timeout = self.settings['detection_timeout']
        if 'current_mode' in self.settings:
            self.current_mode = self.settings['current_mode']
    
    def load_settings(self):
        """Load system settings from file"""
        try:
            with open('counting_device_settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'detection_threshold': self.detection_threshold,
            'detection_stability': self.detection_stability,
            'detection_timeout': self.detection_timeout,
            'baseline_distance': self.baseline_distance,
            'current_mode': self.current_mode,
            'false_positive_filter': self.false_positive_filter,
            'size_filtering': self.size_filtering
        }
        
        with open('counting_device_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    def save_detection_log(self):
        """Save detection history to file"""
        try:
            with open('detection_log.json', 'w') as f:
                json.dump(self.detection_history, f, indent=2)
        except Exception as e:
            print(f"Failed to save detection log: {e}")
    
    def get_statistics(self):
        """Get comprehensive counting statistics"""
        uptime = time.time() - self.session_start_time
        
        return {
            'uptime_hours': uptime / 3600,
            'total_count': self.total_count,
            'in_count': self.in_count,
            'out_count': self.out_count,
            'net_count': self.net_count,
            'current_mode': self.counting_modes[self.current_mode],
            'detection_rate': self.total_count / (uptime / 3600) if uptime > 0 else 0,
            'false_positives': self.false_positive_count,
            'accuracy': (self.total_count / (self.total_count + self.false_positive_count) * 100) if (self.total_count + self.false_positive_count) > 0 else 100,
            'detections_logged': len(self.detection_history)
        }
    
    def get_hourly_report(self):
        """Get hourly counting report"""
        return {
            'hourly_counts': self.hourly_counts,
            'peak_hour': max(self.hourly_counts.items(), key=lambda x: x[1]['total']) if self.hourly_counts else None,
            'total_hours_active': len(self.hourly_counts)
        }
    
    def cleanup(self):
        """Clean up system resources"""
        print("\n🧹 Cleaning up counting device...")
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Wait for threads to finish
        if self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2)
        if self.display_thread.is_alive():
            self.display_thread.join(timeout=2)
        
        # Save data
        self.save_settings()
        self.save_detection_log()
        
        # Clear display
        if self.has_lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Shutdown")
            self.lcd.write(1, 0, f"Total: {self.total_count}")
            time.sleep(2)
            self.lcd.clear()
        
        # Turn off indicators
        if self.has_indicators:
            for led in [self.count_led, self.direction_led, self.status_led, self.error_led]:
                led.off()
            self.count_buzzer.beep(0.2, 0.1, n=3)  # Shutdown sound
        
        # Close hardware
        if self.has_sensors:
            self.entrance_sensor.close()
            self.exit_sensor.close()
            self.reference_sensor.close()
        
        if self.has_buttons:
            self.reset_button.close()
            self.mode_button.close()
            self.calibrate_button.close()
            self.settings_button.close()
        
        if self.has_indicators:
            self.count_led.close()
            self.direction_led.close()
            self.status_led.close()
            self.error_led.close()
            self.count_buzzer.close()
            self.alert_buzzer.close()
        
        if self.has_adc:
            self.adc.cleanup()

def interactive_demo():
    """Interactive counting device demonstration"""
    print("\n🔢 Interactive Object Counting Demo")
    print("Real-time object detection and counting")
    print("Press Ctrl+C to exit")
    
    try:
        counter = ObjectCountingDevice()
        
        print(f"\n📋 Controls:")
        print("🔄 RESET Button: Reset all counters")
        print("🎛️ MODE Button: Cycle counting modes")
        print("🎯 CALIBRATE Button: Calibrate sensors")
        print("⚙️ SETTINGS Button: Adjust detection parameters")
        
        print(f"\n🎮 Counting Modes:")
        for i, mode in enumerate(counter.counting_modes):
            indicator = "👉" if i == counter.current_mode else "  "
            print(f"{indicator} {i+1}. {mode.upper()}")
        
        start_time = time.time()
        
        while True:
            # Display real-time status
            stats = counter.get_statistics()
            elapsed = time.time() - start_time
            
            mode_icon = {"bidirectional": "⇄", "entrance_only": "→", "exit_only": "←", 
                        "presence": "●", "batch": "#"}
            current_icon = mode_icon.get(stats['current_mode'], "🔢")
            
            entrance_status = "🔴" if counter.entrance_triggered else "⚫"
            exit_status = "🔴" if counter.exit_triggered else "⚫"
            
            print(f"\r{current_icon} {stats['current_mode'].upper()} | "
                  f"Total: {stats['total_count']:4d} | "
                  f"In: {stats['in_count']:3d} | Out: {stats['out_count']:3d} | "
                  f"Rate: {stats['detection_rate']:4.1f}/hr | "
                  f"{entrance_status}{exit_status} | "
                  f"Time: {elapsed:.0f}s", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\n📊 Session Summary:")
        stats = counter.get_statistics()
        print(f"Total objects counted: {stats['total_count']}")
        print(f"Objects entering: {stats['in_count']}")
        print(f"Objects exiting: {stats['out_count']}")
        print(f"Net count: {stats['net_count']}")
        print(f"Detection rate: {stats['detection_rate']:.1f} objects/hour")
        print(f"Accuracy: {stats['accuracy']:.1f}%")
        print(f"False positives: {stats['false_positives']}")
        
        # Show hourly breakdown
        hourly_report = counter.get_hourly_report()
        if hourly_report['hourly_counts']:
            print(f"\n⏰ Hourly Activity:")
            for hour, counts in sorted(hourly_report['hourly_counts'].items()):
                print(f"  Hour {hour:2d}: {counts['total']:3d} total "
                      f"({counts['in']:2d} in, {counts['out']:2d} out)")
    finally:
        counter.cleanup()

def automatic_demo():
    """Automatic demonstration of counting features"""
    print("\n🤖 Automatic Object Counting Demo")
    print("Demonstrating different counting modes")
    
    try:
        counter = ObjectCountingDevice()
        
        # Demo each counting mode
        modes_demo = [
            ("Bidirectional Mode", 0, "Count objects in both directions"),
            ("Entrance Only", 1, "Count only entering objects"),
            ("Exit Only", 2, "Count only exiting objects"),
            ("Presence Mode", 3, "Detect object presence")
        ]
        
        for mode_name, mode_index, description in modes_demo:
            print(f"\n🎬 {mode_name} Demo")
            print(f"Description: {description}")
            
            counter.current_mode = mode_index
            counter._update_display()
            
            # Simulate object detections
            print("Simulating object detections...")
            
            # Simulate entering object
            print("  → Simulating object entering...")
            counter._on_entrance_triggered()
            time.sleep(0.5)
            counter._on_exit_triggered()
            time.sleep(0.5)
            counter._on_entrance_cleared()
            time.sleep(0.5)
            counter._on_exit_cleared()
            counter._process_detection_sequence()
            
            time.sleep(1)
            
            # Simulate exiting object  
            print("  ← Simulating object exiting...")
            counter._on_exit_triggered()
            time.sleep(0.5)
            counter._on_entrance_triggered()
            time.sleep(0.5)
            counter._on_exit_cleared()
            time.sleep(0.5)
            counter._on_entrance_cleared()
            counter._process_detection_sequence()
            
            print(f"✅ {mode_name} demo completed")
            time.sleep(2)
        
        print(f"\n✅ All demonstrations completed!")
        
        # Show final statistics
        stats = counter.get_statistics()
        print(f"\n📊 Demo Statistics:")
        print(f"Objects simulated: {stats['total_count']}")
        print(f"Detection accuracy: {stats['accuracy']:.1f}%")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    finally:
        counter.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Object Counting Device")
    print("=====================")
    print("🔢 Intelligent Object Detection")
    print("📊 Multi-Mode Counting System")
    print("📱 LCD Display Interface")
    print("🎯 Automatic Calibration")
    
    while True:
        print("\n\nSelect Demo Mode:")
        print("1. Interactive object counting")
        print("2. Automatic demonstration")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            interactive_demo()
        elif choice == '2':
            automatic_demo()
        elif choice == '3':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()