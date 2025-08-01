#!/bin/bash
# GPIO Cleanup Script - Kills stuck GPIO processes and releases pins

echo "GPIO Cleanup Script"
echo "==================="

# Kill any running hello-world or gpio-interrupts processes
echo "Looking for stuck GPIO processes..."

PROCS=$(ps aux | grep -E 'hello-world|gpio-interrupts' | grep -v grep | awk '{print $2}')

if [ -z "$PROCS" ]; then
    echo "No GPIO processes found running."
else
    echo "Found GPIO processes with PIDs: $PROCS"
    echo "Killing processes..."
    for PID in $PROCS; do
        sudo kill -9 $PID 2>/dev/null && echo "  Killed PID $PID" || echo "  Failed to kill PID $PID"
    done
fi

# Optional: Release all GPIO lines using gpioset
# This resets GPIO pins to their default state
if command -v gpioset &> /dev/null; then
    echo ""
    echo "Resetting GPIO pins to default state..."
    # Reset common pins used in our examples
    for pin in 17 27 22; do
        echo "  Releasing GPIO$pin"
        gpioset -m time -s 1ms gpiochip4 $pin=0 2>/dev/null || true
    done
fi

echo ""
echo "Cleanup complete!"
echo "You can now run your GPIO programs again."