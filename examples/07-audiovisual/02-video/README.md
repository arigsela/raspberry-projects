# Video Recording with Raspberry Pi Camera

Record high-quality video using the Raspberry Pi camera module with advanced features like motion detection, timelapse, and security monitoring.

## What You'll Learn
- Raspberry Pi camera module programming
- Video encoding (H.264, MJPEG)
- Motion-triggered recording
- Timelapse photography techniques
- Circular buffer recording
- File management and conversion
- Security camera system design

## Hardware Requirements
- Raspberry Pi 5 with camera connector
- Raspberry Pi Camera Module (v1, v2, v3, or HQ Camera)
- Optional: PIR motion sensor
- Optional: Buttons for control
- Optional: LEDs for status indication
- Optional: Buzzer for audio feedback
- Jumper wires

## Circuit Diagram

```
Raspberry Pi Camera Module:
┌─────────────────────────┐
│     Camera Module       │
│  ┌─────────────────┐    │  Connect via camera
│  │     Lens        │    │  connector (not GPIO)
│  │                 │    │
│  └─────────────────┘    │
├─────────────────────────┤
│ Ribbon Cable Connector  │
└─────────┬───────────────┘
          │
          └── Camera Connector on Pi

Optional Controls:
Record Button:  GPIO17 → Button → GND (with pull-up)
Mode Button:    GPIO18 → Button → GND (with pull-up)
Motion Sensor:  GPIO27 → PIR Sensor → 5V/GND

Optional Indicators:
Record LED:     GPIO23 → 220Ω → LED → GND
Status LED:     GPIO24 → 220Ω → LED → GND
Buzzer:         GPIO25 → Buzzer → GND

Note: Camera connects via dedicated camera connector,
      not GPIO pins!
```

## Software Dependencies

Install required libraries:
```bash
# Camera library for Pi 5
pip install picamera2

# GPIO library
pip install gpiozero

# Enable camera interface
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Optional: Video conversion tools
sudo apt install ffmpeg
```

## Running the Program

```bash
cd examples/07-audiovisual/02-video
python video-recording.py
```

Or use the Makefile:
```bash
make          # Run the main program
make test     # Test camera functionality
make motion   # Run motion detection demo
make security # Run security camera system
make install  # Install dependencies
```

## Code Walkthrough

### Camera Initialization
Set up the camera with optimal settings:
```python
def _configure_camera(self):
    video_config = self.camera.create_video_configuration(
        main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT), "format": "RGB888"},
        controls={"FrameRate": VIDEO_FPS}
    )
    self.camera.configure(video_config)
```

### Basic Recording
Start and stop video recording:
```python
def start_recording(self, duration=None):
    filename = self._generate_filename("video", "h264")
    encoder = H264Encoder(bitrate=VIDEO_BITRATE)
    output = FileOutput(filename)
    
    self.camera.start_recording(encoder, output)
    self.is_recording = True
```

### Motion-Triggered Recording
Automatically record when motion is detected:
```python
def start_motion_recording(self):
    def motion_handler():
        if not self.is_recording:
            self.start_recording()
        
        # Reset motion timer
        if self.motion_timer:
            self.motion_timer.cancel()
        
        self.motion_timer = threading.Timer(self.motion_timeout, self.stop_recording)
        self.motion_timer.start()
    
    return motion_handler
```

### Timelapse Recording
Create timelapse videos with adjustable intervals:
```python
def start_timelapse_recording(self, total_duration=60, interval=1.0):
    frames_per_second = 1.0 / interval
    total_frames = int(total_duration * frames_per_second)
    
    def timelapse_loop():
        frames_captured = 0
        while frames_captured < total_frames:
            time.sleep(interval)
            frames_captured += 1
```

### Circular Buffer Recording
Continuous recording with the ability to save recent footage:
```python
def start_continuous_recording(self):
    encoder = H264Encoder(bitrate=VIDEO_BITRATE)
    self.circular_output = CircularOutput(
        buffersize=self.circular_buffer_duration * VIDEO_FPS * 1000
    )
    self.camera.start_recording(encoder, self.circular_output)
```

## Key Concepts

### Video Encoding
- **H.264**: Efficient compression, industry standard
- **MJPEG**: Frame-by-frame compression, larger files
- **Bitrate**: Quality vs file size trade-off
- **Resolution**: Higher resolution = more detail, larger files

### Recording Modes
- **Manual**: User-controlled start/stop
- **Motion-triggered**: Automatic recording on movement
- **Timelapse**: Long duration condensed into short video
- **Continuous**: Always recording, save on events

### Camera Settings
- **Frame rate**: 30fps for smooth motion, lower for longer recording
- **Resolution**: 1080p standard, 4K for high quality
- **Format**: RGB888 for processing, YUV420 for efficiency
- **Controls**: Exposure, white balance, focus

## Available Demos

1. **Manual Recording**: Keyboard-controlled recording
2. **Button-Controlled**: Physical button interface
3. **Motion-Triggered**: PIR sensor activation
4. **Security Camera**: Continuous monitoring system
5. **File Manager**: Organize and convert recordings

## Troubleshooting

### Camera not detected
- Check camera cable connection
- Ensure camera is enabled: `sudo raspi-config`
- Test with: `libcamera-hello --preview`
- Check for loose connections

