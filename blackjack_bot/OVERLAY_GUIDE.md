# Overlay Window Guide

## Overview

The **Overlay Window** is a transparent, floating window that displays real-time blackjack recommendations on top of your game. It provides at-a-glance information without blocking your view of the game.

## Features

### Two Display Modes

#### 1. **Full Overlay** (Default)
- **Size**: 300x250 pixels
- **Displays**:
  - Recommended action (HIT, STAND, DOUBLE, SPLIT, SURRENDER)
  - Current dealer and player cards
  - Running count and true count
  - Player advantage percentage
  - Recommended bet amount and units
  - Color-coded action recommendations

#### 2. **Compact Overlay**
- **Size**: 200x120 pixels (minimal footprint)
- **Displays**:
  - Recommended action only (large)
  - True count
  - Recommended bet
  - Perfect for limited screen space

## Getting Started

### Enable the Overlay

**Method 1: From Configuration Tab**
1. Open the main GUI
2. Go to **Configuration** tab
3. Find the **Overlay Window** section
4. Check **"Enable Overlay Window"**
5. Click **"Save Configuration"**
6. Restart the application

**Method 2: From Main Tab**
1. Click the **"Show Overlay"** button in the Controls section
2. The overlay will appear on screen

### Position the Overlay

**Drag and Drop**:
- Click and hold anywhere on the overlay window
- Drag it to your desired position
- Release to place it
- Position is automatically saved

**Best Practices**:
- Place it near the edge of your screen
- Keep it visible but not blocking key game elements
- Position near betting controls for quick reference

## Configuration Options

### Access Configuration
Navigate to **Configuration Tab → Overlay Window**

### Available Settings

| Setting | Description | Default | Range/Options |
|---------|-------------|---------|---------------|
| **Enable Overlay Window** | Turn overlay on/off | Off | Checkbox |
| **Compact Mode** | Use minimal display | Off | Checkbox |
| **Opacity** | Window transparency | 0.85 | 0.1 to 1.0 |
| **Always on top** | Keep overlay above all windows | On | Checkbox |
| **Show card count** | Display count statistics | On | Checkbox |
| **Show betting recommendation** | Display bet amounts | On | Checkbox |

### Opacity Guide
- **0.9-1.0**: Nearly opaque, maximum visibility
- **0.7-0.9**: Semi-transparent, good balance
- **0.5-0.7**: More transparent, minimal obstruction
- **0.1-0.5**: Very transparent, can see through clearly

### Recommended Settings

**For Dual Monitor Setup**:
```
Opacity: 0.9
Always on top: Yes
Compact Mode: No
Position: On secondary monitor
```

**For Single Monitor**:
```
Opacity: 0.7
Always on top: Yes
Compact Mode: Yes
Position: Corner of screen
```

**For Practice/Learning**:
```
Opacity: 1.0
Always on top: Yes
Compact Mode: No
Show all information
```

## Using the Overlay

### During Gameplay

1. **Start Monitoring**
   - Click "Start Monitoring" in main GUI
   - Overlay updates every 2 seconds

2. **Read the Action**
   - Large colored box shows recommended action
   - Colors indicate action type:
     - **Green** = STAND
     - **Orange** = HIT
     - **Blue** = DOUBLE
     - **Purple** = SPLIT
     - **Red** = SURRENDER

3. **Check the Count** (if enabled)
   - **RC**: Running Count
   - **TC**: True Count
   - **Edge**: Your advantage percentage
   - Color changes with count:
     - **Green**: Positive count (TC ≥ +2)
     - **Yellow**: Neutral count (-1 < TC < +2)
     - **Red**: Negative count (TC ≤ -1)

4. **Adjust Your Bet**
   - Recommended bet shown in dollars
   - Units shown in parentheses
   - Updates based on true count

### Keyboard Shortcuts

Currently, the overlay has no keyboard shortcuts, but you can:
- Use the main GUI's "Show Overlay" / "Hide Overlay" button
- Close overlay by clicking the **×** in the top-right corner

## Overlay Display Examples

### Full Overlay Display

```
┌─────────────────────────────┐
│ 🎰 Blackjack Assistant   × │
├─────────────────────────────┤
│        ┌─────────────┐       │
│        │    STAND    │       │
│        └─────────────┘       │
├─────────────────────────────┤
│  Dealer: K, 6               │
│  Player: 10, 6              │
├─────────────────────────────┤
│  RC: +8    TC: +4.0         │
│  Edge: +1.5%                │
├─────────────────────────────┤
│  Recommended Bet:           │
│  $50 (5 units)              │
└─────────────────────────────┘
```

### Compact Overlay Display

```
┌─────────────────┐
│    DOUBLE       │
├─────────────────┤
│ TC: +3.0        │
│ Bet: $40        │
└─────────────────┘
```

## Troubleshooting

### Overlay Not Showing

**Check Configuration**:
1. Go to Configuration tab
2. Verify "Enable Overlay Window" is checked
3. Click "Save Configuration"
4. Click "Show Overlay" button

**Overlay Hidden Behind Game**:
1. Enable "Always on top" in configuration
2. Save and restart overlay

**Overlay Off Screen**:
1. Close and restart the application
2. Overlay will reset to default position (100, 100)
3. Drag to desired location

### Overlay Not Updating

**Ensure Monitoring is Active**:
- Click "Start Monitoring" in main tab
- Check that screen regions are calibrated

**Check Calibration**:
- Go to Calibration tab
- Verify all regions are properly configured
- Test with "Manual Read"

