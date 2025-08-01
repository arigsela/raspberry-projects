/*
 * Simple GPIO Test - No hardware required
 * Tests if GPIO libraries are properly installed
 */

#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>

int main(void) {
    struct gpiod_chip *chip;
    
    printf("Testing GPIO access on Raspberry Pi 5...\n\n");
    
    // Try to open GPIO chip
    chip = gpiod_chip_open_by_name("gpiochip4");
    if (!chip) {
        printf("ERROR: Cannot open gpiochip4\n");
        printf("Make sure you're running on Raspberry Pi 5\n");
        return 1;
    }
    
    printf("SUCCESS: GPIO chip opened!\n");
    printf("Chip name: %s\n", gpiod_chip_name(chip));
    printf("Number of lines: %d\n", gpiod_chip_num_lines(chip));
    
    // Test reading a few GPIO lines
    printf("\nTesting GPIO line access:\n");
    for (int i = 17; i <= 27; i++) {
        struct gpiod_line *line = gpiod_chip_get_line(chip, i);
        if (line) {
            printf("  GPIO%d: Accessible\n", i);
        } else {
            printf("  GPIO%d: Not accessible\n", i);
        }
    }
    
    gpiod_chip_close(chip);
    
    printf("\nGPIO test completed successfully!\n");
    printf("Your libgpiod installation is working correctly.\n");
    
    return 0;
}