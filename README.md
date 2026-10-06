# 🧮 Modern Professional Calculator (Python GUI)

A sleek, modern, desktop calculator application built with **Python** and **Tkinter**, inspired by Windows 11 Fluent Design and modern macOS interfaces.

---

## ✨ Features

- **🎨 Modern Dark & Light Mode:** Toggle between sleek Dark Mode (`Zinc / Slate` palette) and crisp Light Mode with the top header button (`☀️`/`🌙`).
- **🖥️ High-DPI Display Support:** Automatic Windows DPI awareness scaling for razor-sharp text and borders on 1080p, 1440p, and 4K displays.
- **🕒 Expandable Calculation History:**
  - Slide-out history panel recording expressions and results.
  - Click any past calculation card to load its result back into the active calculation.
  - One-click clear history button.
- **🔢 Full Standard & Scientific Utility:**
  - Basic arithmetic: `+`, `−`, `×`, `÷`
  - Unary math: `√x` (square root), `x²` (square), `1/x` (reciprocal), `%` (percentage), `±` (negate)
  - Memory operations: `MC` (Clear), `MR` (Recall), `M+` (Add), `M−` (Subtract), `MS` (Store)
- **📏 High-Precision Arithmetic:** Built with Python's `Decimal` engine to eliminate floating-point rounding bugs (e.g., `0.1 + 0.2` strictly equals `0.3`).
- **🔤 Dynamic Font Scaling:** Display automatically scales font sizes down for large numbers, preventing clipping or overflow.
- **📋 Smart Clipboard:**
  - Click the display or press `Ctrl+C` to copy with a smooth floating toast notification.
  - Press `Ctrl+V` to paste numbers from clipboard.
- **⌨️ Keyboard Shortcuts & Tactile Feedback:** Full physical keyboard support with visual button-flash animations on press.
- **📦 Zero External Dependencies:** Runs natively on Python 3.x using Tkinter.

---

## 🚀 How to Run

Run directly with Python:

```bash
python calculator.py
```

Or run the automated test suite:

```bash
python -m unittest discover
```

---

## ⌨️ Keyboard Shortcuts Reference

| Key / Shortcut | Function |
| :--- | :--- |
| `0` – `9` (or Numpad) | Enter Digits |
| `.` or `,` | Decimal Point |
| `+`, `-`, `*`, `/` | Basic Operators (`+`, `−`, `×`, `÷`) |
| `Enter` or `=` | Calculate Result (`=`) |
| `Backspace` | Delete last digit (⌫) |
| `Delete` | Clear current entry (`CE`) |
| `Escape` | Clear all (`C`) |
| `%` | Percentage |
| `r` | Square Root (`√x`) |
| `q` | Square (`x²`) |
| `i` | Reciprocal (`1/x`) |
| `F9` | Toggle Positive / Negative (`±`) |
| `Ctrl + H` | Toggle History Drawer |
| `Ctrl + C` | Copy current display value to clipboard |
| `Ctrl + V` | Paste number from clipboard |

---

## 📁 Project Structure

```
Calculator/
├── assets/
│   ├── icon.ico           # Windows application icon
│   └── icon.png           # High-resolution icon preview
├── calc_logic.py          # Arithmetic engine with Decimal precision & state management
├── calculator.py          # Main Tkinter GUI application & styling
├── test_calc_logic.py     # Unit test suite for arithmetic & edge cases
├── test_gui.py            # Automated integration test suite for GUI widgets
└── README.md              # Project documentation
```
