"""
Core calculator logic engine with high precision, state management,
unary operations, memory, and calculation history.
"""

from decimal import Decimal, InvalidOperation, getcontext
import math
from typing import Optional, List, Dict, Any

# Set precision to 16 significant digits to avoid floating point artifacts
getcontext().prec = 16


class CalculatorEngine:
    def __init__(self):
        self.reset()
        self.memory = Decimal(0)
        self.has_memory = False
        self.history: List[Dict[str, str]] = []

    def reset(self):
        """Reset calculator state (Clear All / C)."""
        self.current_input: str = "0"
        self.stored_operand: Optional[Decimal] = None
        self.pending_operator: Optional[str] = None
        self.expression_str: str = ""
        self.should_reset_input: bool = False
        self.last_operator: Optional[str] = None
        self.last_operand: Optional[Decimal] = None
        self.error_state: Optional[str] = None

    def clear_entry(self):
        """Clear current entry only (CE)."""
        if self.error_state:
            self.reset()
        else:
            self.current_input = "0"
            self.should_reset_input = False

    def clear_all(self):
        """Clear all state (C)."""
        self.reset()

    def get_display_text(self) -> str:
        """Returns the text that should be shown on the main display."""
        if self.error_state:
            return self.error_state
        return self._format_number_for_display(self.current_input)

    def get_expression_text(self) -> str:
        """Returns the formula / expression history text for the secondary display."""
        return self.expression_str

    def _format_number_for_display(self, num_str: str) -> str:
        """Format number with thousand separators while preserving active typing like '.' or '0.00'."""
        if not num_str or num_str in ("Error", "Cannot divide by zero", "Invalid input"):
            return num_str

        # If it's in scientific notation, leave as-is
        if "e" in num_str.lower():
            return num_str

        # Handle negative sign
        is_negative = num_str.startswith("-")
        clean_str = num_str[1:] if is_negative else num_str

        if "." in clean_str:
            integer_part, decimal_part = clean_str.split(".", 1)
            # Add commas to integer part
            if integer_part:
                formatted_int = f"{int(integer_part):,}"
            else:
                formatted_int = "0"
            res = f"{formatted_int}.{decimal_part}"
        else:
            try:
                res = f"{int(clean_str):,}"
            except ValueError:
                res = clean_str

        return f"-{res}" if is_negative else res

    def _strip_trailing_zeros(self, val: Decimal) -> str:
        """Format Decimal to clean string without unnecessary trailing zeros."""
        val_str = f"{val:f}"
        if "." in val_str:
            val_str = val_str.rstrip("0").rstrip(".")
        if val_str == "-0" or val_str == "":
            val_str = "0"
        return val_str

    def _to_decimal(self, s: str) -> Decimal:
        """Parse clean string to Decimal."""
        try:
            return Decimal(s.replace(",", ""))
        except (InvalidOperation, ValueError):
            return Decimal(0)

    def input_digit(self, digit: str):
        """Append digit (0-9) to current display."""
        if self.error_state:
            self.reset()

        if self.should_reset_input:
            self.current_input = digit
            self.should_reset_input = False
            return

        # Limit maximum display characters
        raw_digits = self.current_input.replace(".", "").replace("-", "")
        if len(raw_digits) >= 15:
            return

        if self.current_input == "0":
            self.current_input = digit
        else:
            self.current_input += digit

    def input_decimal(self):
        """Input decimal separator '.'."""
        if self.error_state:
            self.reset()

        if self.should_reset_input:
            self.current_input = "0."
            self.should_reset_input = False
            return

        if "." not in self.current_input:
            self.current_input += "."

    def toggle_sign(self):
        """Negate current value (+/-)."""
        if self.error_state:
            return

        if self.current_input == "0" or self.current_input == "0.":
            return

        if self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input

    def backspace(self):
        """Delete last character (⌫)."""
        if self.error_state:
            self.reset()
            return

        if self.should_reset_input:
            return

        if len(self.current_input) == 1 or (len(self.current_input) == 2 and self.current_input.startswith("-")):
            self.current_input = "0"
        else:
            self.current_input = self.current_input[:-1]
            if self.current_input == "-":
                self.current_input = "0"

    def _execute_op(self, op: str, a: Decimal, b: Decimal) -> Decimal:
        """Perform binary arithmetic operation."""
        if op == "+":
            return a + b
        elif op in ("-", "−"):
            return a - b
        elif op in ("*", "×"):
            return a * b
        elif op in ("/", "÷"):
            if b == 0:
                raise ZeroDivisionError()
            return a / b
        raise ValueError(f"Unknown operator: {op}")

    def input_operator(self, op: str):
        """Handles operator input: +, -, ×, ÷."""
        if self.error_state:
            return

        current_val = self._to_decimal(self.current_input)

        # Standard symbol mapping
        symbol_map = {"+": "+", "-": "−", "*": "×", "/": "÷", "−": "−", "×": "×", "÷": "÷"}
        disp_op = symbol_map.get(op, op)

        if self.pending_operator is not None:
            if self.should_reset_input:
                # User is changing the operator before entering second number
                self.pending_operator = disp_op
                self.expression_str = f"{self._strip_trailing_zeros(self.stored_operand)} {disp_op}"
                return

            # Intermediate evaluation: e.g. 5 + 3 + ... => computes 8 then queues +
            try:
                res = self._execute_op(self.pending_operator, self.stored_operand, current_val)
                self.stored_operand = res
                res_str = self._strip_trailing_zeros(res)
                self.current_input = res_str
                self.expression_str = f"{res_str} {disp_op}"
                self.pending_operator = disp_op
                self.should_reset_input = True
            except ZeroDivisionError:
                self.error_state = "Cannot divide by zero"
                self.expression_str = ""
            except Exception:
                self.error_state = "Error"
                self.expression_str = ""
        else:
            self.stored_operand = current_val
            self.pending_operator = disp_op
            self.expression_str = f"{self._strip_trailing_zeros(current_val)} {disp_op}"
            self.should_reset_input = True

        self.last_operator = None
        self.last_operand = None

    def calculate_equals(self):
        """Evaluate calculation (=)."""
        if self.error_state:
            return

        current_val = self._to_decimal(self.current_input)

        if self.pending_operator is not None:
            op = self.pending_operator
            first = self.stored_operand
            second = current_val

            try:
                res = self._execute_op(op, first, second)
                first_str = self._strip_trailing_zeros(first)
                second_str = self._strip_trailing_zeros(second)
                res_str = self._strip_trailing_zeros(res)

                expr = f"{first_str} {op} {second_str} ="
                self.expression_str = expr
                self.current_input = res_str
                self.should_reset_input = True

                # Save for repeated equals
                self.last_operator = op
                self.last_operand = second
                self.stored_operand = res
                self.pending_operator = None

                # Add to history
                self.history.append({"expression": f"{first_str} {op} {second_str}", "result": res_str})
            except ZeroDivisionError:
                self.error_state = "Cannot divide by zero"
                self.expression_str = ""
            except Exception:
                self.error_state = "Error"
                self.expression_str = ""
        elif self.last_operator is not None and self.last_operand is not None:
            # Repeated equals: 5 + 3 = 8, = 11, = 14
            first = current_val
            second = self.last_operand
            op = self.last_operator
            try:
                res = self._execute_op(op, first, second)
                first_str = self._strip_trailing_zeros(first)
                second_str = self._strip_trailing_zeros(second)
                res_str = self._strip_trailing_zeros(res)

                expr = f"{first_str} {op} {second_str} ="
                self.expression_str = expr
                self.current_input = res_str
                self.should_reset_input = True

                self.history.append({"expression": f"{first_str} {op} {second_str}", "result": res_str})
            except ZeroDivisionError:
                self.error_state = "Cannot divide by zero"
                self.expression_str = ""
            except Exception:
                self.error_state = "Error"
                self.expression_str = ""

    def calculate_percentage(self):
        """Percentage calculation (%) - contextual or standalone."""
        if self.error_state:
            return

        current_val = self._to_decimal(self.current_input)

        if self.stored_operand is not None and self.pending_operator in ("+", "−", "-", "×", "*", "÷", "/"):
            # Contextual percent: e.g. 200 + 10% => 10% of 200 is 20
            pct_val = (self.stored_operand * current_val) / Decimal(100)
        else:
            pct_val = current_val / Decimal(100)

        res_str = self._strip_trailing_zeros(pct_val)
        self.current_input = res_str
        self.should_reset_input = True

    def calculate_square_root(self):
        """Square root (√x)."""
        if self.error_state:
            return

        current_val = self._to_decimal(self.current_input)
        if current_val < 0:
            self.error_state = "Invalid input"
            self.expression_str = f"√({self._strip_trailing_zeros(current_val)})"
            return

        try:
            res = current_val.sqrt()
            cur_str = self._strip_trailing_zeros(current_val)
            res_str = self._strip_trailing_zeros(res)
            self.expression_str = f"√({cur_str})"
            self.current_input = res_str
            self.should_reset_input = True
            self.history.append({"expression": f"√({cur_str})", "result": res_str})
        except Exception:
            self.error_state = "Invalid input"

    def calculate_square(self):
        """Square (x²)."""
        if self.error_state:
            return

        current_val = self._to_decimal(self.current_input)
        try:
            res = current_val * current_val
            cur_str = self._strip_trailing_zeros(current_val)
            res_str = self._strip_trailing_zeros(res)
            self.expression_str = f"sqr({cur_str})"
            self.current_input = res_str
            self.should_reset_input = True
            self.history.append({"expression": f"sqr({cur_str})", "result": res_str})
        except Exception:
            self.error_state = "Overflow"

    def calculate_reciprocal(self):
        """Reciprocal (1/x)."""
        if self.error_state:
            return

        current_val = self._to_decimal(self.current_input)
        if current_val == 0:
            self.error_state = "Cannot divide by zero"
            self.expression_str = "1/(0)"
            return

        try:
            res = Decimal(1) / current_val
            cur_str = self._strip_trailing_zeros(current_val)
            res_str = self._strip_trailing_zeros(res)
            self.expression_str = f"1/({cur_str})"
            self.current_input = res_str
            self.should_reset_input = True
            self.history.append({"expression": f"1/({cur_str})", "result": res_str})
        except Exception:
            self.error_state = "Error"

    # Memory Operations
    def memory_clear(self):
        """MC - Clear memory."""
        self.memory = Decimal(0)
        self.has_memory = False

    def memory_recall(self):
        """MR - Recall memory value into display."""
        if not self.has_memory:
            return
        self.current_input = self._strip_trailing_zeros(self.memory)
        self.should_reset_input = True

    def memory_add(self):
        """M+ - Add current display value to memory."""
        if self.error_state:
            return
        val = self._to_decimal(self.current_input)
        self.memory += val
        self.has_memory = True
        self.should_reset_input = True

    def memory_subtract(self):
        """M- - Subtract current display value from memory."""
        if self.error_state:
            return
        val = self._to_decimal(self.current_input)
        self.memory -= val
        self.has_memory = True
        self.should_reset_input = True

    def memory_store(self):
        """MS - Store current display value in memory."""
        if self.error_state:
            return
        val = self._to_decimal(self.current_input)
        self.memory = val
        self.has_memory = True
        self.should_reset_input = True

    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()
