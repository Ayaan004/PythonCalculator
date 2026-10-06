"""
Professional Modern Calculator GUI built with Python and Tkinter.
Features:
- Windows High-DPI crisp rendering
- Dark / Light mode toggle
- Expandable calculation history drawer with click-to-recall
- Full memory operations (MC, MR, M+, M-, MS)
- Unary advanced functions (√x, x², 1/x, %)
- Precision Decimal arithmetic (prevents floating-point artifacts)
- Auto-scaling font display (never clips long numbers)
- Full physical keyboard support with tactile button-press flash animations
- Copy (Ctrl+C) and Paste (Ctrl+V) with floating toast alert
"""

import os
import sys
import tkinter as tk
from tkinter import font as tkfont
from typing import Dict, Any, Callable, Optional

from calc_logic import CalculatorEngine

# Enable High-DPI awareness on Windows to prevent blurry rendering
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass


THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "bg": "#18181b",               # Deep Zinc background
        "display_bg": "#18181b",
        "header_bg": "#18181b",
        "display_primary": "#ffffff",
        "display_expr": "#94a3b8",
        # Number buttons
        "btn_num_bg": "#27272a",
        "btn_num_hover": "#3f3f46",
        "btn_num_active": "#52525b",
        "btn_num_fg": "#f4f4f5",
        # Top function buttons (CE, C, ⌫, √, x², etc.)
        "btn_fn_bg": "#202023",
        "btn_fn_hover": "#2e313a",
        "btn_fn_active": "#3b3e4a",
        "btn_fn_fg": "#d4d4d8",
        # Operator buttons (+, -, ×, ÷)
        "btn_op_bg": "#202023",
        "btn_op_hover": "#2e313a",
        "btn_op_active": "#3b3e4a",
        "btn_op_fg": "#60a5fa",        # Sleek electric blue
        # Equals button
        "btn_eq_bg": "#2563eb",        # Royal vibrant blue
        "btn_eq_hover": "#3b82f6",
        "btn_eq_active": "#1d4ed8",
        "btn_eq_fg": "#ffffff",
        # Memory bar
        "btn_mem_bg": "#18181b",
        "btn_mem_hover": "#27272a",
        "btn_mem_active": "#3f3f46",
        "btn_mem_fg_disabled": "#52525b",
        "btn_mem_fg_active": "#94a3b8",
        # Toast / badges
        "toast_bg": "#27272a",
        "toast_fg": "#4ade80",
        # History drawer
        "history_bg": "#141416",
        "history_border": "#27272a",
        "history_title": "#f4f4f5",
        "history_card_bg": "#1c1c20",
        "history_card_hover": "#27272a",
        "history_expr": "#a1a1aa",
        "history_result": "#ffffff",
        "history_empty": "#71717a",
    },
    "light": {
        "bg": "#f4f4f5",
        "display_bg": "#f4f4f5",
        "header_bg": "#f4f4f5",
        "display_primary": "#09090b",
        "display_expr": "#64748b",
        # Number buttons
        "btn_num_bg": "#ffffff",
        "btn_num_hover": "#f1f5f9",
        "btn_num_active": "#e2e8f0",
        "btn_num_fg": "#0f172a",
        # Top function buttons
        "btn_fn_bg": "#e4e4e7",
        "btn_fn_hover": "#d4d4d8",
        "btn_fn_active": "#cbd5e1",
        "btn_fn_fg": "#334155",
        # Operator buttons
        "btn_op_bg": "#e4e4e7",
        "btn_op_hover": "#d4d4d8",
        "btn_op_active": "#cbd5e1",
        "btn_op_fg": "#2563eb",
        # Equals button
        "btn_eq_bg": "#2563eb",
        "btn_eq_hover": "#3b82f6",
        "btn_eq_active": "#1d4ed8",
        "btn_eq_fg": "#ffffff",
        # Memory bar
        "btn_mem_bg": "#f4f4f5",
        "btn_mem_hover": "#e4e4e7",
        "btn_mem_active": "#cbd5e1",
        "btn_mem_fg_disabled": "#a1a1aa",
        "btn_mem_fg_active": "#475569",
        # Toast / badges
        "toast_bg": "#18181b",
        "toast_fg": "#4ade80",
        # History drawer
        "history_bg": "#ffffff",
        "history_border": "#e4e4e7",
        "history_title": "#09090b",
        "history_card_bg": "#f8fafc",
        "history_card_hover": "#f1f5f9",
        "history_expr": "#64748b",
        "history_result": "#0f172a",
        "history_empty": "#94a3b8",
    }
}


