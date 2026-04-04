# Shorturl Entry Point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Project modules
from modules.shorturl.engine import URLService
from shared.ui_utils import print_error, print_success, print_table, confirm
from shared.validators import validate_url

# Data Path
DATA_DIR = Path(__file__).parent / "data"
URL_FILE_PATH = DATA_DIR / "urls.json"

# Initialize URL Service
url_service = URLService(URL_FILE=URL_FILE_PATH)


# ========== COMMANDS ==========


def cmd_shorten(args):
    """Shorten a URL"""
    if len(args) < 2:
        print_error("Usage: shorten <url>")
        return 2

    long_url = args[1]

    try:
        # Validate URL
        is_valid, error_msg = validate_url(long_url)
        if not is_valid:
            print_error(error_msg)
            return 1

        # Check if already exists
        existing = url_service.db.find_by_url(long_url)
        if existing:
            print_success(f"Already shortened: short.ly/{existing.short_code}")
            return 0

        # Create new short URL
        short_code = url_service.shorten(long_url)
        print_success(f"Created: short.ly/{short_code}")
        return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_resolve(args):
    """Resolve a short code to original URL"""
    if len(args) < 2:
        print_error("Usage: resolve <short_code>")
        return 2

    short_code = args[1]

    try:
        existing = url_service.db.find_by_code(short_code)
        if existing:
            print_success(f"→ {existing.long_url}")
            return 0
        else:
            print_error(f"Short code '{short_code}' not found")
            return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_list():
    """List all shortened URLs"""
    try:
        urls = url_service.list_all()

        if not urls:
            print("\nNo URLs shortened yet.")
            print('Get started: shorten "https://example.com"\n')
            return 0

        formatted_data = [
            [
                url.to_dict()["short_code"],
                (
                    url.to_dict()["long_url"][:50] + "..."
                    if len(url.to_dict()["long_url"]) > 50
                    else url.to_dict()["long_url"]
                ),
                url.to_dict()["visit_count"],
                url.to_dict()["created_at"],
            ]
            for url in urls
        ]

        headers = ["Short Code", "Long URL", "Visits", "Created"]

        print("\n Shortened URLs \n")
        print_table(headers, formatted_data)
        print()
        print_success(f"Total {len(urls)} URL(s)")
        return 0

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_help():
    """Show help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║                  SHORTURL - URL Shortener                      ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  shorturl <command> [options]

COMMANDS:
  shorten <url>                       Shorten a long URL
  resolve <short_code>                Get original URL from short code
  list                                List all shortened URLs
  help                                Show this help message
  exit                                Exit shorturl

EXAMPLES:
  shorturl shorten "https://example.com/very/long/path"
  shorturl resolve abc123
  shorturl list

NOTES:
  - URLs must start with http:// or https://
  - Short codes are automatically generated
  - Duplicate URLs return the existing short code
"""
    print(help_text)
    return 0


# ========== SHELL & EXECUTION ==========


def run_shell():
    """Interactive shell mode"""
    print_success("Entering URL Shortener")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("[shorturl] ").strip()
            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)  # Split only on first space
            command = parts[0]

            if command == "exit":
                if confirm("Exit shorturl?"):
                    print("\n👋 Exiting shorturl!\n")
                    break
                else:
                    continue

            result = execute_command(parts)

            if result != 0 and result != 2:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            if confirm("Exit shorturl?"):
                print("\n👋 Exiting shorturl!\n")
                break
        except Exception as e:
            print_error(f"Error: {e}")


def execute_command(args):
    """Execute a command"""
    if not args:
        return 1

    command = args[0].lower()

    try:
        if command == "shorten":
            return cmd_shorten(args)
        elif command == "resolve":
            return cmd_resolve(args)
        elif command == "list":
            return cmd_list()
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
