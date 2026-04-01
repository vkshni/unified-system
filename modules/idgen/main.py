# IDGen Entry point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.ui_utils import print_error, print_success, print_table
from modules.idgen.engine import IDGenerator

# Data Path
DATA_DIR = Path(__file__).parent / "data"
CONFIG_FILE = DATA_DIR / "config.json"
COUNTER_FILE = DATA_DIR / "counter.json"

# Initialize ID Generator
idg = IDGenerator(CONFIG_FILE=str(CONFIG_FILE), COUNTER_FILE=str(COUNTER_FILE))


# Run shell
def run_shell():

    print_success("Entering ID Generator")
    print("Commands: generate, list")

    while True:

        try:

            user_input = input("[idgen] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if command == "exit":
                print("\n👋 Exiting idgen!\n")
                break

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

        elif command == "add":

            if not args[1:]:
                print_error(f"No arguments passed")
                return 2

            # Parser Arguments
            parser = argparse.ArgumentParser()
            parser.add_argument("id_type_label")
            parser.add_argument("id_type")
            parser.add_argument("start_value_label")
            parser.add_argument("start_value", type=int)
            parser.add_argument("increment_step_label")
            parser.add_argument("increment_step", type=int)
            parser.add_argument("prefix_label")
            parser.add_argument("prefix")
            parser.add_argument("padding_label")
            parser.add_argument("padding", type=int)
            print(args)

            parsed = parser.parse_args(args[1:])

            # Execute
            result = idg.add_id_type(
                parsed.id_type,
                int(parsed.start_value),
                int(parsed.increment_step),
                parsed.prefix,
                int(parsed.padding),
            )
            if result:
                print_success(f"ID type '{parsed.id_type}' added successfully")
                return 0
            else:
                return 1

        elif command == "list":

            # Parser Arguments
            parser = argparse.ArgumentParser()
            # parser.add_argument("list")

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

        else:
            print_error(f"Command '{command}' doesn't exit")
            print("Commands: generate, list")
            return 1

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


if __name__ == "__main__":

    run_shell()
