# Makefile for 8x8 LED Matrix Display

# Default target
.DEFAULT_GOAL := run

# Python interpreter
PYTHON := python3

# Main program
PROGRAM := led-matrix.py

# Phony targets
.PHONY: run test pattern scroll game clock install clean help

# Run the main program
run:
	@echo "Starting LED Matrix Display..."
	@$(PYTHON) $(PROGRAM)

# Run with test pattern
test:
	@echo "Running LED Matrix test pattern..."
	@$(PYTHON) -c "import led_matrix; led_matrix.segment_test()"

# Show static patterns
pattern:
	@echo "Showing basic patterns..."
	@$(PYTHON) -c "import led_matrix; led_matrix.basic_patterns()"

# Scrolling text demo
scroll:
	@echo "Running scrolling text demo..."
	@$(PYTHON) -c "import led_matrix; led_matrix.scrolling_message()"

# Game of Life simulation
game:
	@echo "Starting Game of Life..."
	@$(PYTHON) -c "import led_matrix; led_matrix.game_of_life()"

# Digital clock
clock:
	@echo "Starting digital clock..."
	@$(PYTHON) -c "import led_matrix; led_matrix.clock_display()"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install gpiozero

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Help
help:
	@echo "LED Matrix Display Control"
	@echo "========================="
	@echo ""
	@echo "Available targets:"
	@echo "  make run      - Run the interactive menu (default)"
	@echo "  make test     - Run test pattern"
	@echo "  make pattern  - Show basic patterns"
	@echo "  make scroll   - Run scrolling text demo"
	@echo "  make game     - Run Game of Life simulation"
	@echo "  make clock    - Show digital clock"
	@echo "  make install  - Install required dependencies"
	@echo "  make clean    - Clean up cache files"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make             # Run main program"
	@echo "  make scroll      # Show scrolling text"
	@echo "  make game        # Play Game of Life"