class ModernButton(tk.Button):
    """Sleek flat button with micro-interactions, smooth hover and active state colors."""
    def __init__(
        self,
        master,
        text: str,
        command: Optional[Callable[[], None]] = None,
        bg: str = "#27272a",
        hover_bg: str = "#3f3f46",
        active_bg: str = "#52525b",
        fg: str = "#ffffff",
        font_style=("Segoe UI", 13),
        **kwargs
    ):
        super().__init__(
            master,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief="flat",
            bd=0,
            highlightthickness=0,
            cursor="hand2",
            font=font_style,
            takefocus=0,
            **kwargs
        )
        self.normal_bg = bg
        self.hover_bg = hover_bg
        self.active_bg = active_bg
        self.normal_fg = fg

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event):
        if self["state"] != "disabled":
            self.configure(bg=self.hover_bg)

    def _on_leave(self, _event):
        if self["state"] != "disabled":
            self.configure(bg=self.normal_bg)

    def flash_press(self):
        """Briefly illuminate the button to give visual feedback for keyboard presses."""
        self.configure(bg=self.active_bg)
        self.after(90, lambda: self.configure(bg=self.normal_bg))

    def update_palette(self, bg: str, hover_bg: str, active_bg: str, fg: str):
        self.normal_bg = bg
        self.hover_bg = hover_bg
        self.active_bg = active_bg
        self.normal_fg = fg
        self.configure(
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg
        )


