"""Overlay window for blackjack bot - displays recommendations on top of game."""
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict
from dataclasses import dataclass

from strategy_engine import Action


@dataclass
class OverlayConfig:
    """Configuration for overlay window."""
    x: int = 100
    y: int = 100
    width: int = 300
    height: int = 250
    opacity: float = 0.85
    always_on_top: bool = True
    show_count: bool = True
    show_betting: bool = True
    show_stats: bool = True
    font_size: int = 11
    compact_mode: bool = False


class OverlayWindow:
    """Transparent overlay window that displays bot recommendations."""

    # Color schemes for different actions
    ACTION_COLORS = {
        Action.HIT: '#FFA500',      # Orange
        Action.STAND: '#4CAF50',    # Green
        Action.DOUBLE: '#2196F3',   # Blue
        Action.SPLIT: '#9C27B0',    # Purple
        Action.SURRENDER: '#F44336' # Red
    }

    def __init__(self, config: OverlayConfig = None):
        self.config = config or OverlayConfig()
        self.window: Optional[tk.Toplevel] = None
        self.is_visible = False
        self.is_dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        # Data to display
        self.current_action = None
        self.dealer_cards = []
        self.player_cards = []
        self.running_count = 0
        self.true_count = 0.0
        self.recommended_bet = 0.0
        self.bet_units = 1
        self.player_advantage = 0.0

        self._create_window()

    def _create_window(self):
        """Create the overlay window."""
        self.window = tk.Toplevel()
        self.window.title("Blackjack Assistant")

        # Set window properties
        self.window.geometry(f"{self.config.width}x{self.config.height}+{self.config.x}+{self.config.y}")
        self.window.attributes('-alpha', self.config.opacity)

        if self.config.always_on_top:
            self.window.attributes('-topmost', True)

        # Remove window decorations for cleaner look (optional)
        # self.window.overrideredirect(True)

        # Make window background dark
        self.window.configure(bg='#1e1e1e')

        # Bind drag events
        self.window.bind('<Button-1>', self._start_drag)
        self.window.bind('<B1-Motion>', self._on_drag)
        self.window.bind('<ButtonRelease-1>', self._stop_drag)

        self._create_widgets()

        # Hide initially
        self.window.withdraw()

    def _create_widgets(self):
        """Create overlay widgets."""
        main_frame = tk.Frame(self.window, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Title bar with close button
        title_frame = tk.Frame(main_frame, bg='#1e1e1e')
        title_frame.pack(fill='x', pady=(0, 10))

        title_label = tk.Label(title_frame, text="🎰 Blackjack Assistant",
                              font=('Arial', 12, 'bold'),
                              bg='#1e1e1e', fg='#ffffff')
        title_label.pack(side='left')

        close_btn = tk.Button(title_frame, text="×", command=self.hide,
                             font=('Arial', 16), bg='#1e1e1e', fg='#ffffff',
                             bd=0, padx=5, cursor='hand2')
        close_btn.pack(side='right')

        # Action recommendation (large and prominent)
        self.action_frame = tk.Frame(main_frame, bg='#2196F3', relief='raised', bd=2)
        self.action_frame.pack(fill='x', pady=(0, 10))

        self.action_label = tk.Label(self.action_frame, text="STAND",
                                     font=('Arial', 20, 'bold'),
                                     bg='#2196F3', fg='#ffffff', pady=10)
        self.action_label.pack()

        # Game state
        game_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='flat')
        game_frame.pack(fill='x', pady=(0, 10))

        self.dealer_label = tk.Label(game_frame, text="Dealer: -",
                                     font=('Arial', self.config.font_size),
                                     bg='#2d2d2d', fg='#ffffff', anchor='w')
        self.dealer_label.pack(fill='x', padx=5, pady=2)

        self.player_label = tk.Label(game_frame, text="Player: -",
                                     font=('Arial', self.config.font_size),
                                     bg='#2d2d2d', fg='#ffffff', anchor='w')
        self.player_label.pack(fill='x', padx=5, pady=2)

        # Count information
        if self.config.show_count:
            count_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='flat')
            count_frame.pack(fill='x', pady=(0, 10))

            count_grid = tk.Frame(count_frame, bg='#2d2d2d')
            count_grid.pack(fill='x', padx=5, pady=5)

            tk.Label(count_grid, text="RC:", font=('Arial', self.config.font_size),
                    bg='#2d2d2d', fg='#aaaaaa').grid(row=0, column=0, sticky='w')
            self.rc_label = tk.Label(count_grid, text="0",
                                    font=('Arial', self.config.font_size, 'bold'),
                                    bg='#2d2d2d', fg='#4CAF50')
            self.rc_label.grid(row=0, column=1, sticky='w', padx=5)

            tk.Label(count_grid, text="TC:", font=('Arial', self.config.font_size),
                    bg='#2d2d2d', fg='#aaaaaa').grid(row=0, column=2, sticky='w', padx=(10, 0))
            self.tc_label = tk.Label(count_grid, text="0.0",
                                    font=('Arial', self.config.font_size, 'bold'),
                                    bg='#2d2d2d', fg='#4CAF50')
            self.tc_label.grid(row=0, column=3, sticky='w', padx=5)

            tk.Label(count_grid, text="Edge:", font=('Arial', self.config.font_size),
                    bg='#2d2d2d', fg='#aaaaaa').grid(row=1, column=0, sticky='w')
            self.edge_label = tk.Label(count_grid, text="0.0%",
                                       font=('Arial', self.config.font_size, 'bold'),
                                       bg='#2d2d2d', fg='#4CAF50')
            self.edge_label.grid(row=1, column=1, columnspan=3, sticky='w', padx=5)

        # Betting recommendation
        if self.config.show_betting:
            bet_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='flat')
            bet_frame.pack(fill='x')

            tk.Label(bet_frame, text="Recommended Bet:",
                    font=('Arial', self.config.font_size),
                    bg='#2d2d2d', fg='#aaaaaa').pack(anchor='w', padx=5, pady=(5, 0))

            self.bet_label = tk.Label(bet_frame, text="$10 (1 unit)",
                                     font=('Arial', self.config.font_size + 2, 'bold'),
                                     bg='#2d2d2d', fg='#FFC107')
            self.bet_label.pack(anchor='w', padx=5, pady=(0, 5))

    def _start_drag(self, event):
        """Start dragging the window."""
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        """Handle window dragging."""
        if self.is_dragging:
            x = self.window.winfo_x() + event.x - self.drag_start_x
            y = self.window.winfo_y() + event.y - self.drag_start_y
            self.window.geometry(f"+{x}+{y}")
            self.config.x = x
            self.config.y = y

    def _stop_drag(self, event):
        """Stop dragging the window."""
        self.is_dragging = False

    def update_action(self, action: Action):
        """Update the recommended action."""
        if not self.is_visible or not self.window:
            return

        self.current_action = action
        action_text = action.value if action else "WAIT"

        # Update action label
        self.action_label.config(text=action_text)

        # Update color based on action
        color = self.ACTION_COLORS.get(action, '#666666')
        self.action_frame.config(bg=color)
        self.action_label.config(bg=color)

    def update_game_state(self, dealer_cards: list, player_cards: list):
        """Update displayed game state."""
        if not self.is_visible or not self.window:
            return

        self.dealer_cards = dealer_cards
        self.player_cards = player_cards

        dealer_text = f"Dealer: {', '.join(dealer_cards) if dealer_cards else '-'}"
        player_text = f"Player: {', '.join(player_cards) if player_cards else '-'}"

        self.dealer_label.config(text=dealer_text)
        self.player_label.config(text=player_text)

    def update_count(self, running_count: int, true_count: float, advantage: float):
        """Update count information."""
        if not self.is_visible or not self.window or not self.config.show_count:
            return

        self.running_count = running_count
        self.true_count = true_count
        self.player_advantage = advantage

        self.rc_label.config(text=str(running_count))
        self.tc_label.config(text=f"{true_count:.1f}")
        self.edge_label.config(text=f"{advantage:.2f}%")

        # Color code based on count
        if true_count >= 2:
            color = '#4CAF50'  # Green (good)
        elif true_count <= -1:
            color = '#F44336'  # Red (bad)
        else:
            color = '#FFC107'  # Yellow (neutral)

        self.rc_label.config(fg=color)
        self.tc_label.config(fg=color)
        self.edge_label.config(fg=color)

    def update_betting(self, bet_amount: float, units: int):
        """Update betting recommendation."""
        if not self.is_visible or not self.window or not self.config.show_betting:
            return

        self.recommended_bet = bet_amount
        self.bet_units = units

        self.bet_label.config(text=f"${bet_amount:.2f} ({units} unit{'s' if units != 1 else ''})")

    def show(self):
        """Show the overlay window."""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.is_visible = True

    def hide(self):
        """Hide the overlay window."""
        if self.window:
            self.window.withdraw()
            self.is_visible = False

    def toggle(self):
        """Toggle overlay visibility."""
        if self.is_visible:
            self.hide()
        else:
            self.show()

    def set_opacity(self, opacity: float):
        """Set window opacity (0.0 to 1.0)."""
        self.config.opacity = max(0.1, min(1.0, opacity))
        if self.window:
            self.window.attributes('-alpha', self.config.opacity)

    def set_always_on_top(self, on_top: bool):
        """Set always on top property."""
        self.config.always_on_top = on_top
        if self.window:
            self.window.attributes('-topmost', on_top)

    def update_position(self, x: int, y: int):
        """Update window position."""
        self.config.x = x
        self.config.y = y
        if self.window:
            self.window.geometry(f"+{x}+{y}")

    def update_size(self, width: int, height: int):
        """Update window size."""
        self.config.width = width
        self.config.height = height
        if self.window:
            self.window.geometry(f"{width}x{height}+{self.config.x}+{self.config.y}")

    def get_position(self) -> tuple:
        """Get current window position."""
        if self.window:
            return (self.window.winfo_x(), self.window.winfo_y())
        return (self.config.x, self.config.y)

    def destroy(self):
        """Destroy the overlay window."""
        if self.window:
            self.window.destroy()
            self.window = None
            self.is_visible = False


