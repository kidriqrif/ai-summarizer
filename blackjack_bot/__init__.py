"""Blackjack Bot - Optimal Play Assistant

A comprehensive blackjack assistant that:
- Reads game state from screen
- Provides optimal basic strategy recommendations
- Counts cards using various systems (Hi-Lo, KO, etc.)
- Suggests bet sizes based on count and bankroll
- Includes configuration and calibration tools
"""

__version__ = "1.0.0"
__author__ = "Blackjack Bot Team"

from .config_manager import ConfigManager
from .strategy_engine import StrategyEngine, Hand, Action
from .card_counter import CardCounter, CountingSystem
from .screen_reader import ScreenReader, GameState
from .gui import BlackjackBotGUI

__all__ = [
    'ConfigManager',
    'StrategyEngine',
    'Hand',
    'Action',
    'CardCounter',
    'CountingSystem',
    'ScreenReader',
    'GameState',
    'BlackjackBotGUI'
]
