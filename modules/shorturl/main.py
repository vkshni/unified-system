# Shorturl Entry Point

# Libraries
import sys
from pathlib import Path
import argparse

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from modules.shorturl.engine import URLService
from shared.ui_utils import print_error, print_success, print_table, confirm
from shared.validators import validate_url

# Data Path
DATA_DIR = Path(__file__).parent / "data"
URL_FILE_PATH = DATA_DIR / "urls.json"

# Initialize URL Service manager
url_service = URLService(URL_FILE=URL_FILE_PATH)

# Date format
DATE_FORMAT = "%d-%m-%YT%H:%M:%S"

# COMMANDS

# Shorten command
def cmd_shorten(args):
    """Handle shorten command"""

    if not args:
        print_error(f"No arguments passed")
        return 2
    
    # Parser Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("long_url", type=str)

    parsed = parser.parse_args(args[1:])

    # Execute
    existing = url_service.db.find_by_url(parsed.long_url)
    if existing:
        print_success(f"Already shortened: short.ly/{existing.short_code}")
        return 0
    else:
        is_valid, error_msg = validate_url(parsed.long_url)
        if is_valid:
            short_code = url_service.shorten(parsed.long_url)
            print_success(f"Created: short.ly/{short_code}")
            return 0
        else:
            print_error(error_msg)
            return 0

# Resolve command
def cmd_resolve(args):
    """Handle resolve command"""
    if not args:
        print_error(f"No arguments passed")
        return 2
    
    # Parser Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("short_code", type=str)

    parsed = parser.parse_args(args[1:])

    # Execute
    existing = url_service.db.find_by_code(parsed.short_code)
    if existing:
        print_success(f"→ {existing.long_url}")
        return 0
    else:
        print_error(f"URL with short code '{parsed.short_code}' not found")
        return 0

# List command
def cmd_list():
    """Handle list command"""
    urls = url_service.list_all()
    
    if not urls:
        print("\nNo URLs shortened yet.")
        print("Get started: python main.py shorten \"https://example.com\"\n")
        return 0
    formatted_data = [
        [
            url.to_dict()["long_url"],
            url.to_dict()["short_code"],
            url.to_dict()["visit_count"],
            url.to_dict()["created_at"]
        ]
        for url in urls
    ]
    headers = [
        "long_url",
        "short_code",
        "visit_count",
        "created_at"
    ]

    print("\n Available URLs \n")
    print_table(headers, formatted_data)
    print()
    print_success(f"Total {len(urls)} URL(s) fetched")
    return 0

# Run shell
def run_shell():

    print_success("Entering URL Shortener")
    print("Commands: shorten, resolve, list")

    while True:

        try:

            user_input = input("[shorturl] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            if command == "exit":
                if confirm("\nExit shorturl?"):
                    print("\n👋 Exiting shorturl!\n")
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
        if command == "shorten":
            return cmd_shorten(args)
        
        elif command == "resolve":
            return cmd_resolve(args)
        
        elif command == "list":
            return cmd_list()
        
        else:
            print_error(f"Command '{command}' doesn't exit")
            print("Commands: shorten, resolve, list")
            return 1

    except Exception as e:
        print_error(f"Error: {e}")
        return 1


if __name__ == "__main__":

    run_shell()


# Main parser
def main():
    
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="URL Shortener CLI - Shorten and manage URLs",
        epilog="""Examples:
  python main.py shorten "https://example.com/very/long/path"
  python main.py resolve aB3x9Z
  python main.py list

For detailed help on a specific command:
  python main.py <command> --help""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")
    sub.required = True

    # ========== SHORTEN COMMAND ==========
    p_shorten = sub.add_parser(
        "shorten",
        help="Create a short code for a long URL",
        description="Create a short code for a long URL",
        epilog="""Examples:
  Shorten a URL:
    python main.py shorten "https://github.com/user/repo"
    → ✓ Created: short.ly/aB3x9Z

  Shorten with query parameters:
    python main.py shorten "https://example.com/page?id=123&ref=home"
    → ✓ Created: short.ly/xY7mN2

  Get existing short code:
    python main.py shorten "https://github.com/user/repo"
    → ✓ Already shortened: short.ly/aB3x9Z

Notes:
  - URLs must include http:// or https://
  - Maximum URL length: 2000 characters
  - Short codes are case-sensitive
  - Duplicate URLs return the same short code""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_shorten.add_argument(
        "long_url",
        help="The long URL to shorten (must start with http:// or https://)"
    )
    p_shorten.set_defaults(func=cmd_shorten)

    # ========== RESOLVE COMMAND ==========
    p_resolve = sub.add_parser(
        "resolve",
        help="Retrieve the original URL from a short code",
        description="Retrieve the original URL from a short code",
        epilog="""Examples:
  Resolve a short code:
    python main.py resolve aB3x9Z
    → https://github.com/user/repo

  Use the resolved URL (Unix/macOS):
    python main.py resolve aB3x9Z | xargs open

  Use the resolved URL (Windows):
    python main.py resolve aB3x9Z | xargs start

Notes:
  - Short codes are exactly 6 characters
  - Short codes are case-sensitive (a-z, A-Z, 0-9)
  - Each resolve increments the visit counter
  - Use 'list' command to see all available short codes""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_resolve.add_argument(
        "short_code",
        help="The 6-character short code to resolve"
    )
    p_resolve.set_defaults(func=cmd_resolve)

    # ========== LIST COMMAND ==========
    p_list = sub.add_parser(
        "list",
        help="Display all shortened URLs with statistics",
        description="Display all shortened URLs with statistics",
        epilog="""Examples:
  View all URLs:
    python main.py list

  Output:
    #     LONG URL                                         SHORT CODE      CREATED AT                VISIT COUNT    
    --------------------------------------------------------------------------------------------------------------
    1     https://example.com/long/path                    aB3x9Z          14-03-2026T10:30:45       5              
    2     https://github.com/user/repo                     xY7mN2          14-03-2026T11:15:20       0              
    3     https://google.com                               kL9pQ1          14-03-2026T12:00:00       23             

Notes:
  - Sorted by creation date (newest first)
  - Visit count increments each time 'resolve' is called
  - Empty list shows "No URLs shortened yet" """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_list.set_defaults(func=cmd_list)

    # Parse arguments
    args = parser.parse_args()

    # Execute command with error handling
    try:
        args.func(args)
    except ValueError as e:
        # User input errors (validation failures)
        print(f"❌ {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        # File access errors
        print(f"❌ File error: {e}")
        print("Tip: Check if the data file exists or has correct permissions")
        sys.exit(1)
    except PermissionError as e:
        # Permission errors
        print(f"❌ Permission denied: {e}")
        print("Solution: Check file permissions or run with appropriate access")
        sys.exit(1)
    except KeyboardInterrupt:
        # User cancelled (Ctrl+C)
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        # Unexpected system errors
        print(f"💥 Unexpected error: {e}")
        print("This shouldn't happen. Please report this issue.")
        sys.exit(2)

