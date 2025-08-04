#!/usr/bin/env python3
"""
Ultrasonic Parking Sensor with Variable Alert System

A reversing alarm that uses ultrasonic distance sensing to provide
graduated audio/visual alerts based on proximity to obstacles.
Features multiple alert modes, LED indicators, and LCD display.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime
from statistics import mean, median
from enum import Enum
from gpiozero import DistanceSensor, LED, PWMLED, Buzzer, Button
import numpy as np

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602
from adc0834 import ADC0834

# Hardware Pin Definitions
ULTRASONIC_TRIGGER_PIN = 23
ULTRASONIC_ECHO_PIN = 24

# LED Indicators
LED_GREEN_PIN = 17      # Safe distance
LED_YELLOW_PIN = 27     # Caution zone
LED_ORANGE_PIN = 22     # Warning zone
LED_RED_PIN = 18        # Danger zone (PWM for flashing)

# Audio Output
BUZZER_PIN = 25         # Main alert buzzer
SPEAKER_PIN = 8         # Optional speaker for tones

# Controls
MODE_BUTTON_PIN = 19
MUTE_BUTTON_PIN = 20
CALIBRATE_BUTTON_PIN = 26

# ADC for sensitivity control
ADC_CS_PIN = 5
ADC_CLK_PIN = 6
ADC_DI_PIN = 16
ADC_DO_PIN = 12

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Distance Zones (in meters)
ZONE_SAFE = 2.0         # > 2m: Safe
ZONE_CAUTION = 1.0      # 1-2m: Caution
ZONE_WARNING = 0.5      # 0.5-1m: Warning
ZONE_DANGER = 0.3       # < 0.3m: Danger
ZONE_CRITICAL = 0.1     # < 0.1m: Critical

# Alert Timing
BEEP_PATTERNS = {
    'safe': None,                                    # No beep
    'caution': {'on': 0.5, 'off': 1.0},             # Slow beep
    'warning': {'on': 0.3, 'off': 0.5},             # Medium beep
    'danger': {'on': 0.2, 'off': 0.2},              # Fast beep
    'critical': {'on': 0.1, 'off': 0.05}            # Very fast beep
}

class AlertMode(Enum):
    """Alert mode enumeration"""
    STANDARD = "Standard"
    VOICE = "Voice"
    TONE = "Tone"
    VISUAL = "Visual Only"
    EMERGENCY = "Emergency"

class DistanceZone(Enum):
    """Distance zone enumeration"""
    SAFE = "Safe"
    CAUTION = "Caution"
    WARNING = "Warning"
    DANGER = "Danger"
    CRITICAL = "Critical"

class UltrasonicParkingSensor:
    """Main parking sensor system class"""
    
    def __init__(self):
        print("🚗 Initializing Ultrasonic Parking Sensor...")
        
        # Initialize hardware components
        self._init_sensors()
        self._init_indicators()
        self._init_controls()
        self._init_display()
        
        # System state
        self.current_distance = None
        self.current_zone = DistanceZone.SAFE
        self.alert_mode = AlertMode.STANDARD
        self.muted = False
        self.emergency_stop = False
        
        # Configuration
        self.sensitivity = 0.5  # Default sensitivity
        self.smoothing_window = 5  # Distance averaging window
        self.distance_history = []
        
        # Alert state
        self.alert_active = False
        self.last_alert_time = 0
        self.beep_thread = None
        
        # Calibration
        self.calibration_offset = 0.0
        self.min_detection_distance = 0.02  # 2cm minimum
        self.max_detection_distance = 4.0   # 4m maximum
        
        # Statistics
        self.session_start = datetime.now()
        self.zone_times = {zone: 0 for zone in DistanceZone}
        self.min_distance_recorded = float('inf')
        self.alert_count = 0
        
        # Threading
        self.monitoring_active = False
        self.sensor_queue = queue.Queue()
        self.display_queue = queue.Queue()
        
        # Load saved configuration
        self._load_configuration()
        
        print("✅ Parking sensor initialized")
    
    def _init_sensors(self):
        """Initialize ultrasonic sensor"""
        try:
            self.ultrasonic = DistanceSensor(
                echo=ULTRASONIC_ECHO_PIN,
                trigger=ULTRASONIC_TRIGGER_PIN,
                max_distance=self.max_detection_distance,
                threshold_distance=ZONE_DANGER
            )
            print("✓ Ultrasonic sensor initialized")
        except Exception as e:
            print(f"✗ Ultrasonic sensor initialization failed: {e}")
            raise
        
        # Initialize ADC for sensitivity control
        self.adc = ADC0834(cs=ADC_CS_PIN, clk=ADC_CLK_PIN, 
                          di=ADC_DI_PIN, do=ADC_DO_PIN)
    
    def _init_indicators(self):
        """Initialize LED and audio indicators"""
        # LED indicators
        self.led_green = LED(LED_GREEN_PIN)
        self.led_yellow = LED(LED_YELLOW_PIN)
        self.led_orange = LED(LED_ORANGE_PIN)
        self.led_red = PWMLED(LED_RED_PIN)
        
        # Audio indicators
        self.buzzer = Buzzer(BUZZER_PIN)
        self.speaker = Buzzer(SPEAKER_PIN)  # Can produce different tones
        
        # Initial state - all off
        self._all_leds_off()
        print("✓ Indicators initialized")
    
    def _init_controls(self):
        """Initialize control buttons"""
        self.mode_button = Button(MODE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.mute_button = Button(MUTE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.calibrate_button = Button(CALIBRATE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.mode_button.when_pressed = self._cycle_alert_mode
        self.mute_button.when_pressed = self._toggle_mute
        self.calibrate_button.when_pressed = self._calibrate_sensor
        
        print("✓ Controls initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Parking Sensor")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load saved configuration"""
        config_file = "parking_sensor_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.alert_mode = AlertMode(config.get('alert_mode', 'Standard'))
                    self.sensitivity = config.get('sensitivity', 0.5)
                    self.calibration_offset = config.get('calibration_offset', 0.0)
                    print(f"✓ Configuration loaded: Mode={self.alert_mode.value}")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def _save_configuration(self):
        """Save current configuration"""
        config_file = "parking_sensor_config.json"
        try:
            config = {
                'alert_mode': self.alert_mode.value,
                'sensitivity': self.sensitivity,
                'calibration_offset': self.calibration_offset,
                'last_saved': datetime.now().isoformat()
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
    
    def run(self):
        """Main system loop"""
        print("\n🚗 Parking sensor active!")
        print("Press MODE to change alert type")
        print("Press MUTE to toggle sound")
        print("Press CALIBRATE to calibrate sensor")
        print("Press Ctrl+C to exit\n")
        
        self.monitoring_active = True
        
        # Start monitoring threads
        sensor_thread = threading.Thread(target=self._sensor_monitoring_loop, daemon=True)
        display_thread = threading.Thread(target=self._display_update_loop, daemon=True)
        
        sensor_thread.start()
        display_thread.start()
        
        try:
            while True:
                # Update sensitivity from potentiometer
                self._update_sensitivity()
                
                # Process any queued events
                self._process_sensor_data()
                
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down parking sensor...")
            self.monitoring_active = False
            self._stop_alert()
            time.sleep(0.5)
    
    def _sensor_monitoring_loop(self):
        """Continuous sensor monitoring thread"""
        while self.monitoring_active:
            try:
                # Get current distance reading
                raw_distance = self.ultrasonic.distance
                
                # Apply calibration offset
                distance = raw_distance + self.calibration_offset
                
                # Clamp to valid range
                distance = max(self.min_detection_distance, 
                             min(distance, self.max_detection_distance))
                
                # Add to history for smoothing
                self.distance_history.append(distance)
                if len(self.distance_history) > self.smoothing_window:
                    self.distance_history.pop(0)
                
                # Calculate smoothed distance
                if len(self.distance_history) >= 3:
                    # Use median for noise reduction
                    smoothed_distance = median(self.distance_history)
                else:
                    smoothed_distance = distance
                
                # Update current distance
                self.current_distance = smoothed_distance
                
                # Determine zone
                new_zone = self._get_distance_zone(smoothed_distance)
                
                # Check for zone change
                if new_zone != self.current_zone:
                    self.current_zone = new_zone
                    self.sensor_queue.put({
                        'type': 'zone_change',
                        'zone': new_zone,
                        'distance': smoothed_distance
                    })
                
                # Update statistics
                self._update_statistics(smoothed_distance)
                
                # Small delay to prevent CPU overload
                time.sleep(0.05)
                
            except Exception as e:
                print(f"⚠ Sensor error: {e}")
                time.sleep(0.1)
    
    def _get_distance_zone(self, distance):
        """Determine zone based on distance"""
        if distance <= ZONE_CRITICAL:
            return DistanceZone.CRITICAL
        elif distance <= ZONE_DANGER:
            return DistanceZone.DANGER
        elif distance <= ZONE_WARNING:
            return DistanceZone.WARNING
        elif distance <= ZONE_CAUTION:
            return DistanceZone.CAUTION
        else:
            return DistanceZone.SAFE
    
    def _process_sensor_data(self):
        """Process sensor queue data"""
        try:
            while not self.sensor_queue.empty():
                data = self.sensor_queue.get_nowait()
                
                if data['type'] == 'zone_change':
                    self._handle_zone_change(data['zone'], data['distance'])
                    
        except queue.Empty:
            pass
    
    def _handle_zone_change(self, new_zone, distance):
        """Handle zone transitions"""
        print(f"📍 Zone: {new_zone.value} ({distance:.2f}m)")
        
        # Update display
        self.display_queue.put({
            'zone': new_zone,
            'distance': distance
        })
        
        # Update LED indicators
        self._update_led_indicators(new_zone)
        
        # Update alert pattern
        self._update_alert_pattern(new_zone)
        
        # Log zone change
        self._log_zone_change(new_zone, distance)
    
    def _update_led_indicators(self, zone):
        """Update LED indicators based on zone"""
        # Turn off all LEDs first
        self._all_leds_off()
        
        # Turn on appropriate LEDs
        if zone == DistanceZone.SAFE:
            self.led_green.on()
        elif zone == DistanceZone.CAUTION:
            self.led_green.on()
            self.led_yellow.on()
        elif zone == DistanceZone.WARNING:
            self.led_yellow.on()
            self.led_orange.on()
        elif zone == DistanceZone.DANGER:
            self.led_orange.on()
            self.led_red.pulse(fade_in_time=0.2, fade_out_time=0.2)
        elif zone == DistanceZone.CRITICAL:
            # All LEDs on, red flashing rapidly
            self.led_yellow.on()
            self.led_orange.on()
            self.led_red.blink(on_time=0.1, off_time=0.1)
            
            # Emergency stop consideration
            if self.alert_mode == AlertMode.EMERGENCY:
                self._trigger_emergency_stop()
    
    def _all_leds_off(self):
        """Turn off all LED indicators"""
        self.led_green.off()
        self.led_yellow.off()
        self.led_orange.off()
        self.led_red.off()
    
    def _update_alert_pattern(self, zone):
        """Update audio alert pattern based on zone"""
        # Stop current alert
        self._stop_alert()
        
        if self.muted or zone == DistanceZone.SAFE:
            return
        
        # Get beep pattern for zone
        pattern = BEEP_PATTERNS.get(zone.value.lower())
        if not pattern:
            return
        
        # Start new alert pattern
        self.alert_active = True
        self.alert_count += 1
        
        if self.alert_mode == AlertMode.STANDARD:
            self._start_standard_alert(pattern)
        elif self.alert_mode == AlertMode.VOICE:
            self._start_voice_alert(zone)
        elif self.alert_mode == AlertMode.TONE:
            self._start_tone_alert(zone)
        elif self.alert_mode == AlertMode.VISUAL:
            # Visual only - no audio
            pass
        elif self.alert_mode == AlertMode.EMERGENCY:
            self._start_emergency_alert(zone)
    
    def _start_standard_alert(self, pattern):
        """Start standard beep alert"""
        def beep_loop():
            while self.alert_active and not self.muted:
                self.buzzer.on()
                time.sleep(pattern['on'])
                self.buzzer.off()
                time.sleep(pattern['off'])
        
        self.beep_thread = threading.Thread(target=beep_loop, daemon=True)
        self.beep_thread.start()
    
    def _start_voice_alert(self, zone):
        """Start voice announcement alert"""
        # This would use text-to-speech in a real implementation
        # For now, use different beep patterns
        voice_patterns = {
            DistanceZone.CAUTION: [(0.1, 0.1), (0.1, 0.3)],
            DistanceZone.WARNING: [(0.1, 0.05), (0.1, 0.05), (0.1, 0.3)],
            DistanceZone.DANGER: [(0.1, 0.05)] * 4 + [(0.1, 0.3)],
            DistanceZone.CRITICAL: [(0.05, 0.05)] * 8
        }
        
        def voice_loop():
            pattern = voice_patterns.get(zone, [(0.2, 0.5)])
            while self.alert_active and not self.muted:
                for on_time, off_time in pattern:
                    if not self.alert_active or self.muted:
                        break
                    self.speaker.on()
                    time.sleep(on_time)
                    self.speaker.off()
                    time.sleep(off_time)
                time.sleep(0.5)  # Pause between announcements
        
        self.beep_thread = threading.Thread(target=voice_loop, daemon=True)
        self.beep_thread.start()
    
    def _start_tone_alert(self, zone):
        """Start musical tone alert"""
        # Different tones for different zones
        tone_frequencies = {
            DistanceZone.CAUTION: 440,    # A4
            DistanceZone.WARNING: 523,    # C5
            DistanceZone.DANGER: 659,     # E5
            DistanceZone.CRITICAL: 880    # A5
        }
        
        # Simulate different tones with varying beep speeds
        tone_patterns = {
            DistanceZone.CAUTION: (0.05, 0.5),
            DistanceZone.WARNING: (0.04, 0.3),
            DistanceZone.DANGER: (0.03, 0.2),
            DistanceZone.CRITICAL: (0.02, 0.1)
        }
        
        def tone_loop():
            on_time, off_time = tone_patterns.get(zone, (0.1, 0.5))
            while self.alert_active and not self.muted:
                # In real implementation, would generate actual tone
                self.speaker.on()
                time.sleep(on_time)
                self.speaker.off()
                time.sleep(off_time)
        
        self.beep_thread = threading.Thread(target=tone_loop, daemon=True)
        self.beep_thread.start()
    
    def _start_emergency_alert(self, zone):
        """Start emergency alert pattern"""
        if zone == DistanceZone.CRITICAL:
            # Continuous alarm for critical zone
            def emergency_loop():
                while self.alert_active and not self.muted:
                    self.buzzer.on()
                    self.speaker.on()
                    time.sleep(0.1)
                    self.buzzer.off()
                    self.speaker.off()
                    time.sleep(0.05)
            
            self.beep_thread = threading.Thread(target=emergency_loop, daemon=True)
            self.beep_thread.start()
        else:
            # Use standard alert for other zones
            pattern = BEEP_PATTERNS.get(zone.value.lower())
            if pattern:
                self._start_standard_alert(pattern)
    
    def _stop_alert(self):
        """Stop current alert"""
        self.alert_active = False
        if self.beep_thread:
            self.beep_thread.join(timeout=0.5)
        self.buzzer.off()
        self.speaker.off()
    
    def _trigger_emergency_stop(self):
        """Trigger emergency stop (simulation)"""
        if not self.emergency_stop:
            self.emergency_stop = True
            print("🚨 EMERGENCY STOP TRIGGERED!")
            # In real implementation, would engage brakes or stop motor
            
            # Flash all LEDs
            for _ in range(5):
                self._all_leds_off()
                time.sleep(0.1)
                self.led_red.on()
                self.led_orange.on()
                self.led_yellow.on()
                time.sleep(0.1)
            
            self.emergency_stop = False
    
    def _display_update_loop(self):
        """LCD display update thread"""
        last_update = 0
        display_mode = 0
        
        while self.monitoring_active:
            try:
                # Check for display updates
                try:
                    update = self.display_queue.get_nowait()
                    self._update_main_display(update['zone'], update['distance'])
                    last_update = time.time()
                except queue.Empty:
                    pass
                
                # Rotate display information every 3 seconds
                if time.time() - last_update > 3:
                    if display_mode == 0:
                        self._show_status_display()
                    elif display_mode == 1:
                        self._show_statistics_display()
                    elif display_mode == 2:
                        self._show_mode_display()
                    
                    display_mode = (display_mode + 1) % 3
                    last_update = time.time()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠ Display error: {e}")
    
    def _update_main_display(self, zone, distance):
        """Update main distance display"""
        if not self.lcd:
            return
        
        try:
            # Zone indicators
            zone_chars = {
                DistanceZone.SAFE: "✓",
                DistanceZone.CAUTION: "!",
                DistanceZone.WARNING: "⚠",
                DistanceZone.DANGER: "☢",
                DistanceZone.CRITICAL: "🚨"
            }
            
            # Format distance display
            if distance < 1.0:
                dist_str = f"{distance*100:.0f}cm"
            else:
                dist_str = f"{distance:.2f}m"
            
            # Update LCD
            self.lcd.clear()
            zone_char = zone_chars.get(zone, "?")
            self.lcd.write(0, 0, f"{zone_char} {zone.value:<8}")
            self.lcd.write(1, 0, f"Dist: {dist_str}")
            
            # Add mute indicator
            if self.muted:
                self.lcd.write(1, 14, "🔇")
                
        except Exception as e:
            print(f"⚠ Display update error: {e}")
    
    def _show_status_display(self):
        """Show system status on LCD"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, f"Mode: {self.alert_mode.value[:10]}")
            self.lcd.write(1, 0, f"Sens: {self.sensitivity*100:.0f}%")
            if self.muted:
                self.lcd.write(1, 14, "🔇")
        except:
            pass
    
    def _show_statistics_display(self):
        """Show statistics on LCD"""
        if not self.lcd:
            return
        
        try:
            runtime = (datetime.now() - self.session_start).total_seconds()
            runtime_min = int(runtime / 60)
            
            self.lcd.clear()
            self.lcd.write(0, 0, f"Alerts: {self.alert_count}")
            self.lcd.write(1, 0, f"Time: {runtime_min}min")
        except:
            pass
    
    def _show_mode_display(self):
        """Show current operating mode"""
        if not self.lcd:
            return
        
        try:
            if self.current_distance:
                dist_str = f"{self.current_distance:.2f}m"
            else:
                dist_str = "---"
            
            self.lcd.clear()
            self.lcd.write(0, 0, "Parking Sensor")
            self.lcd.write(1, 0, f"Active: {dist_str}")
        except:
            pass
    
    def _cycle_alert_mode(self):
        """Cycle through alert modes"""
        modes = list(AlertMode)
        current_index = modes.index(self.alert_mode)
        new_index = (current_index + 1) % len(modes)
        self.alert_mode = modes[new_index]
        
        print(f"🔔 Alert mode: {self.alert_mode.value}")
        
        # Update display
        self.display_queue.put({
            'zone': self.current_zone,
            'distance': self.current_distance or 0
        })
        
        # Save configuration
        self._save_configuration()
        
        # Beep confirmation
        if not self.muted:
            self.buzzer.beep(0.1, 0.1, n=2)
    
    def _toggle_mute(self):
        """Toggle mute state"""
        self.muted = not self.muted
        
        if self.muted:
            print("🔇 Audio muted")
            self._stop_alert()
        else:
            print("🔊 Audio enabled")
            # Beep confirmation
            self.buzzer.beep(0.1, 0.1, n=1)
        
        # Update display
        self.display_queue.put({
            'zone': self.current_zone,
            'distance': self.current_distance or 0
        })
    
    def _calibrate_sensor(self):
        """Calibrate sensor to current environment"""
        print("\n📏 Starting calibration...")
        print("Ensure area is clear of obstacles")
        
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Calibrating...")
            self.lcd.write(1, 0, "Clear area!")
        
        # Stop alerts during calibration
        was_muted = self.muted
        self.muted = True
        
        # Take multiple readings
        readings = []
        for i in range(20):
            distance = self.ultrasonic.distance
            readings.append(distance)
            time.sleep(0.1)
            
            # Show progress
            if self.lcd and i % 5 == 0:
                self.lcd.write(1, 0, f"Progress: {i*5}%  ")
        
        # Calculate calibration offset
        avg_distance = mean(readings)
        
        # Assume clear area should read as max distance
        self.calibration_offset = self.max_detection_distance - avg_distance
        
        print(f"✓ Calibration complete")
        print(f"  Average reading: {avg_distance:.2f}m")
        print(f"  Calibration offset: {self.calibration_offset:+.2f}m")
        
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Calibrated!")
            self.lcd.write(1, 0, f"Offset: {self.calibration_offset:+.2f}m")
        
        # Save configuration
        self._save_configuration()
        
        # Restore mute state
        self.muted = was_muted
        
        # Confirmation beep
        if not self.muted:
            self.buzzer.beep(0.1, 0.1, n=3)
        
        time.sleep(2)
    
    def _update_sensitivity(self):
        """Update sensitivity from ADC potentiometer"""
        try:
            # Read ADC value (0-255)
            adc_value = self.adc.read(0)
            
            # Convert to sensitivity (0.1 to 1.0)
            self.sensitivity = 0.1 + (adc_value / 255) * 0.9
            
        except Exception as e:
            # Keep current sensitivity on error
            pass
    
    def _update_statistics(self, distance):
        """Update running statistics"""
        # Track minimum distance
        if distance < self.min_distance_recorded:
            self.min_distance_recorded = distance
        
        # Track time in each zone
        # This is simplified - in reality would track actual time spent
        self.zone_times[self.current_zone] += 0.05  # Loop interval
    
    def _log_zone_change(self, zone, distance):
        """Log zone changes to file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'zone': zone.value,
                'distance': round(distance, 3),
                'alert_mode': self.alert_mode.value,
                'muted': self.muted
            }
            
            with open('parking_sensor_log.json', 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
        except:
            pass
    
    def get_statistics(self):
        """Get session statistics"""
        runtime = (datetime.now() - self.session_start).total_seconds()
        
        stats = {
            'runtime_seconds': runtime,
            'alert_count': self.alert_count,
            'min_distance': self.min_distance_recorded,
            'zone_percentages': {}
        }
        
        # Calculate zone percentages
        total_zone_time = sum(self.zone_times.values())
        if total_zone_time > 0:
            for zone, time_spent in self.zone_times.items():
                percentage = (time_spent / total_zone_time) * 100
                stats['zone_percentages'][zone.value] = round(percentage, 1)
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop monitoring
        self.monitoring_active = False
        self._stop_alert()
        
        # Turn off all indicators
        self._all_leds_off()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
        
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Runtime: {stats['runtime_seconds']/60:.1f} minutes")
        print(f"  Alerts triggered: {stats['alert_count']}")
        print(f"  Minimum distance: {stats['min_distance']:.2f}m")
        print("  Zone distribution:")
        for zone, percentage in stats['zone_percentages'].items():
            print(f"    {zone}: {percentage}%")
        
        # Close hardware
        self.ultrasonic.close()
        self.led_green.close()
        self.led_yellow.close()
        self.led_orange.close()
        self.led_red.close()
        self.buzzer.close()
        self.speaker.close()
        self.mode_button.close()
        self.mute_button.close()
        self.calibrate_button.close()
        
        print("\n✅ Cleanup complete")


def parking_demo():
    """Demonstrate parking sensor features"""
    print("\n🎮 Parking Sensor Demo")
    print("=" * 50)
    
    sensor = UltrasonicParkingSensor()
    
    try:
        # Simulate different distances
        demo_distances = [
            (3.0, "Far away - safe zone"),
            (1.5, "Approaching - caution zone"),
            (0.7, "Getting close - warning zone"),
            (0.4, "Very close - danger zone"),
            (0.15, "Too close! - critical zone"),
            (0.4, "Backing up - danger zone"),
            (1.0, "Better - warning zone"),
            (2.5, "Safe distance again")
        ]
        
        print("\nSimulating parking approach...")
        print("Watch the LEDs and listen to the alerts!\n")
        
        for distance, description in demo_distances:
            print(f"📏 Distance: {distance}m - {description}")
            
            # Simulate the distance reading
            sensor.distance_history = [distance] * sensor.smoothing_window
            sensor.current_distance = distance
            
            # Get zone and handle change
            zone = sensor._get_distance_zone(distance)
            sensor._handle_zone_change(zone, distance)
            
            # Wait to observe the alert
            time.sleep(3)
        
        print("\n✅ Demo complete!")
        
    finally:
        sensor.cleanup()


def calibration_test():
    """Test calibration procedure"""
    print("\n🔧 Calibration Test")
    print("=" * 50)
    
    sensor = UltrasonicParkingSensor()
    
    try:
        print("Starting calibration test...")
        sensor._calibrate_sensor()
        
        print("\nTesting calibrated readings...")
        for i in range(10):
            distance = sensor.ultrasonic.distance + sensor.calibration_offset
            print(f"  Reading {i+1}: {distance:.2f}m")
            time.sleep(0.5)
        
    finally:
        sensor.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        parking_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        calibration_test()
    else:
        # Normal operation
        sensor = UltrasonicParkingSensor()
        try:
            sensor.run()
        finally:
            sensor.cleanup()