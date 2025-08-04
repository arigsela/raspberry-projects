# Project 07-01: Camera Module - Digital Photography

Capture high-quality photos with the Raspberry Pi Camera Module for photography, computer vision, and monitoring applications.

## What You'll Learn

- Camera module setup and configuration
- Photo capture techniques
- Image quality settings and effects
- Hardware triggers and LED flash
- Timelapse photography
- Photo booth creation

## Hardware Requirements

- Raspberry Pi 5
- Raspberry Pi Camera Module (v2, v3, or HQ)
- Camera ribbon cable (appropriate length)
- Optional: Button for trigger (GPIO18)
- Optional: LED for flash (GPIO17)
- Optional: RGB LED for status
- Optional: Tripod or camera mount

## Camera Module Types

| Model | Resolution | Sensor | Features | Use Cases |
|-------|------------|--------|----------|-----------|
| Camera v2 | 8MP | Sony IMX219 | Fixed focus, 1080p video | General purpose |
| Camera v3 | 12MP | Sony IMX708 | Autofocus, HDR, 1080p | Better quality |
| HQ Camera | 12MP | Sony IMX477 | Interchangeable lens | Professional |
| NoIR | 8MP | IMX219 (no IR filter) | Night vision | Low light, IR |

## Camera Connection

```
Raspberry Pi 5 Camera Connections:

┌─────────────────────────────┐
│                             │
│  CAM1  CAM0    (CSI Ports)  │
│   |||   |||                 │
│                             │
└─────────────────────────────┘

Ribbon Cable Orientation:
- Blue/Silver side faces ethernet/USB ports
- Contacts face towards PCB
- Lift black clip, insert cable, press down

For Photo Booth Circuit:
Button -------- GPIO18 (Pin 12)
Button -------- GND

Flash LED ----- GPIO17 (Pin 11) ---[220Ω]--- GND

RGB Status LED:
Red ----------- GPIO22 (Pin 15) ---[220Ω]--- GND
Green --------- GPIO27 (Pin 13) ---[220Ω]--- GND
Blue ---------- GPIO23 (Pin 16) ---[220Ω]--- GND
```

## Software Setup

### Enable Camera Interface
```bash
# Method 1: Using raspi-config
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable

# Method 2: Manual edit
sudo nano /boot/config.txt
# Add: camera_auto_detect=1

# Reboot
sudo reboot
```

### Install Dependencies
```bash
# Update system
sudo apt update
sudo apt upgrade

# Install picamera2 (usually pre-installed on Pi OS)
sudo apt install -y python3-picamera2

# Optional: Install additional tools
sudo apt install -y python3-opencv python3-pil
pip3 install numpy pillow

# For video creation from timelapse
sudo apt install -y ffmpeg
```

### Verify Camera
```bash
# List cameras
libcamera-hello --list-cameras

# Test camera
libcamera-hello -t 5000  # 5 second preview
```

## Running the Programs

```bash
# Navigate to project directory
cd ~/raspberry-projects/examples/07-audiovisual/01-photograph

# Run basic photo capture
python3 camera-capture.py

# Or run photo booth with hardware
python3 camera-trigger.py

# To stop, press Ctrl+C
```

## Code Walkthrough

### Basic Photo Capture (camera-capture.py)

1. **Camera Initialization**
   ```python
   picam2 = Picamera2()
   ```
   - Automatically detects camera
   - Configures default settings

2. **Photo Capture**
   ```python
   picam2.start()
   picam2.capture_file("photo.jpg")
   picam2.stop()
   ```
   - Start camera streaming
   - Capture and save
   - Stop to save power

3. **Configuration Options**
   ```python
   config = picam2.create_still_configuration(
       main={"size": (1920, 1080)}
   )
   ```
   - Resolution control
   - Format selection
   - Multiple streams

### Photo Booth (camera-trigger.py)

1. **Hardware Integration**
   - Button for shutter
   - LED flash timing
   - Status indicators

2. **Interactive Features**
   - Countdown sequence
   - Burst mode
   - Preview display

## Key Concepts

### Camera Pipeline
```
Light → Lens → Sensor → ISP → Encoder → File
                ↓        ↓      ↓
              (RAW)  (Process) (JPEG)
```

### Image Signal Processor (ISP)
- **Auto Exposure**: Brightness control
- **Auto White Balance**: Color correction
- **Auto Focus**: Sharpness (v3 only)
- **Noise Reduction**: Clean images
- **Lens Shading**: Vignette correction

### Resolution vs File Size
| Resolution | Megapixels | File Size | Use Case |
|------------|------------|-----------|----------|
| 640×480 | 0.3 MP | ~100 KB | Thumbnails |
| 1280×720 | 0.9 MP | ~300 KB | Web/Email |
| 1920×1080 | 2.1 MP | ~800 KB | HD Display |
| 3280×2464 | 8.1 MP | ~2-3 MB | Printing |
| 4056×3040 | 12.3 MP | ~3-5 MB | Maximum |

