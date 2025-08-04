#!/usr/bin/env python3
"""
Camera with Button Trigger and LED Flash
Interactive photo booth with hardware controls
"""

from picamera2 import Picamera2, Preview
from gpiozero import Button, LED, RGBLED
import time
import os
from datetime import datetime
import signal
import sys
from threading import Thread

# GPIO Configuration
BUTTON_PIN = 18      # Shutter button
FLASH_LED_PIN = 17   # White LED for flash
STATUS_LED_PINS = {  # RGB LED for status
    'red': 22,
    'green': 27,
    'blue': 23
}

# Camera Configuration
PHOTO_DIR = os.path.expanduser("~/Pictures/photo-booth")
COUNTDOWN_TIME = 3  # seconds

class PhotoBooth:
    """Photo booth with hardware controls"""
    
    def __init__(self):
        """Initialize photo booth components"""
        # Hardware
        self.button = Button(BUTTON_PIN, bounce_time=0.1)
        self.flash = LED(FLASH_LED_PIN)
        self.status = RGBLED(
            red=STATUS_LED_PINS['red'],
            green=STATUS_LED_PINS['green'],
            blue=STATUS_LED_PINS['blue']
        )
        
        # Camera
        self.picam2 = Picamera2()
        self.configure_camera()
        
        # State
        self.ready = False
        self.processing = False
        
        # Create photo directory
        if not os.path.exists(PHOTO_DIR):
            os.makedirs(PHOTO_DIR)
        
        # Set up button handler
        self.button.when_pressed = self.button_pressed
    
    def configure_camera(self):
        """Configure camera for photo booth use"""
        config = self.picam2.create_still_configuration(
            main={"size": (1920, 1080)},  # Full HD photos
            lores={"size": (640, 480)},   # Preview resolution
            display="lores"
        )
        self.picam2.configure(config)
    
    def set_status(self, color):
        """Set status LED color"""
        colors = {
            'ready': (0, 1, 0),      # Green
            'countdown': (1, 1, 0),   # Yellow
            'capture': (1, 0, 0),     # Red
            'processing': (0, 0, 1),  # Blue
            'error': (1, 0, 1)        # Magenta
        }
        self.status.color = colors.get(color, (0, 0, 0))
    
    def button_pressed(self):
        """Handle button press"""
        if self.ready and not self.processing:
            Thread(target=self.take_photo).start()
    
    def countdown_sequence(self):
        """Countdown with LED feedback"""
        print("\nGet ready!")
        
        for i in range(COUNTDOWN_TIME, 0, -1):
            print(f"{i}...")
            self.set_status('countdown')
            time.sleep(0.5)
            self.status.off()
            time.sleep(0.5)
    
    def flash_sequence(self):
        """Camera flash simulation"""
        self.flash.on()
        time.sleep(0.1)
        self.flash.off()
    
    def take_photo(self):
        """Take a photo with countdown and effects"""
        self.processing = True
        self.set_status('processing')
        
        try:
            # Countdown
            self.countdown_sequence()
            
            # Capture moment
            self.set_status('capture')
            print("SMILE!")
            
            # Flash and capture
            self.flash_sequence()
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(PHOTO_DIR, f"photo_{timestamp}.jpg")
            
            # Capture photo
            self.picam2.capture_file(filename)
            
            print(f"Photo saved: {filename}")
            
            # Success indication
            for _ in range(3):
                self.set_status('ready')
                time.sleep(0.2)
                self.status.off()
                time.sleep(0.2)
            
        except Exception as e:
            print(f"Error taking photo: {e}")
            self.set_status('error')
            time.sleep(2)
        
        finally:
            self.processing = False
            self.set_status('ready')
    
    def photo_booth_mode(self):
        """Run interactive photo booth"""
        print("\n=== Photo Booth Mode ===")
        print("Press the button to take a photo")
        print("Press Ctrl+C to exit\n")
        
        # Start camera preview
        self.picam2.start_preview(Preview.QTGL)
        self.picam2.start()
        
        # Set ready state
        self.ready = True
        self.set_status('ready')
        
        try:
            # Keep running
            signal.pause()
        
        except KeyboardInterrupt:
            print("\nShutting down photo booth...")
        
        finally:
            self.ready = False
            self.picam2.stop_preview()
            self.picam2.stop()
            self.status.off()
            self.flash.off()
    
    def burst_mode(self):
        """Take burst photos on button hold"""
        print("\n=== Burst Mode ===")
        print("Hold button for burst photos")
        print("Press Ctrl+C to exit\n")
        
        self.picam2.start()
        self.set_status('ready')
        
        burst_count = 0
        burst_active = False
        
        try:
            while True:
                if self.button.is_pressed and not burst_active:
                    # Start burst
                    burst_active = True
                    burst_count = 0
                    burst_dir = os.path.join(PHOTO_DIR, f"burst_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    os.makedirs(burst_dir)
                    print(f"Burst started! Hold button...")
                    self.set_status('capture')
                
                elif self.button.is_pressed and burst_active:
                    # Continue burst
                    burst_count += 1
                    filename = os.path.join(burst_dir, f"burst_{burst_count:03d}.jpg")
                    self.picam2.capture_file(filename)
                    
                    # Flash effect
                    self.flash.on()
                    time.sleep(0.05)
                    self.flash.off()
                    
                    time.sleep(0.1)  # Burst rate limiter
                
                elif not self.button.is_pressed and burst_active:
                    # End burst
                    burst_active = False
                    print(f"Burst complete! {burst_count} photos taken")
                    self.set_status('ready')
                
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\nBurst mode stopped")
        
        finally:
            self.picam2.stop()
            self.status.off()
    
    def motion_trigger_mode(self):
        """Placeholder for motion-triggered photos"""
        print("\n=== Motion Trigger Mode ===")
        print("This would use a PIR sensor to trigger photos")
        print("See the PIR sensor example for implementation")
    
    def run(self):
        """Main menu for photo booth"""
        print("Camera Photo Booth")
        print("==================")
        print(f"Photos will be saved to: {PHOTO_DIR}")
        
        while True:
            print("\n\nSelect Mode:")
            print("1. Photo booth (button trigger)")
            print("2. Burst mode (hold button)")
            print("3. Motion trigger (requires PIR)")
            print("4. Exit")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                self.photo_booth_mode()
            elif choice == '2':
                self.burst_mode()
            elif choice == '3':
                self.motion_trigger_mode()
            elif choice == '4':
                break
            else:
                print("Invalid choice")
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        self.picam2.close()
        self.button.close()
        self.flash.close()
        self.status.close()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def main():
    """Main program"""
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        booth = PhotoBooth()
        booth.run()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure:")
        print("1. Camera is connected and enabled")
        print("2. LEDs and button are wired correctly")
        print("3. You have necessary permissions")

if __name__ == "__main__":
    main()