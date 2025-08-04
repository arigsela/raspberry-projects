#!/usr/bin/env python3
"""
Thermistor Temperature Sensing
Measure temperature using NTC thermistor with ADC
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

from adc0834 import ADC0834
from gpiozero import LED, Buzzer, PWMLED
import time
import signal
import math
from datetime import datetime
import statistics

# GPIO Configuration
ADC_CS = 17    # ADC Chip Select
ADC_CLK = 18   # ADC Clock
ADC_DI = 27    # ADC Data In
ADC_DO = 22    # ADC Data Out
THERMISTOR_CHANNEL = 0  # ADC channel for thermistor

# Optional outputs
LED_PIN = 23      # Temperature indicator LED
BUZZER_PIN = 24   # Over-temp alarm

# Thermistor parameters (10K NTC)
THERMISTOR_NOMINAL = 10000    # Resistance at 25°C
TEMPERATURE_NOMINAL = 25      # Temperature for nominal resistance
B_COEFFICIENT = 3950          # Beta coefficient
SERIES_RESISTOR = 10000       # Fixed resistor value

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class Thermistor:
    """Thermistor temperature sensor class"""
    
    def __init__(self, adc, channel, r_nominal=10000, t_nominal=25, beta=3950, r_series=10000):
        """
        Initialize thermistor
        
        Args:
            adc: ADC0834 instance
            channel: ADC channel
            r_nominal: Nominal resistance at t_nominal
            t_nominal: Temperature for nominal resistance (Celsius)
            beta: Beta coefficient
            r_series: Series resistor value
        """
        self.adc = adc
        self.channel = channel
        self.r_nominal = r_nominal
        self.t_nominal = t_nominal + 273.15  # Convert to Kelvin
        self.beta = beta
        self.r_series = r_series
        
        # Calibration offset
        self.calibration_offset = 0
    
    def read_resistance(self):
        """Read thermistor resistance"""
        # Read ADC value
        adc_value = self.adc.read_channel(self.channel)
        
        if adc_value == 0:
            return float('inf')  # Open circuit
        elif adc_value == 255:
            return 0  # Short circuit
        
        # Calculate resistance using voltage divider
        # Vout = Vin * R2 / (R1 + R2)
        # R2 = R1 * Vout / (Vin - Vout)
        ratio = adc_value / 255.0
        resistance = self.r_series * ratio / (1 - ratio)
        
        return resistance
    
    def read_temperature_c(self):
        """Read temperature in Celsius"""
        # Get resistance
        resistance = self.read_resistance()
        
        if resistance <= 0 or resistance == float('inf'):
            return None
        
        # Steinhart-Hart equation (simplified with Beta)
        # 1/T = 1/T0 + (1/B) * ln(R/R0)
        temp_k = 1.0 / (1.0 / self.t_nominal + 
                        (1.0 / self.beta) * math.log(resistance / self.r_nominal))
        
        # Convert to Celsius
        temp_c = temp_k - 273.15 + self.calibration_offset
        
        return temp_c
    
    def read_temperature_f(self):
        """Read temperature in Fahrenheit"""
        temp_c = self.read_temperature_c()
        if temp_c is None:
            return None
        return temp_c * 9.0 / 5.0 + 32
    
    def calibrate(self, known_temp_c):
        """Calibrate sensor with known temperature"""
        current_temp = self.read_temperature_c()
        if current_temp is not None:
            self.calibration_offset = known_temp_c - current_temp
            return True
        return False

def basic_temperature_reading():
    """Basic temperature measurement"""
    print("\n=== Basic Temperature Reading ===")
    print("Reading temperature from thermistor...")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    try:
        while True:
            temp_c = thermistor.read_temperature_c()
            
            if temp_c is not None:
                temp_f = thermistor.read_temperature_f()
                resistance = thermistor.read_resistance()
                
                print(f"\rTemperature: {temp_c:5.1f}°C ({temp_f:5.1f}°F) | "
                      f"Resistance: {resistance:6.0f}Ω", end='')
            else:
                print("\rTemperature: ERROR - Check connections", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        adc.cleanup()

def temperature_monitor():
    """Temperature monitoring with statistics"""
    print("\n=== Temperature Monitor ===")
    print("Monitoring temperature with min/max tracking")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    # Statistics tracking
    readings = []
    min_temp = float('inf')
    max_temp = float('-inf')
    start_time = time.time()
    
    try:
        while True:
            temp_c = thermistor.read_temperature_c()
            
            if temp_c is not None:
                readings.append(temp_c)
                if len(readings) > 120:  # Keep last 2 minutes
                    readings.pop(0)
                
                # Update min/max
                min_temp = min(min_temp, temp_c)
                max_temp = max(max_temp, temp_c)
                
                # Calculate average
                avg_temp = statistics.mean(readings)
                
                # Display
                elapsed = int(time.time() - start_time)
                print(f"\rCurrent: {temp_c:5.1f}°C | "
                      f"Avg: {avg_temp:5.1f}°C | "
                      f"Min: {min_temp:5.1f}°C | "
                      f"Max: {max_temp:5.1f}°C | "
                      f"Time: {elapsed}s", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n--- Temperature Summary ---")
        print(f"Recording duration: {(time.time() - start_time)/60:.1f} minutes")
        print(f"Samples collected: {len(readings)}")
        if readings:
            print(f"Average: {statistics.mean(readings):.1f}°C")
            print(f"Minimum: {min_temp:.1f}°C")
            print(f"Maximum: {max_temp:.1f}°C")
            print(f"Std Dev: {statistics.stdev(readings):.2f}°C" if len(readings) > 1 else "")
    finally:
        adc.cleanup()

def thermostat_control():
    """Thermostat simulation with hysteresis"""
    print("\n=== Thermostat Control ===")
    print("Simulating temperature control")
    print("Set point: 25°C ± 2°C")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    try:
        led = LED(LED_PIN)  # Represents heater/cooler
        has_led = True
    except:
        has_led = False
        print("Note: No LED connected for heater simulation")
    
    # Thermostat settings
    set_point = 25.0
    hysteresis = 2.0
    heater_on = False
    
    try:
        while True:
            temp_c = thermistor.read_temperature_c()
            
            if temp_c is not None:
                # Thermostat logic
                if temp_c < (set_point - hysteresis) and not heater_on:
                    heater_on = True
                    if has_led:
                        led.on()
                    print(f"\n{datetime.now().strftime('%H:%M:%S')} - Heater ON")
                elif temp_c > (set_point + hysteresis) and heater_on:
                    heater_on = False
                    if has_led:
                        led.off()
                    print(f"\n{datetime.now().strftime('%H:%M:%S')} - Heater OFF")
                
                # Status display
                status = "HEATING" if heater_on else "IDLE"
                deviation = temp_c - set_point
                bar_pos = int((deviation + 5) * 2)  # Scale to 0-20
                bar_pos = max(0, min(20, bar_pos))
                
                bar = " " * bar_pos + "|" + " " * (20 - bar_pos)
                
                print(f"\rTemp: {temp_c:5.1f}°C [{bar}] "
                      f"Set: {set_point}°C | {status:7s}", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_led:
            led.close()
        adc.cleanup()

def temperature_alarm():
    """Over-temperature alarm system"""
    print("\n=== Temperature Alarm ===")
    print("Alerts when temperature exceeds threshold")
    
    # Get threshold
    try:
        threshold = float(input("Enter alarm threshold (°C) [30]: ") or "30")
    except ValueError:
        threshold = 30.0
    
    print(f"Alarm set for temperatures above {threshold}°C")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
    
    try:
        led = LED(LED_PIN)
        has_led = True
    except:
        has_led = False
    
    alarm_active = False
    alarm_count = 0
    
    try:
        while True:
            temp_c = thermistor.read_temperature_c()
            
            if temp_c is not None:
                if temp_c > threshold and not alarm_active:
                    alarm_active = True
                    alarm_count += 1
                    print(f"\n⚠️ ALARM! Temperature {temp_c:.1f}°C exceeds {threshold}°C")
                    
                    if has_buzzer:
                        buzzer.beep(0.2, 0.2, n=3)
                    if has_led:
                        led.blink(0.2, 0.2)
                        
                elif temp_c <= (threshold - 1) and alarm_active:  # Hysteresis
                    alarm_active = False
                    print(f"\n✓ Temperature normal: {temp_c:.1f}°C")
                    
                    if has_buzzer:
                        buzzer.off()
                    if has_led:
                        led.off()
                
                # Status display
                status = "ALARM!" if alarm_active else "Normal"
                margin = threshold - temp_c
                
                print(f"\rTemp: {temp_c:5.1f}°C | "
                      f"Threshold: {threshold}°C | "
                      f"Margin: {margin:+5.1f}°C | "
                      f"Status: {status:6s}", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal alarms triggered: {alarm_count}")
    finally:
        if has_buzzer:
            buzzer.close()
        if has_led:
            led.close()
        adc.cleanup()

def temperature_logger():
    """Log temperature data to file"""
    print("\n=== Temperature Logger ===")
    print("Logging temperature data to file")
    
    # Create log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"temperature_log_{timestamp}.csv"
    
    print(f"Logging to: {filename}")
    print("Press Ctrl+C to stop")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    sample_count = 0
    
    try:
        with open(filename, 'w') as f:
            # Write header
            f.write("Timestamp,Temperature_C,Temperature_F,Resistance_Ohm\n")
            
            while True:
                temp_c = thermistor.read_temperature_c()
                
                if temp_c is not None:
                    temp_f = thermistor.read_temperature_f()
                    resistance = thermistor.read_resistance()
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Write to file
                    f.write(f"{timestamp},{temp_c:.2f},{temp_f:.2f},{resistance:.0f}\n")
                    f.flush()  # Ensure data is written
                    
                    sample_count += 1
                    
                    # Display status
                    print(f"\rSamples logged: {sample_count} | "
                          f"Current: {temp_c:.1f}°C", end='')
                
                time.sleep(1)  # Log every second
    
    except KeyboardInterrupt:
        print(f"\n\nLogging stopped. {sample_count} samples saved to {filename}")
    finally:
        adc.cleanup()

def temperature_trend():
    """Display temperature trend with visual graph"""
    print("\n=== Temperature Trend ===")
    print("Visual temperature trend display")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    # Trend buffer (last 50 samples)
    trend_buffer = []
    graph_height = 10
    
    try:
        while True:
            temp_c = thermistor.read_temperature_c()
            
            if temp_c is not None:
                trend_buffer.append(temp_c)
                if len(trend_buffer) > 50:
                    trend_buffer.pop(0)
                
                if len(trend_buffer) > 1:
                    # Calculate trend
                    temp_min = min(trend_buffer)
                    temp_max = max(trend_buffer)
                    temp_range = temp_max - temp_min
                    
                    if temp_range < 0.1:
                        temp_range = 1.0  # Minimum range
                    
                    # Create graph
                    print("\n" * (graph_height + 3))  # Clear screen area
                    print(f"\033[{graph_height + 3}A", end='')  # Move cursor up
                    
                    print(f"Temperature Trend - Current: {temp_c:.1f}°C")
                    print(f"Range: {temp_min:.1f}°C to {temp_max:.1f}°C")
                    print("-" * 52)
                    
                    # Draw graph
                    for row in range(graph_height, 0, -1):
                        line = ""
                        threshold = temp_min + (row - 1) * temp_range / (graph_height - 1)
                        
                        for temp in trend_buffer:
                            if temp >= threshold:
                                line += "█"
                            else:
                                line += " "
                        
                        print(f"{threshold:5.1f}°C |{line}|")
                    
                    print("-" * 52)
                    
                    # Trend indicator
                    if len(trend_buffer) >= 3:
                        recent_avg = sum(trend_buffer[-3:]) / 3
                        older_avg = sum(trend_buffer[-6:-3]) / 3 if len(trend_buffer) >= 6 else trend_buffer[0]
                        
                        if recent_avg > older_avg + 0.1:
                            trend = "↑ Rising"
                        elif recent_avg < older_avg - 0.1:
                            trend = "↓ Falling"
                        else:
                            trend = "→ Stable"
                        
                        print(f"Trend: {trend}")
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        adc.cleanup()

def calibrate_thermistor():
    """Calibrate thermistor with known temperature"""
    print("\n=== Thermistor Calibration ===")
    print("Calibrate sensor with known temperature")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    try:
        # Show current reading
        current_temp = thermistor.read_temperature_c()
        if current_temp is None:
            print("Error: Cannot read temperature. Check connections.")
            return
        
        print(f"Current reading: {current_temp:.1f}°C")
        
        # Get known temperature
        known_temp = float(input("Enter actual temperature (°C): "))
        
        # Calibrate
        if thermistor.calibrate(known_temp):
            print(f"Calibration successful! Offset: {thermistor.calibration_offset:.1f}°C")
            
            # Verify
            new_temp = thermistor.read_temperature_c()
            print(f"New reading: {new_temp:.1f}°C")
        else:
            print("Calibration failed!")
    
    except ValueError:
        print("Invalid temperature entered")
    except KeyboardInterrupt:
        pass
    finally:
        adc.cleanup()

def temperature_color_indicator():
    """Temperature indication with RGB LED"""
    print("\n=== Temperature Color Indicator ===")
    print("LED color indicates temperature range")
    print("Blue=Cold, Green=Normal, Red=Hot")
    print("Press Ctrl+C to exit")
    
    adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    thermistor = Thermistor(adc, THERMISTOR_CHANNEL)
    
    # Temperature thresholds
    COLD_THRESHOLD = 20.0
    HOT_THRESHOLD = 30.0
    
    try:
        led = PWMLED(LED_PIN)  # Single LED with brightness
        has_led = True
    except:
        has_led = False
        print("Note: No PWM LED connected")
    
    try:
        while True:
            temp_c = thermistor.read_temperature_c()
            
            if temp_c is not None:
                # Determine color/brightness based on temperature
                if temp_c < COLD_THRESHOLD:
                    color = "BLUE"
                    if has_led:
                        # Pulse slowly for cold
                        led.pulse(fade_in_time=2, fade_out_time=2)
                elif temp_c > HOT_THRESHOLD:
                    color = "RED"
                    if has_led:
                        # Pulse quickly for hot
                        led.pulse(fade_in_time=0.5, fade_out_time=0.5)
                else:
                    color = "GREEN"
                    if has_led:
                        # Steady for normal
                        brightness = (temp_c - COLD_THRESHOLD) / (HOT_THRESHOLD - COLD_THRESHOLD)
                        led.value = brightness
                
                # Display
                bar_pos = int((temp_c - 10) / 30 * 20)  # Scale 10-40°C to 0-20
                bar_pos = max(0, min(20, bar_pos))
                
                if temp_c < COLD_THRESHOLD:
                    bar_char = "▓"
                elif temp_c > HOT_THRESHOLD:
                    bar_char = "█"
                else:
                    bar_char = "▒"
                
                bar = bar_char * bar_pos + "░" * (20 - bar_pos)
                
                print(f"\rTemp: {temp_c:5.1f}°C [{bar}] Color: {color:5s}", end='')
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_led:
            led.close()
        adc.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Thermistor Temperature Sensor")
    print("============================")
    print("ADC Pins:")
    print(f"  CS:  GPIO{ADC_CS}")
    print(f"  CLK: GPIO{ADC_CLK}")
    print(f"  DI:  GPIO{ADC_DI}")
    print(f"  DO:  GPIO{ADC_DO}")
    print(f"\nThermistor on ADC channel {THERMISTOR_CHANNEL}")
    print(f"LED: GPIO{LED_PIN} (optional)")
    print(f"Buzzer: GPIO{BUZZER_PIN} (optional)")
    
    while True:
        print("\n\nSelect Function:")
        print("1. Basic temperature reading")
        print("2. Temperature monitor with stats")
        print("3. Thermostat control simulation")
        print("4. Over-temperature alarm")
        print("5. Temperature data logger")
        print("6. Temperature trend graph")
        print("7. Calibrate thermistor")
        print("8. Temperature color indicator")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_temperature_reading()
        elif choice == '2':
            temperature_monitor()
        elif choice == '3':
            thermostat_control()
        elif choice == '4':
            temperature_alarm()
        elif choice == '5':
            temperature_logger()
        elif choice == '6':
            temperature_trend()
        elif choice == '7':
            calibrate_thermistor()
        elif choice == '8':
            temperature_color_indicator()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()