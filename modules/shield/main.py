# Shield Entry Point - Password Manager

# Libraries
import sys
from pathlib import Path
import argparse
import getpass

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project modules
from modules.shield.engine import Vault
from shared.ui_utils import print_error, print_success, print_table, confirm

# Data Path
DATA_DIR = Path(__file__).parent / "data"

# Initialize Vault (lazy loading)
_vault = None


def get_vault():
    """Lazy initialization of Vault"""
    global _vault
    if _vault is None:
        _vault = Vault()
    return _vault


# ========== COMMANDS ==========


def cmd_add(args):
    """Add a new password"""
    if len(args) < 7:
        print_error(
            "Usage: add --service <name> --username <user> --password <pass> [--label <label>]"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--service", required=True)
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--label", default="default")

        parsed = parser.parse_args(args[1:])

        vault = get_vault()
        vault.add_credential(
            parsed.service, parsed.username, parsed.password, label=parsed.label
        )

        print_success(f"Password added: {parsed.service}/{parsed.label}")
        return 0

    except ValueError as e:
        print_error(f"Validation error: {e}")
        return 1
    except PermissionError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_list():
    """List all stored services"""
    try:
        vault = get_vault()
        services = vault.list_services()

        if not services:
            print(
                "\nNo passwords stored yet.\nAdd one with: add --service github --username user --password pass\n"
            )
            return 0

        formatted_data = [[s[0], s[1]] for s in services]
        headers = ["Service", "Label"]

        print("\n Stored Passwords \n")
        print_table(headers, formatted_data)
        print()
        print_success(f"Total {len(services)} password(s)")
        return 0

    except PermissionError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_get(args):
    """Get a password"""
    if len(args) < 2:
        print_error("Usage: get <service> [--label <label>]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("service")
        parser.add_argument("--label", default="default")

        parsed = parser.parse_args(args[1:])

        vault = get_vault()

        # Check if password verification is needed
        from auth.auth_manager import AuthService

        auth = AuthService()

        print(f"\n🔒 Viewing password for: {parsed.service}/{parsed.label}")
        user_password = getpass.getpass("Enter master password to view: ")

        if not auth.verify(user_password):
            print_error("Wrong password")
            return 1

        credential = vault.get_credential(parsed.service, parsed.label)

        if not credential:
            print_error(f"Password not found: {parsed.service}/{parsed.label}")
            return 1

        print(f"\nService:  {credential.service_name}")
        print(f"Label:    {credential.label}")
        print(f"Username: {credential.username}")
        print(f"Password: {credential.password}")
        print(f"Created:  {credential.created_at.strftime('%d-%m-%Y %H:%M:%S')}")
        if credential.updated_at:
            print(f"Updated:  {credential.updated_at.strftime('%d-%m-%Y %H:%M:%S')}")
        print()

        return 0

    except PermissionError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_update(args):
    """Update a password"""
    if len(args) < 2:
        print_error(
            "Usage: update <service> [--label <label>] [--username <user>] [--password <pass>]"
        )
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("service")
        parser.add_argument("--label", default="default")
        parser.add_argument("--new-service")
        parser.add_argument("--new-label")
        parser.add_argument("--username")
        parser.add_argument("--password")

        parsed = parser.parse_args(args[1:])

        # Check if any update provided
        if not any(
            [parsed.new_service, parsed.new_label, parsed.username, parsed.password]
        ):
            print_error("Nothing to update. Specify at least one option")
            return 1

        vault = get_vault()
        vault.update_credential(
            parsed.service,
            label=parsed.label,
            new_service_name=parsed.new_service,
            new_label=parsed.new_label,
            new_username=parsed.username,
            new_password=parsed.password,
        )

        print_success(f"Password updated: {parsed.service}/{parsed.label}")
        return 0

    except ValueError as e:
        print_error(str(e))
        return 1
    except PermissionError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_delete(args):
    """Delete a password"""
    if len(args) < 2:
        print_error("Usage: delete <service> [--label <label>] [--force]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("service")
        parser.add_argument("--label", default="default")
        parser.add_argument("--force", action="store_true")

        parsed = parser.parse_args(args[1:])

        vault = get_vault()

        # Get credential to show what will be deleted
        credential = vault.get_credential(parsed.service, parsed.label)

        if not credential:
            print_error(f"Password not found: {parsed.service}/{parsed.label}")
            return 1

        if not parsed.force:
            print(f"\n⚠️  About to delete:")
            print(f"  Service:  {credential.service_name}")
            print(f"  Label:    {credential.label}")
            print(f"  Username: {credential.username}")

            if not confirm("Delete this password?"):
                print("Cancelled")
                return 0

        vault.delete_credential(parsed.service, parsed.label)
        print_success(f"Password deleted: {parsed.service}/{parsed.label}")
        return 0

    except ValueError as e:
        print_error(str(e))
        return 1
    except PermissionError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_help():
    """Show help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║              SHIELD - Password Manager                         ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  shield <command> [options]

COMMANDS:
  add <options>                      Add new password
  list                               List all services
  get <service> [--label <label>]    View password (requires verification)
  update <service> <options>         Update password
  delete <service> [--label <label>] Delete password
  help                               Show this help
  exit                               Exit shield

ADD OPTIONS:
  --service <name>                   Service name (e.g., github)
  --username <user>                  Username or email
  --password <pass>                  Password
  --label <label>                    Account label (default: default)

UPDATE OPTIONS:
  --new-service <name>               Rename service
  --new-label <label>                Rename label
  --username <user>                  Update username
  --password <pass>                  Update password

EXAMPLES:
  shield add --service github --username john --password pass123
  shield add --service gmail --username john@gmail.com --password abc --label personal
  shield list
  shield get github
  shield get gmail --label personal
  shield update github --password newpass123
  shield delete github --force

NOTES:
  - Master password required to view passwords
  - Service + label combination must be unique
  - All comparisons are case-insensitive
"""
    print(help_text)
    return 0


# ========== SHELL & EXECUTION ==========


def run_shell():
    """Interactive shell mode"""
    print_success("Entering Shield - Password Manager")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("[shield] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]

            if command == "exit":
                if confirm("Exit shield?"):
                    print("\n👋 Exiting shield!\n")
                    break
                else:
                    continue

            result = execute_command(parts)

            if result != 0 and result != 2:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            if confirm("Exit shield?"):
                print("\n👋 Exiting shield!\n")
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
        elif command == "get":
            return cmd_get(args)
        elif command == "update":
            return cmd_update(args)
        elif command == "delete":
            return cmd_delete(args)
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
