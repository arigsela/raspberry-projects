/*
 * Raspberry Pi 5 PWM LED Brightness Control
 * 
 * This program demonstrates Pulse Width Modulation (PWM) for LED brightness control
 * on Raspberry Pi 5. Since Pi 5's libgpiod doesn't have built-in PWM support,
 * we implement software PWM using high-resolution timers.
 * 
 * PWM Concepts:
 * - Frequency: How many on/off cycles per second (Hz)
 * - Duty Cycle: Percentage of time the signal is HIGH (0-100%)
 * - Period: Total time for one complete cycle (1/frequency)
 * 
 * Hardware setup:
 * - LED connected to GPIO17 (pin 11) with a 330Ω resistor to GND
 * - Optional: Potentiometer on GPIO27 for brightness control
 * 
 * Compile: gcc -o pwm-control pwm-control.c -lgpiod -lpthread -lm
 * Run: sudo ./pwm-control
 */

// Include statements
#include <gpiod.h>      // GPIO control library for Linux
#include <stdio.h>      // Standard I/O functions
#include <unistd.h>     // Unix standard functions
#include <signal.h>     // Signal handling for graceful exit
#include <stdbool.h>    // Boolean type support
#include <time.h>       // High-resolution timing functions
#include <pthread.h>    // Threading support for PWM timing
#include <math.h>       // Mathematical functions (sin, cos)
#include <errno.h>      // Error reporting

// GPIO Configuration
#define GPIO_CHIP "gpiochip4"  // Pi 5 main GPIO chip
#define LED_PIN 17             // GPIO17 for LED output
#define BUTTON_PIN 27          // GPIO27 for mode selection

// PWM Configuration
#define PWM_FREQUENCY 1000     // 1 kHz PWM frequency
#define PWM_PERIOD_NS (1000000000 / PWM_FREQUENCY)  // Period in nanoseconds
#define DUTY_CYCLE_STEPS 100   // Resolution: 0-100%

// Animation modes
typedef enum {
    MODE_MANUAL,      // Fixed brightness levels
    MODE_BREATHING,   // Smooth fade in/out
    MODE_STROBE,      // Fast blinking
    MODE_SINE_WAVE    // Sine wave brightness pattern
} animation_mode_t;

// Global variables
static volatile bool running = true;
static volatile animation_mode_t current_mode = MODE_MANUAL;
static volatile int manual_brightness = 50;  // Default 50% brightness

// PWM control structure
typedef struct {
    struct gpiod_line *line;
    pthread_t thread;
    pthread_mutex_t mutex;
    volatile int duty_cycle;    // 0-100%
    volatile bool active;
} pwm_control_t;

/*
 * Signal handler for graceful shutdown
 */
void signal_handler(int sig) {
    printf("\nShutting down PWM control...\n");
    running = false;
}

/*
 * High-resolution sleep function
 * More accurate than usleep() for PWM timing
 * 
 * @param nanoseconds: Time to sleep in nanoseconds
 */
void nano_sleep(long nanoseconds) {
    struct timespec req = {
        .tv_sec = nanoseconds / 1000000000L,
        .tv_nsec = nanoseconds % 1000000000L
    };
    
    // Loop to handle interruptions
    while (nanosleep(&req, &req) == -1 && errno == EINTR) {
        continue;
    }
}

/*
 * PWM thread function - generates the PWM signal
 * This runs in a separate thread for accurate timing
 * 
 * @param arg: Pointer to pwm_control_t structure
 */
void* pwm_thread(void* arg) {
    pwm_control_t *pwm = (pwm_control_t*)arg;
    
    while (pwm->active) {
        // Get current duty cycle (thread-safe)
        pthread_mutex_lock(&pwm->mutex);
        int duty = pwm->duty_cycle;
        pthread_mutex_unlock(&pwm->mutex);
        
        // Calculate on and off times
        long on_time_ns = (PWM_PERIOD_NS * duty) / 100;
        long off_time_ns = PWM_PERIOD_NS - on_time_ns;
        
        if (duty > 0) {
            // Set HIGH and wait
            gpiod_line_set_value(pwm->line, 1);
            nano_sleep(on_time_ns);
        }
        
        if (duty < 100) {
            // Set LOW and wait
            gpiod_line_set_value(pwm->line, 0);
            nano_sleep(off_time_ns);
        }
    }
    
    // Ensure LED is off when exiting
    gpiod_line_set_value(pwm->line, 0);
    return NULL;
}

