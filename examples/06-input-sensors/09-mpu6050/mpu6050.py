#!/usr/bin/env python3
"""
MPU6050 6-Axis Accelerometer and Gyroscope
Read acceleration and rotation data from MPU6050 sensor
"""

import time
import signal
import sys
import math
import statistics
from collections import deque

# Import I2C support
try:
    import smbus2 as smbus
    I2C_AVAILABLE = True
except ImportError:
    try:
        import smbus
        I2C_AVAILABLE = True
    except ImportError:
        I2C_AVAILABLE = False

from gpiozero import LED, PWMLED, Buzzer

# MPU6050 I2C Configuration
MPU6050_ADDR = 0x68  # Default I2C address
I2C_BUS = 1          # I2C bus number

# MPU6050 Register Addresses
PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
INT_ENABLE = 0x38

# Data registers
ACCEL_XOUT_H = 0x3B
ACCEL_XOUT_L = 0x3C
ACCEL_YOUT_H = 0x3D
ACCEL_YOUT_L = 0x3E
ACCEL_ZOUT_H = 0x3F
ACCEL_ZOUT_L = 0x40
TEMP_OUT_H = 0x41
TEMP_OUT_L = 0x42
GYRO_XOUT_H = 0x43
GYRO_XOUT_L = 0x44
GYRO_YOUT_H = 0x45
GYRO_YOUT_L = 0x46
GYRO_ZOUT_H = 0x47
GYRO_ZOUT_L = 0x48

