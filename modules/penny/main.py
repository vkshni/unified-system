# Penny Entry Point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project modules
from modules.penny.engine import ExpenseTracker
from modules.penny.exceptions import *
from shared.ui_utils import print_error, print_success, print_table, confirm

# Data Path
DATA_DIR = Path(__file__).parent / "data"
EXPENSE_FILE_PATH = DATA_DIR / "expenses.csv"

# Initialize Expense Tracker (lazy loading handled below)
_tracker = None


def get_tracker():
    """Lazy initialization of ExpenseTracker"""
    global _tracker
    if _tracker is None:
        _tracker = ExpenseTracker()
    return _tracker


# ========== HELPER FUNCTIONS ==========


def display_expenses(expenses):
    """Display expenses in a formatted table"""
    if not expenses:
        print("\nNo expenses found.")
        return

    formatted_data = [
        [
            e[0],  # display_id
            f"₹{e[2]:.2f}",  # amount
            e[3],  # category
            e[4],  # date
            e[5] if len(e) > 5 else "",  # note
        ]
        for e in expenses
    ]

    headers = ["#", "Amount", "Category", "Date", "Note"]

    print("\n Expenses \n")
    print_table(headers, formatted_data)
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


# ========== COMMANDS ==========


def cmd_add(args):
    """Add a new expense"""
    if len(args) < 7:
        print_error(
            "Usage: add --amount <num> --category <name> --date <DD-MM-YYYY> [--note <text>]"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--amount", required=True, type=float)
        parser.add_argument("--category", required=True)
        parser.add_argument("--date", required=True)
        parser.add_argument("--note", default="")

        parsed = parser.parse_args(args[1:])

        tracker = get_tracker()
        tracker.add_expense(parsed.amount, parsed.category, parsed.date, parsed.note)

        print_success(f"Expense added: ₹{parsed.amount} - {parsed.category}")
        return 0

    except InvalidAmountError as e:
        print_error(f"Invalid amount: {e}")
        return 1
    except EmptyFieldError as e:
        print_error(f"Empty field: {e}")
        return 1
    except InvalidDateError as e:
        print_error(f"Invalid date: {e}")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_view():
    """View all expenses"""
    try:
        tracker = get_tracker()
        expenses = tracker.view_all()

        if not expenses:
            print(
                "\nNo expenses yet. Add one with: add --amount 50 --category food --date 15-02-2026\n"
            )
            return 0

        display_expenses(expenses)
        print_success(f"Total {len(expenses)} expense(s)")
        return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_filter(args):
    """Filter expenses by category or date range"""
    if len(args) < 3:
        print_error(
            "Usage: filter --category <name>  OR  filter --from <date> --to <date>"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--category")
        parser.add_argument("--from", dest="date_from")
        parser.add_argument("--to", dest="date_to")

        parsed = parser.parse_args(args[1:])

        tracker = get_tracker()

        if parsed.category:
            expenses = tracker.filter_by_category(parsed.category)
            print(f"\nExpenses in category: {parsed.category}")
            display_expenses(expenses)
            return 0

        elif parsed.date_from and parsed.date_to:
            expenses = tracker.filter_by_date_range(parsed.date_from, parsed.date_to)
            print(f"\nExpenses from {parsed.date_from} to {parsed.date_to}")
            display_expenses(expenses)
            return 0

        else:
            print_error("Provide either --category or both --from and --to")
            return 1

    except InvalidDateError as e:
        print_error(f"Invalid date: {e}")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_summary(args):
    """Show monthly summary"""
    if len(args) < 5:
        print_error("Usage: summary --month <1-12> --year <YYYY>")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--month", required=True, type=int)
        parser.add_argument("--year", required=True, type=int)

        parsed = parser.parse_args(args[1:])

        if not (1 <= parsed.month <= 12):
            print_error("Month must be between 1 and 12")
            return 1

        tracker = get_tracker()
        summary = tracker.monthly_summary(parsed.month, parsed.year)

        print(f"\nMonthly Summary for {parsed.month:02d}/{parsed.year}")
        display_summary(summary)
        return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_edit(args):
    """Edit an existing expense"""
    if len(args) < 2:
        print_error(
            "Usage: edit <id> [--amount <num>] [--category <name>] [--date <DD-MM-YYYY>] [--note <text>]"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("display_id", type=int)
        parser.add_argument("--amount", type=float)
        parser.add_argument("--category")
        parser.add_argument("--date")
        parser.add_argument("--note")

        parsed = parser.parse_args(args[1:])

        # Build kwargs for only provided arguments
        kwargs = {}
        if parsed.amount is not None:
            kwargs["amount"] = parsed.amount
        if parsed.category is not None:
            kwargs["category"] = parsed.category
        if parsed.date is not None:
            kwargs["date"] = parsed.date
        if parsed.note is not None:
            kwargs["note"] = parsed.note

        if not kwargs:
            print_error("Nothing to update. Specify at least one option")
            return 1

        tracker = get_tracker()
        result = tracker.edit_expense(parsed.display_id, **kwargs)

        if result:
            print_success(f"Expense #{parsed.display_id} updated")
            return 0
        else:
            print_error(f"Expense #{parsed.display_id} not found")
            return 1

    except ExpenseNotFoundError as e:
        print_error(str(e))
        return 1
    except (InvalidAmountError, EmptyFieldError, InvalidDateError) as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_delete(args):
    """Delete an expense"""
    if len(args) < 2:
        print_error("Usage: delete <id> [--force]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("display_id", type=int)
        parser.add_argument("--force", action="store_true")

        parsed = parser.parse_args(args[1:])

        tracker = get_tracker()

        # Get the expense to show what will be deleted
        expense = tracker.get_expense_by_display_id(parsed.display_id)

        if not parsed.force:
            print(f"\n⚠️  About to delete:")
            print(f"  Amount: ₹{expense.amount:.2f}")
            print(f"  Category: {expense.category}")
            print(f"  Date: {expense.date}")
            print(f"  Note: {expense.note}")

            if not confirm("Delete this expense?"):
                print("Cancelled")
                return 0

        tracker.delete_expense(parsed.display_id)
        print_success(f"Expense #{parsed.display_id} deleted")
        return 0

    except ExpenseNotFoundError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_help():
    """Show help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║                PENNY - Expense Tracker                         ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  penny <command> [options]

COMMANDS:
  add <options>                       Add new expense
  view                                View all expenses
  filter <options>                    Filter expenses
  summary <options>                   Show monthly summary
  edit <id> <options>                 Edit expense
  delete <id> [--force]               Delete expense
  help                                Show this help message
  exit                                Exit penny

ADD OPTIONS:
  --amount <number>                   Expense amount (required)
  --category <name>                   Category (required)
  --date <DD-MM-YYYY>                 Date (required)
  --note <text>                       Optional note

FILTER OPTIONS:
  --category <name>                   Filter by category
  --from <DD-MM-YYYY>                 Start date
  --to <DD-MM-YYYY>                   End date

SUMMARY OPTIONS:
  --month <1-12>                      Month number
  --year <YYYY>                       Year

EDIT OPTIONS:
  --amount <number>                   New amount
  --category <name>                   New category
  --date <DD-MM-YYYY>                 New date
  --note <text>                       New note

EXAMPLES:
  penny add --amount 50 --category food --date 15-02-2026 --note "lunch"
  penny view
  penny filter --category food
  penny filter --from 10-02-2026 --to 20-02-2026
  penny summary --month 2 --year 2026
  penny edit 1 --amount 75 --note "fancy lunch"
  penny delete 2 --force

CATEGORIES:
  Common categories: food, transport, entertainment, bills, shopping, 
  health, education, other
"""
    print(help_text)
    return 0


# ========== SHELL & EXECUTION ==========


def run_shell():
    """Interactive shell mode"""
    print_success("Entering Penny - Expense Tracker")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("[penny] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]

            if command == "exit":
                if confirm("Exit penny?"):
                    print("\n👋 Exiting penny!\n")
                    break
                else:
                    continue

            result = execute_command(parts)

            if result != 0 and result != 2:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            if confirm("Exit penny?"):
                print("\n👋 Exiting penny!\n")
                break
        except Exception as e:
            print_error(f"Error: {e}")


def execute_command(args):
    """Execute a command"""
    if not args:
        return 1

    command = args[0].lower()

    try:
        if command == "add":
            return cmd_add(args)
        elif command == "view":
            return cmd_view()
        elif command == "filter":
            return cmd_filter(args)
        elif command == "summary":
            return cmd_summary(args)
        elif command == "edit":
            return cmd_edit(args)
        elif command == "delete":
            return cmd_delete(args)
        elif command == "help":
            return cmd_help()
        else:
            print_error(f"Unknown command: '{command}'")
            print("Type 'help' for available commands")
            return 1

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    run_shell()
