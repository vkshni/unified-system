# IDGen Entry point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project modules
from shared.ui_utils import print_error, print_success, print_table, confirm
from modules.idgen.engine import IDGenerator

# Data Path
DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = DATA_DIR / "config.json"
COUNTER_FILE = DATA_DIR / "counter.json"

# Initialize ID Generator
idg = IDGenerator(CONFIG_FILE=str(CONFIG_FILE), COUNTER_FILE=str(COUNTER_FILE))


# ========== COMMANDS ==========


def cmd_generate(args):
    """Generate a new ID for a type"""
    if len(args) < 2:
        print_error("Usage: generate <type>")
        return 2

    type_name = args[1]

    try:
        generated_id = idg.generate(type_name)
        print_success(f"Generated: {generated_id}")
        return 0
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_add(args):
    """Add a new ID type"""
    if len(args) < 11:
        print_error(
            "Usage: add --name <name> --start <num> --step <num> --prefix <text> --padding <num>"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", required=True)
        parser.add_argument("--start", type=int, required=True)
        parser.add_argument("--step", type=int, required=True)
        parser.add_argument("--prefix", required=True)
        parser.add_argument("--padding", type=int, required=True)

        parsed = parser.parse_args(args[1:])

        result = idg.add_id_type(
            parsed.name,
            parsed.start,
            parsed.step,
            parsed.prefix,
            parsed.padding,
        )

        if result:
            print_success(f"ID type '{parsed.name}' added successfully")
            return 0
        else:
            print_error("Failed to add ID type")
            return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_update(args):
    """Update an existing ID type"""
    if len(args) < 3:
        print_error(
            "Usage: update <name> [--start <num>] [--step <num>] [--prefix <text>] [--padding <num>]"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("name")
        parser.add_argument("--start", type=int)
        parser.add_argument("--step", type=int)
        parser.add_argument("--prefix")
        parser.add_argument("--padding", type=int)

        parsed = parser.parse_args(args[1:])

        kwargs = {}
        if parsed.start is not None:
            kwargs["start_value"] = parsed.start
        if parsed.step is not None:
            kwargs["increment_step"] = parsed.step
        if parsed.prefix is not None:
            kwargs["prefix"] = parsed.prefix
        if parsed.padding is not None:
            kwargs["padding"] = parsed.padding

        if not kwargs:
            print_error("Nothing to update. Specify at least one option.")
            return 1

        result = idg.update_id_type(parsed.name, **kwargs)

        if result:
            print_success(f"ID type '{parsed.name}' updated successfully")
            return 0
        else:
            print_error("Failed to update ID type")
            return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_delete(args):
    """Delete an ID type"""
    if len(args) < 2:
        print_error("Usage: delete <name> [--force]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("name")
        parser.add_argument("--force", action="store_true")

        parsed = parser.parse_args(args[1:])

        if not parsed.force:
            if not confirm(f"Delete ID type '{parsed.name}'?"):
                print("Cancelled")
                return 0

        result = idg.delete_id_type(parsed.name, force=True)

        if result:
            print_success(f"ID type '{parsed.name}' deleted successfully")
            return 0
        else:
            print_error("Failed to delete ID type")
            return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_reset(args):
    """Reset counter for an ID type"""
    if len(args) < 2:
        print_error("Usage: reset <name> [--force]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("name")
        parser.add_argument("--force", action="store_true")

        parsed = parser.parse_args(args[1:])

        if not parsed.force:
            if not confirm(f"Reset counter for '{parsed.name}'?"):
                print("Cancelled")
                return 0

        result = idg.reset_counter(parsed.name, force=True)

        if result:
            print_success(f"Counter for '{parsed.name}' reset successfully")
            return 0
        else:
            print_error("Failed to reset counter")
            return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_genpass(args):
    """Generate a random password"""
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--length", type=int, default=12)

        parsed = parser.parse_args(args[1:])

        result = idg.generate_password(pwd_len=parsed.length)

        if result:
            print_success(f"Password: {result}")
            return 0
        else:
            print_error("Failed to generate password")
            return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_list():
    """List all ID types"""
    try:
        id_types = idg.list_id_types()

        if not id_types:
            print("\nNo ID types configured yet.")
            print(
                'Add one with: add --name "TASK" --start 1 --step 1 --prefix "T" --padding 3\n'
            )
            return 0

        formatted_data = [
            [
                i["name"],
                i["prefix"],
                i["counter"],
                i["start_value"],
                i["increment_step"],
                i["padding"],
            ]
            for i in id_types
        ]

        headers = ["Name", "Prefix", "Counter", "Start", "Step", "Padding"]

        print("\n Available ID Types \n")
        print_table(headers, formatted_data)
        print()
        print_success(f"Total {len(id_types)} ID type(s)")
        return 0
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_help():
    """Show help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║                    IDGEN - ID Generator                        ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  idgen <command> [options]

COMMANDS:
  generate <type>                     Generate a new ID for a type
  add <options>                       Add a new ID type
  update <name> <options>             Update an existing ID type
  delete <name> [--force]             Delete an ID type
  reset <name> [--force]              Reset counter for an ID type
  list                                List all ID types
  genpass [--length <num>]            Generate random password
  help                                Show this help message
  exit                                Exit idgen

ADD/UPDATE OPTIONS:
  --name <name>                       Type name (required for add)
  --start <num>                       Starting value
  --step <num>                        Increment step
  --prefix <text>                     Prefix for IDs
  --padding <num>                     Zero-padding width

EXAMPLES:
  idgen add --name TASK --start 1 --step 1 --prefix T --padding 3
  idgen generate TASK
  idgen update TASK --step 5
  idgen list
  idgen reset TASK
  idgen delete TASK --force
  idgen genpass --length 16
"""
    print(help_text)
    return 0


# ========== SHELL & EXECUTION ==========


def run_shell():
    """Interactive shell mode"""
    print_success("Entering ID Generator")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("[idgen] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]

            if command == "exit":
                if confirm("Exit idgen?"):
                    print("\n👋 Exiting idgen!\n")
                    break
                else:
                    continue

            result = execute_command(parts)

            if result != 0 and result != 2:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            if confirm("Exit idgen?"):
                print("\n👋 Exiting idgen!\n")
                break
        except Exception as e:
            print_error(f"Error: {e}")


def execute_command(args):
    """Execute a command"""
    if not args:
        return 1

    command = args[0].lower()

    try:
        if command == "generate":
            return cmd_generate(args)
        elif command == "add":
            return cmd_add(args)
        elif command == "update":
            return cmd_update(args)
        elif command == "delete":
            return cmd_delete(args)
        elif command == "reset":
            return cmd_reset(args)
        elif command == "list":
            return cmd_list()
        elif command == "genpass":
            return cmd_genpass(args)
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
