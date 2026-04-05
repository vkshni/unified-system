"""
Storage Manager - Data Persistence Layer

This module handles all file I/O operations for the snippet manager.
Provides abstraction over JSON file operations and manages three types of data:
- Snippets: User's code snippets and notes
- Config: Master password and security settings
- Attempts: Failed login attempt tracking

All data is stored in JSON format in the data/ directory.
"""

# Libraries
from pathlib import Path
import sys

# import json
# from datetime import datetime

# Adding project root to the python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.file_handler import JSONFile
from modules.snippet.entity import Snippet

# # Date format for counter file (DDMMYYYY)
# COUNTER_DATE_FORMAT = "%d%m%Y"

# Base directory - parent directory of this file
SNIPPET_DIR = Path(__file__).parent

DATA_DIR = SNIPPET_DIR / "data"
SNIPPET_FILE_PATH = DATA_DIR / "snippets.json"


# class JSONFile:
#     """
#     Generic JSON file handler for reading and writing JSON data.

#     Provides low-level file operations with automatic directory creation
#     and default empty structure initialization.

#     Attributes:
#         path (Path): Full path to the JSON file
#     """

#     def __init__(self, file_name):
#         """
#         Initialize JSON file handler.

#         Args:
#             file_name (str): Name of the JSON file (stored in data/ directory)
#         """
#         self.path = self.create(file_name)

#     def create(self, file_name):
#         """
#         Create JSON file if it doesn't exist and ensure data directory exists.

#         Creates the data/ directory if needed and initializes the file
#         with an empty JSON object {}.

#         Args:
#             file_name (str): Name of the JSON file

#         Returns:
#             Path: Full path to the created/existing file
#         """
#         path = BASE_DIR / "data" / file_name

#         # Create data directory if it doesn't exist (handles edge case)
#         path.parent.mkdir(exist_ok=True)

#         # Initialize file with empty JSON object if new
#         if not path.exists():
#             with open(path, "w") as f:
#                 json.dump({}, f)

#         return path

#     def read_all(self):
#         """
#         Read and parse the entire JSON file.

#         Returns:
#             dict or list: Parsed JSON data

#         Raises:
#             json.JSONDecodeError: If file contains invalid JSON
#             FileNotFoundError: If file doesn't exist
#         """
#         with open(self.path, "r") as f:
#             data = json.load(f)
#             return data

#     def write_all(self, data):
#         """
#         Write data to JSON file with pretty formatting.

#         Overwrites the entire file with new data. Uses 4-space indentation
#         for readability.

#         Args:
#             data (dict or list): Data to write (must be JSON-serializable)
#         """
#         with open(self.path, "w") as f:
#             json.dump(data, f, indent=4)


# class ConfigFile:
#     """
#     Configuration file manager for master password and security settings.

#     Stores:
#     - Master password hash (SHA-256)
#     - Hash algorithm identifier
#     - Creation timestamp
#     - Security settings (max attempts, lockout duration)

#     Attributes:
#         json_handler (JSONFile): Handler for config.json file
#     """

#     def __init__(self, CONFIG_FILE="config.json"):
#         """
#         Initialize configuration file handler.

#         Args:
#             CONFIG_FILE (str): Config filename (default: config.json)
#         """
#         self.json_handler = JSONFile(CONFIG_FILE)

#     def _initial_data(self):
#         """
#         Get default configuration structure.

#         Returns:
#             dict: Default config with empty password and security settings
#         """
#         return {
#             "password_hash": None,
#             "hash_algorithm": "sha256",
#             "created_at": None,
#             "security": {
#                 "max_attempts": 3,  # Failed attempts before lockout
#                 "lockout_duration": 30,  # Lockout duration in seconds
#             },
#         }

#     def initialize(self):
#         """
#         Initialize config file with default structure if empty or corrupted.

#         Creates a fresh config with default values if the file is empty
#         or cannot be read. Safe to call multiple times.
#         """
#         try:
#             data = self.json_handler.read_all()
#             if not data:
#                 self.json_handler.write_all(self._initial_data())
#         except:
#             # Handle any read errors by resetting to defaults
#             self.json_handler.write_all(self._initial_data())

#     def is_initialized(self):
#         """
#         Check if master password has been set.

#         Returns:
#             bool: True if password hash exists, False otherwise

#         Note:
#             Returns False on any error (file corruption, missing fields, etc.)
#         """
#         try:
#             if self.get_master_password_hash():
#                 return True
#             return False
#         except:
#             return False

#     def get_master_password_hash(self):
#         """
#         Retrieve the stored master password hash.

#         Returns:
#             str or None: SHA-256 hash of master password, or None if not set

#         Raises:
#             KeyError: If config structure is invalid
#         """
#         master_password_hash = self.json_handler.read_all()["password_hash"]
#         return master_password_hash


# class AttemptsFile:
#     """
#     Failed login attempts tracker for security lockout mechanism.

#     Tracks:
#     - Number of consecutive failed password attempts
#     - Lockout expiration timestamp (if locked out)

#     Used to prevent brute-force password attacks by locking the account
#     after a configurable number of failed attempts.

#     Attributes:
#         json_handler (JSONFile): Handler for attempts.json file
#     """

#     def __init__(self, ATTEMPTS_FILE="attempts.json"):
#         """
#         Initialize attempts tracking file.

#         Args:
#             ATTEMPTS_FILE (str): Attempts filename (default: attempts.json)
#         """
#         self.json_handler = JSONFile(ATTEMPTS_FILE)
#         self.initialize()

#     def initialize(self):
#         """
#         Initialize attempts file with default (unlocked) state.

