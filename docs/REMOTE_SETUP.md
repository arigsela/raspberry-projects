# Remote Development Setup Guide

This guide explains how to develop on your laptop while executing code on your Raspberry Pi.

## Prerequisites

1. **SSH enabled on Raspberry Pi**
   ```bash
   # On your Pi (if not already enabled):
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

2. **SSH key setup (optional but recommended)**
   ```bash
   # On your laptop:
   ssh-keygen -t rsa -b 4096  # If you don't have a key
   ssh-copy-id pi@raspberrypi.local  # Copy key to Pi
   ```

## Method 1: Deploy Script (Recommended)

### Initial Setup

1. Edit `deploy.sh` to match your Pi's configuration:
   ```bash
   PI_HOST="raspberrypi.local"  # or your Pi's IP
   PI_USER="pi"                  # your username
   PI_PATH="~/projects/raspberry-projects"
   ```

2. Make the script executable (already done):
   ```bash
   chmod +x deploy.sh
   ```

### Usage

```bash
# Sync all files to Pi
./deploy.sh

# Sync specific project
./deploy.sh 01-hello-world

# Sync and build on Pi
./deploy.sh 01-hello-world --build

# Sync, build, and run on Pi
./deploy.sh 01-hello-world --run

# Clean build files on Pi
./deploy.sh 01-hello-world --clean
```

### VS Code Integration

Use the Command Palette (`Cmd+Shift+P` on Mac, `Ctrl+Shift+P` on Linux/Windows):

1. **Run Build Task** (`Cmd+Shift+B`): Deploys and builds current project
2. **Run Task**: Shows all available tasks:
   - Deploy All to Pi
   - Deploy Current Project
   - Deploy and Build Current Project
   - Deploy and Run Current Project
   - SSH to Raspberry Pi

## Method 2: VS Code Remote-SSH

### Setup

1. Install "Remote - SSH" extension in VS Code
2. Connect to Pi:
   - `Cmd+Shift+P` → "Remote-SSH: Connect to Host"
   - Enter: `pi@raspberrypi.local`
3. Open the project folder on Pi
4. Install C/C++ extension on remote

**Pros**: Direct editing on Pi, no sync needed
**Cons**: Requires stable connection, can be slower

## Method 3: Git-based Workflow

### On your laptop:
```bash
git add .
git commit -m "Update GPIO code"
git push origin main
```

### On your Pi:
```bash
cd ~/projects/raspberry-projects
git pull
cd 01-hello-world
make run
```

## Method 4: Automated Sync with fswatch (macOS)

Install fswatch and auto-sync on file changes:

```bash
# Install on macOS
brew install fswatch

# Create watch script
cat > watch-sync.sh << 'EOF'
#!/bin/bash
fswatch -o . | while read f; do
    ./deploy.sh
done
EOF

chmod +x watch-sync.sh
./watch-sync.sh  # Runs until you stop it
```

## Method 5: SSHFS Mount (Advanced)

Mount Pi's filesystem on your laptop:

```bash
# macOS (requires macFUSE)
brew install sshfs
mkdir ~/pi-mount
sshfs pi@raspberrypi.local:/home/pi ~/pi-mount

# Unmount when done
umount ~/pi-mount
```

## Typical Workflow

1. **Edit** code on your laptop in VS Code
2. **Deploy** using one of:
   - `./deploy.sh 01-hello-world --run` (command line)
   - `Cmd+Shift+B` in VS Code (deploys and builds)
   - VS Code Run Task menu
3. **Monitor** output in terminal
4. **Debug** by SSHing to Pi if needed

## Troubleshooting

### "Connection refused" error
- Ensure Pi is on network: `ping raspberrypi.local`
- Check SSH is running: `sudo systemctl status ssh`
- Try IP instead of hostname

### "Permission denied" error
- Run on Pi: `sudo usermod -a -G gpio $USER`
- Logout and login again

### Sync issues
- Check rsync is installed on both machines
- Verify paths in deploy.sh
- Use `-v` flag with rsync for verbose output

## Performance Tips

1. **Exclude large files** from sync (.git, binaries, etc.)
2. **Use SSH keys** to avoid password prompts
3. **Consider wired ethernet** for faster transfers
4. **Use incremental builds** (make tracks dependencies)

## Security Note

For production/public projects:
- Don't hardcode IPs or passwords
- Use environment variables
- Consider VPN for remote access