# IDGen Entry point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.ui_utils import print_error, print_success, print_table, confirm
from modules.idgen.engine import IDGenerator

# Data Path
DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = DATA_DIR / "config.json"
COUNTER_FILE = DATA_DIR / "counter.json"

# Initialize ID Generator
idg = IDGenerator(CONFIG_FILE=str(CONFIG_FILE), COUNTER_FILE=str(COUNTER_FILE))


# COMMANDS


# generate
def cmd_generate(args):

    if not args[1:]:
        print_error(f"No arguments passed")
        return 2

    # Parser Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("type_label")
    parser.add_argument("type")

    parsed = parser.parse_args(args[1:])

    # Execute
    generated_id = idg.generate(parsed.type)
    print_success(f"Generated successfully: {generated_id}")
    return 0


# add
def cmd_add(args):

    if not args[1:]:
        print_error(f"No arguments passed")
        return 2

    # Parser Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("name_label")
    parser.add_argument("name")
    parser.add_argument("start_label")
    parser.add_argument("start", type=int)
    parser.add_argument("step_label")
    parser.add_argument("step", type=int)
    parser.add_argument("prefix_label")
    parser.add_argument("prefix")
    parser.add_argument("padding_label")
    parser.add_argument("padding", type=int)

    parsed = parser.parse_args(args[1:])

    # Execute
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
        return 1


# update
def cmd_update(args):

    if not args[1:]:
        print_error(f"No arguments passed")
        return 2

    # Parser Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("name_label")
    parser.add_argument("name", type=str)
    parser.add_argument("--start_label")
    parser.add_argument("--start", type=int)
    parser.add_argument("--step_label")
    parser.add_argument("--step", type=int)
    parser.add_argument("--prefix_label")
    parser.add_argument("--prefix", type=str)
    parser.add_argument("--padding_label")
    parser.add_argument("--padding", type=int)

    parsed = parser.parse_args(args[1:])

    # Execute
    kwargs = {}
    if parsed.start:
        kwargs["start_value"] = parsed.start
    if parsed.step:
        kwargs["increment_step"] = parsed.step
    if parsed.prefix:
        kwargs["prefix"] = parsed.prefix
    if parsed.padding:
        kwargs["padding"] = parsed.padding

    result = idg.update_id_type(parsed.name, **kwargs)

    if result:
        print_success(f"ID type '{parsed.name}' updated successfully")
        return 0
    else:
        return 1


# delete command
def cmd_delete(args):

    if not args:
        print_error(f"No arguments passed")
        return 2

    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("name_label")
    parser.add_argument("name", type=str)
    parser.add_argument("--force", action="store_true")

    parsed = parser.parse_args(args[1:])

    # Execute
    result = idg.delete_id_type(parsed.name, force=parsed.force)
    if result:
        print_success(f"ID type '{parsed.name}' deleted successfully")
        return 0
    else:
        return 1


# reset command
def cmd_reset(args):

    if not args:
        print_error(f"No arguments passed")
        return 2

    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("name_label")
    parser.add_argument("name", type=str)
    parser.add_argument("--force", action="store_true")

    parsed = parser.parse_args(args[1:])

    # Execute
    result = idg.reset_counter(parsed.name, force=parsed.force)
    if result:
        print_success(f"ID type '{parsed.name}' reset successfully")
        return 0
    else:
        return 1


# command genpass
def cmd_genpass(args):

    if not args:
        print_error(f"No arguments passed")
        return 2

    # Parse Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--length_label")
    parser.add_argument("--length", type=int)

    parsed = parser.parse_args(args[1:])

    # Execute
    if parsed.length:
        result = idg.generate_password(pwd_len=parsed.length)
    else:
        result = idg.generate_password()

    if result:
        print_success(f"Password generated successfully: {result}")
        return 0
    else:
        return 1


def cmd_list():

    # Fetching all ID types
    id_types = idg.list_id_types()

    if not id_types:
        print("No ID types found")
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
    headers = [
        "name",
        "prefix",
        "counter",
        "start_value",
        "increment_step",
        "padding",
    ]
    print("\n Available ID types \n")
    print_table(headers, formatted_data)
    print()
    print_success(f"Total {len(id_types)} ID type(s) fetched")
    return 0


# Run shell
def run_shell():

    print_success("Entering ID Generator")
    print("Commands: generate, add, update, delete, reset, list, genpass")

    while True:

        try:

            user_input = input("[idgen] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if command == "exit":
                if confirm("\nExit idgen?"):
                    print("\n👋 Exiting idgen!\n")
                    break
                else:
                    continue

            result = execute_command([command] + args)

            if result != 0:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print_error(f"Error: {e}")


def execute_command(args):

    if not args:
        return 1
    command = args[0]

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

        else:
            print_error(f"Command '{command}' doesn't exit")
            print("Commands: generate, add, update, delete, reset, list, genpass")
            return 1

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


if __name__ == "__main__":

    run_shell()
