#!/usr/bin/env python3
"""
Temperature-Controlled Smart Fan System

Automatic fan speed control based on temperature with multiple
operating modes, LCD display, and comprehensive monitoring.
"""

import time
import threading
import queue
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean
from gpiozero import LED, PWMLED, Button, Buzzer
import RPi.GPIO as GPIO

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602
from adc0834 import ADC0834

# Hardware Pin Definitions
# Temperature Sensor (NTC Thermistor via ADC)
ADC_CS_PIN = 5
ADC_CLK_PIN = 6
ADC_DI_PIN = 16
ADC_DO_PIN = 12
TEMP_CHANNEL = 0        # ADC channel for temperature

# Fan Control
FAN_PWM_PIN = 18        # PWM control for fan speed
FAN_TACH_PIN = 17       # Tachometer input (fan RPM)
FAN_ENABLE_PIN = 27     # Fan enable/disable

# Status LEDs
LED_COOL_PIN = 22       # Blue - Cool temperature
LED_NORMAL_PIN = 23     # Green - Normal temperature
LED_WARM_PIN = 24       # Yellow - Warm temperature
LED_HOT_PIN = 25        # Red - Hot temperature

# Control Buttons
MODE_BUTTON_PIN = 19
UP_BUTTON_PIN = 20
DOWN_BUTTON_PIN = 21
POWER_BUTTON_PIN = 26

# Alert Buzzer
BUZZER_PIN = 13

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Setpoint Potentiometer (via ADC)
SETPOINT_CHANNEL = 1    # ADC channel for setpoint

# Temperature Thresholds (Celsius)
TEMP_COOL = 20          # Below this is cool
TEMP_NORMAL = 25        # Normal room temperature
TEMP_WARM = 30          # Getting warm
TEMP_HOT = 35           # Hot - maximum cooling

# Fan Speed Levels (0-100%)
FAN_OFF = 0
FAN_LOW = 30
FAN_MEDIUM = 60
FAN_HIGH = 80
FAN_MAX = 100

# Thermistor Constants (for 10K NTC thermistor)
THERMISTOR_NOMINAL = 10000    # Resistance at 25°C
TEMP_NOMINAL = 25             # Temperature for nominal resistance
B_COEFFICIENT = 3950          # Beta coefficient
SERIES_RESISTOR = 10000       # Value of series resistor

class FanMode(Enum):
    """Fan operating modes"""
    AUTO = "Auto"
    MANUAL = "Manual"
    ECO = "Eco"
    TURBO = "Turbo"
    SILENT = "Silent"
    SCHEDULE = "Schedule"

