# Snippet Entry Point

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
from modules.snippet.engine import SnippetManager
from shared.ui_utils import print_error, print_success, print_table, confirm

# Data Path
DATA_DIR = Path(__file__).parent / "data"

# Initialize Snippet Manager (lazy loading)
_sm = None


def get_sm():
    """Lazy initialization of SnippetManager"""
    global _sm
    if _sm is None:
        _sm = SnippetManager()
    return _sm


# ========== HELPER FUNCTIONS ==========

def display_snippet(snippet):
    """Display full snippet details"""
    lock_indicator = "🔒 LOCKED" if snippet.access_level == "LOCKED" else "PUBLIC"
    created = snippet.created_at.strftime("%d/%m/%Y %H:%M:%S")

    print("\n" + "━" * 70)
    print(f"\n  {snippet.title}\n")
    print(f"  ID:      {snippet.snippet_id}")
    print(f"  Tag:     {snippet.tag if snippet.tag else '-'}")
    print(f"  Status:  {snippet.status}")
    print(f"  Access:  {lock_indicator}")
    print(f"  Created: {created}")
    print("\n" + "━" * 70 + "\n")
    print(snippet.content)
    print("\n" + "━" * 70 + "\n")


def handle_password_verification(snippet, action="view"):
    """Handle password verification for locked snippets"""
    from auth.auth_manager import AuthService
    
    print(f"\n🔒 This snippet is LOCKED")
    print(f"   Title: {snippet.title}")
    print(f"   Enter master password to {action}\n")

    MAX_ATTEMPTS = 3
    retry = 1

    auth = AuthService()

    while retry <= MAX_ATTEMPTS:
        try:
            user_password = getpass.getpass("Master password: ")
            if auth.verify_master(user_password):
                return True

        except ValueError as e:
            print_error(str(e))
            return False

        remaining = MAX_ATTEMPTS - retry
        if remaining > 0:
            print_error(f"Wrong password ({remaining} attempt{'s' if remaining > 1 else ''} remaining)")
        retry += 1

    print_error("Too many failed attempts")
    return False


# ========== COMMANDS ==========

