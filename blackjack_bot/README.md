# Blackjack Bot - Optimal Play Assistant

A comprehensive blackjack assistant that provides real-time optimal play recommendations, card counting, and bet sizing advice by reading the game state from your screen.

## Features

### Core Features
- **Screen Reading**: Captures and reads game state using OCR technology
- **Basic Strategy Engine**: Provides optimal play decisions based on mathematical probability
- **Card Counting**: Implements multiple counting systems (Hi-Lo, KO, Omega II, Halves)
- **Bet Sizing**: Suggests optimal bet amounts using Kelly Criterion
- **Real-time Monitoring**: Continuously monitors game and updates recommendations
- **Configuration System**: Customizable game rules, betting parameters, and counting settings
- **Calibration Tools**: Easy setup for different online blackjack platforms

### Strategy Features
- Complete basic strategy for all hand combinations
- Soft hand (Ace) optimization
- Pair splitting recommendations
- Double down situations
- Surrender decisions (when allowed)
- Insurance recommendations based on count

### Card Counting Features
- **Hi-Lo System**: Industry standard, easy to learn
- **KO System**: Unbalanced system, no true count conversion needed
- **Omega II**: Advanced multi-level system
- **Halves**: Precision system with half-value cards
- Running count and true count calculations
- Player advantage estimation
- Wong out recommendations (leave table at negative counts)
- Index play deviations (Illustrious 18)

### Betting Features
- Kelly Criterion-based bet sizing
- Configurable risk tolerance (full Kelly, half Kelly, etc.)
- Bankroll management
- Spread recommendations based on count
- Minimum/maximum bet enforcement

## Installation

### Prerequisites
1. **Python 3.8+** required
2. **Tesseract OCR** must be installed separately:
   - **Windows**: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

### Setup
```bash
# Clone the repository
cd blackjack_bot

# Install Python dependencies
pip install -r requirements.txt

# Run the application
python gui.py
```

## Usage

### Initial Setup

1. **Launch the Application**
   ```bash
   python gui.py
   ```

2. **Configure Game Rules** (Configuration Tab)
   - Set number of decks
   - Dealer hits/stands on soft 17
   - Double after split allowed
   - Surrender option availability

3. **Configure Betting Parameters** (Configuration Tab)
   - Set minimum and maximum bet amounts
   - Enter your starting bankroll
   - Choose Kelly fraction (0.5 recommended for half-Kelly)
   - Enable/disable card counting

4. **Calibrate Screen Regions** (Calibration Tab)
   - Open your online blackjack game
   - Position windows so both are visible
   - Use "Save Screenshot" to capture current screen
   - Adjust X, Y, Width, Height for each region:
     - Dealer Cards
     - Player Cards
     - Balance Display
     - Bet Amount
   - Use "Test Read" buttons to verify detection
   - Click "Save Regions" when satisfied

### Playing with the Bot

1. **Start Monitoring**
   - Go to Main tab
   - Click "Start Monitoring"
   - The bot will continuously read the game state

2. **Follow Recommendations**
   - **Action**: Shows optimal play (HIT, STAND, DOUBLE, SPLIT, SURRENDER)
   - **Reasoning**: Explains why this action is optimal
   - **Recommended Bet**: Shows optimal bet size based on count
   - **Card Count**: Displays running count, true count, and player advantage

3. **Manual Reading**
   - Use "Manual Read" button for one-time screen capture
   - Useful when auto-monitoring isn't working properly

4. **Reset Count**
   - Click "Reset Count" when dealer shuffles
   - Important to maintain accurate count

## Configuration File

Settings are automatically saved to `blackjack_config.json`:

```json
{
  "game_rules": {
    "num_decks": 6,
    "dealer_hits_soft_17": true,
    "double_after_split": true,
    "surrender_allowed": false,
    "blackjack_payout": 1.5
  },
  "betting": {
    "min_bet": 10.0,
    "max_bet": 500.0,
    "bankroll": 1000.0,
    "kelly_fraction": 0.5
  },
  "counting": {
    "system": "hi_lo",
    "enabled": true,
    "true_count_threshold": 2.0
  },
  "screen": {
    "dealer_region": {"x": 0, "y": 0, "width": 400, "height": 150},
    "player_region": {"x": 0, "y": 200, "width": 400, "height": 150},
    "balance_region": {"x": 0, "y": 400, "width": 200, "height": 50},
    "bet_region": {"x": 0, "y": 450, "width": 200, "height": 50}
  }
}
```

## Basic Strategy Overview

The bot implements optimal basic strategy based on:
- Player hand value (hard/soft)
- Dealer upcard
- Available options (double, split, surrender)
- Game rules configuration

### Example Scenarios

**Hard 16 vs Dealer 10**
- Basic Strategy: HIT (without counting)
- With Count: STAND if true count ≥ 0