class CalculatorApp(tk.Tk):
    """Main Calculator GUI application."""
    def __init__(self):
        super().__init__()

        self.engine = CalculatorEngine()
        self.current_theme = "dark"
        self.history_open = False
        self.toast_job = None

        self.title("Calculator")
        self.configure(bg=THEMES[self.current_theme]["bg"])

        # Set Window Icon if available
        self._set_app_icon()

        # Geometry dimensions
        self.main_width = 370
        self.history_width = 280
        self.app_height = 570
        self.geometry(f"{self.main_width}x{self.app_height}")
        self.minsize(350, 520)

        # Center on screen
        self._center_window()

        # Build UI
        self._setup_layout()
        self._bind_keyboard()
        self._update_display()

    def _set_app_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _center_window(self):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = max(0, (screen_w - self.main_width) // 2)
        pos_y = max(0, (screen_h - self.app_height) // 2)
        self.geometry(f"{self.main_width}x{self.app_height}+{pos_x}+{pos_y}")

    def _setup_layout(self):
        palette = THEMES[self.current_theme]

        # Container for main calculator & history panel side-by-side
        self.root_container = tk.Frame(self, bg=palette["bg"])
        self.root_container.pack(fill="both", expand=True)

        # Main Calculator Frame
        self.calc_frame = tk.Frame(self.root_container, bg=palette["bg"])
        self.calc_frame.pack(side="left", fill="both", expand=True)

        # 1. Header Bar (Standard Title, Theme Toggle, History Toggle)
        self.header_frame = tk.Frame(self.calc_frame, bg=palette["header_bg"], height=42)
        self.header_frame.pack(fill="x", padx=14, pady=(10, 0))

        self.lbl_title = tk.Label(
            self.header_frame,
            text="Standard",
            font=("Segoe UI", 13, "bold"),
            bg=palette["header_bg"],
            fg=palette["display_primary"]
        )
        self.lbl_title.pack(side="left")

        # Header tool buttons
        self.header_btn_frame = tk.Frame(self.header_frame, bg=palette["header_bg"])
        self.header_btn_frame.pack(side="right")

        self.btn_theme = tk.Button(
            self.header_btn_frame,
            text="☀️",
            command=self.toggle_theme,
            font=("Segoe UI", 11),
            bg=palette["header_bg"],
            fg=palette["display_primary"],
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=6,
            pady=2,
            takefocus=0
        )
        self.btn_theme.pack(side="left", padx=(0, 4))

        self.btn_history = tk.Button(
            self.header_btn_frame,
            text="🕒 History",
            command=self.toggle_history_panel,
            font=("Segoe UI", 10),
            bg=palette["header_bg"],
            fg=palette["display_primary"],
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=6,
            pady=2,
            takefocus=0
        )
        self.btn_history.pack(side="left")

        # 2. Display Area
        self.display_frame = tk.Frame(self.calc_frame, bg=palette["display_bg"])
        self.display_frame.pack(fill="x", padx=14, pady=(4, 6))

        # Expression history label
        self.lbl_expr = tk.Label(
            self.display_frame,
            text="",
            font=("Segoe UI", 12),
            bg=palette["display_bg"],
            fg=palette["display_expr"],
            anchor="e"
        )
        self.lbl_expr.pack(fill="x", pady=(2, 0))

        # Primary input / result label
        self.lbl_display = tk.Label(
            self.display_frame,
            text="0",
            font=("Segoe UI", 34, "bold"),
            bg=palette["display_bg"],
            fg=palette["display_primary"],
            anchor="e"
        )
        self.lbl_display.pack(fill="x", pady=(0, 2))

        # Quick copy badge on click
        self.lbl_display.bind("<Button-1>", lambda _e: self.copy_to_clipboard())
        self.lbl_display.configure(cursor="hand2")

        # Toast notification pill
        self.toast_label = tk.Label(
            self.calc_frame,
            text="✓ Copied to clipboard",
            font=("Segoe UI", 9, "bold"),
            bg=palette["toast_bg"],
            fg=palette["toast_fg"],
            padx=12,
            pady=5,
            relief="flat"
        )

        # 3. Memory Bar
        self.memory_frame = tk.Frame(self.calc_frame, bg=palette["bg"])
        self.memory_frame.pack(fill="x", padx=14, pady=(2, 6))
        for col in range(5):
            self.memory_frame.columnconfigure(col, weight=1)

        self.mem_buttons = {}
        mem_defs = [
            ("MC", self._on_mem_clear),
            ("MR", self._on_mem_recall),
            ("M+", self._on_mem_add),
            ("M−", self._on_mem_sub),
            ("MS", self._on_mem_store)
        ]

        for idx, (m_text, m_cmd) in enumerate(mem_defs):
            btn = tk.Button(
                self.memory_frame,
                text=m_text,
                command=m_cmd,
                font=("Segoe UI", 9, "bold"),
                bg=palette["btn_mem_bg"],
                fg=palette["btn_mem_fg_disabled"],
                relief="flat",
                bd=0,
                cursor="hand2",
                takefocus=0
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=2, pady=1)
            self.mem_buttons[m_text] = btn

        # 4. Keypad Grid
        self.keypad_frame = tk.Frame(self.calc_frame, bg=palette["bg"])
        self.keypad_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        for c in range(4):
            self.keypad_frame.columnconfigure(c, weight=1)
        for r in range(6):
            self.keypad_frame.rowconfigure(r, weight=1)

        self.all_buttons: Dict[str, ModernButton] = {}
        self._build_keypad()

        # 5. History Side Panel (Initially hidden)
        self.history_frame = tk.Frame(
            self.root_container,
            bg=palette["history_bg"],
            width=self.history_width,
            highlightbackground=palette["history_border"],
            highlightthickness=1
        )

        self._build_history_panel()

    def _build_keypad(self):
        palette = THEMES[self.current_theme]

        # Layout: 6 rows x 4 columns
        grid_items = [
            # Row 0
            ("%", 0, 0, "fn", lambda: self._on_percent()),
            ("CE", 0, 1, "fn", lambda: self._on_clear_entry()),
            ("C", 0, 2, "fn", lambda: self._on_clear_all()),
            ("⌫", 0, 3, "fn", lambda: self._on_backspace()),

            # Row 1
            ("1/x", 1, 0, "fn", lambda: self._on_reciprocal()),
            ("x²", 1, 1, "fn", lambda: self._on_square()),
            ("√x", 1, 2, "fn", lambda: self._on_sqrt()),
            ("÷", 1, 3, "op", lambda: self._on_operator("÷")),

            # Row 2
            ("7", 2, 0, "num", lambda: self._on_digit("7")),
            ("8", 2, 1, "num", lambda: self._on_digit("8")),
            ("9", 2, 2, "num", lambda: self._on_digit("9")),
            ("×", 2, 3, "op", lambda: self._on_operator("×")),

            # Row 3
            ("4", 3, 0, "num", lambda: self._on_digit("4")),
            ("5", 3, 1, "num", lambda: self._on_digit("5")),
            ("6", 3, 2, "num", lambda: self._on_digit("6")),
            ("−", 3, 3, "op", lambda: self._on_operator("−")),

            # Row 4
            ("1", 4, 0, "num", lambda: self._on_digit("1")),
            ("2", 4, 1, "num", lambda: self._on_digit("2")),
            ("3", 4, 2, "num", lambda: self._on_digit("3")),
            ("+", 4, 3, "op", lambda: self._on_operator("+")),

            # Row 5
            ("±", 5, 0, "num", lambda: self._on_toggle_sign()),
            ("0", 5, 1, "num", lambda: self._on_digit("0")),
            (".", 5, 2, "num", lambda: self._on_decimal()),
            ("=", 5, 3, "eq", lambda: self._on_equals()),
        ]

        for text, r, c, b_type, cmd in grid_items:
            if b_type == "num":
                bg = palette["btn_num_bg"]
                hover = palette["btn_num_hover"]
                active = palette["btn_num_active"]
                fg = palette["btn_num_fg"]
                font_style = ("Segoe UI", 15, "bold") if text.isdigit() or text in (".", "±") else ("Segoe UI", 13)
            elif b_type == "fn":
                bg = palette["btn_fn_bg"]
                hover = palette["btn_fn_hover"]
                active = palette["btn_fn_active"]
                fg = palette["btn_fn_fg"]
                font_style = ("Segoe UI", 12)
            elif b_type == "op":
                bg = palette["btn_op_bg"]
                hover = palette["btn_op_hover"]
                active = palette["btn_op_active"]
                fg = palette["btn_op_fg"]
                font_style = ("Segoe UI", 16)
            else:  # eq
                bg = palette["btn_eq_bg"]
                hover = palette["btn_eq_hover"]
                active = palette["btn_eq_active"]
                fg = palette["btn_eq_fg"]
                font_style = ("Segoe UI", 16, "bold")

            btn = ModernButton(
                self.keypad_frame,
                text=text,
                command=cmd,
                bg=bg,
                hover_bg=hover,
                active_bg=active,
                fg=fg,
                font_style=font_style
            )
            btn.grid(row=r, column=c, sticky="nsew", padx=2, pady=2)
            self.all_buttons[text] = btn

    def _build_history_panel(self):
        palette = THEMES[self.current_theme]

        # Top row in history panel: Title & Clear History button
        hist_header = tk.Frame(self.history_frame, bg=palette["history_bg"])
        hist_header.pack(fill="x", padx=12, pady=10)

        lbl_hist_title = tk.Label(
            hist_header,
            text="History",
            font=("Segoe UI", 12, "bold"),
            bg=palette["history_bg"],
            fg=palette["history_title"]
        )
        lbl_hist_title.pack(side="left")

        self.btn_clear_hist = tk.Button(
            hist_header,
            text="🗑 Clear",
            command=self._on_clear_history,
            font=("Segoe UI", 9),
            bg=palette["history_bg"],
            fg=palette["display_expr"],
            relief="flat",
            bd=0,
            cursor="hand2",
            takefocus=0
        )
        self.btn_clear_hist.pack(side="right")

        # Scrollable container for history items
        self.hist_canvas = tk.Canvas(
            self.history_frame,
            bg=palette["history_bg"],
            bd=0,
            highlightthickness=0
        )
        self.hist_scrollbar = tk.Scrollbar(
            self.history_frame,
            orient="vertical",
            command=self.hist_canvas.yview
        )
        self.hist_items_frame = tk.Frame(
            self.hist_canvas,
            bg=palette["history_bg"]
        )

        self.hist_items_frame.bind(
            "<Configure>",
            lambda _e: self.hist_canvas.configure(scrollregion=self.hist_canvas.bbox("all"))
        )
        self.hist_canvas.create_window((0, 0), window=self.hist_items_frame, anchor="nw", width=self.history_width - 24)
        self.hist_canvas.configure(yscrollcommand=self.hist_scrollbar.set)

        self.hist_canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=(0, 10))
        self.hist_scrollbar.pack(side="right", fill="y", pady=(0, 10))

    def _flash(self, key_name: str):
        btn = self.all_buttons.get(key_name)
        if btn:
            btn.flash_press()

    def _bind_keyboard(self):
        """Bind keyboard inputs for natural, responsive calculator experience."""
        # Digits
        for num in "0123456789":
            self.bind_all(f"<Key-{num}>", lambda _e, d=num: (self._flash(d), self._on_digit(d)))
            self.bind_all(f"<KP_{num}>", lambda _e, d=num: (self._flash(d), self._on_digit(d)))

        # Decimal
        self.bind_all("<period>", lambda _e: (self._flash("."), self._on_decimal()))
        self.bind_all("<comma>", lambda _e: (self._flash("."), self._on_decimal()))
        self.bind_all("<KP_Decimal>", lambda _e: (self._flash("."), self._on_decimal()))

        # Operators
        self.bind_all("<plus>", lambda _e: (self._flash("+"), self._on_operator("+")))
        self.bind_all("<KP_Add>", lambda _e: (self._flash("+"), self._on_operator("+")))

        self.bind_all("<minus>", lambda _e: (self._flash("−"), self._on_operator("−")))
        self.bind_all("<KP_Subtract>", lambda _e: (self._flash("−"), self._on_operator("−")))

        self.bind_all("<asterisk>", lambda _e: (self._flash("×"), self._on_operator("×")))
        self.bind_all("<KP_Multiply>", lambda _e: (self._flash("×"), self._on_operator("×")))

        self.bind_all("<slash>", lambda _e: (self._flash("÷"), self._on_operator("÷")))
        self.bind_all("<KP_Divide>", lambda _e: (self._flash("÷"), self._on_operator("÷")))

        # Calculate / Equals
        self.bind_all("<Return>", lambda _e: (self._flash("="), self._on_equals()))
        self.bind_all("<KP_Enter>", lambda _e: (self._flash("="), self._on_equals()))
        self.bind_all("<equal>", lambda _e: (self._flash("="), self._on_equals()))

        # Backspace & Delete
        self.bind_all("<BackSpace>", lambda _e: (self._flash("⌫"), self._on_backspace()))
        self.bind_all("<Delete>", lambda _e: (self._flash("CE"), self._on_clear_entry()))

        # Clear All
        self.bind_all("<Escape>", lambda _e: (self._flash("C"), self._on_clear_all()))

        # Percentage
        self.bind_all("<percent>", lambda _e: (self._flash("%"), self._on_percent()))

        # Function shortcuts
        self.bind_all("<F9>", lambda _e: (self._flash("±"), self._on_toggle_sign()))
        self.bind_all("<Key-r>", lambda _e: (self._flash("√x"), self._on_sqrt()))
        self.bind_all("<Key-q>", lambda _e: (self._flash("x²"), self._on_square()))
        self.bind_all("<Key-i>", lambda _e: (self._flash("1/x"), self._on_reciprocal()))

        # Copy & Paste
        self.bind_all("<Control-c>", lambda _e: self.copy_to_clipboard())
        self.bind_all("<Control-v>", lambda _e: self.paste_from_clipboard())
        self.bind_all("<Control-h>", lambda _e: self.toggle_history_panel())

    # User Actions
    def _on_digit(self, digit: str):
        self.engine.input_digit(digit)
        self._update_display()

    def _on_decimal(self):
        self.engine.input_decimal()
        self._update_display()

    def _on_operator(self, op: str):
        self.engine.input_operator(op)
        self._update_display()

    def _on_equals(self):
        self.engine.calculate_equals()
        self._update_display()
        self._refresh_history_ui()

    def _on_clear_all(self):
        self.engine.clear_all()
        self._update_display()

    def _on_clear_entry(self):
        self.engine.clear_entry()
        self._update_display()

    def _on_backspace(self):
        self.engine.backspace()
        self._update_display()

    def _on_toggle_sign(self):
        self.engine.toggle_sign()
        self._update_display()

    def _on_percent(self):
        self.engine.calculate_percentage()
        self._update_display()

    def _on_sqrt(self):
        self.engine.calculate_square_root()
        self._update_display()
        self._refresh_history_ui()

    def _on_square(self):
        self.engine.calculate_square()
        self._update_display()
        self._refresh_history_ui()

    def _on_reciprocal(self):
        self.engine.calculate_reciprocal()
        self._update_display()
        self._refresh_history_ui()

    # Memory Operations
    def _on_mem_clear(self):
        self.engine.memory_clear()
        self._update_display()

    def _on_mem_recall(self):
        self.engine.memory_recall()
        self._update_display()

    def _on_mem_add(self):
        self.engine.memory_add()
        self._update_display()

    def _on_mem_sub(self):
        self.engine.memory_subtract()
        self._update_display()

    def _on_mem_store(self):
        self.engine.memory_store()
        self._update_display()

    def _update_display(self):
        """Update display text and dynamically scale font size to avoid clipping."""
        disp_text = self.engine.get_display_text()
        expr_text = self.engine.get_expression_text()

        self.lbl_expr.configure(text=expr_text)
        self.lbl_display.configure(text=disp_text)

        # Dynamic font scaling based on length
        length = len(disp_text)
        if length <= 9:
            font_size = 34
        elif length <= 12:
            font_size = 28
        elif length <= 15:
            font_size = 22
        else:
            font_size = 18

        self.lbl_display.configure(font=("Segoe UI", font_size, "bold"))

        # Update memory buttons state
        palette = THEMES[self.current_theme]
        mem_active_fg = palette["btn_mem_fg_active"]
        mem_disabled_fg = palette["btn_mem_fg_disabled"]

        has_mem = self.engine.has_memory
        self.mem_buttons["MC"].configure(
            fg=mem_active_fg if has_mem else mem_disabled_fg,
            state="normal" if has_mem else "disabled"
        )
        self.mem_buttons["MR"].configure(
            fg=mem_active_fg if has_mem else mem_disabled_fg,
            state="normal" if has_mem else "disabled"
        )

    def copy_to_clipboard(self):
        """Copy current number to clipboard and show toast."""
        raw_val = self.engine.current_input
        self.clipboard_clear()
        self.clipboard_append(raw_val)
        self._show_toast("✓ Copied to clipboard")

    def paste_from_clipboard(self):
        """Paste number from clipboard."""
        try:
            val = self.clipboard_get().strip().replace(",", "")
            # Validate number
            float(val)
            self.engine.current_input = val
            self.engine.should_reset_input = True
            self._update_display()
            self._show_toast("✓ Pasted number")
        except Exception:
            self._show_toast("⚠ Clipboard does not contain a number")

    def _show_toast(self, text: str):
        """Display a subtle floating toast message that auto-dismisses."""
        if self.toast_job:
            self.after_cancel(self.toast_job)

        self.toast_label.configure(text=text)
        self.toast_label.place(relx=0.5, rely=0.22, anchor="center")

        def hide():
            self.toast_label.place_forget()

        self.toast_job = self.after(1600, hide)

    def toggle_history_panel(self):
        """Toggle side history drawer."""
        self.history_open = not self.history_open
        cur_h = self.winfo_height()

        if self.history_open:
            self.history_frame.pack(side="right", fill="both", expand=False)
            self.geometry(f"{self.main_width + self.history_width}x{cur_h}")
            self.btn_history.configure(text="✕ Close")
            self._refresh_history_ui()
        else:
            self.history_frame.pack_forget()
            self.geometry(f"{self.main_width}x{cur_h}")
            self.btn_history.configure(text="🕒 History")

    def _refresh_history_ui(self):
        """Render history entries."""
        for widget in self.hist_items_frame.winfo_children():
            widget.destroy()

        palette = THEMES[self.current_theme]
        history = self.engine.history

        if not history:
            lbl_empty = tk.Label(
                self.hist_items_frame,
                text="There's no history yet",
                font=("Segoe UI", 10, "italic"),
                bg=palette["history_bg"],
                fg=palette["history_empty"],
                pady=40
            )
            lbl_empty.pack(fill="x")
            return

        # Show newest on top
        for item in reversed(history):
            card = tk.Frame(
                self.hist_items_frame,
                bg=palette["history_card_bg"],
                cursor="hand2",
                padx=10,
                pady=6
            )
            card.pack(fill="x", pady=4)

            lbl_expr = tk.Label(
                card,
                text=item["expression"],
                font=("Segoe UI", 10),
                bg=palette["history_card_bg"],
                fg=palette["history_expr"],
                anchor="e"
            )
            lbl_expr.pack(fill="x")

            lbl_res = tk.Label(
                card,
                text=f"= {item['result']}",
                font=("Segoe UI", 14, "bold"),
                bg=palette["history_card_bg"],
                fg=palette["history_result"],
                anchor="e"
            )
            lbl_res.pack(fill="x")

            # Click to restore result into calculator
            result_val = item["result"]

            def load_val(_e, v=result_val):
                self.engine.current_input = v
                self.engine.should_reset_input = True
                self._update_display()
                self._show_toast(f"Loaded {v}")

            card.bind("<Button-1>", load_val)
            lbl_expr.bind("<Button-1>", load_val)
            lbl_res.bind("<Button-1>", load_val)

            # Hover highlight
            def on_enter(_e, f=card, le=lbl_expr, lr=lbl_res):
                f.configure(bg=palette["history_card_hover"])
                le.configure(bg=palette["history_card_hover"])
                lr.configure(bg=palette["history_card_hover"])

            def on_leave(_e, f=card, le=lbl_expr, lr=lbl_res):
                f.configure(bg=palette["history_card_bg"])
                le.configure(bg=palette["history_card_bg"])
                lr.configure(bg=palette["history_card_bg"])

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

    def _on_clear_history(self):
        self.engine.clear_history()
        self._refresh_history_ui()

    def toggle_theme(self):
        """Switch between dark and light themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._apply_theme()

    def _apply_theme(self):
        """Update colors of all UI widgets to match active theme."""
        palette = THEMES[self.current_theme]

        self.configure(bg=palette["bg"])
        self.root_container.configure(bg=palette["bg"])
        self.calc_frame.configure(bg=palette["bg"])
        self.header_frame.configure(bg=palette["header_bg"])
        self.header_btn_frame.configure(bg=palette["header_bg"])
        self.lbl_title.configure(bg=palette["header_bg"], fg=palette["display_primary"])

        self.btn_theme.configure(
            text="🌙" if self.current_theme == "light" else "☀️",
            bg=palette["header_bg"],
            fg=palette["display_primary"]
        )
        self.btn_history.configure(
            bg=palette["header_bg"],
            fg=palette["display_primary"]
        )

        self.display_frame.configure(bg=palette["display_bg"])
        self.lbl_expr.configure(bg=palette["display_bg"], fg=palette["display_expr"])
        self.lbl_display.configure(bg=palette["display_bg"], fg=palette["display_primary"])

        self.toast_label.configure(
            bg=palette["toast_bg"],
            fg=palette["toast_fg"]
        )

        self.memory_frame.configure(bg=palette["bg"])
        for m_btn in self.mem_buttons.values():
            m_btn.configure(bg=palette["btn_mem_bg"])

        self.keypad_frame.configure(bg=palette["bg"])

        # Update button colors
        for text, btn in self.all_buttons.items():
            if text in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "±"):
                btn.update_palette(
                    palette["btn_num_bg"],
                    palette["btn_num_hover"],
                    palette["btn_num_active"],
                    palette["btn_num_fg"]
                )
            elif text in ("%", "CE", "C", "⌫", "1/x", "x²", "√x"):
                btn.update_palette(
                    palette["btn_fn_bg"],
                    palette["btn_fn_hover"],
                    palette["btn_fn_active"],
                    palette["btn_fn_fg"]
                )
            elif text in ("÷", "×", "−", "+"):
                btn.update_palette(
                    palette["btn_op_bg"],
                    palette["btn_op_hover"],
                    palette["btn_op_active"],
                    palette["btn_op_fg"]
                )
            elif text == "=":
                btn.update_palette(
                    palette["btn_eq_bg"],
                    palette["btn_eq_hover"],
                    palette["btn_eq_active"],
                    palette["btn_eq_fg"]
                )

        # History panel
        self.history_frame.configure(
            bg=palette["history_bg"],
            highlightbackground=palette["history_border"]
        )
        self.hist_canvas.configure(bg=palette["history_bg"])
        self.hist_items_frame.configure(bg=palette["history_bg"])
        self.btn_clear_hist.configure(
            bg=palette["history_bg"],
            fg=palette["display_expr"]
        )

        self._update_display()
        self._refresh_history_ui()


def main():
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
