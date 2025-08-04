# Automatic Motion Capture System

Intelligent motion-triggered photography and video recording system with advanced detection algorithms, multiple capture modes, and smart false positive filtering.

## What You'll Learn
- PIR motion sensor programming
- Intelligent motion detection algorithms
- Multi-mode camera capture systems
- False positive filtering techniques
- Automated file management
- Real-time system monitoring
- Background thread management
- Smart storage cleanup

## Hardware Requirements
- Raspberry Pi 5 with camera connector
- Raspberry Pi Camera Module (v1, v2, v3, or HQ Camera)
- PIR motion sensor (HC-SR501 or similar)
- Optional: Secondary PIR sensor for dual-zone detection
- 3x Push buttons for control
- 4x LEDs for status indication (including 1 PWM LED)
- Buzzer for audio feedback
- Jumper wires
- Breadboard
- Adequate power supply (3A+ recommended)

## Circuit Diagram

```
Automatic Motion Capture System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ Camera Connector ── Camera Module                          │
│                                                             │
│ GPIO27 ── PIR Sensor 1 (Primary)                           │
│ GPIO22 ── PIR Sensor 2 (Secondary, optional)               │
│                                                             │
│ GPIO17 ── Capture Button                                    │
│ GPIO18 ── Mode Button                                       │
│ GPIO23 ── Settings Button                                   │
│                                                             │
│ GPIO24 ── Motion LED (+220Ω)                               │
│ GPIO25 ── Capture LED (PWM, +220Ω)                         │
│ GPIO26 ── Status LED (+220Ω)                               │
│ GPIO19 ── Power LED (+220Ω)                                │
│                                                             │
│ GPIO13 ── Buzzer                                            │
│                                                             │
│ 5V ────── PIR VCC, Button Pull-ups                         │
│ GND ───── PIR GND, Button GND, LED Cathodes               │
└─────────────────────────────────────────────────────────────┘

PIR Motion Sensor (HC-SR501):
┌─────────────────┐
│   HC-SR501      │
├─────────────────┤
│ VCC ── 5V       │
│ OUT ── GPIO27   │
│ GND ── GND      │
└─────────────────┘

Optional Second PIR (Dual-Zone Detection):
┌─────────────────┐
│   HC-SR501 #2   │
├─────────────────┤
│ VCC ── 5V       │
│ OUT ── GPIO22   │
│ GND ── GND      │
└─────────────────┘

Control Buttons (with 10kΩ pull-up resistors):
Capture Button:  GPIO17 ── Button ── GND
Mode Button:     GPIO18 ── Button ── GND  
Settings Button: GPIO23 ── Button ── GND

Status LEDs (with 220Ω current limiting resistors):
Motion LED:   GPIO24 ── 220Ω ── LED ── GND
Capture LED:  GPIO25 ── 220Ω ── LED ── GND (PWM for effects)
Status LED:   GPIO26 ── 220Ω ── LED ── GND
Power LED:    GPIO19 ── 220Ω ── LED ── GND

Audio Feedback:
Buzzer:       GPIO13 ── Buzzer ── GND

Note: PIR sensors may require 30-60 seconds warm-up time
```

## Software Dependencies

Install required libraries:
```bash
# Camera library for Pi 5
pip install picamera2

# GPIO and hardware control
pip install gpiozero

# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/02-motion-capture
python automatic-motion-capture.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Automatic demonstration
make security # Security monitoring mode
make test     # Test hardware components
make setup    # Install dependencies
```

## Code Walkthrough

### Motion Detection Setup
Initialize PIR sensors with intelligent detection:
```python
def __init__(self):
    # Dual PIR setup for better coverage
    self.primary_pir = MotionSensor(PIR_SENSOR_PIN)
    self.secondary_pir = MotionSensor(BACKUP_PIR_PIN)
    
    # Setup callbacks
    self.primary_pir.when_motion = self._on_motion_detected
    self.primary_pir.when_no_motion = self._on_motion_ended
```

