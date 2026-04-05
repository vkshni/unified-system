# Authentication
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Now imports work
from shared.file_handler import JSONFile, file_exists
import hashlib
from hmac import compare_digest
from datetime import datetime, timedelta

# Auth directory
AUTH_DIR = Path(__file__).parent

# Vault Meta file
VAULT_META_FILE_PATH = AUTH_DIR / "data" / "vault_meta.json"

# Attempts file
ATTEMPTS_FILE_PATH = AUTH_DIR / "data" / "attempts.json"
MAX_ATTEMPTS = 3
LOCKOUT_DURATION = 30
DATETIME_FORMAT = "%d-%m-%YT%H:%M:%S"

# Session file
SESSION_FILE_PATH = AUTH_DIR / "data" / "session.json"
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Protected systems
PROTECTED_SYSTEMS = ["snippet", "penny", "shield"]


class AuthService:

    def __init__(self):
        self.vault = JSONFile(VAULT_META_FILE_PATH)
        self.attempt = JSONFile(ATTEMPTS_FILE_PATH)
        self.session = JSONFile(SESSION_FILE_PATH)
        self.is_authenticated = self.check_session()

    def require_authenticated(self):
        """
        Assert that the current session is authenticated.

        Called at the start of every sensitive Vault operation. Raises
        immediately if is_authenticated is False, halting execution before
        any data is accessed or modified.

        Raises:
            PermissionError: If is_authenticated is False.
        """

        if not self.is_authenticated:
            raise PermissionError("Access denied. Please login first")

    # Check session
    def check_session(self):

        session_data = self.session.read_json(default={})

        if not session_data.get("logged_in"):
            return False

        # Check if session expired
        login_time = session_data.get("login_time")
        if not login_time:
            return False

        login_dt = datetime.strptime(login_time, DATETIME_FORMAT)
        if datetime.now() > login_dt + timedelta(seconds=SESSION_TIMEOUT):
            # Session expired
            self.logout()
            return False

        return True

    # Create session
    def create_session(self):
        session_data = {
            "logged_in": True,
            "login_time": datetime.now().strftime(DATETIME_FORMAT),
            "user": "master",
        }
        self.session.write_json(session_data)

    # Log out
    def logout(self):

        self.is_authenticated = False
        session_data = {"logged_in": False, "login_time": None, "user": None}
        self.session.write_json(session_data)

    # Get session info
    def get_session_info(self):
        return self.session.read_json(default={})

    # setup master (one-time)
    def setup_master(self, master_password):

        # check if vault meta initialized
        if self.is_initialized():
            raise PermissionError("Vault already initialized")

        # proceed if not
        master_password_hash = self.generate_hash(master_password)
        self.vault.write_json({"master_password_hash": master_password_hash})
        return True

    # verify_master
    def verify_master(self, user_password):

        # check if locked out
        if self.is_locked_out():
            raise ValueError(f"Locked out! Try after {LOCKOUT_DURATION} seconds")

        # verify password
        if not self.verify(user_password):
            # record failed attempt
            self.record_failed_attempt()
            return False

        # successful login
        self.is_authenticated = True
        self.create_session()
        self.attempt.write_json({"failed_attempts": 0, "locked_until": None})
        return True

    # record failed attempt
    def record_failed_attempt(self):

        # read attempt data
        attempt_data = self.attempt.read_json()

        failed_attempt = attempt_data.get("failed_attempts", 0)
        failed_attempt += 1

        # write updated failed_attempts
        attempt_data["failed_attempts"] = failed_attempt
        self.attempt.write_json(attempt_data)

        # Trigger lockout after MAX_ATTEMPTS
        if failed_attempt >= MAX_ATTEMPTS:
            locked_until = (
                datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
            ).strftime(DATETIME_FORMAT)

            # write updated locked_until
            attempt_data["locked_until"] = locked_until
            self.attempt.write_json(attempt_data)

    # Check if locked out
    def is_locked_out(self):

        attempt_data = self.attempt.read_json()

        locked_until = attempt_data["locked_until"]

        if not locked_until:
            return False

        expiry = datetime.strptime(locked_until, DATETIME_FORMAT)
        if datetime.now() > expiry:

            attempt_data["failed_attempts"] = 0
            attempt_data["locked_until"] = None
            self.attempt.write_json(attempt_data)
            return False

        return True

    # hashing
    def generate_hash(self, password_str):

        password_hash = hashlib.sha256(password_str.encode()).hexdigest()
        return password_hash

    # verify password
    def verify(self, password: str):

        input_hash = hashlib.sha256(password.encode()).hexdigest()
        master_password_hash = self.vault.read_json().get("master_password_hash", None)
        return compare_digest(input_hash, master_password_hash)

    # Check if protected
    @staticmethod
    def is_protected(system_name: str):

        return system_name in PROTECTED_SYSTEMS

    # Check if vault meta initialized or not
    def is_initialized(self):
        return file_exists(VAULT_META_FILE_PATH)


# decorator to check if authenticated
def require_auth(func):

    def wrapper(*args, **kwargs):

        auth = AuthService()

        if not auth.is_authenticated:
            raise PermissionError("Authentication required! Please login first")

        return func(*args, **kwargs)

    return wrapper


if __name__ == "__main__":
    auth = AuthService()

    # print(auth.setup_master("vks123"))
    # print(auth.is_authenticated)
    # print(auth.verify_master("vks123"))
    # print(auth.is_authenticated)

    # auth2 = AuthService()
    # print(auth2.is_authenticated)

    # print(auth.is_protected("snippet"))
    # auth.logout()

    @require_auth
    def add_password(password):
        print("FUrther code")

    add_password("vsk")