class TemperatureControlledFan:
    """Main smart fan system class"""
    
    def __init__(self):
        print("🌡️  Initializing Temperature-Controlled Fan System...")
        
        # Initialize hardware
        self._init_sensors()
        self._init_fan_control()
        self._init_indicators()
        self._init_controls()
        self._init_display()
        
        # System state
        self.current_temp = None
        self.target_temp = 25.0
        self.fan_speed = 0
        self.fan_rpm = 0
        self.fan_enabled = True
        self.mode = FanMode.AUTO
        
        # Control parameters
        self.hysteresis = 1.0  # Temperature hysteresis
        self.min_fan_speed = 20  # Minimum PWM for fan to start
        self.max_temp_limit = 40  # Safety limit
        
        # Temperature history
        self.temp_history = []
        self.history_size = 60  # Keep 1 minute of data
        
        # Fan curves for different modes
        self.fan_curves = {
            FanMode.AUTO: self._auto_fan_curve,
            FanMode.ECO: self._eco_fan_curve,
            FanMode.TURBO: self._turbo_fan_curve,
            FanMode.SILENT: self._silent_fan_curve
        }
        
        # Schedule settings
        self.schedule_enabled = False
        self.schedule = self._default_schedule()
        
        # Statistics
        self.session_start = datetime.now()
        self.total_runtime = timedelta()
        self.energy_saved = 0.0  # Estimated energy savings
        self.temp_stats = {
            'min': float('inf'),
            'max': float('-inf'),
            'avg': 0
        }
        
        # Threading
        self.monitoring_active = False
        self.sensor_queue = queue.Queue()
        self.display_queue = queue.Queue()
        
        # RPM measurement
        self.rpm_pulses = 0
        self.last_rpm_time = time.time()
        
        # Load configuration
        self._load_configuration()
        
        print("✅ Smart fan system initialized")
    
    def _init_sensors(self):
        """Initialize temperature sensor (ADC)"""
        self.adc = ADC0834(cs=ADC_CS_PIN, clk=ADC_CLK_PIN,
                          di=ADC_DI_PIN, do=ADC_DO_PIN)
        print("✓ Temperature sensor initialized")
    
    def _init_fan_control(self):
        """Initialize fan control hardware"""
        # PWM fan control
        self.fan_pwm = PWMLED(FAN_PWM_PIN)
        self.fan_enable = LED(FAN_ENABLE_PIN)
        
        # Tachometer setup for RPM measurement
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FAN_TACH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(FAN_TACH_PIN, GPIO.FALLING, 
                            callback=self._rpm_pulse_callback)
        
        print("✓ Fan control initialized")
    
    def _init_indicators(self):
        """Initialize LED indicators"""
        self.led_cool = LED(LED_COOL_PIN)
        self.led_normal = LED(LED_NORMAL_PIN)
        self.led_warm = LED(LED_WARM_PIN)
        self.led_hot = PWMLED(LED_HOT_PIN)
        
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # Test LEDs
        self._all_leds_off()
        print("✓ Indicators initialized")
    
    def _init_controls(self):
        """Initialize control buttons"""
        self.mode_button = Button(MODE_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.up_button = Button(UP_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.down_button = Button(DOWN_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        self.power_button = Button(POWER_BUTTON_PIN, pull_up=True, bounce_time=0.1)
        
        # Button callbacks
        self.mode_button.when_pressed = self._cycle_mode
        self.up_button.when_pressed = self._increase_target
        self.down_button.when_pressed = self._decrease_target
        self.power_button.when_pressed = self._toggle_power
        
        print("✓ Controls initialized")
    
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Smart Fan System")
            self.lcd.write(1, 0, "Initializing...")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
    
    def _load_configuration(self):
        """Load saved configuration"""
        config_file = "fan_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    self.mode = FanMode(config.get('mode', 'Auto'))
                    self.target_temp = config.get('target_temp', 25.0)
                    self.schedule = config.get('schedule', self._default_schedule())
                    print(f"✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
    
    def _save_configuration(self):
        """Save current configuration"""
        config_file = "fan_config.json"
        try:
            config = {
                'mode': self.mode.value,
                'target_temp': self.target_temp,
                'schedule': self.schedule,
                'last_saved': datetime.now().isoformat()
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
    
    def _default_schedule(self):
        """Default temperature schedule"""
        return {
            "00:00": 22,  # Night - cooler
            "06:00": 24,  # Morning
            "08:00": 25,  # Day
            "18:00": 24,  # Evening
            "22:00": 22   # Night
        }
    
    def run(self):
        """Main system loop"""
        print("\n🌡️  Smart Fan System Active!")
        print("MODE: Change operating mode")
        print("UP/DOWN: Adjust target temperature")
        print("POWER: Toggle fan on/off")
        print("Press Ctrl+C to exit\n")
        
        self.monitoring_active = True
        
        # Start monitoring threads
        sensor_thread = threading.Thread(target=self._sensor_monitoring_loop, daemon=True)
        fan_thread = threading.Thread(target=self._fan_control_loop, daemon=True)
        display_thread = threading.Thread(target=self._display_update_loop, daemon=True)
        rpm_thread = threading.Thread(target=self._rpm_monitoring_loop, daemon=True)
        
        sensor_thread.start()
        fan_thread.start()
        display_thread.start()
        rpm_thread.start()
        
        try:
            while True:
                # Update target from potentiometer if in manual mode
                if self.mode == FanMode.MANUAL:
                    self._update_manual_target()
                
                # Process sensor data
                self._process_sensor_data()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Shutting down smart fan system...")
            self.monitoring_active = False
            self._set_fan_speed(0)
            time.sleep(0.5)
    
    def _sensor_monitoring_loop(self):
        """Continuous temperature monitoring"""
        while self.monitoring_active:
            try:
                # Read temperature from ADC
                adc_value = self.adc.read(TEMP_CHANNEL)
                
                # Convert ADC value to temperature
                temperature = self._adc_to_temperature(adc_value)
                
                # Validate reading
                if -10 <= temperature <= 50:  # Reasonable range
                    self.current_temp = temperature
                    
                    # Add to history
                    self.temp_history.append({
                        'time': datetime.now(),
                        'temp': temperature
                    })
                    
                    # Maintain history size
                    if len(self.temp_history) > self.history_size:
                        self.temp_history.pop(0)
                    
                    # Update statistics
                    self._update_statistics(temperature)
                    
                    # Queue temperature update
                    self.sensor_queue.put({
                        'type': 'temperature',
                        'value': temperature
                    })
                
                time.sleep(1)  # Read every second
                
            except Exception as e:
                print(f"⚠ Sensor error: {e}")
                time.sleep(1)
    
    def _adc_to_temperature(self, adc_value):
        """Convert ADC reading to temperature using Steinhart-Hart equation"""
        # Convert ADC to resistance
        if adc_value == 0:
            adc_value = 1  # Prevent division by zero
        
        resistance = SERIES_RESISTOR / (255.0 / adc_value - 1.0)
        
        # Steinhart-Hart equation
        import math
        steinhart = resistance / THERMISTOR_NOMINAL
        steinhart = math.log(steinhart)
        steinhart /= B_COEFFICIENT
        steinhart += 1.0 / (TEMP_NOMINAL + 273.15)
        steinhart = 1.0 / steinhart
        steinhart -= 273.15  # Convert to Celsius
        
        return steinhart
    
    def _fan_control_loop(self):
        """Fan speed control loop"""
        while self.monitoring_active:
            try:
                if self.fan_enabled and self.current_temp is not None:
                    # Get target speed based on mode
                    if self.mode == FanMode.MANUAL:
                        target_speed = self._manual_speed_control()
                    elif self.mode == FanMode.SCHEDULE:
                        self._update_scheduled_target()
                        target_speed = self._auto_fan_curve(self.current_temp)
                    else:
                        # Use mode-specific fan curve
                        fan_curve = self.fan_curves.get(self.mode, self._auto_fan_curve)
                        target_speed = fan_curve(self.current_temp)
                    
                    # Apply speed with smoothing
                    self._set_fan_speed(target_speed)
                else:
                    self._set_fan_speed(0)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠ Fan control error: {e}")
                time.sleep(1)
    
    def _auto_fan_curve(self, temp):
        """Automatic fan curve based on temperature"""
        if temp < self.target_temp - self.hysteresis:
            return FAN_OFF
        elif temp < self.target_temp:
            # Proportional control near target
            ratio = (temp - (self.target_temp - self.hysteresis)) / self.hysteresis
            return FAN_LOW * ratio
        elif temp < self.target_temp + 5:
            # Linear increase above target
            ratio = (temp - self.target_temp) / 5
            return FAN_LOW + (FAN_MEDIUM - FAN_LOW) * ratio
        elif temp < self.target_temp + 10:
            # Faster increase when hot
            ratio = (temp - self.target_temp - 5) / 5
            return FAN_MEDIUM + (FAN_HIGH - FAN_MEDIUM) * ratio
        else:
            # Maximum cooling when very hot
            return FAN_MAX
    
    def _eco_fan_curve(self, temp):
        """Energy-saving fan curve"""
        if temp < self.target_temp + 2:
            return FAN_OFF
        elif temp < self.target_temp + 5:
            return FAN_LOW
        elif temp < self.target_temp + 8:
            return FAN_MEDIUM
        else:
            return FAN_HIGH  # Never goes to maximum
    
    def _turbo_fan_curve(self, temp):
        """Aggressive cooling curve"""
        if temp < self.target_temp - 2:
            return FAN_OFF
        elif temp < self.target_temp:
            return FAN_MEDIUM
        elif temp < self.target_temp + 3:
            return FAN_HIGH
        else:
            return FAN_MAX
    
    def _silent_fan_curve(self, temp):
        """Quiet operation curve"""
        if temp < self.target_temp + 3:
            return FAN_OFF
        elif temp < self.target_temp + 6:
            return FAN_LOW
        else:
            return FAN_MEDIUM  # Never exceeds medium speed
    
    def _manual_speed_control(self):
        """Manual speed based on temperature difference"""
        if self.current_temp < self.target_temp:
            return FAN_OFF
        else:
            # Simple proportional control
            diff = self.current_temp - self.target_temp
            speed = min(FAN_MAX, FAN_LOW + diff * 10)
            return speed
    
    def _set_fan_speed(self, speed):
        """Set fan speed with PWM"""
        # Clamp speed to valid range
        speed = max(0, min(100, speed))
        
        # Apply minimum speed threshold
        if 0 < speed < self.min_fan_speed:
            speed = self.min_fan_speed
        
        # Smooth speed changes
        if abs(speed - self.fan_speed) > 5:
            # Large change - ramp to new speed
            step = 5 if speed > self.fan_speed else -5
            new_speed = self.fan_speed + step
        else:
            new_speed = speed
        
        self.fan_speed = new_speed
        
        # Set PWM duty cycle
        if self.fan_speed > 0:
            self.fan_enable.on()
            self.fan_pwm.value = self.fan_speed / 100.0
        else:
            self.fan_pwm.value = 0
            self.fan_enable.off()
        
        # Update display
        self.display_queue.put({
            'type': 'fan_speed',
            'value': self.fan_speed
        })
    
    def _rpm_pulse_callback(self, channel):
        """Callback for fan tachometer pulses"""
        self.rpm_pulses += 1
    
    def _rpm_monitoring_loop(self):
        """Calculate fan RPM from tachometer pulses"""
        while self.monitoring_active:
            # Count pulses over 1 second
            self.rpm_pulses = 0
            time.sleep(1)
            
            # Calculate RPM (2 pulses per revolution for typical fans)
            self.fan_rpm = (self.rpm_pulses * 60) // 2
            
            # Update display
            self.display_queue.put({
                'type': 'rpm',
                'value': self.fan_rpm
            })
    
    def _display_update_loop(self):
        """LCD display update thread"""
        display_mode = 0
        last_rotation = time.time()
        
        while self.monitoring_active:
            try:
                # Process display queue
                try:
                    while not self.display_queue.empty():
                        update = self.display_queue.get_nowait()
                        # Updates are processed in main display
                except queue.Empty:
                    pass
                
                # Rotate display every 3 seconds
                if time.time() - last_rotation > 3:
                    if display_mode == 0:
                        self._show_main_display()
                    elif display_mode == 1:
                        self._show_status_display()
                    elif display_mode == 2:
                        self._show_statistics_display()
                    
                    display_mode = (display_mode + 1) % 3
                    last_rotation = time.time()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠ Display error: {e}")
    
    def _show_main_display(self):
        """Show main temperature and fan info"""
        if not self.lcd:
            return
        
        try:
            # Temperature display
            temp_str = f"{self.current_temp:.1f}°C" if self.current_temp else "--.-°C"
            target_str = f"{self.target_temp:.0f}°C"
            
            self.lcd.clear()
            self.lcd.write(0, 0, f"Temp: {temp_str}")
            self.lcd.write(0, 11, f"→{target_str}")
            
            # Fan status
            if self.fan_enabled:
                fan_str = f"Fan: {self.fan_speed:3.0f}%"
                if self.fan_rpm > 0:
                    fan_str += f" {self.fan_rpm}rpm"
            else:
                fan_str = "Fan: OFF"
            
            self.lcd.write(1, 0, fan_str[:16])
            
        except Exception as e:
            print(f"⚠ Main display error: {e}")
    
    def _show_status_display(self):
        """Show system status"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, f"Mode: {self.mode.value}")
            
            # Power status and time
            status = "ON" if self.fan_enabled else "OFF"
            runtime = (datetime.now() - self.session_start).total_seconds() / 60
            self.lcd.write(1, 0, f"Pwr:{status} Run:{runtime:.0f}m")
            
        except:
            pass
    
    def _show_statistics_display(self):
        """Show temperature statistics"""
        if not self.lcd:
            return
        
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, f"Min:{self.temp_stats['min']:.1f} Max:{self.temp_stats['max']:.1f}")
            self.lcd.write(1, 0, f"Avg:{self.temp_stats['avg']:.1f}°C")
            
            # Energy saving indicator
            if self.mode == FanMode.ECO:
                self.lcd.write(1, 12, "ECO")
                
        except:
            pass
    
    def _process_sensor_data(self):
        """Process queued sensor data"""
        try:
            while not self.sensor_queue.empty():
                data = self.sensor_queue.get_nowait()
                
                if data['type'] == 'temperature':
                    self._update_temperature_display(data['value'])
                    self._update_led_indicators(data['value'])
                    
        except queue.Empty:
            pass
    
    def _update_temperature_display(self, temp):
        """Update temperature-related displays"""
        # Check for extreme temperatures
        if temp > self.max_temp_limit:
            print(f"⚠️  WARNING: High temperature: {temp:.1f}°C")
            if hasattr(self, 'last_alert_time'):
                if time.time() - self.last_alert_time > 30:  # Alert every 30s
                    self.buzzer.beep(0.5, 0.5, n=3)
                    self.last_alert_time = time.time()
            else:
                self.buzzer.beep(0.5, 0.5, n=3)
                self.last_alert_time = time.time()
    
    def _update_led_indicators(self, temp):
        """Update LED indicators based on temperature"""
        # Turn off all LEDs first
        self._all_leds_off()
        
        # Light appropriate LED
        if temp < TEMP_COOL:
            self.led_cool.on()
        elif temp < TEMP_NORMAL:
            self.led_normal.on()
        elif temp < TEMP_WARM:
            self.led_warm.on()
        else:
            # Hot - pulse red LED
            self.led_hot.pulse(fade_in_time=0.5, fade_out_time=0.5)
    
    def _all_leds_off(self):
        """Turn off all LED indicators"""
        self.led_cool.off()
        self.led_normal.off()
        self.led_warm.off()
        self.led_hot.off()
    
    def _cycle_mode(self):
        """Cycle through operating modes"""
        modes = list(FanMode)
        current_index = modes.index(self.mode)
        new_index = (current_index + 1) % len(modes)
        self.mode = modes[new_index]
        
        print(f"🔄 Mode: {self.mode.value}")
        
        # Save configuration
        self._save_configuration()
        
        # Update display immediately
        self._show_status_display()
        
        # Beep confirmation
        self.buzzer.beep(0.1, 0.1, n=1)
    
    def _increase_target(self):
        """Increase target temperature"""
        if self.target_temp < 35:
            self.target_temp += 1
            print(f"📈 Target temperature: {self.target_temp}°C")
            self._save_configuration()
            self.buzzer.beep(0.05, 0, n=1)
    
    def _decrease_target(self):
        """Decrease target temperature"""
        if self.target_temp > 15:
            self.target_temp -= 1
            print(f"📉 Target temperature: {self.target_temp}°C")
            self._save_configuration()
            self.buzzer.beep(0.05, 0, n=1)
    
    def _toggle_power(self):
        """Toggle fan power on/off"""
        self.fan_enabled = not self.fan_enabled
        
        if self.fan_enabled:
            print("🔌 Fan enabled")
            self.buzzer.beep(0.1, 0.1, n=1)
        else:
            print("🔌 Fan disabled")
            self._set_fan_speed(0)
            self.buzzer.beep(0.1, 0.1, n=2)
    
    def _update_manual_target(self):
        """Update target temperature from potentiometer"""
        try:
            # Read setpoint potentiometer
            adc_value = self.adc.read(SETPOINT_CHANNEL)
            
            # Map to temperature range (15-35°C)
            self.target_temp = 15 + (adc_value / 255) * 20
            
        except:
            pass
    
    def _update_scheduled_target(self):
        """Update target based on schedule"""
        if not self.schedule_enabled:
            return
        
        current_time = datetime.now().strftime("%H:%M")
        
        # Find applicable schedule entry
        scheduled_temp = None
        for time_str, temp in sorted(self.schedule.items()):
            if current_time >= time_str:
                scheduled_temp = temp
        
        if scheduled_temp is not None:
            self.target_temp = scheduled_temp
    
    def _update_statistics(self, temp):
        """Update temperature statistics"""
        if temp < self.temp_stats['min']:
            self.temp_stats['min'] = temp
        if temp > self.temp_stats['max']:
            self.temp_stats['max'] = temp
        
        # Calculate running average
        if self.temp_history:
            temps = [entry['temp'] for entry in self.temp_history]
            self.temp_stats['avg'] = mean(temps)
    
    def get_statistics(self):
        """Get system statistics"""
        stats = {
            'runtime': (datetime.now() - self.session_start).total_seconds(),
            'current_temp': self.current_temp,
            'target_temp': self.target_temp,
            'fan_speed': self.fan_speed,
            'fan_rpm': self.fan_rpm,
            'mode': self.mode.value,
            'temp_min': self.temp_stats['min'],
            'temp_max': self.temp_stats['max'],
            'temp_avg': self.temp_stats['avg']
        }
        
        # Calculate energy savings (simplified)
        if self.mode == FanMode.ECO:
            # Estimate 30% energy saving in ECO mode
            runtime_hours = stats['runtime'] / 3600
            stats['energy_saved'] = runtime_hours * 0.3  # kWh saved
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Turn off fan
        self._set_fan_speed(0)
        self.fan_enable.off()
        
        # Turn off indicators
        self._all_leds_off()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "System Off")
        
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Session Statistics:")
        print(f"  Runtime: {stats['runtime']/60:.1f} minutes")
        print(f"  Temperature range: {stats['temp_min']:.1f}°C - {stats['temp_max']:.1f}°C")
        print(f"  Average temperature: {stats['temp_avg']:.1f}°C")
        if 'energy_saved' in stats:
            print(f"  Estimated energy saved: {stats['energy_saved']:.2f} kWh")
        
        # Save final configuration
        self._save_configuration()
        
        # Clean up GPIO
        GPIO.cleanup()
        
        # Close hardware
        self.fan_pwm.close()
        self.fan_enable.close()
        self.led_cool.close()
        self.led_normal.close()
        self.led_warm.close()
        self.led_hot.close()
        self.buzzer.close()
        self.mode_button.close()
        self.up_button.close()
        self.down_button.close()
        self.power_button.close()
        
        print("\n✅ Cleanup complete")


def temperature_demo():
    """Demonstrate temperature control features"""
    print("\n🎮 Temperature Control Demo")
    print("=" * 50)
    
    fan = TemperatureControlledFan()
    
    try:
        # Simulate different temperatures
        demo_temps = [
            (18, "Cool - Fan off"),
            (23, "Normal - Fan low"),
            (28, "Warm - Fan medium"),
            (33, "Hot - Fan high"),
            (38, "Very hot - Fan maximum"),
            (25, "Back to normal")
        ]
        
        print("\nSimulating temperature changes...")
        print("Watch the fan speed and LED indicators!\n")
        
        for temp, description in demo_temps:
            print(f"🌡️  Temperature: {temp}°C - {description}")
            
            # Simulate temperature
            fan.current_temp = temp
            fan._update_led_indicators(temp)
            
            # Calculate fan speed
            if fan.mode in fan.fan_curves:
                speed = fan.fan_curves[fan.mode](temp)
            else:
                speed = fan._auto_fan_curve(temp)
            
            fan._set_fan_speed(speed)
            
            print(f"   Fan speed: {fan.fan_speed}%")
            
            # Show on display
            fan._show_main_display()
            
            time.sleep(3)
        
        print("\n✅ Demo complete!")
        
    finally:
        fan.cleanup()


def mode_test():
    """Test different operating modes"""
    print("\n🔧 Mode Test")
    print("=" * 50)
    
    fan = TemperatureControlledFan()
    
    try:
        test_temp = 30  # Test at 30°C
        fan.current_temp = test_temp
        
        print(f"Testing all modes at {test_temp}°C:\n")
        
        for mode in FanMode:
            fan.mode = mode
            print(f"{mode.value} mode:")
            
            if mode in fan.fan_curves:
                speed = fan.fan_curves[mode](test_temp)
            elif mode == FanMode.MANUAL:
                speed = fan._manual_speed_control()
            else:
                speed = fan._auto_fan_curve(test_temp)
            
            print(f"  Fan speed: {speed}%")
            
            time.sleep(1)
        
    finally:
        fan.cleanup()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        temperature_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "modes":
        mode_test()
    else:
        # Normal operation
        fan = TemperatureControlledFan()
        try:
            fan.run()
        finally:
            fan.cleanup()