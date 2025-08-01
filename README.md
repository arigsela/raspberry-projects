# Raspberry Pi 5 Python Development Projects

A collection of example projects for getting started with Raspberry Pi 5 using Python, designed specifically for engineers returning to electronics with modern tools.

## Project Structure

```
raspberry-projects/
├── examples/          # Python example projects
│   ├── 01-hello-world/
│   ├── 02-gpio-interrupts/
│   └── 03-pwm-control/
├── scripts/           # Utility scripts for deployment and setup
│   ├── deploy.sh      # Deploy code to Raspberry Pi
│   ├── gpio-cleanup.sh # GPIO cleanup utility
│   └── pi-setup.sh    # Raspberry Pi initial setup
├── docs/              # Documentation and guides
│   ├── LEARNING_PROGRESSION_PLAN.md
│   └── REMOTE_SETUP.md
└── README.md          # This file
```

## Example Projects

### [01-hello-world](./examples/01-hello-world/)
**Basic GPIO Control** - Your first Pi 5 project
- LED control and button input
- Introduction to gpiod library for Python
- Clean Python patterns with comprehensive comments

### [02-gpio-interrupts](./examples/02-gpio-interrupts/)
**Event-Driven GPIO** - Advanced interrupt-style programming
- Multiple button monitoring
- Edge detection and event timestamps
- Non-blocking I/O patterns

### [03-pwm-control](./examples/03-pwm-control/)
**PWM LED Brightness Control** - Software PWM implementation
- Pulse Width Modulation theory and practice
- Python threading for accurate timing
- Multiple animation modes (breathing, sine wave, strobe)
- Includes both simple and advanced versions

### Future Projects (Coming Soon)
- 04-spi-communication - SPI devices and sensors
- 05-i2c-devices - I2C communication examples
- 06-real-time - Real-time considerations and techniques

## Quick Start

### 1. Initial Setup on Raspberry Pi 5

**Option A: Use the setup script (recommended)**
```bash
# Deploy and run the setup script:
./scripts/deploy.sh scripts/pi-setup.sh
ssh -i ~/.ssh/pi_id_rsa asela@192.168.0.202
cd ~/projects/raspberry-projects/scripts
./pi-setup.sh
# Then logout and login again for gpio group changes
```

**Option B: Manual installation**
```bash
# Update system
sudo apt update && sudo apt upgrade

# Install required tools for Python GPIO development
sudo apt install python3 python3-pip git
sudo apt install python3-gpiod gpiod

# Add yourself to gpio group
sudo usermod -a -G gpio $USER
# Logout and login again for this to take effect

# Clone this repository (or use deploy.sh from your laptop)
git clone <your-repo-url>
cd raspberry-projects
```

### 2. VS Code Remote Development Setup

**On your development machine:**
1. Install [VS Code](https://code.visualstudio.com/)
2. Install the "Remote - SSH" extension
3. Connect to your Pi:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Remote-SSH: Connect to Host"
   - Enter: `pi@raspberrypi.local` (or your Pi's IP address)
4. Install Python extension in the remote session

### 3. Building and Running Projects

Each project has its own directory with:
- Python source code with comprehensive comments
- Makefile for easy running and dependency management
- Detailed README with circuit diagrams
- Hardware requirements list

**Using the deploy script (recommended):**
```bash
# Deploy a specific project
./scripts/deploy.sh examples/01-hello-world

# Deploy and run
./scripts/deploy.sh examples/01-hello-world --run
```

**Or manually on the Pi:**
```bash
# Navigate to a project
cd ~/projects/raspberry-projects/examples/01-hello-world

# Install dependencies (first time only)
make deps

# Run (requires sudo for GPIO access)
make run
```

## Key Differences: Pi 5 vs Traditional Embedded

| Aspect | Traditional Embedded | Raspberry Pi 5 |
|--------|---------------------|----------------|
| GPIO Access | Direct register manipulation | gpiod character device |
| Architecture | Single MCU | RP1 southbridge + BCM2712 |
| Interrupts | Hardware ISR | Event-driven with polling |
| Memory | Fixed, mapped | Virtual memory with Linux |
| Real-time | Deterministic | Soft real-time only |

## Hardware Notes

### GPIO Chip on Pi 5
- Main GPIO: `/dev/gpiochip4`
- Different from Pi 4 due to new RP1 chip
- 40-pin header remains compatible

### Power Considerations
- 5V/3A minimum recommended
- GPIO pins are 3.3V logic (not 5V tolerant!)
- Total GPIO current limit: 50mA

## Learning Path

1. **Start with 01-hello-world**
   - Understand basic GPIO operations
   - Learn libgpiod fundamentals
   
2. **Move to 02-gpio-interrupts**
   - Master event-driven programming
   - Handle multiple inputs efficiently

3. **Experiment and Extend**
   - Modify examples for your hardware
   - Combine concepts from multiple projects

## Troubleshooting

### Common Issues

**"Permission denied" when accessing GPIO**
- Run with `sudo` or add user to `gpio` group:
  ```bash
  sudo usermod -a -G gpio $USER
  # Logout and login for changes to take effect
  ```

**"gpiochip4 not found"**
- Verify you're on Pi 5: `cat /proc/device-tree/model`
- List available chips: `ls /dev/gpiochip*`

**Old RPi.GPIO code not working**
- Pi 5 requires gpiod, not RPi.GPIO
- The gpiod library is the modern way to control GPIO
- See project examples for proper implementation

## Contributing

Feel free to:
- Report issues
- Suggest new project ideas
- Submit improvements to existing examples

## Documentation

### Available Guides
- **[Learning Progression Plan](./docs/LEARNING_PROGRESSION_PLAN.md)** - 20-week structured learning path combining Pi projects with MIT OpenCourseWare
- **[Remote Development Setup](./docs/REMOTE_SETUP.md)** - Guide for developing on your laptop while executing on Pi

### Utility Scripts
- **[deploy.sh](./scripts/deploy.sh)** - Sync and run code on your Raspberry Pi
- **[gpio-cleanup.sh](./scripts/gpio-cleanup.sh)** - Clean up stuck GPIO processes
- **[pi-setup.sh](./scripts/pi-setup.sh)** - Initial Raspberry Pi setup script

## Resources

- [Official Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [Python gpiod Documentation](https://pypi.org/project/gpiod/)
- [libgpiod Documentation](https://libgpiod.readthedocs.io/)
- [Raspberry Pi Forums](https://forums.raspberrypi.com/)

## License

These examples are provided as-is for educational purposes.