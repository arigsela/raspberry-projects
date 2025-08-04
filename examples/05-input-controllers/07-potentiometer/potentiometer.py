#!/usr/bin/env python3
"""
Potentiometer Input Control
Read analog values and control various outputs with a potentiometer
"""

from gpiozero import MCP3008, LED, PWMLED, Buzzer, Servo
import time
import signal
import sys
import math

# ADC Configuration (MCP3008)
POT_CHANNEL = 0  # Potentiometer on channel 0

# Output devices (optional demos)
LED_PIN = 17
BUZZER_PIN = 18
SERVO_PIN = 22

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_reading():
    """Read and display potentiometer values"""
    print("\n=== Basic Potentiometer Reading ===")
    print("Rotate the potentiometer to see values")
    print("Press Ctrl+C to stop")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        
        while True:
            # Read value (0.0 to 1.0)
            value = pot.value
            
            # Convert to different scales
            percentage = value * 100
            raw_adc = int(value * 1023)  # 10-bit ADC
            voltage = value * 3.3  # Assuming 3.3V reference
            
            # Create visual bar
            bar_length = int(value * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            
            # Display
            print(f"\r[{bar}] {percentage:5.1f}% | ADC: {raw_adc:4d} | {voltage:.2f}V", end='')
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure MCP3008 is connected properly")

def led_brightness_control():
    """Control LED brightness with potentiometer"""
    print("\n=== LED Brightness Control ===")
    print("Rotate potentiometer to control LED brightness")
    print("Press Ctrl+C to stop")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        led = PWMLED(LED_PIN)
        
        while True:
            # Direct mapping
            led.value = pot.value
            
            # Display
            brightness = int(pot.value * 100)
            print(f"\rLED Brightness: {brightness}%  ", end='')
            
            time.sleep(0.01)
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            led.close()
        except:
            pass

def servo_position_control():
    """Control servo position with potentiometer"""
    print("\n=== Servo Position Control ===")
    print("Rotate potentiometer to control servo angle")
    print("Press Ctrl+C to stop")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        servo = Servo(SERVO_PIN)
        
        while True:
            # Map potentiometer to servo position (-1 to 1)
            servo_pos = (pot.value * 2) - 1
            servo.value = servo_pos
            
            # Convert to angle (0-180 degrees)
            angle = int(pot.value * 180)
            
            # Display
            bar_pos = int(pot.value * 20)
            bar = '─' * 20
            bar = bar[:bar_pos] + '●' + bar[bar_pos+1:]
            print(f"\rServo: [{bar}] {angle:3d}°", end='')
            
            time.sleep(0.02)
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            servo.close()
        except:
            pass

def sound_frequency_control():
    """Control buzzer frequency with potentiometer"""
    print("\n=== Sound Frequency Control ===")
    print("Rotate potentiometer to control pitch")
    print("Press Ctrl+C to stop")
    
    try:
        from gpiozero import PWMOutputDevice
        pot = MCP3008(channel=POT_CHANNEL)
        buzzer = PWMOutputDevice(BUZZER_PIN)
        
        # Frequency range (Hz)
        MIN_FREQ = 100
        MAX_FREQ = 2000
        
        while True:
            if pot.value > 0.01:  # Threshold to avoid noise
                # Map to frequency range
                frequency = MIN_FREQ + (pot.value * (MAX_FREQ - MIN_FREQ))
                
                buzzer.frequency = frequency
                buzzer.value = 0.5  # 50% duty cycle
                
                # Musical note approximation
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                a4_freq = 440
                half_steps = 12 * math.log2(frequency / a4_freq)
                note_index = int(round(half_steps) % 12)
                octave = int(4 + (half_steps + 9) / 12)
                note = f"{note_names[note_index]}{octave}"
                
                print(f"\rFrequency: {frequency:6.1f} Hz ≈ {note:3s}  ", end='')
            else:
                buzzer.value = 0  # Silence
                print(f"\rFrequency: Silent              ", end='')
            
            time.sleep(0.01)
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            buzzer.close()
        except:
            pass

def threshold_detector():
    """Detect when potentiometer crosses thresholds"""
    print("\n=== Threshold Detector ===")
    print("Set thresholds with potentiometer")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        
        # Define thresholds
        thresholds = {
            0.2: "LOW",
            0.4: "MEDIUM-LOW",
            0.6: "MEDIUM",
            0.8: "MEDIUM-HIGH",
            1.0: "HIGH"
        }
        
        current_level = None
        
        while True:
            value = pot.value
            
            # Determine level
            level = "VERY LOW"
            for threshold, name in thresholds.items():
                if value <= threshold:
                    level = name
                    break
            
            # Check for level change
            if level != current_level:
                current_level = level
                print(f"\nLevel changed to: {level} ({value*100:.1f}%)")
            
            # Visual indicator
            bar_length = int(value * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            print(f"\r[{bar}] {value*100:5.1f}%", end='')
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"\nError: {e}")

def data_logger():
    """Log potentiometer values over time"""
    print("\n=== Data Logger ===")
    print("Logging potentiometer values...")
    print("Press Ctrl+C to stop and show summary")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        
        values = []
        start_time = time.time()
        
        while True:
            value = pot.value
            timestamp = time.time() - start_time
            values.append((timestamp, value))
            
            # Display current
            print(f"\rTime: {timestamp:6.1f}s  Value: {value*100:5.1f}%  Samples: {len(values)}", end='')
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nData Summary:")
        print(f"Duration: {values[-1][0]:.1f} seconds")
        print(f"Samples: {len(values)}")
        
        # Calculate statistics
        just_values = [v[1] for v in values]
        avg_value = sum(just_values) / len(just_values)
        min_value = min(just_values)
        max_value = max(just_values)
        
        print(f"Average: {avg_value*100:.1f}%")
        print(f"Minimum: {min_value*100:.1f}%")
        print(f"Maximum: {max_value*100:.1f}%")
        
        # Simple graph
        print("\nValue over time:")
        graph_height = 10
        graph_width = 50
        
        # Downsample if needed
        if len(values) > graph_width:
            step = len(values) // graph_width
            sampled = values[::step]
        else:
            sampled = values
        
        for row in range(graph_height, -1, -1):
            threshold = row / graph_height
            line = ""
            for _, value in sampled:
                if value >= threshold:
                    line += "█"
                else:
                    line += " "
            print(f"{threshold*100:3.0f}% |{line}")
        print("     " + "─" * len(sampled))

def menu_selector():
    """Use potentiometer to select menu items"""
    print("\n=== Menu Selector ===")
    print("Rotate potentiometer to select option")
    print("Current selection will be highlighted")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        
        menu_items = [
            "File", "Edit", "View", "Search", 
            "Tools", "Window", "Help"
        ]
        
        current_selection = -1
        
        while True:
            # Map potentiometer to menu index
            index = int(pot.value * len(menu_items))
            if index >= len(menu_items):
                index = len(menu_items) - 1
            
            # Check if selection changed
            if index != current_selection:
                current_selection = index
                
                # Clear and redraw menu
                print("\033[2J\033[H")  # Clear screen
                print("=== Menu Selector ===")
                print("Rotate potentiometer to select:\n")
                
                for i, item in enumerate(menu_items):
                    if i == index:
                        print(f"  → [{item}] ←")
                    else:
                        print(f"     {item}")
                
                print(f"\nPotentiometer: {pot.value*100:.1f}%")
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"\nError: {e}")

