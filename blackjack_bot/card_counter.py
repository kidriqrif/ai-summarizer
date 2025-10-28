"""Card counting system implementation."""
from typing import List, Dict
from enum import Enum


class CountingSystem(Enum):
    """Available card counting systems."""
    HI_LO = "hi_lo"
    KO = "ko"
    OMEGA_II = "omega_ii"
    HALVES = "halves"


class CardCounter:
    """Implements various card counting systems."""

    # Card values for different counting systems
    SYSTEMS = {
        CountingSystem.HI_LO: {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        },
        CountingSystem.KO: {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1,
            '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        },
        CountingSystem.OMEGA_II: {
            '2': 1, '3': 1, '4': 2, '5': 2, '6': 2, '7': 1,
            '8': 0, '9': -1,
            '10': -2, 'J': -2, 'Q': -2, 'K': -2, 'A': 0
        },
        CountingSystem.HALVES: {
            '2': 0.5, '3': 1, '4': 1, '5': 1.5, '6': 1,
            '7': 0.5, '8': 0, '9': -0.5,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
    }

    def __init__(self, system: CountingSystem = CountingSystem.HI_LO,
                 num_decks: int = 6):
        self.system = system
        self.num_decks = num_decks
        self.running_count = 0
        self.cards_seen = 0
        self.total_cards = num_decks * 52
        self.card_values = self.SYSTEMS[system]

    def reset(self):
        """Reset the count (new shoe)."""
        self.running_count = 0
        self.cards_seen = 0

    def count_card(self, card: str):
        """
        Add a card to the count.

        Args:
            card: Card value ('2'-'10', 'J', 'Q', 'K', 'A')
        """
        if card in self.card_values:
            self.running_count += self.card_values[card]
            self.cards_seen += 1

    def count_cards(self, cards: List[str]):
        """
        Add multiple cards to the count.

        Args:
            cards: List of card values
        """
        for card in cards:
            self.count_card(card)

    @property
    def decks_remaining(self) -> float:
        """Calculate approximate number of decks remaining."""
        cards_remaining = self.total_cards - self.cards_seen
        return max(1, cards_remaining / 52)  # Minimum 1 to avoid division by zero

    @property
    def true_count(self) -> float:
        """
        Calculate true count (running count / decks remaining).

        The true count normalizes the running count for the number of
        decks remaining, giving a more accurate representation of the
        deck composition.
        """
        return self.running_count / self.decks_remaining

    @property
    def player_advantage(self) -> float:
        """
        Estimate player advantage based on true count.

        Each +1 in true count gives approximately 0.5% advantage.
        House edge is typically around 0.5% with basic strategy.
        """
        house_edge = 0.005  # 0.5% house edge with basic strategy
        advantage_per_count = 0.005  # 0.5% per true count point

        return (self.true_count * advantage_per_count) - house_edge

    def get_betting_advice(self, min_bet: float, max_bet: float,
                          bankroll: float, kelly_fraction: float = 0.5) -> Dict:
        """
        Calculate optimal bet size based on count and bankroll.

        Uses Kelly Criterion for bet sizing:
        Bet = Bankroll * (Player_Advantage / Variance)

        Args:
            min_bet: Minimum table bet
            max_bet: Maximum table bet
            bankroll: Current bankroll
            kelly_fraction: Fraction of Kelly to use (0.5 = half Kelly)

        Returns:
            Dictionary with bet recommendation and reasoning
        """
        tc = self.true_count
        advantage = self.player_advantage

        # If no advantage, bet minimum
        if advantage <= 0:
            return {
                'bet': min_bet,
                'units': 1,
                'reason': 'Negative count - bet minimum',
                'true_count': tc,
                'advantage': advantage * 100,
                'action': 'bet_min'
            }

        # Kelly bet calculation
        # Variance for blackjack is approximately 1.3
        variance = 1.3
        kelly_bet = bankroll * (advantage / variance) * kelly_fraction

        # Round to nearest min_bet unit
        units = max(1, round(kelly_bet / min_bet))
        recommended_bet = min(units * min_bet, max_bet)

        # Determine action
        if tc < 1:
            action = 'bet_min'
            recommended_bet = min_bet
            units = 1
            reason = 'Count not high enough - bet minimum'
        elif tc >= 1 and tc < 2:
            action = 'bet_small'
            units = min(2, units)
            recommended_bet = units * min_bet
            reason = f'Slight advantage (TC: {tc:.1f}) - small bet increase'
        elif tc >= 2 and tc < 3:
            action = 'bet_medium'
            units = min(4, units)
            recommended_bet = units * min_bet
            reason = f'Good advantage (TC: {tc:.1f}) - medium bet increase'
        elif tc >= 3:
            action = 'bet_large'
            recommended_bet = min(recommended_bet, max_bet)
            units = round(recommended_bet / min_bet)
            reason = f'Strong advantage (TC: {tc:.1f}) - large bet increase'
        else:
            action = 'bet_min'
            recommended_bet = min_bet
            units = 1
            reason = 'Bet minimum'

        return {
            'bet': recommended_bet,
            'units': units,
            'reason': reason,
            'true_count': tc,
            'advantage': advantage * 100,  # As percentage
            'action': action
        }

    def get_deviation_plays(self, player_value: int, dealer_card: str) -> Dict:
        """
        Get index play deviations from basic strategy based on count.

        These are the "Illustrious 18" and "Fab 4" deviations.

        Returns:
            Dictionary with deviation advice
        """
        tc = self.true_count
        deviations = []

        # Illustrious 18 (simplified version)
        if player_value == 16 and dealer_card == '10':
            if tc >= 0:
                deviations.append("STAND on 16 vs 10 (TC >= 0)")

        if player_value == 15 and dealer_card == '10':
            if tc >= 4:
                deviations.append("STAND on 15 vs 10 (TC >= 4)")

        if player_value == 20 and dealer_card in ['5', '6']:
            if tc >= 5:
                deviations.append("Consider SPLITTING 10,10 vs 5 or 6 (TC >= 5)")

        if player_value == 10 and dealer_card in ['10', 'A']:
            if tc >= 4:
                deviations.append("DOUBLE 10 vs 10 or A (TC >= 4)")

        if player_value == 12 and dealer_card in ['2', '3']:
            if tc >= 3:
                deviations.append("STAND on 12 vs 2 or 3 (TC >= 3)")

        if player_value == 9 and dealer_card == '2':
            if tc >= 1:
                deviations.append("DOUBLE 9 vs 2 (TC >= 1)")

        if player_value == 16 and dealer_card == '9':
            if tc >= 5:
                deviations.append("STAND on 16 vs 9 (TC >= 5)")

        # Insurance deviation
        if dealer_card == 'A' and tc >= 3:
            deviations.append("TAKE INSURANCE (TC >= 3)")

        return {
            'has_deviations': len(deviations) > 0,
            'deviations': deviations,
            'true_count': tc
        }

    def get_stats(self) -> Dict:
        """Get current counting statistics."""
        return {
            'running_count': self.running_count,
            'true_count': self.true_count,
            'cards_seen': self.cards_seen,
            'decks_remaining': self.decks_remaining,
            'player_advantage': self.player_advantage * 100,
            'penetration': (self.cards_seen / self.total_cards) * 100,
            'system': self.system.value
        }

    def should_wong_out(self, threshold: float = -1.0) -> bool:
        """
        Determine if player should leave the table (Wong out).

        Args:
            threshold: True count threshold for leaving (default -1)

        Returns:
            True if player should leave
        """
        return self.true_count <= threshold
