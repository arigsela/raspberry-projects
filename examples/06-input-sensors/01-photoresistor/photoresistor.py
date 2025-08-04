#!/usr/bin/env python3
"""
Photoresistor Light Sensor
Detect and measure ambient light levels for automatic lighting and monitoring
"""

from gpiozero import MCP3008, LED, PWMLED, Buzzer
import time
import signal
import sys
import math
from datetime import datetime

# ADC Configuration
LDR_CHANNEL = 0  # Photoresistor on MCP3008 channel 0

# Output devices for demos
LED_PIN = 17
LED_BAR_PINS = [18, 23, 24, 25, 8, 7, 12, 16, 20, 21]  # 10 LEDs for bar graph
BUZZER_PIN = 22

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_light_reading():
    """Read and display light levels"""
    print("\n=== Basic Light Level Reading ===")
    print("Cover/uncover the photoresistor to see changes")
    print("Press Ctrl+C to stop")
    
    try:
        ldr = MCP3008(channel=LDR_CHANNEL)
        
        # Calibration values (adjust based on your setup)
        # Higher value = more light
        DARK_THRESHOLD = 0.1
        DIM_THRESHOLD = 0.3
        NORMAL_THRESHOLD = 0.6
        BRIGHT_THRESHOLD = 0.8
        
        while True:
            # Read light level (0.0 = dark, 1.0 = bright)
            light_level = ldr.value
            
            # Determine light condition
            if light_level < DARK_THRESHOLD:
                condition = "DARK    "
            elif light_level < DIM_THRESHOLD:
                condition = "DIM     "
            elif light_level < NORMAL_THRESHOLD:
                condition = "NORMAL  "
            elif light_level < BRIGHT_THRESHOLD:
                condition = "BRIGHT  "
            else:
                condition = "VERY BRIGHT"
            
            # Calculate approximate lux (rough estimation)
            # This requires calibration with a lux meter
            resistance = (1 - light_level) * 10000  # Assuming 10k resistor
            lux = 500 / (resistance / 1000) if resistance > 0 else 9999
            
            # Visual bar
            bar_length = int(light_level * 40)
            bar = '█' * bar_length + '░' * (40 - bar_length)
            
            # Display
            print(f"\r[{bar}] {light_level*100:5.1f}% | {condition} | ~{lux:4.0f} lux", end='')
            
            time.sleep(0.1)
    
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure MCP3008 is connected properly")

def automatic_night_light():
    """Automatically control LED based on ambient light"""
    print("\n=== Automatic Night Light ===")
    print("LED will turn on in darkness")
    print("Press Ctrl+C to stop")
    
    try:
        ldr = MCP3008(channel=LDR_CHANNEL)
        led = PWMLED(LED_PIN)
        
        # Thresholds
        LIGHT_ON_THRESHOLD = 0.2   # Turn on when darker than this
        LIGHT_OFF_THRESHOLD = 0.3  # Turn off when brighter than this
        
        # State
        light_is_on = False
        
        while True:
            light_level = ldr.value
            
            # Hysteresis to prevent flickering
            if not light_is_on and light_level < LIGHT_ON_THRESHOLD:
                # Turn on light (fade in)
                led.pulse(fade_in_time=1, fade_out_time=0, n=1)
                led.on()
                light_is_on = True
                print(f"\n💡 Light ON (ambient: {light_level*100:.1f}%)")
            
            elif light_is_on and light_level > LIGHT_OFF_THRESHOLD:
                # Turn off light (fade out)
                led.pulse(fade_in_time=0, fade_out_time=1, n=1)
                led.off()
                light_is_on = False
                print(f"\n🌑 Light OFF (ambient: {light_level*100:.1f}%)")
            
            # Adjust brightness inversely to ambient light
            if light_is_on:
                # Dimmer in brighter ambient light
                brightness = 1 - (light_level * 2)
                brightness = max(0.1, min(1, brightness))
                led.value = brightness
            
            # Status display
            status = "ON " if light_is_on else "OFF"
            print(f"\rAmbient: {light_level*100:5.1f}% | Night Light: {status} | Brightness: {led.value*100:3.0f}%", end='')
            
            time.sleep(0.1)
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            led.close()
        except:
            pass

