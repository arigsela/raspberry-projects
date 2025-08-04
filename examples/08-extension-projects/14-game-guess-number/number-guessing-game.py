#!/usr/bin/env python3
"""
Number Guessing Game

Interactive game where players guess a random number using button controls,
LCD feedback, LED indicators, and progressive difficulty levels.
"""

import time
import random
import threading
import json
import os
from datetime import datetime
from enum import Enum
from collections import deque
import math

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602

# Hardware Pin Definitions
# Input Controls
BUTTON_UP_PIN = 17      # Increase guess
BUTTON_DOWN_PIN = 27    # Decrease guess
BUTTON_SELECT_PIN = 22  # Confirm guess
BUTTON_MODE_PIN = 23    # Change game mode

# LED Indicators
LED_HOT_PIN = 5         # Red - Getting warmer
LED_COLD_PIN = 6        # Blue - Getting colder
LED_CORRECT_PIN = 13    # Green - Correct guess
LED_POWER_PIN = 19      # White - Power indicator

# Buzzer for audio feedback
BUZZER_PIN = 26

# 7-Segment Display Pins (optional)
SEG_A_PIN = 16
SEG_B_PIN = 20
SEG_C_PIN = 21
SEG_D_PIN = 12
SEG_E_PIN = 25
SEG_F_PIN = 24
SEG_G_PIN = 18
SEG_DP_PIN = 4

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Game Constants
DEFAULT_MIN = 1
DEFAULT_MAX = 100
MAX_HISTORY = 10
HINT_THRESHOLD = 5
TIME_LIMIT_SECONDS = 60

from gpiozero import LED, Button, Buzzer, PWMLED

class GameMode(Enum):
    """Game difficulty modes"""
    EASY = "Easy"           # 1-50, unlimited guesses
    NORMAL = "Normal"       # 1-100, hints after 5 guesses
    HARD = "Hard"          # 1-200, limited guesses
    EXTREME = "Extreme"     # 1-500, time limit
    CUSTOM = "Custom"       # User-defined range
    BINARY = "Binary"       # Binary search practice

class GameState(Enum):
    """Game state tracking"""
    MENU = "Menu"
    PLAYING = "Playing"
    WON = "Won"
    LOST = "Lost"
    PAUSED = "Paused"
    SETTINGS = "Settings"

class GuessResult(Enum):
    """Result of a guess"""
    TOO_LOW = "Too Low"
    TOO_HIGH = "Too High"
    CORRECT = "Correct!"
    GETTING_WARMER = "Warmer"
    GETTING_COLDER = "Colder"

class SevenSegment:
    """7-segment display controller"""
    
    # Segment patterns for digits 0-9
    PATTERNS = {
        0: [1, 1, 1, 1, 1, 1, 0],  # 0
        1: [0, 1, 1, 0, 0, 0, 0],  # 1
        2: [1, 1, 0, 1, 1, 0, 1],  # 2
        3: [1, 1, 1, 1, 0, 0, 1],  # 3
        4: [0, 1, 1, 0, 0, 1, 1],  # 4
        5: [1, 0, 1, 1, 0, 1, 1],  # 5
        6: [1, 0, 1, 1, 1, 1, 1],  # 6
        7: [1, 1, 1, 0, 0, 0, 0],  # 7
        8: [1, 1, 1, 1, 1, 1, 1],  # 8
        9: [1, 1, 1, 1, 0, 1, 1],  # 9
        '-': [0, 0, 0, 0, 0, 0, 1], # dash
        ' ': [0, 0, 0, 0, 0, 0, 0]  # blank
    }
    
    def __init__(self):
        self.segments = [
            LED(SEG_A_PIN), LED(SEG_B_PIN), LED(SEG_C_PIN),
            LED(SEG_D_PIN), LED(SEG_E_PIN), LED(SEG_F_PIN),
            LED(SEG_G_PIN)
        ]
        self.dp = LED(SEG_DP_PIN)
        
    def display_digit(self, digit):
        """Display a single digit"""
        if digit in self.PATTERNS:
            pattern = self.PATTERNS[digit]
            for i, segment in enumerate(self.segments):
                if pattern[i]:
                    segment.on()
                else:
                    segment.off()
                    
    def clear(self):
        """Clear the display"""
        for segment in self.segments:
            segment.off()
        self.dp.off()
        
    def cleanup(self):
        """Clean up resources"""
        self.clear()
        for segment in self.segments:
            segment.close()
        self.dp.close()

