"""Basic strategy engine for optimal blackjack play."""
from typing import Tuple, List
from enum import Enum


class Action(Enum):
    """Possible blackjack actions."""
    HIT = "HIT"
    STAND = "STAND"
    DOUBLE = "DOUBLE"
    SPLIT = "SPLIT"
    SURRENDER = "SURRENDER"


class Hand:
    """Represents a blackjack hand."""

    def __init__(self, cards: List[str]):
        self.cards = cards

    @property
    def value(self) -> int:
        """Calculate hand value."""
        total = 0
        aces = 0

        for card in self.cards:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                aces += 1
                total += 11
            else:
                total += int(card)

        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    @property
    def is_soft(self) -> bool:
        """Check if hand is soft (contains usable ace)."""
        total = 0
        aces = 0

        for card in self.cards:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card == 'A':
                aces += 1
            else:
                total += int(card)

        # Check if we can count an ace as 11
        if aces > 0:
            if total + 11 + (aces - 1) <= 21:
                return True
        return False

    @property
    def is_pair(self) -> bool:
        """Check if hand is a pair."""
        if len(self.cards) != 2:
            return False

        # Normalize card values for comparison
        card1 = self.cards[0] if self.cards[0] not in ['J', 'Q', 'K'] else '10'
        card2 = self.cards[1] if self.cards[1] not in ['J', 'Q', 'K'] else '10'

        return card1 == card2

    @property
    def pair_card(self) -> str:
        """Get the card value for pairs."""
        if not self.is_pair:
            return None
        card = self.cards[0]
        return '10' if card in ['J', 'Q', 'K'] else card


