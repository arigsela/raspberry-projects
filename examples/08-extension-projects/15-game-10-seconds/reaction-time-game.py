#!/usr/bin/env python3
"""
Reaction Time Challenge Game

Test your reflexes with various challenges including 10-second timer,
pattern matching, multi-button sequences, and competitive modes.
"""

import time
import random
import threading
import queue
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import statistics

# Add parent directory to path for shared modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../_shared'))
from lcd1602 import LCD1602

# Hardware Pin Definitions
# Game buttons (4 colored buttons)
BUTTON_RED_PIN = 17
BUTTON_GREEN_PIN = 27
BUTTON_BLUE_PIN = 22
BUTTON_YELLOW_PIN = 23

# Control buttons
BUTTON_START_PIN = 24   # Start/pause game
BUTTON_MODE_PIN = 25    # Change game mode

# LED indicators (match button colors)
LED_RED_PIN = 5
LED_GREEN_PIN = 6
LED_BLUE_PIN = 13
LED_YELLOW_PIN = 19

# Status LEDs
LED_READY_PIN = 16      # White - Ready
LED_ACTIVE_PIN = 20     # Orange - Game active
LED_RECORD_PIN = 21     # Purple - New record

# Buzzer for audio feedback
BUZZER_PIN = 26

# LCD Display
LCD_I2C_ADDRESS = 0x27

# Game Constants
TEN_SECOND_TARGET = 10.0
REACTION_TIMEOUT = 5.0
SEQUENCE_SHOW_TIME = 0.5
SEQUENCE_GAP_TIME = 0.2
MAX_SEQUENCE_LENGTH = 20

from gpiozero import LED, Button, Buzzer, PWMLED

class GameMode(Enum):
    """Available game modes"""
    TEN_SECONDS = "10 Second Timer"      # Stop at exactly 10 seconds
    REACTION = "Reaction Time"          # Single button reaction
    SEQUENCE = "Memory Sequence"        # Simon Says style
    PATTERN = "Pattern Match"           # Match shown pattern
    SPEED = "Speed Test"                # Hit targets quickly
    ENDURANCE = "Endurance"             # How long can you last?
    MULTIPLAYER = "2 Player VS"         # Competitive mode

class GameState(Enum):
    """Game state tracking"""
    MENU = "Menu"
    READY = "Ready"
    COUNTDOWN = "Countdown"
    PLAYING = "Playing"
    SHOWING = "Showing"      # For sequence games
    WAITING = "Waiting"      # For player input
    FINISHED = "Finished"
    GAME_OVER = "Game Over"

class ButtonColor(Enum):
    """Button color mapping"""
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3

