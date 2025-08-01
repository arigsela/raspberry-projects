/*
 * Simple PWM Example - Minimal LED brightness control
 * 
 * This is a simplified version without threads or animations,
 * useful for understanding basic PWM concepts.
 * 
 * Compile: gcc -o simple-pwm simple-pwm.c -lgpiod
 * Run: sudo ./simple-pwm
 */

#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdbool.h>

#define GPIO_CHIP "gpiochip4"
#define LED_PIN 17
#define PWM_FREQUENCY 1000  // 1 kHz

static volatile bool running = true;

void signal_handler(int sig) {
    running = false;
}

int main(void) {
    struct gpiod_chip *chip;
    struct gpiod_line *led_line;
    
    printf("Simple PWM Demo - LED Brightness Control\n\n");
    
    signal(SIGINT, signal_handler);
    
    // Open GPIO chip
    chip = gpiod_chip_open_by_name(GPIO_CHIP);
    if (!chip) {
        perror("Open chip failed");
        return 1;
    }
    
    // Get LED line
    led_line = gpiod_chip_get_line(chip, LED_PIN);
    if (!led_line) {
        perror("Get line failed");
        gpiod_chip_close(chip);
        return 1;
    }
    
    // Request LED as output
    if (gpiod_line_request_output(led_line, "simple-pwm", 0) < 0) {
        perror("Request output failed");
        gpiod_chip_close(chip);
        return 1;
    }
    
    printf("PWM on GPIO%d\n", LED_PIN);
    printf("Watch LED brightness change!\n");
    printf("Press Ctrl+C to exit\n\n");
    
    // Calculate PWM period in microseconds
    int period_us = 1000000 / PWM_FREQUENCY;  // 1000 us for 1 kHz
    
    // Main PWM loop - gradually change brightness
    int brightness = 0;
    int direction = 1;
    
    while (running) {
        // Simple PWM generation
        // Duty cycle determines brightness (0-100%)
        int on_time = (period_us * brightness) / 100;
        int off_time = period_us - on_time;
        
        if (on_time > 0) {
            gpiod_line_set_value(led_line, 1);
            usleep(on_time);
        }
        
        if (off_time > 0) {
            gpiod_line_set_value(led_line, 0);
            usleep(off_time);
        }
        
        // Update brightness every 100 cycles (~100ms)
        static int cycle_count = 0;
        if (++cycle_count >= 100) {
            cycle_count = 0;
            
            brightness += direction * 5;  // 5% steps
            if (brightness >= 100) {
                brightness = 100;
                direction = -1;
            } else if (brightness <= 0) {
                brightness = 0;
                direction = 1;
            }
            
            printf("\rBrightness: %3d%%", brightness);
            fflush(stdout);
        }
    }
    
    printf("\n\nCleaning up...\n");
    
    // Turn off LED and cleanup
    gpiod_line_set_value(led_line, 0);
    gpiod_line_release(led_line);
    gpiod_chip_close(chip);
    
    return 0;
}

/*
 * This simple example demonstrates:
 * 1. Basic PWM without threading
 * 2. Gradual brightness changes
 * 3. How duty cycle affects LED brightness
 * 
 * Limitations:
 * - Less accurate timing than threaded version
 * - Can't do other tasks while generating PWM
 * - More susceptible to timing jitter
 */