class StrategyEngine:
    """Implements optimal basic strategy."""

    def __init__(self, dealer_hits_soft_17: bool = True,
                 double_after_split: bool = True,
                 surrender_allowed: bool = False):
        self.dealer_hits_soft_17 = dealer_hits_soft_17
        self.double_after_split = double_after_split
        self.surrender_allowed = surrender_allowed
        self._init_strategy_tables()

    def _init_strategy_tables(self):
        """Initialize basic strategy tables."""
        # Hard totals strategy (player_total, dealer_up_card) -> Action
        self.hard_strategy = {
            # Player 8 or less: always hit
            **{(i, j): Action.HIT for i in range(5, 9) for j in range(2, 12)},

            # Player 9
            9: {2: Action.HIT, 3: Action.DOUBLE, 4: Action.DOUBLE, 5: Action.DOUBLE,
                6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                10: Action.HIT, 11: Action.HIT},

            # Player 10
            10: {2: Action.DOUBLE, 3: Action.DOUBLE, 4: Action.DOUBLE, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.DOUBLE, 8: Action.DOUBLE, 9: Action.DOUBLE,
                 10: Action.HIT, 11: Action.HIT},

            # Player 11
            11: {2: Action.DOUBLE, 3: Action.DOUBLE, 4: Action.DOUBLE, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.DOUBLE, 8: Action.DOUBLE, 9: Action.DOUBLE,
                 10: Action.DOUBLE, 11: Action.DOUBLE},

            # Player 12
            12: {2: Action.HIT, 3: Action.HIT, 4: Action.STAND, 5: Action.STAND,
                 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},

            # Player 13-16
            **{i: {2: Action.STAND, 3: Action.STAND, 4: Action.STAND, 5: Action.STAND,
                   6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                   10: Action.HIT, 11: Action.HIT}
               for i in range(13, 17)},

            # Player 17+: always stand
            **{i: {j: Action.STAND for j in range(2, 12)} for i in range(17, 22)}
        }

        # Soft totals strategy
        self.soft_strategy = {
            # Soft 13-15 (A,2 to A,4)
            13: {2: Action.HIT, 3: Action.HIT, 4: Action.HIT, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},
            14: {2: Action.HIT, 3: Action.HIT, 4: Action.HIT, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},
            15: {2: Action.HIT, 3: Action.HIT, 4: Action.DOUBLE, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},

            # Soft 16-17 (A,5 to A,6)
            16: {2: Action.HIT, 3: Action.HIT, 4: Action.DOUBLE, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},
            17: {2: Action.HIT, 3: Action.DOUBLE, 4: Action.DOUBLE, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},

            # Soft 18 (A,7)
            18: {2: Action.STAND, 3: Action.DOUBLE, 4: Action.DOUBLE, 5: Action.DOUBLE,
                 6: Action.DOUBLE, 7: Action.STAND, 8: Action.STAND, 9: Action.HIT,
                 10: Action.HIT, 11: Action.HIT},

            # Soft 19+: always stand
            19: {j: Action.STAND for j in range(2, 12)},
            20: {j: Action.STAND for j in range(2, 12)},
            21: {j: Action.STAND for j in range(2, 12)},
        }

        # Pair splitting strategy
        self.pair_strategy = {
            '2': {2: Action.SPLIT, 3: Action.SPLIT, 4: Action.SPLIT, 5: Action.SPLIT,
                  6: Action.SPLIT, 7: Action.SPLIT, 8: Action.HIT, 9: Action.HIT,
                  10: Action.HIT, 11: Action.HIT},
            '3': {2: Action.SPLIT, 3: Action.SPLIT, 4: Action.SPLIT, 5: Action.SPLIT,
                  6: Action.SPLIT, 7: Action.SPLIT, 8: Action.HIT, 9: Action.HIT,
                  10: Action.HIT, 11: Action.HIT},
            '4': {2: Action.HIT, 3: Action.HIT, 4: Action.HIT, 5: Action.SPLIT,
                  6: Action.SPLIT, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                  10: Action.HIT, 11: Action.HIT},
            '5': {j: Action.HIT for j in range(2, 12)},  # Never split 5s, treat as 10
            '6': {2: Action.SPLIT, 3: Action.SPLIT, 4: Action.SPLIT, 5: Action.SPLIT,
                  6: Action.SPLIT, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT,
                  10: Action.HIT, 11: Action.HIT},
            '7': {2: Action.SPLIT, 3: Action.SPLIT, 4: Action.SPLIT, 5: Action.SPLIT,
                  6: Action.SPLIT, 7: Action.SPLIT, 8: Action.HIT, 9: Action.HIT,
                  10: Action.HIT, 11: Action.HIT},
            '8': {j: Action.SPLIT for j in range(2, 12)},  # Always split 8s
            '9': {2: Action.SPLIT, 3: Action.SPLIT, 4: Action.SPLIT, 5: Action.SPLIT,
                  6: Action.SPLIT, 7: Action.STAND, 8: Action.SPLIT, 9: Action.SPLIT,
                  10: Action.STAND, 11: Action.STAND},
            '10': {j: Action.STAND for j in range(2, 12)},  # Never split 10s
            'A': {j: Action.SPLIT for j in range(2, 12)},  # Always split Aces
        }

        # Surrender strategy (late surrender)
        self.surrender_strategy = {
            16: {9: True, 10: True, 11: True},  # Surrender 16 vs 9, 10, A
            15: {10: True},  # Surrender 15 vs 10
        }

    def get_action(self, player_hand: Hand, dealer_up_card: str,
                   can_double: bool = True, can_split: bool = True,
                   can_surrender: bool = True) -> Action:
        """
        Determine optimal action based on basic strategy.

        Args:
            player_hand: Player's current hand
            dealer_up_card: Dealer's face-up card
            can_double: Whether doubling is allowed
            can_split: Whether splitting is allowed
            can_surrender: Whether surrender is allowed

        Returns:
            Optimal action to take
        """
        # Convert dealer card to numeric value
        if dealer_up_card == 'A':
            dealer_value = 11
        elif dealer_up_card in ['J', 'Q', 'K']:
            dealer_value = 10
        else:
            dealer_value = int(dealer_up_card)

        # Check for surrender first (if allowed)
        if can_surrender and self.surrender_allowed:
            if player_hand.value in self.surrender_strategy:
                if dealer_value in self.surrender_strategy[player_hand.value]:
                    if self.surrender_strategy[player_hand.value][dealer_value]:
                        return Action.SURRENDER

        # Check for pair splitting
        if can_split and player_hand.is_pair:
            pair_card = player_hand.pair_card
            if pair_card in self.pair_strategy:
                action = self.pair_strategy[pair_card].get(dealer_value, Action.HIT)
                if action == Action.SPLIT:
                    return Action.SPLIT

        # Soft hand strategy
        if player_hand.is_soft:
            player_value = player_hand.value
            if player_value in self.soft_strategy:
                action = self.soft_strategy[player_value].get(dealer_value, Action.STAND)
                if action == Action.DOUBLE and not can_double:
                    return Action.HIT
                return action

        # Hard hand strategy
        player_value = player_hand.value
        if player_value in self.hard_strategy:
            action = self.hard_strategy[player_value].get(dealer_value, Action.STAND)
            if action == Action.DOUBLE and not can_double:
                return Action.HIT
            return action

        # Default: stand on 17+, hit otherwise
        return Action.STAND if player_value >= 17 else Action.HIT

    def get_insurance_decision(self, player_hand: Hand, dealer_up_card: str,
                              true_count: float = 0) -> bool:
        """
        Decide whether to take insurance.

        Insurance is generally a bad bet unless counting cards.
        Take insurance when true count >= +3.
        """
        if dealer_up_card != 'A':
            return False

        # Only take insurance with high true count
        return true_count >= 3.0
