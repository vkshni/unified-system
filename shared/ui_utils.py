# UI utils
from os import system
from colorama import init, Fore
from tabulate import tabulate

from validators import validate_choice


def clear_screen():

    system(command="cls")


def print_header(title: str, width=30):

    print("╔" + "═" * width + "╗")
    print("║" + title.center(width) + "║")
    print("╚" + "═" * width + "╝")


def print_subheader(text, width=30):

    print("─" * width)
    print(text)
    print("─" * width)


def get_choice(prompt, choices):

    if validate_choice(prompt, valid_choices=choices):
        pass


def confirm(message):

    user_input = input(f"Confirm ({message}): ")
    if user_input.lower() in ["y", "yes"]:
        return True
    elif user_input.lower() in ["n", "no"]:
        return False


def print_success(message):

    init(autoreset=True)
    print(Fore.GREEN + f"✓ {message}")


def print_error(message):

    init(autoreset=True)
    print(Fore.RED + f"✗ {message}")


def print_table(headers: list, rows: list[list]):

    print(tabulate(rows, headers=headers, tablefmt="grid"))


if __name__ == "__main__":
    clear_screen()
    print_header("SNIPPET MANAGER")
    print_subheader("Add new task")
    print_success("Task added successfully")
    print_error("Invalid Input")
    headers = ["ID", "Name", "Age"]
    rows = [[1, "Vijay", 20], [2, "Eran", 30]]
    print_table(headers, rows)
    # print(confirm("Delete this task?"))
