# Battery Voltage Monitor

Comprehensive battery monitoring system with real-time voltage measurement, charge level indication, discharge rate calculation, and support for multiple battery chemistries.

## What You'll Learn
- Voltage measurement with ADC
- Voltage divider design for safe measurement
- Battery chemistry characteristics
- Charge level calculation algorithms
- Discharge rate analysis
- Data logging and statistics
- Multi-LED bar graph displays
- Low battery alert systems

## Hardware Requirements
- Raspberry Pi 5
- ADC0834 analog-to-digital converter
- 10x LEDs for battery level bar graph
- 3x Status LEDs (Charging, Low Battery, Critical)
- 2x Push buttons for control
- Buzzer for alerts
- 16x2 LCD display with I2C backpack
- Voltage divider resistors (10kΩ and 3.3kΩ)
- Jumper wires and breadboard
- Current limiting resistors (220Ω for LEDs)
- Pull-up resistors (10kΩ for buttons)
- Battery holder/connector for testing

## Circuit Diagram

```
Battery Voltage Monitor System:
┌─────────────────────────────────────────────────────────────┐
│                  Raspberry Pi 5                            │
│                                                             │
│ ADC0834 (Voltage Measurement):                              │
│ CS ──────────── GPIO5                                      │
│ CLK ─────────── GPIO6                                      │
│ DI ──────────── GPIO16                                     │
│ DO ──────────── GPIO12                                     │
│ CH0 ─────────── Voltage divider output                     │
│                                                             │
│ LED Bar Graph (10 segments):                               │
│ LED1 (10%) ──── GPIO17                                     │
│ LED2 (20%) ──── GPIO18                                     │
│ LED3 (30%) ──── GPIO27                                     │
│ LED4 (40%) ──── GPIO22                                     │
│ LED5 (50%) ──── GPIO23                                     │
│ LED6 (60%) ──── GPIO24                                     │
│ LED7 (70%) ──── GPIO25                                     │
│ LED8 (80%) ──── GPIO8                                      │
│ LED9 (90%) ──── GPIO7                                      │
│ LED10(100%) ─── GPIO1                                      │
│                                                             │
│ Status LEDs:                                                │
│ CHARGING LED ── GPIO19 (Green)                             │
│ LOW BAT LED ─── GPIO20 (Yellow, PWM)                       │
│ CRITICAL LED ── GPIO21 (Red, PWM)                          │
│                                                             │
│ Control Buttons:                                            │
│ MODE BTN ────── GPIO26 (Cycle display/battery type)        │
│ CALIBRATE BTN ─ GPIO13 (Voltage calibration)               │
│                                                             │
│ Alert Buzzer ── GPIO14                                     │
│                                                             │
│ I2C LCD Display:                                           │
│ SDA ─────────── GPIO2                                      │
│ SCL ─────────── GPIO3                                      │
└─────────────────────────────────────────────────────────────┘

Voltage Divider Circuit (for 12V battery):
┌─────────────────────────────────────────────────────────────┐
│                  VOLTAGE DIVIDER                            │
│                                                             │
│  Battery + ──┬── R1 (10kΩ) ──┬── ADC CH0                  │
│              │                │                             │
│              │             R2 (3.3kΩ)                       │
│              │                │                             │
│  Battery - ──┴────────────────┴── GND                      │
│                                                             │
│  Vout = Vin × R2/(R1+R2) = Vin × 0.248                    │
│  Max input: 13.3V (for 3.3V ADC)                          │
└─────────────────────────────────────────────────────────────┘

Battery Level Indicator Design:
┌─────────────────────────────────────────────────────────────┐
│                 LED BAR GRAPH DISPLAY                       │
│                                                             │
│  100% ████████████████████████ Full                       │
│   90% ███████████████████████░                             │
│   80% ██████████████████████░░                             │
│   70% █████████████████████░░░                             │
│   60% ████████████████████░░░░                             │
│   50% ███████████████████░░░░░                             │
│   40% ██████████████████░░░░░░                             │
│   30% █████████████████░░░░░░░ Low Battery                │
│   20% ████████████████░░░░░░░░                             │
│   10% ███████████████░░░░░░░░░ Critical                   │
│    0% ░░░░░░░░░░░░░░░░░░░░░░░ Empty                       │
└─────────────────────────────────────────────────────────────┘

ADC0834 Connections:
┌─────────────────┐
│     ADC0834     │
├─────────────────┤
│ VCC ── 3.3V     │
│ CS ──  GPIO5    │
│ CLK ── GPIO6    │
│ DI ──  GPIO16   │
│ DO ──  GPIO12   │
│ CH0 ── V_Divider│
│ GND ── GND      │
└─────────────────┘

LED Bar Graph (with 220Ω resistors):
LED1:  GPIO17 ── 220Ω ── LED ── GND (10%)
LED2:  GPIO18 ── 220Ω ── LED ── GND (20%)
LED3:  GPIO27 ── 220Ω ── LED ── GND (30%)
LED4:  GPIO22 ── 220Ω ── LED ── GND (40%)
LED5:  GPIO23 ── 220Ω ── LED ── GND (50%)
LED6:  GPIO24 ── 220Ω ── LED ── GND (60%)
LED7:  GPIO25 ── 220Ω ── LED ── GND (70%)
LED8:  GPIO8  ── 220Ω ── LED ── GND (80%)
LED9:  GPIO7  ── 220Ω ── LED ── GND (90%)
LED10: GPIO1  ── 220Ω ── LED ── GND (100%)
```