def calibration_mode():
    """Calibrate potentiometer range"""
    print("\n=== Calibration Mode ===")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        
        print("1. Turn potentiometer to MINIMUM position")
        print("   Press Enter when ready...")
        input()
        min_val = pot.value
        print(f"   Minimum recorded: {min_val:.3f}")
        
        print("\n2. Turn potentiometer to MAXIMUM position")
        print("   Press Enter when ready...")
        input()
        max_val = pot.value
        print(f"   Maximum recorded: {max_val:.3f}")
        
        print("\n3. Turn potentiometer to CENTER position")
        print("   Press Enter when ready...")
        input()
        center_val = pot.value
        print(f"   Center recorded: {center_val:.3f}")
        
        # Calculate calibration
        range_val = max_val - min_val
        print(f"\nCalibration Results:")
        print(f"  Usable range: {range_val:.3f} ({range_val*100:.1f}%)")
        print(f"  Dead zone at minimum: {min_val:.3f}")
        print(f"  Dead zone at maximum: {1-max_val:.3f}")
        print(f"  Center accuracy: {abs(center_val - 0.5)*100:.1f}% off")
        
        # Test calibration
        print("\nTesting calibration (press Ctrl+C to exit):")
        while True:
            raw = pot.value
            # Apply calibration
            calibrated = (raw - min_val) / range_val
            calibrated = max(0, min(1, calibrated))  # Clamp
            
            print(f"\rRaw: {raw:.3f}  Calibrated: {calibrated:.3f} ({calibrated*100:5.1f}%)", end='')
            time.sleep(0.05)
    
    except Exception as e:
        print(f"\nError: {e}")

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Potentiometer Control Examples")
    print("=============================")
    print("Using MCP3008 ADC")
    print(f"Potentiometer on channel: {POT_CHANNEL}")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic reading and display")
        print("2. LED brightness control")
        print("3. Servo position control")
        print("4. Sound frequency control")
        print("5. Threshold detector")
        print("6. Data logger")
        print("7. Menu selector")
        print("8. Calibration mode")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            basic_reading()
        elif choice == '2':
            led_brightness_control()
        elif choice == '3':
            servo_position_control()
        elif choice == '4':
            sound_frequency_control()
        elif choice == '5':
            threshold_detector()
        elif choice == '6':
            data_logger()
        elif choice == '7':
            menu_selector()
        elif choice == '8':
            calibration_mode()
        elif choice == '9':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()