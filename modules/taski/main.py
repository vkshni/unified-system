# Taski Entry Point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from modules.taski.engine import TaskManager
from shared.ui_utils import print_error, print_success, print_table, confirm
from exceptions import (
    TaskNotFoundError,
    FilterNotFoundError,
    FieldEmptyError,
    StateTransitionError,
    CompletedTimeError,
)

# Data Path
DATA_DIR = Path(__file__).parent / "data"
TASK_FILE_PATH = DATA_DIR / "tasks.csv"

# Initialize Task Manager
tm = TaskManager(TASK_FILE=TASK_FILE_PATH)


def cmd_add(args):
    tm.add_task(args.title, note=args.note or "")
    print(f"✓ Task '{args.title}' added.")


def cmd_list(args):
    tasks = tm.view_all()
    if not tasks:
        print('No tasks yet. Add one with: taski add "Task title"')
        return
    print(f"\n{'#':<5} {'TITLE':<25} {'STATE':<15} {'CREATED':<22} {'NOTE'}")
    print("-" * 85)
    for t in tasks:
        num, task_id, title, created, completed, note, state = t
        print(f"{num:<5} {title:<25} {state:<15} {created:<22} {note}")
    print()


def cmd_update(args):
    if args.title is None and args.note is None:
        print("Nothing to update. Use --title or --note to specify what to change.")
        print('  Example: taski update 1 --title "New Title"')
        sys.exit(1)
    tm.update_task(args.id, title=args.title, note=args.note)
    print(f"✓ Task {args.id} updated.")


def cmd_advance(args):
    tm.update_task(args.id, state=args.state.upper())
    print(f"✓ Task {args.id} advanced to {args.state.upper()}.")


def cmd_delete(args):
    tm.delete_task(args.id)
    print(f"✓ Task {args.id} deleted.")


def cmd_filter(args):
    tasks = tm.get_task_by_filter(args.by.upper(), args.value)
    if not tasks:
        print(f"No tasks found where {args.by.upper()} = '{args.value}'.")
        return
    print(f"\n{'TITLE':<25} {'STATE':<15} {'CREATED':<22} {'NOTE'}")
    print("-" * 75)
    for t in tasks:
        print(
            f"{t.title:<25} {t.state:<15} {t.created_at.strftime('%d-%m-%Y %H:%M:%S'):<22} {t.note}"
        )
    print()


def cmd_help(args):
    help_text = """
taski — a simple state-driven task manager

COMMANDS:
  add <title> [--note <text>]         Add a new task
  list                                List all tasks
  update <id> [--title] [--note]      Edit a task's title or note
  advance <id> <state>                Move task to next state
  delete <id>                         Delete a task
  filter <by> <value>                 Filter tasks by field

STATES:
  Flow: TODO → IN_PROGRESS → DONE
  Valid targets for advance: in_progress, done, cancelled
  Rules:
    - Cannot skip states (TODO → DONE not allowed)
    - Cannot modify a DONE task
    - Cannot reverse a transition

FILTER OPTIONS:
  title         Match by exact title
  created_on    Match by date (format: DD-MM-YYYY)
  completed_on  Match by completion date (format: DD-MM-YYYY)

EXAMPLES:
  taski add "Learn Python" --note "2 hrs"
  taski list
  taski advance 1 in_progress
  taski advance 1 done
  taski update 2 --title "Learn Python 3"
  taski delete 3
  taski filter title "Learn Python"
  taski filter created_on "26-02-2026"
"""
    print(help_text)


def handle_error(e):
    errors = {
        TaskNotFoundError: "Task not found. Run 'taski list' to see valid task numbers.",
        FilterNotFoundError: "Invalid filter. Use: title, created_on, or completed_on.",
        FieldEmptyError: "Title cannot be empty or blank.",
        StateTransitionError: str(e),
        CompletedTimeError: str(e),
    }
    msg = errors.get(type(e), f"Unexpected error: {e}")
    print(f"Error: {msg}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="taski",
        description="A state-driven task manager CLI",
        add_help=True,
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    # add
    p_add = sub.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("--note", help="Optional note", default="")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=cmd_list)

    # update
    p_update = sub.add_parser("update", help="Update task title or note")
    p_update.add_argument("id", type=int, help="Task display number")
    p_update.add_argument("--title", help="New title", default=None)
    p_update.add_argument("--note", help="New note", default=None)
    p_update.set_defaults(func=cmd_update)

    # advance
    p_advance = sub.add_parser("advance", help="Advance task to next state")
    p_advance.add_argument("id", type=int, help="Task display number")
    p_advance.add_argument(
        "state", choices=["in_progress", "done", "cancelled"], help="Target state"
    )
    p_advance.set_defaults(func=cmd_advance)

    # delete
    p_delete = sub.add_parser("delete", help="Delete a task")
    p_delete.add_argument("id", type=int, help="Task display number")
    p_delete.set_defaults(func=cmd_delete)

    # filter
    p_filter = sub.add_parser("filter", help="Filter tasks by field")
    p_filter.add_argument(
        "by", choices=["title", "created_on", "completed_on"], help="Filter field"
    )
    p_filter.add_argument("value", help="Value to match")
    p_filter.set_defaults(func=cmd_filter)

    # help
    p_help = sub.add_parser("help", help="Show usage and examples")
    p_help.set_defaults(func=cmd_help)

    args = parser.parse_args()

    try:
        args.func(args)
    except (
        TaskNotFoundError,
        FilterNotFoundError,
        FieldEmptyError,
        StateTransitionError,
        CompletedTimeError,
    ) as e:
        handle_error(e)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