def cmd_add(args):
    """Add a new snippet"""
    if len(args) < 3:
        print_error("Usage: add <title> <content> [--tag <tag>] [--access <PUBLIC|LOCKED>]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("title")
        parser.add_argument("content")
        parser.add_argument("--tag")
        parser.add_argument("--access", default="PUBLIC", choices=["PUBLIC", "LOCKED"])
        
        parsed = parser.parse_args(args[1:])
        
        sm = get_sm()
        snippet = sm.add_snippet(
            parsed.title,
            parsed.content,
            tag=parsed.tag,
            access_level=parsed.access
        )
        
        lock_msg = " 🔒" if parsed.access == "LOCKED" else ""
        print_success(f"Snippet added: {snippet.snippet_id}{lock_msg}")
        return 0
        
    except ValueError as e:
        print_error(f"Validation error: {e}")
        return 1
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_list(args):
    """List snippets"""
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--tag")
        parser.add_argument("--archived", action="store_true")
        
        parsed = parser.parse_args(args[1:])
        
        sm = get_sm()
        
        # Determine which snippets to show
        if parsed.tag:
            snippets = sm.list_by_tag(tag=parsed.tag.lower())
        elif parsed.archived:
            snippets = sm.list_all(status="ARCHIVED")
        else:
            snippets = sm.list_all(status="ACTIVE")
        
        if not snippets:
            if parsed.tag:
                print(f"\nNo snippets found with tag: {parsed.tag}\n")
            elif parsed.archived:
                print("\nNo archived snippets\n")
            else:
                print('\nNo snippets yet. Add one with: add "Title" "Content" --tag test\n')
            return 0
        
        # Display header
        if parsed.archived:
            print("\n📦 ARCHIVED SNIPPETS\n")
        else:
            print()
        
        # Prepare table data
        formatted_data = []
        for s in snippets:
            lock_indicator = "🔒" if s.access_level == "LOCKED" else ""
            tag_display = s.tag if s.tag else "-"
            title_display = s.title[:47] + "..." if len(s.title) > 50 else s.title
            
            formatted_data.append([
                s.snippet_id,
                title_display,
                tag_display,
                lock_indicator
            ])
        
        headers = ["ID", "Title", "Tag", "Access"]
        print_table(headers, formatted_data)
        
        status_text = "archived" if parsed.archived else "active"
        print()
        print_success(f"Total {len(snippets)} {status_text} snippet(s)")
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_search(args):
    """Search snippets by keyword"""
    if len(args) < 2:
        print_error("Usage: search <keyword>")
        return 2

    try:
        keyword = args[1]
        
        sm = get_sm()
        snippets = sm.search_snippet(keyword)
        
        if not snippets:
            print(f"\nNo snippets found for '{keyword}'\n")
            return 0
        
        print(f"\n🔍 Search results for '{keyword}':\n")
        
        formatted_data = []
        for s in snippets:
            lock_indicator = "🔒" if s.access_level == "LOCKED" else ""
            tag_display = s.tag if s.tag else "-"
            
            formatted_data.append([
                s.snippet_id,
                s.title[:47] + "..." if len(s.title) > 50 else s.title,
                tag_display,
                lock_indicator
            ])
        
        headers = ["ID", "Title", "Tag", "Access"]
        print_table(headers, formatted_data)
        print()
        print_success(f"Found {len(snippets)} snippet(s)")
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_view(args):
    """View snippet details"""
    if len(args) < 2:
        print_error("Usage: view <snippet_id>")
        return 2

    try:
        snippet_id = args[1]
        
        sm = get_sm()
        snippet = sm.get_snippet_by_id(snippet_id)
        
        if not snippet:
            print_error(f"Snippet not found: {snippet_id}")
            return 1
        
        # Handle locked snippets
        if sm.is_locked(snippet):
            if not handle_password_verification(snippet, action="view"):
                return 1
        
        display_snippet(snippet)
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_archive(args):
    """Archive a snippet"""
    if len(args) < 2:
        print_error("Usage: archive <snippet_id> [--force]")
        return 2

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("snippet_id")
        parser.add_argument("--force", action="store_true")
        
        parsed = parser.parse_args(args[1:])
        
        sm = get_sm()
        snippet = sm.get_snippet_by_id(parsed.snippet_id)
        
        if not snippet:
            print_error(f"Snippet not found: {parsed.snippet_id}")
            return 1
        
        if sm.is_archived(snippet):
            print_error("Snippet already archived")
            return 1
        
        if not parsed.force:
            if not confirm(f"Archive '{snippet.title}'?"):
                print("Cancelled")
                return 0
        
        sm.archive_snippet(parsed.snippet_id)
        print_success(f"Snippet archived: {parsed.snippet_id}")
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_unarchive(args):
    """Unarchive a snippet"""
    if len(args) < 2:
        print_error("Usage: unarchive <snippet_id>")
        return 2

    try:
        snippet_id = args[1]
        
        sm = get_sm()
        snippet = sm.get_snippet_by_id(snippet_id)
        
        if not snippet:
            print_error(f"Snippet not found: {snippet_id}")
            return 1
        
        if not sm.is_archived(snippet):
            print_error("Snippet is not archived")
            return 1
        
        if confirm(f"Unarchive '{snippet.title}'?"):
            sm.unarchive_snippet(snippet_id)
            print_success(f"Snippet restored: {snippet_id}")
        else:
            print("Cancelled")
        
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_lock(args):
    """Lock a snippet"""
    if len(args) < 2:
        print_error("Usage: lock <snippet_id>")
        return 2

    try:
        snippet_id = args[1]
        
        sm = get_sm()
        snippet = sm.get_snippet_by_id(snippet_id)
        
        if not snippet:
            print_error(f"Snippet not found: {snippet_id}")
            return 1
        
        if sm.is_locked(snippet):
            print_error("Snippet already locked 🔒")
            return 1
        
        if confirm(f"Lock '{snippet.title}'?"):
            sm.lock_snippet(snippet_id)
            print_success(f"Snippet locked 🔒: {snippet_id}")
            print("This snippet now requires master password to view")
        else:
            print("Cancelled")
        
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_unlock(args):
    """Unlock a snippet"""
    if len(args) < 2:
        print_error("Usage: unlock <snippet_id>")
        return 2

    try:
        snippet_id = args[1]
        
        sm = get_sm()
        snippet = sm.get_snippet_by_id(snippet_id)
        
        if not snippet:
            print_error(f"Snippet not found: {snippet_id}")
            return 1
        
        if not sm.is_locked(snippet):
            print_error("Snippet is not locked")
            return 1
        
        # Verify password before unlocking
        if handle_password_verification(snippet, action="unlock"):
            if confirm(f"Unlock '{snippet.title}'?"):
                sm.unlock_snippet(snippet_id)
                print_success(f"Snippet unlocked: {snippet_id}")
            else:
                print("Cancelled")
        
        return 0
        
    except Exception as e:
        print_error(f"Error: {e}")
        return 1


def cmd_help():
    """Show help message"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║              SNIPPET - Code Snippet Manager                    ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  snippet <command> [options]

COMMANDS:
  add <title> <content> [options]    Add new snippet
  list [--tag <tag>] [--archived]    List snippets
  search <keyword>                   Search snippets
  view <id>                          View snippet details
  archive <id> [--force]             Archive snippet
  unarchive <id>                     Restore archived snippet
  lock <id>                          Lock snippet (require password)
  unlock <id>                        Unlock snippet
  help                               Show this help
  exit                               Exit snippet

ADD OPTIONS:
  --tag <tag>                        Category tag (lowercase, no spaces)
  --access <PUBLIC|LOCKED>           Access level (default: PUBLIC)

LIST OPTIONS:
  --tag <tag>                        Filter by tag
  --archived                         Show archived snippets

EXAMPLES:
  snippet add "Git Reset" "git reset --hard HEAD" --tag git
  snippet add "API Key" "sk-123..." --tag secrets --access LOCKED
  snippet list
  snippet list --tag python
  snippet list --archived
  snippet search docker
  snippet view 19032026_00001
  snippet archive 19032026_00001
  snippet lock 19032026_00002
  snippet unlock 19032026_00002

ACCESS LEVELS:
  PUBLIC  - No password required
  LOCKED  - Master password required to view
"""
    print(help_text)
    return 0


# ========== SHELL & EXECUTION ==========

def run_shell():
    """Interactive shell mode"""
    print_success("Entering Snippet Manager")
    print("Type 'help' for available commands or 'exit' to quit")

    while True:
        try:
            user_input = input("[snippet] ").strip()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]

            if command == "exit":
                if confirm("Exit snippet?"):
                    print("\n👋 Exiting snippet!\n")
                    break
                else:
                    continue

            result = execute_command(parts)

            if result != 0 and result != 2:
                print_error("Command failed")

        except KeyboardInterrupt:
            print("\n")
            if confirm("Exit snippet?"):
                print("\n👋 Exiting snippet!\n")
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
            return cmd_list(args)
        elif command == "search":
            return cmd_search(args)
        elif command == "view":
            return cmd_view(args)
        elif command == "archive":
            return cmd_archive(args)
        elif command == "unarchive":
            return cmd_unarchive(args)
        elif command == "lock":
            return cmd_lock(args)
        elif command == "unlock":
            return cmd_unlock(args)
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