# MPU6050 6-Axis Accelerometer and Gyroscope

Read 3-axis acceleration and rotation data from the MPU6050 sensor using I2C communication.

## What You'll Learn
- I2C communication protocol
- 3-axis accelerometer and gyroscope principles
- Sensor calibration and offset correction
- Motion detection and gesture recognition
- Orientation calculation (roll, pitch)
- Digital signal filtering techniques
- Interrupt-driven sensor reading

## Hardware Requirements
- Raspberry Pi 5
- MPU6050 6-axis sensor module
- Optional: LEDs for visual feedback
- Optional: Buzzer for motion alerts
- Jumper wires

## Circuit Diagram

```
MPU6050 Module:
┌─────────────────────────┐
│       MPU6050           │
│   ┌─────────────────┐   │  6-axis sensor
│   │ Accelerometer   │   │  (3-axis accel +
│   │ Gyroscope       │   │   3-axis gyro)
│   │ Temperature     │   │
│   └─────────────────┘   │
├─────────────────────────┤
│VCC GND SCL SDA XDA XCL │
└─┬───┬───┬───┬───┬───┬──┘
  │   │   │   │   │   │
  │   │   │   │   │   └── Not used
  │   │   │   │   └────── Not used  
  │   │   │   └────────── GPIO3 (SDA - I2C Data)
  │   │   └────────────── GPIO5 (SCL - I2C Clock)
  │   └────────────────── GND
  └────────────────────── 3.3V

Note: I2C address is typically 0x68
Enable I2C: sudo raspi-config → Interface Options → I2C

Optional Indicators:
Activity LED:   GPIO23 → 220Ω → LED → GND
PWM LED:        GPIO25 → 220Ω → LED → GND
Buzzer:         GPIO24 → Buzzer → GND
```

## Software Dependencies

Install required libraries:
```bash
# I2C library
pip install smbus2
# Alternative: sudo apt-get install python3-smbus

# GPIO library
pip install gpiozero

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/06-input-sensors/09-mpu6050
python mpu6050.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test basic sensor reading
make motion   # Run motion detector
make tilt     # Run tilt indicator
make install  # Install dependencies
```

## Code Walkthrough

### I2C Communication
Initialize and communicate with the MPU6050:
```python
def _initialize(self):
    # Wake up sensor (default is sleep mode)
    self.bus.write_byte_data(self.address, PWR_MGMT_1, 0x00)
    
    # Set sample rate to 100Hz
    self.bus.write_byte_data(self.address, SMPLRT_DIV, 0x09)
    
    # Configure accelerometer (±2g range)
    self.bus.write_byte_data(self.address, ACCEL_CONFIG, 0x00)
```

### Reading Sensor Data
Convert raw 16-bit values to meaningful units:
```python
def read_accelerometer(self):
    accel_x = self._read_word(ACCEL_XOUT_H) / self.accel_scale
    accel_y = self._read_word(ACCEL_YOUT_H) / self.accel_scale  
    accel_z = self._read_word(ACCEL_ZOUT_H) / self.accel_scale
    
    # Apply calibration offsets
    accel_x -= self.accel_offset['x']
    
    return {'x': accel_x, 'y': accel_y, 'z': accel_z}
```

### Angle Calculation
Calculate roll and pitch from accelerometer data:
```python
def calculate_angles(self):
    accel = self.read_accelerometer()
    
    # Calculate angles using accelerometer
    roll = math.atan2(accel['y'], accel['z']) * 180 / math.pi
    pitch = math.atan2(-accel['x'], 
                      math.sqrt(accel['y']**2 + accel['z']**2)) * 180 / math.pi
    
    return {'roll': roll, 'pitch': pitch}
```

### Motion Detection
Detect movement based on acceleration changes:
```python
def detect_motion(self, threshold=0.1):
    magnitude = self.calculate_magnitude()
    # Motion if acceleration deviates from 1g (gravity)
    return abs(magnitude - 1.0) > threshold
```

## Key Concepts

### Accelerometer Principles
- **3-axis measurement**: X, Y, Z acceleration in g-force units
- **Gravity sensing**: Always reads ~1g total when stationary
- **Motion detection**: Changes in acceleration indicate movement
- **Tilt sensing**: Gravity components reveal orientation

### Gyroscope Principles
- **Angular velocity**: Rotation rate in degrees per second
- **3-axis rotation**: Roll, pitch, yaw measurements
- **Integration**: Can calculate angle changes over time
- **Drift**: Tends to accumulate errors over time

### Sensor Fusion
- **Complementary filter**: Combine accelerometer and gyroscope
- **Kalman filter**: Advanced sensor fusion technique
- **Madgwick filter**: Efficient orientation estimation
- **Dead reckoning**: Track position using acceleration integration

## Register Map

