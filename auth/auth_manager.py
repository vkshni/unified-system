# Authentication
import hashlib
from hmac import compare_digest
from pathlib import Path
from datetime import datetime, timedelta

from shared.file_handler import JSONFile, file_exists

# Auth directory
AUTH_DIR = Path(__file__).parent

# Vault Meta file
VAULT_META_FILE_PATH = AUTH_DIR / "data" / "vault_meta.json"

vm = JSONFile(VAULT_META_FILE_PATH)

# Attempts file
ATTEMPTS_FILE_PATH = AUTH_DIR / "data" / "attempts.json"
MAX_ATTEMPTS = 3
LOCKOUT_DURATION = 30
DATETIME_FORMAT = "%d-%m-%YT%H:%M:%S"
attempt = JSONFile(ATTEMPTS_FILE_PATH)


class AuthService:

    def __init__(self):
        self.is_authenticated = False
        pass

    # setup master (one-time)
    def setup_master(self, master_password):

        # check if vault meta initialized
        if file_exists(VAULT_META_FILE_PATH):
            raise PermissionError("Vault already initialized")

        # proceed if not
        master_password_hash = self.generate_hash(master_password)
        vm.write_json({"master_password_hash": master_password_hash})
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
        attempt.write_json({"failed_attempts": 0, "locked_until": None})
        return True

    # record failed attempt
    def record_failed_attempt(self):

        # read attempt data
        attempt_data = attempt.read_json()

        failed_attempt = attempt_data.get("failed_attempts", 0)
        failed_attempt += 1

        # write updated failed_attempts
        attempt_data["failed_attempts"] = failed_attempt
        attempt.write_json(attempt_data)

        # Trigger lockout after MAX_ATTEMPTS
        if failed_attempt >= MAX_ATTEMPTS:
            locked_until = (
                datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
            ).strftime(DATETIME_FORMAT)

            # write updated locked_until
            attempt_data["locked_until"] = locked_until
            attempt.write_json(attempt_data)

    # Check if locked out
    def is_locked_out(self):

        attempt_data = attempt.read_json()

        locked_until = attempt_data["locked_until"]

        if not locked_until:
            return False

        expiry = datetime.strptime(locked_until, DATETIME_FORMAT)
        if datetime.now() > expiry:

            attempt_data["failed_attempts"] = 0
            attempt_data["locked_until"] = None
            attempt.write_json(attempt_data)
            return False

        return True

    # hashing
    def generate_hash(self, password_str):

        password_hash = hashlib.sha256(password_str.encode()).hexdigest()
        return password_hash

    # verify password
    def verify(self, password: str):

        input_hash = hashlib.sha256(password.encode()).hexdigest()
        master_password_hash = vm.read_json().get("master_password_hash", None)
        return compare_digest(input_hash, master_password_hash)

    # decorator to check if authenticated
    # @staticmethod
    # def require_auth(func):

    #     def wrapper(args):


if __name__ == "__main__":
    auth = AuthService()

    # print(auth.setup_master("vks123"))
    # print(auth.verify("vks123"))

    # print(auth.verify_master("vks123"))
