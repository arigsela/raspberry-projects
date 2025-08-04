#!/usr/bin/env python3
"""
Battery Voltage Monitor with Smart Indicators

Real-time battery monitoring system with voltage measurement,
charge level indication, low battery alerts, and data logging.
Supports various battery types and chemistries.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean, stdev
from gpiozero import LED, PWMLED, Buzzer, Button
import numpy as np

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602
from adc0834 import ADC0834

# Hardware Pin Definitions
# ADC for voltage measurement
ADC_CS_PIN = 5
ADC_CLK_PIN = 6
ADC_DI_PIN = 16
ADC_DO_PIN = 12
BATTERY_CHANNEL = 0     # ADC channel for battery voltage

# LED Indicators (10-segment bar graph + status LEDs)
LED_BAR_PINS = [17, 18, 27, 22, 23, 24, 25, 8, 7, 1]  # 10 LEDs for bar graph
LED_CHARGING_PIN = 19   # Charging indicator
LED_LOW_BAT_PIN = 20    # Low battery warning (PWM)
LED_CRITICAL_PIN = 21   # Critical battery (PWM)

# Control Buttons
MODE_BUTTON_PIN = 26
CALIBRATE_BUTTON_PIN = 13

# Alert Buzzer
BUZZER_PIN = 14

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Voltage Divider Constants
# For measuring higher voltages (e.g., 12V battery)
# Vout = Vin * R2 / (R1 + R2)
R1 = 10000  # 10kΩ
R2 = 3300   # 3.3kΩ
VOLTAGE_DIVIDER_RATIO = (R1 + R2) / R2
ADC_REFERENCE_VOLTAGE = 3.3  # ADC reference voltage

# Battery Types and Characteristics
BATTERY_PROFILES = {
    "LiPo_1S": {
        "nominal": 3.7,
        "full": 4.2,
        "empty": 3.0,
        "critical": 3.2,
        "cells": 1
    },
    "LiPo_2S": {
        "nominal": 7.4,
        "full": 8.4,
        "empty": 6.0,
        "critical": 6.4,
        "cells": 2
    },
    "LiPo_3S": {
        "nominal": 11.1,
        "full": 12.6,
        "empty": 9.0,
        "critical": 9.6,
        "cells": 3
    },
    "Lead_Acid_12V": {
        "nominal": 12.0,
        "full": 12.8,
        "empty": 11.8,
        "critical": 11.5,
        "cells": 6
    },
    "NiMH_4": {
        "nominal": 4.8,
        "full": 5.6,
        "empty": 4.0,
        "critical": 4.2,
        "cells": 4
    },
    "Alkaline_4": {
        "nominal": 6.0,
        "full": 6.4,
        "empty": 4.0,
        "critical": 4.4,
        "cells": 4
    }
}

class DisplayMode(Enum):
    """Display mode enumeration"""
    VOLTAGE = "Voltage"
    PERCENTAGE = "Percentage"
    TIME_REMAINING = "Time Left"
    STATISTICS = "Statistics"
    GRAPH = "Graph"

class BatteryVoltageMonitor:
    """Main battery monitoring system class"""
    
    def __init__(self):
        print("🔋 Initializing Battery Voltage Monitor...")
        
        # Initialize hardware
        self._init_adc()
        self._init_indicators()
        self._init_controls()
        self._init_display()
        
        # System state
        self.battery_voltage = 0.0
        self.battery_percentage = 0
        self.battery_type = "LiPo_3S"  # Default battery type
        self.display_mode = DisplayMode.VOLTAGE
        self.is_charging = False
        self.calibration_offset = 0.0
        
        # Voltage history for averaging and analysis
        self.voltage_history = []
        self.history_size = 60  # Keep 1 minute of data
        self.discharge_rate = 0.0  # V/hour
        
        # Alert thresholds
        self.low_battery_threshold = 20  # Percentage
        self.critical_battery_threshold = 10  # Percentage
        self.last_alert_time = 0
        self.alert_interval = 60  # Seconds between alerts
        
        # Statistics
        self.session_start = datetime.now()
        self.min_voltage = float('inf')
        self.max_voltage = 0.0
        self.total_samples = 0
        
        # Data logging
        self.log_interval = 60  # Log every minute
        self.last_log_time = time.time()
        
        # Threading
        self.monitoring_active = False
        self.voltage_queue = queue.Queue()
        self.display_queue = queue.Queue()
        
        # Load configuration
        self._load_configuration()
        
        print("✅ Battery monitor initialized")
    
    def _init_adc(self):
        """Initialize ADC for voltage measurement"""
        self.adc = ADC0834(cs=ADC_CS_PIN, clk=ADC_CLK_PIN,
                          di=ADC_DI_PIN, do=ADC_DO_PIN)
        print("✓ ADC initialized")
    
    def _init_indicators(self):
        """Initialize LED indicators"""
        # Bar graph LEDs
        self.led_bar = []
        for pin in LED_BAR_PINS:
            self.led_bar.append(LED(pin))
        
        # Status LEDs
        self.led_charging = LED(LED_CHARGING_PIN)
        self.led_low_battery = PWMLED(LED_LOW_BAT_PIN)
        self.led_critical = PWMLED(LED_CRITICAL_PIN)
        
        # Buzzer
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # Turn off all LEDs
        self._all_leds_off()
        print("✓ Indicators initialized")
    
    def _init_controls(self):
        """Initialize control buttons"""
        self.mode_button = Button(MODE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.calibrate_button = Button(CALIBRATE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.mode_button.when_pressed = self._cycle_display_mode
        self.calibrate_button.when_pressed = self._calibrate_voltage
        
        # Long press for battery type selection
        self.mode_button.when_held = self._cycle_battery_type
        
        print("✓ Controls initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Battery Monitor")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load saved configuration"""
        config_file = "battery_monitor_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.battery_type = config.get('battery_type', 'LiPo_3S')
                    self.calibration_offset = config.get('calibration_offset', 0.0)
                    self.low_battery_threshold = config.get('low_threshold', 20)
                    self.critical_battery_threshold = config.get('critical_threshold', 10)
                    print(f"✓ Configuration loaded: {self.battery_type}")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def _save_configuration(self):
        """Save current configuration"""
        config_file = "battery_monitor_config.json"
        try:
            config = {
                'battery_type': self.battery_type,
                'calibration_offset': self.calibration_offset,
                'low_threshold': self.low_battery_threshold,
                'critical_threshold': self.critical_battery_threshold,
                'last_saved': datetime.now().isoformat()
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
    
    def run(self):
        """Main system loop"""
        print(f"\n🔋 Battery Monitor Active! ({self.battery_type})")
        print("MODE: Change display mode (hold for battery type)")
        print("CALIBRATE: Calibrate voltage reading")
        print("Press Ctrl+C to exit\n")
        
        self.monitoring_active = True
        
        # Start monitoring threads
        voltage_thread = threading.Thread(target=self._voltage_monitoring_loop, daemon=True)
        display_thread = threading.Thread(target=self._display_update_loop, daemon=True)
        alert_thread = threading.Thread(target=self._alert_monitoring_loop, daemon=True)
        
        voltage_thread.start()
        display_thread.start()
        alert_thread.start()
        
        try:
            while True:
                # Process voltage readings
                self._process_voltage_data()
                
                # Update LED bar graph
                self._update_led_bar()
                
                # Check for data logging
                if time.time() - self.last_log_time > self.log_interval:
                    self._log_battery_data()
                    self.last_log_time = time.time()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down battery monitor...")
            self.monitoring_active = False
            time.sleep(0.5)
    
    def _voltage_monitoring_loop(self):
        """Continuous voltage monitoring"""
        while self.monitoring_active:
            try:
                # Read ADC value
                adc_value = self.adc.read(BATTERY_CHANNEL)
                
                # Convert to voltage
                adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE
                actual_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO
                
                # Apply calibration offset
                calibrated_voltage = actual_voltage + self.calibration_offset
                
                # Validate reading
                profile = BATTERY_PROFILES[self.battery_type]
                if 0 < calibrated_voltage < profile['full'] * 1.5:
                    # Add to queue
                    self.voltage_queue.put({
                        'voltage': calibrated_voltage,
                        'timestamp': datetime.now()
                    })
                
                time.sleep(0.5)  # Sample every 500ms
                
            except Exception as e:
                print(f"⚠ Voltage reading error: {e}")
                time.sleep(1)
    
    def _process_voltage_data(self):
        """Process queued voltage readings"""
        readings = []
        
        try:
            # Get all available readings
            while not self.voltage_queue.empty():
                data = self.voltage_queue.get_nowait()
                readings.append(data['voltage'])
                
                # Add to history
                self.voltage_history.append({
                    'voltage': data['voltage'],
                    'timestamp': data['timestamp']
                })
        except queue.Empty:
            pass
        
        if readings:
            # Calculate average voltage
            self.battery_voltage = mean(readings)
            
            # Update statistics
            self.total_samples += len(readings)
            if self.battery_voltage < self.min_voltage:
                self.min_voltage = self.battery_voltage
            if self.battery_voltage > self.max_voltage:
                self.max_voltage = self.battery_voltage
            
            # Maintain history size
            while len(self.voltage_history) > self.history_size:
                self.voltage_history.pop(0)
            
            # Calculate battery percentage
            self._calculate_battery_percentage()
            
            # Calculate discharge rate
            self._calculate_discharge_rate()
            
            # Update display
            self.display_queue.put({
                'voltage': self.battery_voltage,
                'percentage': self.battery_percentage,
                'discharge_rate': self.discharge_rate
            })
    
    def _calculate_battery_percentage(self):
        """Calculate battery percentage based on voltage"""
        profile = BATTERY_PROFILES[self.battery_type]
        
        # Linear interpolation between empty and full
        voltage_range = profile['full'] - profile['empty']
        voltage_above_empty = self.battery_voltage - profile['empty']
        
        percentage = (voltage_above_empty / voltage_range) * 100
        
        # Clamp to 0-100%
        self.battery_percentage = max(0, min(100, percentage))
    
    def _calculate_discharge_rate(self):
        """Calculate discharge rate from voltage history"""
        if len(self.voltage_history) < 10:
            return
        
        # Get data from last 30 seconds
        recent_history = self.voltage_history[-30:]
        if len(recent_history) < 2:
            return
        
        # Calculate voltage change over time
        start_voltage = recent_history[0]['voltage']
        end_voltage = recent_history[-1]['voltage']
        time_diff = (recent_history[-1]['timestamp'] - 
                    recent_history[0]['timestamp']).total_seconds()
        
        if time_diff > 0:
            # V/hour
            self.discharge_rate = (start_voltage - end_voltage) * 3600 / time_diff
    
    def _update_led_bar(self):
        """Update LED bar graph based on battery percentage"""
        # Calculate how many LEDs to light
        leds_to_light = int((self.battery_percentage / 100) * len(self.led_bar))
        
        # Update LEDs
        for i, led in enumerate(self.led_bar):
            if i < leds_to_light:
                led.on()
            else:
                led.off()
        
        # Color coding for last LED (if using RGB LEDs in real implementation)
        # Green: > 50%, Yellow: 20-50%, Red: < 20%
        if self.battery_percentage < self.critical_battery_threshold:
            # Critical - flash last LED
            if leds_to_light > 0:
                self.led_bar[leds_to_light - 1].off()
                self.led_bar[0].on()  # Keep at least one LED for visibility
        
        # Update status LEDs
        if self.battery_percentage < self.critical_battery_threshold:
            self.led_critical.pulse(fade_in_time=0.2, fade_out_time=0.2)
            self.led_low_battery.off()
        elif self.battery_percentage < self.low_battery_threshold:
            self.led_low_battery.pulse(fade_in_time=0.5, fade_out_time=0.5)
            self.led_critical.off()
        else:
            self.led_low_battery.off()
            self.led_critical.off()
    
    def _display_update_loop(self):
        """LCD display update thread"""
        while self.monitoring_active:
            try:
                # Get latest data
                display_data = None
                try:
                    while not self.display_queue.empty():
                        display_data = self.display_queue.get_nowait()
                except queue.Empty:
                    pass
                
                if display_data:
                    # Update display based on mode
                    if self.display_mode == DisplayMode.VOLTAGE:
                        self._show_voltage_display(display_data)
                    elif self.display_mode == DisplayMode.PERCENTAGE:
                        self._show_percentage_display(display_data)
                    elif self.display_mode == DisplayMode.TIME_REMAINING:
                        self._show_time_display(display_data)
                    elif self.display_mode == DisplayMode.STATISTICS:
                        self._show_statistics_display()
                    elif self.display_mode == DisplayMode.GRAPH:
                        self._show_graph_display()
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠ Display error: {e}")
    
    def _show_voltage_display(self, data):
        """Show voltage information"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Voltage and percentage
            self.lcd.write(0, 0, f"{data['voltage']:.2f}V  {data['percentage']:3.0f}%")
            
            # Battery type and status
            profile = BATTERY_PROFILES[self.battery_type]
            cells = profile['cells']
            cell_voltage = data['voltage'] / cells
            
            self.lcd.write(1, 0, f"{self.battery_type[:6]} {cell_voltage:.2f}V/cell")
            
        except Exception as e:
            print(f"⚠ Voltage display error: {e}")
    
    def _show_percentage_display(self, data):
        """Show percentage with bar graph"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Large percentage display
            percentage_str = f"{data['percentage']:3.0f}%"
            self.lcd.write(0, 0, f"Battery: {percentage_str}")
            
            # Visual bar graph on LCD
            bar_length = int((data['percentage'] / 100) * 16)
            bar = '█' * bar_length + '░' * (16 - bar_length)
            self.lcd.write(1, 0, bar)
            
        except:
            pass
    
    def _show_time_display(self, data):
        """Show estimated time remaining"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            # Calculate time remaining based on discharge rate
            if abs(data['discharge_rate']) > 0.01:
                profile = BATTERY_PROFILES[self.battery_type]
                voltage_remaining = data['voltage'] - profile['empty']
                hours_remaining = voltage_remaining / abs(data['discharge_rate'])
                
                if hours_remaining > 0:
                    hours = int(hours_remaining)
                    minutes = int((hours_remaining - hours) * 60)
                    
                    self.lcd.write(0, 0, f"Time Left:")
                    self.lcd.write(1, 0, f"{hours}h {minutes}m")
                else:
                    self.lcd.write(0, 0, "Time Left:")
                    self.lcd.write(1, 0, "Calculating...")
            else:
                self.lcd.write(0, 0, "Discharge Rate:")
                self.lcd.write(1, 0, "Too Low")
                
        except:
            pass
    
    def _show_statistics_display(self):
        """Show battery statistics"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            runtime = (datetime.now() - self.session_start).total_seconds() / 60
            
            self.lcd.write(0, 0, f"Min:{self.min_voltage:.1f} Max:{self.max_voltage:.1f}")
            self.lcd.write(1, 0, f"Runtime: {runtime:.0f}min")
            
        except:
            pass
    
    def _show_graph_display(self):
        """Show voltage trend graph"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            
            if len(self.voltage_history) > 1:
                # Get recent voltages
                recent = [h['voltage'] for h in self.voltage_history[-16:]]
                
                # Normalize to 0-7 range for graph characters
                v_min = min(recent)
                v_max = max(recent)
                v_range = v_max - v_min if v_max > v_min else 1
                
                # Create graph
                graph_chars = " ▁▂▃▄▅▆▇█"
                graph = ""
                for v in recent:
                    level = int(((v - v_min) / v_range) * 8)
                    graph += graph_chars[level]
                
                self.lcd.write(0, 0, "Voltage Trend:")
                self.lcd.write(1, 0, graph)
            else:
                self.lcd.write(0, 0, "Voltage Trend:")
                self.lcd.write(1, 0, "Collecting data...")
                
        except:
            pass
    
    def _alert_monitoring_loop(self):
        """Monitor for low battery alerts"""
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Check battery level
                if self.battery_percentage < self.critical_battery_threshold:
                    # Critical alert
                    if current_time - self.last_alert_time > self.alert_interval:
                        print(f"🚨 CRITICAL BATTERY: {self.battery_voltage:.2f}V ({self.battery_percentage:.0f}%)")
                        self.buzzer.beep(0.5, 0.5, n=5)
                        self.last_alert_time = current_time
                        
                elif self.battery_percentage < self.low_battery_threshold:
                    # Low battery alert
                    if current_time - self.last_alert_time > self.alert_interval * 2:
                        print(f"⚠️  LOW BATTERY: {self.battery_voltage:.2f}V ({self.battery_percentage:.0f}%)")
                        self.buzzer.beep(0.2, 0.3, n=3)
                        self.last_alert_time = current_time
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠ Alert error: {e}")
                time.sleep(5)
    
    def _cycle_display_mode(self):
        """Cycle through display modes"""
        modes = list(DisplayMode)
        current_index = modes.index(self.display_mode)
        new_index = (current_index + 1) % len(modes)
        self.display_mode = modes[new_index]
        
        print(f"📟 Display mode: {self.display_mode.value}")
        self.buzzer.beep(0.1, 0, n=1)
    
    def _cycle_battery_type(self):
        """Cycle through battery types (long press)"""
        types = list(BATTERY_PROFILES.keys())
        current_index = types.index(self.battery_type)
        new_index = (current_index + 1) % len(types)
        self.battery_type = types[new_index]
        
        print(f"🔋 Battery type: {self.battery_type}")
        
        # Save configuration
        self._save_configuration()
        
        # Update display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Battery Type:")
            self.lcd.write(1, 0, self.battery_type)
        
        self.buzzer.beep(0.1, 0.1, n=2)
        time.sleep(2)
    
    def _calibrate_voltage(self):
        """Calibrate voltage reading"""
        print("\n📏 Voltage Calibration")
        print("Measure actual battery voltage with multimeter")
        
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Calibration Mode")
            self.lcd.write(1, 0, f"Current: {self.battery_voltage:.2f}V")
        
        # Take multiple readings
        readings = []
        for i in range(20):
            adc_value = self.adc.read(BATTERY_CHANNEL)
            adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE
            actual_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO
            readings.append(actual_voltage)
            time.sleep(0.1)
        
        avg_reading = mean(readings)
        
        print(f"Average reading: {avg_reading:.3f}V")
        print("Enter actual voltage (or press Enter to cancel):")
        
        # In real implementation, would get user input
        # For now, just show the process
        print(f"Current offset: {self.calibration_offset:+.3f}V")
        
        self.buzzer.beep(0.1, 0.1, n=3)
    
    def _log_battery_data(self):
        """Log battery data to file"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'voltage': round(self.battery_voltage, 3),
                'percentage': round(self.battery_percentage, 1),
                'discharge_rate': round(self.discharge_rate, 3),
                'battery_type': self.battery_type
            }
            
            with open('battery_log.json', 'a') as f:
                json.dump(log_entry, f)
                f.write('\n')
                
        except Exception as e:
            print(f"⚠ Logging error: {e}")
    
    def _all_leds_off(self):
        """Turn off all LED indicators"""
        for led in self.led_bar:
            led.off()
        self.led_charging.off()
        self.led_low_battery.off()
        self.led_critical.off()
    
    def get_statistics(self):
        """Get battery statistics"""
        runtime = (datetime.now() - self.session_start).total_seconds()
        
        stats = {
            'runtime_seconds': runtime,
            'current_voltage': self.battery_voltage,
            'current_percentage': self.battery_percentage,
            'min_voltage': self.min_voltage,
            'max_voltage': self.max_voltage,
            'total_samples': self.total_samples,
            'discharge_rate': self.discharge_rate,
            'battery_type': self.battery_type
        }
        
        # Calculate average discharge rate
        if len(self.voltage_history) > 10:
            voltages = [h['voltage'] for h in self.voltage_history]
            stats['voltage_stability'] = stdev(voltages)
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop monitoring
        self.monitoring_active = False
        
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
        print(f"  Battery type: {stats['battery_type']}")
        print(f"  Voltage range: {stats['min_voltage']:.2f}V - {stats['max_voltage']:.2f}V")
        print(f"  Final voltage: {stats['current_voltage']:.2f}V ({stats['current_percentage']:.0f}%)")
        print(f"  Discharge rate: {stats['discharge_rate']:.3f} V/hour")
        print(f"  Total samples: {stats['total_samples']}")
        
        # Save final configuration
        self._save_configuration()
        
        # Close hardware
        for led in self.led_bar:
            led.close()
        self.led_charging.close()
        self.led_low_battery.close()
        self.led_critical.close()
        self.buzzer.close()
        self.mode_button.close()
        self.calibrate_button.close()
        
        print("\n✅ Cleanup complete")


