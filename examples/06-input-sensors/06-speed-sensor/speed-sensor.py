#!/usr/bin/env python3
"""
Speed Sensor - Rotation Speed Measurement
Measure rotation speed using infrared or hall effect sensor
"""

from gpiozero import Button, LED, PWMLED, Buzzer
import time
import signal
import sys
import threading
from collections import deque
import statistics

# GPIO Configuration
SPEED_SENSOR_PIN = 17    # Speed sensor input (IR or Hall effect)
TRIGGER_PIN = 18         # Optional trigger/enable pin

# Optional outputs
LED_PIN = 23            # Activity indicator LED
BUZZER_PIN = 24         # Speed feedback buzzer
PWM_LED_PIN = 25        # PWM LED for speed visualization

# Speed calculation parameters
PULSES_PER_REVOLUTION = 1  # Number of pulses per full rotation (adjust based on setup)

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class SpeedSensor:
    """Speed sensor for measuring rotation speed"""
    
    def __init__(self, sensor_pin=SPEED_SENSOR_PIN, pulses_per_rev=1):
        """
        Initialize speed sensor
        
        Args:
            sensor_pin: GPIO pin for speed sensor
            pulses_per_rev: Number of pulses per revolution
        """
        self.sensor = Button(sensor_pin, pull_up=True, bounce_time=0.001)
        self.pulses_per_rev = pulses_per_rev
        
        # Pulse counting
        self.pulse_count = 0
        self.last_pulse_time = 0
        self.pulse_times = deque(maxlen=10)  # Store last 10 pulse intervals
        
        # Speed calculation
        self.current_speed = 0.0  # RPM
        self.current_frequency = 0.0  # Hz
        self.last_speed_update = time.time()
        
        # Statistics
        self.total_pulses = 0
        self.max_speed = 0.0
        self.start_time = time.time()
        
        # Threading
        self.monitoring_thread = None
        self.monitoring = False
        
        # Callbacks
        self.pulse_callback = None
        self.speed_callback = None
        
        # Setup sensor event
        self.sensor.when_pressed = self._on_pulse
        self.sensor.when_released = self._on_pulse
    
    def _on_pulse(self):
        """Handle sensor pulse"""
        current_time = time.time()
        
        # Update pulse count
        self.pulse_count += 1
        self.total_pulses += 1
        
        # Calculate time since last pulse
        if self.last_pulse_time > 0:
            interval = current_time - self.last_pulse_time
            self.pulse_times.append(interval)
            
            # Calculate instantaneous speed
            if len(self.pulse_times) >= 2:
                avg_interval = statistics.mean(list(self.pulse_times)[-3:])  # Use last 3 pulses
                if avg_interval > 0:
                    # Convert to RPM
                    self.current_frequency = 1.0 / avg_interval
                    self.current_speed = (self.current_frequency / self.pulses_per_rev) * 60.0
                    self.max_speed = max(self.max_speed, self.current_speed)
        
        self.last_pulse_time = current_time
        self.last_speed_update = current_time
        
        # Call pulse callback
        if self.pulse_callback:
            self.pulse_callback(self.pulse_count, self.current_speed)
    
    def get_speed(self):
        """Get current speed in RPM"""
        # Check if speed is stale (no pulses for 2 seconds)
        if time.time() - self.last_speed_update > 2.0:
            self.current_speed = 0.0
            self.current_frequency = 0.0
        
        return self.current_speed
    
    def get_frequency(self):
        """Get current frequency in Hz"""
        if time.time() - self.last_speed_update > 2.0:
            self.current_frequency = 0.0
        
        return self.current_frequency
    
    def get_statistics(self):
        """Get measurement statistics"""
        elapsed_time = time.time() - self.start_time
        
        return {
            'total_pulses': self.total_pulses,
            'max_speed': self.max_speed,
            'current_speed': self.get_speed(),
            'average_speed': (self.total_pulses / self.pulses_per_rev * 60.0) / elapsed_time if elapsed_time > 0 else 0,
            'elapsed_time': elapsed_time,
            'pulse_rate': self.total_pulses / elapsed_time if elapsed_time > 0 else 0
        }
    
    def reset_counters(self):
        """Reset all counters and statistics"""
        self.pulse_count = 0
        self.total_pulses = 0
        self.max_speed = 0.0
        self.start_time = time.time()
        self.pulse_times.clear()
    
    def set_pulses_per_revolution(self, pulses):
        """Set number of pulses per revolution"""
        self.pulses_per_rev = max(1, pulses)
    
    def set_pulse_callback(self, callback):
        """Set callback for pulse events"""
        self.pulse_callback = callback
    
    def set_speed_callback(self, callback):
        """Set callback for speed updates"""
        self.speed_callback = callback
    
    def start_monitoring(self, update_interval=0.1):
        """Start background speed monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_speed, args=(update_interval,))
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitor_speed(self, interval):
        """Background speed monitoring thread"""
        while self.monitoring:
            if self.speed_callback:
                self.speed_callback(self.get_speed())
            time.sleep(interval)
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_monitoring()
        self.sensor.close()

def basic_speed_measurement():
    """Basic speed measurement display"""
    print("\n=== Basic Speed Measurement ===")
    print("Rotate object with sensor to measure speed")
    print("Press Ctrl+C to exit")
    
    speed_sensor = SpeedSensor()
    
    def on_pulse(count, speed):
        print(f"\rPulses: {count:6d} | Speed: {speed:6.1f} RPM | Freq: {speed_sensor.get_frequency():5.1f} Hz", end='')
    
    speed_sensor.set_pulse_callback(on_pulse)
    
    try:
        print("Waiting for rotation...")
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        stats = speed_sensor.get_statistics()
        print(f"\n\n--- Measurement Summary ---")
        print(f"Total pulses: {stats['total_pulses']}")
        print(f"Max speed: {stats['max_speed']:.1f} RPM")
        print(f"Average speed: {stats['average_speed']:.1f} RPM")
        print(f"Measurement time: {stats['elapsed_time']:.1f} seconds")
        print(f"Pulse rate: {stats['pulse_rate']:.1f} pulses/second")
    finally:
        speed_sensor.cleanup()

def visual_tachometer():
    """Visual tachometer with LED and bar display"""
    print("\n=== Visual Tachometer ===")
    print("LED brightness indicates rotation speed")
    print("Press Ctrl+C to exit")
    
    speed_sensor = SpeedSensor()
    
    try:
        activity_led = LED(LED_PIN)
        pwm_led = PWMLED(PWM_LED_PIN)
        has_leds = True
    except:
        has_leds = False
        print("Note: No LEDs connected for visual feedback")
    
    max_display_speed = 1000  # RPM for full scale
    
    def on_pulse(count, speed):
        # Update activity LED
        if has_leds:
            activity_led.on()
            threading.Timer(0.05, activity_led.off).start()
            
            # Update PWM LED brightness based on speed
            brightness = min(speed / max_display_speed, 1.0)
            pwm_led.value = brightness
        
        # Create visual speed bar
        bar_length = 30
        bar_position = int((speed / max_display_speed) * bar_length)
        bar_position = min(bar_position, bar_length)
        
        bar = "█" * bar_position + "░" * (bar_length - bar_position)
        
        print(f"\rSpeed: {speed:6.1f} RPM [{bar}] {speed/max_display_speed*100:5.1f}%", end='')
    
    speed_sensor.set_pulse_callback(on_pulse)
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_leds:
            activity_led.close()
            pwm_led.close()
        speed_sensor.cleanup()

def speed_alarm():
    """Speed monitoring with threshold alarms"""
    print("\n=== Speed Alarm System ===")
    
    # Get alarm thresholds
    try:
        min_speed = float(input("Enter minimum speed alarm (RPM) [100]: ") or "100")
        max_speed = float(input("Enter maximum speed alarm (RPM) [500]: ") or "500")
    except ValueError:
        min_speed, max_speed = 100, 500
    
    print(f"Monitoring speed: {min_speed} - {max_speed} RPM")
    print("Press Ctrl+C to exit")
    
    speed_sensor = SpeedSensor()
    
    try:
        buzzer = Buzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
        print("Note: No buzzer connected for alarms")
    
    alarm_state = "NORMAL"
    alarm_count = 0
    
    def on_pulse(count, speed):
        nonlocal alarm_state, alarm_count
        
        # Check alarm conditions
        new_state = "NORMAL"
        if speed < min_speed and speed > 0:
            new_state = "TOO_SLOW"
        elif speed > max_speed:
            new_state = "TOO_FAST"
        
        # Handle state changes
        if new_state != alarm_state:
            alarm_state = new_state
            
            if alarm_state == "TOO_SLOW":
                alarm_count += 1
                print(f"\n⚠️ ALARM: Speed too slow ({speed:.1f} RPM < {min_speed} RPM)")
                if has_buzzer:
                    buzzer.beep(0.1, 0.1, n=2)
            elif alarm_state == "TOO_FAST":
                alarm_count += 1
                print(f"\n⚠️ ALARM: Speed too fast ({speed:.1f} RPM > {max_speed} RPM)")
                if has_buzzer:
                    buzzer.beep(0.05, 0.05, n=5)
            else:
                print(f"\n✓ Speed normal: {speed:.1f} RPM")
                if has_buzzer:
                    buzzer.off()
        
        # Status display
        status_symbol = "⚠️" if alarm_state != "NORMAL" else "✓"
        print(f"\r{status_symbol} Speed: {speed:6.1f} RPM | Range: {min_speed}-{max_speed} | "
              f"Status: {alarm_state:8s} | Alarms: {alarm_count}", end='')
    
    speed_sensor.set_pulse_callback(on_pulse)
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal alarms triggered: {alarm_count}")
    finally:
        if has_buzzer:
            buzzer.close()
        speed_sensor.cleanup()

def rpm_data_logger():
    """Log speed data to file"""
    print("\n=== RPM Data Logger ===")
    print("Logging speed measurements to file")
    
    from datetime import datetime
    
    # Create log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"speed_log_{timestamp}.csv"
    
    print(f"Logging to: {filename}")
    print("Press Ctrl+C to stop logging")
    
    speed_sensor = SpeedSensor()
    log_count = 0
    
    try:
        with open(filename, 'w') as f:
            # Write CSV header
            f.write("Timestamp,RPM,Frequency_Hz,Pulse_Count,Total_Pulses\\n")
            
            def on_pulse(count, speed):
                nonlocal log_count
                
                # Log every 10th pulse to avoid too much data
                if count % 10 == 0:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                    frequency = speed_sensor.get_frequency()
                    total = speed_sensor.total_pulses
                    
                    f.write(f"{timestamp},{speed:.2f},{frequency:.2f},{count},{total}\\n")
                    f.flush()
                    log_count += 1
                
                print(f"\rSpeed: {speed:6.1f} RPM | Logs: {log_count} | Pulses: {count}", end='')
            
            speed_sensor.set_pulse_callback(on_pulse)
            
            while True:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\nLogging stopped. {log_count} entries saved to {filename}")
    finally:
        speed_sensor.cleanup()

def speed_control_simulation():
    """Simulate speed control system"""
    print("\n=== Speed Control Simulation ===")
    print("Simulate a speed control system with target speed")
    
    # Get target speed
    try:
        target_speed = float(input("Enter target speed (RPM) [300]: ") or "300")
    except ValueError:
        target_speed = 300
    
    print(f"Target speed: {target_speed} RPM")
    print("Control tolerance: ±10 RPM")
    print("Press Ctrl+C to exit")
    
    speed_sensor = SpeedSensor()
    
    try:
        control_led = PWMLED(PWM_LED_PIN)
        has_led = True
    except:
        has_led = False
        print("Note: No control output LED")
    
    # Control parameters
    tolerance = 10  # RPM
    control_output = 0.5  # 0-1 range
    
    def on_pulse(count, speed):
        nonlocal control_output
        
        # Simple proportional control
        error = target_speed - speed
        
        # Calculate control output (simplified)
        if abs(error) < tolerance:
            status = "ON TARGET"
            control_change = 0
        elif error > 0:
            status = "SPEED UP"
            control_change = min(0.01, error / target_speed)
        else:
            status = "SLOW DOWN"
            control_change = -min(0.01, abs(error) / target_speed)
        
        control_output += control_change
        control_output = max(0.0, min(1.0, control_output))
        
        # Update control LED
        if has_led:
            control_led.value = control_output
        
        # Visual control bar
        bar_length = 20
        control_bar_pos = int(control_output * bar_length)
        control_bar = "█" * control_bar_pos + "░" * (bar_length - control_bar_pos)
        
        print(f"\rSpeed: {speed:6.1f} RPM | Target: {target_speed:6.1f} | "
              f"Error: {error:+6.1f} | Control: [{control_bar}] {control_output*100:5.1f}% | {status:9s}", end='')
    
    speed_sensor.set_pulse_callback(on_pulse)
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_led:
            control_led.close()
        speed_sensor.cleanup()

def multi_pulse_calibration():
    """Calibrate pulses per revolution"""
    print("\n=== Pulses Per Revolution Calibration ===")
    print("Determine the number of pulses per revolution")
    print("Manually rotate the object exactly one full revolution")
    print("Press Enter when you start, Enter again when you complete one revolution")
    
    speed_sensor = SpeedSensor()
    
    try:
        input("Press Enter to start counting...")
        start_pulses = speed_sensor.total_pulses
        
        input("Rotate one full revolution, then press Enter...")
        end_pulses = speed_sensor.total_pulses
        
        pulses_per_rev = end_pulses - start_pulses
        
        print(f"\nCalibration Results:")
        print(f"Pulses counted: {pulses_per_rev}")
        print(f"Pulses per revolution: {pulses_per_rev}")
        
        if pulses_per_rev > 0:
            speed_sensor.set_pulses_per_revolution(pulses_per_rev)
            print(f"Sensor configured for {pulses_per_rev} pulses per revolution")
            
            # Test the calibration
            print("\\nTesting calibration (rotate continuously):")
            print("Press Ctrl+C to stop")
            
            def on_pulse(count, speed):
                print(f"\rSpeed: {speed:6.1f} RPM | Pulses/rev: {pulses_per_rev}", end='')
            
            speed_sensor.set_pulse_callback(on_pulse)
            
            while True:
                time.sleep(0.1)
        else:
            print("No pulses detected. Check sensor connection.")
    
    except KeyboardInterrupt:
        pass
    finally:
        speed_sensor.cleanup()

def frequency_analysis():
    """Analyze pulse frequency patterns"""
    print("\n=== Frequency Analysis ===")
    print("Analyze pulse timing and frequency patterns")
    print("Press Ctrl+C to exit")
    
    speed_sensor = SpeedSensor()
    
    # Frequency bins for analysis
    freq_bins = [0, 1, 2, 5, 10, 20, 50, 100]  # Hz boundaries
    freq_counts = [0] * (len(freq_bins) - 1)
    
    def on_pulse(count, speed):
        frequency = speed_sensor.get_frequency()
        
        # Update frequency histogram
        for i in range(len(freq_bins) - 1):
            if freq_bins[i] <= frequency < freq_bins[i + 1]:
                freq_counts[i] += 1
                break
        
        # Display current stats
        pulse_times = list(speed_sensor.pulse_times)
        if len(pulse_times) > 1:
            avg_interval = statistics.mean(pulse_times)
            std_interval = statistics.stdev(pulse_times) if len(pulse_times) > 1 else 0
            min_interval = min(pulse_times)
            max_interval = max(pulse_times)
            
            print(f"\rFreq: {frequency:5.1f} Hz | Interval: {avg_interval*1000:5.1f}±{std_interval*1000:4.1f}ms | "
                  f"Range: {min_interval*1000:4.1f}-{max_interval*1000:4.1f}ms | Pulses: {count}", end='')
    
    speed_sensor.set_pulse_callback(on_pulse)
    
    try:
        while True:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\\n\\n--- Frequency Analysis Results ---")
        print("Frequency Range (Hz) | Count | Percentage")
        print("-" * 40)
        
        total_pulses = sum(freq_counts)
        if total_pulses > 0:
            for i in range(len(freq_counts)):
                percentage = (freq_counts[i] / total_pulses) * 100
                print(f"{freq_bins[i]:3.0f} - {freq_bins[i+1]:3.0f} Hz       | "
                      f"{freq_counts[i]:5d} | {percentage:6.1f}%")
    finally:
        speed_sensor.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Speed Sensor - Rotation Speed Measurement")
    print("========================================")
    print(f"Sensor: GPIO{SPEED_SENSOR_PIN}")
    print(f"Activity LED: GPIO{LED_PIN} (optional)")
    print(f"PWM LED: GPIO{PWM_LED_PIN} (optional)")
    print(f"Buzzer: GPIO{BUZZER_PIN} (optional)")
    
    while True:
        print("\\n\\nSelect Function:")
        print("1. Basic speed measurement")
        print("2. Visual tachometer")
        print("3. Speed alarm system")
        print("4. RPM data logger")
        print("5. Speed control simulation")
        print("6. Calibrate pulses per revolution")
        print("7. Frequency analysis")
        print("8. Exit")
        
        choice = input("\\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_speed_measurement()
        elif choice == '2':
            visual_tachometer()
        elif choice == '3':
            speed_alarm()
        elif choice == '4':
            rpm_data_logger()
        elif choice == '5':
            speed_control_simulation() 
        elif choice == '6':
            multi_pulse_calibration()
        elif choice == '7':
            frequency_analysis()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\\nGoodbye!")

if __name__ == "__main__":
    main()