"""
Penny Tracker - Simple Expense Management CLI
"""

# Libraries
from datetime import datetime
from pathlib import Path
import argparse
import sys

# Adding project root to the python paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from modules.penny.engine import ExpenseTracker
from modules.penny.exceptions import *

# Directories for file operations
PENNY_DIR = Path(__file__).parent
DATA_DIR = PENNY_DIR / "data"

EXPENSE_FILE_PATH = DATA_DIR / "expenses.csv"


# COMMANDS


# display command
def display_expenses(expenses):
    """Display expenses in a formatted table"""
    if not expenses:
        print("No expenses found.")
        return

    print(f"\n{'#':<4} {'Amount':<10} {'Category':<15} {'Date':<12} {'Note'}")
    print("-" * 65)

    for e in expenses:
        display_id = e[0]
        amount = e[2]
        category = e[3]
        date = e[4]
        note = e[5] if len(e) > 5 else ""

        print(f"{display_id:<4} {amount:<10.2f} {category:<15} {date:<12} {note}")

    print()


def display_summary(summary):
    """Display monthly summary"""
    print(f"\nTotal Spent: ₹{summary['total']:.2f}")
    print("\nCategory Breakdown:")
    print("-" * 40)

    if not summary["by_category"]:
        print("No expenses in this month.")
        return

    for category, amount in summary["by_category"].items():
        print(f"{category:<20} ₹{amount:.2f}")

    print()


def cmd_add(args, tracker):
    """Handle add command"""
    try:
        tracker.add_expense(args.amount, args.category, args.date, args.note)
        print(f"✓ Expense added successfully: ₹{args.amount} - {args.category}")
    except InvalidAmountError as e:
        print(f"✗ Invalid Amount: {e}")
        sys.exit(1)
    except EmptyFieldError as e:
        print(f"✗ Empty Field: {e}")
        sys.exit(1)
    except InvalidDateError as e:
        print(f"✗ Invalid Date: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        sys.exit(1)


def cmd_view(args, tracker):
    """Handle view command"""
    expenses = tracker.view_all()
    display_expenses(expenses)


def cmd_filter(args, tracker):
    """Handle filter command"""
    try:
        if args.category:
            expenses = tracker.filter_by_category(args.category)
            print(f"\nExpenses in category: {args.category}")
            display_expenses(expenses)

        elif args.date_from and args.date_to:

            expenses = tracker.filter_by_date_range(args.date_from, args.date_to)
            print(f"\nExpenses from {args.date_from} to {args.date_to}")
            display_expenses(expenses)

        else:
            print("✗ Error: Please provide either --category or both --from and --to")
            sys.exit(1)

    except InvalidDateError as e:
        print(f"✗ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        sys.exit(1)


def cmd_summary(args, tracker):
    """Handle summary command"""
    try:
        summary = tracker.monthly_summary(args.month, args.year)
        print(f"\nMonthly Summary for {args.month:02d}/{args.year}")
        display_summary(summary)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def cmd_edit(args, tracker):
    """Handle edit command"""
    try:
        # Build kwargs for only provided arguments
        kwargs = {}
        if args.amount is not None:
            kwargs["amount"] = args.amount
        if args.category is not None:
            kwargs["category"] = args.category
        if args.date is not None:
            kwargs["date"] = args.date
        if args.note is not None:
            kwargs["note"] = args.note

        if not kwargs:
            print("✗ Error: Please provide at least one field to update")
            sys.exit(1)

        result = tracker.edit_expense(args.display_id, **kwargs)

        if result:
            print(f"✓ Expense #{args.display_id} updated successfully")
        else:
            print(f"✗ Error: Expense #{args.display_id} not found")
            sys.exit(1)

    except ExpenseNotFoundError as e:
        print(f"✗ {e}")
        sys.exit(1)
    except (InvalidAmountError, EmptyFieldError, InvalidDateError) as e:
        print(f"✗ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        sys.exit(1)


def cmd_delete(args, tracker):
    """Handle delete command"""
    try:
        # Get the expense first to show what will be deleted
        expense = tracker.get_expense_by_display_id(args.display_id)

        # Show what will be deleted
        print(f"\n⚠️  About to delete:")
        print(f"  Amount: ₹{expense.amount:.2f}")
        print(f"  Category: {expense.category}")
        print(f"  Date: {expense.date}")
        print(f"  Note: {expense.note}")

        # Ask for confirmation
        confirm = input("\nAre you sure? (y/N): ").strip().lower()

        if confirm != "y":
            print("❌ Deletion cancelled")
            return

        tracker.delete_expense(args.display_id)
        print(f"✓ Expense #{args.display_id} deleted successfully")

    except ExpenseNotFoundError as e:
        print(f"✗ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Penny Tracker - Simple Expense Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  penny add --amount 50 --category food --date 15-02-2026 --note "lunch"
  penny view
  penny filter --category food
  penny filter --from 10-02-2026 --to 20-02-2026
  penny summary --month 2 --year 2026
  penny edit 1 --amount 75 --note "fancy lunch"
  penny delete 2
        """,
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add new expense")
    add_parser.add_argument(
        "--amount", required=True, type=float, help="Expense amount"
    )
    add_parser.add_argument("--category", required=True, help="Expense category")
    add_parser.add_argument("--date", required=True, help="Date in DD-MM-YYYY format")
    add_parser.add_argument("--note", default="", help="Optional note")

    # View command
    view_parser = subparsers.add_parser("view", help="View all expenses")

    # Filter command
    filter_parser = subparsers.add_parser("filter", help="Filter expenses")
    filter_parser.add_argument("--category", help="Filter by category")
    filter_parser.add_argument(
        "--from", dest="date_from", help="Start date (DD-MM-YYYY)"
    )
    filter_parser.add_argument("--to", dest="date_to", help="End date (DD-MM-YYYY)")

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Monthly summary")
    summary_parser.add_argument("--month", required=True, type=int, help="Month (1-12)")
    summary_parser.add_argument(
        "--year", required=True, type=int, help="Year (e.g., 2026)"
    )

    # Edit command
    edit_parser = subparsers.add_parser("edit", help="Edit expense by display ID")
    edit_parser.add_argument(
        "display_id", type=int, help="Display ID from view command"
    )
    edit_parser.add_argument("--amount", type=float, help="New amount")
    edit_parser.add_argument("--category", help="New category")
    edit_parser.add_argument("--date", help="New date (DD-MM-YYYY)")
    edit_parser.add_argument("--note", help="New note")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete expense by display ID")
    delete_parser.add_argument(
        "display_id", type=int, help="Display ID from view command"
    )

    # Parse arguments
    args = parser.parse_args()

    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize tracker
    tracker = ExpenseTracker()

    # Route to appropriate command handler
    if args.command == "add":
        cmd_add(args, tracker)
    elif args.command == "view":
        cmd_view(args, tracker)
    elif args.command == "filter":
        cmd_filter(args, tracker)
    elif args.command == "summary":
        cmd_summary(args, tracker)
    elif args.command == "edit":
        cmd_edit(args, tracker)
    elif args.command == "delete":
        cmd_delete(args, tracker)


if __name__ == "__main__":
    main()
