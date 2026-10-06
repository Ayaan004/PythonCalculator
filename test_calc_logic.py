import unittest
from decimal import Decimal
from calc_logic import CalculatorEngine


class TestCalculatorEngine(unittest.TestCase):
    def setUp(self):
        self.calc = CalculatorEngine()

    def test_digit_input(self):
        self.calc.input_digit("5")
        self.assertEqual(self.calc.get_display_text(), "5")
        self.calc.input_digit("8")
        self.assertEqual(self.calc.get_display_text(), "58")
        self.calc.input_digit("0")
        self.assertEqual(self.calc.get_display_text(), "580")

    def test_decimal_input(self):
        self.calc.input_digit("3")
        self.calc.input_decimal()
        self.calc.input_digit("1")
        self.calc.input_digit("4")
        self.assertEqual(self.calc.get_display_text(), "3.14")
        # Duplicate decimal should be ignored
        self.calc.input_decimal()
        self.assertEqual(self.calc.get_display_text(), "3.14")

    def test_thousand_separator_formatting(self):
        for digit in "1234567":
            self.calc.input_digit(digit)
        self.assertEqual(self.calc.get_display_text(), "1,234,567")
        self.calc.input_decimal()
        self.calc.input_digit("8")
        self.assertEqual(self.calc.get_display_text(), "1,234,567.8")

    def test_addition_and_precision(self):
        # 0.1 + 0.2 should equal 0.3 without floating point error
        self.calc.input_digit("0")
        self.calc.input_decimal()
        self.calc.input_digit("1")
        self.calc.input_operator("+")
        self.calc.input_digit("0")
        self.calc.input_decimal()
        self.calc.input_digit("2")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "0.3")

    def test_subtraction_and_negation(self):
        self.calc.input_digit("5")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.get_display_text(), "-5")
        self.calc.toggle_sign()
        self.assertEqual(self.calc.get_display_text(), "5")

    def test_multiplication_and_division(self):
        self.calc.input_digit("7")
        self.calc.input_operator("×")
        self.calc.input_digit("8")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "56")

        self.calc.input_operator("÷")
        self.calc.input_digit("2")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "28")

    def test_division_by_zero(self):
        self.calc.input_digit("9")
        self.calc.input_operator("÷")
        self.calc.input_digit("0")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "Cannot divide by zero")

    def test_chained_operations(self):
        # 10 + 5 × 2 = (10 + 5) * 2 = 30 in standard calculator mode
        self.calc.input_digit("1")
        self.calc.input_digit("0")
        self.calc.input_operator("+")
        self.calc.input_digit("5")
        self.calc.input_operator("×")
        self.assertEqual(self.calc.get_display_text(), "15")
        self.calc.input_digit("2")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "30")

    def test_repeated_equals(self):
        # 5 + 3 = 8, = 11, = 14
        self.calc.input_digit("5")
        self.calc.input_operator("+")
        self.calc.input_digit("3")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "8")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "11")
        self.calc.calculate_equals()
        self.assertEqual(self.calc.get_display_text(), "14")

    def test_backspace(self):
        self.calc.input_digit("1")
        self.calc.input_digit("2")
        self.calc.input_digit("3")
        self.calc.backspace()
        self.assertEqual(self.calc.get_display_text(), "12")
        self.calc.backspace()
        self.assertEqual(self.calc.get_display_text(), "1")
        self.calc.backspace()
        self.assertEqual(self.calc.get_display_text(), "0")

    def test_unary_operations(self):
        # Square
        self.calc.input_digit("5")
        self.calc.calculate_square()
        self.assertEqual(self.calc.get_display_text(), "25")

        # Square Root
        self.calc.calculate_square_root()
        self.assertEqual(self.calc.get_display_text(), "5")

        # Reciprocal of 4
        self.calc.clear_all()
        self.calc.input_digit("4")
        self.calc.calculate_reciprocal()
        self.assertEqual(self.calc.get_display_text(), "0.25")

        # Sqrt of negative
        self.calc.clear_all()
        self.calc.input_digit("9")
        self.calc.toggle_sign()
        self.calc.calculate_square_root()
        self.assertEqual(self.calc.get_display_text(), "Invalid input")

    def test_memory_functions(self):
        self.calc.input_digit("5")
        self.calc.input_digit("0")
        self.calc.memory_store()
        self.assertTrue(self.calc.has_memory)

        self.calc.clear_all()
        self.calc.input_digit("1")
        self.calc.input_digit("0")
        self.calc.memory_add()  # memory becomes 60

        self.calc.clear_all()
        self.calc.memory_recall()
        self.assertEqual(self.calc.get_display_text(), "60")

        self.calc.memory_clear()
        self.assertFalse(self.calc.has_memory)

    def test_history_logging(self):
        self.calc.input_digit("6")
        self.calc.input_operator("×")
        self.calc.input_digit("7")
        self.calc.calculate_equals()

        self.assertEqual(len(self.calc.history), 1)
        self.assertEqual(self.calc.history[0]["expression"], "6 × 7")
        self.assertEqual(self.calc.history[0]["result"], "42")


if __name__ == "__main__":
    unittest.main()