## Camera Controls

### Exposure Settings
```python
# Manual exposure
picam2.set_controls({
    "ExposureTime": 10000,     # Microseconds
    "AnalogueGain": 1.0,       # ISO equivalent
    "AeEnable": False          # Disable auto
})
```

### Image Enhancement
```python
controls = {
    "Brightness": 0.0,    # -1.0 to 1.0
    "Contrast": 1.0,      # 0.0 to 2.0
    "Saturation": 1.0,    # 0.0 to 2.0
    "Sharpness": 1.0      # 0.0 to 10.0
}
```

### White Balance
```python
# Presets
picam2.set_controls({"AwbMode": "tungsten"})
# Options: auto, tungsten, fluorescent, daylight, cloudy

# Manual
picam2.set_controls({
    "AwbEnable": False,
    "ColourGains": (1.5, 1.2)  # (red, blue)
})
```

## Photography Techniques

### 1. Macro Photography
- Use HQ camera with macro lens
- Manual focus adjustment
- Good lighting essential

### 2. Long Exposure
```python
# Night photography
picam2.set_controls({
    "ExposureTime": 10000000,  # 10 seconds
    "AnalogueGain": 1.0
})
```

### 3. HDR Imaging
```python
# Take multiple exposures
exposures = [1000, 10000, 100000]
for exp in exposures:
    picam2.set_controls({"ExposureTime": exp})
    picam2.capture_file(f"hdr_{exp}.jpg")
# Combine in post-processing
```

### 4. Focus Stacking (v3 only)
```python
# Multiple focus points
for focus in range(0, 10):
    picam2.set_controls({"AfMode": 0, "LensPosition": focus})
    time.sleep(0.5)
    picam2.capture_file(f"focus_{focus}.jpg")
```

## Timelapse Creation

### Capture Sequence
```python
# Capture frames
for i in range(num_frames):
    picam2.capture_file(f"frame_{i:04d}.jpg")
    time.sleep(interval)
```

### Create Video
```bash
# Basic video (30 fps)
ffmpeg -r 30 -i frame_%04d.jpg -vcodec libx264 timelapse.mp4

# With options
ffmpeg -r 30 -i frame_%04d.jpg \
    -vcodec libx264 \
    -crf 25 \
    -pix_fmt yuv420p \
    timelapse.mp4
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No camera detected | Check cable connection, enable camera |
| Black images | Remove lens cap, check exposure |
| Blurry photos | Clean lens, check focus (v3) |
| Color issues | Adjust white balance |
| Slow capture | Reduce resolution, disable preview |
| Out of memory | Lower resolution, clear storage |

## Performance Tips

### Fast Capture
```python
# Use video port for speed
picam2.start()
for i in range(100):
    picam2.capture_file(f"fast_{i}.jpg")
# No stop/start between captures
```

### Memory Efficiency
```python
# Capture to array instead of file
array = picam2.capture_array()
# Process in memory
# Save only if needed
```

### Power Saving
```python
# Stop camera when not in use
picam2.stop()

# Lower resolution for preview
config = picam2.create_preview_configuration(
    main={"size": (640, 480)}
)
```

## Project Ideas

1. **Security Camera**
   - Motion detection trigger
   - Email notifications
   - Cloud upload

2. **Wildlife Camera**
   - PIR sensor trigger
   - Weatherproof enclosure
   - Battery powered

3. **360° Product Photography**
   - Turntable control
   - Multiple angles
   - Background removal

4. **Microscope Camera**
   - Macro lens attachment
   - Focus stacking
   - Measurement overlay

5. **Astrophotography**
   - Long exposure
   - Star tracking mount
   - Image stacking

## Image Processing

### With OpenCV
```python
import cv2
import numpy as np

# Capture as array
image = picam2.capture_array()

# Convert colorspace
gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

# Apply filters
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)
```

### With PIL
```python
from PIL import Image, ImageEnhance

# Open captured image
img = Image.open("photo.jpg")

# Enhance
enhancer = ImageEnhance.Contrast(img)
enhanced = enhancer.enhance(1.5)

# Resize
thumbnail = img.resize((128, 128))
```

## Camera Module Care

1. **Handling**
   - Hold by edges only
   - Avoid touching lens/sensor
   - Ground yourself (static)

2. **Cleaning**
   - Use lens cleaning cloth
   - Compressed air for dust
   - Isopropyl alcohol if needed

3. **Storage**
   - Keep in anti-static bag
   - Protect from moisture
   - Avoid extreme temperatures

## Next Steps

After mastering photography:
1. Explore video recording
2. Implement computer vision
3. Build streaming applications
4. Create time-lapse projects
5. Develop AI image recognition

## Resources

- [Picamera2 Documentation](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Camera Module Hardware](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [libcamera Apps](https://www.raspberrypi.com/documentation/computers/camera_software.html)
- [Computer Vision Tutorials](https://opencv.org/)