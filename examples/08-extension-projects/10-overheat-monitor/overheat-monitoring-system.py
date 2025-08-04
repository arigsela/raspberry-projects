#!/usr/bin/env python3
"""
Overheat Monitoring System

Multi-zone temperature monitoring with alerts, cooling control,
data logging, and predictive analysis for equipment protection.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean, stdev
from collections import deque
import math

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602
from adc0834 import ADC0834

# Hardware Pin Definitions
# Temperature Sensors (via ADC)
ADC_CS_PIN = 5
ADC_CLK_PIN = 6
ADC_DI_PIN = 16
ADC_DO_PIN = 12

# Temperature sensor channels
ZONE1_SENSOR_CHANNEL = 0  # CPU/Main equipment
ZONE2_SENSOR_CHANNEL = 1  # Ambient/Environment
ZONE3_SENSOR_CHANNEL = 2  # Power supply
ZONE4_SENSOR_CHANNEL = 3  # Exhaust/Output

# Status LEDs
LED_NORMAL_PIN = 17      # Green - Normal temperature
LED_WARNING_PIN = 27     # Yellow - Warning level
LED_CRITICAL_PIN = 22    # Red - Critical temperature
LED_ALARM_PIN = 23       # Red flashing - Overheat alarm

# Zone indicator LEDs
ZONE1_LED_PIN = 24
ZONE2_LED_PIN = 25
ZONE3_LED_PIN = 8
ZONE4_LED_PIN = 7

# Cooling Control
FAN1_PIN = 18           # Primary cooling fan (PWM)
FAN2_PIN = 19           # Secondary cooling fan (PWM)
PUMP_PIN = 26           # Water cooling pump (if applicable)

# Alarm and Controls
BUZZER_PIN = 21
RESET_BUTTON_PIN = 20
MODE_BUTTON_PIN = 13
SILENCE_BUTTON_PIN = 14

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Temperature Thresholds (Celsius)
TEMP_THRESHOLDS = {
    'normal': 40,
    'warning': 60,
    'critical': 75,
    'shutdown': 85
}

# Thermistor Constants
THERMISTOR_NOMINAL = 10000
TEMP_NOMINAL = 25
B_COEFFICIENT = 3950
SERIES_RESISTOR = 10000

from gpiozero import LED, PWMLED, Buzzer, Button

class AlertLevel(Enum):
    """Temperature alert levels"""
    NORMAL = "Normal"
    WARNING = "Warning"
    CRITICAL = "Critical"
    OVERHEAT = "Overheat"
    SHUTDOWN = "Shutdown"

class DisplayMode(Enum):
    """Display modes"""
    ALL_ZONES = "All Zones"
    ZONE_DETAIL = "Zone Detail"
    STATISTICS = "Statistics"
    TREND = "Trend"
    ALERTS = "Alerts"

class TemperatureZone:
    """Individual temperature zone monitoring"""
    def __init__(self, name, channel, led_pin):
        self.name = name
        self.channel = channel
        self.led = LED(led_pin)
        self.current_temp = 0.0
        self.alert_level = AlertLevel.NORMAL
        self.history = deque(maxlen=300)  # 5 minutes at 1Hz
        self.max_temp = 0.0
        self.min_temp = float('inf')
        self.alert_count = 0
        self.last_alert_time = None
        
    def update_temperature(self, temp):
        """Update zone temperature"""
        self.current_temp = temp
        self.history.append({
            'temp': temp,
            'time': datetime.now()
        })
        
        # Update min/max
        if temp > self.max_temp:
            self.max_temp = temp
        if temp < self.min_temp:
            self.min_temp = temp
        
        # Determine alert level
        prev_level = self.alert_level
        if temp >= TEMP_THRESHOLDS['shutdown']:
            self.alert_level = AlertLevel.SHUTDOWN
        elif temp >= TEMP_THRESHOLDS['critical']:
            self.alert_level = AlertLevel.CRITICAL
        elif temp >= TEMP_THRESHOLDS['warning']:
            self.alert_level = AlertLevel.WARNING
        else:
            self.alert_level = AlertLevel.NORMAL
        
        # Track alerts
        if self.alert_level != prev_level and self.alert_level != AlertLevel.NORMAL:
            self.alert_count += 1
            self.last_alert_time = datetime.now()
        
        # Update LED
        self._update_led()
    
    def _update_led(self):
        """Update zone LED based on temperature"""
        if self.alert_level == AlertLevel.NORMAL:
            self.led.off()
        elif self.alert_level == AlertLevel.WARNING:
            self.led.on()
        else:
            # Critical or higher - blink
            self.led.blink(on_time=0.2, off_time=0.2)
    
    def get_trend(self):
        """Calculate temperature trend"""
        if len(self.history) < 10:
            return 0.0
        
        # Get last 30 seconds of data
        recent = list(self.history)[-30:]
        if len(recent) < 2:
            return 0.0
        
        # Calculate trend (degrees per minute)
        time_diff = (recent[-1]['time'] - recent[0]['time']).total_seconds()
        if time_diff > 0:
            temp_diff = recent[-1]['temp'] - recent[0]['temp']
            return (temp_diff / time_diff) * 60
        
        return 0.0
    
    def cleanup(self):
        """Clean up resources"""
        self.led.close()

class OverheatMonitoringSystem:
    """Main overheat monitoring system"""
    
    def __init__(self):
        print("🌡️  Initializing Overheat Monitoring System...")
        
        # Initialize hardware
        self._init_sensors()
        self._init_indicators()
        self._init_cooling()
        self._init_controls()
        self._init_display()
        
        # Temperature zones
        self.zones = {
            'zone1': TemperatureZone("CPU/Main", ZONE1_SENSOR_CHANNEL, ZONE1_LED_PIN),
            'zone2': TemperatureZone("Ambient", ZONE2_SENSOR_CHANNEL, ZONE2_LED_PIN),
            'zone3': TemperatureZone("Power", ZONE3_SENSOR_CHANNEL, ZONE3_LED_PIN),
            'zone4': TemperatureZone("Exhaust", ZONE4_SENSOR_CHANNEL, ZONE4_LED_PIN)
        }
        
        # System state
        self.display_mode = DisplayMode.ALL_ZONES
        self.selected_zone = 'zone1'
        self.system_alert_level = AlertLevel.NORMAL
        self.alarm_active = False
        self.alarm_silenced = False
        self.cooling_level = 0  # 0-100%
        
        # Monitoring settings
        self.alert_hysteresis = 2.0  # Degrees
        self.trend_threshold = 5.0   # Degrees per minute
        self.prediction_window = 60   # Seconds
        
        # Statistics
        self.session_start = datetime.now()
        self.total_alerts = 0
        self.overheat_events = 0
        self.max_cooling_used = 0
        
        # Data logging
        self.log_interval = 30  # Seconds
        self.last_log_time = time.time()
        
        # Threading
        self.monitoring_active = False
        self.sensor_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        
        # Load configuration
        self._load_configuration()
        
        print("✅ Overheat monitoring system initialized")
    
    def _init_sensors(self):
        """Initialize temperature sensors"""
        self.adc = ADC0834(cs=ADC_CS_PIN, clk=ADC_CLK_PIN,
                          di=ADC_DI_PIN, do=ADC_DO_PIN)
        print("✓ Temperature sensors initialized")
    
    def _init_indicators(self):
        """Initialize LED indicators and buzzer"""
        self.led_normal = LED(LED_NORMAL_PIN)
        self.led_warning = LED(LED_WARNING_PIN)
        self.led_critical = LED(LED_CRITICAL_PIN)
        self.led_alarm = PWMLED(LED_ALARM_PIN)
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # Initial state
        self.led_normal.on()
        self.led_warning.off()
        self.led_critical.off()
        self.led_alarm.off()
        
        print("✓ Indicators initialized")
    
    def _init_cooling(self):
        """Initialize cooling systems"""
        self.fan1 = PWMLED(FAN1_PIN)
        self.fan2 = PWMLED(FAN2_PIN)
        self.pump = LED(PUMP_PIN)
        
        print("✓ Cooling systems initialized")
    
    def _init_controls(self):
        """Initialize control buttons"""
        self.reset_button = Button(RESET_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.mode_button = Button(MODE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.silence_button = Button(SILENCE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.reset_button.when_pressed = self._reset_alerts
        self.mode_button.when_pressed = self._cycle_display_mode
        self.silence_button.when_pressed = self._silence_alarm
        
        print("✓ Controls initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Overheat Monitor")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load saved configuration"""
        config_file = "overheat_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if 'thresholds' in config:
                        TEMP_THRESHOLDS.update(config['thresholds'])
                    print("✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def run(self):
        """Main system loop"""
        print("\n🌡️  Overheat Monitoring Active!")
        print("MODE: Change display mode")
        print("RESET: Reset alerts")
        print("SILENCE: Silence alarm")
        print("Press Ctrl+C to exit\n")
        
        self.monitoring_active = True
        
        # Start monitoring threads
        sensor_thread = threading.Thread(target=self._sensor_monitoring_loop, daemon=True)
        cooling_thread = threading.Thread(target=self._cooling_control_loop, daemon=True)
        alert_thread = threading.Thread(target=self._alert_monitoring_loop, daemon=True)
        display_thread = threading.Thread(target=self._display_update_loop, daemon=True)
        
        sensor_thread.start()
        cooling_thread.start()
        alert_thread.start()
        display_thread.start()
        
        try:
            while True:
                # Process sensor data
                self._process_sensor_queue()
                
                # Check for predictive alerts
                self._check_temperature_trends()
                
                # Log data periodically
                if time.time() - self.last_log_time > self.log_interval:
                    self._log_temperature_data()
                    self.last_log_time = time.time()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down overheat monitor...")
            self.monitoring_active = False
            self._set_cooling_level(0)
            time.sleep(0.5)
    
    def _sensor_monitoring_loop(self):
        """Continuous temperature monitoring"""
        while self.monitoring_active:
            try:
                # Read all temperature zones
                for zone_name, zone in self.zones.items():
                    # Read ADC value
                    adc_value = self.adc.read(zone.channel)
                    
                    # Convert to temperature
                    temperature = self._adc_to_temperature(adc_value)
                    
                    # Validate reading
                    if -10 <= temperature <= 150:  # Reasonable range
                        self.sensor_queue.put({
                            'zone': zone_name,
                            'temp': temperature,
                            'time': datetime.now()
                        })
                
                time.sleep(1)  # Sample every second
                
            except Exception as e:
                print(f"⚠ Sensor error: {e}")
                time.sleep(1)
    
    def _adc_to_temperature(self, adc_value):
        """Convert ADC reading to temperature"""
        if adc_value == 0:
            adc_value = 1
        
        # Convert to resistance
        resistance = SERIES_RESISTOR / (255.0 / adc_value - 1.0)
        
        # Steinhart-Hart equation
        steinhart = resistance / THERMISTOR_NOMINAL
        steinhart = math.log(steinhart)
        steinhart /= B_COEFFICIENT
        steinhart += 1.0 / (TEMP_NOMINAL + 273.15)
        steinhart = 1.0 / steinhart
        steinhart -= 273.15
        
        return steinhart
    
    def _process_sensor_queue(self):
        """Process temperature readings"""
        try:
            while not self.sensor_queue.empty():
                data = self.sensor_queue.get_nowait()
                
                # Update zone temperature
                zone = self.zones[data['zone']]
                zone.update_temperature(data['temp'])
                
                # Check for alerts
                if zone.alert_level != AlertLevel.NORMAL:
                    self.alert_queue.put({
                        'zone': data['zone'],
                        'level': zone.alert_level,
                        'temp': data['temp']
                    })
                
        except queue.Empty:
            pass
    
    def _cooling_control_loop(self):
        """Automatic cooling control"""
        while self.monitoring_active:
            try:
                # Determine required cooling level
                max_temp = max(zone.current_temp for zone in self.zones.values())
                
                # Calculate cooling requirement
                if max_temp < TEMP_THRESHOLDS['normal']:
                    required_cooling = 0
                elif max_temp < TEMP_THRESHOLDS['warning']:
                    # Linear increase 0-50%
                    ratio = (max_temp - TEMP_THRESHOLDS['normal']) / (TEMP_THRESHOLDS['warning'] - TEMP_THRESHOLDS['normal'])
                    required_cooling = int(ratio * 50)
                elif max_temp < TEMP_THRESHOLDS['critical']:
                    # Linear increase 50-80%
                    ratio = (max_temp - TEMP_THRESHOLDS['warning']) / (TEMP_THRESHOLDS['critical'] - TEMP_THRESHOLDS['warning'])
                    required_cooling = 50 + int(ratio * 30)
                else:
                    # Maximum cooling
                    required_cooling = 100
                
                # Apply cooling with hysteresis
                if abs(required_cooling - self.cooling_level) > 5:
                    self._set_cooling_level(required_cooling)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠ Cooling control error: {e}")
                time.sleep(5)
    
    def _set_cooling_level(self, level):
        """Set cooling system output"""
        self.cooling_level = max(0, min(100, level))
        
        # Track maximum cooling used
        if self.cooling_level > self.max_cooling_used:
            self.max_cooling_used = self.cooling_level
        
        # Primary fan (always runs above 20%)
        if self.cooling_level > 20:
            self.fan1.value = self.cooling_level / 100.0
        else:
            self.fan1.value = 0
        
        # Secondary fan (runs above 50%)
        if self.cooling_level > 50:
            self.fan2.value = (self.cooling_level - 50) / 50.0
        else:
            self.fan2.value = 0
        
        # Water pump (runs above 80%)
        if self.cooling_level > 80:
            self.pump.on()
        else:
            self.pump.off()
    
    def _alert_monitoring_loop(self):
        """Monitor and handle alerts"""
        while self.monitoring_active:
            try:
                # Process alert queue
                alerts = []
                try:
                    while not self.alert_queue.empty():
                        alerts.append(self.alert_queue.get_nowait())
                except queue.Empty:
                    pass
                
                # Determine overall system alert level
                if alerts:
                    max_level = max(alert['level'] for alert in alerts)
                    self._update_system_alert(max_level)
                    
                    # Log critical alerts
                    for alert in alerts:
                        if alert['level'] in [AlertLevel.CRITICAL, AlertLevel.OVERHEAT, AlertLevel.SHUTDOWN]:
                            print(f"🚨 {alert['level'].value} temperature in {alert['zone']}: {alert['temp']:.1f}°C")
                            self.total_alerts += 1
                
                # Handle alarm
                if self.alarm_active and not self.alarm_silenced:
                    # Beep pattern based on severity
                    if self.system_alert_level == AlertLevel.SHUTDOWN:
                        self.buzzer.beep(0.1, 0.1, n=3)
                    elif self.system_alert_level == AlertLevel.CRITICAL:
                        self.buzzer.beep(0.2, 0.3, n=2)
                    elif self.system_alert_level == AlertLevel.WARNING:
                        self.buzzer.beep(0.3, 0.7, n=1)
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠ Alert monitoring error: {e}")
                time.sleep(2)
    
    def _update_system_alert(self, alert_level):
        """Update overall system alert status"""
        self.system_alert_level = alert_level
        
        # Update status LEDs
        self.led_normal.off()
        self.led_warning.off()
        self.led_critical.off()
        self.led_alarm.off()
        
        if alert_level == AlertLevel.NORMAL:
            self.led_normal.on()
            self.alarm_active = False
        elif alert_level == AlertLevel.WARNING:
            self.led_warning.on()
            self.alarm_active = True
        elif alert_level == AlertLevel.CRITICAL:
            self.led_critical.on()
            self.led_alarm.pulse(fade_in_time=0.3, fade_out_time=0.3)
            self.alarm_active = True
        elif alert_level in [AlertLevel.OVERHEAT, AlertLevel.SHUTDOWN]:
            self.led_critical.on()
            self.led_alarm.blink(on_time=0.2, off_time=0.2)
            self.alarm_active = True
            self.overheat_events += 1
    
    def _check_temperature_trends(self):
        """Check for concerning temperature trends"""
        for zone_name, zone in self.zones.items():
            trend = zone.get_trend()
            
            # Alert if temperature rising rapidly
            if trend > self.trend_threshold:
                current_temp = zone.current_temp
                
                # Predict temperature in prediction window
                predicted_temp = current_temp + (trend * self.prediction_window / 60)
                
                # Warn if predicted to exceed threshold
                if predicted_temp > TEMP_THRESHOLDS['critical'] and zone.alert_level == AlertLevel.NORMAL:
                    print(f"⚠️  Rapid temperature rise in {zone.name}: {trend:.1f}°C/min")
                    print(f"   Predicted: {predicted_temp:.1f}°C in {self.prediction_window}s")
    
    def _display_update_loop(self):
        """Update LCD display"""
        display_cycle = 0
        
        while self.monitoring_active:
            try:
                if self.display_mode == DisplayMode.ALL_ZONES:
                    self._show_all_zones_display()
                elif self.display_mode == DisplayMode.ZONE_DETAIL:
                    self._show_zone_detail_display()
                elif self.display_mode == DisplayMode.STATISTICS:
                    self._show_statistics_display()
                elif self.display_mode == DisplayMode.TREND:
                    self._show_trend_display()
                elif self.display_mode == DisplayMode.ALERTS:
                    self._show_alerts_display()
                
                # Rotate through zones in ALL_ZONES mode
                if self.display_mode == DisplayMode.ALL_ZONES:
                    display_cycle = (display_cycle + 1) % 4
                
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠ Display error: {e}")
                time.sleep(1)
    
    def _show_all_zones_display(self):
        """Show all zone temperatures"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Show two zones at a time
            zones_list = list(self.zones.values())
            for i in range(0, len(zones_list), 2):
                if i + 1 < len(zones_list):
                    zone1 = zones_list[i]
                    zone2 = zones_list[i + 1]
                    
                    self.lcd.write(0, 0, f"{zone1.name[:7]}: {zone1.current_temp:4.1f}C")
                    self.lcd.write(1, 0, f"{zone2.name[:7]}: {zone2.current_temp:4.1f}C")
                    
                    # Show alert indicators
                    if zone1.alert_level != AlertLevel.NORMAL:
                        self.lcd.write(0, 15, "!")
                    if zone2.alert_level != AlertLevel.NORMAL:
                        self.lcd.write(1, 15, "!")
                    
                    time.sleep(2)
                    
        except Exception as e:
            print(f"⚠ All zones display error: {e}")
    
    def _show_zone_detail_display(self):
        """Show detailed zone information"""
        if not self.lcd:
            return
        
        try:
            zone = self.zones[self.selected_zone]
            
            self.lcd.clear()
            self.lcd.write(0, 0, f"{zone.name}: {zone.current_temp:.1f}C")
            
            # Show trend
            trend = zone.get_trend()
            if abs(trend) > 0.5:
                trend_str = f"{trend:+.1f}C/m"
                self.lcd.write(0, 10, trend_str)
            
            # Show status and cooling
            self.lcd.write(1, 0, f"{zone.alert_level.value[:4]} Cool:{self.cooling_level}%")
            
        except:
            pass
    
    def _show_statistics_display(self):
        """Show system statistics"""
        if not self.lcd:
            return
        
        try:
            runtime = (datetime.now() - self.session_start).total_seconds() / 60
            
            self.lcd.clear()
            self.lcd.write(0, 0, f"Runtime: {runtime:.0f}min")
            self.lcd.write(1, 0, f"Alerts: {self.total_alerts}")
            
        except:
            pass
    
    def _show_trend_display(self):
        """Show temperature trends"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Find zone with highest trend
            max_trend_zone = None
            max_trend = 0
            
            for zone in self.zones.values():
                trend = zone.get_trend()
                if abs(trend) > abs(max_trend):
                    max_trend = trend
                    max_trend_zone = zone
            
            if max_trend_zone:
                self.lcd.write(0, 0, f"Trend: {max_trend_zone.name}")
                self.lcd.write(1, 0, f"{max_trend:+.1f}C/min")
                
        except:
            pass
    
    def _show_alerts_display(self):
        """Show active alerts"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Count alerts by level
            alert_count = sum(1 for zone in self.zones.values() 
                            if zone.alert_level != AlertLevel.NORMAL)
            
            if alert_count == 0:
                self.lcd.write(0, 0, "No active alerts")
                self.lcd.write(1, 0, f"Max cool: {self.max_cooling_used}%")
            else:
                self.lcd.write(0, 0, f"{alert_count} alerts active")
                self.lcd.write(1, 0, f"Level: {self.system_alert_level.value}")
                
        except:
            pass
    
    def _cycle_display_mode(self):
        """Cycle through display modes"""
        modes = list(DisplayMode)
        current_index = modes.index(self.display_mode)
        new_index = (current_index + 1) % len(modes)
        self.display_mode = modes[new_index]
        
        print(f"📟 Display mode: {self.display_mode.value}")
        self.buzzer.beep(0.1, 0, n=1)
    
    def _reset_alerts(self):
        """Reset alert counts and statistics"""
        print("🔄 Resetting alerts...")
        
        for zone in self.zones.values():
            zone.alert_count = 0
            zone.max_temp = zone.current_temp
            zone.min_temp = zone.current_temp
        
        self.total_alerts = 0
        self.overheat_events = 0
        self.alarm_silenced = False
        
        self.buzzer.beep(0.1, 0.1, n=2)
    
    def _silence_alarm(self):
        """Silence alarm temporarily"""
        self.alarm_silenced = True
        print("🔇 Alarm silenced for 5 minutes")
        
        # Auto-reactivate after 5 minutes
        threading.Timer(300, self._reactivate_alarm).start()
        
        self.buzzer.beep(0.1, 0, n=1)
    
    def _reactivate_alarm(self):
        """Reactivate alarm after silence period"""
        self.alarm_silenced = False
        print("🔊 Alarm reactivated")
    
    def _log_temperature_data(self):
        """Log temperature data to file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'zones': {}
            }
            
            for zone_name, zone in self.zones.items():
                log_entry['zones'][zone_name] = {
                    'temp': round(zone.current_temp, 2),
                    'alert': zone.alert_level.value,
                    'trend': round(zone.get_trend(), 2)
                }
            
            log_entry['cooling_level'] = self.cooling_level
            log_entry['system_alert'] = self.system_alert_level.value
            
            with open('overheat_log.json', 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
                
        except Exception as e:
            print(f"⚠ Logging error: {e}")
    
    def get_statistics(self):
        """Get system statistics"""
        runtime = (datetime.now() - self.session_start).total_seconds()
        
        stats = {
            'runtime_seconds': runtime,
            'total_alerts': self.total_alerts,
            'overheat_events': self.overheat_events,
            'max_cooling_used': self.max_cooling_used,
            'zones': {}
        }
        
        for zone_name, zone in self.zones.items():
            stats['zones'][zone_name] = {
                'current_temp': zone.current_temp,
                'max_temp': zone.max_temp,
                'min_temp': zone.min_temp,
                'alert_count': zone.alert_count,
                'current_alert': zone.alert_level.value
            }
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Turn off cooling
        self._set_cooling_level(0)
        
        # Turn off alarms
        self.led_alarm.off()
        self.buzzer.off()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
        
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Runtime: {stats['runtime_seconds']/60:.1f} minutes")
        print(f"  Total alerts: {stats['total_alerts']}")
        print(f"  Overheat events: {stats['overheat_events']}")
        print(f"  Max cooling used: {stats['max_cooling_used']}%")
        
        print("\n  Zone Statistics:")
        for zone_name, zone_stats in stats['zones'].items():
            print(f"    {zone_name}:")
            print(f"      Temperature range: {zone_stats['min_temp']:.1f}°C - {zone_stats['max_temp']:.1f}°C")
            print(f"      Alert count: {zone_stats['alert_count']}")
        
        # Clean up hardware
        for zone in self.zones.values():
            zone.cleanup()
        
        self.led_normal.close()
        self.led_warning.close()
        self.led_critical.close()
        self.led_alarm.close()
        self.buzzer.close()
        self.fan1.close()
        self.fan2.close()
        self.pump.close()
        self.reset_button.close()
        self.mode_button.close()
        self.silence_button.close()
        
        print("\n✅ Cleanup complete")


def temperature_demo():
    """Demonstrate temperature monitoring"""
    print("\n🎮 Overheat Monitor Demo")
    print("=" * 50)
    
    monitor = OverheatMonitoringSystem()
    
    try:
        print("\nSimulating temperature scenarios...")
        
        # Simulate different temperature conditions
        scenarios = [
            ("Normal operation", {'zone1': 35, 'zone2': 30, 'zone3': 32, 'zone4': 28}),
            ("Zone 1 warming", {'zone1': 55, 'zone2': 35, 'zone3': 38, 'zone4': 33}),
            ("Zone 1 critical", {'zone1': 78, 'zone2': 45, 'zone3': 50, 'zone4': 42}),
            ("Multiple warnings", {'zone1': 65, 'zone2': 62, 'zone3': 58, 'zone4': 55}),
            ("System overheat", {'zone1': 88, 'zone2': 75, 'zone3': 80, 'zone4': 72}),
            ("Cooling down", {'zone1': 45, 'zone2': 40, 'zone3': 42, 'zone4': 38})
        ]
        
        for description, temps in scenarios:
            print(f"\n{description}:")
            
            # Update zone temperatures
            for zone_name, temp in temps.items():
                zone = monitor.zones[zone_name]
                zone.update_temperature(temp)
                print(f"  {zone.name}: {temp}°C ({zone.alert_level.value})")
            
            # Determine cooling level
            max_temp = max(temps.values())
            if max_temp < 40:
                cooling = 0
            elif max_temp < 60:
                cooling = int((max_temp - 40) / 20 * 50)
            elif max_temp < 75:
                cooling = 50 + int((max_temp - 60) / 15 * 30)
            else:
                cooling = 100
            
            monitor._set_cooling_level(cooling)
            print(f"  Cooling: {cooling}%")
            
            # Update system alert
            max_alert = max(zone.alert_level for zone in monitor.zones.values())
            monitor._update_system_alert(max_alert)
            
            time.sleep(3)
        
        print("\n✅ Demo complete!")
        
    finally:
        monitor.cleanup()


def cooling_test():
    """Test cooling system"""
    print("\n🔧 Cooling System Test")
    print("=" * 50)
    
    monitor = OverheatMonitoringSystem()
    
    try:
        print("\nTesting cooling levels...")
        
        levels = [0, 25, 50, 75, 100]
        
        for level in levels:
            print(f"\nCooling level: {level}%")
            monitor._set_cooling_level(level)
            
            print(f"  Fan 1: {'ON' if monitor.fan1.value > 0 else 'OFF'} ({monitor.fan1.value*100:.0f}%)")
            print(f"  Fan 2: {'ON' if monitor.fan2.value > 0 else 'OFF'} ({monitor.fan2.value*100:.0f}%)")
            print(f"  Pump: {'ON' if monitor.pump.is_lit else 'OFF'}")
            
            time.sleep(2)
        
        print("\n✅ Cooling test complete!")
        
    finally:
        monitor.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        temperature_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "cooling":
        cooling_test()
    else:
        # Normal operation
        monitor = OverheatMonitoringSystem()
        try:
            monitor.run()
        finally:
            monitor.cleanup()