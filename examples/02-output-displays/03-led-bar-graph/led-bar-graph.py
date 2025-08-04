#!/usr/bin/env python3
"""
LED Bar Graph Display
Display data visually using a 10-segment LED bar graph
"""

from gpiozero import LEDBarGraph, MCP3008
import time
import math
import signal
import sys

# GPIO Pin Configuration (10 LEDs)
LED_PINS = [17, 18, 27, 22, 23, 24, 25, 8, 7, 12]

# For potentiometer input (optional)
POT_CHANNEL = 0  # MCP3008 channel 0

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\nExiting...")
    sys.exit(0)

def basic_bar_graph_demo():
    """Basic bar graph demonstration"""
    print("\n=== Basic Bar Graph Demo ===")
    print("Lighting up LEDs in sequence")
    
    # Create bar graph object
    graph = LEDBarGraph(*LED_PINS)
    
    try:
        # Light up one by one
        print("Sequential lighting...")
        for i in range(11):
            graph.value = i / 10
            time.sleep(0.2)
        
        # Light down
        for i in range(10, -1, -1):
            graph.value = i / 10
            time.sleep(0.2)
        
        # Pulse effect
        print("Pulse effect...")
        for _ in range(3):
            graph.pulse(fade_in_time=1, fade_out_time=1)
            time.sleep(2)
        
    finally:
        graph.close()

def level_meter_demo():
    """VU meter style level display"""
    print("\n=== Level Meter Demo ===")
    print("Simulating audio levels")
    
    graph = LEDBarGraph(*LED_PINS)
    
    try:
        for i in range(100):
            # Simulate audio level with sine wave
            level = abs(math.sin(i * 0.1))
            # Add some random variation
            import random
            level += random.uniform(-0.1, 0.1)
            level = max(0, min(1, level))  # Clamp to 0-1
            
            graph.value = level
            time.sleep(0.05)
            
    finally:
        graph.close()

def potentiometer_control():
    """Control bar graph with potentiometer"""
    print("\n=== Potentiometer Control ===")
    print("Connect potentiometer to MCP3008 channel 0")
    print("Rotate potentiometer to control bar graph")
    print("Press Ctrl+C to exit")
    
    try:
        pot = MCP3008(channel=POT_CHANNEL)
        graph = LEDBarGraph(*LED_PINS)
        
        while True:
            # Read potentiometer value (0-1)
            graph.value = pot.value
            time.sleep(0.01)
            
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MCP3008 is connected properly")
    finally:
        try:
            pot.close()
            graph.close()
        except:
            pass

def temperature_display():
    """Display temperature on bar graph"""
    print("\n=== Temperature Display ===")
    print("Simulating temperature readings")
    print("0 LEDs = 0°C, 10 LEDs = 40°C")
    
    graph = LEDBarGraph(*LED_PINS)
    
    try:
        base_temp = 20  # Starting temperature
        
        for i in range(50):
            # Simulate temperature changes
            temp_change = math.sin(i * 0.1) * 5
            current_temp = base_temp + temp_change
            
            # Convert temperature to bar graph value
            # 0°C = 0.0, 40°C = 1.0
            graph_value = current_temp / 40
            graph_value = max(0, min(1, graph_value))
            
            graph.value = graph_value
            
            # Show temperature
            lit_leds = int(graph_value * 10)
            print(f"\rTemp: {current_temp:.1f}°C  LEDs: {'█' * lit_leds}{'░' * (10 - lit_leds)}", end='')
            
            time.sleep(0.2)
        
        print()  # New line after loop
        
    finally:
        graph.close()

def battery_indicator():
    """Simulate battery level indicator"""
    print("\n=== Battery Level Indicator ===")
    print("Simulating battery discharge")
    
    graph = LEDBarGraph(*LED_PINS)
    
    # Define battery levels and colors
    # In real application, you might use RGB LEDs
    levels = [
        (1.0, "100% - Full"),
        (0.8, "80% - Good"),
        (0.6, "60% - OK"),
        (0.4, "40% - Low"),
        (0.2, "20% - Critical"),
        (0.1, "10% - Very Low"),
    ]
    
    try:
        # Simulate battery discharge
        for level, status in levels:
            print(f"Battery: {status}")
            graph.value = level
            
            # Blink if critical
            if level <= 0.2:
                for _ in range(3):
                    time.sleep(0.2)
                    graph.off()
                    time.sleep(0.2)
                    graph.value = level
            else:
                time.sleep(2)
        
        # Battery empty
        print("Battery: 0% - Empty")
        graph.off()
        
    finally:
        graph.close()

def network_activity():
    """Simulate network activity indicator"""
    print("\n=== Network Activity Monitor ===")
    print("Simulating network traffic")
    
    graph = LEDBarGraph(*LED_PINS)
    
    try:
        import random
        
        for _ in range(50):
            # Simulate random network activity
            activity = random.random()
            
            # Quick flash for activity
            graph.value = activity
            time.sleep(0.05)
            
            # Decay
            while activity > 0:
                activity *= 0.8
                graph.value = activity
                time.sleep(0.05)
        
    finally:
        graph.close()

def custom_patterns():
    """Create custom LED patterns"""
    print("\n=== Custom Patterns ===")
    
    graph = LEDBarGraph(*LED_PINS)
    
    patterns = [
        # Knight Rider effect
        ("Knight Rider", [
            0b0000000001,
            0b0000000010,
            0b0000000100,
            0b0000001000,
            0b0000010000,
            0b0000100000,
            0b0001000000,
            0b0010000000,
            0b0100000000,
            0b1000000000,
            0b0100000000,
            0b0010000000,
            0b0001000000,
            0b0000100000,
            0b0000010000,
            0b0000001000,
            0b0000000100,
            0b0000000010,
        ]),
        # Growing bar
        ("Growing", [
            0b0000000001,
            0b0000000011,
            0b0000000111,
            0b0000001111,
            0b0000011111,
            0b0000111111,
            0b0001111111,
            0b0011111111,
            0b0111111111,
            0b1111111111,
        ]),
        # Center out
        ("Center Out", [
            0b0000110000,
            0b0001111000,
            0b0011111100,
            0b0111111110,
            0b1111111111,
        ]),
    ]
    
    try:
        for name, pattern in patterns:
            print(f"\nPattern: {name}")
            
            # Play pattern 3 times
            for _ in range(3):
                for bits in pattern:
                    # Set individual LEDs based on bit pattern
                    for i in range(10):
                        if bits & (1 << i):
                            graph.leds[i].on()
                        else:
                            graph.leds[i].off()
                    time.sleep(0.05)
            
            graph.off()
            time.sleep(0.5)
        
    finally:
        graph.close()

def main():
    """Main program with menu"""
    signal.signal(signal.SIGINT, signal_handler)
    
    print("LED Bar Graph Examples")
    print("=====================")
    print("Using GPIO pins:", LED_PINS)
    
    while True:
        print("\n\nSelect Demo:")
        print("1. Basic bar graph demo")
        print("2. Level meter (VU meter)")
        print("3. Potentiometer control (needs MCP3008)")
        print("4. Temperature display")
        print("5. Battery indicator")
        print("6. Network activity")
        print("7. Custom patterns")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == '1':
            basic_bar_graph_demo()
        elif choice == '2':
            level_meter_demo()
        elif choice == '3':
            potentiometer_control()
        elif choice == '4':
            temperature_display()
        elif choice == '5':
            battery_indicator()
        elif choice == '6':
            network_activity()
        elif choice == '7':
            custom_patterns()
        elif choice == '8':
            break
        else:
            print("Invalid choice")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()