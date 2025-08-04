#!/usr/bin/env python3
"""
Video Recording with Raspberry Pi Camera
Record video using the Raspberry Pi camera module with various features
"""

import time
import signal
import sys
import os
import threading
from datetime import datetime, timedelta
import subprocess

# Import camera libraries
try:
    from picamera2 import Picamera2, Preview
    from picamera2.encoders import H264Encoder, MJPEGEncoder
    from picamera2.outputs import FileOutput, CircularOutput
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False

from gpiozero import Button, LED, Buzzer, MotionSensor

# GPIO Configuration
RECORD_BUTTON_PIN = 17   # Start/stop recording button
MODE_BUTTON_PIN = 18     # Mode selection button
MOTION_SENSOR_PIN = 27   # PIR motion sensor (optional)

# Status indicators
RECORD_LED_PIN = 23      # Recording indicator LED
STATUS_LED_PIN = 24      # General status LED  
BUZZER_PIN = 25          # Audio feedback buzzer

# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_BITRATE = 10000000  # 10 Mbps

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class VideoRecorder:
    """Advanced video recording system with multiple modes"""
    
    def __init__(self):
        """Initialize video recorder"""
        if not CAMERA_AVAILABLE:
            raise ImportError("picamera2 library not available. Install with: pip install picamera2")
        
        # Initialize camera
        self.camera = Picamera2()
        
        # Recording state
        self.is_recording = False
        self.current_encoder = None
        self.current_output = None
        
        # Recording modes
        self.recording_mode = "manual"  # manual, motion, timelapse, continuous
        self.video_format = "h264"      # h264, mjpeg
        
        # File management
        self.output_directory = "videos"
        self.max_file_size_mb = 500
        self.max_recording_duration = 3600  # 1 hour max
        
        # Motion detection
        self.motion_timeout = 10  # seconds
        self.motion_timer = None
        
        # Timelapse settings
        self.timelapse_interval = 1.0  # seconds between frames
        self.timelapse_timer = None
        
        # Circular buffer for continuous recording
        self.circular_buffer_duration = 60  # seconds
        self.circular_output = None
        
        # Statistics
        self.recording_start_time = None
        self.total_recordings = 0
        self.total_recording_time = 0
        
        # Create output directory
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Configure camera
        self._configure_camera()
    
    def _configure_camera(self):
        """Configure camera settings"""
        # Configure video mode
        video_config = self.camera.create_video_configuration(
            main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT), "format": "RGB888"},
            controls={"FrameRate": VIDEO_FPS}
        )
        self.camera.configure(video_config)
        
        print(f"Camera configured: {VIDEO_WIDTH}x{VIDEO_HEIGHT} @ {VIDEO_FPS}fps")
    
    def _generate_filename(self, prefix="video", extension="h264"):
        """Generate unique filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.{extension}"
        return os.path.join(self.output_directory, filename)
    
    def start_recording(self, duration=None):
        """
        Start video recording
        
        Args:
            duration: Maximum recording duration in seconds
        """
        if self.is_recording:
            print("Already recording!")
            return False
        
        try:
            # Generate filename
            if self.video_format == "h264":
                filename = self._generate_filename("video", "h264")
                encoder = H264Encoder(bitrate=VIDEO_BITRATE)
            else:  # mjpeg
                filename = self._generate_filename("video", "mjpeg")
                encoder = MJPEGEncoder()
            
            # Create output
            output = FileOutput(filename)
            
            # Start recording
            self.camera.start_recording(encoder, output)
            
            self.is_recording = True
            self.current_encoder = encoder
            self.current_output = output
            self.recording_start_time = time.time()
            self.total_recordings += 1
            
            print(f"📹 Recording started: {os.path.basename(filename)}")
            
            # Set up automatic stop if duration specified
            if duration:
                def stop_after_duration():
                    time.sleep(duration)
                    if self.is_recording:
                        self.stop_recording()
                
                threading.Thread(target=stop_after_duration, daemon=True).start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self):
        """Stop current recording"""
        if not self.is_recording:
            print("Not currently recording!")
            return False
        
        try:
            self.camera.stop_recording()
            
            # Calculate recording duration
            if self.recording_start_time:
                duration = time.time() - self.recording_start_time
                self.total_recording_time += duration
                print(f"📹 Recording stopped. Duration: {duration:.1f} seconds")
            
            self.is_recording = False
            self.current_encoder = None
            self.current_output = None
            self.recording_start_time = None
            
            return True
            
        except Exception as e:
            print(f"Failed to stop recording: {e}")
            return False
    
    def start_motion_recording(self):
        """Start motion-triggered recording mode"""
        print("🚶 Motion recording mode activated")
        self.recording_mode = "motion"
        
        def motion_handler():
            if not self.is_recording:
                print("Motion detected! Starting recording...")
                self.start_recording()
            
            # Reset motion timer
            if self.motion_timer:
                self.motion_timer.cancel()
            
            # Stop recording after timeout
            self.motion_timer = threading.Timer(self.motion_timeout, self.stop_recording)
            self.motion_timer.start()
        
        return motion_handler
    
    def start_timelapse_recording(self, total_duration=60, interval=1.0):
        """
        Start timelapse recording
        
        Args:
            total_duration: Total duration to record (seconds)
            interval: Interval between frames (seconds)
        """
        if self.is_recording:
            print("Cannot start timelapse while recording!")
            return False
        
        print(f"⏱️ Starting timelapse: {total_duration}s duration, {interval}s interval")
        
        filename = self._generate_filename("timelapse", "h264")
        encoder = H264Encoder(bitrate=VIDEO_BITRATE)
        output = FileOutput(filename)
        
        # Calculate frame rate for timelapse
        frames_per_second = 1.0 / interval
        total_frames = int(total_duration * frames_per_second)
        
        try:
            self.camera.start_recording(encoder, output)
            self.is_recording = True
            self.recording_mode = "timelapse"
            
            # Timelapse capture loop
            def timelapse_loop():
                frames_captured = 0
                while frames_captured < total_frames and self.is_recording:
                    time.sleep(interval)
                    frames_captured += 1
                    print(f"\rTimelapse: {frames_captured}/{total_frames} frames", end='')
                
                if self.is_recording:
                    self.stop_recording()
                    print(f"\n⏱️ Timelapse complete: {frames_captured} frames")
            
            threading.Thread(target=timelapse_loop, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Failed to start timelapse: {e}")
            return False
    
    def start_continuous_recording(self):
        """Start continuous recording with circular buffer"""
        if self.is_recording:
            print("Cannot start continuous mode while recording!")
            return False
        
        print(f"🔄 Starting continuous recording with {self.circular_buffer_duration}s buffer")
        
        try:
            encoder = H264Encoder(bitrate=VIDEO_BITRATE)
            
            # Create circular output buffer
            self.circular_output = CircularOutput(
                buffersize=self.circular_buffer_duration * VIDEO_FPS * 1000  # Rough estimate
            )
            
            self.camera.start_recording(encoder, self.circular_output)
            self.is_recording = True
            self.recording_mode = "continuous"
            
            print("🔄 Continuous recording active. Use save_circular_buffer() to save footage.")
            return True
            
        except Exception as e:
            print(f"Failed to start continuous recording: {e}")
            return False
    
    def save_circular_buffer(self):
        """Save the current circular buffer to file"""
        if self.recording_mode != "continuous" or not self.circular_output:
            print("Not in continuous recording mode!")
            return False
        
        try:
            filename = self._generate_filename("continuous", "h264")
            
            # Save buffer to file
            self.circular_output.fileoutput = filename
            self.circular_output.start()
            time.sleep(1)  # Brief pause to ensure save
            self.circular_output.stop()
            
            print(f"💾 Circular buffer saved: {os.path.basename(filename)}")
            return True
            
        except Exception as e:
            print(f"Failed to save buffer: {e}")
            return False
    
    def capture_still(self):
        """Capture a still image"""
        try:
            filename = self._generate_filename("photo", "jpg")
            
            # Capture still
            self.camera.capture_file(filename)
            
            print(f"📸 Photo captured: {os.path.basename(filename)}")
            return filename
            
        except Exception as e:
            print(f"Failed to capture photo: {e}")
            return None
    
    def list_recordings(self):
        """List all recordings in output directory"""
        try:
            files = os.listdir(self.output_directory)
            video_files = [f for f in files if f.endswith(('.h264', '.mjpeg', '.jpg'))]
            
            if not video_files:
                print("No recordings found.")
                return []
            
            print(f"\n📁 Recordings in {self.output_directory}:")
            for i, filename in enumerate(sorted(video_files), 1):
                filepath = os.path.join(self.output_directory, filename)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                print(f"  {i:2d}. {filename} ({size_mb:.1f} MB) - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return video_files
            
        except Exception as e:
            print(f"Error listing recordings: {e}")
            return []
    
    def delete_recording(self, filename):
        """Delete a specific recording"""
        try:
            filepath = os.path.join(self.output_directory, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Deleted: {filename}")
                return True
            else:
                print(f"File not found: {filename}")
                return False
                
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_statistics(self):
        """Get recording statistics"""
        return {
            'total_recordings': self.total_recordings,
            'total_time': self.total_recording_time,
            'current_mode': self.recording_mode,
            'is_recording': self.is_recording,
            'output_directory': self.output_directory
        }
    
    def cleanup(self):
        """Clean up camera resources"""
        if self.is_recording:
            self.stop_recording()
        
        if self.motion_timer:
            self.motion_timer.cancel()
        
        if self.timelapse_timer:
            self.timelapse_timer.cancel()
        
        self.camera.close()

def manual_recording():
    """Manual video recording control"""
    print("\n=== Manual Video Recording ===")
    print("Control recording with keyboard commands")
    print("Commands: [s]tart, [q]uit, [p]hoto, [l]ist files")
    
    if not CAMERA_AVAILABLE:
        print("Error: picamera2 library not available")
        return
    
    try:
        recorder = VideoRecorder()
        
        while True:
            if recorder.is_recording:
                duration = time.time() - recorder.recording_start_time if recorder.recording_start_time else 0
                print(f"\r🔴 Recording... {duration:.1f}s (press 's' to stop)", end='')
            else:
                print("\r⚪ Ready to record (press 's' to start)", end='')
            
            # Check for keyboard input (simple approach)
            import select
            if select.select([sys.stdin], [], [], 0.1)[0]:
                command = sys.stdin.read(1).lower()
                
                if command == 's':
                    if recorder.is_recording:
                        recorder.stop_recording()
                    else:
                        recorder.start_recording()
                
                elif command == 'p':
                    recorder.capture_still()
                
                elif command == 'l':
                    recorder.list_recordings()
                
                elif command == 'q':
                    break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        recorder.cleanup()

def button_controlled_recording():
    """Button-controlled recording system"""
    print("\n=== Button-Controlled Recording ===")
    print("Use physical buttons to control recording")
    print("Press Ctrl+C to exit")
    
    if not CAMERA_AVAILABLE:
        print("Error: picamera2 library not available")
        return
    
    try:
        recorder = VideoRecorder()
        
        # Setup buttons and indicators
        try:
            record_button = Button(RECORD_BUTTON_PIN)
            mode_button = Button(MODE_BUTTON_PIN)
            record_led = LED(RECORD_LED_PIN)
            status_led = LED(STATUS_LED_PIN)
            buzzer = Buzzer(BUZZER_PIN)
            has_hardware = True
        except:
            has_hardware = False
            print("Note: No buttons/LEDs connected, using keyboard fallback")
        
        modes = ["manual", "motion", "timelapse"]
        current_mode_index = 0
        
        def toggle_recording():
            if recorder.is_recording:
                recorder.stop_recording()
                if has_hardware:
                    record_led.off()
                    buzzer.beep(0.1, 0.1, n=2)
            else:
                mode = modes[current_mode_index]
                if mode == "manual":
                    recorder.start_recording()
                elif mode == "timelapse":
                    recorder.start_timelapse_recording(60, 2.0)  # 60s timelapse, 2s intervals
                
                if has_hardware:
                    record_led.on()
                    buzzer.beep(0.2, 0.0, n=1)
        
        def cycle_mode():
            nonlocal current_mode_index
            current_mode_index = (current_mode_index + 1) % len(modes)
            print(f"\nMode: {modes[current_mode_index].upper()}")
            if has_hardware:
                buzzer.beep(0.05, 0.05, n=current_mode_index + 1)
        
        if has_hardware:
            record_button.when_pressed = toggle_recording
            mode_button.when_pressed = cycle_mode
            status_led.on()  # System ready
        
        print(f"Mode: {modes[current_mode_index].upper()}")
        print("Record button: Start/stop recording")
        print("Mode button: Cycle through modes")
        
        while True:
            # Keyboard fallback if no hardware
            if not has_hardware:
                import select
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()
                    if key == 'r':
                        toggle_recording()
                    elif key == 'm':
                        cycle_mode()
                    elif key == 'q':
                        break
            
            # Update status
            stats = recorder.get_statistics()
            if recorder.is_recording and recorder.recording_start_time:
                duration = time.time() - recorder.recording_start_time
                print(f"\r🔴 Recording {modes[current_mode_index]} - {duration:.1f}s", end='')
            else:
                print(f"\r⚪ {modes[current_mode_index].title()} mode - Ready", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        pass
    finally:
        if has_hardware:
            record_led.close()
            status_led.close()
            record_button.close()
            mode_button.close()
            buzzer.close()
        recorder.cleanup()

def motion_triggered_recording():
    """Motion-triggered recording system"""
    print("\n=== Motion-Triggered Recording ===")
    print("Automatically record when motion is detected")
    print("Press Ctrl+C to exit")
    
    if not CAMERA_AVAILABLE:
        print("Error: picamera2 library not available")
        return
    
    try:
        recorder = VideoRecorder()
        
        try:
            motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
            status_led = LED(STATUS_LED_PIN)
            record_led = LED(RECORD_LED_PIN)
            has_motion_sensor = True
        except:
            has_motion_sensor = False
            print("Note: No motion sensor connected, using simulation mode")
        
        motion_handler = recorder.start_motion_recording()
        motion_count = 0
        
        if has_motion_sensor:
            def on_motion():
                nonlocal motion_count
                motion_count += 1
                print(f"\n🚶 Motion #{motion_count} detected!")
                motion_handler()
                record_led.on()
            
            def on_no_motion():
                record_led.off()
            
            motion_sensor.when_motion = on_motion
            motion_sensor.when_no_motion = on_no_motion
            status_led.on()
        
        print("Motion detection active...")
        print("Walk in front of sensor to trigger recording")
        
        while True:
            if not has_motion_sensor:
                # Simulate motion every 10 seconds for demo
                print("Simulating motion detection...")
                motion_count += 1
                motion_handler()
                time.sleep(15)  # Wait for recording to finish
            else:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        total_recordings = recorder.get_statistics()['total_recordings']
        print(f"\n\nMotion session complete:")
        print(f"Motion detections: {motion_count}")
        print(f"Recordings created: {total_recordings}")
    finally:
        if has_motion_sensor:
            motion_sensor.close()
            status_led.close()
            record_led.close()
        recorder.cleanup()

def security_camera_system():
    """Complete security camera system"""
    print("\n=== Security Camera System ===")
    print("Continuous monitoring with motion detection")
    print("Press Ctrl+C to exit")
    
    if not CAMERA_AVAILABLE:
        print("Error: picamera2 library not available")
        return
    
    try:
        recorder = VideoRecorder()
        
        # Start continuous recording
        recorder.start_continuous_recording()
        
        try:
            motion_sensor = MotionSensor(MOTION_SENSOR_PIN)
            has_motion_sensor = True
        except:
            has_motion_sensor = False
            print("Note: Using simulated motion detection")
        
        motion_events = []
        
        def on_motion_event():
            timestamp = datetime.now()
            motion_events.append(timestamp)
            print(f"\n🚨 Security Event: {timestamp.strftime('%H:%M:%S')}")
            
            # Save the last 60 seconds
            if recorder.save_circular_buffer():
                print("📹 Motion footage saved")
        
        if has_motion_sensor:
            motion_sensor.when_motion = on_motion_event
        
        print("🔒 Security system armed")
        print("📹 Continuous recording active")
        print("🚨 Motion detection enabled")
        
        # Security monitoring loop
        start_time = time.time()
        while True:
            if not has_motion_sensor:
                # Simulate security events
                if int(time.time()) % 30 == 0:  # Every 30 seconds
                    on_motion_event()
                    time.sleep(1)  # Prevent multiple triggers
            
            elapsed = time.time() - start_time
            print(f"\r🔒 Security Active: {elapsed/60:.1f}min | Events: {len(motion_events)}", end='')
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n\n🔒 Security session summary:")
        print(f"Total monitoring time: {(time.time() - start_time)/60:.1f} minutes")
        print(f"Motion events detected: {len(motion_events)}")
        if motion_events:
            print("Event times:")
            for event in motion_events[-5:]:  # Show last 5 events
                print(f"  - {event.strftime('%H:%M:%S')}")
    finally:
        if has_motion_sensor:
            motion_sensor.close()
        recorder.cleanup()

def video_file_manager():
    """Manage recorded video files"""
    print("\n=== Video File Manager ===")
    
    if not CAMERA_AVAILABLE:
        print("Error: picamera2 library not available")
        return
    
    try:
        recorder = VideoRecorder()
        
        while True:
            print("\n📁 Video File Management")
            print("1. List recordings")
            print("2. Delete recording")
            print("3. Record statistics")
            print("4. Convert H.264 to MP4")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                files = recorder.list_recordings()
                
            elif choice == '2':
                files = recorder.list_recordings()
                if files:
                    try:
                        index = int(input("Enter file number to delete: ")) - 1
                        if 0 <= index < len(files):
                            confirm = input(f"Delete '{files[index]}'? (yes/no): ").lower()
                            if confirm == 'yes':
                                recorder.delete_recording(files[index])
                        else:
                            print("Invalid file number")
                    except ValueError:
                        print("Invalid input")
            
            elif choice == '3':
                stats = recorder.get_statistics()
                print(f"\n📊 Recording Statistics:")
                print(f"Total recordings: {stats['total_recordings']}")
                print(f"Total recording time: {stats['total_time']/60:.1f} minutes")
                print(f"Current mode: {stats['current_mode']}")
                print(f"Output directory: {stats['output_directory']}")
            
            elif choice == '4':
                files = [f for f in recorder.list_recordings() if f.endswith('.h264')]
                if files:
                    try:
                        index = int(input("Enter H.264 file number to convert: ")) - 1
                        if 0 <= index < len(files):
                            h264_file = files[index]
                            mp4_file = h264_file.replace('.h264', '.mp4')
                            
                            print(f"Converting {h264_file} to {mp4_file}...")
                            
                            # Use ffmpeg to convert (if available)
                            cmd = [
                                'ffmpeg', '-i', 
                                os.path.join(recorder.output_directory, h264_file),
                                '-c', 'copy',
                                os.path.join(recorder.output_directory, mp4_file)
                            ]
                            
                            try:
                                subprocess.run(cmd, check=True, capture_output=True)
                                print(f"✅ Conversion complete: {mp4_file}")
                            except subprocess.CalledProcessError:
                                print("❌ Conversion failed. Is ffmpeg installed?")
                            except FileNotFoundError:
                                print("❌ ffmpeg not found. Install with: sudo apt install ffmpeg")
                    except ValueError:
                        print("Invalid input")
                else:
                    print("No H.264 files found")
            
            elif choice == '5':
                break
            
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        pass
    finally:
        recorder.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Raspberry Pi Camera Video Recording System")
    print("=========================================")
    print(f"Video Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"Frame Rate: {VIDEO_FPS} fps")
    print(f"Bitrate: {VIDEO_BITRATE/1000000} Mbps")
    
    if not CAMERA_AVAILABLE:
        print("\n⚠️ Warning: picamera2 library not available")
        print("Install with: pip install picamera2")
        print("Also ensure camera is enabled: sudo raspi-config → Interface → Camera")
        return
    
    while True:
        print("\n\nSelect Recording Mode:")
        print("1. Manual recording (keyboard control)")
        print("2. Button-controlled recording")
        print("3. Motion-triggered recording")
        print("4. Security camera system")
        print("5. Video file manager")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == '1':
            manual_recording()
        elif choice == '2':
            button_controlled_recording()
        elif choice == '3':
            motion_triggered_recording()
        elif choice == '4':
            security_camera_system()
        elif choice == '5':
            video_file_manager()
        elif choice == '6':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()