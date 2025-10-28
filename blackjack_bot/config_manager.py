"""Configuration manager for blackjack bot settings."""
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class GameRules:
    """Blackjack game rules configuration."""
    num_decks: int = 6
    dealer_hits_soft_17: bool = True
    double_after_split: bool = True
    surrender_allowed: bool = False
    blackjack_payout: float = 1.5  # 3:2
    resplit_aces: bool = False
    max_splits: int = 3


@dataclass
class BettingConfig:
    """Betting strategy configuration."""
    min_bet: float = 10.0
    max_bet: float = 500.0
    bankroll: float = 1000.0
    risk_tolerance: str = "medium"  # low, medium, high
    kelly_fraction: float = 0.5  # Half-Kelly for safety
    spread_ratio: int = 10  # max_bet / min_bet


@dataclass
class ScreenConfig:
    """Screen capture region configuration."""
    dealer_region: Dict[str, int] = None
    player_region: Dict[str, int] = None
    balance_region: Dict[str, int] = None
    bet_region: Dict[str, int] = None

    def __post_init__(self):
        if self.dealer_region is None:
            self.dealer_region = {"x": 0, "y": 0, "width": 400, "height": 150}
        if self.player_region is None:
            self.player_region = {"x": 0, "y": 200, "width": 400, "height": 150}
        if self.balance_region is None:
            self.balance_region = {"x": 0, "y": 400, "width": 200, "height": 50}
        if self.bet_region is None:
            self.bet_region = {"x": 0, "y": 450, "width": 200, "height": 50}


@dataclass
class CardCountingConfig:
    """Card counting configuration."""
    system: str = "hi_lo"  # hi_lo, ko, omega_ii
    enabled: bool = True
    true_count_threshold: float = 2.0  # Start increasing bets at TC +2
    wong_out: bool = False  # Leave table at negative counts
    wong_out_threshold: float = -1.0


class ConfigManager:
    """Manages all configuration settings."""

    def __init__(self, config_file: str = "blackjack_config.json"):
        self.config_file = config_file
        self.game_rules = GameRules()
        self.betting = BettingConfig()
        self.screen = ScreenConfig()
        self.counting = CardCountingConfig()
        self.load()

    def load(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            self.save()  # Create default config
            return

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)

            if 'game_rules' in data:
                self.game_rules = GameRules(**data['game_rules'])
            if 'betting' in data:
                self.betting = BettingConfig(**data['betting'])
            if 'screen' in data:
                self.screen = ScreenConfig(**data['screen'])
            if 'counting' in data:
                self.counting = CardCountingConfig(**data['counting'])
        except Exception as e:
            print(f"Error loading config: {e}")
            self.save()  # Reset to defaults

    def save(self):
        """Save configuration to file."""
        data = {
            'game_rules': asdict(self.game_rules),
            'betting': asdict(self.betting),
            'screen': asdict(self.screen),
            'counting': asdict(self.counting)
        }

        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update_game_rules(self, **kwargs):
        """Update game rules."""
        for key, value in kwargs.items():
            if hasattr(self.game_rules, key):
                setattr(self.game_rules, key, value)
        self.save()

    def update_betting(self, **kwargs):
        """Update betting configuration."""
        for key, value in kwargs.items():
            if hasattr(self.betting, key):
                setattr(self.betting, key, value)
        self.save()

    def update_screen(self, **kwargs):
        """Update screen configuration."""
        for key, value in kwargs.items():
            if hasattr(self.screen, key):
                setattr(self.screen, key, value)
        self.save()

    def update_counting(self, **kwargs):
        """Update card counting configuration."""
        for key, value in kwargs.items():
            if hasattr(self.counting, key):
                setattr(self.counting, key, value)
        self.save()
