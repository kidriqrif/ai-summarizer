#!/usr/bin/env python3
"""Main entry point for Blackjack Bot application."""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from gui import BlackjackBotGUI


def main():
    """Launch the blackjack bot GUI application."""
    print("=" * 60)
    print("Blackjack Bot - Optimal Play Assistant")
    print("=" * 60)
    print()
    print("Starting GUI application...")
    print()
    print("IMPORTANT NOTES:")
    print("1. This tool is for EDUCATIONAL purposes only")
    print("2. Check your local laws regarding online gambling")
    print("3. Review casino terms of service before use")
    print("4. Always gamble responsibly")
    print()
    print("=" * 60)
    print()

    try:
        app = BlackjackBotGUI()
        app.run()
    except KeyboardInterrupt:
        print("\nApplication closed by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting application: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        print("\nAnd Tesseract OCR is installed on your system.")
        sys.exit(1)


if __name__ == "__main__":
    main()
