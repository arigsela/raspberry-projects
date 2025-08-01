/*
 * Raspberry Pi 5 GPIO Example - Embedded Style with Comprehensive Comments
 *
 * This program demonstrates GPIO control on Raspberry Pi 5 using libgpiod
 * (GPIO character device) library. The older RPi.GPIO doesn't work on Pi 5
 * due to the new RP1 chip architecture.
 *
 * Hardware setup:
 * - LED connected to GPIO17 (pin 11) with a 330Ω resistor to GND
 * - Button connected between GPIO27 (pin 13) and GND
 *
 * Compile: gcc -o hello-world hello-world.c -lgpiod
 * Run: sudo ./hello-world
 */

// Include statements - similar to embedded C programming
#include <gpiod.h>   // GPIO control library for Linux (replaces RPi.GPIO for Pi 5)
#include <stdio.h>   // Standard I/O functions (printf, perror)
#include <unistd.h>  // Unix standard functions (usleep for delays)
#include <signal.h>  // Signal handling (for Ctrl+C graceful exit)
#include <stdbool.h> // Boolean type support (true/false)

// Preprocessor definitions - like #define in embedded systems
#define GPIO_CHIP "gpiochip4" // Pi 5 uses gpiochip4 for the main 40-pin header
                              // (gpiochip0-3 are for other peripherals)
#define LED_PIN 17            // GPIO17 in BCM numbering (physical pin 11)
#define BUTTON_PIN 27         // GPIO27 in BCM numbering (physical pin 13)

// Global variable with 'volatile' keyword
// 'volatile' tells compiler this variable can change unexpectedly (by interrupt)
// This is crucial in embedded systems for interrupt-modified variables
static volatile bool running = true;

/*
 * Signal handler function - called when Ctrl+C is pressed
 * In embedded systems, this would be similar to an interrupt service routine (ISR)
 *
 * @param sig: Signal number (SIGINT for Ctrl+C)
 */
void signal_handler(int sig)
{
    running = false; // Set flag to exit main loop
}

/*
 * Main function - program entry point
 * Returns: 0 on success, 1 on failure (standard Linux convention)
 */
int main(void)
{
    // Declare pointers to GPIO structures
    // In C, the asterisk (*) denotes a pointer - a variable that holds a memory address
    struct gpiod_chip *chip;        // Represents the GPIO controller chip
    struct gpiod_line *led_line;    // Represents a single GPIO pin for LED
    struct gpiod_line *button_line; // Represents a single GPIO pin for button
    int ret;                        // Return value for error checking

    // Register our signal handler for SIGINT (Ctrl+C)
    // This allows graceful shutdown instead of abrupt termination
    signal(SIGINT, signal_handler);

    // Step 1: Open the GPIO chip
    // This is like initializing a peripheral in embedded systems
    chip = gpiod_chip_open_by_name(GPIO_CHIP);
    if (!chip)
    {                               // In C, NULL pointers evaluate to false
        perror("Open chip failed"); // perror prints error with system error message
        return 1;                   // Return non-zero to indicate failure
    }

    // Step 2: Get handle to specific GPIO pins (lines)
    // Similar to configuring specific pins in embedded MCU
    led_line = gpiod_chip_get_line(chip, LED_PIN);
    if (!led_line)
    {
        perror("Get LED line failed");
        goto close_chip; // 'goto' jumps to cleanup code - common in C error handling
    }

    button_line = gpiod_chip_get_line(chip, BUTTON_PIN);
    if (!button_line)
    {
        perror("Get button line failed");
        goto close_chip;
    }

    // Step 3: Configure LED pin as output
    // The second parameter is a consumer name (for debugging)
    // The third parameter is initial value (0 = LOW, 1 = HIGH)
    ret = gpiod_line_request_output(led_line, "hello-world", 0);
    if (ret < 0)
    { // Negative return values typically indicate errors in Linux
        perror("Request LED output failed");
        goto release_line;
    }

    // Step 4: Configure button pin as input with internal pull-up resistor
    // Pull-up means the pin reads HIGH when button is not pressed
    // Button press connects pin to GND, making it read LOW (active-low logic)
    ret = gpiod_line_request_input_flags(button_line, "hello-world",
                                         GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP);
    if (ret < 0)
    {
        perror("Request button input failed");
        goto release_line;
    }

    // Print startup messages
    printf("\n=== Raspberry Pi 5 GPIO Example ===\n");
    printf("LED on GPIO%d, Button on GPIO%d\n", LED_PIN, BUTTON_PIN);
    printf("Press button to light LED, Ctrl+C to exit\n");
    printf("Program is running... waiting for button press\n\n");
    fflush(stdout); // Force output to display immediately

    // Main control loop - equivalent to while(1) in embedded systems
    // Continues until 'running' becomes false (set by signal handler)
    while (running)
    {
        // Read current state of button pin
        // Returns 1 for HIGH (not pressed due to pull-up), 0 for LOW (pressed)
        int button_state = gpiod_line_get_value(button_line);

        // Simple button-to-LED logic
        if (button_state == 0)
        {                                      // Button pressed (connected to GND)
            gpiod_line_set_value(led_line, 1); // Turn LED ON

            // Only print when state changes to reduce console spam
            static int last_state = 1; // 'static' preserves value between function calls
            if (last_state != button_state)
            {
                printf("Button pressed - LED ON\n");
                last_state = button_state;
            }
        }
        else
        {                                      // Button not pressed (pull-up makes it HIGH)
            gpiod_line_set_value(led_line, 0); // Turn LED OFF

            static int last_state = 1;
            if (last_state != button_state)
            {
                printf("Button released - LED OFF\n");
                last_state = button_state;
            }
        }

        // Small delay for debouncing and to reduce CPU usage
        // usleep() takes microseconds (1 second = 1,000,000 microseconds)
        usleep(10000); // 10ms delay
    }

    printf("\nCleaning up...\n");

// Cleanup section using goto labels
// This is a common C pattern for error handling and cleanup
// Each label handles progressively more cleanup as we unwind
release_line:
    // Release GPIO lines (similar to de-initializing peripherals)
    gpiod_line_release(led_line);
    gpiod_line_release(button_line);

close_chip:
    // Close the GPIO chip handle
    gpiod_chip_close(chip);

    return 0; // Return 0 to indicate successful execution
}

/*
 * Key C concepts demonstrated:
 * 1. Pointers (*) - Variables that store memory addresses
 * 2. Structures (struct) - Custom data types grouping related data
 * 3. Error handling with goto - Common in system programming
 * 4. Static variables - Preserve values between function calls
 * 5. Volatile variables - For interrupt-safe programming
 * 6. Preprocessor macros (#define) - Text substitution before compilation
 *
 * Key differences from typical embedded C:
 * 1. Uses Linux system calls instead of direct register access
 * 2. File-based GPIO access through /dev/gpiochip devices
 * 3. Signal handling instead of hardware interrupts
 * 4. Dynamic memory allocation (hidden in library functions)
 */