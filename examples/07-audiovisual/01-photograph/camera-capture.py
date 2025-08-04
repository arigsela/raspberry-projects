#!/usr/bin/env python3
"""
Raspberry Pi Camera Module - Photo Capture
Basic photography with the Camera Module using picamera2
"""

from picamera2 import Picamera2, Preview
import time
import os
from datetime import datetime
import signal
import sys

# Configuration
PHOTO_DIR = os.path.expanduser("~/Pictures/raspberry-pi-camera")
PREVIEW_DURATION = 3  # seconds

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def ensure_photo_directory():
    """Create photo directory if it doesn't exist"""
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)
        print(f"Created photo directory: {PHOTO_DIR}")

def generate_filename(prefix="photo", extension="jpg"):
    """Generate timestamped filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def take_basic_photo(picam2):
    """Take a basic photo with preview"""
    print("\n=== Basic Photo Capture ===")
    print("Showing preview for 3 seconds...")
    
    # Start preview
    picam2.start_preview(Preview.QTGL)
    picam2.start()
    
    # Wait for preview
    time.sleep(PREVIEW_DURATION)
    
    # Capture image
    filename = os.path.join(PHOTO_DIR, generate_filename())
    picam2.capture_file(filename)
    
    # Stop preview
    picam2.stop_preview()
    picam2.stop()
    
    print(f"Photo saved: {filename}")
    return filename

def take_multiple_photos(picam2, count=5, interval=2):
    """Take multiple photos with interval"""
    print(f"\n=== Burst Mode: {count} photos ===")
    print(f"Taking photo every {interval} seconds...")
    
    picam2.start()
    photos = []
    
    for i in range(count):
        filename = os.path.join(PHOTO_DIR, generate_filename(f"burst_{i+1}"))
        picam2.capture_file(filename)
        photos.append(filename)
        print(f"Photo {i+1}/{count}: {filename}")
        
        if i < count - 1:
            time.sleep(interval)
    
    picam2.stop()
    print(f"Burst complete! {len(photos)} photos saved")
    return photos

def take_photo_with_effects(picam2):
    """Demonstrate different camera effects"""
    print("\n=== Photo Effects Demo ===")
    
    effects = {
        "normal": {},
        "bright": {"Brightness": 0.7},
        "dark": {"Brightness": 0.3},
        "high_contrast": {"Contrast": 1.5},
        "low_contrast": {"Contrast": 0.5},
        "saturated": {"Saturation": 1.5},
        "desaturated": {"Saturation": 0.5}
    }
    
    picam2.start()
    
    for effect_name, controls in effects.items():
        print(f"\nApplying effect: {effect_name}")
        
        # Reset controls
        picam2.set_controls({"Brightness": 0.0, "Contrast": 1.0, "Saturation": 1.0})
        
        # Apply effect
        if controls:
            picam2.set_controls(controls)
            time.sleep(0.5)  # Let effect settle
        
        # Capture
        filename = os.path.join(PHOTO_DIR, generate_filename(f"effect_{effect_name}"))
        picam2.capture_file(filename)
        print(f"Saved: {filename}")
    
    picam2.stop()
    print("\nEffects demo complete!")

def take_different_resolutions(picam2):
    """Capture photos at different resolutions"""
    print("\n=== Resolution Test ===")
    
    resolutions = [
        (640, 480, "VGA"),
        (1280, 720, "HD"),
        (1920, 1080, "FullHD"),
        (2592, 1944, "5MP"),
        (3280, 2464, "8MP"),
        (4056, 3040, "12MP")
    ]
    
    for width, height, name in resolutions:
        try:
            print(f"\nTrying {name} ({width}x{height})...")
            
            # Configure camera
            config = picam2.create_still_configuration(
                main={"size": (width, height)}
            )
            picam2.configure(config)
            
            picam2.start()
            time.sleep(1)  # Let camera adjust
            
            # Capture
            filename = os.path.join(PHOTO_DIR, generate_filename(f"res_{name}"))
            picam2.capture_file(filename)
            picam2.stop()
            
            # Check file size
            file_size = os.path.getsize(filename) / 1024 / 1024  # MB
            print(f"Saved: {filename} ({file_size:.2f} MB)")
            
        except Exception as e:
            print(f"Failed: {e}")

def timelapse_mode(picam2, duration_minutes=1, interval_seconds=10):
    """Simple timelapse capture"""
    print(f"\n=== Timelapse Mode ===")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Interval: {interval_seconds} seconds")
    print("Press Ctrl+C to stop early\n")
    
    picam2.start()
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    frame_count = 0
    
    timelapse_dir = os.path.join(PHOTO_DIR, f"timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    os.makedirs(timelapse_dir)
    
    try:
        while time.time() < end_time:
            frame_count += 1
            filename = os.path.join(timelapse_dir, f"frame_{frame_count:04d}.jpg")
            
            picam2.capture_file(filename)
            print(f"Frame {frame_count} captured")
            
            # Wait for next frame
            next_frame_time = start_time + (frame_count * interval_seconds)
            sleep_time = next_frame_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\nTimelapse stopped by user")
    
    finally:
        picam2.stop()
        print(f"\nTimelapse complete! {frame_count} frames captured")
        print(f"Saved in: {timelapse_dir}")
        print(f"\nTo create video, use:")
        print(f"ffmpeg -r 30 -i {timelapse_dir}/frame_%04d.jpg -vcodec libx264 timelapse.mp4")

def camera_info(picam2):
    """Display camera information"""
    print("\n=== Camera Information ===")
    
    # Get camera properties
    properties = picam2.camera_properties
    
    print(f"Model: {properties.get('Model', 'Unknown')}")
    print(f"Pixel Array Size: {properties.get('PixelArraySize', 'Unknown')}")
    print(f"Unit Cell Size: {properties.get('UnitCellSize', 'Unknown')}")
    print(f"Color Filter: {properties.get('ColorFilterArrangement', 'Unknown')}")
    
    # Get available configurations
    print("\nAvailable sensor modes:")
    sensor_modes = picam2.sensor_modes
    for i, mode in enumerate(sensor_modes):
        print(f"  Mode {i}: {mode}")

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Raspberry Pi Camera Photo Capture")
    print("=================================")
    
    # Ensure photo directory exists
    ensure_photo_directory()
    
    # Initialize camera
    try:
        picam2 = Picamera2()
        print("Camera initialized successfully!")
        
        # Display camera info
        camera_info(picam2)
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        print("\nTroubleshooting:")
        print("1. Check camera cable connection")
        print("2. Enable camera: sudo raspi-config > Interface Options > Camera")
        print("3. Reboot after enabling camera")
        print("4. Check if using correct camera port")
        return
    
    while True:
        print("\n\nSelect Option:")
        print("1. Take basic photo")
        print("2. Burst mode (5 photos)")
        print("3. Photo effects demo")
        print("4. Resolution test")
        print("5. Timelapse mode")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        try:
            if choice == '1':
                take_basic_photo(picam2)
            elif choice == '2':
                take_multiple_photos(picam2)
            elif choice == '3':
                take_photo_with_effects(picam2)
            elif choice == '4':
                take_different_resolutions(picam2)
            elif choice == '5':
                duration = int(input("Duration in minutes (default 1): ") or "1")
                interval = int(input("Interval in seconds (default 10): ") or "10")
                timelapse_mode(picam2, duration, interval)
            elif choice == '6':
                break
            else:
                print("Invalid choice")
        
        except Exception as e:
            print(f"Error: {e}")
            picam2.stop()
    
    # Cleanup
    picam2.close()
    print("\nGoodbye!")

if __name__ == "__main__":
    main()