# Optional outputs
LED_PIN = 23        # Activity LED
BUZZER_PIN = 24     # Alert buzzer
PWM_LED_PIN = 25    # PWM LED for tilt indication

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class MPU6050:
    """MPU6050 6-axis accelerometer and gyroscope sensor"""
    
    def __init__(self, address=MPU6050_ADDR, bus=I2C_BUS):
        """
        Initialize MPU6050 sensor
        
        Args:
            address: I2C address of the sensor
            bus: I2C bus number
        """
        if not I2C_AVAILABLE:
            raise ImportError("smbus library not available. Install with: pip install smbus2")
        
        self.address = address
        self.bus = smbus.SMBus(bus)
        
        # Sensor scaling factors
        self.accel_scale = 16384.0  # LSB/g for ±2g range
        self.gyro_scale = 131.0     # LSB/°/s for ±250°/s range
        
        # Calibration offsets
        self.accel_offset = {'x': 0, 'y': 0, 'z': 0}
        self.gyro_offset = {'x': 0, 'y': 0, 'z': 0}
        
        # Data history for filtering
        self.accel_history = {'x': deque(maxlen=10), 'y': deque(maxlen=10), 'z': deque(maxlen=10)}
        self.gyro_history = {'x': deque(maxlen=10), 'y': deque(maxlen=10), 'z': deque(maxlen=10)}
        
        # Initialize sensor
        self._initialize()
    
    def _initialize(self):
        """Initialize the MPU6050 sensor"""
        try:
            # Wake up the sensor (default is sleep mode)
            self.bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
            time.sleep(0.1)
            
            # Set sample rate to 100Hz (1kHz / (9+1))
            self.bus.write_byte_data(self.address, SMPLRT_DIV, 0x09)
            
            # Configure accelerometer (±2g)
            self.bus.write_byte_data(self.address, ACCEL_CONFIG, 0x00)
            
            # Configure gyroscope (±250°/s)
            self.bus.write_byte_data(self.address, GYRO_CONFIG, 0x00)
            
            # Set digital low pass filter
            self.bus.write_byte_data(self.address, CONFIG, 0x06)
            
            print("MPU6050 initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            raise
    
    def _read_word(self, reg):
        """Read a 16-bit signed word from two consecutive registers"""
        high = self.bus.read_byte_data(self.address, reg)
        low = self.bus.read_byte_data(self.address, reg + 1)
        
        # Combine high and low bytes
        value = (high << 8) | low
        
        # Convert to signed 16-bit
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        
        return value
    
    def read_accelerometer(self):
        """
        Read accelerometer data
        
        Returns:
            Dictionary with x, y, z acceleration in g's
        """
        try:
            accel_x = self._read_word(ACCEL_XOUT_H) / self.accel_scale
            accel_y = self._read_word(ACCEL_YOUT_H) / self.accel_scale
            accel_z = self._read_word(ACCEL_ZOUT_H) / self.accel_scale
            
            # Apply calibration offsets
            accel_x -= self.accel_offset['x']
            accel_y -= self.accel_offset['y']
            accel_z -= self.accel_offset['z']
            
            return {'x': accel_x, 'y': accel_y, 'z': accel_z}
            
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
            return {'x': 0, 'y': 0, 'z': 0}
    
    def read_gyroscope(self):
        """
        Read gyroscope data
        
        Returns:
            Dictionary with x, y, z rotation in degrees per second
        """
        try:
            gyro_x = self._read_word(GYRO_XOUT_H) / self.gyro_scale
            gyro_y = self._read_word(GYRO_YOUT_H) / self.gyro_scale
            gyro_z = self._read_word(GYRO_ZOUT_H) / self.gyro_scale
            
            # Apply calibration offsets
            gyro_x -= self.gyro_offset['x']
            gyro_y -= self.gyro_offset['y']
            gyro_z -= self.gyro_offset['z']
            
            return {'x': gyro_x, 'y': gyro_y, 'z': gyro_z}
            
        except Exception as e:
            print(f"Error reading gyroscope: {e}")
            return {'x': 0, 'y': 0, 'z': 0}
    
    def read_temperature(self):
        """
        Read temperature from internal sensor
        
        Returns:
            Temperature in Celsius
        """
        try:
            temp_raw = self._read_word(TEMP_OUT_H)
            temperature = (temp_raw / 340.0) + 36.53
            return temperature
            
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return 0
    
    def read_all(self):
        """
        Read all sensor data
        
        Returns:
            Dictionary with accelerometer, gyroscope, and temperature data
        """
        return {
            'accel': self.read_accelerometer(),
            'gyro': self.read_gyroscope(),
            'temp': self.read_temperature()
        }
    
    def get_filtered_data(self):
        """Get filtered sensor data using moving average"""
        # Read raw data
        accel = self.read_accelerometer()
        gyro = self.read_gyroscope()
        
        # Add to history
        for axis in ['x', 'y', 'z']:
            self.accel_history[axis].append(accel[axis])
            self.gyro_history[axis].append(gyro[axis])
        
        # Calculate filtered values
        filtered_accel = {}
        filtered_gyro = {}
        
        for axis in ['x', 'y', 'z']:
            if len(self.accel_history[axis]) > 0:
                filtered_accel[axis] = statistics.mean(self.accel_history[axis])
                filtered_gyro[axis] = statistics.mean(self.gyro_history[axis])
            else:
                filtered_accel[axis] = accel[axis]
                filtered_gyro[axis] = gyro[axis]
        
        return {'accel': filtered_accel, 'gyro': filtered_gyro}
    
    def calculate_angles(self):
        """
        Calculate roll and pitch angles from accelerometer
        
        Returns:
            Dictionary with roll and pitch in degrees
        """
        accel = self.read_accelerometer()
        
        # Calculate angles using accelerometer
        roll = math.atan2(accel['y'], accel['z']) * 180 / math.pi
        pitch = math.atan2(-accel['x'], math.sqrt(accel['y']**2 + accel['z']**2)) * 180 / math.pi
        
        return {'roll': roll, 'pitch': pitch}
    
    def calculate_magnitude(self):
        """
        Calculate acceleration magnitude (total acceleration)
        
        Returns:
            Total acceleration magnitude in g's
        """
        accel = self.read_accelerometer()
        magnitude = math.sqrt(accel['x']**2 + accel['y']**2 + accel['z']**2)
        return magnitude
    
    def calibrate(self, samples=100):
        """
        Calibrate sensor by measuring offsets when stationary
        
        Args:
            samples: Number of samples to average for calibration
        """
        print(f"\nCalibrating MPU6050 with {samples} samples...")
        print("Keep the sensor stationary and level during calibration")
        
        # Collect calibration data
        accel_sum = {'x': 0, 'y': 0, 'z': 0}
        gyro_sum = {'x': 0, 'y': 0, 'z': 0}
        
        for i in range(samples):
            accel = self.read_accelerometer()
            gyro = self.read_gyroscope()
            
            for axis in ['x', 'y', 'z']:
                accel_sum[axis] += accel[axis]
                gyro_sum[axis] += gyro[axis]
            
            print(f"\rProgress: {i+1}/{samples}", end='')
            time.sleep(0.01)
        
        # Calculate offsets
        for axis in ['x', 'y', 'z']:
            self.accel_offset[axis] = accel_sum[axis] / samples
            self.gyro_offset[axis] = gyro_sum[axis] / samples
        
        # For accelerometer, Z should read ~1g when level
        self.accel_offset['z'] -= 1.0
        
        print(f"\n\nCalibration complete:")
        print(f"Accel offsets: X={self.accel_offset['x']:.3f}, Y={self.accel_offset['y']:.3f}, Z={self.accel_offset['z']:.3f}")
        print(f"Gyro offsets:  X={self.gyro_offset['x']:.3f}, Y={self.gyro_offset['y']:.3f}, Z={self.gyro_offset['z']:.3f}")
    
    def detect_motion(self, threshold=0.1):
        """
        Detect motion based on acceleration changes
        
        Args:
            threshold: Motion detection threshold in g's
            
        Returns:
            True if motion detected
        """
        magnitude = self.calculate_magnitude()
        # Motion if acceleration deviates significantly from 1g (gravity)
        return abs(magnitude - 1.0) > threshold
    
    def detect_tap(self, threshold=2.0):
        """
        Detect tap/shock based on sudden acceleration
        
        Args:
            threshold: Tap detection threshold in g's
            
        Returns:
            True if tap detected
        """
        magnitude = self.calculate_magnitude()
        return magnitude > threshold
    
    def cleanup(self):
        """Clean up I2C resources"""
        if hasattr(self, 'bus'):
            self.bus.close()

def basic_sensor_reading():
    """Basic sensor data reading"""
    print("\n=== Basic MPU6050 Reading ===")
    print("Displaying accelerometer and gyroscope data")
    print("Press Ctrl+C to exit")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        print("Install with: pip install smbus2")
        return
    
    try:
        mpu = MPU6050()
    except Exception as e:
        print(f"Failed to initialize MPU6050: {e}")
        print("Check I2C connections and address")
        return
    
    try:
        while True:
            data = mpu.read_all()
            angles = mpu.calculate_angles()
            magnitude = mpu.calculate_magnitude()
            
            print(f"\rAccel: X={data['accel']['x']:6.2f} Y={data['accel']['y']:6.2f} Z={data['accel']['z']:6.2f} g | "
                  f"Gyro: X={data['gyro']['x']:6.1f} Y={data['gyro']['y']:6.1f} Z={data['gyro']['z']:6.1f} °/s | "
                  f"Roll={angles['roll']:5.1f}° Pitch={angles['pitch']:5.1f}° | "
                  f"Mag={magnitude:.2f}g | Temp={data['temp']:.1f}°C", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        mpu.cleanup()

def tilt_indicator():
    """Visual tilt indication with LEDs"""
    print("\n=== Tilt Indicator ===")
    print("LED indicates tilt angle")
    print("Press Ctrl+C to exit")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        return
    
    try:
        mpu = MPU6050()
        pwm_led = PWMLED(PWM_LED_PIN)
        has_led = True
    except Exception as e:
        print(f"Setup error: {e}")
        has_led = False
    
    try:
        while True:
            angles = mpu.calculate_angles()
            
            # Calculate total tilt (0° = level, 90° = vertical)
            total_tilt = math.sqrt(angles['roll']**2 + angles['pitch']**2)
            
            # Update LED brightness based on tilt
            if has_led:
                brightness = min(total_tilt / 45.0, 1.0)  # Full brightness at 45°
                pwm_led.value = brightness
            
            # Visual tilt display
            tilt_bar_length = 20
            tilt_bar_pos = int(min(total_tilt / 90.0, 1.0) * tilt_bar_length)
            tilt_bar = "█" * tilt_bar_pos + "░" * (tilt_bar_length - tilt_bar_pos)
            
            print(f"\rRoll: {angles['roll']:6.1f}° | Pitch: {angles['pitch']:6.1f}° | "
                  f"Total: {total_tilt:5.1f}° [{tilt_bar}]", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_led:
            pwm_led.close()
        mpu.cleanup()

def motion_detector():
    """Motion detection system"""
    print("\n=== Motion Detector ===")
    print("Detecting motion and orientation changes")
    print("Press Ctrl+C to exit")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        return
    
    try:
        mpu = MPU6050()
        activity_led = LED(LED_PIN)
        buzzer = Buzzer(BUZZER_PIN)
        has_outputs = True
    except Exception as e:
        print(f"Setup error: {e}")
        has_outputs = False
    
    motion_count = 0
    tap_count = 0
    
    try:
        while True:
            # Check for motion
            if mpu.detect_motion(threshold=0.15):
                motion_count += 1
                if has_outputs:
                    activity_led.on()
                    # Brief beep for motion
                    buzzer.beep(0.05, 0.05, n=1, background=True)
                print(f"\n🏃 Motion detected! Count: {motion_count}")
            else:
                if has_outputs:
                    activity_led.off()
            
            # Check for taps
            if mpu.detect_tap(threshold=1.8):
                tap_count += 1
                if has_outputs:
                    # Double beep for tap
                    buzzer.beep(0.1, 0.1, n=2, background=True)
                print(f"\n👆 Tap detected! Count: {tap_count}")
            
            # Display current status
            magnitude = mpu.calculate_magnitude()
            angles = mpu.calculate_angles()
            
            status = "MOTION" if mpu.detect_motion(0.15) else "STILL"
            
            print(f"\rStatus: {status:6s} | Magnitude: {magnitude:.2f}g | "
                  f"Roll: {angles['roll']:5.1f}° | Pitch: {angles['pitch']:5.1f}° | "
                  f"Motion: {motion_count} | Taps: {tap_count}", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nFinal counts - Motion: {motion_count}, Taps: {tap_count}")
    finally:
        if has_outputs:
            activity_led.close()
            buzzer.close()
        mpu.cleanup()

def orientation_monitor():
    """Monitor device orientation"""
    print("\n=== Orientation Monitor ===")
    print("Monitor device orientation and position")
    print("Press Ctrl+C to exit")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        return
    
    try:
        mpu = MPU6050()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    def get_orientation(roll, pitch):
        """Determine device orientation"""
        if abs(roll) < 30 and abs(pitch) < 30:
            return "FLAT"
        elif abs(roll) > 60:
            return "TILTED_SIDE"
        elif pitch > 45:
            return "TILTED_FORWARD"
        elif pitch < -45:
            return "TILTED_BACKWARD"
        else:
            return "ANGLED"
    
    orientation_history = deque(maxlen=10)
    
    try:
        while True:
            angles = mpu.calculate_angles()
            orientation = get_orientation(angles['roll'], angles['pitch'])
            orientation_history.append(orientation)
            
            # Stable orientation (same for last 5 readings)
            if len(orientation_history) >= 5 and all(o == orientation for o in list(orientation_history)[-5:]):
                stable = "✓"
            else:
                stable = "~"
            
            # ASCII art orientation display
            print("\033[2J\033[H", end='')  # Clear screen
            print("Device Orientation Monitor")
            print("=" * 30)
            print()
            
            # Simple device representation
            if orientation == "FLAT":
                print("    ┌─────┐")
                print("    │  •  │")
                print("    └─────┘")
            elif orientation == "TILTED_SIDE":
                if angles['roll'] > 0:
                    print("       ┌─┐")
                    print("      ╱ • │")
                    print("     ╱   │")
                    print("    └────┘")
                else:
                    print("    ┌─┐")
                    print("    │ • ╲")
                    print("    │   ╲")
                    print("    └────╲")
            elif orientation == "TILTED_FORWARD":
                print("    ┌─────┐")
                print("   ╱   •   ╲")
                print("  ╱         ╲")
                print(" └───────────┘")
            elif orientation == "TILTED_BACKWARD":
                print(" ┌───────────┐")
                print("  ╲         ╱")
                print("   ╲   •   ╱")
                print("    └─────┘")
            else:
                print("    ┌─────┐")
                print("    │ • / │")
                print("    └─────┘")
            
            print()
            print(f"Roll:        {angles['roll']:6.1f}°")
            print(f"Pitch:       {angles['pitch']:6.1f}°")
            print(f"Orientation: {orientation}")
            print(f"Stable:      {stable}")
            
            time.sleep(0.2)
    
    except KeyboardInterrupt:
        pass
    finally:
        mpu.cleanup()

def data_logger():
    """Log sensor data to file"""
    print("\n=== MPU6050 Data Logger ===")
    print("Logging accelerometer and gyroscope data")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        return
    
    from datetime import datetime
    
    # Create log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mpu6050_log_{timestamp}.csv"
    
    print(f"Logging to: {filename}")
    print("Press Ctrl+C to stop logging")
    
    try:
        mpu = MPU6050()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    sample_count = 0
    
    try:
        with open(filename, 'w') as f:
            # Write CSV header
            f.write("Timestamp,Accel_X,Accel_Y,Accel_Z,Gyro_X,Gyro_Y,Gyro_Z,Roll,Pitch,Temperature\\n")
            
            while True:
                data = mpu.read_all()
                angles = mpu.calculate_angles()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # Write to file
                f.write(f"{timestamp},"
                       f"{data['accel']['x']:.3f},{data['accel']['y']:.3f},{data['accel']['z']:.3f},"
                       f"{data['gyro']['x']:.2f},{data['gyro']['y']:.2f},{data['gyro']['z']:.2f},"
                       f"{angles['roll']:.2f},{angles['pitch']:.2f},"
                       f"{data['temp']:.1f}\\n")
                f.flush()
                
                sample_count += 1
                
                print(f"\rSamples logged: {sample_count} | "
                      f"Accel: {data['accel']['x']:5.2f},{data['accel']['y']:5.2f},{data['accel']['z']:5.2f} | "
                      f"Gyro: {data['gyro']['x']:5.1f},{data['gyro']['y']:5.1f},{data['gyro']['z']:5.1f}", end='')
                
                time.sleep(0.1)  # 10 Hz logging
    
    except KeyboardInterrupt:
        print(f"\n\nLogging stopped. {sample_count} samples saved to {filename}")
    finally:
        mpu.cleanup()

def calibration_wizard():
    """Interactive calibration process"""
    print("\n=== MPU6050 Calibration Wizard ===")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        return
    
    try:
        mpu = MPU6050()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    try:
        print("This will calibrate the MPU6050 sensor offsets.")
        print("Place the sensor on a flat, stable surface.")
        input("Press Enter when ready...")
        
        # Perform calibration
        mpu.calibrate(samples=200)
        
        print("\nTesting calibration...")
        print("The readings should be close to:")
        print("Accelerometer: X≈0, Y≈0, Z≈1 (gravity)")
        print("Gyroscope: X≈0, Y≈0, Z≈0")
        print("Roll and Pitch should be near 0°")
        print()
        
        # Test for 10 seconds
        for i in range(50):
            data = mpu.read_all()
            angles = mpu.calculate_angles()
            
            print(f"Test {i+1:2d}/50: "
                  f"Accel({data['accel']['x']:5.2f},{data['accel']['y']:5.2f},{data['accel']['z']:5.2f}) "
                  f"Gyro({data['gyro']['x']:5.1f},{data['gyro']['y']:5.1f},{data['gyro']['z']:5.1f}) "
                  f"Angles({angles['roll']:5.1f}°, {angles['pitch']:5.1f}°)")
            
            time.sleep(0.2)
        
        print("\nCalibration test complete!")
        
    except KeyboardInterrupt:
        pass
    finally:
        mpu.cleanup()

def gesture_recognition():
    """Simple gesture recognition"""
    print("\n=== Gesture Recognition ===")
    print("Perform gestures with the sensor:")
    print("- Shake: Rapid back-and-forth motion")
    print("- Rotate: Circular motion")
    print("- Flip: 180° rotation")
    print("Press Ctrl+C to exit")
    
    if not I2C_AVAILABLE:
        print("Error: I2C library not available")
        return
    
    try:
        mpu = MPU6050()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return
    
    # Gesture detection parameters
    shake_history = deque(maxlen=20)
    rotation_history = deque(maxlen=30)
    
    gesture_count = {'shake': 0, 'rotate': 0, 'flip': 0}
    
    try:
        while True:
            data = mpu.read_all()
            angles = mpu.calculate_angles()
            magnitude = mpu.calculate_magnitude()
            
            # Add to history
            shake_history.append(magnitude)
            rotation_history.append(angles['roll'])
            
            detected_gesture = None
            
            # Shake detection (high frequency magnitude changes)
            if len(shake_history) >= 10:
                shake_variance = statistics.variance(list(shake_history)[-10:])
                if shake_variance > 0.5:  # Threshold for shake detection
                    detected_gesture = "SHAKE"
                    gesture_count['shake'] += 1
                    shake_history.clear()  # Reset to avoid multiple detections
            
            # Rotation detection (consistent angular velocity)
            if len(rotation_history) >= 20:
                roll_changes = [abs(rotation_history[i] - rotation_history[i-1]) 
                               for i in range(1, len(rotation_history))]
                if all(change > 2 for change in roll_changes[-10:]):
                    detected_gesture = "ROTATE"
                    gesture_count['rotate'] += 1
                    rotation_history.clear()
            
            # Flip detection (large angle change in short time)
            if len(rotation_history) >= 2:
                angle_change = abs(rotation_history[-1] - rotation_history[0])
                if angle_change > 120:  # Nearly 180° change
                    detected_gesture = "FLIP"
                    gesture_count['flip'] += 1
                    rotation_history.clear()
            
            if detected_gesture:
                print(f"\n🎭 {detected_gesture} detected!")
            
            # Display current status
            print(f"\rMagnitude: {magnitude:.2f}g | "
                  f"Roll: {angles['roll']:5.1f}° | "
                  f"Gestures - Shake: {gesture_count['shake']} "
                  f"Rotate: {gesture_count['rotate']} "
                  f"Flip: {gesture_count['flip']}", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nGesture Summary:")
        for gesture, count in gesture_count.items():
            print(f"{gesture.title()}: {count}")
    finally:
        mpu.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("MPU6050 6-Axis Accelerometer and Gyroscope")
    print("==========================================")
    print(f"I2C Address: 0x{MPU6050_ADDR:02X}")
    print(f"I2C Bus: {I2C_BUS}")
    
    if not I2C_AVAILABLE:
        print("\n⚠️ Warning: I2C library not available")
        print("Install with: pip install smbus2")
        print("Or: sudo apt-get install python3-smbus")
        return
    
    while True:
        print("\n\nSelect Function:")
        print("1. Basic sensor reading")
        print("2. Tilt indicator")
        print("3. Motion detector")
        print("4. Orientation monitor")
        print("5. Data logger")
        print("6. Calibration wizard")
        print("7. Gesture recognition")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_sensor_reading()
        elif choice == '2':
            tilt_indicator()
        elif choice == '3':
            motion_detector()
        elif choice == '4':
            orientation_monitor()
        elif choice == '5':
            data_logger()
        elif choice == '6':
            calibration_wizard()
        elif choice == '7':
            gesture_recognition()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()