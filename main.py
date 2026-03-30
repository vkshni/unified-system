# CLI

# Libraries
import argparse
import sys
import getpass

# Project modules
from auth.auth_manager import AuthService
from config.systems import SYSTEMS
import shared.ui_utils as ui

auth = AuthService()


# Decorator
def require_init(func):

    def wrapper(args):
        if not auth.is_initialized:
            print("\n✗ System not initialized\n")
            print("First-time setup required:")
            print("  python main.py init\n")
            sys.exit(1)
        return func(args)

    return wrapper


# Commands
def cmd_init(args):

    if auth.is_initialized():
        print("\n✗ System already initialized\n")
        return

    print("\n=== First-Time Setup ===\n")
    password = getpass.getpass("Create master password (min 6 chars): ")
    confirm_password = getpass.getpass("Confirm password: ")

    # Validate password match
    if password != confirm_password:
        print("\n✗ Passwords don't match. Please try again.\n")
        return

    # Validate password length
    if len(password) < 6:
        print("\n✗ Password too short (minimum 6 characters)\n")
        return

    # Validate alphanumeric
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
        print("\n✗ Password must contain both letters and numbers\n")
        return

    # Setup complete
    auth.setup_master(password)
    print("\n✓ Master password created successfully!")


# welcome screen
def cmd_welcome():

    ui.clear_screen()
    ui.print_header("UNIFIED SYSTEM v1.0")
    print(
        """Available Systems:

  idgen      - Generate IDs with prefixes and counters
  penny      - Track expenses and view summaries [AUTH REQUIRED]
  taski      - Manage tasks with states and priorities
  shield     - Password manager with encryption [AUTH REQUIRED]
  shorturl   - Shorten URLs and track clicks
  snippet    - Store code snippets [AUTH REQUIRED]

Commands:
  <system>   - Enter system shell mode
  help       - Show detailed help
  exit       - Quit application"""
    )

    user_input = ui.get_input("Enter system name (or exit): ")
    if user_input == "exit":
        return "exit"
    if user_input not in SYSTEMS:
        print(f"System name '{user_input}' not found")
        return False

    return user_input


# help
def cmd_help(args):
    print("Help Message! (To be implemented)")


def main():

    ui.clear_screen()

    parser = argparse.ArgumentParser(
        prog="main.py", description=ui.print_header("UNIFIED SYSTEM V1.0")
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")
    # sub.required = True

    # ========== INIT ==========
    p_init = sub.add_parser(
        "init",
        help="Initialize system (first-time setup)",
        description="Set up master password for protected systems",
    )
    p_init.set_defaults(func=cmd_init)

    # ========== HELP ==========
    p_help = sub.add_parser("help", help="Help")
    p_help.set_defaults(func=cmd_help)

    # Parse and execute
    args = parser.parse_args()

    try:
        # If no command provided, show help
        if len(sys.argv) == 1:
            mode = "menu"
            system_name = cmd_welcome()
            while True:
                if system_name == "exit":
                    print("\nExiting system. Good bye!\n")
                    sys.exit(0)
        elif len(sys.argv) == 2:
            mode = "shell"
            system_name = sys.argv[1]
        else:
            mode = "direct"
            system_name = sys.argv[1]
            command_args = sys.argv[2:]

        args.func(args)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