### Intelligent False Positive Filtering
Smart algorithm to reduce false triggers:
```python
def _is_false_positive(self):
    current_time = time.time()
    
    # Check for too frequent triggers (sensor noise)
    if current_time - self.last_motion_time < 0.5:
        return True
    
    # Time-based pattern learning
    if self.learning_mode:
        current_hour = datetime.now().hour
        recent_false_positives = self._count_recent_false_positives(current_hour)
        if recent_false_positives > 5:
            return True
    
    return False
```

### Multi-Mode Capture System
Support for different capture modes:
```python
def _trigger_capture(self):
    mode = self.capture_modes[self.current_mode]
    
    if mode == "photo":
        self._capture_photo()
    elif mode == "video":
        self._capture_video()
    elif mode == "burst":
        self._capture_burst()
    elif mode == "timelapse":
        self._start_timelapse()
    elif mode == "security":
        self._start_security_recording()
```

### Burst Photography
Capture multiple photos in rapid succession:
```python
def _capture_burst(self):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for i in range(self.burst_count):
        filename = f"burst_{timestamp}_{i+1:02d}.jpg"
        filepath = os.path.join(self.output_directory, filename)
        
        self.camera.capture_file(filepath)
        print(f"📸 Burst {i+1}/{self.burst_count}: {filename}")
        
        if i < self.burst_count - 1:
            time.sleep(self.burst_interval)
```

### Automatic Storage Management
Clean up old files to prevent storage overflow:
```python
def _cleanup_storage(self):
    # Get all capture files with timestamps
    files = [(filepath, size, mtime) for file in captures]
    files.sort(key=lambda x: x[2])  # Sort by modification time
    
    # Remove oldest files if limits exceeded
    if total_size > self.max_storage_mb or total_count > self.max_files:
        files_to_remove = len(files) // 10  # Remove 10%
        for i in range(files_to_remove):
            os.remove(files[i][0])
```

## Capture Modes

### 1. Photo Mode
Single high-quality photo on motion detection:
- 3280x2464 resolution (8MP)
- Optimized exposure settings
- Instant capture with minimal delay

### 2. Video Mode
Motion-triggered video recording:
- 1920x1080 @ 30fps
- Configurable duration (default 10 seconds)
- H.264 encoding for efficiency

### 3. Burst Mode
Rapid sequence of photos:
- Configurable count (default 5 photos)
- Adjustable interval (default 0.5 seconds)
- Perfect for capturing motion sequences

### 4. Timelapse Mode
Motion-triggered timelapse sequence:
- Extended capture period
- Configurable frame intervals
- Creates motion-activated time-lapse clips

### 5. Security Mode
Continuous monitoring system:
- Records until motion stops
- Maintains motion history log
- Automated storage management

## Advanced Features

### Intelligent Detection
- **False Positive Filtering**: Learns patterns to reduce false triggers
- **Dual Sensor Mode**: Uses two PIR sensors for better accuracy
- **Time-Based Sensitivity**: Adjusts detection based on time of day
- **Cooldown Periods**: Prevents excessive triggering

### Smart Storage Management
- **Automatic Cleanup**: Removes old files when storage limits reached
- **Size Monitoring**: Tracks total storage usage
- **File Organization**: Timestamped filenames with sequence numbers

### Real-Time Feedback
- **Visual Indicators**: LEDs show system status and activity
- **Audio Feedback**: Buzzer provides capture confirmation
- **Status Display**: Real-time statistics and system information

## Available Demos

1. **Interactive Mode**: Full manual and automatic operation
2. **Automatic Demo**: Showcase all capture modes
3. **Security Monitoring**: Continuous surveillance mode
4. **Component Test**: Verify hardware connections

## Troubleshooting

### PIR sensor not triggering
- Check 5V power connection
- Allow 30-60 seconds warm-up time
- Adjust sensitivity potentiometer on sensor
- Verify GPIO pin connections
- Test sensor with multimeter

### Camera not capturing
- Check camera cable connection
- Ensure camera enabled: `sudo raspi-config`
- Test with: `libcamera-hello --preview`
- Verify adequate power supply
- Check available disk space

