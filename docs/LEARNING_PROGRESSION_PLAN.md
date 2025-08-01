# Electronics Engineering Learning Progression Plan
## Raspberry Pi 5 + MIT OCW 6.002 Integration

### Overview
This 20-week progression plan combines hands-on Raspberry Pi 5 projects with MIT's 6.002 Circuits and Electronics course (Spring 2007). Designed for an electronics engineer returning after 14 years, using Python for modern embedded systems development while reinforcing electronics fundamentals.

### Primary Course: MIT 6.002 Circuits and Electronics
- **Instructor:** Prof. Anant Agarwal
- **URL:** https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/
- **Why this course:** Perfect balance of analog/digital fundamentals, systematic progression, practical applications for embedded systems

---

## Phase 1: Foundation & Refresh (Weeks 1-4)
**Goal:** Rebuild confidence with basic electronics and establish good embedded programming practices

### Week 1-2: Getting Grounded
**Hands-On Projects:**
- ✅ Basic GPIO control (LED & Button) - Already completed!
- PWM LED brightness control
- Multiple button debouncing techniques
- 7-segment display driver

**Theory (MIT 6.002):**
- Lecture 1: Introduction and Lumped Abstraction
- Lecture 2: Basic Circuit Analysis Method (KVL, KCL, Ohm's Law)
- Problem Set 1: Basic resistive circuits
- Lab: Build voltage dividers, measure with multimeter

**Code Focus:**
```python
# PWM example structure
PWM_FREQUENCY = 1000  # 1kHz
DUTY_CYCLE_STEPS = 100

# Learn: Threading for timing, duty cycle calculation
# Practice: Clean state machines for button handling
# Python advantage: Easier prototyping and debugging
```

### Week 3-4: Capacitors & Timing
**Hands-On Projects:**
- RC circuit LED fade (hardware PWM vs RC)
- Capacitive touch sensor
- Power supply filtering demonstration
- Simple oscillator circuit

**Theory (MIT 6.002):**
- Lecture 3: Superposition, Thévenin & Norton
- Lecture 4: The Digital Abstraction
- Lecture 5: Inside the Digital Gate
- Lecture 6: Nonlinear Analysis

**Key Learning:**
- Measure RC time constants with oscilloscope
- Compare theoretical vs actual values
- Understand decoupling capacitor placement

---

## Phase 2: Communication & Interfacing (Weeks 5-8)
**Goal:** Master digital communication protocols essential for modern embedded systems

### Week 5-6: Serial Protocols
**Hands-On Projects:**
```
03-spi-temperature/
├── spi-temp-sensor.c    # SPI temperature sensor (MAX31855)
├── i2c-oled-display.c   # I2C OLED display driver
└── uart-gps-parser.c    # UART GPS module integration
```

**Theory (MIT 6.002):**
- Lecture 7: Incremental Analysis
- Lecture 8: Amplifiers - Small Signal Model
- Lecture 9: Amplifiers - Large Signal Analysis
- Focus: MOSFET operation for digital communication

**Protocol Deep Dive:**
- SPI: Clock polarity/phase, multi-device management
- I2C: Address conflicts, clock stretching, pull-ups
- UART: Baud rate calculation, error detection

### Week 7-8: Advanced Interfacing
**Hands-On Projects:**
- 1-Wire temperature sensor network
- CAN bus implementation (automotive focus)
- Modbus RTU over RS485

**Theory (MIT 6.002):**
- Lecture 10: Amplifiers - Follower Circuits
- Lecture 11: Capacitors
- Lecture 12: Circuits with Capacitors
- Application: Decoupling caps for clean sensor readings

**Industry Applications:**
- Industrial sensor networks
- Automotive diagnostics
- Building automation

---

## Phase 3: Real-Time Systems (Weeks 9-12)
**Goal:** Transition from bare-metal to RTOS-based design

### Week 9-10: Async Programming & Threading
**Hands-On Projects:**
```
04-async-programming/
├── threading-basics.py    # Python threading fundamentals
├── queue-communication.py # Thread-safe communication
├── async-sensors.py       # Asyncio for I/O operations
└── event-driven.py        # Event-based architecture
```

**Theory (MIT 6.002):**
- Lecture 13: Digital Circuit Speed
- Lecture 14: State and Memory
- Lecture 15: Second-Order Systems
- Real-time constraints in embedded systems

**Python Concurrency Concepts:**
- Threading vs async/await patterns
- Queue and Lock mechanisms
- Event-driven programming with gpiod
- Real-time constraints in Linux

### Week 11-12: Advanced RTOS
**Hands-On Projects:**
- Multi-sensor data logger with SD card
- Motor control with encoder feedback
- Real-time audio processing

**Theory (MIT 6.002):**
- Lecture 16: Sinusoidal Steady State
- Lecture 17: The Impedance Model
- Lecture 18: Filters
- Application: Sensor noise filtering, motor control

**Performance Focus:**
- DMA usage for high-speed transfers
- Power management in RTOS
- Profiling and optimization

---

## Phase 4: IoT & Networking (Weeks 13-16)
**Goal:** Blend software engineering background with embedded IoT

### Week 13-14: Wireless Connectivity
**Hands-On Projects:**
```
05-iot-connectivity/
├── mqtt-sensor-node.c   # MQTT client implementation
├── ble-beacon.c         # BLE advertising and GATT
├── wifi-provisioning.c  # WiFi setup via BLE
└── lorawan-node.c       # Long-range IoT
```

**Theory (MIT 6.002):**
- Lecture 19: The Operational Amplifier
- Lecture 20: Op Amps Positive Feedback
- Lecture 21: Op Amps Negative Feedback
- Application: Sensor signal conditioning for IoT

**Practical Security:**
- TLS/SSL implementation
- Certificate management
- Secure boot concepts

### Week 15-16: Edge Computing
**Hands-On Projects:**
- Local data aggregation and filtering
- Edge ML inference (temperature anomaly detection)
- Time-series database on Pi

**Theory (MIT 6.002):**
- Lecture 22: Energy and Power
- Lecture 23: Energy, CMOS
- Lecture 24: Power Conversion Circuits
- Critical for battery-powered edge devices

**Python Integration:**
```python
# MicroPython for rapid prototyping
import machine
import ujson

# Leverage your Python experience for:
# - Data processing algorithms
# - Quick protocol testing
# - Web API integration
```

---

## Phase 5: Advanced Applications (Weeks 17-20)
**Goal:** Integrate all skills into career-ready projects

### Week 17-18: AI at the Edge
**Hands-On Projects:**
```
06-edge-ai/
├── tflite-gesture.py     # TensorFlow Lite for Python
├── anomaly-detection.py  # Sensor anomaly detection
├── voice-commands.py     # Speech recognition
└── camera-inference.py   # OpenCV object detection
```

**Theory Completion (MIT 6.002):**
- Lecture 25: Violating the Abstraction Barrier
- Review all problem sets
- Final exam preparation
- Bridge to advanced topics (6.111 Digital Systems)

**TinyML Focus:**
- Model quantization
- Inference optimization
- Power/accuracy trade-offs

### Week 19-20: Capstone Project
**Choose One:**

1. **Industrial IoT Gateway**
   - Multiple sensor protocols
   - Edge processing
   - Cloud connectivity
   - OTA updates

2. **Automotive Diagnostic Tool**
   - CAN bus interface
   - Real-time data logging
   - Bluetooth app interface
   - DTC code reading

3. **Smart Home Controller**
   - Multiple protocol support (Zigbee, Z-Wave)
   - Local automation rules
   - Voice control integration
   - Energy monitoring

---

## Weekly Schedule Template

### Weekday Evenings (1-2 hours)
- **Monday:** MIT 6.002 lecture video + notes
- **Tuesday:** Hands-on project coding
- **Wednesday:** MIT 6.002 problem set work
- **Thursday:** Project debugging/testing
- **Friday:** Documentation & git commits

### Weekend (3-4 hours)
- **Saturday:** Extended project work
- **Sunday:** Week review & next week prep

---

## MIT 6.002 Lecture-to-Project Mapping

### Direct Applications
| Lecture | Topic | Pi Project Application |
|---------|-------|----------------------|
| 1-2 | Basic Circuits | LED current limiting, voltage dividers |
| 4-6 | Digital Abstraction | GPIO digital thresholds, noise margins |
| 11-12 | Capacitors | Debouncing, power supply filtering |
| 13 | Digital Speed | SPI/I2C timing constraints |
| 16-18 | Filters | Sensor noise reduction |
| 19-21 | Op Amps | Analog sensor amplification |
| 22-24 | Power/Energy | Battery life optimization |

### Lab Integration Ideas
- **After Lecture 11:** Build RC debounce circuit, measure with scope
- **After Lecture 18:** Design active filter for temperature sensor
- **After Lecture 23:** Measure Pi power consumption in different modes

---

## Resources & Tools

### Hardware Shopping List
- Logic analyzer (essential for protocols)
- Oscilloscope (Rigol DS1054Z recommended)
- Sensor kit (temperature, humidity, motion)
- Various communication modules
- Breadboards and component kit

### Software Tools
```bash
# Essential installations
sudo apt install logic-analyzer pulseview
sudo apt install kicad  # For PCB design phase
pip3 install gpiod numpy matplotlib
pip3 install tensorflow-lite opencv-python
```

### Online Communities
- r/embedded - Technical discussions
- EEVblog Forums - Hardware focus
- Raspberry Pi Forums - Pi-specific help
- Python Forums - Python-specific help

### Recommended Books
1. "Making Embedded Systems" - Elecia White
2. "The Art of Electronics" - Horowitz & Hill (reference)
3. "Real-Time Concepts for Embedded Systems" - Li & Yao

---

## Career Positioning

### Your Unique Value Proposition
- **Hardware Understanding** + **Software Architecture**
- **14 years production code** + **Embedded constraints**
- **Python ecosystem expertise** + **Real-time systems**

### Target Roles
1. **IoT Solutions Architect**
   - Design end-to-end systems
   - $120k-180k range

2. **Embedded Linux Engineer**
   - Leverage software background
   - $110k-160k range

3. **Edge AI Engineer**
   - Hottest field in 2025
   - $130k-200k range

### Portfolio Projects
- GitHub with documented projects
- Blog posts on implementation challenges
- Open-source contributions to embedded projects

---

## Success Metrics

### Month 1-2 Checkpoint
- [ ] Complete 10+ GPIO projects
- [ ] MIT 6.002 through Lecture 12 (Capacitors)
- [ ] Comfortable with oscilloscope
- [ ] First PR to embedded OSS project

### Month 3-4 Checkpoint
- [ ] Python async/threading projects working
- [ ] Implemented 3+ communication protocols
- [ ] MIT 6.002 through Lecture 24 (Power)
- [ ] Published first technical blog post

### Month 5 Final Goals
- [ ] Capstone project completed
- [ ] LinkedIn updated with projects
- [ ] Applied to 5+ relevant positions
- [ ] Contributing to embedded community

---

## Troubleshooting Guide

### Common Challenges
1. **"It works in simulation but not on hardware"**
   - Check power supply stability
   - Add decoupling capacitors
   - Verify ground connections

2. **"My Python threads aren't working right"**
   - Check for GIL limitations
   - Consider async/await instead
   - Use proper thread synchronization

3. **"Communication protocols aren't working"**
   - Verify voltage levels (3.3V vs 5V)
   - Check pull-up resistors
   - Use logic analyzer

### When Stuck
1. Read the datasheet (completely)
2. Check errata documents
3. Simplify to minimal example
4. Ask with specific details

---

## Final Advice

Remember: You're not starting from zero. Your software engineering experience gives you:
- Debugging methodology
- Version control expertise  
- Code organization skills
- Testing discipline

The hardware is just another API to master. Stay curious, break things, and enjoy the journey back to your electronics roots!

**Next Step:** Continue with Project 02 (GPIO Interrupts) while starting MIT 6.002 Lecture 1 this week.

**Course Access:** https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/