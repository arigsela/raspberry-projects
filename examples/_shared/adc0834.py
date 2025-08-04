#!/usr/bin/env python3
"""
ADC0834 - 4-Channel 8-bit Analog-to-Digital Converter
Provides interface for reading analog values using ADC0834 chip
"""

from gpiozero import OutputDevice, InputDevice
from time import sleep

class ADC0834:
    """
    Interface for ADC0834 4-channel 8-bit ADC
    
    The ADC0834 uses a serial interface to communicate:
    - CS: Chip Select (active low)
    - CLK: Clock signal
    - DI: Data Input (to ADC)
    - DO: Data Output (from ADC)
    """
    
    def __init__(self, cs_pin=17, clk_pin=18, di_pin=27, do_pin=22):
        """
        Initialize ADC0834 interface
        
        Args:
            cs_pin: Chip Select pin (default: GPIO17)
            clk_pin: Clock pin (default: GPIO18)
            di_pin: Data Input pin (default: GPIO27)
            do_pin: Data Output pin (default: GPIO22)
        """
        self.cs = OutputDevice(cs_pin)
        self.clk = OutputDevice(clk_pin)
        self.di = OutputDevice(di_pin)
        self.do = InputDevice(do_pin)
        
        # Initialize pins
        self.cs.on()  # CS is active low, so high = inactive
        self.clk.off()
        self.di.off()
    
    def read_channel(self, channel):
        """
        Read analog value from specified channel
        
        Args:
            channel: Channel number (0-3)
            
        Returns:
            8-bit value (0-255)
        """
        if not 0 <= channel <= 3:
            raise ValueError("Channel must be 0-3")
        
        # Start bit and single-ended mode
        # Command format: Start(1) + SGL/DIF(1) + D1 + D0
        # For single-ended: SGL/DIF = 1
        # Channel select: D1 D0
        # Channel 0: 0 0
        # Channel 1: 0 1
        # Channel 2: 1 0
        # Channel 3: 1 1
        
        # Construct command
        cmd = 0x18  # Start bit (1) + Single-ended (1) + padding
        cmd |= (channel & 0x03) << 1  # Add channel bits
        
        # Begin communication
        self.cs.off()  # Select chip
        
        # Send command bits (5 bits total)
        for i in range(5):
            if cmd & 0x10:  # Check MSB
                self.di.on()
            else:
                self.di.off()
            
            # Clock pulse
            self.clk.on()
            sleep(0.000002)  # 2 microseconds
            self.clk.off()
            sleep(0.000002)
            
            cmd <<= 1  # Shift to next bit
        
        # Read data
        data = 0
        
        # Skip null bit
        self.clk.on()
        sleep(0.000002)
        self.clk.off()
        sleep(0.000002)
        
        # Read 8 data bits
        for i in range(8):
            self.clk.on()
            sleep(0.000002)
            
            data <<= 1
            if self.do.is_active:
                data |= 1
            
            self.clk.off()
            sleep(0.000002)
        
        # Deselect chip
        self.cs.on()
        
        return data
    
    def read_voltage(self, channel, vref=3.3):
        """
        Read analog voltage from specified channel
        
        Args:
            channel: Channel number (0-3)
            vref: Reference voltage (default: 3.3V)
            
        Returns:
            Voltage value (0 to vref)
        """
        raw_value = self.read_channel(channel)
        voltage = (raw_value / 255.0) * vref
        return voltage
    
    def read_percentage(self, channel):
        """
        Read analog value as percentage
        
        Args:
            channel: Channel number (0-3)
            
        Returns:
            Percentage (0-100)
        """
        raw_value = self.read_channel(channel)
        percentage = (raw_value / 255.0) * 100
        return percentage
    
    def read_all_channels(self):
        """
        Read all 4 channels
        
        Returns:
            List of 4 values (0-255)
        """
        values = []
        for channel in range(4):
            values.append(self.read_channel(channel))
        return values
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.cs.close()
        self.clk.close()
        self.di.close()
        self.do.close()


# Example usage and test code
if __name__ == "__main__":
    # Test the ADC0834 module
    print("Testing ADC0834 module...")
    
    # Create ADC instance
    adc = ADC0834()
    
    try:
        print("\nReading all channels 5 times:")
        print("Channel:  CH0   CH1   CH2   CH3")
        print("-" * 35)
        
        for i in range(5):
            values = adc.read_all_channels()
            print(f"Reading {i+1}: ", end="")
            for val in values:
                print(f"{val:3d}  ", end="")
            print()
            sleep(0.5)
        
        print("\nReading voltages (assuming 3.3V reference):")
        for channel in range(4):
            voltage = adc.read_voltage(channel)
            print(f"Channel {channel}: {voltage:.2f}V")
        
        print("\nReading as percentages:")
        for channel in range(4):
            percentage = adc.read_percentage(channel)
            print(f"Channel {channel}: {percentage:.1f}%")
    
    except KeyboardInterrupt:
        print("\nTest interrupted")
    finally:
        adc.cleanup()
        print("Cleanup complete")