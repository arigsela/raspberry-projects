#!/usr/bin/env python3
"""
Advanced Camera Control System
Combine camera, joystick, servos, and display for a pan-tilt camera system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))

from adc0834 import ADC0834
import time
import signal
import threading
import json
from datetime import datetime
import math

# Import camera libraries
try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FileOutput
    CAMERA_AVAILABLE = True
except ImportError:
    CAMERA_AVAILABLE = False

from gpiozero import Servo, Button, LED, PWMLED, Buzzer

# GPIO Configuration
# ADC for joystick
ADC_CS = 17
ADC_CLK = 18  
ADC_DI = 27
ADC_DO = 22
JOYSTICK_X_CHANNEL = 0
JOYSTICK_Y_CHANNEL = 1

# Servo motors for pan/tilt
PAN_SERVO_PIN = 20      # Horizontal rotation
TILT_SERVO_PIN = 21     # Vertical rotation

# Control buttons
RECORD_BUTTON_PIN = 23  # Start/stop recording
MODE_BUTTON_PIN = 24    # Cycle modes
PRESET_BUTTON_PIN = 25  # Save/recall presets

# Status indicators
STATUS_LED_PIN = 26     # System status
RECORD_LED_PIN = 19     # Recording indicator
BUZZER_PIN = 13         # Audio feedback

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

class CameraController:
    """Advanced camera control with pan/tilt and recording"""
    
    def __init__(self):
        """Initialize camera control system"""
        # Initialize hardware
        self.adc = ADC0834(ADC_CS, ADC_CLK, ADC_DI, ADC_DO)
        
        # Initialize servos
        self.pan_servo = Servo(PAN_SERVO_PIN)
        self.tilt_servo = Servo(TILT_SERVO_PIN)
        
        # Initialize camera
        if CAMERA_AVAILABLE:
            self.camera = Picamera2()
            self._configure_camera()
        else:
            self.camera = None
            print("Warning: Camera not available")
        
        # Control buttons
        self.record_button = Button(RECORD_BUTTON_PIN)
        self.mode_button = Button(MODE_BUTTON_PIN)
        self.preset_button = Button(PRESET_BUTTON_PIN)
        
        # Status indicators
        self.status_led = LED(STATUS_LED_PIN)
        self.record_led = LED(RECORD_LED_PIN)
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # Control state
        self.pan_position = 0.0    # -1.0 to 1.0
        self.tilt_position = 0.0   # -1.0 to 1.0
        self.is_recording = False
        self.recording_encoder = None
        self.recording_output = None
        
        # Control modes
        self.control_modes = ["manual", "preset", "auto_track", "patrol"]
        self.current_mode = 0
        
        # Presets storage
        self.presets = self.load_presets()
        self.current_preset = 0
        
        # Auto tracking
        self.auto_track_center_x = 0.5
        self.auto_track_center_y = 0.5
        
        # Patrol mode
        self.patrol_positions = [
            (-0.8, 0.0),   # Far left
            (0.0, 0.5),    # Center up
            (0.8, 0.0),    # Far right
            (0.0, -0.3)    # Center down
        ]
        self.patrol_index = 0
        self.patrol_thread = None
        self.patrol_active = False
        
        # Joystick calibration
        self.joystick_deadzone = 0.1
        self.joystick_sensitivity = 1.0
        
        # Movement smoothing
        self.movement_smoothing = 0.1  # Lower = smoother movement
        
        # Setup button callbacks
        self.record_button.when_pressed = self.toggle_recording
        self.mode_button.when_pressed = self.cycle_mode
        self.preset_button.when_pressed = self.handle_preset
        
        # Initialize positions
        self.pan_servo.value = self.pan_position
        self.tilt_servo.value = self.tilt_position
        
        # Start control loop
        self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
        self.control_active = True
        self.control_thread.start()
        
        # Status indication
        self.status_led.on()
        self.buzzer.beep(0.1, 0.1, n=2)  # Startup sound
        
        print("🎥 Advanced Camera Control System Initialized")
        print(f"Mode: {self.control_modes[self.current_mode].upper()}")
    
    def _configure_camera(self):
        """Configure camera settings"""
        if not self.camera:
            return
        
        try:
            video_config = self.camera.create_video_configuration(
                main={"size": (1920, 1080), "format": "RGB888"},
                controls={"FrameRate": 30}
            )
            self.camera.configure(video_config)
            print("📹 Camera configured: 1920x1080 @ 30fps")
        except Exception as e:
            print(f"Camera configuration failed: {e}")
    
    def read_joystick(self):
        """Read joystick position with deadzone"""
        try:
            x_raw = self.adc.read_channel(JOYSTICK_X_CHANNEL)
            y_raw = self.adc.read_channel(JOYSTICK_Y_CHANNEL)
            
            # Convert to -1.0 to 1.0 range (assuming center at 127)
            x = (x_raw - 127) / 127.0
            y = (y_raw - 127) / 127.0
            
            # Apply deadzone
            if abs(x) < self.joystick_deadzone:
                x = 0.0
            if abs(y) < self.joystick_deadzone:
                y = 0.0
            
            # Apply sensitivity
            x *= self.joystick_sensitivity
            y *= self.joystick_sensitivity
            
            # Clamp values
            x = max(-1.0, min(1.0, x))
            y = max(-1.0, min(1.0, y))
            
            return x, y
            
        except Exception as e:
            print(f"Joystick read error: {e}")
            return 0.0, 0.0
    
    def update_servo_positions(self, pan_delta, tilt_delta):
        """Update servo positions with smoothing"""
        # Calculate new positions
        new_pan = self.pan_position + pan_delta * self.movement_smoothing
        new_tilt = self.tilt_position + tilt_delta * self.movement_smoothing
        
        # Clamp to servo limits
        new_pan = max(-1.0, min(1.0, new_pan))
        new_tilt = max(-1.0, min(1.0, new_tilt))
        
        # Update if changed significantly
        if abs(new_pan - self.pan_position) > 0.01 or abs(new_tilt - self.tilt_position) > 0.01:
            self.pan_position = new_pan
            self.tilt_position = new_tilt
            
            # Apply to servos
            self.pan_servo.value = self.pan_position
            self.tilt_servo.value = self.tilt_position
            
            return True
        return False
    
    def move_to_position(self, pan, tilt, speed=0.02):
        """Smoothly move to specific position"""
        target_pan = max(-1.0, min(1.0, pan))
        target_tilt = max(-1.0, min(1.0, tilt))
        
        while abs(self.pan_position - target_pan) > 0.05 or abs(self.tilt_position - target_tilt) > 0.05:
            # Calculate movement direction
            pan_diff = target_pan - self.pan_position
            tilt_diff = target_tilt - self.tilt_position
            
            # Limit movement speed
            pan_move = max(-speed, min(speed, pan_diff))
            tilt_move = max(-speed, min(speed, tilt_diff))
            
            # Update positions
            self.pan_position += pan_move
            self.tilt_position += tilt_move
            
            # Apply to servos
            self.pan_servo.value = self.pan_position
            self.tilt_servo.value = self.tilt_position
            
            time.sleep(0.02)
    
    def _control_loop(self):
        """Main control loop"""
        while self.control_active:
            mode = self.control_modes[self.current_mode]
            
            if mode == "manual":
                self._manual_control()
            elif mode == "preset":
                self._preset_control()
            elif mode == "auto_track":
                self._auto_track_control()
            elif mode == "patrol":
                self._patrol_control()
            
            time.sleep(0.02)  # 50Hz update rate
    
    def _manual_control(self):
        """Manual joystick control"""
        x, y = self.read_joystick()
        
        if abs(x) > 0.01 or abs(y) > 0.01:
            self.update_servo_positions(x * 0.5, -y * 0.5)  # Invert Y for intuitive control
    
    def _preset_control(self):
        """Preset position control"""
        # In preset mode, joystick can fine-tune position
        x, y = self.read_joystick()
        
        if abs(x) > 0.3 or abs(y) > 0.3:  # Larger deadzone for fine control
            self.update_servo_positions(x * 0.1, -y * 0.1)  # Slower movement
    
    def _auto_track_control(self):
        """Auto tracking control (simulated)"""
        # This would integrate with computer vision for real tracking
        # For now, simulate gentle movement toward center
        center_error_x = self.auto_track_center_x - 0.5
        center_error_y = self.auto_track_center_y - 0.5
        
        # Gentle correction toward center
        self.update_servo_positions(center_error_x * 0.02, center_error_y * 0.02)
    
    def _patrol_control(self):
        """Patrol mode control"""
        if not self.patrol_active:
            self.start_patrol()
    
    def start_patrol(self):
        """Start patrol sequence"""
        if self.patrol_thread and self.patrol_thread.is_alive():
            return
        
        self.patrol_active = True
        self.patrol_thread = threading.Thread(target=self._patrol_sequence, daemon=True)
        self.patrol_thread.start()
        print("🚶 Patrol mode started")
    
    def _patrol_sequence(self):
        """Execute patrol sequence"""
        while self.patrol_active and self.control_modes[self.current_mode] == "patrol":
            for i, (pan, tilt) in enumerate(self.patrol_positions):
                if not self.patrol_active:
                    break
                
                print(f"📍 Moving to patrol position {i+1}/4")
                self.move_to_position(pan, tilt, speed=0.03)
                
                # Hold position for observation
                time.sleep(3)
        
        self.patrol_active = False
        print("🚶 Patrol sequence completed")
    
    def toggle_recording(self):
        """Toggle video recording"""
        if not self.camera:
            print("❌ Camera not available")
            return
        
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start video recording"""
        if self.is_recording or not self.camera:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"camera_recording_{timestamp}.h264"
            
            encoder = H264Encoder(bitrate=10000000)
            output = FileOutput(filename)
            
            self.camera.start_recording(encoder, output)
            self.recording_encoder = encoder
            self.recording_output = output
            self.is_recording = True
            
            self.record_led.on()
            self.buzzer.beep(0.2, 0.0, n=1)
            
            print(f"🔴 Recording started: {filename}")
            
        except Exception as e:
            print(f"❌ Recording failed: {e}")
    
    def stop_recording(self):
        """Stop video recording"""
        if not self.is_recording:
            return
        
        try:
            self.camera.stop_recording()
            self.is_recording = False
            self.recording_encoder = None
            self.recording_output = None
            
            self.record_led.off()
            self.buzzer.beep(0.1, 0.1, n=2)
            
            print("⏹️ Recording stopped")
            
        except Exception as e:
            print(f"❌ Stop recording failed: {e}")
    
    def cycle_mode(self):
        """Cycle through control modes"""
        # Stop current mode activities
        if self.control_modes[self.current_mode] == "patrol":
            self.patrol_active = False
        
        # Cycle to next mode
        self.current_mode = (self.current_mode + 1) % len(self.control_modes)
        mode_name = self.control_modes[self.current_mode]
        
        print(f"🔄 Mode: {mode_name.upper()}")
        
        # Audio feedback (number of beeps = mode number)
        self.buzzer.beep(0.1, 0.1, n=self.current_mode + 1)
    
    def handle_preset(self):
        """Handle preset button press"""
        mode = self.control_modes[self.current_mode]
        
        if mode == "preset":
            # Long press saves, short press recalls
            # For simplicity, we'll cycle through presets
            self.recall_preset(self.current_preset)
            self.current_preset = (self.current_preset + 1) % len(self.presets)
        else:
            # In other modes, save current position as preset
            self.save_preset()
    
    def save_preset(self):
        """Save current position as preset"""
        preset_name = f"preset_{len(self.presets) + 1}"
        preset_data = {
            'name': preset_name,
            'pan': self.pan_position,
            'tilt': self.tilt_position,
            'timestamp': datetime.now().isoformat()
        }
        
        self.presets.append(preset_data)
        self.save_presets()
        
        print(f"💾 Preset saved: {preset_name} ({self.pan_position:.2f}, {self.tilt_position:.2f})")
        self.buzzer.beep(0.05, 0.05, n=5)  # Quick beeps for save
    
    def recall_preset(self, index):
        """Recall preset position"""
        if 0 <= index < len(self.presets):
            preset = self.presets[index]
            print(f"📍 Recalling preset: {preset['name']}")
            self.move_to_position(preset['pan'], preset['tilt'])
            self.buzzer.beep(0.2, 0.0, n=1)  # Single beep for recall
    
    def load_presets(self):
        """Load presets from file"""
        try:
            with open('camera_presets.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_presets(self):
        """Save presets to file"""
        with open('camera_presets.json', 'w') as f:
            json.dump(self.presets, f, indent=2)
    
    def calibrate_joystick(self):
        """Calibrate joystick center and range"""
        print("\n🎯 Joystick Calibration")
        print("Center the joystick and press Enter...")
        input()
        
        # Read center position
        center_readings = []
        for _ in range(10):
            x_raw = self.adc.read_channel(JOYSTICK_X_CHANNEL)
            y_raw = self.adc.read_channel(JOYSTICK_Y_CHANNEL)
            center_readings.append((x_raw, y_raw))
            time.sleep(0.1)
        
        center_x = sum(r[0] for r in center_readings) / len(center_readings)
        center_y = sum(r[1] for r in center_readings) / len(center_readings)
        
        print(f"✅ Center calibrated: X={center_x:.1f}, Y={center_y:.1f}")
        
        # Store calibration (in real implementation, save to file)
        self.joystick_center_x = center_x
        self.joystick_center_y = center_y
    
    def get_status(self):
        """Get system status"""
        return {
            'mode': self.control_modes[self.current_mode],
            'position': {'pan': self.pan_position, 'tilt': self.tilt_position},
            'recording': self.is_recording,
            'presets': len(self.presets),
            'patrol_active': self.patrol_active
        }
    
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up camera control system...")
        
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
        
        # Stop control loop
        self.control_active = False
        if self.control_thread:
            self.control_thread.join(timeout=1)
        
        # Stop patrol
        self.patrol_active = False
        
        # Center servos
        self.pan_servo.value = 0
        self.tilt_servo.value = 0
        time.sleep(0.5)
        
        # Turn off indicators
        self.status_led.off()
        self.record_led.off()
        
        # Shutdown sound
        self.buzzer.beep(0.2, 0.1, n=3)
        
        # Close hardware
        self.adc.cleanup()
        self.pan_servo.close()
        self.tilt_servo.close()
        self.record_button.close()
        self.mode_button.close()
        self.preset_button.close()
        self.status_led.close()
        self.record_led.close()
        self.buzzer.close()
        
        if self.camera:
            self.camera.close()

def interactive_demo():
    """Interactive demonstration of camera control"""
    print("\n🎥 Interactive Camera Control Demo")
    print("Use joystick to control camera pan/tilt")
    print("Buttons: Record, Mode, Preset")
    print("Press Ctrl+C to exit")
    
    try:
        controller = CameraController()
        
        print("\n📋 Control Instructions:")
        print("🕹️  Joystick: Pan/tilt camera")
        print("🔴 Record button: Start/stop recording")
        print("🔄 Mode button: Cycle control modes")
        print("📍 Preset button: Save/recall positions")
        print("\n🎮 Control Modes:")
        print("1. MANUAL - Direct joystick control")
        print("2. PRESET - Recall saved positions")
        print("3. AUTO_TRACK - Simulated tracking")
        print("4. PATROL - Automatic patrol sequence")
        
        start_time = time.time()
        
        while True:
            status = controller.get_status()
            elapsed = time.time() - start_time
            
            # Status display
            mode_icon = {"manual": "🕹️", "preset": "📍", "auto_track": "🎯", "patrol": "🚶"}
            record_icon = "🔴" if status['recording'] else "⚪"
            
            print(f"\r{mode_icon.get(status['mode'], '🎮')} {status['mode'].upper()} | "
                  f"Pan: {status['position']['pan']:+5.2f} | "
                  f"Tilt: {status['position']['tilt']:+5.2f} | "
                  f"{record_icon} | "
                  f"Presets: {status['presets']} | "
                  f"Time: {elapsed:.0f}s", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print(f"\n\n📊 Session Summary:")
        status = controller.get_status()
        print(f"Final position: Pan {status['position']['pan']:.2f}, Tilt {status['position']['tilt']:.2f}")
        print(f"Presets saved: {status['presets']}")
        print(f"Recording active: {status['recording']}")
    finally:
        controller.cleanup()

def automatic_demo():
    """Automatic demonstration of all features"""
    print("\n🤖 Automatic Camera Control Demo")
    print("Demonstrating all control modes automatically")
    
    try:
        controller = CameraController()
        
        # Demo sequence
        demos = [
            ("Manual Control", lambda: manual_demo_sequence(controller)),
            ("Preset System", lambda: preset_demo_sequence(controller)),
            ("Patrol Mode", lambda: patrol_demo_sequence(controller)),
            ("Recording Demo", lambda: recording_demo_sequence(controller))
        ]
        
        for demo_name, demo_func in demos:
            print(f"\n🎬 Starting: {demo_name}")
            demo_func()
            time.sleep(2)
        
        print(f"\n✅ All demonstrations completed!")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted")
    finally:
        controller.cleanup()

def manual_demo_sequence(controller):
    """Demonstrate manual control"""
    print("📍 Manual positioning demo...")
    
    positions = [
        (-0.5, 0.3, "Left-Up"),
        (0.5, 0.3, "Right-Up"), 
        (0.5, -0.3, "Right-Down"),
        (-0.5, -0.3, "Left-Down"),
        (0.0, 0.0, "Center")
    ]
    
    for pan, tilt, name in positions:
        print(f"  Moving to: {name}")
        controller.move_to_position(pan, tilt)
        time.sleep(1)

def preset_demo_sequence(controller):
    """Demonstrate preset system"""
    print("💾 Preset system demo...")
    
    # Save some presets
    test_positions = [
        (-0.8, 0.0, "Far Left"),
        (0.8, 0.0, "Far Right"),
        (0.0, 0.5, "Center Up")
    ]
    
    for pan, tilt, name in test_positions:
        controller.move_to_position(pan, tilt)
        controller.save_preset()
        print(f"  Saved preset: {name}")
        time.sleep(1)
    
    # Recall presets
    print("  Recalling presets...")
    for i in range(len(test_positions)):
        controller.recall_preset(i)
        time.sleep(2)

def patrol_demo_sequence(controller):
    """Demonstrate patrol mode"""
    print("🚶 Patrol mode demo...")
    
    # Switch to patrol mode
    controller.current_mode = 3  # patrol mode
    controller.start_patrol()
    
    # Let patrol run for a bit
    time.sleep(15)
    
    # Stop patrol
    controller.patrol_active = False

def recording_demo_sequence(controller):
    """Demonstrate recording features"""
    print("🎬 Recording demo...")
    
    if not controller.camera:
        print("  Camera not available, skipping recording demo")
        return
    
    # Record while moving
    print("  Starting recording...")
    controller.start_recording()
    
    # Move camera while recording
    positions = [(0.0, 0.0), (-0.3, 0.2), (0.3, 0.2), (0.0, 0.0)]
    for pan, tilt in positions:
        controller.move_to_position(pan, tilt, speed=0.01)  # Slow for smooth recording
        time.sleep(3)
    
    # Stop recording
    print("  Stopping recording...")
    controller.stop_recording()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Advanced Camera Control System")
    print("============================")
    print("🎥 Pan/Tilt Camera with Recording")
    print("🕹️  Joystick Control")
    print("📍 Preset Positions")
    print("🚶 Patrol Mode")
    print("🎬 Video Recording")
    
    if not CAMERA_AVAILABLE:
        print("\n⚠️ Warning: Camera not available")
        print("Video recording features will be disabled")
    
    while True:
        print("\n\nSelect Demo Mode:")
        print("1. Interactive control (use hardware)")
        print("2. Automatic demonstration")
        print("3. Calibrate joystick")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            interactive_demo()
        elif choice == '2':
            automatic_demo()
        elif choice == '3':
            # Quick calibration demo
            try:
                controller = CameraController()
                controller.calibrate_joystick()
                controller.cleanup()
            except Exception as e:
                print(f"Calibration failed: {e}")
        elif choice == '4':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()