class ReactionTimeGame:
    """Main game controller"""
    
    def __init__(self):
        print("⏱️  Initializing Reaction Time Game...")
        
        # Initialize hardware
        self._init_hardware()
        self._init_display()
        
        # Game state
        self.state = GameState.MENU
        self.mode = GameMode.TEN_SECONDS
        self.current_score = 0
        self.high_scores = defaultdict(list)  # High scores by mode
        self.player_stats = defaultdict(dict)  # Player statistics
        
        # Game-specific variables
        self.start_time = None
        self.target_time = None
        self.sequence = []
        self.player_sequence = []
        self.sequence_index = 0
        self.reaction_times = []
        self.round_number = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        
        # Multiplayer
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        
        # Configuration
        self.config = self._load_configuration()
        self.sound_enabled = self.config.get('sound', True)
        self.difficulty = self.config.get('difficulty', 'Normal')
        
        # Threading
        self.running = False
        self.game_thread = None
        self.event_queue = queue.Queue()
        
        # Button mapping
        self.button_colors = [
            ButtonColor.RED, ButtonColor.GREEN,
            ButtonColor.BLUE, ButtonColor.YELLOW
        ]
        
        # Load high scores
        self._load_high_scores()
        
        print("✅ Reaction time game initialized")
        
    def _init_hardware(self):
        """Initialize hardware components"""
        # Game buttons
        self.buttons = [
            Button(BUTTON_RED_PIN, pull_up=True, bounce_time=0.05),
            Button(BUTTON_GREEN_PIN, pull_up=True, bounce_time=0.05),
            Button(BUTTON_BLUE_PIN, pull_up=True, bounce_time=0.05),
            Button(BUTTON_YELLOW_PIN, pull_up=True, bounce_time=0.05)
        ]
        
        # Control buttons
        self.button_start = Button(BUTTON_START_PIN, pull_up=True, bounce_time=0.1)
        self.button_mode = Button(BUTTON_MODE_PIN, pull_up=True, bounce_time=0.1)
        
        # LEDs
        self.leds = [
            LED(LED_RED_PIN),
            LED(LED_GREEN_PIN),
            LED(LED_BLUE_PIN),
            LED(LED_YELLOW_PIN)
        ]
        
        # Status LEDs
        self.led_ready = LED(LED_READY_PIN)
        self.led_active = LED(LED_ACTIVE_PIN)
        self.led_record = LED(LED_RECORD_PIN)
        
        # Buzzer
        self.buzzer = Buzzer(BUZZER_PIN)
        
        # Set up button callbacks
        for i, button in enumerate(self.buttons):
            button.when_pressed = lambda idx=i: self._handle_game_button(idx)
            
        self.button_start.when_pressed = self._handle_start
        self.button_mode.when_pressed = self._handle_mode
        
        # Initial state
        self.led_ready.on()
        
        print("✓ Hardware initialized")
        
    def _init_display(self):
        """Initialize LCD display"""
        try:
            self.lcd = LCD1602(LCD_I2C_ADDRESS)
            self.lcd.clear()
            self.lcd.write(0, 0, "Reaction Game")
            self.lcd.write(1, 0, "Ready!")
            print("✓ LCD display initialized")
        except Exception as e:
            print(f"⚠ LCD initialization failed: {e}")
            self.lcd = None
            
    def _load_configuration(self):
        """Load game configuration"""
        config_file = "reaction_config.json"
        default_config = {
            'sound': True,
            'difficulty': 'Normal',
            'player_name': 'Player1'
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
        config_file = "reaction_config.json"
        try:
            self.config['last_played'] = datetime.now().isoformat()
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save configuration: {e}")
            
    def _load_high_scores(self):
        """Load high scores from file"""
        scores_file = "reaction_scores.json"
        try:
            if os.path.exists(scores_file):
                with open(scores_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to mode-specific high scores
                    for mode, scores in data.items():
                        self.high_scores[mode] = scores
                    print("✓ High scores loaded")
        except Exception as e:
            print(f"⚠ Could not load high scores: {e}")
            
    def _save_high_scores(self):
        """Save high scores to file"""
        scores_file = "reaction_scores.json"
        try:
            # Convert enum keys to strings for JSON
            data = {}
            for mode, scores in self.high_scores.items():
                mode_name = mode.value if isinstance(mode, GameMode) else mode
                # Keep only top 10 scores
                data[mode_name] = sorted(scores, reverse=True)[:10]
                
            with open(scores_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save high scores: {e}")
            
    def run(self):
        """Main game loop"""
        print("\n🎮 Reaction Time Challenge!")
        print("START: Begin game / Select")
        print("MODE: Change game mode")
        print("Press Ctrl+C to exit\n")
        
        self.running = True
        self._show_menu()
        
        try:
            while self.running:
                # Process events
                self._process_events()
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\n⏹ Exiting game...")
            self.running = False
            
    def _show_menu(self):
        """Show game menu"""
        self.state = GameState.MENU
        self._update_display("Select Mode:", self.mode.value[:16])
        
        # Show mode indicator
        self._clear_all_leds()
        self.led_ready.blink(on_time=0.5, off_time=0.5)
        
    def _handle_start(self):
        """Handle start button press"""
        if self.state == GameState.MENU:
            self._start_game()
        elif self.state == GameState.READY:
            self._begin_round()
        elif self.state == GameState.FINISHED:
            self._show_menu()
        elif self.state == GameState.PLAYING:
            # For 10-second game
            if self.mode == GameMode.TEN_SECONDS:
                self._stop_timer()
                
    def _handle_mode(self):
        """Handle mode button press"""
        if self.state == GameState.MENU:
            # Cycle through modes
            modes = list(GameMode)
            current_index = modes.index(self.mode)
            self.mode = modes[(current_index + 1) % len(modes)]
            self._update_display("Select Mode:", self.mode.value[:16])
            self._beep(0.05)
            
    def _handle_game_button(self, button_index):
        """Handle game button press"""
        # Add to event queue for processing
        self.event_queue.put(('button', button_index, time.time()))
        
    def _process_events(self):
        """Process queued events"""
        try:
            while not self.event_queue.empty():
                event = self.event_queue.get_nowait()
                event_type = event[0]
                
                if event_type == 'button':
                    button_index = event[1]
                    timestamp = event[2]
                    self._process_button_press(button_index, timestamp)
                    
        except queue.Empty:
            pass
            
    def _process_button_press(self, button_index, timestamp):
        """Process a button press based on game state"""
        if self.state == GameState.WAITING:
            if self.mode == GameMode.REACTION:
                self._handle_reaction_press(button_index, timestamp)
            elif self.mode == GameMode.SEQUENCE:
                self._handle_sequence_press(button_index)
            elif self.mode == GameMode.PATTERN:
                self._handle_pattern_press(button_index)
            elif self.mode == GameMode.SPEED:
                self._handle_speed_press(button_index, timestamp)
                
    def _start_game(self):
        """Start a new game"""
        print(f"\n🎯 Starting {self.mode.value}...")
        
        # Reset game state
        self.current_score = 0
        self.round_number = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.reaction_times.clear()
        self.sequence.clear()
        self.player_sequence.clear()
        
        # Stop menu LED
        self.led_ready.on()
        
        # Mode-specific initialization
        if self.mode == GameMode.TEN_SECONDS:
            self._init_ten_seconds()
        elif self.mode == GameMode.REACTION:
            self._init_reaction()
        elif self.mode == GameMode.SEQUENCE:
            self._init_sequence()
        elif self.mode == GameMode.PATTERN:
            self._init_pattern()
        elif self.mode == GameMode.SPEED:
            self._init_speed()
        elif self.mode == GameMode.ENDURANCE:
            self._init_endurance()
        elif self.mode == GameMode.MULTIPLAYER:
            self._init_multiplayer()
            
    def _init_ten_seconds(self):
        """Initialize 10-second timer game"""
        self.state = GameState.READY
        self._update_display("Stop at 10 sec!", "Press START")
        self._countdown_beeps(3)
        
    def _init_reaction(self):
        """Initialize reaction time game"""
        self.state = GameState.READY
        self._update_display("Reaction Test", "Get ready...")
        self.game_thread = threading.Thread(target=self._reaction_game_loop, daemon=True)
        self.game_thread.start()
        
    def _init_sequence(self):
        """Initialize sequence memory game"""
        self.state = GameState.READY
        self.sequence = []
        self.round_number = 0
        self._update_display("Memory Game", "Watch pattern")
        self.game_thread = threading.Thread(target=self._sequence_game_loop, daemon=True)
        self.game_thread.start()
        
    def _init_pattern(self):
        """Initialize pattern matching game"""
        self.state = GameState.READY
        self._update_display("Pattern Match", "Copy pattern")
        self.game_thread = threading.Thread(target=self._pattern_game_loop, daemon=True)
        self.game_thread.start()
        
    def _init_speed(self):
        """Initialize speed test game"""
        self.state = GameState.READY
        self.target_count = 20  # Hit 20 targets
        self.targets_hit = 0
        self._update_display("Speed Test", "Hit targets!")
        self.game_thread = threading.Thread(target=self._speed_game_loop, daemon=True)
        self.game_thread.start()
        
    def _init_endurance(self):
        """Initialize endurance game"""
        self.state = GameState.READY
        self._update_display("Endurance", "How long?")
        self.game_thread = threading.Thread(target=self._endurance_game_loop, daemon=True)
        self.game_thread.start()
        
    def _init_multiplayer(self):
        """Initialize 2-player game"""
        self.state = GameState.READY
        self.player1_score = 0
        self.player2_score = 0
        self.current_player = 1
        self._update_display("2 Player Mode", "P1 vs P2")
        self.game_thread = threading.Thread(target=self._multiplayer_game_loop, daemon=True)
        self.game_thread.start()
        
    # Game-specific loops
    def _reaction_game_loop(self):
        """Reaction time test loop"""
        time.sleep(2)  # Initial delay
        
        for round_num in range(5):  # 5 rounds
            if not self.running or self.state == GameState.MENU:
                break
                
            self.round_number = round_num + 1
            
            # Random delay before showing target
            delay = random.uniform(1.5, 4.0)
            time.sleep(delay)
            
            # Show random target
            target = random.randint(0, 3)
            self.leds[target].on()
            self.led_active.on()
            self.target_time = time.time()
            self.state = GameState.WAITING
            
            # Wait for response or timeout
            timeout = time.time() + REACTION_TIMEOUT
            while self.state == GameState.WAITING and time.time() < timeout:
                time.sleep(0.01)
                
            # Turn off target
            self.leds[target].off()
            self.led_active.off()
            
            if self.state == GameState.WAITING:
                # Timeout
                self._update_display("Too slow!", "")
                self.buzzer.beep(0.5, 0, n=1)
                time.sleep(1)
                
            time.sleep(1)  # Gap between rounds
            
        # Game over
        self._reaction_game_over()
        
    def _sequence_game_loop(self):
        """Memory sequence game loop"""
        time.sleep(2)
        
        while self.running and self.state != GameState.MENU and self.lives > 0:
            self.round_number += 1
            
            # Add new color to sequence
            self.sequence.append(random.randint(0, 3))
            
            # Show sequence
            self._update_display(f"Round {self.round_number}", f"Length: {len(self.sequence)}")
            time.sleep(1)
            
            self.state = GameState.SHOWING
            for color in self.sequence:
                if not self.running:
                    break
                self.leds[color].on()
                if self.sound_enabled:
                    self._play_tone(color)
                time.sleep(SEQUENCE_SHOW_TIME)
                self.leds[color].off()
                time.sleep(SEQUENCE_GAP_TIME)
                
            # Player's turn
            self.state = GameState.WAITING
            self.player_sequence.clear()
            self.sequence_index = 0
            self._update_display("Your turn!", f"Lives: {self.lives}")
            
            # Wait for player to complete sequence
            timeout = time.time() + (len(self.sequence) * 2 + 5)
            while (self.state == GameState.WAITING and 
                   len(self.player_sequence) < len(self.sequence) and 
                   time.time() < timeout):
                time.sleep(0.01)
                
            # Check if correct
            if self.player_sequence == self.sequence:
                self.current_score += len(self.sequence) * 10
                self._update_display("Correct!", f"Score: {self.current_score}")
                self._play_success_sound()
                time.sleep(1)
            else:
                self.lives -= 1
                self._update_display("Wrong!", f"Lives: {self.lives}")
                self.buzzer.beep(0.5, 0, n=1)
                time.sleep(1)
                
            if len(self.sequence) >= MAX_SEQUENCE_LENGTH:
                break
                
        # Game over
        self._sequence_game_over()
        
    def _pattern_game_loop(self):
        """Pattern matching game loop"""
        patterns = [
            [0, 1, 2, 3],  # Sequential
            [0, 2, 1, 3],  # Cross pattern
            [0, 0, 1, 1],  # Doubles
            [0, 1, 0, 1],  # Alternating
            [3, 2, 1, 0],  # Reverse
            [0, 1, 2, 1],  # Up and back
            [0, 3, 1, 2],  # Diagonal
            [2, 2, 3, 3],  # Bottom doubles
        ]
        
        time.sleep(2)
        rounds_completed = 0
        
        while self.running and self.state != GameState.MENU and rounds_completed < 10:
            # Select random pattern
            pattern = random.choice(patterns)
            
            # Show pattern
            self._update_display("Watch pattern", "")
            self.state = GameState.SHOWING
            
            for color in pattern:
                if not self.running:
                    break
                self.leds[color].on()
                if self.sound_enabled:
                    self._play_tone(color)
                time.sleep(0.4)
                self.leds[color].off()
                time.sleep(0.2)
                
            # Player's turn
            self.state = GameState.WAITING
            self.player_sequence.clear()
            self._update_display("Copy pattern!", f"Round: {rounds_completed + 1}")
            
            # Wait for player input
            timeout = time.time() + 10
            while (self.state == GameState.WAITING and 
                   len(self.player_sequence) < len(pattern) and 
                   time.time() < timeout):
                time.sleep(0.01)
                
            # Check if correct
            if self.player_sequence == pattern:
                rounds_completed += 1
                self.current_score += 50
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                self._update_display("Perfect!", f"Combo: {self.combo}")
                self._play_success_sound()
            else:
                self.combo = 0
                self._update_display("Wrong!", "Try again")
                self.buzzer.beep(0.5, 0, n=1)
                
            time.sleep(1.5)
            
        # Game over
        self._pattern_game_over()
        
    def _speed_game_loop(self):
        """Speed test game loop"""
        time.sleep(2)
        
        self.targets_hit = 0
        start_time = time.time()
        
        while self.running and self.state != GameState.MENU and self.targets_hit < self.target_count:
            # Show random target
            target = random.randint(0, 3)
            self.leds[target].on()
            self.state = GameState.WAITING
            self.current_target = target
            
            # Wait for correct hit
            timeout = time.time() + 2
            hit = False
            
            while time.time() < timeout:
                if not self.running:
                    break
                    
                # Check event queue for button press
                try:
                    while not self.event_queue.empty():
                        event = self.event_queue.get_nowait()
                        if event[0] == 'button' and event[1] == target:
                            hit = True
                            self.targets_hit += 1
                            break
                except queue.Empty:
                    pass
                    
                if hit:
                    break
                    
                time.sleep(0.001)
                
            self.leds[target].off()
            
            if hit:
                self._beep(0.05)
                self._update_display(f"Hits: {self.targets_hit}/{self.target_count}", 
                                   f"Time: {time.time() - start_time:.1f}s")
            else:
                self.buzzer.beep(0.2, 0, n=1)
                
            time.sleep(0.1)  # Brief gap
            
        # Calculate final time
        total_time = time.time() - start_time
        self.current_score = int(1000 / total_time) if self.targets_hit == self.target_count else 0
        
        # Game over
        self._speed_game_over(total_time)
        
    def _endurance_game_loop(self):
        """Endurance game loop"""
        time.sleep(2)
        
        start_time = time.time()
        speed_multiplier = 1.0
        correct_hits = 0
        
        while self.running and self.state != GameState.MENU:
            # Show random target
            target = random.randint(0, 3)
            self.leds[target].on()
            self.state = GameState.WAITING
            
            # Time limit decreases with difficulty
            time_limit = max(0.5, 2.0 / speed_multiplier)
            timeout = time.time() + time_limit
            hit_correct = False
            
            while time.time() < timeout:
                if not self.running:
                    break
                    
                # Check for button press
                try:
                    while not self.event_queue.empty():
                        event = self.event_queue.get_nowait()
                        if event[0] == 'button':
                            if event[1] == target:
                                hit_correct = True
                                correct_hits += 1
                            else:
                                # Wrong button - game over
                                self.state = GameState.FINISHED
                            break
                except queue.Empty:
                    pass
                    
                if hit_correct or self.state == GameState.FINISHED:
                    break
                    
                time.sleep(0.001)
                
            self.leds[target].off()
            
            if self.state == GameState.FINISHED:
                break
                
            if not hit_correct:
                # Timeout - game over
                break
                
            # Increase difficulty
            speed_multiplier += 0.05
            
            # Update display
            elapsed = time.time() - start_time
            self._update_display(f"Time: {elapsed:.1f}s", f"Hits: {correct_hits}")
            self._beep(0.05)
            
            time.sleep(0.1)
            
        # Game over
        total_time = time.time() - start_time
        self.current_score = int(total_time * 10)
        self._endurance_game_over(total_time, correct_hits)
        
    def _multiplayer_game_loop(self):
        """2-player competitive mode"""
        time.sleep(2)
        
        rounds = 5  # Best of 5
        
        for round_num in range(rounds):
            if not self.running or self.state == GameState.MENU:
                break
                
            # Alternate players
            for player in [1, 2]:
                self.current_player = player
                self._update_display(f"Player {player}", "Get ready!")
                time.sleep(2)
                
                # Random delay
                delay = random.uniform(1.5, 3.5)
                time.sleep(delay)
                
                # Show target
                target = random.randint(0, 3)
                self.leds[target].on()
                self.led_active.on()
                start_time = time.time()
                self.state = GameState.WAITING
                
                # Wait for response
                timeout = time.time() + REACTION_TIMEOUT
                reacted = False
                
                while time.time() < timeout:
                    if not self.running:
                        break
                        
                    # Check for correct button
                    try:
                        while not self.event_queue.empty():
                            event = self.event_queue.get_nowait()
                            if event[0] == 'button' and event[1] == target:
                                reaction_time = event[2] - start_time
                                reacted = True
                                break
                    except queue.Empty:
                        pass
                        
                    if reacted:
                        break
                        
                    time.sleep(0.001)
                    
                self.leds[target].off()
                self.led_active.off()
                
                # Update scores
                if reacted:
                    score = int(1000 / reaction_time)
                    if player == 1:
                        self.player1_score += score
                    else:
                        self.player2_score += score
                    self._update_display(f"P{player}: {reaction_time:.3f}s", f"Score: {score}")
                else:
                    self._update_display(f"P{player}: Missed!", "No points")
                    
                time.sleep(2)
                
            # Show current scores
            self._update_display(f"P1: {self.player1_score}", f"P2: {self.player2_score}")
            time.sleep(2)
            
        # Determine winner
        self._multiplayer_game_over()
        
    def _begin_round(self):
        """Begin a game round"""
        if self.mode == GameMode.TEN_SECONDS:
            self.state = GameState.PLAYING
            self.start_time = time.time()
            self.led_active.on()
            self._update_display("Timer running...", "Stop at 10!")
            
    def _stop_timer(self):
        """Stop the 10-second timer"""
        if self.state == GameState.PLAYING and self.mode == GameMode.TEN_SECONDS:
            elapsed = time.time() - self.start_time
            self.state = GameState.FINISHED
            self.led_active.off()
            
            # Calculate score
            difference = abs(elapsed - TEN_SECOND_TARGET)
            
            if difference < 0.05:
                result = "PERFECT!"
                score = 1000
                self.led_record.on()
                self._play_fanfare()
            elif difference < 0.1:
                result = "Excellent!"
                score = 500
                self._play_success_sound()
            elif difference < 0.5:
                result = "Good!"
                score = 100
                self._beep(0.1)
            elif difference < 1.0:
                result = "OK"
                score = 50
                self._beep(0.2)
            else:
                result = "Try again"
                score = 10
                self.buzzer.beep(0.5, 0, n=1)
                
            self.current_score = score
            self._update_display(f"{elapsed:.3f}s - {result}", f"Score: {score}")
            
            # Update high score
            self._update_high_score(GameMode.TEN_SECONDS, score)
            
            print(f"Time: {elapsed:.3f}s, Difference: {difference:.3f}s, Score: {score}")
            
    def _handle_reaction_press(self, button_index, timestamp):
        """Handle button press in reaction mode"""
        if hasattr(self, 'target_time'):
            reaction_time = timestamp - self.target_time
            self.reaction_times.append(reaction_time * 1000)  # Convert to ms
            self.state = GameState.PLAYING
            
            self._update_display(f"React: {reaction_time*1000:.0f}ms", f"Round {self.round_number}/5")
            self._beep(0.05)
            
    def _handle_sequence_press(self, button_index):
        """Handle button press in sequence mode"""
        self.player_sequence.append(button_index)
        
        # Light up the pressed button
        self.leds[button_index].on()
        if self.sound_enabled:
            self._play_tone(button_index)
        time.sleep(0.2)
        self.leds[button_index].off()
        
        # Check if wrong
        if self.player_sequence[len(self.player_sequence)-1] != self.sequence[len(self.player_sequence)-1]:
            self.state = GameState.PLAYING  # Wrong sequence
            
    def _handle_pattern_press(self, button_index):
        """Handle button press in pattern mode"""
        self.player_sequence.append(button_index)
        
        # Visual feedback
        self.leds[button_index].on()
        if self.sound_enabled:
            self._play_tone(button_index)
        time.sleep(0.2)
        self.leds[button_index].off()
        
    def _handle_speed_press(self, button_index, timestamp):
        """Handle button press in speed mode"""
        # Handled in the game loop via event queue
        pass
        
    # Game over handlers
    def _reaction_game_over(self):
        """Handle reaction game over"""
        if self.reaction_times:
            avg_time = statistics.mean(self.reaction_times)
            best_time = min(self.reaction_times)
            
            self.current_score = int(10000 / avg_time)
            
            self._update_display(f"Avg: {avg_time:.0f}ms", f"Best: {best_time:.0f}ms")
            self._update_high_score(GameMode.REACTION, self.current_score)
            
            print(f"Average reaction: {avg_time:.0f}ms, Best: {best_time:.0f}ms")
        else:
            self._update_display("No reactions", "Too slow!")
            
        self.state = GameState.FINISHED
        self._play_game_over_sound()
        
    def _sequence_game_over(self):
        """Handle sequence game over"""
        self._update_display("Game Over!", f"Score: {self.current_score}")
        self._update_high_score(GameMode.SEQUENCE, self.current_score)
        self.state = GameState.FINISHED
        self._play_game_over_sound()
        
        print(f"Sequence game: Score {self.current_score}, Max length: {len(self.sequence)}")
        
    def _pattern_game_over(self):
        """Handle pattern game over"""
        bonus = self.max_combo * 20
        self.current_score += bonus
        
        self._update_display(f"Score: {self.current_score}", f"Best combo: {self.max_combo}")
        self._update_high_score(GameMode.PATTERN, self.current_score)
        self.state = GameState.FINISHED
        self._play_game_over_sound()
        
        print(f"Pattern game: Score {self.current_score}, Max combo: {self.max_combo}")
        
    def _speed_game_over(self, total_time):
        """Handle speed game over"""
        if self.targets_hit == self.target_count:
            self._update_display(f"Time: {total_time:.2f}s", f"Score: {self.current_score}")
            self._play_fanfare()
        else:
            self._update_display("Incomplete!", f"Hit: {self.targets_hit}/{self.target_count}")
            
        self._update_high_score(GameMode.SPEED, self.current_score)
        self.state = GameState.FINISHED
        
        print(f"Speed test: {self.targets_hit} hits in {total_time:.2f}s")
        
    def _endurance_game_over(self, total_time, hits):
        """Handle endurance game over"""
        self._update_display(f"Time: {total_time:.1f}s", f"Score: {self.current_score}")
        self._update_high_score(GameMode.ENDURANCE, self.current_score)
        self.state = GameState.FINISHED
        self._play_game_over_sound()
        
        print(f"Endurance: Lasted {total_time:.1f}s with {hits} hits")
        
    def _multiplayer_game_over(self):
        """Handle multiplayer game over"""
        if self.player1_score > self.player2_score:
            winner = "Player 1 Wins!"
        elif self.player2_score > self.player1_score:
            winner = "Player 2 Wins!"
        else:
            winner = "It's a tie!"
            
        self._update_display(winner, f"{self.player1_score} - {self.player2_score}")
        self.state = GameState.FINISHED
        self._play_fanfare() if winner != "It's a tie!" else self._play_game_over_sound()
        
        print(f"Multiplayer: P1={self.player1_score}, P2={self.player2_score}")
        
    # Helper methods
    def _update_high_score(self, mode, score):
        """Update high score for a mode"""
        mode_name = mode.value if isinstance(mode, GameMode) else mode
        
        if mode_name not in self.high_scores:
            self.high_scores[mode_name] = []
            
        self.high_scores[mode_name].append(score)
        self.high_scores[mode_name] = sorted(self.high_scores[mode_name], reverse=True)[:10]
        
        # Check if new high score
        if score == self.high_scores[mode_name][0]:
            self.led_record.blink(on_time=0.2, off_time=0.2, n=5)
            print(f"🏆 New high score for {mode_name}: {score}!")
            
        self._save_high_scores()
        
    def _clear_all_leds(self):
        """Turn off all LEDs"""
        for led in self.leds:
            led.off()
        self.led_active.off()
        self.led_record.off()
        
    def _countdown_beeps(self, count):
        """Play countdown beeps"""
        for i in range(count):
            self._beep(0.1)
            time.sleep(0.5)
            
    def _play_tone(self, button_index):
        """Play a tone for button press"""
        # Different tone for each button
        tones = [0.1, 0.15, 0.2, 0.25]
        self.buzzer.on()
        time.sleep(tones[button_index])
        self.buzzer.off()
        
    def _play_success_sound(self):
        """Play success sound"""
        if self.sound_enabled:
            for _ in range(2):
                self.buzzer.on()
                time.sleep(0.05)
                self.buzzer.off()
                time.sleep(0.05)
                
    def _play_fanfare(self):
        """Play victory fanfare"""
        if self.sound_enabled:
            notes = [0.1, 0.1, 0.1, 0.2]
            for note in notes:
                self.buzzer.on()
                time.sleep(note)
                self.buzzer.off()
                time.sleep(0.05)
                
    def _play_game_over_sound(self):
        """Play game over sound"""
        if self.sound_enabled:
            self.buzzer.beep(0.3, 0.1, n=3)
            
    def _beep(self, duration=0.05):
        """Simple beep"""
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
        total_games = sum(len(scores) for scores in self.high_scores.values())
        
        stats = {
            'total_games': total_games,
            'modes_played': list(self.high_scores.keys()),
            'best_scores': {}
        }
        
        for mode, scores in self.high_scores.items():
            if scores:
                stats['best_scores'][mode] = scores[0]
                
        return stats
        
    def cleanup(self):
        """Clean up resources"""
        print("\n🧹 Cleaning up...")
        
        # Stop game
        self.running = False
        
        # Save data
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
        print(f"  Total games played: {stats['total_games']}")
        
        if stats['best_scores']:
            print("\n🏆 Best Scores:")
            for mode, score in stats['best_scores'].items():
                print(f"  {mode}: {score}")
                
        # Clean up hardware
        self._clear_all_leds()
        
        for button in self.buttons:
            button.close()
        self.button_start.close()
        self.button_mode.close()
        
        for led in self.leds:
            led.close()
        self.led_ready.close()
        self.led_active.close()
        self.led_record.close()
        
        self.buzzer.close()
        
        print("\n✅ Cleanup complete")


def reaction_demo():
    """Demonstrate reaction game features"""
    print("\n🎮 Reaction Time Game Demo")
    print("=" * 50)
    
    # Initialize minimal hardware for demo
    leds = [LED(LED_RED_PIN), LED(LED_GREEN_PIN), LED(LED_BLUE_PIN), LED(LED_YELLOW_PIN)]
    buzzer = Buzzer(BUZZER_PIN)
    
    try:
        # Demo 1: Button colors
        print("\n1. Button Color Indicators")
        colors = ["Red", "Green", "Blue", "Yellow"]
        for i, (led, color) in enumerate(zip(leds, colors)):
            print(f"  {color} button...")
            led.on()
            time.sleep(0.5)
            led.off()
            time.sleep(0.2)
            
        # Demo 2: Reaction sequence
        print("\n2. Reaction Test Sequence")
        print("  Random delay...")
        time.sleep(random.uniform(1, 2))
        target = random.randint(0, 3)
        print(f"  Target: {colors[target]}!")
        leds[target].on()
        buzzer.beep(0.1, 0, n=1)
        time.sleep(1)
        leds[target].off()
        
        # Demo 3: Memory sequence
        print("\n3. Memory Sequence")
        sequence = [0, 2, 1, 3]
        print("  Watch the pattern...")
        for idx in sequence:
            leds[idx].on()
            time.sleep(0.4)
            leds[idx].off()
            time.sleep(0.2)
            
        # Demo 4: Victory celebration
        print("\n4. Victory Celebration")
        for _ in range(3):
            for led in leds:
                led.on()
            buzzer.on()
            time.sleep(0.1)
            for led in leds:
                led.off()
            buzzer.off()
            time.sleep(0.1)
            
        print("\n✅ Demo complete!")
        
    finally:
        for led in leds:
            led.close()
        buzzer.close()


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        reaction_demo()
    else:
        # Normal game
        game = ReactionTimeGame()
        try:
            game.run()
        finally:
            game.cleanup()