class NumberGuessingGame:
    """Main game controller"""
    
    def __init__(self):
        print("🎲 Initializing Number Guessing Game...")
        
        # Initialize hardware
        self._init_hardware()
        self._init_display()
        
        # Game state
        self.state = GameState.MENU
        self.mode = GameMode.NORMAL
        self.min_number = DEFAULT_MIN
        self.max_number = DEFAULT_MAX
        self.target_number = 0
        self.current_guess = 0
        self.guess_count = 0
        self.guess_history = deque(maxlen=MAX_HISTORY)
        self.start_time = None
        self.time_remaining = 0
        
        # Statistics
        self.total_games = 0
        self.games_won = 0
        self.best_scores = {}  # Best scores by mode
        self.total_guesses = 0
        self.perfect_games = 0  # Won in optimal guesses
        
        # Configuration
        self.config = self._load_configuration()
        self.sound_enabled = self.config.get('sound', True)
        self.hints_enabled = self.config.get('hints', True)
        
        # Threading
        self.running = False
        self.timer_thread = None
        
        # Load high scores
        self._load_high_scores()
        
        print("✅ Number guessing game initialized")
        
    def _init_hardware(self):
        """Initialize hardware components"""
        # Buttons
        self.button_up = Button(BUTTON_UP_PIN, pull_up=True, bounce_time=0.1)
        self.button_down = Button(BUTTON_DOWN_PIN, pull_up=True, bounce_time=0.1)
        self.button_select = Button(BUTTON_SELECT_PIN, pull_up=True, bounce_time=0.1)
        self.button_mode = Button(BUTTON_MODE_PIN, pull_up=True, bounce_time=0.1)
        
        # LEDs
        self.led_hot = LED(LED_HOT_PIN)
        self.led_cold = LED(LED_COLD_PIN)
        self.led_correct = LED(LED_CORRECT_PIN)
        self.led_power = LED(LED_POWER_PIN)
        
        # Buzzer
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # 7-segment display (optional)
        try:
            self.seven_seg = SevenSegment()
            print("✓ 7-segment display initialized")
        except:
            self.seven_seg = None
            print("⚠ 7-segment display not available")
            
        # Button callbacks
        self.button_up.when_pressed = self._handle_up
        self.button_down.when_pressed = self._handle_down
        self.button_select.when_pressed = self._handle_select
        self.button_mode.when_pressed = self._handle_mode
        
        # Power indicator
        self.led_power.on()
        
        print("✓ Hardware initialized")
        
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Number Guess")
            self.lcd.write(1, 0, "Game Ready!")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
            
    def _load_configuration(self):
        """Load game configuration"""
        config_file = "game_config.json"
        default_config = {
            'sound': True,
            'hints': True,
            'difficulty': 'Normal',
            'custom_min': 1,
            'custom_max': 100
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
                    print("✓ Configuration loaded")
        except Exception as e:
            print(f"⚠ Could not load configuration: {e}")
            
        return default_config
        
    def _save_configuration(self):
        """Save current configuration"""
        config_file = "game_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
            
    def _load_high_scores(self):
        """Load high scores from file"""
        scores_file = "high_scores.json"
        try:
            if os.path.exists(scores_file):
                with open(scores_file, 'r') as f:
                    self.best_scores = json.load(f)
                    print("✓ High scores loaded")
        except Exception as e:
            print(f"⚠ Could not load high scores: {e}")
            
    def _save_high_scores(self):
        """Save high scores to file"""
        scores_file = "high_scores.json"
        try:
            with open(scores_file, 'w') as f:
                json.dump(self.best_scores, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save high scores: {e}")
            
    def run(self):
        """Main game loop"""
        print("\n🎮 Number Guessing Game!")
        print("UP/DOWN: Change value")
        print("SELECT: Confirm")
        print("MODE: Change difficulty")
        print("Press Ctrl+C to exit\n")
        
        self.running = True
        self._show_menu()
        
        try:
            while self.running:
                if self.state == GameState.PLAYING:
                    self._update_game_display()
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Exiting game...")
            self.running = False
            
    def _show_menu(self):
        """Show main menu"""
        self.state = GameState.MENU
        self._update_display("Select Mode:", self.mode.value)
        
        # Flash mode LED
        self.led_correct.blink(on_time=0.5, off_time=0.5)
        
    def _handle_up(self):
        """Handle up button press"""
        if self.state == GameState.MENU:
            # Cycle through modes
            modes = list(GameMode)
            current_index = modes.index(self.mode)
            self.mode = modes[(current_index - 1) % len(modes)]
            self._update_display("Select Mode:", self.mode.value)
            self._beep(0.05)
            
        elif self.state == GameState.PLAYING:
            # Increase guess
            self.current_guess = min(self.current_guess + 1, self.max_number)
            self._update_guess_display()
            self._beep(0.02)
            
    def _handle_down(self):
        """Handle down button press"""
        if self.state == GameState.MENU:
            # Cycle through modes
            modes = list(GameMode)
            current_index = modes.index(self.mode)
            self.mode = modes[(current_index + 1) % len(modes)]
            self._update_display("Select Mode:", self.mode.value)
            self._beep(0.05)
            
        elif self.state == GameState.PLAYING:
            # Decrease guess
            self.current_guess = max(self.current_guess - 1, self.min_number)
            self._update_guess_display()
            self._beep(0.02)
            
    def _handle_select(self):
        """Handle select button press"""
        if self.state == GameState.MENU:
            self._start_game()
            
        elif self.state == GameState.PLAYING:
            self._make_guess()
            
        elif self.state in [GameState.WON, GameState.LOST]:
            self._show_menu()
            
    def _handle_mode(self):
        """Handle mode button press"""
        if self.state == GameState.PLAYING:
            # Show hint if available
            if self.hints_enabled and self.guess_count >= HINT_THRESHOLD:
                self._show_hint()
                
        else:
            # Return to menu
            self._show_menu()
            
    def _start_game(self):
        """Start a new game"""
        print(f"\n🎯 Starting {self.mode.value} mode...")
        
        # Stop menu LED
        self.led_correct.off()
        
        # Set game parameters based on mode
        if self.mode == GameMode.EASY:
            self.min_number = 1
            self.max_number = 50
            self.max_guesses = None
            self.time_limit = None
            
        elif self.mode == GameMode.NORMAL:
            self.min_number = 1
            self.max_number = 100
            self.max_guesses = None
            self.time_limit = None
            
        elif self.mode == GameMode.HARD:
            self.min_number = 1
            self.max_number = 200
            self.max_guesses = 10
            self.time_limit = None
            
        elif self.mode == GameMode.EXTREME:
            self.min_number = 1
            self.max_number = 500
            self.max_guesses = 15
            self.time_limit = TIME_LIMIT_SECONDS
            
        elif self.mode == GameMode.CUSTOM:
            self.min_number = self.config['custom_min']
            self.max_number = self.config['custom_max']
            self.max_guesses = None
            self.time_limit = None
            
        elif self.mode == GameMode.BINARY:
            # Binary search practice mode
            self.min_number = 1
            self.max_number = 128
            self.max_guesses = 7  # log2(128)
            self.time_limit = None
            
        # Generate target number
        self.target_number = random.randint(self.min_number, self.max_number)
        self.current_guess = (self.min_number + self.max_number) // 2
        self.guess_count = 0
        self.guess_history.clear()
        self.start_time = time.time()
        
        # Start timer if needed
        if self.time_limit:
            self.time_remaining = self.time_limit
            self.timer_thread = threading.Thread(target=self._timer_countdown, daemon=True)
            self.timer_thread.start()
            
        # Update state
        self.state = GameState.PLAYING
        self.total_games += 1
        
        # Show range
        self._update_display(f"Range: {self.min_number}-{self.max_number}", "Make a guess!")
        time.sleep(2)
        
        # Initial display
        self._update_guess_display()
        
        print(f"Target: {self.target_number} (debug mode)")
        
    def _make_guess(self):
        """Process a guess"""
        self.guess_count += 1
        self.total_guesses += 1
        self.guess_history.append(self.current_guess)
        
        print(f"Guess #{self.guess_count}: {self.current_guess}")
        
        # Check guess
        if self.current_guess == self.target_number:
            self._handle_correct_guess()
            
        elif self.current_guess < self.target_number:
            self._handle_low_guess()
            
        else:
            self._handle_high_guess()
            
        # Check for game over conditions
        if self.state == GameState.PLAYING:
            if self.max_guesses and self.guess_count >= self.max_guesses:
                self._game_over(False)
                
    def _handle_correct_guess(self):
        """Handle correct guess"""
        self.state = GameState.WON
        self.games_won += 1
        
        # Calculate time
        elapsed_time = time.time() - self.start_time
        
        # Check for perfect game (optimal guesses)
        optimal_guesses = math.ceil(math.log2(self.max_number - self.min_number + 1))
        if self.guess_count <= optimal_guesses:
            self.perfect_games += 1
            print("⭐ Perfect game!")
            
        # Update high score
        mode_name = self.mode.value
        if mode_name not in self.best_scores or self.guess_count < self.best_scores[mode_name]:
            self.best_scores[mode_name] = self.guess_count
            self._save_high_scores()
            print("🏆 New high score!")
            
        # Celebration
        self.led_correct.on()
        self.led_hot.off()
        self.led_cold.off()
        
        # Victory sound
        if self.sound_enabled:
            self._play_victory_sound()
            
        # Display result
        self._update_display("🎉 CORRECT! 🎉", f"Guesses: {self.guess_count}")
        
        print(f"✅ Won in {self.guess_count} guesses ({elapsed_time:.1f}s)")
        
    def _handle_low_guess(self):
        """Handle too low guess"""
        # Temperature indicator
        distance_before = abs(self.guess_history[-2] - self.target_number) if len(self.guess_history) > 1 else float('inf')
        distance_now = abs(self.current_guess - self.target_number)
        
        if distance_now < distance_before:
            # Getting warmer
            self.led_hot.on()
            self.led_cold.off()
            result = GuessResult.GETTING_WARMER
            print("🔥 Getting warmer!")
        else:
            # Getting colder
            self.led_hot.off()
            self.led_cold.on()
            result = GuessResult.GETTING_COLDER
            print("❄️ Getting colder!")
            
        self._update_display("Too Low! ⬆", f"Try: {self.current_guess + 1}-{self.max_number}")
        
        # Feedback sound
        if self.sound_enabled:
            self.buzzer.beep(0.1, 0.1, n=1)
            
    def _handle_high_guess(self):
        """Handle too high guess"""
        # Temperature indicator
        distance_before = abs(self.guess_history[-2] - self.target_number) if len(self.guess_history) > 1 else float('inf')
        distance_now = abs(self.current_guess - self.target_number)
        
        if distance_now < distance_before:
            # Getting warmer
            self.led_hot.on()
            self.led_cold.off()
            result = GuessResult.GETTING_WARMER
            print("🔥 Getting warmer!")
        else:
            # Getting colder
            self.led_hot.off()
            self.led_cold.on()
            result = GuessResult.GETTING_COLDER
            print("❄️ Getting colder!")
            
        self._update_display("Too High! ⬇", f"Try: {self.min_number}-{self.current_guess - 1}")
        
        # Feedback sound
        if self.sound_enabled:
            self.buzzer.beep(0.2, 0.1, n=1)
            
    def _show_hint(self):
        """Show a hint"""
        if not self.hints_enabled or self.guess_count < HINT_THRESHOLD:
            return
            
        # Different hints based on distance
        distance = abs(self.current_guess - self.target_number)
        range_size = self.max_number - self.min_number
        
        if distance <= range_size * 0.05:
            hint = "Very close! 🔥🔥🔥"
        elif distance <= range_size * 0.1:
            hint = "Getting warm! 🔥🔥"
        elif distance <= range_size * 0.2:
            hint = "Warmer... 🔥"
        elif distance <= range_size * 0.3:
            hint = "Cold ❄️"
        else:
            hint = "Very cold! ❄️❄️"
            
        # Divisibility hint
        if self.target_number % 2 == 0:
            hint += " (Even)"
        else:
            hint += " (Odd)"
            
        self._update_display("Hint:", hint)
        time.sleep(2)
        self._update_guess_display()
        
    def _timer_countdown(self):
        """Countdown timer for timed modes"""
        while self.running and self.state == GameState.PLAYING and self.time_remaining > 0:
            self.time_remaining -= 1
            time.sleep(1)
            
        if self.state == GameState.PLAYING and self.time_remaining == 0:
            self._game_over(False)
            
    def _game_over(self, won):
        """Handle game over"""
        if won:
            self.state = GameState.WON
        else:
            self.state = GameState.LOST
            
        # Turn off temperature LEDs
        self.led_hot.off()
        self.led_cold.off()
        
        if not won:
            # Show the answer
            self._update_display("Game Over!", f"Answer: {self.target_number}")
            
            # Failure sound
            if self.sound_enabled:
                self.buzzer.beep(0.5, 0.5, n=2)
                
            print(f"❌ Game over! The answer was {self.target_number}")
            
    def _update_guess_display(self):
        """Update display with current guess"""
        # Show current guess and remaining info
        line1 = f"Guess: {self.current_guess}"
        
        # Build second line
        info = []
        if self.max_guesses:
            info.append(f"#{self.guess_count}/{self.max_guesses}")
        else:
            info.append(f"#{self.guess_count}")
            
        if self.time_limit and self.time_remaining:
            info.append(f"{self.time_remaining}s")
            
        line2 = " ".join(info)
        
        self._update_display(line1, line2)
        
        # Update 7-segment if available
        if self.seven_seg:
            # Show last digit of current guess
            digit = self.current_guess % 10
            self.seven_seg.display_digit(digit)
            
    def _update_game_display(self):
        """Update game display during play"""
        if self.state == GameState.PLAYING and self.time_limit:
            # Update timer display
            self._update_guess_display()
            
    def _play_victory_sound(self):
        """Play victory sound sequence"""
        notes = [
            (0.1, 0.05),  # C
            (0.1, 0.05),  # E
            (0.1, 0.05),  # G
            (0.2, 0.0)    # C (higher)
        ]
        
        for duration, pause in notes:
            self.buzzer.on()
            time.sleep(duration)
            self.buzzer.off()
            time.sleep(pause)
            
    def _beep(self, duration=0.05):
        """Simple beep sound"""
        if self.sound_enabled:
            self.buzzer.on()
            time.sleep(duration)
            self.buzzer.off()
            
    def _update_display(self, line1="", line2=""):
        """Update LCD display"""
        if not self.lcd:
            return
            
        try:
            self.lcd.clear()
            self.lcd.write(0, 0, line1[:16])
            self.lcd.write(1, 0, line2[:16])
        except Exception as e:
            print(f"⚠ Display error: {e}")
            
    def get_statistics(self):
        """Get game statistics"""
        win_rate = (self.games_won / self.total_games * 100) if self.total_games > 0 else 0
        avg_guesses = (self.total_guesses / self.games_won) if self.games_won > 0 else 0
        
        return {
            'total_games': self.total_games,
            'games_won': self.games_won,
            'win_rate': win_rate,
            'average_guesses': avg_guesses,
            'perfect_games': self.perfect_games,
            'best_scores': self.best_scores
        }
        
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop game
        self.running = False
        
        # Save configuration and scores
        self._save_configuration()
        self._save_high_scores()
        
        # Clear display
        if self.lcd:
            self.lcd.clear()
            self.lcd.write(0, 0, "Thanks for")
            self.lcd.write(1, 0, "playing!")
            
        # Show statistics
        stats = self.get_statistics()
        print("\n📊 Game Statistics:")
        print(f"  Total games: {stats['total_games']}")
        print(f"  Games won: {stats['games_won']}")
        print(f"  Win rate: {stats['win_rate']:.1f}%")
        print(f"  Average guesses: {stats['average_guesses']:.1f}")
        print(f"  Perfect games: {stats['perfect_games']}")
        
        if self.best_scores:
            print("\n🏆 Best Scores:")
            for mode, score in self.best_scores.items():
                print(f"  {mode}: {score} guesses")
                
        # Clean up hardware
        self.button_up.close()
        self.button_down.close()
        self.button_select.close()
        self.button_mode.close()
        self.led_hot.close()
        self.led_cold.close()
        self.led_correct.close()
        self.led_power.close()
        self.buzzer.close()
        
        if self.seven_seg:
            self.seven_seg.cleanup()
            
        print("\n✅ Cleanup complete")


def game_demo():
    """Demonstrate game features"""
    print("\n🎮 Number Guessing Game Demo")
    print("=" * 50)
    
    # Initialize minimal hardware for demo
    led_hot = LED(LED_HOT_PIN)
    led_cold = LED(LED_COLD_PIN)
    led_correct = LED(LED_CORRECT_PIN)
    buzzer = Buzzer(BUZZER_PIN)
    
    try:
        # Demo 1: Temperature indicators
        print("\n1. Temperature Indicators")
        
        print("Getting warmer...")
        led_hot.on()
        time.sleep(1)
        led_hot.off()
        
        print("Getting colder...")
        led_cold.on()
        time.sleep(1)
        led_cold.off()
        
        print("Correct guess!")
        led_correct.on()
        time.sleep(1)
        led_correct.off()
        
        # Demo 2: Sound effects
        print("\n2. Sound Effects")
        
        print("Button press...")
        buzzer.beep(0.05, 0, n=1)
        time.sleep(0.5)
        
        print("Wrong guess...")
        buzzer.beep(0.1, 0.1, n=2)
        time.sleep(0.5)
        
        print("Victory sound...")
        for _ in range(4):
            buzzer.on()
            time.sleep(0.1)
            buzzer.off()
            time.sleep(0.05)
            
        # Demo 3: Game modes
        print("\n3. Available Game Modes")
        for mode in GameMode:
            print(f"  - {mode.value}")
            
        # Demo 4: Difficulty ranges
        print("\n4. Difficulty Ranges")
        print("  Easy: 1-50")
        print("  Normal: 1-100")
        print("  Hard: 1-200 (10 guesses)")
        print("  Extreme: 1-500 (15 guesses, 60s time)")
        print("  Binary: 1-128 (7 guesses, practice mode)")
        
        print("\n✅ Demo complete!")
        
    finally:
        led_hot.close()
        led_cold.close()
        led_correct.close()
        buzzer.close()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        game_demo()
    else:
        # Normal game
        game = NumberGuessingGame()
        try:
            game.run()
        finally:
            game.cleanup()