#!/usr/bin/env python3
"""
Touch Switch Capacitive Sensing
Detect touch input using capacitive or resistive touch sensors
"""

from gpiozero import Button, LED, PWMLED, TonalBuzzer
import time
import signal
import sys
from datetime import datetime
import statistics

# GPIO Configuration
TOUCH_PIN = 17      # Touch sensor output
LED_PIN = 18        # Status LED
BUZZER_PIN = 22     # Feedback buzzer

# For multiple touch sensors
TOUCH_PINS = {
    "button1": 17,
    "button2": 27,
    "button3": 23,
    "button4": 24
}

# Musical notes for touch piano
NOTES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25
}

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_touch_detection():
    """Basic capacitive touch detection"""
    print("\n=== Basic Touch Detection ===")
    print("Touch the sensor to trigger")
    print("Press Ctrl+C to exit")
    
    # Touch sensor outputs HIGH when touched
    touch = Button(TOUCH_PIN, pull_up=False)
    
    # Track touches
    touch_count = 0
    last_state = touch.is_pressed
    
    # Initial state
    print(f"Initial state: {'TOUCHED' if last_state else 'NOT TOUCHED'}")
    
    try:
        while True:
            current_state = touch.is_pressed
            
            if current_state != last_state:
                if current_state:
                    touch_count += 1
                    print(f"TOUCHED (Count: {touch_count})")
                else:
                    print("Released")
                last_state = current_state
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nTotal touches: {touch_count}")
    finally:
        touch.close()

def touch_toggle_led():
    """Toggle LED with touch"""
    print("\n=== Touch Toggle LED ===")
    print("Touch to toggle LED on/off")
    print("Press Ctrl+C to exit")
    
    touch = Button(TOUCH_PIN, pull_up=False)
    led = LED(LED_PIN)
    
    # State tracking
    led_state = False
    
    def toggle_led():
        nonlocal led_state
        led_state = not led_state
        if led_state:
            led.on()
            print("LED: ON")
        else:
            led.off()
            print("LED: OFF")
    
    # Toggle on touch
    touch.when_pressed = toggle_led
    
    try:
        signal.pause()
    except KeyboardInterrupt:
        pass
    finally:
        touch.close()
        led.close()

def touch_dimmer():
    """Touch-controlled LED dimmer"""
    print("\n=== Touch Dimmer ===")
    print("Hold touch to increase brightness")
    print("Release and touch again to decrease")
    print("Press Ctrl+C to exit")
    
    touch = Button(TOUCH_PIN, pull_up=False)
    
    try:
        led = PWMLED(LED_PIN)
        has_led = True
    except:
        has_led = False
        print("Note: No PWM LED connected")
    
    # Dimmer state
    brightness = 0.0
    direction = 1  # 1 = increasing, -1 = decreasing
    touch_start = None
    
    try:
        while True:
            if touch.is_pressed:
                if touch_start is None:
                    touch_start = time.time()
                
                # Adjust brightness while touched
                brightness += direction * 0.02
                
                # Reverse at limits
                if brightness >= 1.0:
                    brightness = 1.0
                    direction = -1
                elif brightness <= 0.0:
                    brightness = 0.0
                    direction = 1
                
                if has_led:
                    led.value = brightness
                
                # Visual feedback
                bar_length = int(brightness * 20)
                bar = '█' * bar_length + '░' * (20 - bar_length)
                print(f"\rBrightness: [{bar}] {brightness*100:3.0f}%", end='')
                
            else:
                if touch_start is not None:
                    # Touch ended
                    touch_duration = time.time() - touch_start
                    print(f"\nTouch duration: {touch_duration:.1f}s")
                    touch_start = None
            
            time.sleep(0.02)
    
    except KeyboardInterrupt:
        pass
    finally:
        touch.close()
        if has_led:
            led.close()