class CompactOverlay:
    """Ultra-compact overlay showing just the essentials."""

    def __init__(self, x: int = 100, y: int = 100, opacity: float = 0.9):
        self.window = tk.Toplevel()
        self.window.title("BJ Bot")
        self.window.geometry(f"200x120+{x}+{y}")
        self.window.attributes('-alpha', opacity)
        self.window.attributes('-topmost', True)
        self.window.configure(bg='#1e1e1e')

        # Make it draggable
        self.window.bind('<Button-1>', self._start_drag)
        self.window.bind('<B1-Motion>', self._on_drag)

        self.drag_start_x = 0
        self.drag_start_y = 0

        self._create_compact_ui()
        self.window.withdraw()

    def _create_compact_ui(self):
        """Create ultra-compact UI."""
        frame = tk.Frame(self.window, bg='#1e1e1e')
        frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Action (large)
        self.action_label = tk.Label(frame, text="STAND",
                                     font=('Arial', 16, 'bold'),
                                     bg='#4CAF50', fg='#ffffff', pady=5)
        self.action_label.pack(fill='x', pady=(0, 5))

        # Count and bet
        info_frame = tk.Frame(frame, bg='#2d2d2d')
        info_frame.pack(fill='x')

        tk.Label(info_frame, text="TC:", font=('Arial', 10),
                bg='#2d2d2d', fg='#aaaaaa').grid(row=0, column=0, sticky='w', padx=2)
        self.tc_label = tk.Label(info_frame, text="0.0",
                                font=('Arial', 10, 'bold'),
                                bg='#2d2d2d', fg='#4CAF50')
        self.tc_label.grid(row=0, column=1, sticky='w')

        tk.Label(info_frame, text="Bet:", font=('Arial', 10),
                bg='#2d2d2d', fg='#aaaaaa').grid(row=1, column=0, sticky='w', padx=2)
        self.bet_label = tk.Label(info_frame, text="$10",
                                 font=('Arial', 10, 'bold'),
                                 bg='#2d2d2d', fg='#FFC107')
        self.bet_label.grid(row=1, column=1, sticky='w')

    def _start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        x = self.window.winfo_x() + event.x - self.drag_start_x
        y = self.window.winfo_y() + event.y - self.drag_start_y
        self.window.geometry(f"+{x}+{y}")

    def update(self, action: Action, true_count: float, bet: float):
        """Quick update with minimal info."""
        color_map = {
            Action.HIT: '#FFA500',
            Action.STAND: '#4CAF50',
            Action.DOUBLE: '#2196F3',
            Action.SPLIT: '#9C27B0',
            Action.SURRENDER: '#F44336'
        }

        self.action_label.config(text=action.value if action else "WAIT",
                                bg=color_map.get(action, '#666666'))
        self.tc_label.config(text=f"{true_count:.1f}")
        self.bet_label.config(text=f"${bet:.0f}")

    def show(self):
        self.window.deiconify()
        self.window.lift()

    def hide(self):
        self.window.withdraw()

    def toggle(self):
        if self.window.winfo_viewable():
            self.hide()
        else:
            self.show()

    def destroy(self):
        self.window.destroy()
