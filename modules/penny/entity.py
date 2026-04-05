"""
Expense Entity Module

This module defines the Expense class which represents a single expense record
with validation logic for all fields.
"""

# Libraries
from datetime import datetime
from pathlib import Path
import sys

# Adding project root to the python paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.id_generator import generate_uuid
from modules.penny.exceptions import *


class Expense:
    """
    Represents a single expense entry.

    Attributes:
        id (str): Unique identifier (UUID4) for the expense
        amount (float): Expense amount (must be positive)
        category (str): Expense category (lowercase)
        date (str): Date in DD-MM-YYYY format
        note (str): Optional note/description

    Raises:
        InvalidAmountError: If amount is not positive
        EmptyFieldError: If required fields are empty
        InvalidDateError: If date format is invalid

    Example:
        >>> expense = Expense(50.0, "food", "20-02-2026", "lunch")
        >>> print(expense.amount)
        50.0
    """

    def __init__(self, amount, category, date, note="", id=None) -> None:
        """
        Initialize a new Expense.

        Args:
            amount: Expense amount (converted to float)
            category: Category name (converted to lowercase)
            date: Date string in DD-MM-YYYY format
            note: Optional description (default: "")
            id: Optional UUID (generates new one if None)
        """

        self.id = str(id) if id else generate_uuid()
        self.amount = float(amount)
        self.category = category.lower()
        self.date = date
        self.note = note

        self.validate_fields()

    def to_dict(self) -> dict:
        """
        Convert expense to dictionary.

        Returns:
            dict: Expense data as dictionary with keys: id, amount, category, date, note
        """

        expense_dict = {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "note": self.note,
        }

        return expense_dict

    def to_list(self) -> list:
        """
        Convert expense to list for CSV storage.

        Returns:
            list: Expense data as [id, amount, category, date, note]
        """

        expense_row = [self.id, self.amount, self.category, self.date, self.note]

        return expense_row

    @classmethod
    def from_dict(cls, expense_dict: dict):
        """
        Create Expense object from dictionary.

        Args:
            expense_dict (dict): Dictionary with keys: id, amount, category, date, note

        Returns:
            Expense: New Expense instance
        """

        return cls(
            amount=expense_dict["amount"],
            category=expense_dict["category"],
            date=expense_dict["date"],
            note=expense_dict["note"],
            id=expense_dict["id"],
        )

    def validate_fields(self):
        """
        Validate all expense fields.

        Raises:
            EmptyFieldError: If ID or category is empty
            InvalidAmountError: If amount is not positive
            InvalidDateError: If date format is invalid (not DD-MM-YYYY)
        """

        if not self.id:
            raise EmptyFieldError("Empty Field")

        if self.amount <= 0:
            raise InvalidAmountError("Amount should be greater than 0")

        if not self.category.strip():
            raise EmptyFieldError("Category cannot be empty")

        try:
            datetime.strptime(self.date, "%d-%m-%Y")
        except ValueError:
            raise InvalidDateError(
                f"Date must be in DD-MM-YYYY format, got: {self.date}"
            )