/*
 * Set PWM duty cycle (thread-safe)
 * 
 * @param pwm: PWM control structure
 * @param duty_cycle: Desired duty cycle (0-100%)
 */
void set_duty_cycle(pwm_control_t *pwm, int duty_cycle) {
    // Clamp to valid range
    if (duty_cycle < 0) duty_cycle = 0;
    if (duty_cycle > 100) duty_cycle = 100;
    
    pthread_mutex_lock(&pwm->mutex);
    pwm->duty_cycle = duty_cycle;
    pthread_mutex_unlock(&pwm->mutex);
}

/*
 * Initialize PWM control
 * 
 * @param pwm: PWM control structure to initialize
 * @param line: GPIO line to use for PWM
 * @return: 0 on success, -1 on failure
 */
int pwm_init(pwm_control_t *pwm, struct gpiod_line *line) {
    pwm->line = line;
    pwm->duty_cycle = 0;
    pwm->active = true;
    
    // Initialize mutex for thread safety
    if (pthread_mutex_init(&pwm->mutex, NULL) != 0) {
        perror("Mutex init failed");
        return -1;
    }
    
    // Create PWM thread
    if (pthread_create(&pwm->thread, NULL, pwm_thread, pwm) != 0) {
        perror("Thread creation failed");
        pthread_mutex_destroy(&pwm->mutex);
        return -1;
    }
    
    return 0;
}

/*
 * Cleanup PWM control
 */
void pwm_cleanup(pwm_control_t *pwm) {
    // Stop PWM thread
    pwm->active = false;
    pthread_join(pwm->thread, NULL);
    
    // Cleanup mutex
    pthread_mutex_destroy(&pwm->mutex);
}

/*
 * Animation functions for different LED patterns
 */

// Breathing effect - smooth fade in and out
void breathing_animation(pwm_control_t *pwm) {
    static int brightness = 0;
    static int direction = 1;
    
    brightness += direction * 2;  // Adjust speed here
    
    if (brightness >= 100) {
        brightness = 100;
        direction = -1;
    } else if (brightness <= 0) {
        brightness = 0;
        direction = 1;
    }
    
    set_duty_cycle(pwm, brightness);
}

// Sine wave pattern for smooth periodic brightness
void sine_wave_animation(pwm_control_t *pwm) {
    static float phase = 0.0;
    
    // Calculate brightness using sine function
    // Maps sine wave (-1 to 1) to brightness (0 to 100)
    int brightness = (int)(50 * (1 + sin(phase)));
    
    set_duty_cycle(pwm, brightness);
    
    // Increment phase
    phase += 0.1;  // Adjust for animation speed
    if (phase > 2 * M_PI) {
        phase -= 2 * M_PI;
    }
}

// Strobe effect - rapid on/off
void strobe_animation(pwm_control_t *pwm) {
    static int state = 0;
    static int counter = 0;
    
    if (++counter >= 5) {  // Adjust for strobe speed
        counter = 0;
        state = !state;
        set_duty_cycle(pwm, state ? 100 : 0);
    }
}

/*
 * Main function
 */
