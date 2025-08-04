#!/usr/bin/env python3
"""
Automatic Motion Capture System
Intelligent motion-triggered photography and video recording system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

import time
import signal
import threading
import json
from datetime import datetime, timedelta
import subprocess

# Import camera libraries
try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder, MJPEGEncoder
    from picamera2.outputs import FileOutput, CircularOutput
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False

from gpiozero import MotionSensor, Button, LED, Buzzer, PWMLED

# GPIO Configuration
PIR_SENSOR_PIN = 27      # PIR motion sensor
BACKUP_PIR_PIN = 22      # Secondary PIR for coverage

# Control inputs
CAPTURE_BUTTON_PIN = 17  # Manual capture trigger
MODE_BUTTON_PIN = 18     # Mode selection
SETTINGS_BUTTON_PIN = 23 # Settings adjustment

# Status indicators
MOTION_LED_PIN = 24      # Motion detection indicator
CAPTURE_LED_PIN = 25     # Capture in progress
STATUS_LED_PIN = 26      # System status
POWER_LED_PIN = 19       # Power/ready indicator

# Audio feedback
BUZZER_PIN = 13          # Audio notifications

# Camera settings
PHOTO_WIDTH = 3280
PHOTO_HEIGHT = 2464
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30
VIDEO_BITRATE = 15000000  # 15 Mbps for high quality

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class MotionCaptureSystem:
    """Intelligent motion-triggered capture system with multiple modes"""
    
    def __init__(self):
        """Initialize motion capture system"""
        # Initialize camera
        if CAMERA_AVAILABLE:
            self.camera = Picamera2()
            self._configure_camera()
        else:
            self.camera = None
            print("Warning: Camera not available")
        
        # Initialize motion sensors
        try:
            self.primary_pir = MotionSensor(PIR_SENSOR_PIN)
            self.secondary_pir = MotionSensor(BACKUP_PIR_PIN)
            self.dual_pir = True
        except:
            try:
                self.primary_pir = MotionSensor(PIR_SENSOR_PIN)
                self.secondary_pir = None
                self.dual_pir = False
            except:
                self.primary_pir = None
                self.secondary_pir = None
                self.dual_pir = False
                print("Warning: No PIR sensors detected")
        
        # Initialize controls
        try:
            self.capture_button = Button(CAPTURE_BUTTON_PIN)
            self.mode_button = Button(MODE_BUTTON_PIN)
            self.settings_button = Button(SETTINGS_BUTTON_PIN)
            self.has_buttons = True
        except:
            self.has_buttons = False
            print("Warning: Control buttons not available")
        
        # Initialize indicators
        try:
            self.motion_led = LED(MOTION_LED_PIN)
            self.capture_led = PWMLED(CAPTURE_LED_PIN)  # PWM for breathing effect
            self.status_led = LED(STATUS_LED_PIN)
            self.power_led = LED(POWER_LED_PIN)
            self.buzzer = Buzzer(BUZZER_PIN)
            self.has_indicators = True
        except:
            self.has_indicators = False
            print("Warning: Status indicators not available")
        
        # Capture modes
        self.capture_modes = ["photo", "video", "timelapse", "burst", "security"]
        self.current_mode = 0
        
        # Motion detection settings
        self.motion_sensitivity = "medium"  # low, medium, high
        self.motion_timeout = 5.0          # seconds before considering motion ended
        self.cooldown_period = 2.0         # seconds between captures
        self.multi_sensor_required = False # require both sensors for trigger
        
        # Capture settings
        self.burst_count = 5               # photos in burst mode
        self.burst_interval = 0.5          # seconds between burst photos
        self.video_duration = 10           # seconds for video mode
        self.timelapse_interval = 2.0      # seconds between timelapse frames
        self.timelapse_duration = 60       # total timelapse duration
        
        # File management
        self.output_directory = "motion_captures"
        self.max_files = 1000             # maximum files to keep
        self.max_storage_mb = 5000        # maximum storage usage
        
        # Statistics and state
        self.motion_count = 0
        self.capture_count = 0
        self.false_positive_count = 0
        self.system_start_time = time.time()
        self.last_motion_time = 0
        self.last_capture_time = 0
        self.is_capturing = False
        
        # Motion detection state
        self.motion_detected = False
        self.motion_timer = None
        self.capture_in_progress = False
        
        # Advanced features
        self.intelligent_detection = True  # filter false positives
        self.time_based_sensitivity = True # adjust sensitivity by time of day
        self.learning_mode = True          # learn motion patterns
        self.motion_zones = []             # future: define detection zones
        
        # Data storage
        self.motion_log = []
        self.settings = self.load_settings()
        
        # Create output directory
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Setup callbacks
        self._setup_callbacks()
        
        # Start background processes
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Initialize indicators
        if self.has_indicators:
            self.power_led.on()
            self.status_led.on()
            self.buzzer.beep(0.1, 0.1, n=3)  # Startup sound
        
        print("🎥 Motion Capture System Initialized")
        print(f"Mode: {self.capture_modes[self.current_mode].upper()}")
        
    def _configure_camera(self):
        """Configure camera for optimal capture"""
        if not self.camera:
            return
        
        try:
            # Configure for high-quality stills
            still_config = self.camera.create_still_configuration(
                main={"size": (PHOTO_WIDTH, PHOTO_HEIGHT), "format": "RGB888"},
                controls={
                    "FrameRate": 15,
                    "ExposureTime": 20000,  # 20ms max exposure
                    "AnalogueGain": 1.0,
                    "ColourGains": (1.4, 1.5)
                }
            )
            self.camera.configure(still_config)
            print(f"📷 Camera configured: {PHOTO_WIDTH}x{PHOTO_HEIGHT} stills")
        except Exception as e:
            print(f"Camera configuration failed: {e}")
    
    def _setup_callbacks(self):
        """Setup hardware callbacks"""
        if self.primary_pir:
            self.primary_pir.when_motion = self._on_motion_detected
            self.primary_pir.when_no_motion = self._on_motion_ended
        
        if self.secondary_pir:
            self.secondary_pir.when_motion = self._on_secondary_motion
        
        if self.has_buttons:
            self.capture_button.when_pressed = self._manual_capture
            self.mode_button.when_pressed = self._cycle_mode
            self.settings_button.when_pressed = self._adjust_settings
    
    def _on_motion_detected(self):
        """Handle motion detection from primary sensor"""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_capture_time < self.cooldown_period:
            return
        
        # Check if dual sensor mode requires confirmation
        if self.dual_pir and self.multi_sensor_required:
            if not (self.secondary_pir and self.secondary_pir.motion_detected):
                return
        
        # Apply intelligent filtering
        if self.intelligent_detection and self._is_false_positive():
            self.false_positive_count += 1
            return
        
        self.motion_count += 1
        self.last_motion_time = current_time
        self.motion_detected = True
        
        # Log motion event
        motion_event = {
            'timestamp': datetime.now().isoformat(),
            'sensor': 'primary',
            'mode': self.capture_modes[self.current_mode],
            'sensitivity': self.motion_sensitivity
        }
        self.motion_log.append(motion_event)
        
        # Visual/audio feedback
        if self.has_indicators:
            self.motion_led.on()
            self.buzzer.beep(0.05, 0.0, n=1)
        
        print(f"🚶 Motion detected! #{self.motion_count}")
        
        # Trigger capture based on mode
        self._trigger_capture()
        
        # Reset motion timer
        if self.motion_timer:
            self.motion_timer.cancel()
        self.motion_timer = threading.Timer(self.motion_timeout, self._on_motion_timeout)
        self.motion_timer.start()
    
    def _on_secondary_motion(self):
        """Handle motion from secondary sensor"""
        if self.dual_pir and not self.multi_sensor_required:
            # Independent triggering
            self._on_motion_detected()
        # If multi_sensor_required, this just confirms primary detection
    
    def _on_motion_ended(self):
        """Handle end of motion detection"""
        # Motion timer will handle the actual end of motion period
        pass
    
    def _on_motion_timeout(self):
        """Handle motion timeout"""
        self.motion_detected = False
        if self.has_indicators:
            self.motion_led.off()
        
        # Stop continuous capture modes if active
        if self.capture_modes[self.current_mode] == "security" and self.is_capturing:
            self._stop_security_recording()
    
    def _is_false_positive(self):
        """Intelligent false positive detection"""
        if not self.intelligent_detection:
            return False
        
        current_time = time.time()
        
        # Check for too frequent triggers (possible sensor noise)
        if current_time - self.last_motion_time < 0.5:
            return True
        
        # Check time-based patterns (learn when false positives occur)
        if self.learning_mode and len(self.motion_log) > 10:
            # Simple pattern detection - avoid times with many false positives
            current_hour = datetime.now().hour
            recent_false_positives = sum(1 for event in self.motion_log[-20:] 
                                       if event.get('false_positive', False) and 
                                       datetime.fromisoformat(event['timestamp']).hour == current_hour)
            if recent_false_positives > 5:
                return True
        
        return False
    
    def _trigger_capture(self):
        """Trigger capture based on current mode"""
        if self.capture_in_progress:
            return
        
        mode = self.capture_modes[self.current_mode]
        
        if mode == "photo":
            self._capture_photo()
        elif mode == "video":
            self._capture_video()
        elif mode == "timelapse":
            self._start_timelapse()
        elif mode == "burst":
            self._capture_burst()
        elif mode == "security":
            self._start_security_recording()
    
    def _capture_photo(self):
        """Capture a single high-quality photo"""
        if not self.camera or self.capture_in_progress:
            return
        
        self.capture_in_progress = True
        self.capture_count += 1
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motion_photo_{timestamp}_{self.motion_count:04d}.jpg"
            filepath = os.path.join(self.output_directory, filename)
            
            # Visual feedback
            if self.has_indicators:
                self.capture_led.on()
            
            # Capture photo
            self.camera.capture_file(filepath)
            
            print(f"📸 Photo captured: {filename}")
            
            # Audio feedback
            if self.has_indicators:
                self.buzzer.beep(0.2, 0.0, n=1)
            
            self.last_capture_time = time.time()
            
        except Exception as e:
            print(f"Photo capture failed: {e}")
        finally:
            if self.has_indicators:
                self.capture_led.off()
            self.capture_in_progress = False
    
    def _capture_video(self):
        """Capture motion-triggered video"""
        if not self.camera or self.capture_in_progress:
            return
        
        self.capture_in_progress = True
        self.capture_count += 1
        
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"motion_video_{timestamp}_{self.motion_count:04d}.h264"
            filepath = os.path.join(self.output_directory, filename)
            
            # Configure for video
            video_config = self.camera.create_video_configuration(
                main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT), "format": "RGB888"},
                controls={"FrameRate": VIDEO_FPS}
            )
            self.camera.configure(video_config)
            
            # Visual feedback
            if self.has_indicators:
                self.capture_led.on()
            
            # Start recording
            encoder = H264Encoder(bitrate=VIDEO_BITRATE)
            output = FileOutput(filepath)
            
            self.camera.start_recording(encoder, output)
            self.is_capturing = True
            
            print(f"🎬 Video recording started: {filename}")
            
            # Record for specified duration
            def stop_recording():
                try:
                    self.camera.stop_recording()
                    self.is_capturing = False
                    print(f"🎬 Video recording completed: {self.video_duration}s")
                    
                    if self.has_indicators:
                        self.capture_led.off()
                        self.buzzer.beep(0.1, 0.1, n=2)
                    
                except Exception as e:
                    print(f"Stop recording failed: {e}")
                finally:
                    self.capture_in_progress = False
            
            # Schedule stop
            stop_timer = threading.Timer(self.video_duration, stop_recording)
            stop_timer.start()
            
            self.last_capture_time = time.time()
            
        except Exception as e:
            print(f"Video capture failed: {e}")
            self.capture_in_progress = False
            if self.has_indicators:
                self.capture_led.off()
    
    def _capture_burst(self):
        """Capture burst of photos"""
        if not self.camera or self.capture_in_progress:
            return
        
        self.capture_in_progress = True
        
        def burst_sequence():
            try:
                if self.has_indicators:
                    self.capture_led.on()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                for i in range(self.burst_count):
                    filename = f"burst_{timestamp}_{self.motion_count:04d}_{i+1:02d}.jpg"
                    filepath = os.path.join(self.output_directory, filename)
                    
                    self.camera.capture_file(filepath)
                    self.capture_count += 1
                    
                    print(f"📸 Burst {i+1}/{self.burst_count}: {filename}")
                    
                    if i < self.burst_count - 1:  # Don't sleep after last photo
                        time.sleep(self.burst_interval)
                
                print(f"📸 Burst complete: {self.burst_count} photos")
                
                if self.has_indicators:
                    self.buzzer.beep(0.05, 0.05, n=self.burst_count)
                
            except Exception as e:
                print(f"Burst capture failed: {e}")
            finally:
                if self.has_indicators:
                    self.capture_led.off()
                self.capture_in_progress = False
        
        # Run burst in thread to avoid blocking
        burst_thread = threading.Thread(target=burst_sequence, daemon=True)
        burst_thread.start()
        
        self.last_capture_time = time.time()
    
    def _start_timelapse(self):
        """Start motion-triggered timelapse"""
        if not self.camera or self.capture_in_progress:
            return
        
        self.capture_in_progress = True
        
        def timelapse_sequence():
            try:
                if self.has_indicators:
                    self.capture_led.pulse()  # Pulsing effect for timelapse
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                total_frames = int(self.timelapse_duration / self.timelapse_interval)
                
                print(f"⏱️ Timelapse started: {total_frames} frames over {self.timelapse_duration}s")
                
                for frame in range(total_frames):
                    if not self.capture_in_progress:  # Allow early termination
                        break
                    
                    filename = f"timelapse_{timestamp}_{self.motion_count:04d}_{frame+1:04d}.jpg"
                    filepath = os.path.join(self.output_directory, filename)
                    
                    self.camera.capture_file(filepath)
                    self.capture_count += 1
                    
                    print(f"⏱️ Frame {frame+1}/{total_frames}")
                    
                    if frame < total_frames - 1:
                        time.sleep(self.timelapse_interval)
                
                print(f"⏱️ Timelapse complete: {frame+1} frames")
                
                if self.has_indicators:
                    self.buzzer.beep(0.2, 0.1, n=3)
                
            except Exception as e:
                print(f"Timelapse failed: {e}")
            finally:
                if self.has_indicators:
                    self.capture_led.off()
                self.capture_in_progress = False
        
        timelapse_thread = threading.Thread(target=timelapse_sequence, daemon=True)
        timelapse_thread.start()
        
        self.last_capture_time = time.time()
    
    def _start_security_recording(self):
        """Start continuous security recording"""
        if not self.camera or self.is_capturing:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_{timestamp}_{self.motion_count:04d}.h264"
            filepath = os.path.join(self.output_directory, filename)
            
            # Configure for video
            video_config = self.camera.create_video_configuration(
                main={"size": (VIDEO_WIDTH, VIDEO_HEIGHT), "format": "RGB888"},
                controls={"FrameRate": VIDEO_FPS}
            )
            self.camera.configure(video_config)
            
            # Start recording
            encoder = H264Encoder(bitrate=VIDEO_BITRATE)
            output = FileOutput(filepath)
            
            self.camera.start_recording(encoder, output)
            self.is_capturing = True
            
            if self.has_indicators:
                self.capture_led.on()
            
            print(f"🔒 Security recording started: {filename}")
            
        except Exception as e:
            print(f"Security recording failed: {e}")
    
    def _stop_security_recording(self):
        """Stop security recording"""
        if not self.is_capturing:
            return
        
        try:
            self.camera.stop_recording()
            self.is_capturing = False
            
            if self.has_indicators:
                self.capture_led.off()
                self.buzzer.beep(0.1, 0.1, n=2)
            
            print("🔒 Security recording stopped")
            
        except Exception as e:
            print(f"Stop security recording failed: {e}")
    
    def _manual_capture(self):
        """Manual capture trigger"""
        print("📷 Manual capture triggered")
        self._trigger_capture()
    
    def _cycle_mode(self):
        """Cycle through capture modes"""
        self.current_mode = (self.current_mode + 1) % len(self.capture_modes)
        mode_name = self.capture_modes[self.current_mode]
        
        print(f"🔄 Mode: {mode_name.upper()}")
        
        if self.has_indicators:
            # Beep count indicates mode number
            self.buzzer.beep(0.1, 0.1, n=self.current_mode + 1)
    
    def _adjust_settings(self):
        """Adjust sensitivity settings"""
        sensitivities = ["low", "medium", "high"]
        current_index = sensitivities.index(self.motion_sensitivity)
        next_index = (current_index + 1) % len(sensitivities)
        self.motion_sensitivity = sensitivities[next_index]
        
        print(f"🎛️ Sensitivity: {self.motion_sensitivity.upper()}")
        
        if self.has_indicators:
            # Different beep patterns for sensitivity
            if self.motion_sensitivity == "low":
                self.buzzer.beep(0.3, 0.0, n=1)
            elif self.motion_sensitivity == "medium":
                self.buzzer.beep(0.15, 0.15, n=2)
            else:  # high
                self.buzzer.beep(0.1, 0.1, n=3)
    
    def _monitoring_loop(self):
        """Background monitoring and maintenance"""
        while self.monitoring_active:
            try:
                # Breathing LED effect when idle
                if self.has_indicators and not self.capture_in_progress:
                    self.capture_led.pulse()
                
                # Cleanup old files if storage limit reached
                self._cleanup_storage()
                
                # Save motion log periodically
                if len(self.motion_log) > 0 and len(self.motion_log) % 10 == 0:
                    self._save_motion_log()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def _cleanup_storage(self):
        """Clean up old files to manage storage"""
        try:
            files = []
            for filename in os.listdir(self.output_directory):
                filepath = os.path.join(self.output_directory, filename)
                if os.path.isfile(filepath) and filename.endswith(('.jpg', '.h264')):
                    size = os.path.getsize(filepath)
                    mtime = os.path.getmtime(filepath)
                    files.append((filepath, size, mtime))
            
            # Sort by modification time (oldest first)
            files.sort(key=lambda x: x[2])
            
            # Check if cleanup needed
            total_size = sum(size for _, size, _ in files) / (1024 * 1024)  # MB
            total_count = len(files)
            
            if total_size > self.max_storage_mb or total_count > self.max_files:
                files_to_remove = max(1, len(files) // 10)  # Remove 10% of files
                
                for i in range(files_to_remove):
                    if i < len(files):
                        os.remove(files[i][0])
                        print(f"🗑️ Cleaned up: {os.path.basename(files[i][0])}")
                
        except Exception as e:
            print(f"Storage cleanup failed: {e}")
    
    def load_settings(self):
        """Load system settings"""
        try:
            with open('motion_capture_settings.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_settings(self):
        """Save system settings"""
        settings = {
            'capture_mode': self.current_mode,
            'motion_sensitivity': self.motion_sensitivity,
            'video_duration': self.video_duration,
            'burst_count': self.burst_count,
            'timelapse_interval': self.timelapse_interval,
            'cooldown_period': self.cooldown_period
        }
        
        with open('motion_capture_settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    def _save_motion_log(self):
        """Save motion detection log"""
        try:
            with open('motion_log.json', 'w') as f:
                json.dump(self.motion_log, f, indent=2)
        except Exception as e:
            print(f"Failed to save motion log: {e}")
    
    def get_statistics(self):
        """Get system statistics"""
        uptime = time.time() - self.system_start_time
        return {
            'uptime_hours': uptime / 3600,
            'motion_detections': self.motion_count,
            'captures_taken': self.capture_count,
            'false_positives': self.false_positive_count,
            'current_mode': self.capture_modes[self.current_mode],
            'sensitivity': self.motion_sensitivity,
            'detection_rate': self.motion_count / (uptime / 3600) if uptime > 0 else 0,
            'capture_success_rate': (self.capture_count / self.motion_count * 100) if self.motion_count > 0 else 0
        }
    
    def cleanup(self):
        """Clean up system resources"""
        print("\n🧹 Cleaning up motion capture system...")
        
        # Stop recording if active
        if self.is_capturing:
            self._stop_security_recording()
        
        # Stop monitoring
        self.monitoring_active = False
        
        # Cancel timers
        if self.motion_timer:
            self.motion_timer.cancel()
        
        # Save settings and logs
        self.save_settings()
        self._save_motion_log()
        
        # Turn off indicators
        if self.has_indicators:
            self.motion_led.off()
            self.capture_led.off()
            self.status_led.off()
            self.buzzer.beep(0.2, 0.1, n=3)  # Shutdown sound
            time.sleep(1)
            self.power_led.off()
        
        # Close hardware
        if self.primary_pir:
            self.primary_pir.close()
        if self.secondary_pir:
            self.secondary_pir.close()
        
        if self.has_buttons:
            self.capture_button.close()
            self.mode_button.close()
            self.settings_button.close()
        
        if self.has_indicators:
            self.motion_led.close()
            self.capture_led.close()
            self.status_led.close()
            self.power_led.close()
            self.buzzer.close()
        
        if self.camera:
            self.camera.close()

def interactive_demo():
    """Interactive motion capture demonstration"""
    print("\n🎥 Interactive Motion Capture Demo")
    print("System will respond to motion and button presses")
    print("Press Ctrl+C to exit")
    
    if not CAMERA_AVAILABLE:
        print("⚠️ Warning: Camera not available - using simulation mode")
    
    try:
        system = MotionCaptureSystem()
        
        print("\n📋 Controls:")
        print("🚶 Motion Detection: Automatic capture on movement")
        print("📷 Capture Button: Manual trigger")
        print("🔄 Mode Button: Cycle capture modes")
        print("🎛️ Settings Button: Adjust sensitivity")
        
        print(f"\n🎮 Capture Modes:")
        for i, mode in enumerate(system.capture_modes):
            indicator = "👉" if i == system.current_mode else "  "
            print(f"{indicator} {i+1}. {mode.upper()}")
        
        start_time = time.time()
        
        while True:
            # Display status
            stats = system.get_statistics()
            elapsed = time.time() - start_time
            
            mode_icon = {"photo": "📸", "video": "🎬", "timelapse": "⏱️", 
                        "burst": "📱", "security": "🔒"}
            current_icon = mode_icon.get(system.capture_modes[system.current_mode], "🎥")
            
            motion_status = "🚶" if system.motion_detected else "⚪"
            capture_status = "🔴" if system.capture_in_progress else "⚫"
            
            print(f"\r{current_icon} {system.capture_modes[system.current_mode].upper()} | "
                  f"{motion_status} Motion: {stats['motion_detections']:3d} | "
                  f"{capture_status} Captures: {stats['captures_taken']:3d} | "
                  f"Sensitivity: {stats['sensitivity'].upper()[:3]} | "
                  f"Time: {elapsed:.0f}s", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\n📊 Session Summary:")
        stats = system.get_statistics()
        print(f"Motion detections: {stats['motion_detections']}")
        print(f"Captures taken: {stats['captures_taken']}")
        print(f"False positives: {stats['false_positives']}")
        print(f"Detection rate: {stats['detection_rate']:.1f}/hour")
        print(f"Success rate: {stats['capture_success_rate']:.1f}%")
    finally:
        system.cleanup()

def automatic_demo():
    """Automatic demonstration of motion capture features"""
    print("\n🤖 Automatic Motion Capture Demo")
    print("Demonstrating all capture modes with simulated motion")
    
    if not CAMERA_AVAILABLE:
        print("⚠️ Camera simulation mode")
    
    try:
        system = MotionCaptureSystem()
        
        # Demo sequence for each mode
        modes_demo = [
            ("Photo Mode", 0, "Single photo capture"),
            ("Video Mode", 1, "Short video recording"),
            ("Burst Mode", 3, "Multiple photos in sequence"),
            ("Security Mode", 4, "Continuous monitoring")
        ]
        
        for mode_name, mode_index, description in modes_demo:
            print(f"\n🎬 {mode_name} Demo")
            print(f"Description: {description}")
            
            system.current_mode = mode_index
            print(f"Mode set to: {system.capture_modes[mode_index].upper()}")
            
            # Simulate motion detection
            print("Simulating motion detection...")
            system._on_motion_detected()
            
            # Wait for capture to complete
            time.sleep(3 if mode_index == 1 else 2)  # Longer for video
            
            print(f"✅ {mode_name} demo completed")
            time.sleep(1)
        
        print(f"\n✅ All demonstrations completed!")
        
        # Show final statistics
        stats = system.get_statistics()
        print(f"\n📊 Demo Statistics:")
        print(f"Motion simulations: {stats['motion_detections']}")
        print(f"Captures created: {stats['captures_taken']}")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    finally:
        system.cleanup()

def security_monitoring():
    """Security monitoring mode"""
    print("\n🔒 Security Monitoring Mode")
    print("Continuous monitoring with motion-triggered recording")
    print("Press Ctrl+C to exit")
    
    if not CAMERA_AVAILABLE:
        print("⚠️ Camera simulation mode")
    
    try:
        system = MotionCaptureSystem()
        system.current_mode = 4  # Security mode
        
        print("🔒 Security system armed")
        print("📹 Motion detection active")
        print("🚨 Recording will start on motion")
        
        detection_count = 0
        start_time = time.time()
        
        while True:
            # Simulate security events for demo
            if not system.primary_pir:  # No real PIR sensor
                if int(time.time()) % 15 == 0:  # Every 15 seconds
                    detection_count += 1
                    print(f"\n🚨 Security Alert #{detection_count}")
                    system._on_motion_detected()
                    time.sleep(1)  # Prevent multiple triggers
            
            # Display security status
            elapsed = time.time() - start_time
            recording_status = "🔴 RECORDING" if system.is_capturing else "⚪ MONITORING"
            
            print(f"\r🔒 Security Active: {elapsed/60:.1f}min | "
                  f"Alerts: {system.motion_count} | {recording_status}", end='')
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n\n🔒 Security session summary:")
        stats = system.get_statistics()
        print(f"Monitoring time: {stats['uptime_hours']:.1f} hours")
        print(f"Motion alerts: {stats['motion_detections']}")
        print(f"Recordings created: {stats['captures_taken']}")
    finally:
        system.cleanup()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Automatic Motion Capture System")
    print("==============================")
    print("🎥 Intelligent Motion-Triggered Photography")
    print("📸 Multiple Capture Modes")
    print("🚶 Advanced Motion Detection")
    print("🤖 Smart False Positive Filtering")
    
    if not CAMERA_AVAILABLE:
        print("\n⚠️ Warning: Camera not available")
        print("Demo modes will simulate camera functionality")
    
    while True:
        print("\n\nSelect Demo Mode:")
        print("1. Interactive motion capture")
        print("2. Automatic demonstration")
        print("3. Security monitoring mode")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            interactive_demo()
        elif choice == '2':
            automatic_demo()
        elif choice == '3':
            security_monitoring()
        elif choice == '4':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()