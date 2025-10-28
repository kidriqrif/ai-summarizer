"""Example usage of blackjack bot components."""

from strategy_engine import StrategyEngine, Hand, Action
from card_counter import CardCounter, CountingSystem
from config_manager import ConfigManager


def example_basic_strategy():
    """Example: Using the basic strategy engine."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Strategy Engine")
    print("=" * 60)

    engine = StrategyEngine(dealer_hits_soft_17=True)

    # Example 1: Hard 16 vs 10
    player_hand = Hand(['10', '6'])
    dealer_card = '10'
    action = engine.get_action(player_hand, dealer_card)
    print(f"\nPlayer: 16 (hard) vs Dealer: {dealer_card}")
    print(f"Recommended action: {action.value}")

    # Example 2: Soft 18 vs 9
    player_hand = Hand(['A', '7'])
    dealer_card = '9'
    action = engine.get_action(player_hand, dealer_card)
    print(f"\nPlayer: Soft 18 (A,7) vs Dealer: {dealer_card}")
    print(f"Recommended action: {action.value}")

    # Example 3: Pair of 8s vs 10
    player_hand = Hand(['8', '8'])
    dealer_card = '10'
    action = engine.get_action(player_hand, dealer_card, can_split=True)
    print(f"\nPlayer: Pair of 8s vs Dealer: {dealer_card}")
    print(f"Recommended action: {action.value}")

    # Example 4: 11 vs 6 (double down situation)
    player_hand = Hand(['6', '5'])
    dealer_card = '6'
    action = engine.get_action(player_hand, dealer_card, can_double=True)
    print(f"\nPlayer: 11 vs Dealer: {dealer_card}")
    print(f"Recommended action: {action.value}")


def example_card_counting():
    """Example: Using the card counting system."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Card Counting System (Hi-Lo)")
    print("=" * 60)

    counter = CardCounter(system=CountingSystem.HI_LO, num_decks=6)

    # Simulate some cards being dealt
    print("\nSimulating cards dealt from shoe...")
    cards_dealt = ['K', '5', '10', '6', '2', 'A', '7', '9', '4', '3',
                  'Q', '8', '5', '10', 'J', '6', '2', '3', 'K', 'A']

    print(f"Cards: {', '.join(cards_dealt)}")

    for card in cards_dealt:
        counter.count_card(card)

    # Display count statistics
    stats = counter.get_stats()
    print(f"\nRunning Count: {stats['running_count']}")
    print(f"True Count: {stats['true_count']:.2f}")
    print(f"Decks Remaining: {stats['decks_remaining']:.1f}")
    print(f"Player Advantage: {stats['player_advantage']:.2f}%")
    print(f"Deck Penetration: {stats['penetration']:.1f}%")

    # Get betting advice
    bet_advice = counter.get_betting_advice(
        min_bet=10.0,
        max_bet=500.0,
        bankroll=1000.0,
        kelly_fraction=0.5
    )

    print(f"\nBetting Recommendation:")
    print(f"  Bet Amount: ${bet_advice['bet']:.2f}")
    print(f"  Units: {bet_advice['units']}")
    print(f"  Reason: {bet_advice['reason']}")


