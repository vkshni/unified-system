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
                print("\nExiting idgen!\n")
                break

            result = execute_command([command] + args)

            if result != 0:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print_error(f"Error: {e}")

    #     elif command == "generate":
    #         id_type = args[1].strip()
    #         generated_id = idg.generate(id_type)
    #         print_success(f"Generated: {generated_id}")

    #     elif command == "list":

    # print("Leaving idgen shell")


def execute_command(args):

    if not args:
        return 1
    command = args[0]

    try:
        if command == "generate":

            # Parser Arguments
            parser = argparse.ArgumentParser()
            parser.add_argument("type")

            parsed = parser.parse_args(args[1:])

            # Execute
            generated_id = idg.generate(parsed.type)
            print_success(f"Generated: {generated_id}")
            return 0

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
            print_table(headers, formatted_data)
            print()
            print_success(f"Total {len(id_types)} ID type(s) fetched")
            return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


if __name__ == "__main__":

    run_shell()