int main(void) {
    struct gpiod_chip *chip;
    struct gpiod_line *led_line;
    struct gpiod_line *button_line;
    pwm_control_t pwm;
    int ret;
    
    printf("\n=== Raspberry Pi 5 PWM LED Control ===\n");
    printf("Demonstrates software PWM for LED brightness\n\n");
    
    // Register signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Open GPIO chip
    chip = gpiod_chip_open_by_name(GPIO_CHIP);
    if (!chip) {
        perror("Failed to open GPIO chip");
        return 1;
    }
    
    // Get LED line
    led_line = gpiod_chip_get_line(chip, LED_PIN);
    if (!led_line) {
        perror("Failed to get LED line");
        goto cleanup_chip;
    }
    
    // Get button line
    button_line = gpiod_chip_get_line(chip, BUTTON_PIN);
    if (!button_line) {
        perror("Failed to get button line");
        goto cleanup_chip;
    }
    
    // Configure LED as output
    ret = gpiod_line_request_output(led_line, "pwm-control", 0);
    if (ret < 0) {
        perror("Failed to request LED output");
        goto cleanup_chip;
    }
    
    // Configure button as input with pull-up
    ret = gpiod_line_request_input_flags(button_line, "pwm-control",
                                         GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP);
    if (ret < 0) {
        perror("Failed to request button input");
        goto release_led;
    }
    
    // Initialize PWM
    if (pwm_init(&pwm, led_line) < 0) {
        fprintf(stderr, "Failed to initialize PWM\n");
        goto release_button;
    }
    
    printf("PWM Configuration:\n");
    printf("  Frequency: %d Hz\n", PWM_FREQUENCY);
    printf("  Period: %.2f ms\n", PWM_PERIOD_NS / 1000000.0);
    printf("  Resolution: %d steps\n\n", DUTY_CYCLE_STEPS);
    
    printf("Controls:\n");
    printf("  Press button to cycle through modes\n");
    printf("  Modes: Manual -> Breathing -> Sine Wave -> Strobe\n");
    printf("  Press Ctrl+C to exit\n\n");
    
    // Main control loop
    int last_button_state = 1;
    int animation_counter = 0;
    
    while (running) {
        // Check button for mode change
        int button_state = gpiod_line_get_value(button_line);
        
        // Detect button press (falling edge)
        if (button_state == 0 && last_button_state == 1) {
            current_mode = (current_mode + 1) % 4;
            
            const char *mode_names[] = {
                "Manual (50%)", "Breathing", "Sine Wave", "Strobe"
            };
            printf("Mode: %s\n", mode_names[current_mode]);
        }
        last_button_state = button_state;
        
        // Run animation based on current mode
        if (++animation_counter >= 10) {  // Control animation speed
            animation_counter = 0;
            
            switch (current_mode) {
                case MODE_MANUAL:
                    set_duty_cycle(&pwm, manual_brightness);
                    break;
                    
                case MODE_BREATHING:
                    breathing_animation(&pwm);
                    break;
                    
                case MODE_SINE_WAVE:
                    sine_wave_animation(&pwm);
                    break;
                    
                case MODE_STROBE:
                    strobe_animation(&pwm);
                    break;
            }
        }
        
        usleep(1000);  // 1ms main loop delay
    }
    
    printf("\nCleaning up...\n");
    
    // Cleanup
    pwm_cleanup(&pwm);
    
release_button:
    gpiod_line_release(button_line);
release_led:
    gpiod_line_release(led_line);
cleanup_chip:
    gpiod_chip_close(chip);
    
    printf("PWM control terminated.\n");
    return 0;
}

/*
 * Key concepts demonstrated:
 * 
 * 1. Software PWM Implementation:
 *    - Uses precise timing to create PWM signal
 *    - Separate thread for consistent timing
 *    - Thread-safe duty cycle updates
 * 
 * 2. PWM Theory:
 *    - Frequency determines flicker perception
 *    - Duty cycle controls average power/brightness
 *    - Higher frequency = smoother control
 * 
 * 3. Advanced C Concepts:
 *    - POSIX threads (pthreads)
 *    - Mutexes for thread synchronization
 *    - High-resolution timing
 *    - Function pointers (implicit in pthread_create)
 * 
 * 4. Practical Applications:
 *    - LED dimming
 *    - Motor speed control
 *    - Servo positioning
 *    - Audio generation
 * 
 * Note: For production use, consider hardware PWM pins or
 * kernel PWM drivers for better performance and accuracy.
 */