### Too many false positives
- Adjust PIR sensitivity (potentiometer)
- Enable intelligent filtering
- Use dual sensor mode
- Position sensors away from heat sources
- Enable learning mode for pattern recognition

### Storage filling up quickly
- Reduce capture quality settings
- Enable automatic cleanup
- Lower storage limits
- Use external USB storage
- Implement cloud backup

## Advanced Usage

### Custom Detection Zones
Configure specific areas for motion detection:
```python
# Future enhancement - define detection zones
system.motion_zones = [
    {'name': 'entrance', 'bounds': (100, 100, 300, 200)},
    {'name': 'window', 'bounds': (400, 150, 200, 250)}
]
```

### Time-Based Scheduling
Different behavior for different times:
```python
def get_time_based_settings(self):
    current_hour = datetime.now().hour
    
    if 22 <= current_hour or current_hour <= 6:  # Night mode
        return {'sensitivity': 'high', 'mode': 'security'}
    elif 6 < current_hour < 8:  # Morning mode
        return {'sensitivity': 'medium', 'mode': 'burst'}
    else:  # Day mode
        return {'sensitivity': 'low', 'mode': 'photo'}
```

### Cloud Integration
Upload captures to cloud storage:
```python
import boto3

def upload_to_cloud(self, filepath):
    s3 = boto3.client('s3')
    key = f"motion-captures/{os.path.basename(filepath)}"
    
    try:
        s3.upload_file(filepath, 'my-bucket', key)
        print(f"☁️ Uploaded: {key}")
        os.remove(filepath)  # Remove local copy
    except Exception as e:
        print(f"Upload failed: {e}")
```

### Motion Analytics
Analyze motion patterns:
```python
def analyze_motion_patterns(self):
    # Group motions by hour
    hourly_counts = {}
    for event in self.motion_log:
        hour = datetime.fromisoformat(event['timestamp']).hour
        hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
    
    # Find peak activity times
    peak_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
    return peak_hours[:3]  # Top 3 active hours
```

### Mobile Notifications
Send alerts to mobile devices:
```python
import requests

def send_mobile_alert(self, message):
    # Using Pushover service (example)
    url = "https://api.pushover.net/1/messages.json"
    data = {
        'token': 'YOUR_APP_TOKEN',
        'user': 'YOUR_USER_KEY',
        'message': message,
        'title': 'Motion Alert'
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("📱 Mobile alert sent")
    except Exception as e:
        print(f"Alert failed: {e}")
```

### Computer Vision Integration
Add object detection capabilities:
```python
import cv2

def detect_objects(self, image_path):
    # Load pre-trained model (example with YOLO)
    net = cv2.dnn.readNet('yolo.weights', 'yolo.cfg')
    
    # Load and process image
    image = cv2.imread(image_path)
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    
    # Run detection
    net.setInput(blob)
    outputs = net.forward()
    
    # Process detections
    detected_objects = self._process_detections(outputs, image)
    return detected_objects
```

## Performance Optimization

### System Resources
- Monitor CPU usage during capture
- Use hardware encoding when available
- Optimize thread usage for background tasks
- Implement efficient file I/O

### Power Management
- Use motion-activated power for peripherals
- Implement sleep modes during inactive periods
- Monitor battery levels for portable operation
- Optimize LED brightness for power saving

### Storage Efficiency
- Use appropriate compression settings
- Implement smart file rotation
- Consider real-time streaming for remote storage
- Use symbolic links for file organization

## Integration Ideas

### Home Security
- Integration with existing alarm systems
- Automated lighting activation on motion
- SMS/email alerts for security events
- Integration with door locks and access control

### Wildlife Photography
- Extended battery operation
- Weather-resistant enclosure
- Ultra-sensitive motion detection
- Time-lapse for long-term observation

### Scientific Research
- Data logging for motion studies
- Integration with environmental sensors
- Automated species identification
- Long-term behavioral analysis

## Next Steps
- Add facial recognition capabilities
- Implement machine learning for motion classification
- Create web interface for remote monitoring
- Add GPS tagging for portable installations
- Integrate with home automation systems
- Develop mobile app for configuration
- Add support for multiple camera angles