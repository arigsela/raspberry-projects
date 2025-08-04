# Advanced Camera Control System

Control a pan-tilt camera system using joystick input, servo motors, and the Raspberry Pi camera module with multiple control modes and recording capabilities.

## What You'll Learn
- Pan-tilt servo motor control
- Analog joystick reading with ADC
- Camera module programming
- Multi-mode control systems
- Preset position management
- Automatic patrol sequences
- Motion tracking simulation
- Real-time video recording

## Hardware Requirements
- Raspberry Pi 5 with camera connector
- Raspberry Pi Camera Module (v1, v2, v3, or HQ Camera)
- 2x Servo motors (SG90 or similar) for pan/tilt
- Analog joystick module
- ADC0834 analog-to-digital converter
- 3x Push buttons for control
- 2x LEDs for status indication
- Buzzer for audio feedback
- Jumper wires
- Breadboard
- Pan-tilt camera mount (optional)

## Circuit Diagram

```
Advanced Camera Control System:
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 5                          │
│                                                             │
│ Camera Connector ── Camera Module                          │
│                                                             │
│ GPIO17 ── ADC CS    │ GPIO20 ── Pan Servo (Signal)         │
│ GPIO18 ── ADC CLK   │ GPIO21 ── Tilt Servo (Signal)        │
│ GPIO27 ── ADC DI    │                                       │
│ GPIO22 ── ADC DO    │ GPIO23 ── Record Button              │
│                     │ GPIO24 ── Mode Button                 │
│ 5V ────── Servo VCC │ GPIO25 ── Preset Button              │
│ GND ───── Servo GND │                                       │
│                     │ GPIO26 ── Status LED (+220Ω)         │
│                     │ GPIO19 ── Record LED (+220Ω)         │
│                     │ GPIO13 ── Buzzer                      │
└─────────────────────────────────────────────────────────────┘

ADC0834 (SPI Interface):
┌──────────────┐        ┌─────────────────┐
│     Pi       │        │     ADC0834     │
├──────────────┤        ├─────────────────┤
│ GPIO17 (CS)  ├────────┤ CS (Pin 1)      │
│ GPIO18 (CLK) ├────────┤ CLK (Pin 7)     │
│ GPIO27 (DI)  ├────────┤ DI (Pin 6)      │
│ GPIO22 (DO)  ├────────┤ DO (Pin 5)      │
│ 5V           ├────────┤ VCC (Pin 8)     │
│ GND          ├────────┤ GND (Pin 4)     │
└──────────────┘        └─────────────────┘
                               │       │
                        CH0 ──┘       └── CH1
                         │               │
                    Joystick X      Joystick Y

Joystick Connection:
┌─────────────────┐
│    Joystick     │
├─────────────────┤
│ VCC ── 5V       │
│ GND ── GND      │
│ VRX ── ADC CH0  │  (X-axis)
│ VRY ── ADC CH1  │  (Y-axis)
│ SW  ── GPIO     │  (optional button)
└─────────────────┘

Servo Motors:
Pan Servo (GPIO20):   Red=5V, Brown=GND, Orange=Signal
Tilt Servo (GPIO21):  Red=5V, Brown=GND, Orange=Signal

Note: Ensure adequate power supply (3A+) for servos
```

## Software Dependencies

Install required libraries:
```bash
# Camera library for Pi 5
pip install picamera2

# GPIO and servo control
pip install gpiozero

# ADC and SPI support
pip install spidev

# Enable camera and SPI interfaces
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Navigate to: Interface Options → SPI → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/01-camera
python advanced-camera-control.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test hardware components
make demo     # Run automatic demo
make manual   # Manual control mode
make setup    # Install dependencies
```

## Code Walkthrough

### Camera and Servo Initialization
Set up all hardware components:
```python
def __init__(self):
    # Initialize ADC for joystick
    self.adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
    
    # Initialize servos
    self.pan_servo = Servo(PAN_SERVO_PIN)
    self.tilt_servo = Servo(TILT_SERVO_PIN)
    
    # Initialize camera
    if CAMERA_AVAILABLE:
        self.camera = Picamera2()
        self._configure_camera()
```

### Joystick Reading
Read analog joystick position with deadzone:
```python
def read_joystick(self):
    x_raw = self.adc.read_channel(JOYSTICK_X_CHANNEL)
    y_raw = self.adc.read_channel(JOYSTICK_Y_CHANNEL)
    
    # Convert to -1.0 to 1.0 range
    x = (x_raw - 127) / 127.0
    y = (y_raw - 127) / 127.0
    
    # Apply deadzone
    if abs(x) < self.joystick_deadzone:
        x = 0.0
    if abs(y) < self.joystick_deadzone:
        y = 0.0
    
    return x, y
```

### Smooth Servo Movement
Update servo positions with smoothing:
```python
def update_servo_positions(self, pan_delta, tilt_delta):
    # Calculate new positions with smoothing
    new_pan = self.pan_position + pan_delta * self.movement_smoothing
    new_tilt = self.tilt_position + tilt_delta * self.movement_smoothing
    
    # Clamp to servo limits
    new_pan = max(-1.0, min(1.0, new_pan))
    new_tilt = max(-1.0, min(1.0, new_tilt))
    
    # Apply to servos
    self.pan_servo.value = new_pan
    self.tilt_servo.value = new_tilt
```

### Preset Position System
Save and recall camera positions:
```python
def save_preset(self):
    preset_data = {
        'name': f"preset_{len(self.presets) + 1}",
        'pan': self.pan_position,
        'tilt': self.tilt_position,
        'timestamp': datetime.now().isoformat()
    }
    self.presets.append(preset_data)
    self.save_presets()

def recall_preset(self, index):
    if 0 <= index < len(self.presets):
        preset = self.presets[index]
        self.move_to_position(preset['pan'], preset['tilt'])
```