## Software Dependencies

Install required libraries:
```bash
# GPIO and hardware control
pip install gpiozero numpy

# I2C for LCD
pip install smbus2

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
```

## Running the Program

```bash
cd examples/08-extension-projects/08-battery-indicator
python battery-voltage-monitor.py
```

Or use the Makefile:
```bash
make          # Run the main program
make demo     # Battery level demonstration
make test     # Test all components
make discharge # Test discharge calculation
make setup    # Install dependencies
```

## Code Walkthrough

### Voltage Measurement with ADC
Safe voltage measurement using voltage divider:
```python
def _voltage_monitoring_loop(self):
    # Read ADC value
    adc_value = self.adc.read(BATTERY_CHANNEL)
    
    # Convert to voltage
    adc_voltage = (adc_value / 255.0) * ADC_REFERENCE_VOLTAGE
    actual_voltage = adc_voltage * VOLTAGE_DIVIDER_RATIO
    
    # Apply calibration offset
    calibrated_voltage = actual_voltage + self.calibration_offset
```

### Battery Percentage Calculation
Convert voltage to charge percentage:
```python
def _calculate_battery_percentage(self):
    profile = BATTERY_PROFILES[self.battery_type]
    
    # Linear interpolation between empty and full
    voltage_range = profile['full'] - profile['empty']
    voltage_above_empty = self.battery_voltage - profile['empty']
    
    percentage = (voltage_above_empty / voltage_range) * 100
    self.battery_percentage = max(0, min(100, percentage))
```

### LED Bar Graph Update
Visual battery level indication:
```python
def _update_led_bar(self):
    # Calculate how many LEDs to light
    leds_to_light = int((self.battery_percentage / 100) * len(self.led_bar))
    
    # Update LEDs
    for i, led in enumerate(self.led_bar):
        if i < leds_to_light:
            led.on()
        else:
            led.off()
```

### Discharge Rate Calculation
Monitor battery discharge over time:
```python
def _calculate_discharge_rate(self):
    recent_history = self.voltage_history[-30:]
    
    start_voltage = recent_history[0]['voltage']
    end_voltage = recent_history[-1]['voltage']
    time_diff = (recent_history[-1]['timestamp'] - 
                recent_history[0]['timestamp']).total_seconds()
    
    if time_diff > 0:
        # V/hour
        self.discharge_rate = (start_voltage - end_voltage) * 3600 / time_diff
```

### Low Battery Alerts
Automatic warning system:
```python
def _alert_monitoring_loop(self):
    if self.battery_percentage < self.critical_battery_threshold:
        # Critical alert
        self.buzzer.beep(0.5, 0.5, n=5)
        self.led_critical.pulse()
    elif self.battery_percentage < self.low_battery_threshold:
        # Low battery alert
        self.buzzer.beep(0.2, 0.3, n=3)
        self.led_low_battery.pulse()
```

## Battery Profiles

### Supported Battery Types

#### LiPo (Lithium Polymer)
- **1S**: 3.7V nominal (3.0V empty, 4.2V full)
- **2S**: 7.4V nominal (6.0V empty, 8.4V full)
- **3S**: 11.1V nominal (9.0V empty, 12.6V full)

#### Lead Acid
- **12V**: 12.0V nominal (11.8V empty, 12.8V full)
- Deep discharge protection at 11.5V

#### NiMH (Nickel Metal Hydride)
- **4-cell**: 4.8V nominal (4.0V empty, 5.6V full)
- Memory effect considerations

#### Alkaline
- **4-cell**: 6.0V nominal (4.0V empty, 6.4V full)
- Non-linear discharge curve

## Display Modes

### 1. Voltage Mode
Shows real-time voltage and percentage:
- Current voltage reading
- Battery percentage
- Cell voltage (for multi-cell batteries)

### 2. Percentage Mode
Large percentage display with bar graph:
- Big percentage number
- Visual bar on LCD
- LED bar graph

### 3. Time Remaining Mode
Estimated runtime calculation:
- Based on discharge rate
- Hours and minutes display
- Requires stable discharge

### 4. Statistics Mode
Historical data view:
- Minimum/maximum voltage
- Runtime counter
- Average discharge rate

