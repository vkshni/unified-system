"""
Snippet Manager - Core Business Logic Layer

This module provides the main SnippetManager class that orchestrates all
snippet operations including CRUD, filtering, searching, and state management.

It acts as the intermediary between the CLI interface and the storage/security layers,
implementing business logic and validation rules.
"""

# Libraries
from pathlib import Path
import sys

# Adding project root to the python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from modules.snippet.storage import SnippetDB
from modules.snippet.entity import Snippet
from auth.auth_manager import AuthService

# Base directory - parent directory of this file
SNIPPET_DIR = Path(__file__).parent

DATA_DIR = SNIPPET_DIR / "data"
SNIPPET_FILE_PATH = DATA_DIR / "snippets.json"


class SnippetManager:
    """
    Main manager class for snippet operations.

    Handles all business logic for managing code snippets including:
    - Adding and retrieving snippets
    - Filtering by tag and status
    - Searching by keyword
    - State transitions (archive/unarchive)
    - Access control (lock/unlock)

    Attributes:
        snippet_db (SnippetDB): Database handler for snippet persistence
        auth (AuthService): Authentication service for password management
    """

    def __init__(
        self,
        SNIPPET_FILE=SNIPPET_FILE_PATH,
    ):
        """
        Initialize the snippet manager with database and auth services.

        Args:
            SNIPPET_FILE (str): Filename for snippet storage (default: snippets.json)
            CONFIG_FILE (str): Filename for config storage (default: config.json)
            ATTEMPTS_FILE (str): Filename for login attempts tracking (default: attempts.json)
        """
        self.snippet_db = SnippetDB(SNIPPET_FILE)
        self.auth = AuthService()

    def add_snippet(self, title, content, tag=None, access_level="PUBLIC"):
        """
        Add a new snippet to the database.

        Creates a snippet with automatic ID generation and timestamp.
        Validates input and normalizes tag format (lowercase, underscores).

        Args:
            title (str): Snippet title (1-100 characters, required)
            content (str): Snippet content (required)
            tag (str, optional): Category tag (lowercase, no spaces)
            access_level (str): PUBLIC or LOCKED (default: PUBLIC)

        Returns:
            Snippet: The created snippet object with generated ID

        Raises:
            ValueError: If validation fails (empty title/content, invalid access level)

        Example:
            snippet = manager.add_snippet("Git Reset", "git reset --hard HEAD", tag="git")
        """
        # Validate title
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        if len(title) > 100:
            raise ValueError("Title too long (max 100 characters)")

        # Validate content
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        # Normalize and validate tag
        if tag:
            tag = tag.lower().replace(" ", "_")
            if len(tag) > 20:
                raise ValueError("Tag too long (max 20 characters)")

        # Validate access level
        if access_level not in ["PUBLIC", "LOCKED"]:
            raise ValueError("Access level must be PUBLIC or LOCKED")

        # Create and persist snippet
        snippet_obj = Snippet(title.strip(), content, tag, access_level=access_level)
        self.snippet_db.add_snippet(snippet_obj)

        return snippet_obj

    def list_all(self, status="ACTIVE"):
        """
        List all snippets with the specified status.

        Args:
            status (str): Filter by status - ACTIVE or ARCHIVED (default: ACTIVE)

        Returns:
            list[Snippet]: List of snippets matching the status filter

        Example:
            active_snippets = manager.list_all(status="ACTIVE")
            archived_snippets = manager.list_all(status="ARCHIVED")
        """
        snippets = self.snippet_db.get_all()
        filtered = [s for s in snippets if s.status == status]
        return filtered

    def list_by_tag(self, tag=None, status="ACTIVE"):
        """
        List snippets filtered by tag and status.

        Combines tag and status filtering to return only snippets that match both criteria.
        Tag comparison is case-insensitive.

        Args:
            tag (str, optional): Tag to filter by (case-insensitive)
            status (str): Filter by status - ACTIVE or ARCHIVED (default: ACTIVE)

        Returns:
            list[Snippet]: List of snippets matching both tag and status

        Example:
            python_snippets = manager.list_by_tag(tag="python")
            archived_git = manager.list_by_tag(tag="git", status="ARCHIVED")
        """
        snippets = self.snippet_db.get_all()
        filtered = [
            s for s in snippets if s.tag == tag.lower() and s.status == status.upper()
        ]
        return filtered

    def get_snippet_by_title(self, title, status="ACTIVE"):
        """
        Find snippets by exact title match (case-insensitive).

        Args:
            title (str): Title to search for (case-insensitive)
            status (str): Filter by status (default: ACTIVE)

        Returns:
            list[Snippet]: List of snippets with matching title

        Raises:
            ValueError: If no snippets exist or none match the title

        Note:
            Returns a list because multiple snippets can have the same title.
        """
        snippets = self.snippet_db.get_all()
        if not snippets:
            raise ValueError("No snippets found")

        filtered = [
            s
            for s in snippets
            if s.title.lower() == title.lower() and s.status == status
        ]

        if not filtered:
            raise ValueError(f"Snippet with title '{title}' not found")

        return filtered

    def get_snippet_by_id(self, snippet_id: str):
        """
        Retrieve a specific snippet by its unique ID.

        Args:
            snippet_id (str): Unique snippet identifier (format: DDMMYYYY_NNNNN)

        Returns:
            Snippet or None: The snippet if found, None otherwise

        Raises:
            ValueError: If no snippets exist in the database

        Example:
            snippet = manager.get_snippet_by_id("22032026_00001")
            if snippet:
                print(snippet.title)
        """
        snippets = self.snippet_db.get_all()
        if not snippets:
            raise ValueError("No snippets found")

        # Linear search through snippets
        for s in snippets:
            if s.snippet_id == snippet_id:
                return s

        return None

    def archive_snippet(self, snippet_id: str):
        """
        Archive a snippet (change status from ACTIVE to ARCHIVED).

        Archived snippets are hidden from default listings but can be
        retrieved with status="ARCHIVED" filter.

        Args:
            snippet_id (str): ID of snippet to archive

        Returns:
            bool: True if successfully archived

        Raises:
            ValueError: If snippet not found or already archived

        Example:
            manager.archive_snippet("22032026_00001")
        """
        snippet = self.get_snippet_by_id(snippet_id)

        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # Guard: check if already archived
        if snippet.status == "ARCHIVED":
            raise ValueError(f"Snippet with ID '{snippet_id}' already archived")

        # Update status and persist
        snippet.status = "ARCHIVED"
        self.snippet_db.update_snippet(snippet)

        return True

    def unarchive_snippet(self, snippet_id: str):
        """
        Restore an archived snippet (change status from ARCHIVED to ACTIVE).

        Args:
            snippet_id (str): ID of snippet to unarchive

        Returns:
            bool: True if successfully restored

        Raises:
            ValueError: If snippet not found or already active

        Example:
            manager.unarchive_snippet("22032026_00001")
        """
        snippet = self.get_snippet_by_id(snippet_id)

        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # Guard: check if already active
        if snippet.status == "ACTIVE":
            raise ValueError(f"Snippet with ID '{snippet_id}' already unarchived")

        # Update status and persist
        snippet.status = "ACTIVE"
        self.snippet_db.update_snippet(snippet)

        return True

    def lock_snippet(self, snippet_id: str):
        """
        Lock a snippet to require password for viewing.

        Changes access level from PUBLIC to LOCKED. Locked snippets
        require master password verification before content can be viewed.

        Args:
            snippet_id (str): ID of snippet to lock

        Returns:
            bool: True if successfully locked

        Raises:
            ValueError: If snippet not found or already locked

        Example:
            manager.lock_snippet("22032026_00001")
        """
        snippet = self.get_snippet_by_id(snippet_id)
        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # Guard: check if already locked
        if snippet.access_level == "LOCKED":
            raise ValueError(f"Snippet with ID '{snippet_id}' already locked")

        # Update access level and persist
        snippet.access_level = "LOCKED"
        self.snippet_db.update_snippet(snippet)

        return True

    def unlock_snippet(self, snippet_id: str):
        """
        Unlock a snippet to make it publicly viewable.

        Changes access level from LOCKED to PUBLIC. Public snippets
        can be viewed without password verification.

        Args:
            snippet_id (str): ID of snippet to unlock

        Returns:
            bool: True if successfully unlocked

        Raises:
            ValueError: If snippet not found or already public

        Note:
            This method does not require password verification.
            Password check should be done in the CLI layer before calling this.

        Example:
            manager.unlock_snippet("22032026_00001")
        """
        snippet = self.get_snippet_by_id(snippet_id)
        if not snippet:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # Guard: check if already unlocked
        if snippet.access_level == "PUBLIC":
            raise ValueError(f"Snippet with ID '{snippet_id}' already unlocked")

        # Update access level and persist
        snippet.access_level = "PUBLIC"
        self.snippet_db.update_snippet(snippet)

        return True

    def search_snippet(self, keyword: str, status: str = "ACTIVE"):
        """
        Search snippets by keyword in title or tag.

        Performs case-insensitive partial matching on both title and tag fields.
        Only searches within snippets of the specified status.

        Args:
            keyword (str): Search term (case-insensitive)
            status (str): Filter by status (default: ACTIVE)

        Returns:
            list[Snippet]: List of snippets matching the keyword

        Example:
            # Find all snippets with "docker" in title or tag
            results = manager.search_snippet("docker")

            # Search in archived snippets
            archived_results = manager.search_snippet("python", status="ARCHIVED")
        """
        snippets = self.snippet_db.get_all()

        filtered = list()
        for s in snippets:
            # Check status and keyword match in title or tag
            if s.status == "ACTIVE" and (
                keyword.lower() in s.title.lower()
                or (s.tag and keyword.lower() in s.tag.lower())
            ):
                filtered.append(s)

        return filtered

    def is_archived(self, snippet: Snippet):
        """
        Check if a snippet is archived.

        Args:
            snippet (Snippet): Snippet object to check

        Returns:
            bool: True if snippet is archived, False otherwise
        """
        return snippet.status == "ARCHIVED"

    def is_locked(self, snippet: Snippet):
        """
        Check if a snippet is locked (password-protected).

        Args:
            snippet (Snippet): Snippet object to check

        Returns:
            bool: True if snippet requires password, False otherwise
        """
        return snippet.access_level == "LOCKED"


if __name__ == "__main__":

    sm = SnippetManager()

    # print(sm.list_all())
