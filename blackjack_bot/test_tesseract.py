#!/usr/bin/env python3
"""Test if Tesseract OCR is properly installed and working."""

import sys
import os
import subprocess

def test_tesseract():
    """Test Tesseract installation."""
    print("=" * 60)
    print("TESSERACT OCR INSTALLATION TEST")
    print("=" * 60)
    print()

    # Test 1: Check if tesseract command exists
    print("Test 1: Checking if 'tesseract' command is available...")
    try:
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True, timeout=5)
        print("✓ SUCCESS: Tesseract is installed!")
        print("  " + result.stdout.split('\n')[0])
        print()
    except FileNotFoundError:
        print("✗ FAILED: Tesseract command not found in PATH")
        print()
        print("SOLUTION:")
        if os.name == 'nt':  # Windows
            print("  1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
            print("  2. Run the installer (tesseract-ocr-w64-setup-*.exe)")
            print("  3. During installation, make sure 'Add to PATH' is checked")
            print("  4. Restart your terminal/command prompt")
        elif sys.platform == 'darwin':  # macOS
            print("  Run: brew install tesseract")
        else:  # Linux
            print("  Ubuntu/Debian: sudo apt install tesseract-ocr")
            print("  Fedora: sudo dnf install tesseract")
            print("  Arch: sudo pacman -S tesseract")
        print()
        print("For detailed instructions, see: TESSERACT_INSTALL.md")
        print()
        return False
    except subprocess.TimeoutExpired:
        print("✗ FAILED: Tesseract command timed out")
        print()
        return False

    # Test 2: Check if pytesseract can find it
    print("Test 2: Checking if Python can use Tesseract...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ SUCCESS: Python can use Tesseract v{version}")
        print()
    except ImportError:
        print("✗ FAILED: pytesseract package not installed")
        print()
        print("SOLUTION:")
        print("  Run: pip install pytesseract")
        print()
        return False
    except pytesseract.pytesseract.TesseractNotFoundError as e:
        print(f"✗ FAILED: {e}")
        print()
        print("SOLUTION:")
        print("  Tesseract is not in your PATH. Either:")
        print("  1. Add Tesseract to your PATH (recommended)")
        print("  2. Set the path in screen_reader.py")
        print()
        if os.name == 'nt':
            print("  Common Windows paths:")
            print("    C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
            print("    C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe")
        print()
        print("For detailed instructions, see: TESSERACT_INSTALL.md")
        print()
        return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print()
        return False

    # Test 3: Check where tesseract is located
    print("Test 3: Finding Tesseract installation location...")
    if os.name == 'nt':  # Windows
        try:
            result = subprocess.run(['where', 'tesseract'],
                                  capture_output=True, text=True, timeout=5)
            locations = result.stdout.strip().split('\n')
            for loc in locations:
                if loc:
                    print(f"  → {loc}")
        except:
            print("  Could not determine location")
    else:  # macOS/Linux
        try:
            result = subprocess.run(['which', 'tesseract'],
                                  capture_output=True, text=True, timeout=5)
            print(f"  → {result.stdout.strip()}")
        except:
            print("  Could not determine location")
    print()

    # Test 4: Test actual OCR
    print("Test 4: Testing OCR functionality...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        import pytesseract
        import numpy as np

        # Create a simple test image with text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)

        try:
            # Try to use a font, fall back to default if not available
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()

        draw.text((10, 10), "TEST 123", fill='black', font=font)

        # Convert PIL image to numpy array for tesseract
        img_array = np.array(img)

        # Perform OCR
        text = pytesseract.image_to_string(img_array)
        text = text.strip()

        if text:
            print(f"✓ SUCCESS: OCR detected text: '{text}'")
            print()
        else:
            print("⚠ WARNING: OCR ran but detected no text")
            print("  This might indicate Tesseract is working but needs tuning")
            print()
    except Exception as e:
        print(f"✗ FAILED: OCR test error: {e}")
        print()
        return False

    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print()
    print("Tesseract OCR is properly installed and working.")
    print("You can now use the blackjack bot's screen reading features.")
    print("=" * 60)
    return True


def main():
    """Run the test."""
    print()
    success = test_tesseract()
    print()

    if not success:
        print("❌ Some tests failed. Please fix the issues above.")
        print()
        print("Quick fixes:")
        print("  1. Make sure Tesseract OCR is installed")
        print("  2. Make sure it's in your PATH")
        print("  3. Restart your terminal after installation")
        print()
        print("For detailed help, read: TESSERACT_INSTALL.md")
        print()
        sys.exit(1)
    else:
        print("✅ Everything is working! You're ready to go.")
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