### Patrol Mode
Automatic camera patrol sequence:
```python
def _patrol_sequence(self):
    while self.patrol_active:
        for i, (pan, tilt) in enumerate(self.patrol_positions):
            if not self.patrol_active:
                break
            
            print(f"Moving to patrol position {i+1}/4")
            self.move_to_position(pan, tilt, speed=0.03)
            time.sleep(3)  # Hold position
```

## Control Modes

### 1. Manual Mode
Direct joystick control of camera position:
- Move joystick to pan and tilt camera
- Real-time servo response
- Smooth movement with deadzone

### 2. Preset Mode
Save and recall specific camera positions:
- Save current position as preset
- Cycle through saved presets
- Fine-tune positions with joystick

### 3. Auto-Track Mode
Simulated automatic tracking:
- Gentle movement toward center
- Basis for computer vision integration
- Continuous position adjustment

### 4. Patrol Mode
Automatic patrol sequence:
- Pre-defined patrol positions
- Automatic movement between points
- Configurable hold times

## Available Demos

1. **Interactive Control**: Full manual operation
2. **Automatic Demo**: Showcase all features
3. **Manual Positioning**: Test servo movements
4. **Preset System**: Save/recall demonstration
5. **Patrol Sequence**: Automatic patrol demo
6. **Recording Demo**: Video capture while moving

## Troubleshooting

### Servos not responding
- Check 5V power supply (adequate amperage)
- Verify servo signal wire connections
- Test individual servo movement
- Check for loose connections

### Joystick reading errors
- Verify ADC connections (SPI)
- Check SPI is enabled: `sudo raspi-config`
- Test ADC with multimeter
- Calibrate joystick center position

### Camera issues
- Check camera cable connection
- Ensure camera is enabled in raspi-config
- Test with: `libcamera-hello --preview`
- Verify adequate power supply

### Recording problems
- Check available disk space
- Monitor CPU usage during recording
- Verify write permissions
- Test camera independently

## Advanced Usage

### Custom Control Sensitivity
Adjust joystick response and servo speed:
```python
# In CameraController.__init__()
self.joystick_sensitivity = 1.5  # Increase sensitivity
self.movement_smoothing = 0.05   # Smoother movement
self.joystick_deadzone = 0.15    # Larger deadzone
```

### Extended Patrol Patterns
Create custom patrol sequences:
```python
# Define custom patrol positions
custom_patrol = [
    (-1.0, 0.5),   # Far left, up
    (-0.5, 0.0),   # Mid left, center
    (0.0, -0.5),   # Center, down
    (0.5, 0.0),    # Mid right, center
    (1.0, 0.5),    # Far right, up
]
controller.patrol_positions = custom_patrol
```

### Computer Vision Integration
Add real object tracking:
```python
import cv2

def start_object_tracking(self):
    # Initialize object tracker
    tracker = cv2.TrackerKCF_create()
    
    # Get camera frame
    frame = self.camera.capture_array()
    
    # Define tracking region
    bbox = cv2.selectROI(frame, False)
    tracker.init(frame, bbox)
    
    # Track and adjust camera position
    while True:
        frame = self.camera.capture_array()
        success, bbox = tracker.update(frame)
        
        if success:
            # Calculate object position relative to center
            center_x = bbox[0] + bbox[2] / 2
            center_y = bbox[1] + bbox[3] / 2
            
            # Adjust camera to center object
            self.track_to_position(center_x, center_y)
```

### Remote Control Integration
Web-based camera control:
```python
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
controller = CameraController()

@app.route('/move')
def move_camera():
    pan = float(request.args.get('pan', 0))
    tilt = float(request.args.get('tilt', 0))
    controller.move_to_position(pan, tilt)
    return jsonify({'status': 'moved'})

@app.route('/preset/<int:preset_id>')
def recall_preset(preset_id):
    controller.recall_preset(preset_id)
    return jsonify({'status': 'preset_recalled'})
```

### Multi-Camera System
Control multiple cameras:
```python
class MultiCameraController:
    def __init__(self, camera_count=2):
        self.cameras = []
        for i in range(camera_count):
            camera = CameraController()
            camera.camera_id = i
            self.cameras.append(camera)
    
    def synchronized_movement(self, pan, tilt):
        for camera in self.cameras:
            camera.move_to_position(pan, tilt)
```

## Performance Optimization

### Servo Control
- Use quality servo motors for precision
- Implement acceleration/deceleration curves
- Monitor servo current draw
- Add servo position feedback sensors

### Camera Settings
- Optimize resolution for use case
- Adjust frame rate for smooth recording
- Configure camera exposure settings
- Use hardware encoding when available

### System Resources
- Monitor CPU usage during operation
- Optimize control loop timing
- Use threading for concurrent operations
- Implement resource cleanup

## Integration Ideas

### Home Security
- Motion-triggered recording
- Automatic patrol schedules
- Alert notifications
- Remote monitoring

### Time-lapse Photography
- Programmed camera movements
- Interval shooting
- Motion blur effects
- Multi-angle captures

### Live Streaming
- Real-time video streaming
- Interactive viewer control
- Multiple viewing angles
- Chat-controlled movements

## Next Steps
- Add face detection and tracking
- Implement voice control commands
- Create mobile app interface
- Add GPS coordinates for outdoor use
- Integrate with home automation
- Develop AI-powered auto-framing
- Add zoom control for compatible cameras