def light_level_alarm():
    """Alert when light levels cross thresholds"""
    print("\n=== Light Level Alarm ===")
    print("Alerts for sudden light changes")
    
    try:
        ldr = MCP3008(channel=LDR_CHANNEL)
        buzzer = Buzzer(BUZZER_PIN)
        led = LED(LED_PIN)
        
        # Configuration
        SUDDEN_CHANGE_THRESHOLD = 0.3  # 30% change
        DARKNESS_ALERT = 0.1
        BRIGHTNESS_ALERT = 0.9
        
        last_level = ldr.value
        
        while True:
            current_level = ldr.value
            change = abs(current_level - last_level)
            
            # Check for sudden changes
            if change > SUDDEN_CHANGE_THRESHOLD:
                print(f"\n⚠️  Sudden light change detected! ({last_level*100:.1f}% → {current_level*100:.1f}%)")
                
                # Alert pattern
                for _ in range(3):
                    buzzer.on()
                    led.on()
                    time.sleep(0.1)
                    buzzer.off()
                    led.off()
                    time.sleep(0.1)
            
            # Check extreme levels
            if current_level < DARKNESS_ALERT:
                print(f"\n🌑 DARKNESS ALERT! Light level: {current_level*100:.1f}%")
                buzzer.beep(on_time=0.5, off_time=0.5, n=2)
            
            elif current_level > BRIGHTNESS_ALERT:
                print(f"\n☀️  BRIGHTNESS ALERT! Light level: {current_level*100:.1f}%")
                buzzer.beep(on_time=0.1, off_time=0.1, n=5)
            
            # Update for next iteration
            last_level = current_level
            
            # Display current level
            bar_length = int(current_level * 20)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"\r[{bar}] {current_level*100:5.1f}%", end='')
            
            time.sleep(0.1)
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            buzzer.close()
            led.close()
        except:
            pass

