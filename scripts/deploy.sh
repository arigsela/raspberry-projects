#!/bin/bash
# Deploy script - syncs code to Raspberry Pi and optionally builds/runs

# Configuration - Update these for your setup
PI_HOST="192.168.0.202"  # or use IP address like "192.168.1.100"
PI_USER="asela"                  # your Pi username
PI_PATH="~/projects/raspberry-projects"  # destination path on Pi
SSH_KEY="$HOME/.ssh/pi_id_rsa"  # path to custom SSH key

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Parse command line arguments
PROJECT=""
ACTION="sync"  # Default action is just sync

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            ACTION="build"
            shift
            ;;
        --run)
            ACTION="run"
            shift
            ;;
        --clean)
            ACTION="clean"
            shift
            ;;
        *)
            PROJECT=$1
            shift
            ;;
    esac
done

# Check if SSH is available
print_status "Checking connection to $PI_USER@$PI_HOST..."
ssh -i $SSH_KEY -q -o ConnectTimeout=5 $PI_USER@$PI_HOST exit
if [ $? -ne 0 ]; then
    print_error "Cannot connect to Raspberry Pi at $PI_USER@$PI_HOST"
    print_error "Check that:"
    print_error "  1. Your Pi is powered on and connected to network"
    print_error "  2. SSH is enabled on the Pi"
    print_error "  3. The hostname/IP is correct in this script"
    exit 1
fi

# Create remote directory if it doesn't exist
print_status "Ensuring remote directory exists..."
ssh -i $SSH_KEY $PI_USER@$PI_HOST "mkdir -p $PI_PATH"

# Sync files
print_status "Syncing files to Raspberry Pi..."
if [ -z "$PROJECT" ]; then
    # Sync entire repository
    rsync -avz -e "ssh -i $SSH_KEY" --exclude='.git' --exclude='*.o' --exclude='hello-world' \
          --exclude='gpio-interrupts' --delete \
          ./ $PI_USER@$PI_HOST:$PI_PATH/
    print_status "Synced entire repository"
else
    # Sync specific project
    if [ -d "$PROJECT" ]; then
        rsync -avz -e "ssh -i $SSH_KEY" --exclude='*.o' --exclude="$(basename $PROJECT .c)" \
              --delete \
              $PROJECT/ $PI_USER@$PI_HOST:$PI_PATH/$PROJECT/
        print_status "Synced project: $PROJECT"
    else
        print_error "Project directory '$PROJECT' not found"
        exit 1
    fi
fi

# Perform additional actions based on flags
if [ ! -z "$PROJECT" ]; then
    case $ACTION in
        build)
            print_status "Building project on Raspberry Pi..."
            ssh -i $SSH_KEY $PI_USER@$PI_HOST "cd $PI_PATH/$PROJECT && make clean && make"
            ;;
        run)
            print_status "Building and running project on Raspberry Pi..."
            ssh -i $SSH_KEY $PI_USER@$PI_HOST "cd $PI_PATH/$PROJECT && make clean && make && make run"
            ;;
        clean)
            print_status "Cleaning project on Raspberry Pi..."
            ssh -i $SSH_KEY $PI_USER@$PI_HOST "cd $PI_PATH/$PROJECT && make clean"
            ;;
    esac
fi

print_status "Deployment complete!"

# Show usage if no arguments
if [ -z "$PROJECT" ] && [ "$ACTION" == "sync" ]; then
    echo ""
    echo "Usage examples:"
    echo "  ./deploy.sh                    # Sync all files"
    echo "  ./deploy.sh 01-hello-world     # Sync specific project"
    echo "  ./deploy.sh 01-hello-world --build   # Sync and build"
    echo "  ./deploy.sh 01-hello-world --run     # Sync, build, and run"
    echo "  ./deploy.sh 01-hello-world --clean   # Sync and clean"
fi