**Soft 18 vs Dealer 9**
- Basic Strategy: HIT
- Reason: Soft hand can't bust, 19+ is better

**Pair of 8s**
- Basic Strategy: ALWAYS SPLIT
- Even against dealer 10 or Ace

**Player 11 vs Dealer 6**
- Basic Strategy: DOUBLE
- Maximize profit in favorable situation

## Card Counting Guide

### Hi-Lo System (Recommended for Beginners)
- **Low cards (2-6)**: +1
- **Neutral (7-9)**: 0
- **High cards (10-A)**: -1

**True Count** = Running Count ÷ Decks Remaining

**Betting Strategy**:
- True Count ≤ 1: Bet minimum
- True Count 2-3: Bet 2-4 units
- True Count 4+: Bet 5-8 units (or table maximum)

### Player Advantage
- Each +1 true count = ~0.5% player advantage
- Basic strategy alone: ~0.5% house edge
- True count +2 = ~0.5% player advantage
- True count +4 = ~1.5% player advantage

## Bet Sizing with Kelly Criterion

The Kelly Criterion calculates optimal bet size:

**Kelly Bet** = Bankroll × (Player Advantage / Variance)

**Half-Kelly** (recommended): Use 0.5 Kelly fraction for reduced volatility

**Example**:
- Bankroll: $1,000
- True Count: +3
- Player Advantage: ~1.0%
- Variance: 1.3
- Kelly Bet: $1,000 × (0.01 / 1.3) × 0.5 = $3.85
- Round to bet units: $5-10

## Tips for Success

### Accuracy
- Calibrate screen regions carefully
- Test OCR accuracy before playing
- Verify card detection in calibration tab
- Adjust regions if cards change position

### Bankroll Management
- Start with conservative Kelly fraction (0.25-0.5)
- Never bet more than 5% of bankroll on single hand
- Maintain adequate bankroll (40+ max bets recommended)
- Set stop-loss limits

### Counting Tips
- Reset count when shoe is shuffled
- Watch deck penetration (deeper = better)
- Leave table at negative counts (Wong out)
- Practice counting away from the bot first

### Legal Considerations
- Using strategy tools is generally legal
- Check online casino terms of service
- Some casinos prohibit any external assistance
- Physical casinos may ban known counters
- Use responsibly and ethically

## Troubleshooting

### OCR Not Reading Cards
- Increase region size to capture full cards
- Ensure good contrast between cards and background
- Check Tesseract installation
- Try different screen resolutions
- Clean screenshots help debug

### Incorrect Recommendations
- Verify game rules configuration
- Ensure dealer/player regions are correct
- Check that counting is enabled
- Reset count if mid-shoe

### Performance Issues
- Increase monitoring interval (reduce CPU usage)
- Close unnecessary applications
- Use manual read mode instead of continuous monitoring

## Advanced Features

### Index Plays (Illustrious 18)
The bot includes common strategy deviations:
- 16 vs 10: Stand at TC ≥ 0
- 15 vs 10: Stand at TC ≥ 4
- 10 vs 10: Double at TC ≥ 4
- 10 vs A: Double at TC ≥ 4
- And more...

### Risk of Ruin
Monitor your bankroll relative to bet sizes:
- 40+ max bets: Low risk
- 20-40 max bets: Medium risk
- <20 max bets: High risk

## Architecture

```
blackjack_bot/
├── config_manager.py    # Configuration handling
├── strategy_engine.py   # Basic strategy logic
├── card_counter.py      # Card counting systems
├── screen_reader.py     # OCR and screen capture
├── gui.py              # Main GUI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Disclaimer

This tool is for **educational purposes only**.

- **Not a guarantee of winning**: Blackjack always has variance
- **Check local laws**: Online gambling may be restricted
- **Casino policies**: Using bots may violate terms of service
- **Responsible gambling**: Never bet more than you can afford to lose
- **House edge**: Even with perfect play, casino may have edge on unfavorable rules

Card counting provides mathematical advantage but requires:
- Large bankroll
- Favorable game rules
- Good deck penetration
- Perfect play execution
- Emotional discipline

**Use this tool responsibly and at your own risk.**

## Contributing

Contributions welcome! Areas for improvement:
- Additional counting systems
- Better OCR accuracy
- Machine learning for card detection
- Multi-hand support
- Tournament strategy mode
- Enhanced UI/UX
- Mobile version

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests:
1. Check troubleshooting section
2. Review configuration settings
3. Test with calibration tools
4. Open an issue on GitHub

## Version History

**v1.0.0** - Initial Release
- Basic strategy engine
- Hi-Lo card counting
- Screen reading with OCR
- Bet sizing with Kelly Criterion
- Configuration and calibration tools
- Real-time monitoring GUI

---

**Happy Gaming! Remember: The house always has an edge on bad rules. Play smart, play responsibly.**
