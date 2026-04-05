"""
vault.py — Core vault operations
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from datetime import datetime
from modules.shield.storage import VaultData
from modules.shield.entity import Credential
from auth.auth_manager import AuthService  # ✅ Use centralized auth


class Vault:
    """Central interface for all vault credential operations"""

    def __init__(self):
        """Initialize the Vault with centralized auth"""
        DATA_DIR = Path(__file__).parent / "data"
        data_file = DATA_DIR / "vault_data.json"

        self.vd = VaultData(str(data_file))
        self.auth = AuthService()  # ✅ Uses centralized auth

    def add_credential(self, service_name, username, password, label="default"):
        """Add a new credential record"""
        self.auth.require_authenticated()

        # Rest of your existing code stays the same...
        existing = [
            c
            for c in self.vd.get_all()
            if c.service_name.lower() == service_name.lower()
            and c.label.lower() == label.lower()
        ]

        if existing:
            raise ValueError(f"'{service_name}/{label}' already exists")

        credential_obj = Credential(service_name, username, password, label=label)
        self.vd.add(credential_obj)

    # ... rest of your methods stay exactly the same

    def list_services(self):
        """
        Return a list of all stored service/label pairs.

        Returned as a list of [service_name, label] pairs in lowercase,
        preserving insertion order. Used by the CLI to display what
        services are stored without exposing usernames or passwords.

        Returns:
            list[list[str]]: Each inner list is [service_name, label].
                             e.g. [['github', 'default'], ['instagram', 'work']]

        Raises:
            PermissionError: If the session is not authenticated.
        """

        self.auth.require_authenticated()

        credentials = self.vd.get_all()
        services = [[c.service_name.lower(), c.label.lower()] for c in credentials]

        return services

    def get_credential(self, service_name, label="default"):
        """
        Retrieve a single credential by service name and label.

        Matching is case-insensitive on both fields. Returns None if
        no matching record is found — callers are responsible for
        handling the None case explicitly.

        Args:
            service_name (str):           Name of the service to look up.
            label        (str, optional): Account label. Defaults to 'default'.

        Returns:
            Credential | None: The matching credential, or None if not found.

        Raises:
            PermissionError: If the session is not authenticated.
        """

        self.auth.require_authenticated()

        credentials = self.vd.get_all()

        for c in credentials:
            if (
                c.service_name.lower() == service_name.lower()
                and c.label.lower() == label.lower()
            ):
                return c
        return None

    def get_credential_by_service_name(self, service_name):
        """
        Retrieve all credentials stored under a given service name.

        Used when a service has multiple accounts (different labels)
        and the caller needs to present all options to the user before
        asking which label they want.

        Args:
            service_name (str): Name of the service to look up.

        Returns:
            list[Credential]: All matching credentials. Empty list if none found.

        Raises:
            PermissionError: If the session is not authenticated.
        """

        self.auth.require_authenticated()
        all_credentials = self.vd.get_all()

        credentials = [
            c for c in all_credentials if c.service_name.lower() == service_name.lower()
        ]

        return credentials

    def update_credential(
        self,
        service_name,
        label="default",
        new_service_name=None,
        new_label=None,
        new_username=None,
        new_password=None,
    ):
        """
        Update one or more fields of an existing credential.

        Only fields passed as non-None are updated. Fields left as None
        retain their current values. updated_at is always refreshed to
        the current time when any change is made.

        When renaming service_name or label, a conflict check runs first
        to ensure the new service_name/label combination does not already
        exist in the vault.

        Args:
            service_name     (str):           Current service name to identify the record.
            label            (str, optional): Current label to identify the record. Defaults to 'default'.
            new_service_name (str, optional): New service name. None keeps current.
            new_label        (str, optional): New label. None keeps current.
            new_username     (str, optional): New username. None keeps current.
            new_password     (str, optional): New password. None keeps current.

        Raises:
            PermissionError: If the session is not authenticated.
            ValueError:      If no credential exists with the given service_name/label.
            ValueError:      If renaming would create a duplicate service_name/label.
        """

        self.auth.require_authenticated()
        credential = self.get_credential(service_name, label)

        if not credential:
            raise ValueError(f"No credential with service '{service_name}' found")

        if new_service_name is not None:
            # Check the target name doesn't conflict with an existing record
            target_label = new_label if new_label else label
            conflict = self.get_credential(new_service_name, target_label)
            if conflict:
                raise ValueError(f"'{new_service_name}/{new_label}' already exists")
            credential.service_name = new_service_name

        if new_username is not None:
            credential.username = new_username
        if new_password is not None:
            credential.password = new_password
        if new_label is not None:
            credential.label = new_label

        # Always stamp the update time regardless of which fields changed
        credential.updated_at = datetime.now()

        self.vd.update(credential)

    def delete_credential(self, service_name, label="default"):
        """
        Permanently delete a credential from the vault.

        This operation is irreversible. The CLI is responsible for
        presenting a confirmation prompt before calling this method.

        Args:
            service_name (str):           Name of the service to delete.
            label        (str, optional): Label of the account to delete. Defaults to 'default'.

        Raises:
            PermissionError: If the session is not authenticated.
            ValueError:      If no credential exists with the given service_name/label.
        """

        self.auth.require_authenticated()

        credential = self.get_credential(service_name, label)

        if not credential:
            raise ValueError(
                f"No credential with service '{service_name}/{label}' found"
            )

        self.vd.delete(credential)


if __name__ == "__main__":
    pass
