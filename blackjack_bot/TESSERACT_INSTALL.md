# Tesseract OCR Installation Guide

## The Problem

If you see an error like:
```
pytesseract.pytesseract.TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

This means you need to install **Tesseract OCR** separately. The `pytesseract` Python package is just a wrapper - it needs the actual Tesseract program installed on your system.

## Quick Fix by Operating System

### Windows

**Option 1: Official Installer (Recommended)**

1. **Download the installer**:
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)
   - File size: ~60 MB

2. **Run the installer**:
   - Double-click the downloaded `.exe` file
   - Click "Next" through the installation wizard
   - **IMPORTANT**: Note the installation path (usually `C:\Program Files\Tesseract-OCR`)
   - Make sure to check "Add to PATH" if prompted
   - Click "Install"

3. **Verify installation**:
   ```cmd
   tesseract --version
   ```
   You should see something like:
   ```
   tesseract v5.3.3
   ```

4. **If PATH not set automatically**:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all windows
   - **Restart your terminal/command prompt**

5. **Tell Python where Tesseract is** (if still not working):

   Edit `screen_reader.py` and add at the top:
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Option 2: Chocolatey (if you have it)**
```cmd
choco install tesseract
```

**Option 3: Scoop (if you have it)**
```cmd
scoop install tesseract
```

---

### macOS

**Option 1: Homebrew (Recommended)**

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Tesseract**:
   ```bash
   brew install tesseract
   ```

3. **Verify installation**:
   ```bash
   tesseract --version
   ```

**Option 2: MacPorts**
```bash
sudo port install tesseract
```

**Typical installation path**: `/usr/local/bin/tesseract`

---

### Linux

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install tesseract
```

**Arch Linux:**
```bash
sudo pacman -S tesseract
```

**Verify installation:**
```bash
tesseract --version
which tesseract
```

**Typical installation path**: `/usr/bin/tesseract`

---

## Verification Steps

### 1. Check if Tesseract is installed:

**Windows (Command Prompt or PowerShell):**
```cmd
tesseract --version
where tesseract
```

**macOS/Linux (Terminal):**
```bash
tesseract --version
which tesseract
```

**Expected output:**
```
tesseract v5.3.3.20231005
 leptonica-1.83.0
  libgif 5.2.1 : libjpeg 8d (libjpeg-turbo 2.1.5.1) : libpng 1.6.40 : libtiff 4.5.1 : zlib 1.2.13 : libwebp 1.3.2
 Found AVX2
 Found AVX
 Found FMA
 Found SSE4.1
 Found OpenMP 201511
```

### 2. Test Tesseract directly:

Create a test image with text and run:
```bash
tesseract test_image.png output
```

### 3. Test from Python:

```python
import pytesseract
from PIL import Image

# Test if pytesseract can find tesseract
try:
    print(pytesseract.get_tesseract_version())
    print("Tesseract is working!")
except Exception as e:
    print(f"Error: {e}")
```

---

## Common Issues and Solutions

### Issue 1: "tesseract is not installed or it's not in your PATH"

**Solution:**
- Make sure Tesseract is actually installed (run `tesseract --version`)
- Add Tesseract to your PATH (see OS-specific instructions above)
- **On Windows**: Restart your terminal/IDE after adding to PATH
- Explicitly set the path in Python:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/path/to/tesseract'

# Windows example:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# macOS example:
pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'

# Linux example:
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
```

### Issue 2: "Permission denied" (Linux/macOS)

**Solution:**
```bash
sudo chmod +x /usr/local/bin/tesseract
```

### Issue 3: Old version of Tesseract

**Solution:**
- Uninstall old version
- Install latest version (5.3+ recommended)

**Check version:**
```bash
tesseract --version
```

### Issue 4: Multiple Python environments

**Solution:**
Make sure `pytesseract` is installed in the same Python environment you're running the bot from:

```bash
# Check which Python you're using
python --version
which python

# Install pytesseract in that environment
pip install pytesseract

