"""GUI application for blackjack bot."""
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
import time
from typing import Optional

from config_manager import ConfigManager, OverlayConfig
from strategy_engine import StrategyEngine, Hand, Action
from card_counter import CardCounter, CountingSystem
from screen_reader import ScreenReader, GameState
from overlay import OverlayWindow, CompactOverlay


class BlackjackBotGUI:
    """Main GUI application for the blackjack bot."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack Bot - Optimal Play Assistant")
        self.root.geometry("900x700")

        # Initialize components
        self.config = ConfigManager()
        self.strategy_engine = StrategyEngine(
            dealer_hits_soft_17=self.config.game_rules.dealer_hits_soft_17,
            double_after_split=self.config.game_rules.double_after_split,
            surrender_allowed=self.config.game_rules.surrender_allowed
        )
        self.card_counter = CardCounter(
            system=CountingSystem(self.config.counting.system),
            num_decks=self.config.game_rules.num_decks
        )
        self.screen_reader = ScreenReader(
            dealer_region=self.config.screen.dealer_region,
            player_region=self.config.screen.player_region,
            balance_region=self.config.screen.balance_region,
            bet_region=self.config.screen.bet_region,
            shuffle_region=self.config.screen.shuffle_region
        )

        self.monitoring = False
        self.monitor_thread: Optional[Thread] = None

        # Initialize overlay
        overlay_cfg = OverlayConfig(
            x=self.config.overlay.x,
            y=self.config.overlay.y,
            width=self.config.overlay.width,
            height=self.config.overlay.height,
            opacity=self.config.overlay.opacity,
            always_on_top=self.config.overlay.always_on_top,
            show_count=self.config.overlay.show_count,
            show_betting=self.config.overlay.show_betting,
            compact_mode=self.config.overlay.compact_mode
        )

        if self.config.overlay.compact_mode:
            self.compact_overlay = CompactOverlay(
                x=self.config.overlay.x,
                y=self.config.overlay.y,
                opacity=self.config.overlay.opacity
            )
            self.overlay = None
        else:
            self.overlay = OverlayWindow(config=overlay_cfg)
            self.compact_overlay = None

        if self.config.overlay.enabled:
            if self.overlay:
                self.overlay.show()
            elif self.compact_overlay:
                self.compact_overlay.show()

        self._create_ui()

    def _create_ui(self):
        """Create the user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.main_tab = ttk.Frame(notebook)
        self.config_tab = ttk.Frame(notebook)
        self.calibration_tab = ttk.Frame(notebook)

        notebook.add(self.main_tab, text='Main')
        notebook.add(self.config_tab, text='Configuration')
        notebook.add(self.calibration_tab, text='Calibration')

        self._create_main_tab()
        self._create_config_tab()
        self._create_calibration_tab()

    def _create_main_tab(self):
        """Create main monitoring tab."""
        # Control frame
        control_frame = ttk.LabelFrame(self.main_tab, text="Controls", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)

        self.start_button = ttk.Button(control_frame, text="Start Monitoring",
                                       command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring",
                                      command=self.stop_monitoring, state='disabled')
        self.stop_button.pack(side='left', padx=5)

        ttk.Button(control_frame, text="Reset Count",
                  command=self.reset_count).pack(side='left', padx=5)

        ttk.Button(control_frame, text="Manual Read",
                  command=self.manual_read).pack(side='left', padx=5)

        # Overlay toggle button
        self.overlay_button = ttk.Button(control_frame, text="Show Overlay",
                                        command=self.toggle_overlay)
        self.overlay_button.pack(side='left', padx=5)
        if self.config.overlay.enabled:
            self.overlay_button.config(text="Hide Overlay")

        # Game state frame
        state_frame = ttk.LabelFrame(self.main_tab, text="Current Game State", padding=10)
        state_frame.pack(fill='x', padx=10, pady=5)

        self.dealer_label = ttk.Label(state_frame, text="Dealer Cards: -")
        self.dealer_label.pack(anchor='w')

        self.player_label = ttk.Label(state_frame, text="Player Cards: -")
        self.player_label.pack(anchor='w')

        self.balance_label = ttk.Label(state_frame, text="Balance: $0")
        self.balance_label.pack(anchor='w')

        self.bet_label = ttk.Label(state_frame, text="Current Bet: $0")
        self.bet_label.pack(anchor='w')

        # Recommendation frame
        rec_frame = ttk.LabelFrame(self.main_tab, text="Recommendation", padding=10)
        rec_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.action_label = ttk.Label(rec_frame, text="Action: -",
                                      font=('Arial', 16, 'bold'), foreground='blue')
        self.action_label.pack(pady=10)

        self.reason_text = tk.Text(rec_frame, height=3, wrap='word')
        self.reason_text.pack(fill='x', pady=5)

        # Count information frame
        count_frame = ttk.LabelFrame(self.main_tab, text="Card Counting", padding=10)
        count_frame.pack(fill='x', padx=10, pady=5)

        count_info = ttk.Frame(count_frame)
        count_info.pack(fill='x')

        ttk.Label(count_info, text="Running Count:").grid(row=0, column=0, sticky='w')
        self.running_count_label = ttk.Label(count_info, text="0", font=('Arial', 12, 'bold'))
        self.running_count_label.grid(row=0, column=1, padx=10, sticky='w')

        ttk.Label(count_info, text="True Count:").grid(row=1, column=0, sticky='w')
        self.true_count_label = ttk.Label(count_info, text="0.0", font=('Arial', 12, 'bold'))
        self.true_count_label.grid(row=1, column=1, padx=10, sticky='w')

        ttk.Label(count_info, text="Decks Remaining:").grid(row=0, column=2, padx=20, sticky='w')
        self.decks_remaining_label = ttk.Label(count_info, text="6.0")
        self.decks_remaining_label.grid(row=0, column=3, padx=10, sticky='w')

        ttk.Label(count_info, text="Player Advantage:").grid(row=1, column=2, padx=20, sticky='w')
        self.advantage_label = ttk.Label(count_info, text="0.0%")
        self.advantage_label.grid(row=1, column=3, padx=10, sticky='w')

        # Betting recommendation frame
        bet_frame = ttk.LabelFrame(self.main_tab, text="Betting Recommendation", padding=10)
        bet_frame.pack(fill='x', padx=10, pady=5)

        self.bet_recommendation_label = ttk.Label(bet_frame, text="Recommended Bet: $0",
                                                  font=('Arial', 14, 'bold'), foreground='green')
        self.bet_recommendation_label.pack()

        self.bet_reason_label = ttk.Label(bet_frame, text="")
        self.bet_reason_label.pack()

    def _create_config_tab(self):
        """Create configuration tab."""
        # Game rules section
        rules_frame = ttk.LabelFrame(self.config_tab, text="Game Rules", padding=10)
        rules_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(rules_frame, text="Number of Decks:").grid(row=0, column=0, sticky='w', pady=2)
        self.num_decks_var = tk.IntVar(value=self.config.game_rules.num_decks)
        ttk.Spinbox(rules_frame, from_=1, to=8, textvariable=self.num_decks_var,
                   width=10).grid(row=0, column=1, sticky='w', padx=5)

        self.h17_var = tk.BooleanVar(value=self.config.game_rules.dealer_hits_soft_17)
        ttk.Checkbutton(rules_frame, text="Dealer Hits Soft 17",
                       variable=self.h17_var).grid(row=1, column=0, columnspan=2, sticky='w', pady=2)

        self.das_var = tk.BooleanVar(value=self.config.game_rules.double_after_split)
        ttk.Checkbutton(rules_frame, text="Double After Split Allowed",
                       variable=self.das_var).grid(row=2, column=0, columnspan=2, sticky='w', pady=2)

        self.surrender_var = tk.BooleanVar(value=self.config.game_rules.surrender_allowed)
        ttk.Checkbutton(rules_frame, text="Surrender Allowed",
                       variable=self.surrender_var).grid(row=3, column=0, columnspan=2, sticky='w', pady=2)

        # Betting configuration section
        betting_frame = ttk.LabelFrame(self.config_tab, text="Betting Configuration", padding=10)
        betting_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(betting_frame, text="Minimum Bet:").grid(row=0, column=0, sticky='w', pady=2)
        self.min_bet_var = tk.DoubleVar(value=self.config.betting.min_bet)
        ttk.Entry(betting_frame, textvariable=self.min_bet_var, width=10).grid(row=0, column=1, sticky='w', padx=5)

        ttk.Label(betting_frame, text="Maximum Bet:").grid(row=1, column=0, sticky='w', pady=2)
        self.max_bet_var = tk.DoubleVar(value=self.config.betting.max_bet)
        ttk.Entry(betting_frame, textvariable=self.max_bet_var, width=10).grid(row=1, column=1, sticky='w', padx=5)

        ttk.Label(betting_frame, text="Bankroll:").grid(row=2, column=0, sticky='w', pady=2)
        self.bankroll_var = tk.DoubleVar(value=self.config.betting.bankroll)
        ttk.Entry(betting_frame, textvariable=self.bankroll_var, width=10).grid(row=2, column=1, sticky='w', padx=5)

        ttk.Label(betting_frame, text="Kelly Fraction:").grid(row=3, column=0, sticky='w', pady=2)
        self.kelly_var = tk.DoubleVar(value=self.config.betting.kelly_fraction)
        ttk.Entry(betting_frame, textvariable=self.kelly_var, width=10).grid(row=3, column=1, sticky='w', padx=5)

        # Card counting configuration
        counting_frame = ttk.LabelFrame(self.config_tab, text="Card Counting", padding=10)
        counting_frame.pack(fill='x', padx=10, pady=5)

        self.counting_enabled_var = tk.BooleanVar(value=self.config.counting.enabled)
        ttk.Checkbutton(counting_frame, text="Enable Card Counting",
                       variable=self.counting_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=2)

        ttk.Label(counting_frame, text="Counting System:").grid(row=1, column=0, sticky='w', pady=2)
        self.counting_system_var = tk.StringVar(value=self.config.counting.system)
        ttk.Combobox(counting_frame, textvariable=self.counting_system_var,
                    values=['hi_lo', 'ko', 'omega_ii', 'halves'],
                    state='readonly', width=15).grid(row=1, column=1, sticky='w', padx=5)

        self.auto_reset_var = tk.BooleanVar(value=self.config.counting.auto_reset_on_shuffle)
        ttk.Checkbutton(counting_frame, text="Auto-reset count on shuffle detection",
                       variable=self.auto_reset_var).grid(row=2, column=0, columnspan=2, sticky='w', pady=2)

        ttk.Label(counting_frame, text="Penetration Reset %:").grid(row=3, column=0, sticky='w', pady=2)
        self.penetration_var = tk.DoubleVar(value=self.config.counting.penetration_reset_threshold)
        ttk.Entry(counting_frame, textvariable=self.penetration_var, width=10).grid(row=3, column=1, sticky='w', padx=5)

        # Overlay configuration
        overlay_frame = ttk.LabelFrame(self.config_tab, text="Overlay Window", padding=10)
        overlay_frame.pack(fill='x', padx=10, pady=5)

        self.overlay_enabled_var = tk.BooleanVar(value=self.config.overlay.enabled)
        ttk.Checkbutton(overlay_frame, text="Enable Overlay Window",
                       variable=self.overlay_enabled_var).grid(row=0, column=0, columnspan=2, sticky='w', pady=2)

        self.compact_mode_var = tk.BooleanVar(value=self.config.overlay.compact_mode)
        ttk.Checkbutton(overlay_frame, text="Compact Mode (minimal display)",
                       variable=self.compact_mode_var).grid(row=1, column=0, columnspan=2, sticky='w', pady=2)

        ttk.Label(overlay_frame, text="Opacity (0.1-1.0):").grid(row=2, column=0, sticky='w', pady=2)
        self.opacity_var = tk.DoubleVar(value=self.config.overlay.opacity)
        ttk.Entry(overlay_frame, textvariable=self.opacity_var, width=10).grid(row=2, column=1, sticky='w', padx=5)

        self.always_on_top_var = tk.BooleanVar(value=self.config.overlay.always_on_top)
        ttk.Checkbutton(overlay_frame, text="Always on top",
                       variable=self.always_on_top_var).grid(row=3, column=0, columnspan=2, sticky='w', pady=2)

        self.overlay_show_count_var = tk.BooleanVar(value=self.config.overlay.show_count)
        ttk.Checkbutton(overlay_frame, text="Show card count",
                       variable=self.overlay_show_count_var).grid(row=4, column=0, columnspan=2, sticky='w', pady=2)

        self.overlay_show_betting_var = tk.BooleanVar(value=self.config.overlay.show_betting)
        ttk.Checkbutton(overlay_frame, text="Show betting recommendation",
                       variable=self.overlay_show_betting_var).grid(row=5, column=0, columnspan=2, sticky='w', pady=2)

        # Save button
        ttk.Button(self.config_tab, text="Save Configuration",
                  command=self.save_configuration).pack(pady=10)

    def _create_calibration_tab(self):
        """Create calibration tab."""
        info_label = ttk.Label(self.calibration_tab,
                              text="Configure screen regions for card detection.",
                              font=('Arial', 12))
        info_label.pack(pady=10)

        # Region configuration frames
        regions = [
            ("Dealer Cards", "dealer_region"),
            ("Player Cards", "player_region"),
            ("Balance", "balance_region"),
            ("Bet Amount", "bet_region"),
            ("Shuffle Indicator", "shuffle_region")
        ]

        self.region_vars = {}

        for label, region_key in regions:
            frame = ttk.LabelFrame(self.calibration_tab, text=label, padding=10)
            frame.pack(fill='x', padx=10, pady=5)

            region = getattr(self.config.screen, region_key)
            vars_dict = {}

            for i, (coord, value) in enumerate([('X', region['x']), ('Y', region['y']),
                                                ('Width', region['width']), ('Height', region['height'])]):
                ttk.Label(frame, text=f"{coord}:").grid(row=0, column=i*2, padx=5)
                var = tk.IntVar(value=value)
                vars_dict[coord.lower()] = var
                ttk.Entry(frame, textvariable=var, width=8).grid(row=0, column=i*2+1, padx=5)

            self.region_vars[region_key] = vars_dict

        # Calibration buttons
        button_frame = ttk.Frame(self.calibration_tab)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Test Read Dealer",
                  command=lambda: self.test_read('dealer')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Test Read Player",
                  command=lambda: self.test_read('player')).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Screenshot",
                  command=self.save_screenshot).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Save Regions",
                  command=self.save_regions).pack(side='left', padx=5)

        # Test results
        self.calibration_results = tk.Text(self.calibration_tab, height=10, wrap='word')
        self.calibration_results.pack(fill='both', expand=True, padx=10, pady=5)

    def start_monitoring(self):
        """Start monitoring the game."""
        self.monitoring = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop monitoring the game."""
        self.monitoring = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                self.update_game_state()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)

    def manual_read(self):
        """Manually read and update game state."""
        self.update_game_state()

    def update_game_state(self):
        """Read screen and update all information."""
        try:
            # Read game state
            game_state = self.screen_reader.read_game_state()

            # Check for shuffle/new shoe and auto-reset if enabled
            if game_state.shuffle_detected and self.config.counting.auto_reset_on_shuffle:
                self.card_counter.reset()
                print("Shuffle detected! Count automatically reset to zero.")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Shuffle Detected",
                    "New shoe detected - count has been reset to zero."
                ))

            # Update display
            self.root.after(0, lambda: self._update_display(game_state))

            # Update card count
            if self.config.counting.enabled:
                # Check penetration-based auto-reset
                stats = self.card_counter.get_stats()
                if stats['penetration'] >= self.config.counting.penetration_reset_threshold:
                    self.card_counter.reset()
                    print(f"Penetration threshold ({self.config.counting.penetration_reset_threshold}%) reached. Count reset.")

                # Add new cards to count
                all_cards = game_state.dealer_cards + game_state.player_cards
                for card in all_cards:
                    self.card_counter.count_card(card)

            # Get recommendations
            self._get_recommendations(game_state)

        except Exception as e:
            print(f"Error updating game state: {e}")

    def _update_display(self, game_state: GameState):
        """Update GUI with game state."""
        self.dealer_label.config(text=f"Dealer Cards: {', '.join(game_state.dealer_cards)}")
        self.player_label.config(text=f"Player Cards: {', '.join(game_state.player_cards)}")
        self.balance_label.config(text=f"Balance: ${game_state.balance:.2f}")
        self.bet_label.config(text=f"Current Bet: ${game_state.current_bet:.2f}")

        # Update count information
        if self.config.counting.enabled:
            stats = self.card_counter.get_stats()
            self.running_count_label.config(text=str(stats['running_count']))
            self.true_count_label.config(text=f"{stats['true_count']:.1f}")
            self.decks_remaining_label.config(text=f"{stats['decks_remaining']:.1f}")
            self.advantage_label.config(text=f"{stats['player_advantage']:.2f}%")

    def _get_recommendations(self, game_state: GameState):
        """Get and display play and betting recommendations."""
        if not game_state.player_cards or not game_state.dealer_cards:
            return

        # Get action recommendation
        player_hand = Hand(game_state.player_cards)
        dealer_up = game_state.dealer_cards[0]

        action = self.strategy_engine.get_action(
            player_hand, dealer_up,
            can_double=game_state.can_double,
            can_split=game_state.can_split,
            can_surrender=game_state.can_surrender
        )

        # Display action
        self.root.after(0, lambda: self.action_label.config(text=f"Action: {action.value}"))

        # Add reasoning
        reason = self._get_action_reason(player_hand, dealer_up, action)
        self.root.after(0, lambda: self.reason_text.delete('1.0', 'end'))
        self.root.after(0, lambda: self.reason_text.insert('1.0', reason))

        # Get betting recommendation
        bet_advice = None
        if self.config.counting.enabled:
            bet_advice = self.card_counter.get_betting_advice(
                self.config.betting.min_bet,
                self.config.betting.max_bet,
                game_state.balance,
                self.config.betting.kelly_fraction
            )

            self.root.after(0, lambda: self.bet_recommendation_label.config(
                text=f"Recommended Bet: ${bet_advice['bet']:.2f} ({bet_advice['units']} units)"
            ))
            self.root.after(0, lambda: self.bet_reason_label.config(
                text=bet_advice['reason']
            ))

        # Update overlay if enabled
        self._update_overlay(action, game_state, bet_advice)

    def _get_action_reason(self, hand: Hand, dealer_card: str, action: Action) -> str:
        """Generate explanation for recommended action."""
        reason = f"Player: {hand.value}"
        if hand.is_soft:
            reason += " (soft)"
        if hand.is_pair:
            reason += f" (pair of {hand.pair_card}s)"

        reason += f"\nDealer: {dealer_card}\n\n"

        if action == Action.HIT:
            reason += "HIT: Take another card to improve your hand."
        elif action == Action.STAND:
            reason += "STAND: Your hand is strong enough. Don't risk busting."
        elif action == Action.DOUBLE:
            reason += "DOUBLE: You have the advantage. Double your bet and take one card."
        elif action == Action.SPLIT:
            reason += "SPLIT: Split your pair into two hands for better odds."
        elif action == Action.SURRENDER:
            reason += "SURRENDER: This is a losing hand. Surrender to save half your bet."

        return reason

    def reset_count(self):
        """Reset the card count."""
        self.card_counter.reset()
        self.update_count_display()
        messagebox.showinfo("Reset", "Card count has been reset to zero.")

    def update_count_display(self):
        """Update count display."""
        stats = self.card_counter.get_stats()
        self.running_count_label.config(text=str(stats['running_count']))
        self.true_count_label.config(text=f"{stats['true_count']:.1f}")
        self.decks_remaining_label.config(text=f"{stats['decks_remaining']:.1f}")
        self.advantage_label.config(text=f"{stats['player_advantage']:.2f}%")

    def save_configuration(self):
        """Save configuration from GUI."""
        try:
            self.config.update_game_rules(
                num_decks=self.num_decks_var.get(),
                dealer_hits_soft_17=self.h17_var.get(),
                double_after_split=self.das_var.get(),
                surrender_allowed=self.surrender_var.get()
            )

            self.config.update_betting(
                min_bet=self.min_bet_var.get(),
                max_bet=self.max_bet_var.get(),
                bankroll=self.bankroll_var.get(),
                kelly_fraction=self.kelly_var.get()
            )

            self.config.update_counting(
                enabled=self.counting_enabled_var.get(),
                system=self.counting_system_var.get(),
                auto_reset_on_shuffle=self.auto_reset_var.get(),
                penetration_reset_threshold=self.penetration_var.get()
            )

            self.config.update_overlay(
                enabled=self.overlay_enabled_var.get(),
                compact_mode=self.compact_mode_var.get(),
                opacity=self.opacity_var.get(),
                always_on_top=self.always_on_top_var.get(),
                show_count=self.overlay_show_count_var.get(),
                show_betting=self.overlay_show_betting_var.get()
            )

            # Reinitialize components with new config
            self.strategy_engine = StrategyEngine(
                dealer_hits_soft_17=self.config.game_rules.dealer_hits_soft_17,
                double_after_split=self.config.game_rules.double_after_split,
                surrender_allowed=self.config.game_rules.surrender_allowed
            )
            self.card_counter = CardCounter(
                system=CountingSystem(self.config.counting.system),
                num_decks=self.config.game_rules.num_decks
            )

            messagebox.showinfo("Success", "Configuration saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def test_read(self, region_type: str):
        """Test reading a specific region."""
        try:
            if region_type == 'dealer':
                cards = self.screen_reader.read_dealer_cards()
                result = f"Dealer cards detected: {', '.join(cards) if cards else 'None'}"
            elif region_type == 'player':
                cards = self.screen_reader.read_player_cards()
                result = f"Player cards detected: {', '.join(cards) if cards else 'None'}"
            else:
                result = "Unknown region type"

            self.calibration_results.insert('end', result + '\n')
            self.calibration_results.see('end')
        except Exception as e:
            self.calibration_results.insert('end', f"Error: {e}\n")
            self.calibration_results.see('end')

    def save_screenshot(self):
        """Save calibration screenshot."""
        try:
            self.screen_reader.save_calibration_screenshot()
            self.calibration_results.insert('end', "Screenshot saved to calibration.png\n")
            self.calibration_results.see('end')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save screenshot: {e}")

    def save_regions(self):
        """Save region configurations."""
        try:
            for region_key, vars_dict in self.region_vars.items():
                region = {
                    'x': vars_dict['x'].get(),
                    'y': vars_dict['y'].get(),
                    'width': vars_dict['width'].get(),
                    'height': vars_dict['height'].get()
                }
                setattr(self.config.screen, region_key, region)

            self.config.save()
            self.screen_reader.update_regions(
                dealer=self.config.screen.dealer_region,
                player=self.config.screen.player_region,
                balance=self.config.screen.balance_region,
                bet=self.config.screen.bet_region,
                shuffle=self.config.screen.shuffle_region
            )
            messagebox.showinfo("Success", "Regions saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save regions: {e}")

    def toggle_overlay(self):
        """Toggle overlay window visibility."""
        if self.overlay:
            if self.overlay.is_visible:
                self.overlay.hide()
                self.overlay_button.config(text="Show Overlay")
            else:
                self.overlay.show()
                self.overlay_button.config(text="Hide Overlay")
        elif self.compact_overlay:
            if self.compact_overlay.window.winfo_viewable():
                self.compact_overlay.hide()
                self.overlay_button.config(text="Show Overlay")
            else:
                self.compact_overlay.show()
                self.overlay_button.config(text="Hide Overlay")

    def _update_overlay(self, action: Action, game_state: GameState, bet_advice: dict):
        """Update overlay with current recommendations."""
        if not self.overlay and not self.compact_overlay:
            return

        try:
            if self.config.overlay.compact_mode and self.compact_overlay:
                # Update compact overlay
                stats = self.card_counter.get_stats()
                bet_amount = bet_advice['bet'] if bet_advice else self.config.betting.min_bet
                self.compact_overlay.update(
                    action=action,
                    true_count=stats['true_count'],
                    bet=bet_amount
                )
            elif self.overlay:
                # Update full overlay
                self.overlay.update_action(action)
                self.overlay.update_game_state(game_state.dealer_cards, game_state.player_cards)

                if self.config.counting.enabled:
                    stats = self.card_counter.get_stats()
                    self.overlay.update_count(
                        running_count=stats['running_count'],
                        true_count=stats['true_count'],
                        advantage=stats['player_advantage']
                    )

                if bet_advice:
                    self.overlay.update_betting(
                        bet_amount=bet_advice['bet'],
                        units=bet_advice['units']
                    )
        except Exception as e:
            print(f"Error updating overlay: {e}")

    def run(self):
        """Start the GUI application."""
        # Cleanup overlay on close
        def on_closing():
            if self.overlay:
                self.overlay.destroy()
            if self.compact_overlay:
                self.compact_overlay.destroy()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()


if __name__ == "__main__":
    app = BlackjackBotGUI()
    app.run()
