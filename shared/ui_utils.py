from os import system
from colorama import init, Fore
from tabulate import tabulate


def clear_screen():
    system("cls")  # Or: system("cls" if os.name == "nt" else "clear")


def print_header(title: str, width=30):
    print("╔" + "═" * width + "╗")
    print("║" + title.center(width) + "║")
    print("╚" + "═" * width + "╝")


def print_subheader(text, width=30):
    print("─" * width)
    print(text)
    print("─" * width)


def get_input(prompt, validator=None, default=None):
    """Get validated input from user"""
    while True:
        user_input = input(prompt).strip()

        if user_input == "" and default is not None:
            return default

        if validator is None:
            if user_input:
                return user_input
            print_error("Input cannot be empty")
            continue

        is_valid, result = validator(user_input)
        if is_valid:
            return result if result else user_input

        print_error(result)


def get_choice(prompt, choices):
    """Prompt until user enters valid choice"""
    from validators import validate_choice

    while True:
        user_input = input(prompt).strip()
        is_valid, error_msg = validate_choice(user_input, choices)

        if is_valid:
            return user_input

        print_error(error_msg)


def confirm(message, default=False):
    """Ask yes/no confirmation"""
    prompt_text = f"{message} [Y/n]: " if default else f"{message} [y/N]: "

    while True:
        user_input = input(prompt_text).strip().lower()

        if user_input == "":
            return default
        elif user_input in ["y", "yes"]:
            return True
        elif user_input in ["n", "no"]:
            return False
        else:
            print_error("Please enter y/yes or n/no")


def print_success(message):
    init(autoreset=True)
    print(Fore.GREEN + f"✓ {message}")


def print_error(message):
    init(autoreset=True)
    print(Fore.RED + f"✗ {message}")


def print_table(headers: list, rows: list[list]):
    print(tabulate(rows, headers=headers, tablefmt="grid"))
