# Makefile for MFRC522 RFID Reader

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := mfrc522-rfid.py

# Phony targets
.PHONY: run test demo access register clone attendance setup install clean help

# Run the main program
run:
	@echo "Starting MFRC522 RFID Reader..."
	@$(PYTHON) $(PROGRAM)

# Test basic card reading
test:
	@echo "Testing basic card reading..."
	@$(PYTHON) -c "from mfrc522_rfid import basic_card_reading; basic_card_reading()"

# Run demo sequence
demo:
	@echo "Running RFID demos..."
	@echo "Note: Demos require user interaction with RFID cards"
	@echo "1. Basic reading test (30 seconds)..."
	@timeout 30 $(PYTHON) -c "from mfrc522_rfid import basic_card_reading; basic_card_reading()" || true

# Access control system
access:
	@echo "Starting access control system..."
	@$(PYTHON) -c "from mfrc522_rfid import access_control_system; access_control_system()"

# Card registration system
register:
	@echo "Starting card registration..."
	@$(PYTHON) -c "from mfrc522_rfid import card_registration_system; card_registration_system()"

# Card cloning demo
clone:
	@echo "Starting card cloning demo..."
	@echo "⚠️ For educational purposes only!"
	@$(PYTHON) -c "from mfrc522_rfid import card_cloning_demo; card_cloning_demo()"

# Attendance system
attendance:
	@echo "Starting attendance system..."
	@$(PYTHON) -c "from mfrc522_rfid import attendance_system; attendance_system()"

# Setup SPI and dependencies
setup:
	@echo "Setting up SPI and dependencies..."
	@echo "Enabling SPI interface..."
	@sudo raspi-config nonint do_spi 0 || echo "SPI setup may require manual configuration"
	@echo "Installing Python libraries..."
	@pip install spidev gpiozero
	@echo "Testing SPI connection..."
	@ls /dev/spi* 2>/dev/null && echo "✓ SPI devices found" || echo "⚠ No SPI devices found - check SPI enable"

# Install dependencies only
install:
	@echo "Installing dependencies..."
	pip install spidev gpiozero

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "rfid_cards.json" -delete
	find . -type f -name "attendance.json" -delete

# Help
help:
	@echo "MFRC522 RFID Reader/Writer"
	@echo "=========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run        - Run the interactive menu (default)"
	@echo "  make test       - Test basic card reading"
	@echo "  make demo       - Run demo sequence"
	@echo "  make access     - Run access control system"
	@echo "  make register   - Run card registration system"
	@echo "  make clone      - Run card cloning demo (educational)"
	@echo "  make attendance - Run attendance tracking system"
	@echo "  make setup      - Setup SPI and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo "  make clean      - Clean up cache and data files"
	@echo "  make help       - Show this help message"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - SPI must be enabled: sudo raspi-config → Interface → SPI"
	@echo "  - Connect MFRC522:"
	@echo "    SDA → GPIO8,  SCK → GPIO11, MOSI → GPIO10"
	@echo "    MISO → GPIO9, RST → GPIO22, 3.3V → 3.3V, GND → GND"
	@echo "  - Have MIFARE Classic 1K cards for testing"
	@echo ""
	@echo "Examples:"
	@echo "  make setup       # First-time setup"
	@echo "  make test        # Test card detection"
	@echo "  make register    # Register new cards"
	@echo "  make access      # Demo access control"
	@echo ""
	@echo "Security Notice:"
	@echo "  - Use cloning features responsibly and legally"
	@echo "  - Only test with cards you own"
	@echo "  - Educational and research purposes only"