def battery_demo():
    """Demonstrate battery monitoring features"""
    print("\n🎮 Battery Monitor Demo")
    print("=" * 50)
    
    monitor = BatteryVoltageMonitor()
    
    try:
        # Simulate different battery levels
        demo_voltages = [
            (12.6, "Full charge"),
            (12.0, "Nominal voltage"),
            (11.5, "Getting low"),
            (11.0, "Low battery warning"),
            (10.5, "Critical battery"),
            (11.8, "Charging")
        ]
        
        print(f"\nSimulating {monitor.battery_type} battery...")
        print("Watch the LED bar graph and display!\n")
        
        for voltage, description in demo_voltages:
            print(f"🔋 {voltage}V - {description}")
            
            # Simulate voltage reading
            monitor.battery_voltage = voltage
            monitor._calculate_battery_percentage()
            
            print(f"   Percentage: {monitor.battery_percentage:.0f}%")
            
            # Update displays
            monitor._update_led_bar()
            monitor.display_queue.put({
                'voltage': voltage,
                'percentage': monitor.battery_percentage,
                'discharge_rate': 0.1
            })
            
            time.sleep(3)
        
        print("\n✅ Demo complete!")
        
    finally:
        monitor.cleanup()


def discharge_test():
    """Test discharge rate calculation"""
    print("\n🔧 Discharge Rate Test")
    print("=" * 50)
    
    monitor = BatteryVoltageMonitor()
    
    try:
        print("Simulating battery discharge...")
        
        # Simulate gradual discharge
        start_voltage = 12.6
        for i in range(10):
            voltage = start_voltage - (i * 0.1)
            timestamp = datetime.now()
            
            monitor.voltage_history.append({
                'voltage': voltage,
                'timestamp': timestamp
            })
            
            if i > 0:
                monitor._calculate_discharge_rate()
                print(f"Voltage: {voltage:.2f}V, Discharge rate: {monitor.discharge_rate:.3f} V/hour")
            
            time.sleep(1)
        
    finally:
        monitor.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        battery_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "discharge":
        discharge_test()
    else:
        # Normal operation
        monitor = BatteryVoltageMonitor()
        try:
            monitor.run()
        finally:
            monitor.cleanup()