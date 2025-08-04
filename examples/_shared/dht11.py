#!/usr/bin/env python3
"""
DHT11 Temperature and Humidity Sensor Driver
Implements the single-wire protocol for DHT11 sensor
"""

import time
import RPi.GPIO as GPIO

class DHT11:
    """
    Driver for DHT11 Temperature and Humidity Sensor
    
    Uses a custom single-wire protocol for communication
    Returns temperature in Celsius and relative humidity percentage
    """
    
    def __init__(self, pin):
        """
        Initialize DHT11 sensor
        
        Args:
            pin: GPIO pin number (BCM numbering)
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Sensor timing constants (in seconds)
        self.TIMEOUT = 0.00001  # 10 microseconds
        self.INIT_WAIT = 0.02   # 20 milliseconds
        
    def _send_start_signal(self):
        """Send start signal to DHT11"""
        # Set pin as output and pull low
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(self.INIT_WAIT)  # Hold for at least 18ms
        
        # Pull high briefly
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.00002)  # 20-40 microseconds
        
        # Switch to input mode
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def _wait_for_level(self, level, timeout=TIMEOUT):
        """
        Wait for pin to reach specified level
        
        Args:
            level: GPIO.HIGH or GPIO.LOW
            timeout: Maximum wait time
            
        Returns:
            Time waited in microseconds, or -1 if timeout
        """
        start_time = time.time()
        
        while GPIO.input(self.pin) != level:
            if time.time() - start_time > timeout:
                return -1
        
        return int((time.time() - start_time) * 1000000)
    
    def _read_bits(self):
        """
        Read 40 bits from DHT11
        
        Returns:
            List of 40 bits or None if error
        """
        bits = []
        
        # Wait for DHT11 response
        # Expect LOW for ~80us, then HIGH for ~80us
        if self._wait_for_level(GPIO.LOW, 0.0001) < 0:
            return None
        if self._wait_for_level(GPIO.HIGH, 0.0001) < 0:
            return None
        if self._wait_for_level(GPIO.LOW, 0.0001) < 0:
            return None
        
        # Read 40 bits
        for i in range(40):
            # Each bit starts with 50us LOW
            if self._wait_for_level(GPIO.HIGH, 0.0001) < 0:
                return None
            
            # HIGH duration determines bit value
            # 26-28us = 0, 70us = 1
            high_time = self._wait_for_level(GPIO.LOW, 0.0001)
            
            if high_time < 0:
                return None
            elif high_time > 50:  # Approximately 70us
                bits.append(1)
            else:  # Approximately 26-28us
                bits.append(0)
        
        return bits
    
    def _bits_to_bytes(self, bits):
        """
        Convert 40 bits to 5 bytes
        
        Args:
            bits: List of 40 bits
            
        Returns:
            List of 5 bytes
        """
        bytes_data = []
        
        for i in range(0, 40, 8):
            byte = 0
            for j in range(8):
                byte = (byte << 1) | bits[i + j]
            bytes_data.append(byte)
        
        return bytes_data
    
    def _verify_checksum(self, data):
        """
        Verify data checksum
        
        Args:
            data: List of 5 bytes
            
        Returns:
            True if checksum valid
        """
        return data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF)
    
    def read(self, retries=3):
        """
        Read temperature and humidity from sensor
        
        Args:
            retries: Number of read attempts
            
        Returns:
            Tuple of (humidity, temperature) or (None, None) if error
        """
        for attempt in range(retries):
            # Send start signal
            self._send_start_signal()
            
            # Read response bits
            bits = self._read_bits()
            if bits is None:
                time.sleep(2)  # DHT11 needs 2 seconds between reads
                continue
            
            # Convert to bytes
            data = self._bits_to_bytes(bits)
            
            # Verify checksum
            if not self._verify_checksum(data):
                time.sleep(2)
                continue
            
            # Extract values
            humidity = data[0] + data[1] * 0.1
            temperature = data[2] + data[3] * 0.1
            
            # DHT11 doesn't support decimal, so ignore decimal bytes
            humidity = float(data[0])
            temperature = float(data[2])
            
            return humidity, temperature
        
        return None, None
    
    def read_retry(self, retries=15, delay=2):
        """
        Read with extended retry logic
        
        Args:
            retries: Maximum number of attempts
            delay: Delay between attempts (seconds)
            
        Returns:
            Tuple of (humidity, temperature) or (None, None)
        """
        for attempt in range(retries):
            humidity, temperature = self.read()
            
            if humidity is not None and temperature is not None:
                # Sanity check values
                if 0 <= humidity <= 100 and -40 <= temperature <= 80:
                    return humidity, temperature
            
            if attempt < retries - 1:
                time.sleep(delay)
        
        return None, None
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup(self.pin)


# Simplified high-level interface
def read_dht11(pin, retries=15):
    """
    Simple function to read DHT11 sensor
    
    Args:
        pin: GPIO pin number
        retries: Number of read attempts
        
    Returns:
        Tuple of (humidity, temperature) or (None, None)
    """
    sensor = DHT11(pin)
    try:
        return sensor.read_retry(retries=retries)
    finally:
        sensor.cleanup()


# Example usage and test code
if __name__ == "__main__":
    import sys
    
    # Test on GPIO17 by default
    test_pin = 17
    if len(sys.argv) > 1:
        test_pin = int(sys.argv[1])
    
    print(f"Testing DHT11 sensor on GPIO{test_pin}")
    print("Press Ctrl+C to stop\n")
    
    sensor = DHT11(test_pin)
    
    try:
        while True:
            print("Reading sensor...", end='', flush=True)
            
            humidity, temperature = sensor.read_retry()
            
            if humidity is not None and temperature is not None:
                print(f"\rTemperature: {temperature:.1f}°C  Humidity: {humidity:.1f}%  ")
                
                # Comfort level indicator
                if 20 <= temperature <= 26 and 40 <= humidity <= 60:
                    print("Comfort: Optimal")
                elif temperature > 28:
                    print("Comfort: Too hot")
                elif temperature < 18:
                    print("Comfort: Too cold")
                elif humidity > 70:
                    print("Comfort: Too humid")
                elif humidity < 30:
                    print("Comfort: Too dry")
                else:
                    print("Comfort: Fair")
            else:
                print("\rFailed to read sensor. Check wiring!")
            
            time.sleep(3)  # DHT11 can only be read every 2+ seconds
            
    except KeyboardInterrupt:
        print("\n\nTest stopped")
    finally:
        sensor.cleanup()
        print("Cleanup complete")