### Poor video quality
- Increase bitrate (more storage required)
- Check lighting conditions
- Clean camera lens
- Verify camera focus (if adjustable)

### Recording fails
- Check available disk space
- Verify write permissions
- Monitor CPU usage during recording
- Check power supply stability

### Motion detection issues
- Adjust PIR sensor sensitivity
- Check sensor power connections
- Verify sensor positioning and range
- Test with manual trigger

## Advanced Usage

### Custom Video Settings
Optimize for specific use cases:
```python
# High quality settings
video_config = camera.create_video_configuration(
    main={"size": (3840, 2160), "format": "RGB888"},  # 4K
    controls={
        "FrameRate": 24,
        "ExposureTime": 33333,  # 1/30s
        "AnalogueGain": 1.0,
        "ColourGains": (1.4, 1.5)
    }
)
```

### Multi-Stream Recording
Record multiple formats simultaneously:
```python
def dual_stream_recording(self):
    # High-res main stream
    main_encoder = H264Encoder(bitrate=20000000)
    main_output = FileOutput("main.h264")
    
    # Low-res preview stream
    preview_encoder = H264Encoder(bitrate=1000000)
    preview_output = FileOutput("preview.h264")
    
    camera.start_recording([main_encoder, preview_encoder], 
                          [main_output, preview_output])
```

### Audio Integration
Add audio recording (requires USB microphone):
```python
def record_with_audio(self):
    # Start video recording
    self.start_recording()
    
    # Start audio recording with arecord
    audio_cmd = [
        'arecord', '-D', 'plughw:1,0', '-f', 'cd',
        '-t', 'wav', 'audio.wav'
    ]
    audio_process = subprocess.Popen(audio_cmd)
    
    # Merge later with ffmpeg
```

### Remote Control
Web-based camera control:
```python
def start_web_server(self):
    from flask import Flask, render_template, request
    
    app = Flask(__name__)
    
    @app.route('/start_recording')
    def start_recording():
        self.recorder.start_recording()
        return "Recording started"
    
    @app.route('/stop_recording')
    def stop_recording():
        self.recorder.stop_recording()
        return "Recording stopped"
```

### Motion Detection Tuning
Adjust sensitivity and zones:
```python
class AdvancedMotionDetector:
    def __init__(self):
        self.motion_threshold = 30
        self.detection_zones = [(100, 100, 300, 300)]  # x, y, w, h
        self.sensitivity = 0.5
    
    def detect_motion(self, frame):
        # Implement custom motion detection
        # using frame differencing or optical flow
        pass
```

## File Management

### Automatic Cleanup
Manage storage space automatically:
```python
def cleanup_old_files(self, max_age_days=7, max_size_gb=10):
    cutoff_time = time.time() - (max_age_days * 24 * 3600)
    total_size = 0
    
    for filename in os.listdir(self.output_directory):
        filepath = os.path.join(self.output_directory, filename)
        if os.path.getmtime(filepath) < cutoff_time:
            os.remove(filepath)
```

### Video Conversion
Convert H.264 to MP4 for compatibility:
```bash
# Using ffmpeg
ffmpeg -i video.h264 -c copy video.mp4

# Using Python
subprocess.run([
    'ffmpeg', '-i', 'input.h264',
    '-c', 'copy', 'output.mp4'
])
```

### Streaming
Stream video over network:
```python
def start_rtmp_stream(self, rtmp_url):
    encoder = H264Encoder(bitrate=2000000)
    
    # Stream to RTMP server
    cmd = [
        'ffmpeg', '-f', 'h264', '-i', '-',
        '-c', 'copy', '-f', 'flv', rtmp_url
    ]
    
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    output = FileOutput(process.stdin)
    
    camera.start_recording(encoder, output)
```

## Performance Optimization

### CPU Usage
- Use hardware encoding (H.264)
- Optimize frame rate vs quality
- Monitor system temperature
- Consider GPU memory split

### Storage Management
- Use fast SD cards (Class 10, U3)
- Consider USB 3.0 storage for high bitrates
- Implement file rotation
- Compress older recordings

### Power Considerations
- Monitor power consumption during recording
- Use adequate power supply (3A+ recommended)
- Consider battery backup for security applications

## Security Applications

### Surveillance System
Complete security camera setup:
```python
class SecuritySystem:
    def __init__(self):
        self.zones = []  # Motion detection zones
        self.alerts = []  # Alert history
        self.recording_schedule = {}  # Time-based recording
    
    def arm_system(self):
        # Enable motion detection
        # Start continuous recording
        # Setup alert notifications
        pass
```

### Privacy Considerations
- Implement access controls
- Encrypt sensitive recordings
- Follow local privacy laws
- Provide recording notifications

## Integration Ideas

### Home Automation
- Integration with Home Assistant
- MQTT messaging for events
- Smart home trigger responses
- Mobile app notifications

### AI Integration
- Object detection (using TensorFlow Lite)
- Face recognition
- Activity classification
- Anomaly detection

## Next Steps
- Add live streaming capabilities
- Implement cloud storage backup
- Create mobile app for remote control
- Add facial recognition features
- Integrate with home automation systems
- Develop time-lapse scheduling
- Add GPS location tagging for portable use