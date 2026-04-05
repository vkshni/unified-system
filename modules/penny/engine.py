"""
Expense Tracker Module

This module contains the core business logic for the Penny Tracker application.
It orchestrates all expense operations including creation, retrieval, filtering,
editing, deletion, and summary generation.

The ExpenseTracker class acts as the main controller, coordinating between
the database layer (db.py) and the entity layer (entity.py) while handling
all business rules and logging.

Classes:
    ExpenseTracker: Main controller for expense management operations

Example:
    >>> tracker = ExpenseTracker()
    >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
    >>> expenses = tracker.view_all()
    >>> summary = tracker.monthly_summary(2, 2026)
"""

# Libraries
from datetime import datetime
from pathlib import Path
import sys

# Adding project root to the python paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from modules.penny.entity import Expense
from modules.penny.storage import ExpenseDB
from modules.penny.exceptions import *

# Directories for file operations
PENNY_DIR = Path(__file__).parent
DATA_DIR = PENNY_DIR / "data"

EXPENSE_FILE_PATH = DATA_DIR / "expenses.csv"


# Expense Tracker
class ExpenseTracker:
    """
    Main controller class for expense tracking operations.

    This class provides a high-level interface for managing expenses including
    CRUD operations (Create, Read, Update, Delete), filtering, and reporting.
    It handles business logic, validation, and logging for all operations.

    Attributes:
        expensedb (ExpenseDB): Database interface for expense persistence
        logger (Logger): Logger instance for tracking operations

    Example:
        >>> tracker = ExpenseTracker()
        >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
        True
        >>> expenses = tracker.view_all()
        >>> len(expenses)
        1
    """

    def __init__(self, EXPENSE_FILE=EXPENSE_FILE_PATH):
        """
        Initialize the ExpenseTracker with database connection and logger.

        Sets up the expense database interface and configures logging for
        tracking all operations performed by the tracker.
        """
        self.expensedb = ExpenseDB(EXPENSE_FILE)

    def add_expense(
        self, amount: int, category: str, date: str, note: str = ""
    ) -> bool:
        """
        Add a new expense to the tracker.

        Creates a new expense with the provided details, validates all fields,
        saves it to the database, and logs the operation.

        Args:
            amount (int): The expense amount (will be converted to float, must be positive)
            category (str): Expense category (will be converted to lowercase)
            date (str): Date in DD-MM-YYYY format (e.g., "20-02-2026")
            note (str, optional): Optional description or note about the expense. Defaults to "".

        Returns:
            bool: True if the expense was successfully added

        Raises:
            InvalidAmountError: If amount is not positive
            EmptyFieldError: If required fields (category, date) are empty
            InvalidDateError: If date format is not DD-MM-YYYY

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch at cafe")
            True
            >>> tracker.add_expense(120.50, "transport", "19-02-2026")
            True
        """
        expense_obj = Expense(amount, category, date, note)

        expense_row = expense_obj.to_list()
        self.expensedb.add_expense(expense_row)

        return True

    def view_all(self) -> list[list]:
        """
        Retrieve all expenses with display IDs for user reference.

        Fetches all expenses from the database and adds sequential display IDs
        (1, 2, 3, ...) for easy reference in CLI operations. Returns None if
        no expenses exist.

        Returns:
            list or None: List of expenses where each expense is represented as:
                [display_id, uuid, amount, category, date, note]
                Returns None if no expenses are found.

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> expenses = tracker.view_all()
            >>> expenses[0]
            [1, 'uuid-string', 50.0, 'food', '20-02-2026', 'lunch']

        Note:
            The display_id (first element) is a 1-indexed sequential number
            for user-friendly reference, while the uuid (second element) is
            used internally for database operations.
        """
        expenses = self.expensedb.get_all_expenses()
        if not expenses:
            return []

        numbered_expenses = [[idx + 1] + e.to_list() for idx, e in enumerate(expenses)]

        return numbered_expenses

    def filter_by_category(self, category: str) -> list[list]:
        """
        Filter expenses by category and return with display IDs.

        Retrieves all expenses matching the specified category (case-insensitive).
        If no matches are found, displays available categories to help the user.
        Each matching expense is assigned a sequential display ID starting from 1.

        Args:
            category (str): The category to filter by (case-insensitive)

        Returns:
            list: List of matching expenses, each formatted as:
                [display_id, uuid, amount, category, date, note]
                Returns empty list if no matches found.

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> tracker.add_expense(120, "transport", "19-02-2026", "uber")
            >>> food_expenses = tracker.filter_by_category("food")
            >>> len(food_expenses)
            1
            >>> food_expenses[0][3]  # category
            'food'

        Note:
            If no expenses match the category, the method prints available
            categories to help the user and returns an empty list.
        """
        expenses = self.expensedb.get_all_expenses()
        total = 1
        expenses_by_category = []
        for e in expenses:
            if e.category == category.lower():
                expenses_by_category.append([total] + e.to_list())
                total += 1

        if not expenses_by_category:
            # Show available categories
            all_categories = set(e.category for e in expenses)
            if all_categories:
                available = ", ".join(sorted(all_categories))
                return f"💡 Available categories: {available}"

            return []  # Return empty list, not None

        return expenses_by_category

    def parse_date(self, date_str: str) -> datetime:
        """
        Parse date string into datetime object with validation.

        Converts a date string in DD-MM-YYYY format to a datetime object.
        Logs errors and raises InvalidDateError if the format is incorrect.

        Args:
            date_str (str): Date string in DD-MM-YYYY format (e.g., "20-02-2026")

        Returns:
            datetime: Parsed datetime object

        Raises:
            InvalidDateError: If date format is not DD-MM-YYYY or date is invalid

        Example:
            >>> tracker = ExpenseTracker()
            >>> date_obj = tracker.parse_date("20-02-2026")
            >>> date_obj.day
            20
            >>> date_obj.month
            2
            >>> date_obj.year
            2026

        Note:
            This method validates both format and logical validity (e.g.,
            "32-01-2026" would be rejected as an invalid date).
        """
        try:
            return datetime.strptime(date_str, "%d-%m-%Y")
        except:
            raise InvalidDateError(
                f"Invalid date format: '{date_str}'\n"
                f"Expected format: DD-MM-YYYY (e.g., 15-02-2026)"
            )

    def filter_by_date_range(self, start_date: str, end_date: str) -> list[list]:
        """
        Filter expenses within a specified date range (inclusive).

        Retrieves all expenses that fall between the start and end dates
        (both dates inclusive). Each matching expense is assigned a sequential
        display ID starting from 1.

        Args:
            start_date (str): Start date in DD-MM-YYYY format (inclusive)
            end_date (str): End date in DD-MM-YYYY format (inclusive)

        Returns:
            list or None: List of matching expenses, each formatted as:
                [display_id, uuid, amount, category, date, note]
                Returns None if no expenses found in range.

        Raises:
            InvalidDateError: If either date has invalid format

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> tracker.add_expense(120, "transport", "15-02-2026", "uber")
            >>> filtered = tracker.filter_by_date_range("15-02-2026", "20-02-2026")
            >>> len(filtered)
            2

        Note:
            The date range is inclusive on both ends. If start_date equals
            end_date, only expenses from that specific date are returned.
        """
        start_date = self.parse_date(start_date)
        end_date = self.parse_date(end_date)

        expenses = self.expensedb.get_all_expenses()
        expenses_by_date_range = []
        total = 1

        for e in expenses:
            parsed_date = self.parse_date(e.date)
            if start_date <= parsed_date <= end_date:
                expenses_by_date_range.append([total] + e.to_list())
                total += 1

        if not expenses_by_date_range:
            return []

        return expenses_by_date_range

    @staticmethod
    def matches_month(date_str, month: int, year: int) -> bool:
        """
        Check if a date string matches a specific month and year.

        Static utility method to determine if a given date falls within
        the specified month and year.

        Args:
            date_str (str): Date string in DD-MM-YYYY format
            month (int): Month number (1-12)
            year (int): Four-digit year (e.g., 2026)

        Returns:
            bool: True if the date is in the specified month/year, False otherwise

        Example:
            >>> ExpenseTracker.matches_month("20-02-2026", 2, 2026)
            True
            >>> ExpenseTracker.matches_month("20-02-2026", 3, 2026)
            False
            >>> ExpenseTracker.matches_month("20-02-2026", 2, 2025)
            False

        Note:
            This is a static method and can be called without creating
            an ExpenseTracker instance.
        """
        date = datetime.strptime(date_str, "%d-%m-%Y")
        return date.month == month and date.year == year

    def monthly_summary(self, month: int, year: int) -> dict:
        """
        Generate a summary of expenses for a specific month and year.

        Calculates the total amount spent and provides a breakdown by category
        for all expenses in the specified month. Validates that month and year
        are within acceptable ranges.

        Args:
            month (int): Month number (1-12)
            year (int): Four-digit year (2000-2100)

        Returns:
            dict: Dictionary containing:
                - 'total' (float): Total amount spent in the month
                - 'by_category' (dict): Category-wise breakdown {category: amount}

        Raises:
            InvalidDateError: If month is not in range 1-12 or year is not in range 2000-2100

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> tracker.add_expense(30, "food", "15-02-2026", "breakfast")
            >>> tracker.add_expense(120, "transport", "18-02-2026", "uber")
            >>> summary = tracker.monthly_summary(2, 2026)
            >>> summary['total']
            200.0
            >>> summary['by_category']['food']
            80.0
            >>> summary['by_category']['transport']
            120.0

        Note:
            If no expenses exist for the specified month, returns total of 0
            and an empty by_category dictionary.
        """
        if not (1 <= month <= 12):
            raise InvalidDateError(f"Month must be between 1-12, got: {month}")

        if not (2000 <= year <= 2100):
            raise InvalidDateError(f"Year seems invalid: {year}")

        expenses = self.expensedb.get_all_expenses()

        monthly_expenses = [
            e for e in expenses if ExpenseTracker.matches_month(e.date, month, year)
        ]

        total = sum(e.amount for e in monthly_expenses)

        by_category = {}

        for e in monthly_expenses:
            by_category[e.category] = by_category.get(e.category, 0) + e.amount

        return {"total": total, "by_category": by_category}

    def get_expense_by_display_id(self, display_id: int) -> Expense:
        """
        Retrieve an expense object using its display ID.

        Fetches the expense corresponding to the given display ID (the
        sequential number shown when viewing expenses). Display IDs are
        1-indexed and correspond to the position in the expense list.

        Args:
            display_id (int): The display ID (1-indexed position) of the expense

        Returns:
            Expense: The Expense object at the specified position

        Raises:
            ExpenseNotFoundError: If display_id is out of range (less than 1
                or greater than total number of expenses)

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> expense = tracker.get_expense_by_display_id(1)
            >>> expense.amount
            50.0
            >>> expense.category
            'food'

        Note:
            Display IDs are temporary and based on the current order of expenses.
            They may change after deletions or when filtering is applied.
        """
        expenses = self.expensedb.get_all_expenses()

        if not (1 <= display_id <= len(expenses)):
            raise ExpenseNotFoundError(f"Display ID {display_id} not found")

        expense = expenses[display_id - 1]

        return expense

    def delete_expense(self, display_id: int) -> bool:
        """
        Delete an expense using its display ID.

        Removes the expense at the specified display ID from the database.
        The operation is permanent and the expense cannot be recovered.

        Args:
            display_id (int): The display ID (1-indexed position) of the expense to delete

        Returns:
            bool: True if the expense was successfully deleted

        Raises:
            ExpenseNotFoundError: If no expense exists at the given display_id

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> tracker.add_expense(120, "transport", "19-02-2026", "uber")
            >>> tracker.delete_expense(1)  # Deletes the first expense
            True
            >>> expenses = tracker.view_all()
            >>> len(expenses)
            1

        Warning:
            This operation is destructive and cannot be undone. The CLI
            interface typically prompts for confirmation before deletion.

        Note:
            After deletion, display IDs are recalculated, so the display_id
            of remaining expenses may change.
        """
        expense = self.get_expense_by_display_id(display_id)

        if not expense:
            raise ExpenseNotFoundError(f"Display ID {display_id} not found")

        self.expensedb.delete_expense(expense.id)

        return True

    def edit_expense(
        self, display_id, amount=None, category=None, date=None, note=None
    ) -> bool:
        """
        Edit an existing expense by its display ID.

        Updates one or more fields of an expense. Only the fields provided
        (not None) are updated. The updated expense is validated before
        being saved to ensure data integrity.

        Args:
            display_id (int): The display ID (1-indexed position) of the expense to edit
            amount (int or float, optional): New amount value. If None, amount is not changed.
            category (str, optional): New category. If None, category is not changed.
            date (str, optional): New date in DD-MM-YYYY format. If None, date is not changed.
            note (str, optional): New note/description. If None, note is not changed.

        Returns:
            bool: True if the expense was successfully updated

        Raises:
            ExpenseNotFoundError: If no expense exists at the given display_id
            InvalidAmountError: If the new amount is not positive
            EmptyFieldError: If the new category is empty
            InvalidDateError: If the new date format is invalid

        Example:
            >>> tracker = ExpenseTracker()
            >>> tracker.add_expense(50, "food", "20-02-2026", "lunch")
            >>> tracker.edit_expense(1, amount=75, note="expensive lunch")
            True
            >>> expense = tracker.get_expense_by_display_id(1)
            >>> expense.amount
            75.0
            >>> expense.note
            'expensive lunch'
            >>> expense.category  # Unchanged
            'food'

        Note:
            All field validations are performed after updating. If validation
            fails, the expense is not saved and an exception is raised.

            Category values are automatically converted to lowercase.
            Amount values are automatically converted to float.
        """
        expense = self.get_expense_by_display_id(display_id)

        if not expense:
            raise ExpenseNotFoundError(f"Display ID {display_id} not found")

        if amount is not None:
            expense.amount = float(amount)
        if category is not None:
            expense.category = category.lower()
        if date is not None:
            expense.date = date
        if note is not None:
            expense.note = note

        expense.validate_fields()

        self.expensedb.update_expense(expense)

        return True


if __name__ == "__main__":

    tracker = ExpenseTracker()

    # print(tracker.add_expense(100, "food", "26-03-2026"))
    expenses = tracker.view_all()
    for e in expenses:
        print(e)
    # print(tracker.filter_by_category("food"))
    # print(tracker.filter_by_date_range("01-02-2026", "28-02-2026"))
    # print(tracker.monthly_summary(2, 2026))
    # print(tracker.get_expense_by_display_id(1))
    # print(tracker.delete_expense(11))
    # print(tracker.edit_expense(11, amount=200))
