# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Raspberry Pi 5 educational project repository containing Python examples for GPIO control, sensors, displays, and various hardware components. The codebase uses the modern `gpiod` library (not RPi.GPIO) for GPIO control on Raspberry Pi 5.

## Key Commands

### Building and Running Examples
```bash
# Deploy code to Raspberry Pi (from development machine)
./scripts/deploy.sh examples/01-hello-world --run

# On Raspberry Pi: Install dependencies for a project
cd examples/01-hello-world
make deps

# Run a project (requires sudo for GPIO access)
make run

# Clean Python cache
make clean
```

### Common Development Tasks
```bash
# GPIO cleanup if processes are stuck
./scripts/gpio-cleanup.sh

# Initial Pi setup (run once)
./scripts/pi-setup.sh

# Deploy specific project
./scripts/deploy.sh examples/02-output-displays/01-blinking-led
```

## Architecture and Structure

### Project Organization
- **examples/** - All tutorial projects organized by category:
  - 01-hello-world - Basic GPIO introduction
  - 02-output-displays - LED displays (single, RGB, bar graph, 7-segment, matrix, LCD)
  - 03-output-sound - Buzzers (active and passive)
  - 04-output-drivers - Motors, servos, relays
  - 05-input-controllers - Buttons, switches, encoders, potentiometers, keypads, joysticks
  - 06-input-sensors - Light, temperature, humidity, motion, distance, accelerometer, RFID
  - 07-audiovisual - Camera integration
  - 08-extension-projects - Complete project examples combining multiple components

- **_shared/** - Reusable Python modules:
  - `adc0834.py` - ADC interface for analog sensors
  - `lcd1602.py` - I2C LCD display driver
  - `dht11.py` - Temperature/humidity sensor interface

### Key Technical Details

#### GPIO Access on Pi 5
- Uses `/dev/gpiochip4` (different from Pi 4)
- Requires `gpiod` library, NOT `RPi.GPIO`
- GPIO operations need sudo or gpio group membership
- 3.3V logic levels (not 5V tolerant)

#### Standard Pin Configurations
- ADC0834: CS=17, CLK=18, DI=27, DO=22
- I2C: SDA=GPIO2 (Pin 3), SCL=GPIO3 (Pin 5)
- Default I2C address for LCD: 0x27

#### Project Structure Pattern
Each example follows consistent structure:
- Python script with comprehensive comments
- Makefile with standard targets (run, deps, clean)
- README.md with circuit diagrams and explanations
- Hardware requirements list

## Development Workflow

### Remote Development Setup
1. Code is developed on laptop using VS Code Remote-SSH
2. Deployed to Pi at IP 192.168.0.202 (user: asela)
3. SSH key: `~/.ssh/pi_id_rsa`
4. Destination: `~/projects/raspberry-projects`

### Testing Pattern
```bash
# Deploy and test cycle
./scripts/deploy.sh examples/[project-name] --run
# Monitor output, Ctrl+C to stop
# Make changes locally, redeploy
```

### Common Issues and Solutions
- **Permission denied on GPIO**: Run with sudo or ensure user is in gpio group
- **gpiochip4 not found**: Verify Pi 5 with `cat /proc/device-tree/model`
- **I2C device not found**: Enable I2C with `sudo raspi-config`
- **ADC readings incorrect**: Check DO/DI wire connections

## Important Notes

- Always use `gpiod` library for GPIO operations on Pi 5
- Check existing examples before implementing new features
- Follow established patterns for GPIO pin assignments
- Include proper signal handlers for clean shutdown
- Test with actual hardware before committing