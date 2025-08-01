/*
 * Advanced GPIO Example - Interrupt-style Event Detection
 * 
 * This example shows how to use libgpiod's event detection features,
 * which are similar to interrupts in embedded systems.
 * 
 * Features demonstrated:
 * - Edge detection (rising/falling edges)
 * - Event-driven programming (no polling)
 * - Timeouts and non-blocking I/O
 * - Multiple GPIO handling
 * 
 * Hardware setup:
 * - LED on GPIO17 (pin 11)
 * - Button on GPIO27 (pin 13) 
 * - Optional: Second button on GPIO22 (pin 15)
 */

#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>
#include <string.h>     // For memset
#include <sys/time.h>   // For timeval structure
#include <errno.h>      // For error codes

#define GPIO_CHIP "gpiochip4"
#define LED_PIN 17
#define BUTTON1_PIN 27
#define BUTTON2_PIN 22

// Global running flag for signal handler
static volatile bool running = true;

// Structure to hold our GPIO context
// Structures in C group related data together
typedef struct {
    struct gpiod_chip *chip;
    struct gpiod_line *led;
    struct gpiod_line *button1;
    struct gpiod_line *button2;
    int button1_count;  // Count button presses
    int button2_count;
} gpio_context_t;

void signal_handler(int sig) {
    printf("\nReceived signal %d, shutting down...\n", sig);
    running = false;
}

/*
 * Initialize GPIO hardware
 * This function demonstrates proper error handling with cleanup
 * 
 * @param ctx: Pointer to GPIO context structure
 * @return: 0 on success, -1 on failure
 */
int gpio_init(gpio_context_t *ctx) {
    // Clear the structure (good practice)
    memset(ctx, 0, sizeof(gpio_context_t));
    
    // Open GPIO chip
    ctx->chip = gpiod_chip_open_by_name(GPIO_CHIP);
    if (!ctx->chip) {
        fprintf(stderr, "Failed to open %s: %s\n", GPIO_CHIP, strerror(errno));
        return -1;
    }
    
    // Get GPIO lines
    ctx->led = gpiod_chip_get_line(ctx->chip, LED_PIN);
    ctx->button1 = gpiod_chip_get_line(ctx->chip, BUTTON1_PIN);
    ctx->button2 = gpiod_chip_get_line(ctx->chip, BUTTON2_PIN);
    
    if (!ctx->led || !ctx->button1 || !ctx->button2) {
        fprintf(stderr, "Failed to get GPIO lines\n");
        return -1;
    }
    
    // Configure LED as output
    if (gpiod_line_request_output(ctx->led, "gpio-interrupts", 0) < 0) {
        fprintf(stderr, "Failed to request LED output\n");
        return -1;
    }
    
    // Configure buttons for event detection
    // FALLING_EDGE means detect HIGH->LOW transition (button press with pull-up)
    // This is similar to configuring interrupt triggers in embedded systems
    if (gpiod_line_request_falling_edge_events_flags(ctx->button1, "gpio-interrupts",
            GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP) < 0) {
        fprintf(stderr, "Failed to request button1 events\n");
        return -1;
    }
    
    if (gpiod_line_request_falling_edge_events_flags(ctx->button2, "gpio-interrupts",
            GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP) < 0) {
        fprintf(stderr, "Failed to request button2 events\n");
        return -1;
    }
    
    return 0;
}

/*
 * Cleanup GPIO resources
 * Always important to release resources in embedded systems
 */
void gpio_cleanup(gpio_context_t *ctx) {
    if (ctx->led) gpiod_line_release(ctx->led);
    if (ctx->button1) gpiod_line_release(ctx->button1);
    if (ctx->button2) gpiod_line_release(ctx->button2);
    if (ctx->chip) gpiod_chip_close(ctx->chip);
}

/*
 * Handle button press event
 * This simulates an interrupt service routine (ISR)
 */