def touch_piano():
    """Multi-touch piano keyboard"""
    print("\n=== Touch Piano ===")
    print("Touch sensors to play notes")
    print("Press Ctrl+C to exit")
    
    # Initialize touch sensors
    touches = {}
    note_map = {}
    note_list = list(NOTES.items())
    
    for i, (name, pin) in enumerate(TOUCH_PINS.items()):
        try:
            touches[name] = Button(pin, pull_up=False)
            if i < len(note_list):
                note_map[name] = note_list[i]
                print(f"{name} -> {note_list[i][0]}")
        except:
            print(f"{name}: Not connected")
    
    if not touches:
        print("No touch sensors available!")
        return
    
    try:
        buzzer = TonalBuzzer(BUZZER_PIN)
        has_buzzer = True
    except:
        has_buzzer = False
        print("Note: No buzzer for audio output")
    
    # Track playing notes
    playing = {}
    
    def start_note(sensor_name):
        if sensor_name in note_map:
            note_name, frequency = note_map[sensor_name]
            playing[sensor_name] = note_name
            print(f"\nPlaying: {note_name} ({frequency:.1f}Hz)")
            if has_buzzer:
                buzzer.play(frequency)
    
    def stop_note(sensor_name):
        if sensor_name in playing:
            print(f"Released: {playing[sensor_name]}")
            del playing[sensor_name]
            if has_buzzer and not playing:  # No other notes playing
                buzzer.stop()
    
    # Set up handlers
    for name, touch in touches.items():
        touch.when_pressed = lambda n=name: start_note(n)
        touch.when_released = lambda n=name: stop_note(n)
    
    try:
        print("\nTouch piano ready!")
        signal.pause()
    
    except KeyboardInterrupt:
        pass
    finally:
        for touch in touches.values():
            touch.close()
        if has_buzzer:
            buzzer.close()

def gesture_recognition():
    """Touch gesture recognition"""
    print("\n=== Touch Gesture Recognition ===")
    print("Perform gestures: tap, double-tap, long press")
    print("Press Ctrl+C to exit")
    
    touch = Button(TOUCH_PIN, pull_up=False)
    
    # Gesture parameters
    DOUBLE_TAP_TIME = 0.5  # Max time between taps
    LONG_PRESS_TIME = 1.0  # Min time for long press
    
    # Tracking variables
    last_press_time = 0
    press_start_time = None
    tap_count = 0
    
    def on_press():
        nonlocal press_start_time, tap_count, last_press_time
        current_time = time.time()
        press_start_time = current_time
        
        # Check for double tap
        if current_time - last_press_time < DOUBLE_TAP_TIME:
            tap_count += 1
        else:
            tap_count = 1
        
        last_press_time = current_time
    
    def on_release():
        nonlocal press_start_time
        if press_start_time is None:
            return
        
        press_duration = time.time() - press_start_time
        press_start_time = None
        
        if press_duration >= LONG_PRESS_TIME:
            print("\nGesture: LONG PRESS")
            tap_count = 0
        elif tap_count == 2:
            print("\nGesture: DOUBLE TAP")
            tap_count = 0
        elif tap_count == 1:
            # Wait a bit to see if it's a double tap
            time.sleep(DOUBLE_TAP_TIME)
            if tap_count == 1:  # Still just one tap
                print("\nGesture: TAP")
                tap_count = 0
    
    touch.when_pressed = on_press
    touch.when_released = on_release
    
    try:
        print("Ready for gestures...")
        signal.pause()
    
    except KeyboardInterrupt:
        pass
    finally:
        touch.close()

