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
    return user_input


# help
def cmd_help(args):
    ui.print_header("UNIFIED CLI SYSTEM - HELP")
    print(
        """
USAGE:
  python main.py                    - Interactive menu mode
  python main.py <system>           - Enter system shell
  python main.py <system> <command> - Execute direct command
  python main.py init               - First-time setup
  python main.py help               - Show this help

AVAILABLE SYSTEMS:
"""
    )
    from config.systems import SYSTEMS

    for key, info in SYSTEMS.items():
        protected = "[AUTH]" if info["protected"] else "      "
        print(f"  {protected} {key:10} - {info['description']}")

    print(
        """
EXAMPLES:
  python main.py taski
  python main.py taski add "Fix bug"
  python main.py penny add 50 food
  python main.py shield
"""
    )


# Systems commands
def cmd_idgen():
    run_shell_mode("idgen")


# Menu mode
def run_menu_mode():

    from core.router import route_to_shell, system_exists

    while True:
        system_name = cmd_welcome()

        if system_name == "exit":
            print("\n👋 Goodbye!\n")
            sys.exit(0)

        if not system_name:
            continue
        if not system_exists(system_name):
            ui.print_error(f"System name '{system_name}' not found")
            continue

        # Route to system
        try:
            route_to_shell(system_name)
        except KeyboardInterrupt:
            print("\n")
            continue
        except Exception as e:
            ui.print_error(f"Error: {e}")
            continue


# Shell mode
def run_shell_mode(system_name):

    try:
        # route_to_shell(system_name)
        pass
    except ValueError as e:
        ui.print_error(e)
    except Exception as e:
        ui.print_error(e)


# Direct mode
def run_direct_mode():
    pass


def main():

    ui.clear_screen()

    parser = argparse.ArgumentParser(
        prog="main.py", description="Unified CLI System v1.0"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

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

    # ========== IDGEN ==========
    p_idgen = sub.add_parser("idgen", help="idgen")
    p_idgen.set_defaults(func=cmd_idgen)

    # If no argument, run menu mode
    if len(sys.argv) == 1:
        run_menu_mode()

    # Special commands
    elif sys.argv[1] in ["init", "help"]:

        # Parse and execute
        args = parser.parse_args()
        args.func(args)

    # System mode only, shell mode
    elif len(sys.argv) == 2:
        system_name = sys.argv[1]
        run_shell_mode(system_name)

    # System name + args, direct command mode
    else:
        system_name = sys.argv[1]
        command_args = sys.argv[2:]
        exit_code = run_direct_mode(system_name, command_args)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