void handle_button_event(gpio_context_t *ctx, struct gpiod_line *line, 
                        const char *button_name, int *count) {
    struct gpiod_line_event event;
    
    // Read the event (clears the event flag)
    if (gpiod_line_event_read(line, &event) == 0) {
        (*count)++;  // Increment counter
        
        // Print event details
        printf("[%ld.%06ld] %s pressed! Count: %d\n", 
               event.ts.tv_sec, event.ts.tv_nsec / 1000,
               button_name, *count);
        
        // Toggle LED on button press
        static int led_state = 0;
        led_state = !led_state;  // Toggle between 0 and 1
        gpiod_line_set_value(ctx->led, led_state);
    }
}

/*
 * Main event loop using poll-style waiting
 * This is more efficient than continuous polling
 */
int main(void) {
    gpio_context_t gpio_ctx;
    struct gpiod_line_bulk bulk;  // For monitoring multiple lines
    struct timeval timeout;
    int ret;
    
    // Install signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Initialize GPIO
    if (gpio_init(&gpio_ctx) < 0) {
        fprintf(stderr, "GPIO initialization failed\n");
        return 1;
    }
    
    // Create a "bulk" object to monitor multiple GPIO lines
    // This allows efficient monitoring of multiple inputs
    gpiod_line_bulk_init(&bulk);
    gpiod_line_bulk_add(&bulk, gpio_ctx.button1);
    gpiod_line_bulk_add(&bulk, gpio_ctx.button2);
    
    printf("GPIO Event Detection Example\n");
    printf("Press buttons to trigger events. Ctrl+C to exit.\n");
    printf("Button 1: GPIO%d, Button 2: GPIO%d\n\n", BUTTON1_PIN, BUTTON2_PIN);
    
    // Main event loop
    while (running) {
        // Set timeout for event wait (1 second)
        // This allows periodic checking of the running flag
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;
        
        // Wait for events on any monitored line
        // This is similar to interrupt-driven programming
        ret = gpiod_line_event_wait_bulk(&bulk, &timeout, NULL);
        
        if (ret < 0) {
            // Error occurred
            fprintf(stderr, "Event wait error: %s\n", strerror(errno));
            break;
        } else if (ret == 0) {
            // Timeout - no events
            // This is normal, just continue loop
            continue;
        }
        
        // Check which button(s) triggered events
        // Multiple events can occur simultaneously
        if (gpiod_line_event_get_fd(gpio_ctx.button1) >= 0) {
            // Check if this specific line has an event pending
            ret = gpiod_line_event_wait(gpio_ctx.button1, &timeout);
            if (ret > 0) {
                handle_button_event(&gpio_ctx, gpio_ctx.button1, 
                                  "Button 1", &gpio_ctx.button1_count);
            }
        }
        
        if (gpiod_line_event_get_fd(gpio_ctx.button2) >= 0) {
            ret = gpiod_line_event_wait(gpio_ctx.button2, &timeout);
            if (ret > 0) {
                handle_button_event(&gpio_ctx, gpio_ctx.button2, 
                                  "Button 2", &gpio_ctx.button2_count);
            }
        }
    }
    
    // Print statistics
    printf("\nFinal statistics:\n");
    printf("Button 1 pressed: %d times\n", gpio_ctx.button1_count);
    printf("Button 2 pressed: %d times\n", gpio_ctx.button2_count);
    
    // Cleanup
    gpio_cleanup(&gpio_ctx);
    
    return 0;
}

/*
 * Advanced C concepts demonstrated:
 * 1. typedef - Creates type aliases for easier code reading
 * 2. Structures with pointers - Organizing complex data
 * 3. Function pointers (hidden in gpiod library callbacks)
 * 4. Event-driven programming - Similar to interrupts
 * 5. Bulk operations - Efficient handling of multiple resources
 * 6. Proper error handling with errno
 * 
 * This example shows how Linux provides interrupt-like functionality
 * through file descriptors and event polling, which is different from
 * bare-metal embedded systems but achieves similar results.
 */