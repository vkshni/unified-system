"""
Snippet Entity - Core Data Model

This module defines the Snippet class, which represents a single code snippet
or note in the system. Each snippet contains metadata (title, tag, timestamps)
and content, along with state information (status, access level).

The Snippet class handles:
- Data validation on creation
- Serialization to/from dictionary format for JSON storage
- Automatic ID and timestamp generation
- Tag normalization (lowercase, space to underscore)
"""

# Libraries
import sys
from pathlib import Path
from datetime import datetime

# Adding project root to the python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.id_generator import generate_time_stamp_id

# Timestamp format for created_at field (DD-MM-YYYYTHH:MM:SS)
DATE_FORMAT = "%d-%m-%YT%H:%M:%S"


class Snippet:
    """
    Represents a single code snippet or note.

    A snippet is the core entity in the system, containing:
    - Unique identifier (auto-generated if not provided)
    - Title and content (both required)
    - Optional tag for categorization
    - Creation timestamp (auto-generated if not provided)
    - Status (ACTIVE or ARCHIVED)
    - Access level (PUBLIC or LOCKED)

    Attributes:
        snippet_id (str): Unique identifier (format: DDMMYYYY_NNNNN)
        title (str): Snippet title (1-100 characters)
        content (str): Snippet content (any length)
        tag (str): Category tag (lowercase, underscores for spaces)
        created_at (datetime): Creation timestamp
        status (str): ACTIVE or ARCHIVED
        access_level (str): PUBLIC or LOCKED

    Example:
        # Create a new snippet
        snippet = Snippet(
            title="Git Reset Hard",
            content="git reset --hard HEAD",
            tag="git",
            access_level="PUBLIC"
        )

        # Create a locked snippet
        secret = Snippet(
            title="API Key",
            content="sk-123456",
            tag="secrets",
            access_level="LOCKED"
        )
    """

    def __init__(
        self,
        title: str,
        content: str,
        tag: str = None,
        created_at: str = None,
        status: str = "ACTIVE",
        access_level: str = "PUBLIC",
        snippet_id: str = None,
    ):
        """
        Initialize a new snippet with validation.

        Args:
            title (str): Snippet title (required, 1-100 chars)
            content (str): Snippet content (required, any length)
            tag (str, optional): Category tag (will be normalized to lowercase)
            created_at (str, optional): ISO timestamp, auto-generated if None
            status (str): ACTIVE or ARCHIVED (default: ACTIVE)
            access_level (str): PUBLIC or LOCKED (default: PUBLIC)
            snippet_id (str, optional): Unique ID, auto-generated if None

        Raises:
            ValueError: If validation fails (empty title/content, invalid access level)

        Side Effects:
            - Generates unique ID if not provided
            - Normalizes tag to lowercase with underscores
            - Sets current timestamp if not provided
            - Validates all fields

        Note:
            The constructor calls validate() which may raise ValueError.
            Always handle this exception when creating snippets.
        """
        # Auto-generate ID if not provided (for new snippets)
        self.snippet_id = snippet_id if snippet_id else generate_time_stamp_id()

        # Store core data
        self.title = title
        self.content = content

        # Normalize tag: lowercase, default to "untagged" if None
        self.tag = tag.lower() if tag else "untagged"

        # Parse or generate timestamp
        self.created_at = (
            datetime.strptime(created_at, DATE_FORMAT) if created_at else datetime.now()
        )

        # Store state information
        self.status = status
        self.access_level = access_level.upper()  # Normalize to uppercase

        # Validate all fields
        self.validate()

    @classmethod
    def from_dict(cls, snippet_dict) -> "Snippet":
        """
        Create a Snippet object from a dictionary (deserialization).

        Used when loading snippets from JSON storage. Converts a dictionary
        representation back into a Snippet object.

        Args:
            snippet_dict (dict): Dictionary with snippet data (from JSON)

        Returns:
            Snippet: New Snippet object created from dictionary

        Required dict keys:
            - title (str)
            - content (str)
            - tag (str or None)
            - created_at (str in DATE_FORMAT)
            - status (str)
            - access_level (str)
            - snippet_id (str)

        Example:
            data = {
                "snippet_id": "22032026_00001",
                "title": "Git Reset",
                "content": "git reset --hard HEAD",
                "tag": "git",
                "created_at": "22-03-2026T10:30:00",
                "status": "ACTIVE",
                "access_level": "PUBLIC"
            }
            snippet = Snippet.from_dict(data)

        Note:
            This is the inverse of to_dict() - they should be symmetric.
        """
        return cls(
            title=snippet_dict["title"],
            content=snippet_dict["content"],
            tag=snippet_dict["tag"],
            created_at=snippet_dict["created_at"],
            status=snippet_dict["status"],
            access_level=snippet_dict["access_level"],
            snippet_id=snippet_dict["snippet_id"],
        )

    def to_dict(self) -> dict:
        """
        Convert snippet to dictionary format (serialization).

        Used when saving snippets to JSON storage. Converts the Snippet
        object into a dictionary that can be JSON-serialized.

        Returns:
            dict: Dictionary representation of the snippet

        Dictionary structure:
            {
                "snippet_id": str,
                "title": str,
                "content": str,
                "tag": str,
                "created_at": str (formatted timestamp),
                "status": str,
                "access_level": str
            }

        Example:
            snippet = Snippet("Title", "Content", "python")
            data = snippet.to_dict()
            # Save data to JSON file

        Note:
            - created_at is converted from datetime to string
            - All other fields are stored as-is
            - This is the inverse of from_dict()
        """
        return {
            "snippet_id": self.snippet_id,
            "title": self.title,
            "content": self.content,
            "tag": self.tag,
            "created_at": self.created_at.strftime(DATE_FORMAT),
            "status": self.status,
            "access_level": self.access_level,
        }

    def validate(self):
        """
        Validate all snippet fields and normalize tag format.

        Performs comprehensive validation on all user-provided fields:
        - Title: Not empty, max 100 characters
        - Content: Not empty
        - Tag: Spaces replaced with underscores
        - Access level: Must be PUBLIC or LOCKED

        Raises:
            ValueError: If any validation check fails

        Side Effects:
            - Normalizes tag by replacing spaces with underscores

        Validation Rules:
            Title:
                - Cannot be empty or whitespace-only
                - Maximum 100 characters

            Content:
                - Cannot be empty or whitespace-only
                - No maximum length restriction

            Tag:
                - Spaces automatically converted to underscores
                - Already normalized to lowercase in __init__

            Access Level:
                - Must be exactly "PUBLIC" or "LOCKED"
                - Case-insensitive (normalized to uppercase in __init__)

        Example:
            # Valid snippet - passes validation
            snippet = Snippet("Title", "Content", "my tag")
            # tag is normalized to "my_tag"

            # Invalid snippet - raises ValueError
            snippet = Snippet("", "Content")  # Empty title

        Note:
            This method is called automatically by __init__().
            You typically don't need to call it manually.
        """
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")

        if len(self.title) > 100:
            raise ValueError("Title length exceeded")

        # Validate content
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")

        # Normalize tag: replace spaces with underscores
        if self.tag:
            self.tag = self.tag.replace(" ", "_")

        # Validate access level
        if self.access_level not in ["PUBLIC", "LOCKED"]:
            raise ValueError("Access level can be only PUBLIC or LOCKED")

    def __str__(self):
        """
        String representation of snippet (for debugging).

        Returns:
            str: Human-readable snippet representation

        Example:
            >>> snippet = Snippet("Git Reset", "content", "git")
            >>> print(snippet)
            Snippet[22032026_00001]: Git Reset (git)
        """
        return f"Snippet[{self.snippet_id}]: {self.title} ({self.tag})"

    def __repr__(self):
        """
        Developer-friendly representation of snippet.

        Returns:
            str: Detailed snippet representation for debugging

        Example:
            >>> snippet = Snippet("Git Reset", "content", "git")
            >>> repr(snippet)
            "Snippet(id='22032026_00001', title='Git Reset', tag='git', status='ACTIVE')"
        """
        return (
            f"Snippet(id='{self.snippet_id}', title='{self.title}', "
            f"tag='{self.tag}', status='{self.status}')"
        )