def touch_slider():
    """Simulate slider control with multiple touch points"""
    print("\n=== Touch Slider ===")
    print("Touch multiple sensors to simulate slider")
    print("Press Ctrl+C to exit")
    
    # Initialize sensors
    sensors = []
    for i, (name, pin) in enumerate(list(TOUCH_PINS.items())[:4]):
        try:
            sensor = Button(pin, pull_up=False)
            sensors.append((i, name, sensor))
            print(f"Position {i}: {name}")
        except:
            pass
    
    if len(sensors) < 2:
        print("Need at least 2 touch sensors for slider!")
        return
    
    try:
        led = PWMLED(LED_PIN)
        has_led = True
    except:
        has_led = False
    
    slider_value = 0
    
    try:
        while True:
            # Find highest touched position
            touched_positions = [i for i, _, sensor in sensors if sensor.is_pressed]
            
            if touched_positions:
                # Use highest position
                position = max(touched_positions)
                slider_value = position / (len(sensors) - 1)
                
                # Update LED
                if has_led:
                    led.value = slider_value
                
                # Visual display
                visual = ""
                for i, _, _ in sensors:
                    if i in touched_positions:
                        visual += "█"
                    else:
                        visual += "░"
                
                print(f"\rSlider: [{visual}] Value: {slider_value*100:3.0f}%", end='')
            else:
                print(f"\rSlider: [░░░░] Value: {slider_value*100:3.0f}%", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        for _, _, sensor in sensors:
            sensor.close()
        if has_led:
            led.close()

def touch_pattern_lock():
    """Pattern lock using touch sensors"""
    print("\n=== Touch Pattern Lock ===")
    print("Enter pattern: 1-2-3-4 to unlock")
    print("Touch sensors in correct sequence")
    print("Press Ctrl+C to exit")
    
    # Initialize sensors
    sensors = {}
    sensor_numbers = {}
    
    for i, (name, pin) in enumerate(list(TOUCH_PINS.items())[:4], 1):
        try:
            sensors[name] = Button(pin, pull_up=False)
            sensor_numbers[name] = i
            print(f"Sensor {i}: {name}")
        except:
            pass
    
    if len(sensors) < 4:
        print("Need 4 touch sensors for pattern lock!")
        return
    
    # Lock configuration
    correct_pattern = [1, 2, 3, 4]
    entered_pattern = []
    last_touch_time = 0
    locked = True
    
    def touch_detected(sensor_name):
        nonlocal entered_pattern, last_touch_time, locked
        
        if not locked:
            return
        
        current_time = time.time()
        
        # Reset pattern if too much time passed
        if current_time - last_touch_time > 3.0:
            entered_pattern = []
        
        # Add to pattern
        number = sensor_numbers[sensor_name]
        entered_pattern.append(number)
        last_touch_time = current_time
        
        print(f"\nEntered: {entered_pattern}")
        
        # Check pattern
        if len(entered_pattern) == len(correct_pattern):
            if entered_pattern == correct_pattern:
                print("\n✅ UNLOCKED!")
                locked = False
                # Auto-lock after 5 seconds
                time.sleep(5)
                locked = True
                print("\n🔒 LOCKED")
            else:
                print("\n❌ INCORRECT PATTERN!")
            entered_pattern = []
    
    # Set up handlers
    for name, sensor in sensors.items():
        sensor.when_pressed = lambda n=name: touch_detected(n)
    
    try:
        print("\nSystem LOCKED")
        signal.pause()
    
    except KeyboardInterrupt:
        pass
    finally:
        for sensor in sensors.values():
            sensor.close()

def proximity_detection():
    """Detect proximity without direct touch"""
    print("\n=== Proximity Detection ===")
    print("Some capacitive sensors detect proximity")
    print("Move hand near sensor")
    print("Press Ctrl+C to exit")
    
    touch = Button(TOUCH_PIN, pull_up=False)
    
    # Proximity tracking
    proximity_samples = []
    max_proximity = 0
    
    try:
        while True:
            # Sample sensor rapidly
            detections = 0
            sample_start = time.time()
            
            while time.time() - sample_start < 0.1:  # 100ms window
                if touch.is_pressed:
                    detections += 1
                time.sleep(0.001)
            
            # Calculate proximity (more detections = closer)
            proximity = min(100, detections)
            proximity_samples.append(proximity)
            if len(proximity_samples) > 10:
                proximity_samples.pop(0)
            
            # Average for stability
            avg_proximity = statistics.mean(proximity_samples)
            max_proximity = max(max_proximity, avg_proximity)
            
            # Determine level
            if avg_proximity == 0:
                level = "No detection"
                bar_char = " "
            elif avg_proximity < 20:
                level = "Far"
                bar_char = "░"
            elif avg_proximity < 50:
                level = "Near"
                bar_char = "▒"
            elif avg_proximity < 80:
                level = "Very near"
                bar_char = "▓"
            else:
                level = "Touching"
                bar_char = "█"
            
            # Visual display
            bar_length = int(avg_proximity / 5)
            bar = bar_char * bar_length + " " * (20 - bar_length)
            
            print(f"\rProximity: {level:12s} [{bar}] {avg_proximity:3.0f}% (Max: {max_proximity:3.0f}%)", end='')
            
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        print(f"\n\nMaximum proximity: {max_proximity:.0f}%")
    finally:
        touch.close()

def touch_response_time():
    """Measure touch response time game"""
    print("\n=== Touch Response Time ===")
    print("Touch as quickly as possible when prompted!")
    print("Press Ctrl+C to exit")
    
    touch = Button(TOUCH_PIN, pull_up=False)
    led = LED(LED_PIN)
    
    scores = []
    
    try:
        for round_num in range(5):
            print(f"\n\nRound {round_num + 1}/5")
            print("Get ready...")
            
            # Random delay
            import random
            delay = random.uniform(2, 5)
            time.sleep(delay)
            
            # Signal to touch
            print("TOUCH NOW!")
            led.on()
            start_time = time.time()
            
            # Wait for touch
            while not touch.is_pressed:
                if time.time() - start_time > 5.0:
                    print("Too slow!")
                    break
                time.sleep(0.001)
            
            if touch.is_pressed:
                response_time = time.time() - start_time
                scores.append(response_time)
                print(f"Response time: {response_time*1000:.0f}ms")
                
                if response_time < 0.3:
                    print("Excellent!")
                elif response_time < 0.5:
                    print("Good!")
                else:
                    print("Try to be faster!")
            
            led.off()
            
            # Wait for release
            while touch.is_pressed:
                time.sleep(0.01)
            
            if round_num < 4:
                time.sleep(1)
        
        # Summary
        if scores:
            avg_time = statistics.mean(scores)
            best_time = min(scores)
            print(f"\n\n--- Results ---")
            print(f"Average: {avg_time*1000:.0f}ms")
            print(f"Best: {best_time*1000:.0f}ms")
    
    except KeyboardInterrupt:
        pass
    finally:
        touch.close()
        led.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Touch Switch Examples")
    print("====================")
    print(f"Touch Sensor GPIO: {TOUCH_PIN}")
    print(f"LED GPIO: {LED_PIN} (optional)")
    print(f"Buzzer GPIO: {BUZZER_PIN} (optional)")
    print("\nNote: Touch sensors output HIGH when touched")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic touch detection")
        print("2. Touch toggle LED")
        print("3. Touch dimmer")
        print("4. Touch piano")
        print("5. Gesture recognition")
        print("6. Touch slider")
        print("7. Pattern lock")
        print("8. Proximity detection")
        print("9. Response time game")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '1':
            basic_touch_detection()
        elif choice == '2':
            touch_toggle_led()
        elif choice == '3':
            touch_dimmer()
        elif choice == '4':
            touch_piano()
        elif choice == '5':
            gesture_recognition()
        elif choice == '6':
            touch_slider()
        elif choice == '7':
            touch_pattern_lock()
        elif choice == '8':
            proximity_detection()
        elif choice == '9':
            touch_response_time()
        elif choice == '0':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()