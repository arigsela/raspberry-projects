#!/bin/bash
# Raspberry Pi 5 Development Environment Setup Script
# Run this script on your Raspberry Pi to install all required dependencies

echo "==================================="
echo "Raspberry Pi 5 Development Setup"
echo "==================================="

# Update package list
echo "Updating package list..."
sudo apt update

# Install Python and essential tools
echo "Installing Python and essential tools..."
sudo apt install -y python3 python3-pip git

# Install GPIO libraries for Raspberry Pi 5
echo "Installing GPIO libraries (required for Pi 5)..."
sudo apt install -y python3-gpiod gpiod
pip3 install gpiod

# Install additional useful tools
echo "Installing additional development tools..."
sudo apt install -y htop tree tmux

# Create project directory if it doesn't exist
echo "Creating project directory..."
mkdir -p ~/projects

# Add user to gpio group (if not already added)
echo "Adding user to gpio group..."
sudo usermod -a -G gpio $USER

# Test GPIO access
echo "Testing GPIO access..."
if command -v gpiodetect &> /dev/null; then
    echo "GPIO tools installed successfully. Available chips:"
    gpiodetect
else
    echo "Warning: GPIO tools not properly installed"
fi

# Display installed versions
echo ""
echo "Installed versions:"
echo "=================="
python3 --version
pip3 --version
echo -n "gpiod module: "
python3 -c "import gpiod; print(gpiod.__version__)" 2>/dev/null || echo "Not installed"

echo ""
echo "Setup complete!"
echo ""
echo "IMPORTANT: You need to logout and login again for gpio group changes to take effect."
echo "After logging back in, you should be able to run GPIO programs without sudo."
echo ""
echo "To test the installation:"
echo "1. Log out and log back in"
echo "2. Run: groups  (should show 'gpio' in the list)"
echo "3. Try building the hello-world example"