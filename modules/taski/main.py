# Taski Entry Point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project modules
from modules.taski.engine import TaskManager
from shared.ui_utils import print_error, print_success, print_table, confirm

# Data Path
DATA_DIR = Path(__file__).parent / "data"
TASK_FILE_PATH = DATA_DIR / "tasks.csv"

# Initialize Task Manager
tm = TaskManager(TASK_FILE=TASK_FILE_PATH)


# ========== COMMANDS ==========


def cmd_add(args):
    """Add a new task"""
    if len(args) < 2:
        print_error("Usage: add <title> [--note <text>]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("title", type=str)
        parser.add_argument("--note", type=str, default="")

        # Join remaining args as title if spaces
        title_parts = []
        note = ""
        i = 1

        while i < len(args):
            if args[i] == "--note":
                if i + 1 < len(args):
                    note = args[i + 1]
                break
            else:
                title_parts.append(args[i])
            i += 1

        title = " ".join(title_parts)

        if not title:
            print_error("Title cannot be empty")
            return 1

        result = tm.add_task(title, note=note)

        if result:
            print_success(f"Task '{title}' added successfully")
            return 0
        else:
            print_error("Failed to add task")
            return 1

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_list():
    """List all tasks"""
    try:
        tasks = tm.view_all()

        if not tasks:
            print('\nNo tasks yet. Add one with: add "Task title"\n')
            return 0

        formatted_data = [
            [
                task[0],  # display_id
                task[2][:30] + "..." if len(task[2]) > 30 else task[2],  # title
                task[6],  # state
                task[3][:10] if task[3] else "-",  # created_at (date only)
                (
                    task[5][:20] + "..."
                    if task[5] and len(task[5]) > 20
                    else task[5] or "-"
                ),  # note
            ]
            for task in tasks
        ]

        headers = ["ID", "Title", "State", "Created", "Note"]

        print("\n Tasks \n")
        print_table(headers, formatted_data)
        print()
        print_success(f"Total {len(tasks)} task(s)")
        return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_update(args):
    """Update a task"""
    if len(args) < 2:
        print_error("Usage: update <id> [--title <text>] [--note <text>]")
        return 2

    try:
        display_id = int(args[1])

        parser = argparse.ArgumentParser()
        parser.add_argument("id", type=int)
        parser.add_argument("--title", type=str)
        parser.add_argument("--note", type=str)

        parsed = parser.parse_args(args[1:])

        if parsed.title is None and parsed.note is None:
            print_error("Nothing to update. Use --title or --note")
            return 1

        result = tm.update_task(
            parsed.id,
            title=parsed.title,
            note=parsed.note,
        )

        if result:
            print_success(f"Task {parsed.id} updated successfully")
            return 0
        else:
            print_error("Failed to update task")
            return 1

    except ValueError:
        print_error("Invalid task ID")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_advance(args):
    """Advance task to next state"""
    if len(args) < 3:
        print_error("Usage: advance <id> <state>")
        print("States: in_progress, done, cancelled")
        return 2

    try:
        display_id = int(args[1])
        state = args[2].upper()

        valid_states = ["IN_PROGRESS", "DONE", "CANCELLED"]
        if state not in valid_states:
            print_error(f"Invalid state. Use: {', '.join(valid_states)}")
            return 1

        result = tm.update_task(display_id, state=state)

        if result:
            print_success(f"Task {display_id} advanced to {state}")
            return 0
        else:
            print_error("Failed to advance task")
            return 1

    except ValueError:
        print_error("Invalid task ID")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_delete(args):
    """Delete a task"""
    if len(args) < 2:
        print_error("Usage: delete <id> [--force]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("id", type=int)
        parser.add_argument("--force", action="store_true")

        parsed = parser.parse_args(args[1:])

        if not parsed.force:
            if not confirm(f"Delete task {parsed.id}?"):
                print("Cancelled")
                return 0

        result = tm.delete_task(parsed.id)

        if result:
            print_success(f"Task {parsed.id} deleted")
            return 0
        else:
            print_error("Failed to delete task")
            return 1

    except ValueError:
        print_error("Invalid task ID")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_filter(args):
    """Filter tasks"""
    if len(args) < 3:
        print_error("Usage: filter <field> <value>")
        print("Fields: title, state, created_on, completed_on")
        return 2

    try:
        field = args[1].upper()
        value = args[2]

        tasks = tm.get_task_by_filter(field, value)

        if not tasks:
            print(f"No tasks found where {field} = '{value}'")
            return 0

        print(f"\n{'ID':<5} {'TITLE':<30} {'STATE':<15} {'CREATED':<12}")
        print("-" * 70)
        for t in tasks:
            created = (
                t.created_at.strftime("%d-%m-%Y")
                if hasattr(t.created_at, "strftime")
                else str(t.created_at)[:10]
            )
            title = t.title[:27] + "..." if len(t.title) > 30 else t.title
            print(f"{t.display_id:<5} {title:<30} {t.state:<15} {created:<12}")
        print()
        print_success(f"Found {len(tasks)} task(s)")
        return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_help():
    """Show help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║                   TASKI - Task Manager                         ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  taski <command> [options]

COMMANDS:
  add <title> [--note <text>]        Add a new task
  list                                List all tasks
  update <id> [options]               Update a task
  advance <id> <state>                Move task to next state
  delete <id> [--force]               Delete a task
  filter <field> <value>              Filter tasks
  help                                Show this help message
  exit                                Exit taski

UPDATE OPTIONS:
  --title <text>                      New title
  --note <text>                       New note

STATES:
  Flow: TODO → IN_PROGRESS → DONE
  Valid states: in_progress, done, cancelled

FILTER FIELDS:
  title, state, created_on, completed_on

EXAMPLES:
  taski add "Learn Python" --note "2 hours daily"
  taski list
  taski advance 1 in_progress
  taski update 2 --title "Learn Python 3"
  taski delete 3 --force
  taski filter state TODO
  taski filter created_on "26-02-2026"

RULES:
  - Cannot skip states (TODO → DONE not allowed)
  - Cannot modify DONE tasks
  - Cannot reverse transitions
"""
    print(help_text)
    return 0


# ========== SHELL & EXECUTION ==========


def run_shell():
    """Interactive shell mode"""
    print_success("Entering Taski - Task Manager")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("[taski] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]

            if command == "exit":
                if confirm("Exit taski?"):
                    print("\n👋 Exiting taski!\n")
                    break
                else:
                    continue

            result = execute_command(parts)

            if result != 0 and result != 2:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            if confirm("Exit taski?"):
                print("\n👋 Exiting taski!\n")
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
        elif command == "list":
            return cmd_list()
        elif command == "update":
            return cmd_update(args)
        elif command == "advance":
            return cmd_advance(args)
        elif command == "delete":
            return cmd_delete(args)
        elif command == "filter":
            return cmd_filter(args)
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