### Power Management
- `PWR_MGMT_1` (0x6B): Power management and clock settings
- `PWR_MGMT_2` (0x6C): Accelerometer and gyroscope power control

### Configuration
- `SMPLRT_DIV` (0x19): Sample rate divider
- `CONFIG` (0x1A): Digital low pass filter configuration
- `GYRO_CONFIG` (0x1B): Gyroscope range selection
- `ACCEL_CONFIG` (0x1C): Accelerometer range selection

### Data Registers
- `ACCEL_XOUT_H/L` (0x3B-0x40): Accelerometer data
- `TEMP_OUT_H/L` (0x41-0x42): Temperature data
- `GYRO_XOUT_H/L` (0x43-0x48): Gyroscope data

## Available Demos

1. **Basic Sensor Reading**: Real-time data display
2. **Tilt Indicator**: Visual tilt angle with LEDs
3. **Motion Detector**: Movement and tap detection
4. **Orientation Monitor**: Device position tracking
5. **Data Logger**: CSV logging of sensor data
6. **Calibration Wizard**: Interactive offset calibration
7. **Gesture Recognition**: Simple gesture detection

## Troubleshooting

### Sensor not detected
- Check I2C connections (SDA=GPIO3, SCL=GPIO5)
- Verify I2C is enabled: `sudo i2cdetect -y 1`
- Should show device at address 0x68
- Check 3.3V power supply

### Erratic readings
- Calibrate sensor when stationary and level
- Check for electromagnetic interference
- Ensure stable power supply
- Add filtering to smooth data

### Wrong orientation
- Check sensor mounting orientation
- Verify axis assignments (X, Y, Z)
- Calibrate with known orientations
- Account for sensor coordinate system

### I2C errors
- Check pull-up resistors on SDA/SCL
- Verify I2C bus speed settings
- Ensure only one device per address
- Check cable length (keep short)

## Advanced Usage

### Sensor Fusion
Combine accelerometer and gyroscope for better accuracy:
```python
def complementary_filter(self, accel_angle, gyro_rate, dt, alpha=0.98):
    # Complementary filter
    angle = alpha * (self.previous_angle + gyro_rate * dt) + (1 - alpha) * accel_angle
    self.previous_angle = angle
    return angle
```

### Quaternion Math
Use quaternions for 3D orientation:
```python
def update_quaternion(self, gx, gy, gz, dt):
    # Quaternion integration
    self.q0 += 0.5 * (-self.q1*gx - self.q2*gy - self.q3*gz) * dt
    self.q1 += 0.5 * (self.q0*gx + self.q2*gz - self.q3*gy) * dt
    self.q2 += 0.5 * (self.q0*gy - self.q1*gz + self.q3*gx) * dt
    self.q3 += 0.5 * (self.q0*gz + self.q1*gy - self.q2*gx) * dt
```

### Interrupt Configuration
Use hardware interrupts for efficient data collection:
```python
def setup_interrupts(self):
    # Configure motion detection interrupt
    self.bus.write_byte_data(self.address, INT_ENABLE, 0x40)
    # Set motion threshold
    self.bus.write_byte_data(self.address, 0x1F, 0x20)  # Motion threshold
```

### Multiple Sensors
Handle multiple MPU6050 sensors:
```python
# Different I2C addresses using AD0 pin
sensor1 = MPU6050(address=0x68)  # AD0 = LOW
sensor2 = MPU6050(address=0x69)  # AD0 = HIGH

# Or use I2C multiplexer for more sensors
```

## Calibration Process

### Static Calibration
1. Place sensor on flat, stable surface
2. Run calibration routine to measure offsets
3. Store offsets for future use
4. Test calibration accuracy

### Dynamic Calibration
1. Rotate sensor through all orientations
2. Collect magnetometer data (if available)
3. Calculate ellipsoid fit parameters
4. Apply correction matrix

## Performance Optimization

### Sample Rate Selection
- Higher rates: Better resolution, more CPU usage
- Lower rates: Less noise, reduced power consumption
- Typical rates: 10-1000 Hz depending on application

### Filtering Strategies
- Moving average: Simple noise reduction
- Low-pass filter: Remove high-frequency noise
- Complementary filter: Combine sensor data
- Kalman filter: Optimal estimation

## Applications

### Motion Sensing
- Step counters and fitness trackers
- Fall detection systems
- Vehicle motion monitoring
- Gaming controllers

### Orientation Tracking
- Camera stabilization
- Virtual reality headsets
- Drone flight controllers
- Robotic navigation

### Vibration Analysis
- Machine health monitoring
- Structural analysis
- Quality control systems
- Predictive maintenance

## Next Steps
- Implement advanced sensor fusion algorithms
- Create a complete IMU (Inertial Measurement Unit)
- Add magnetometer for full 9-axis sensing
- Develop machine learning gesture recognition
- Build orientation-based user interfaces