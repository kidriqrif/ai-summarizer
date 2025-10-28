"""Screen capture and OCR for reading blackjack game state."""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import mss
import cv2
import numpy as np
from PIL import Image
import pytesseract


@dataclass
class GameState:
    """Represents the current game state."""
    dealer_cards: List[str]
    player_cards: List[str]
    balance: float
    current_bet: float
    is_dealer_turn: bool = False
    can_double: bool = True
    can_split: bool = False
    can_surrender: bool = True
    shuffle_detected: bool = False  # New: indicates if shuffle/new shoe detected


class ScreenReader:
    """Captures and reads blackjack game from screen."""

    # Card recognition patterns
    CARD_PATTERNS = {
        'A': ['ace', 'a'],
        '2': ['2', 'two'],
        '3': ['3', 'three'],
        '4': ['4', 'four'],
        '5': ['5', 'five'],
        '6': ['6', 'six'],
        '7': ['7', 'seven'],
        '8': ['8', 'eight'],
        '9': ['9', 'nine'],
        '10': ['10', 'ten'],
        'J': ['j', 'jack'],
        'Q': ['q', 'queen'],
        'K': ['k', 'king']
    }

    def __init__(self, dealer_region: Dict = None, player_region: Dict = None,
                 balance_region: Dict = None, bet_region: Dict = None,
                 shuffle_region: Dict = None):
        """
        Initialize screen reader with capture regions.

        Args:
            dealer_region: Dict with x, y, width, height for dealer cards
            player_region: Dict with x, y, width, height for player cards
            balance_region: Dict with x, y, width, height for balance display
            bet_region: Dict with x, y, width, height for bet display
            shuffle_region: Dict with x, y, width, height for shuffle indicator (optional)
        """
        self.dealer_region = dealer_region or {"x": 0, "y": 0, "width": 400, "height": 150}
        self.player_region = player_region or {"x": 0, "y": 200, "width": 400, "height": 150}
        self.balance_region = balance_region or {"x": 0, "y": 400, "width": 200, "height": 50}
        self.bet_region = bet_region or {"x": 0, "y": 450, "width": 200, "height": 50}
        self.shuffle_region = shuffle_region or {"x": 200, "y": 0, "width": 300, "height": 100}

        self.sct = mss.mss()
        self.last_cards_seen = []  # Track last cards to detect new shoe

    def capture_region(self, region: Dict) -> np.ndarray:
        """
        Capture a screen region.

        Args:
            region: Dictionary with x, y, width, height

        Returns:
            Numpy array of the captured image
        """
        monitor = {
            "top": region["y"],
            "left": region["x"],
            "width": region["width"],
            "height": region["height"]
        }

        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)

        # Convert BGRA to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

        return img

    def preprocess_for_ocr(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.

        Args:
            img: Input image

        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)

        # Increase contrast
        kernel = np.array([[-1, -1, -1],
                          [-1, 9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)

        return sharpened

    def ocr_text(self, img: np.ndarray) -> str:
        """
        Perform OCR on image.

        Args:
            img: Input image

        Returns:
            Extracted text
        """
        processed = self.preprocess_for_ocr(img)
        text = pytesseract.image_to_string(processed, config='--psm 6')
        return text.lower().strip()

    def parse_cards(self, text: str) -> List[str]:
        """
        Parse card values from OCR text.

        Args:
            text: OCR text output

        Returns:
            List of card values
        """
        cards = []

        # Remove common OCR noise
        text = text.replace('|', '1').replace('l', '1').replace('o', '0')

        # Try to find card patterns
        for card_value, patterns in self.CARD_PATTERNS.items():
            for pattern in patterns:
                if pattern in text:
                    cards.append(card_value)

        # Try to find numeric cards
        numbers = re.findall(r'\b([2-9]|10)\b', text)
        for num in numbers:
            if num not in cards:
                cards.append(num)

        return cards

    def parse_currency(self, text: str) -> float:
        """
        Parse currency value from OCR text.

        Args:
            text: OCR text output

        Returns:
            Numeric value
        """
        # Remove currency symbols and commas
        text = text.replace('$', '').replace(',', '').replace('€', '')
        text = text.replace('£', '').strip()

        # Find numeric values
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return 0.0

        return 0.0

    def read_dealer_cards(self) -> List[str]:
        """
        Read dealer's cards from screen.

        Returns:
            List of dealer's card values
        """
        img = self.capture_region(self.dealer_region)
        text = self.ocr_text(img)
        cards = self.parse_cards(text)
        return cards

    def read_player_cards(self) -> List[str]:
        """
        Read player's cards from screen.

        Returns:
            List of player's card values
        """
        img = self.capture_region(self.player_region)
        text = self.ocr_text(img)
        cards = self.parse_cards(text)
        return cards

    def read_balance(self) -> float:
        """
        Read player's balance from screen.

        Returns:
            Current balance
        """
        img = self.capture_region(self.balance_region)
        text = self.ocr_text(img)
        return self.parse_currency(text)

    def read_bet(self) -> float:
        """
        Read current bet amount from screen.

        Returns:
            Current bet amount
        """
        img = self.capture_region(self.bet_region)
        text = self.ocr_text(img)
        return self.parse_currency(text)

    def detect_shuffle(self) -> bool:
        """
        Detect if shoe is being shuffled or changed.

        Looks for common shuffle indicators:
        - "Shuffle" or "Shuffling" text
        - "New Shoe" text
        - "Dealer Shuffle" text
        - No cards visible (empty table between rounds at start of shoe)

        Returns:
            True if shuffle detected
        """
        # Method 1: Check shuffle region for shuffle-related text
        img = self.capture_region(self.shuffle_region)
        text = self.ocr_text(img)

        shuffle_keywords = [
            'shuffle', 'shuffling', 'new shoe', 'new deck',
            'dealer shuffle', 'shuffled', 'reshuffling'
        ]

        for keyword in shuffle_keywords:
            if keyword in text:
                return True

        # Method 2: Check dealer region for shuffle indicators
        dealer_img = self.capture_region(self.dealer_region)
        dealer_text = self.ocr_text(dealer_img)

        for keyword in shuffle_keywords:
            if keyword in dealer_text:
                return True

        return False

    def read_game_state(self) -> GameState:
        """
        Read complete game state from screen.

        Returns:
            GameState object with all current information
        """
        dealer_cards = self.read_dealer_cards()
        player_cards = self.read_player_cards()
        balance = self.read_balance()
        current_bet = self.read_bet()
        shuffle_detected = self.detect_shuffle()

        # Determine game state
        can_split = (len(player_cards) == 2 and
                    (player_cards[0] == player_cards[1] or
                     (player_cards[0] in ['J', 'Q', 'K', '10'] and
                      player_cards[1] in ['J', 'Q', 'K', '10'])))

        can_double = len(player_cards) == 2
        can_surrender = len(player_cards) == 2

        return GameState(
            dealer_cards=dealer_cards,
            player_cards=player_cards,
            balance=balance,
            current_bet=current_bet,
            can_double=can_double,
            can_split=can_split,
            can_surrender=can_surrender,
            shuffle_detected=shuffle_detected
        )

    def update_regions(self, dealer: Dict = None, player: Dict = None,
                      balance: Dict = None, bet: Dict = None, shuffle: Dict = None):
        """
        Update capture regions.

        Args:
            dealer: New dealer region
            player: New player region
            balance: New balance region
            bet: New bet region
            shuffle: New shuffle indicator region
        """
        if dealer:
            self.dealer_region = dealer
        if player:
            self.player_region = player
        if balance:
            self.balance_region = balance
        if bet:
            self.bet_region = bet
        if shuffle:
            self.shuffle_region = shuffle

    def save_calibration_screenshot(self, filename: str = "calibration.png"):
        """
        Save a screenshot with all regions marked for calibration.

        Args:
            filename: Output filename
        """
        # Capture full screen
        monitor = self.sct.monitors[1]  # Primary monitor
        screenshot = self.sct.grab(monitor)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

        # Draw rectangles for each region
        regions = [
            (self.dealer_region, (255, 0, 0), "Dealer"),
            (self.player_region, (0, 255, 0), "Player"),
            (self.balance_region, (0, 0, 255), "Balance"),
            (self.bet_region, (255, 255, 0), "Bet"),
            (self.shuffle_region, (255, 0, 255), "Shuffle")
        ]

        for region, color, label in regions:
            x, y, w, h = region["x"], region["y"], region["width"], region["height"]
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.5, color, 2)

        # Save image
        cv2.imwrite(filename, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        print(f"Calibration screenshot saved to {filename}")