def light_data_logger():
    """Log light levels over time"""
    print("\n=== Light Data Logger ===")
    print("Logging light levels...")
    print("Press Ctrl+C to stop and show analysis")
    
    try:
        ldr = MCP3008(channel=LDR_CHANNEL)
        
        # Data storage
        data = []
        start_time = time.time()
        
        # Sample rate
        SAMPLE_INTERVAL = 1.0  # seconds
        
        while True:
            timestamp = time.time() - start_time
            light_level = ldr.value
            
            data.append({
                'time': timestamp,
                'level': light_level,
                'datetime': datetime.now()
            })
            
            # Display current
            print(f"\rTime: {timestamp:6.1f}s | Light: {light_level*100:5.1f}% | Samples: {len(data)}", end='')
            
            time.sleep(SAMPLE_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\nData Analysis:")
        print("=" * 50)
        
        if data:
            # Calculate statistics
            levels = [d['level'] for d in data]
            avg_level = sum(levels) / len(levels)
            min_level = min(levels)
            max_level = max(levels)
            
            # Find trends
            increasing = sum(1 for i in range(1, len(levels)) if levels[i] > levels[i-1])
            decreasing = sum(1 for i in range(1, len(levels)) if levels[i] < levels[i-1])
            
            print(f"Duration: {data[-1]['time']:.1f} seconds")
            print(f"Samples: {len(data)}")
            print(f"Average light level: {avg_level*100:.1f}%")
            print(f"Minimum: {min_level*100:.1f}%")
            print(f"Maximum: {max_level*100:.1f}%")
            print(f"Range: {(max_level-min_level)*100:.1f}%")
            print(f"Trend: {increasing} increases, {decreasing} decreases")
            
            # Simple ASCII graph
            print("\nLight level over time:")
            graph_height = 10
            graph_width = min(50, len(data))
            
            # Downsample if needed
            if len(data) > graph_width:
                step = len(data) // graph_width
                sampled = data[::step]
            else:
                sampled = data
            
            for row in range(graph_height, -1, -1):
                threshold = row / graph_height
                line = ""
                for point in sampled:
                    if point['level'] >= threshold:
                        line += "█"
                    else:
                        line += " "
                print(f"{threshold*100:3.0f}% |{line}")
            print("     " + "─" * len(sampled))
            print("     Start" + " " * (len(sampled)-9) + "End")

def sunrise_simulator():
    """Simulate sunrise/sunset with LED"""
    print("\n=== Sunrise/Sunset Simulator ===")
    
    try:
        led = PWMLED(LED_PIN)
        
        duration = input("Enter duration in seconds (default 10): ")
        duration = float(duration) if duration else 10.0
        
        print("\nSimulating sunrise...")
        steps = 100
        step_time = duration / steps
        
        # Sunrise (darkness to light)
        for i in range(steps):
            brightness = i / steps
            # Apply curve for more natural transition
            brightness = math.pow(brightness, 2)
            led.value = brightness
            
            # Color temperature simulation (warmer at start/end)
            warmth = 1 - abs(brightness - 0.5) * 2
            
            print(f"\r☀️  Sunrise: {i+1}% | Brightness: {brightness*100:.1f}% | Warmth: {warmth*100:.0f}%", end='')
            time.sleep(step_time)
        
        print("\n\nFull daylight for 3 seconds...")
        time.sleep(3)
        
        print("\nSimulating sunset...")
        # Sunset (light to darkness)
        for i in range(steps):
            brightness = 1 - (i / steps)
            brightness = math.pow(brightness, 2)
            led.value = brightness
            
            warmth = 1 - abs(brightness - 0.5) * 2
            
            print(f"\r🌅 Sunset: {i+1}% | Brightness: {brightness*100:.1f}% | Warmth: {warmth*100:.0f}%", end='')
            time.sleep(step_time)
        
        print("\n\nNight time 🌙")
        led.off()
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            led.close()
        except:
            pass

def light_bar_graph():
    """Display light level on LED bar graph"""
    print("\n=== Light Level Bar Graph ===")
    print("LEDs show current light level")
    
    try:
        from gpiozero import LEDBarGraph
        
        ldr = MCP3008(channel=LDR_CHANNEL)
        graph = LEDBarGraph(*LED_BAR_PINS[:8])  # Use first 8 LEDs
        
        print("Press Ctrl+C to stop")
        
        while True:
            light_level = ldr.value
            
            # Direct mapping
            graph.value = light_level
            
            # Also show numerically
            percentage = light_level * 100
            lit_leds = int(light_level * 8)
            
            print(f"\rLight: {percentage:5.1f}% | LEDs: {'█' * lit_leds}{'░' * (8-lit_leds)}", end='')
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure LED bar graph is connected")
    finally:
        try:
            graph.close()
        except:
            pass

def light_activated_switch():
    """Use light sensor as a switch"""
    print("\n=== Light-Activated Switch ===")
    print("Wave hand over sensor to toggle")
    
    try:
        ldr = MCP3008(channel=LDR_CHANNEL)
        led = LED(LED_PIN)
        
        # Configuration
        TRIGGER_THRESHOLD = 0.3  # Darkness level to trigger
        DEBOUNCE_TIME = 0.5      # Prevent multiple triggers
        
        # State
        led_state = False
        last_trigger = 0
        waiting_for_light = False
        
        print("Ready! Cover sensor to toggle LED")
        
        while True:
            light_level = ldr.value
            current_time = time.time()
            
            # Detect hand wave (darkness then light)
            if not waiting_for_light and light_level < TRIGGER_THRESHOLD:
                waiting_for_light = True
                print(f"\nSensor covered... (light: {light_level*100:.1f}%)")
            
            elif waiting_for_light and light_level > TRIGGER_THRESHOLD * 2:
                # Hand removed, toggle LED
                if current_time - last_trigger > DEBOUNCE_TIME:
                    led_state = not led_state
                    if led_state:
                        led.on()
                        print("LED ON ✓")
                    else:
                        led.off()
                        print("LED OFF")
                    
                    last_trigger = current_time
                waiting_for_light = False
            
            # Status display
            status = "ON " if led_state else "OFF"
            bar_length = int(light_level * 20)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"\r[{bar}] Light: {light_level*100:5.1f}% | LED: {status}", end='')
            
            time.sleep(0.05)
    
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            led.close()
        except:
            pass

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Photoresistor Light Sensor Examples")
    print("==================================")
    print("Using MCP3008 ADC")
    print(f"Photoresistor on channel: {LDR_CHANNEL}")
    
    while True:
        print("\n\nSelect Example:")
        print("1. Basic light level reading")
        print("2. Automatic night light")
        print("3. Light level alarm")
        print("4. Light data logger")
        print("5. Sunrise/sunset simulator")
        print("6. Light bar graph display")
        print("7. Light-activated switch")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_light_reading()
        elif choice == '2':
            automatic_night_light()
        elif choice == '3':
            light_level_alarm()
        elif choice == '4':
            light_data_logger()
        elif choice == '5':
            sunrise_simulator()
        elif choice == '6':
            light_bar_graph()
        elif choice == '7':
            light_activated_switch()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()