### 5. Graph Mode
Voltage trend visualization:
- 16-point history graph
- Shows voltage stability
- Trend indication

## Features

### Accurate Measurement
- Voltage divider for safe measurement
- ADC calibration support
- Averaging for stability
- Noise filtering

### Multi-Chemistry Support
- Pre-configured battery profiles
- Easy battery type selection
- Cell voltage calculation
- Chemistry-specific thresholds

### Visual Indicators
- 10-segment LED bar graph
- Status LEDs for alerts
- LCD with multiple views
- Percentage visualization

### Data Logging
- Automatic data logging
- JSON format for analysis
- Configurable intervals
- Statistics tracking

## Available Demos

1. **Battery Demo**: Simulate various charge levels
2. **Discharge Test**: Test discharge rate calculation
3. **Alert Demo**: Test low battery warnings
4. **Calibration**: Voltage calibration procedure

## Troubleshooting

### Incorrect voltage readings
- Check voltage divider resistor values
- Verify ADC connections
- Test with known voltage source
- Run calibration procedure
- Check for loose connections

### LEDs not working properly
- Verify LED polarity
- Check current limiting resistors
- Test individual LEDs
- Verify GPIO pin connections
- Check for sufficient current

### No ADC readings
- Verify ADC power (3.3V)
- Check SPI connections
- Test with simple ADC read
- Verify chip select pin

### Percentage calculation wrong
- Verify correct battery type selected
- Check voltage range settings
- Calibrate voltage reading
- Update battery profile if needed

### Discharge rate erratic
- Ensure stable power supply
- Increase averaging window
- Check for load variations
- Allow time for stabilization

## Advanced Usage

### Custom Battery Profiles
Add support for new battery types:
```python
BATTERY_PROFILES["LiFePO4_4S"] = {
    "nominal": 12.8,
    "full": 14.6,
    "empty": 10.0,
    "critical": 10.8,
    "cells": 4
}
```

### Voltage Divider Calculation
Design for different voltage ranges:
```python
def calculate_divider(max_voltage, adc_max=3.3):
    # Choose R2 (bottom resistor)
    R2 = 3300  # 3.3kΩ
    
    # Calculate R1 (top resistor)
    R1 = R2 * (max_voltage / adc_max - 1)
    
    # Round to nearest standard value
    return round(R1 / 100) * 100
```

### Coulomb Counting
More accurate capacity tracking:
```python
class CoulombCounter:
    def __init__(self, capacity_ah):
        self.capacity = capacity_ah * 3600  # Convert to coulombs
        self.charge_used = 0
    
    def update(self, current, time_delta):
        # Integrate current over time
        self.charge_used += current * time_delta
        
        # Calculate remaining percentage
        percentage = 100 * (1 - self.charge_used / self.capacity)
        return max(0, min(100, percentage))
```

### Battery Health Monitoring
Track battery degradation:
```python
def calculate_battery_health(self):
    # Compare actual capacity to rated capacity
    if self.discharge_cycles > 0:
        actual_capacity = self.total_discharge / self.discharge_cycles
        rated_capacity = BATTERY_PROFILES[self.battery_type]['capacity']
        
        health_percentage = (actual_capacity / rated_capacity) * 100
        return min(100, health_percentage)
```

### Network Monitoring
Remote battery monitoring:
```python
import requests

def send_battery_status(self):
    data = {
        'device_id': 'battery_001',
        'voltage': self.battery_voltage,
        'percentage': self.battery_percentage,
        'battery_type': self.battery_type,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        response = requests.post('http://monitor.example.com/api/battery', 
                               json=data, timeout=5)
    except:
        pass  # Handle offline gracefully
```

## Performance Optimization

### Measurement Accuracy
- Use stable voltage reference
- Multiple ADC samples
- Median filtering
- Temperature compensation

### Power Efficiency
- Sleep between readings
- Dim LEDs in low light
- Reduce LCD updates
- Use interrupts for buttons

### Response Time
- Prioritize critical alerts
- Asynchronous processing
- Efficient data structures
- Optimized calculations

## Integration Ideas

### UPS Systems
- Automatic switchover detection
- Load management
- Runtime estimation
- Maintenance reminders

### Solar Systems
- Charge controller integration
- Daily energy tracking
- Battery bank monitoring
- Load balancing

### Electric Vehicles
- Multi-cell monitoring
- Temperature compensation
- Regenerative charging detection
- Range estimation

### IoT Devices
- Remote monitoring
- Low power operation
- Predictive maintenance
- Alert notifications

## Next Steps
- Add current measurement for accurate capacity
- Implement battery charging detection
- Create web dashboard for monitoring
- Add temperature compensation
- Support for battery banks (parallel/series)
- Implement predictive failure detection
- Add Bluetooth/WiFi connectivity