#         Resets to zero failed attempts if file is empty or corrupted.
#         """
#         try:
#             data = self.json_handler.read_all()
#             if not data:
#                 self.reset()
#         except:
#             # Handle any errors by resetting
#             self.reset()

#     def reset(self):
#         """
#         Reset attempts counter and clear lockout.

#         Sets failed attempts to 0 and removes lockout timestamp.
#         Called after successful password verification or lockout expiry.

#         Returns:
#             bool: True on success
#         """
#         self.json_handler.write_all({"failed_attempts": 0, "locked_until": None})
#         return True

#     def update(self, failed_attempts=None, locked_until=None):
#         """
#         Update attempt tracking data.

#         Allows partial updates - only specified fields are modified.

#         Args:
#             failed_attempts (int, optional): New failed attempt count
#             locked_until (str, optional): ISO format timestamp for lockout expiry

#         Example:
#             # Increment attempts
#             attempts.update(failed_attempts=2)

#             # Set lockout
#             attempts.update(locked_until="22-03-2026T15:30:00")

#             # Update both
#             attempts.update(failed_attempts=3, locked_until="22-03-2026T15:30:00")
#         """
#         data = self.json_handler.read_all()

#         # Update only provided fields
#         if failed_attempts is not None:
#             data["failed_attempts"] = failed_attempts
#         if locked_until is not None:
#             data["locked_until"] = locked_until

#         self.json_handler.write_all(data)

#     def get_data(self):
#         """
#         Get current attempts tracking data.

#         Returns:
#             dict: Contains 'failed_attempts' (int) and 'locked_until' (str or None)

#         Example:
#             data = attempts.get_data()
#             print(data["failed_attempts"])  # 2
#             print(data["locked_until"])     # "22-03-2026T15:30:00" or None
#         """
#         data = self.json_handler.read_all()
#         return data


class SnippetDB:
    """
    Snippet database manager - handles CRUD operations for snippets.

    Stores all snippets in a JSON array. Each snippet is converted to/from
    dictionary format for persistence.

    Provides methods for:
    - Adding new snippets
    - Retrieving all snippets
    - Updating existing snippets
    - Deleting snippets

    Attributes:
        json_handler (JSONFile): Handler for snippets.json file
    """

    def __init__(self, SNIPPET_FILE="snippets.json"):
        """
        Initialize snippet database.

        Args:
            SNIPPET_FILE (str): Snippets filename (default: snippets.json)
        """
        self.json_handler = JSONFile(SNIPPET_FILE)
        self.initialize()

    def initialize(self):
        """
        Initialize snippets file with empty array if needed.

        Creates a fresh empty snippet list if file is empty or corrupted.
        """
        try:
            data = self.json_handler.read_json(default=[])
            if not data:
                self.json_handler.write_json([])
        except:
            # Handle any errors by creating empty array
            self.json_handler.write_all([])

    def add_snippet(self, snippet: Snippet):
        """
        Add a new snippet to the database.

        Converts snippet object to dictionary and appends to the JSON array.

        Args:
            snippet (Snippet): Snippet object to add

        Returns:
            bool: True on success

        Example:
            snippet = Snippet("Title", "Content", "tag")
            db.add_snippet(snippet)
        """
        # Load existing snippets
        snippets = self.json_handler.read_json(default=[])

        # Convert snippet object to dictionary
        snippet_dict = snippet.to_dict()

        # Append and save
        snippets.append(snippet_dict)
        self.json_handler.write_json(snippets)

        return True

    def get_all(self) -> list[Snippet]:
        """
        Retrieve all snippets from database.

        Reads JSON array and converts each dictionary back to a Snippet object.

        Returns:
            list[Snippet]: List of all snippet objects

        Example:
            snippets = db.get_all()
            for s in snippets:
                print(s.title)
        """
        # Read raw JSON data
        snippets = self.json_handler.read_json(default=[])

        if not snippets:
            return []

        # Convert dictionaries to Snippet objects
        snippet_objs = [Snippet.from_dict(s) for s in snippets]

        return snippet_objs

    def update_snippet(self, snippet: Snippet):
        """
        Update an existing snippet in the database.

        Finds snippet by ID and replaces it with updated version.
        Uses linear search to find matching snippet.

        Args:
            snippet (Snippet): Updated snippet object (must have valid snippet_id)

        Returns:
            bool: True if snippet was found and updated, False if not found

        Example:
            snippet = db.get_all()[0]
            snippet.title = "New Title"
            db.update_snippet(snippet)
        """
        snippets = self.json_handler.read_json(default=[])

        updated = False

        # Find and replace matching snippet
        for i, s in enumerate(snippets):
            if s["snippet_id"] == snippet.snippet_id:
                snippets[i] = snippet.to_dict()
                updated = True
                break

        # Save changes
        self.json_handler.write_json(snippets)

        return updated

    def delete_snippet(self, snippet: Snippet):
        """
        Delete a snippet from the database.

        Removes snippet with matching ID from the database.

        Args:
            snippet (Snippet): Snippet object to delete (identified by snippet_id)

        Returns:
            bool: True if deleted, False if snippet not found

        Note:
            This is a hard delete - snippet cannot be recovered.
            Consider using archive instead for soft delete.

        Example:
            snippet = db.get_all()[0]
            success = db.delete_snippet(snippet)
        """
        snippets = self.json_handler.read_json(default=[])

        # Filter out the snippet to delete
        filtered = [s for s in snippets if s["snippet_id"] != snippet.snippet_id]

        # Check if anything was actually removed
        if len(snippets) == len(filtered):
            return False  # Snippet not found

        # Save filtered list
        self.json_handler.write_json(filtered)

        return True


if __name__ == "__main__":
    pass