def example_strategy_with_count():
    """Example: Combining strategy with card counting for index plays."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Strategy with Card Counting (Index Plays)")
    print("=" * 60)

    engine = StrategyEngine()
    counter = CardCounter(system=CountingSystem.HI_LO, num_decks=6)

    # Simulate positive count
    high_cards = ['2', '3', '4', '5', '6'] * 8  # Many low cards gone
    for card in high_cards:
        counter.count_card(card)

    stats = counter.get_stats()
    print(f"\nTrue Count: {stats['true_count']:.2f}")
    print(f"Player Advantage: {stats['player_advantage']:.2f}%")

    # Example: 16 vs 10 (basic strategy says hit, but with high count might stand)
    player_hand = Hand(['10', '6'])
    dealer_card = '10'
    basic_action = engine.get_action(player_hand, dealer_card)

    print(f"\nScenario: Player 16 vs Dealer 10")
    print(f"Basic Strategy: {basic_action.value}")
    print(f"With TC {stats['true_count']:.1f}: Consider STANDING (index play)")

    # Check for deviations
    deviations = counter.get_deviation_plays(16, '10')
    if deviations['has_deviations']:
        print(f"\nIndex Play Deviations:")
        for dev in deviations['deviations']:
            print(f"  - {dev}")

    # Insurance example
    dealer_card = 'A'
    should_insure = engine.get_insurance_decision(player_hand, dealer_card, stats['true_count'])
    print(f"\nInsurance Decision (Dealer showing Ace):")
    print(f"  True Count: {stats['true_count']:.2f}")
    print(f"  Take Insurance: {should_insure}")


def example_bankroll_management():
    """Example: Bankroll and bet sizing management."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Bankroll Management")
    print("=" * 60)

    counter = CardCounter(system=CountingSystem.HI_LO, num_decks=6)

    bankroll = 1000.0
    min_bet = 10.0
    max_bet = 100.0

    print(f"\nStarting Bankroll: ${bankroll}")
    print(f"Min Bet: ${min_bet}")
    print(f"Max Bet: ${max_bet}")
    print(f"Kelly Fraction: 0.5 (Half-Kelly)")

    # Simulate different count scenarios
    scenarios = [
        ("Negative Count", -2),
        ("Neutral Count", 0),
        ("Slight Positive", 1.5),
        ("Good Count", 3),
        ("Hot Deck", 5)
    ]

    print("\nBet Sizing at Different Counts:")
    print("-" * 60)

    for scenario_name, true_count in scenarios:
        # Simulate cards to get desired true count
        counter.reset()
        cards_needed = int(true_count * counter.decks_remaining)
        if cards_needed > 0:
            for _ in range(abs(cards_needed)):
                counter.count_card('2')  # Low card = +1
        else:
            for _ in range(abs(cards_needed)):
                counter.count_card('K')  # High card = -1

        # Get betting advice
        bet_advice = counter.get_betting_advice(min_bet, max_bet, bankroll, kelly_fraction=0.5)

        print(f"\n{scenario_name} (TC: {bet_advice['true_count']:.1f}):")
        print(f"  Recommended Bet: ${bet_advice['bet']:.2f} ({bet_advice['units']} units)")
        print(f"  Player Advantage: {bet_advice['advantage']:.2f}%")
        print(f"  Strategy: {bet_advice['reason']}")


def example_configuration():
    """Example: Using the configuration manager."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Configuration Management")
    print("=" * 60)

    config = ConfigManager("example_config.json")

    print("\nDefault Configuration:")
    print(f"  Game: {config.game_rules.num_decks} decks")
    print(f"  Dealer H17: {config.game_rules.dealer_hits_soft_17}")
    print(f"  Min Bet: ${config.betting.min_bet}")
    print(f"  Max Bet: ${config.betting.max_bet}")
    print(f"  Counting System: {config.counting.system}")

    # Update configuration
    print("\nUpdating configuration...")
    config.update_game_rules(num_decks=8, dealer_hits_soft_17=False)
    config.update_betting(min_bet=25.0, max_bet=1000.0)

    print("\nUpdated Configuration:")
    print(f"  Game: {config.game_rules.num_decks} decks")
    print(f"  Dealer H17: {config.game_rules.dealer_hits_soft_17}")
    print(f"  Min Bet: ${config.betting.min_bet}")
    print(f"  Max Bet: ${config.betting.max_bet}")

    print(f"\nConfiguration saved to: {config.config_file}")


def run_all_examples():
    """Run all example functions."""
    print("\n" + "=" * 60)
    print("BLACKJACK BOT - USAGE EXAMPLES")
    print("=" * 60)

    example_basic_strategy()
    example_card_counting()
    example_strategy_with_count()
    example_bankroll_management()
    example_configuration()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nTo use the full GUI application, run:")
    print("  python main.py")
    print("\nor:")
    print("  python gui.py")
    print()


if __name__ == "__main__":
    run_all_examples()
