"""
Database Module

Handles all CSV file operations and data persistence for Penny Tracker.
Provides low-level CSV operations and high-level expense database management.
"""

# Libraries
from pathlib import Path
import sys

# Adding project root to the python paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.file_handler import CSVFile
from modules.penny.entity import Expense
from modules.penny.exceptions import *

# Directories for file operations
PENNY_DIR = Path(__file__).parent
DATA_DIR = PENNY_DIR / "data"

EXPENSE_FILE_PATH = DATA_DIR / "expenses.csv"

# Expense DB


class ExpenseDB:
    """
    High-level expense database manager.

    Provides CRUD operations for expenses stored in CSV format.

    Attributes:
        csv_handler (CSVFile): CSV file handler instance
    """

    def __init__(self, EXPENSE_FILE=EXPENSE_FILE_PATH) -> None:
        """Initialize expense database with expenses.csv file."""

        self.csv_handler = CSVFile(EXPENSE_FILE)

    def get_all_expenses(self, skip_header=True) -> list[Expense]:
        """
        Retrieve all expenses from database.

        Args:
            skip_header (bool): Whether to skip the header row (default: True)

        Returns:
            list[Expense]: List of Expense objects
        """

        rows = self.csv_handler.read_csv()
        if skip_header:
            rows = rows[1:]

        expenses = [Expense.from_dict(r) for r in rows if r and len(r) == 5]
        return expenses

    def add_expense(self, expense_row: list) -> bool:
        """
        Add new expense to database.

        Args:
            expense_row (list): Expense data as list [id, amount, category, date, note]

        Returns:
            bool: True if successful
        """

        self.csv_handler.append_csv(expense_row)
        return True

    def delete_expense(self, expense_id: str) -> bool:
        """
        Delete expense by UUID.

        Args:
            expense_id (str): UUID of expense to delete

        Returns:
            bool: True if deleted

        Raises:
            ExpenseNotFoundError: if expense object not found
        """

        rows = self.get_all_expenses(skip_header=False)

        filtered = [r.to_dict() for r in rows if r.id != expense_id]

        if len(rows) == len(filtered):
            raise ExpenseNotFoundError("Expense doesn't exist: not found")

        self.csv_handler.write_csv(filtered)
        return True

    def update_expense(self, expense: Expense) -> bool:
        """
        Update existing expense by UUID.

        Args:
            expense (Expense): Updated expense object

        Returns:
            bool: True if updated

        Raises:
            ExpenseNotFoundError: if expense object not found
        """

        rows = self.csv_handler.read_csv()
        header = rows[0]
        data_rows = rows[1:]

        updated = False

        for i, r in enumerate(data_rows):
            if r["id"] == expense.id:
                data_rows[i] = expense.to_dict()
                updated = True
                break

        if not updated:
            raise ExpenseNotFoundError("Expense doesn't exist: not found")

        self.csv_handler.write_csv([header] + data_rows)
        return True


if __name__ == "__main__":
    e = ExpenseDB()

    # print(e.get_all_expenses())
    exp1 = [
        "sklw-3njksdj-3sdhik-480sl",
        100,
        "food",
        "21-02-2026",
        "",
    ]
    # print(e.add_expense(exp1))
