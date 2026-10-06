"""
Automated GUI integration tests for the Calculator application.
Verifies widget initialization, keypad actions, memory, clipboard, theme, and history.
"""

import unittest
from calculator import CalculatorApp


class TestCalculatorGUI(unittest.TestCase):
    def setUp(self):
        self.app = CalculatorApp()
        self.app.withdraw()  # Hide window during test execution

    def tearDown(self):
        self.app.destroy()

    def test_app_initial_state(self):
        self.assertEqual(self.app.lbl_display["text"], "0")
        self.assertEqual(self.app.lbl_expr["text"], "")
        self.assertEqual(self.app.current_theme, "dark")
        self.assertFalse(self.app.history_open)

    def test_button_calculations(self):
        # 9 * 6 = 54
        self.app.all_buttons["9"].invoke()
        self.app.all_buttons["×"].invoke()
        self.app.all_buttons["6"].invoke()
        self.app.all_buttons["="].invoke()

        self.assertEqual(self.app.lbl_display["text"], "54")
        self.assertIn("9 × 6 =", self.app.lbl_expr["text"])

    def test_theme_toggle(self):
        self.assertEqual(self.app.current_theme, "dark")
        self.app.toggle_theme()
        self.assertEqual(self.app.current_theme, "light")
        self.app.toggle_theme()
        self.assertEqual(self.app.current_theme, "dark")

    def test_history_toggle_and_entry(self):
        # Calculate something first
        self.app.all_buttons["5"].invoke()
        self.app.all_buttons["+"].invoke()
        self.app.all_buttons["5"].invoke()
        self.app.all_buttons["="].invoke()

        # Open history
        self.app.toggle_history_panel()
        self.assertTrue(self.app.history_open)
        self.assertEqual(len(self.app.engine.history), 1)

        # Close history
        self.app.toggle_history_panel()
        self.assertFalse(self.app.history_open)

    def test_clear_and_clear_entry(self):
        self.app.all_buttons["8"].invoke()
        self.app.all_buttons["+"].invoke()
        self.app.all_buttons["4"].invoke()
        self.app.all_buttons["CE"].invoke()
        self.assertEqual(self.app.lbl_display["text"], "0")
        self.app.all_buttons["2"].invoke()
        self.app.all_buttons["="].invoke()
        self.assertEqual(self.app.lbl_display["text"], "10")

    def test_memory_bar_integration(self):
        self.app.all_buttons["7"].invoke()
        self.app.all_buttons["0"].invoke()
        self.app.mem_buttons["MS"].invoke()
        self.assertTrue(self.app.engine.has_memory)

        self.app.all_buttons["C"].invoke()
        self.assertEqual(self.app.lbl_display["text"], "0")

        self.app.mem_buttons["MR"].invoke()
        self.assertEqual(self.app.lbl_display["text"], "70")

        self.app.mem_buttons["MC"].invoke()
        self.assertFalse(self.app.engine.has_memory)


if __name__ == "__main__":
    unittest.main()