### Performance Issues

**Reduce Update Frequency**:
- Overlay updates every 2 seconds
- This is tied to the main monitoring loop
- Cannot be changed independently

**Lower Opacity**:
- Lower opacity = less GPU usage
- Try 0.6-0.7 for better performance

**Use Compact Mode**:
- Smaller window = less rendering
- Fewer UI elements to update

## Best Practices

### Screen Layout

**Recommended Arrangements**:

1. **Side-by-side** (Dual Monitor)
   ```
   [Blackjack Game]  [Main GUI + Overlay]
   ```

2. **Overlay Corner** (Single Monitor)
   ```
   ┌────────────────────────┐
   │ [Game Window]          │
   │                 [Overlay]│
   │                        │
   └────────────────────────┘
   ```

3. **Compact Overlay Edge**
   ```
   ┌────────────────────────┐
   │[O] [Game Window]       │
   │v                       │
   │e                       │
   │r                       │
   │l                       │
   │a                       │
   │y                       │
   └────────────────────────┘
   ```

### Usage Tips

**For Beginners**:
- Start with full overlay
- Keep opacity high (0.9-1.0)
- Show all information
- Use as learning tool

**For Experienced Players**:
- Switch to compact mode
- Lower opacity (0.6-0.7)
- Focus on action and count only
- Minimize distraction

**For Card Counting Practice**:
- Enable full overlay
- Show count information
- Verify your mental count matches
- Practice bet sizing

## Advanced Features

### Draggable Window

The overlay is fully draggable:
- Click and hold **anywhere** on the overlay
- Drag to new position
- Position is saved automatically

### Always on Top

When enabled:
- Overlay stays above **all** windows
- Even when blackjack game is focused
- Essential for single-monitor use

### Automatic Updates

The overlay updates automatically when:
- New cards are dealt
- Game state changes
- Count changes
- Shuffle detected
- Monitoring is active

## Privacy and Security

### What the Overlay Shows

The overlay only displays:
- Strategy recommendations
- Card count information
- Betting suggestions
- Game state (cards visible on screen)

### What the Overlay Does NOT Show

- Your actual bets
- Historical results
- Personal information
- Account balance (only what's read from screen)

### Recording Software Compatibility

**OBS/Streaming**:
- Overlay can be captured
- Set opacity to 1.0 for cleaner capture
- Position carefully to avoid blocking content

**Screen Recording**:
- Works with most recording software
- May appear transparent in recordings
- Use window capture, not display capture

## Configuration File

Overlay settings are stored in `blackjack_config.json`:

```json
{
  "overlay": {
    "enabled": false,
    "x": 100,
    "y": 100,
    "width": 300,
    "height": 250,
    "opacity": 0.85,
    "always_on_top": true,
    "show_count": true,
    "show_betting": true,
    "show_stats": true,
    "font_size": 11,
    "compact_mode": false
  }
}
```

**Manual Editing**:
- Close the application first
- Edit the JSON file
- Save and restart
- Changes will take effect

## FAQ

**Q: Can I resize the overlay window?**
A: Window size is fixed based on mode (full vs compact). This ensures consistent display and readability.

**Q: Does the overlay work with all games?**
A: Yes, if the game is visible on screen and properly calibrated.

**Q: Can I use overlay without the main GUI?**
A: No, the overlay requires the main GUI to run. But you can minimize the main GUI.

**Q: Will casinos detect the overlay?**
A: The overlay is a separate window on your computer. It doesn't interact with the casino software. However, check casino terms of service.

**Q: Can I have multiple overlays?**
A: Currently only one overlay per application instance.

**Q: Does overlay support multi-monitor?**
A: Yes, drag it to any connected monitor.

**Q: What happens if I change to compact mode?**
A: You need to restart the application or save configuration and toggle overlay off/on.

**Q: Can I change the colors?**
A: Not through the GUI. Colors are hardcoded for optimal visibility and meaning.

## Keyboard Shortcuts (Future)

Planned for future versions:
- `Ctrl+O`: Toggle overlay
- `Ctrl+Shift+O`: Switch mode (full/compact)
- `Ctrl++`: Increase opacity
- `Ctrl+-`: Decrease opacity

## Version History

**v1.0.0** - Initial overlay release
- Full and compact modes
- Draggable positioning
- Configurable opacity
- Always on top option
- Real-time updates
- Color-coded actions

## Support

For issues or questions:
1. Check main README.md
2. Verify calibration
3. Review this guide
4. Check configuration settings
5. Restart application

## Example Workflows

### Workflow 1: Learning Basic Strategy

1. Enable full overlay with high opacity
2. Position on side of screen
3. Start monitoring
4. Play hands slowly
5. Compare your instinct to recommendation
6. Learn from differences

### Workflow 2: Card Counting Practice

1. Enable full overlay
2. Show count information
3. Practice counting mentally
4. Check your count against overlay
5. Verify bet sizing matches recommendation

### Workflow 3: Actual Play (Advanced)

1. Switch to compact mode
2. Lower opacity to 0.6-0.7
3. Position in unobtrusive corner
4. Quick glance for action
5. Trust your count, verify with overlay

## Conclusion

The overlay window is designed to provide **quick, at-a-glance information** without disrupting your gameplay. Whether you're learning, practicing, or playing, the overlay adapts to your needs with full and compact modes.

**Remember**: The overlay is a tool to assist you. Use it responsibly, practice good bankroll management, and always gamble within your means.

---

**Happy Gaming! Play smart, play responsibly.**
