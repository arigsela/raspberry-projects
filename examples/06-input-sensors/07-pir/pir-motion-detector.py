#!/usr/bin/env python3
"""
PIR Motion Detector with RGB LED Indicator
Detects motion and provides visual feedback using an RGB LED
"""

from gpiozero import MotionSensor, RGBLED
from time import sleep, time
from datetime import datetime
import signal
import sys

# GPIO Configuration
PIR_PIN = 17
RGB_RED_PIN = 18
RGB_GREEN_PIN = 27
RGB_BLUE_PIN = 22

# Colors for different states
COLOR_NO_MOTION = (0, 0, 1)    # Blue - idle
COLOR_MOTION = (1, 1, 0)        # Yellow - motion detected
COLOR_ALERT = (1, 0, 0)         # Red - continuous motion

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def format_time():
    """Return current time as formatted string"""
    return datetime.now().strftime("%H:%M:%S")

def main():
    """Main motion detection program"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize components
    pir = MotionSensor(PIR_PIN)
    led = RGBLED(red=RGB_RED_PIN, green=RGB_GREEN_PIN, blue=RGB_BLUE_PIN)
    
    print("PIR Motion Detector with RGB LED")
    print(f"PIR Sensor: GPIO{PIR_PIN}")
    print(f"RGB LED: R=GPIO{RGB_RED_PIN}, G=GPIO{RGB_GREEN_PIN}, B=GPIO{RGB_BLUE_PIN}")
    print("\nWaiting for PIR to stabilize...")
    
    # Let PIR stabilize (some modules need warm-up time)
    led.color = (0.1, 0.1, 0.1)  # Dim white during warm-up
    sleep(5)
    
    print("Ready! Monitoring for motion...")
    print("\nLED Colors:")
    print("- Blue: No motion")
    print("- Yellow: Motion detected")
    print("- Red: Continuous motion (>5 seconds)")
    print("\nPress Ctrl+C to exit\n")
    
    # Set initial state
    led.color = COLOR_NO_MOTION
    motion_start_time = None
    motion_count = 0
    last_motion_time = 0
    
    # Motion detection callbacks
    def motion_detected():
        nonlocal motion_start_time, motion_count, last_motion_time
        
        current_time = time()
        motion_count += 1
        
        # If this is the first motion or motion after a break
        if motion_start_time is None:
            motion_start_time = current_time
            print(f"[{format_time()}] Motion detected! (Event #{motion_count})")
            led.color = COLOR_MOTION
        
        # Check for continuous motion
        if current_time - motion_start_time > 5:
            if led.color != COLOR_ALERT:
                print(f"[{format_time()}] Continuous motion detected - Alert!")
                led.color = COLOR_ALERT
                # Could add alarm sound here
        
        last_motion_time = current_time
    
    def no_motion():
        nonlocal motion_start_time
        
        if motion_start_time is not None:
            duration = time() - motion_start_time
            print(f"[{format_time()}] Motion ended (duration: {duration:.1f}s)")
            motion_start_time = None
            led.color = COLOR_NO_MOTION
    
    # Attach callbacks
    pir.when_motion = motion_detected
    pir.when_no_motion = no_motion
    
    # Main loop for statistics
    try:
        start_time = time()
        
        while True:
            sleep(30)  # Update statistics every 30 seconds
            
            # Calculate statistics
            runtime = time() - start_time
            if runtime > 0:
                activity_rate = (motion_count / runtime) * 60  # Events per minute
                
                print(f"\n--- Statistics ---")
                print(f"Runtime: {runtime/60:.1f} minutes")
                print(f"Motion events: {motion_count}")
                print(f"Activity rate: {activity_rate:.2f} events/minute")
                print(f"Currently: {'Motion detected' if pir.motion_detected else 'No motion'}")
                print("------------------\n")
    
    except KeyboardInterrupt:
        pass
    finally:
        # Turn off LED on exit
        led.off()
        print(f"\nTotal motion events: {motion_count}")

if __name__ == "__main__":
    main()