# Or if using conda:
conda install -c conda-forge pytesseract
```

### Issue 5: "No such file or directory: 'tesseract'"

**Solution:**
Tesseract isn't in your PATH. Either:
1. Add it to PATH (recommended)
2. Set full path in Python code (see Issue 1 solution)

---

## Setting Tesseract Path in the Blackjack Bot

If you can't or don't want to add Tesseract to your PATH, you can configure it directly in the bot.

**Option 1: Edit screen_reader.py**

Add this at the top of `/home/user/ai-summarizer/blackjack_bot/screen_reader.py`:

```python
import pytesseract
import os

# Auto-detect common Tesseract paths
if os.name == 'nt':  # Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
```

**Option 2: Add to config file**

We could add a `tesseract_path` setting to the configuration, but PATH is the cleaner solution.

---

## Quick Start Script

Save this as `test_tesseract.py` and run it:

```python
#!/usr/bin/env python3
"""Test if Tesseract OCR is properly installed."""

import sys
import os
import subprocess

def test_tesseract():
    print("=" * 60)
    print("TESSERACT OCR INSTALLATION TEST")
    print("=" * 60)
    print()

    # Test 1: Check if tesseract command exists
    print("Test 1: Checking if 'tesseract' command is available...")
    try:
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True)
        print("✓ SUCCESS: Tesseract is installed!")
        print(result.stdout.split('\n')[0])
        print()
    except FileNotFoundError:
        print("✗ FAILED: Tesseract command not found")
        print("  → Install Tesseract OCR (see TESSERACT_INSTALL.md)")
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
        print("✗ FAILED: pytesseract not installed")
        print("  → Run: pip install pytesseract")
        print()
        return False
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print("  → Set tesseract_cmd path in Python")
        print()
        return False

    # Test 3: Check where tesseract is located
    print("Test 3: Finding Tesseract location...")
    if os.name == 'nt':  # Windows
        try:
            result = subprocess.run(['where', 'tesseract'],
                                  capture_output=True, text=True)
            print(f"  Location: {result.stdout.strip()}")
        except:
            print("  Could not determine location")
    else:  # macOS/Linux
        try:
            result = subprocess.run(['which', 'tesseract'],
                                  capture_output=True, text=True)
            print(f"  Location: {result.stdout.strip()}")
        except:
            print("  Could not determine location")
    print()

    print("=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("Tesseract OCR is properly installed and configured.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_tesseract()
    sys.exit(0 if success else 1)
```

Run it:
```bash
python test_tesseract.py
```

---

## After Installing Tesseract

Once Tesseract is installed:

1. **Restart your terminal/command prompt**
2. **Restart your IDE** (VS Code, PyCharm, etc.)
3. **Test the blackjack bot**:
   ```bash
   cd /home/user/ai-summarizer/blackjack_bot
   python main.py
   ```
4. **Try the calibration tools** to test OCR

---

## Still Not Working?

### Debug Checklist:

- [ ] Tesseract is installed (`tesseract --version` works)
- [ ] Tesseract is in PATH (or path is set in Python)
- [ ] pytesseract is installed (`pip list | grep pytesseract`)
- [ ] Using the correct Python environment
- [ ] Restarted terminal/IDE after installation
- [ ] No firewall/antivirus blocking Tesseract

### Get More Help:

1. **Check installation path**:
   - Windows: `where tesseract`
   - macOS/Linux: `which tesseract`

2. **Verify permissions**:
   - Make sure you can execute tesseract
   - Try running `tesseract` in terminal

3. **Check Python environment**:
   ```bash
   python -c "import pytesseract; print(pytesseract.pytesseract.tesseract_cmd)"
   ```

4. **Manual path configuration**:
   If all else fails, edit `screen_reader.py` and hard-code the path:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'YOUR_TESSERACT_PATH_HERE'
   ```

---

## Resources

- **Official Tesseract**: https://github.com/tesseract-ocr/tesseract
- **Windows Installer**: https://github.com/UB-Mannheim/tesseract/wiki
- **pytesseract Docs**: https://pypi.org/project/pytesseract/
- **Tesseract Documentation**: https://tesseract-ocr.github.io/

---

## Summary

**The key steps are:**

1. Install Tesseract OCR (the actual program)
2. Add it to your PATH
3. Install pytesseract Python package (`pip install pytesseract`)
4. Restart terminal/IDE
5. Test with `tesseract --version`

**Most common mistake:** Installing `pytesseract` but not installing Tesseract itself.

**Quick test:** If `tesseract --version` works in your terminal, you're good to go!
