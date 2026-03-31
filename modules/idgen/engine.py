from pathlib import Path
import sys
from keyword import kwlist
import threading
import string
import random

from modules.idgen.storage import CounterFile, ConfigFile
from modules.idgen.exceptions import (
    IDTypeExistsError,
    IDTypeNotFoundError,
    InvalidIDTypeNameError,
    CounterResetError,
)

PROJECT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_DIR))

from shared.validators import validate_not_empty

# Files and directories
IDGEN_DIR = Path(__file__).parent
CONFIG_FILE_PATH = IDGEN_DIR / "data" / "config.json"
COUNTER_FILE_PATH = IDGEN_DIR / "data" / "counter.json"


# ID Generator


class IDGenerator:
    """
    Generates unique sequential IDs with configurable prefixes and padding.

    Supports multiple ID types (order, user, invoice..) with independent counters.
    Persists state to JSON files for durability across restarts.
    """

    def __init__(
        self, CONFIG_FILE=CONFIG_FILE_PATH, COUNTER_FILE=COUNTER_FILE_PATH
    ) -> None:
        """
        ID Generator Constructor
        """

        self.config = ConfigFile(CONFIG_FILE)
        self.counter = CounterFile(COUNTER_FILE)
        self.lock = threading.Lock()

    def generate(self, id_type: str) -> str:
        """
        Generates new ID for the given type

        Args:
            id_type (str): Name of the ID type (e.g. "order", "user")

        Returns:
            result (str): Generated ID

        Raises:
            IDTypeNotFoundError: if ID type not found
        """

        with self.lock:

            counter_data = self.counter.json_handler.read_json(default={})
            config_data = self.config.get_id_type_info(id_type)
            if not config_data or not counter_data:
                raise IDTypeNotFoundError(f"ID type '{id_type}' not found")

            counter_data[id_type] += config_data["increment_step"]

            self.counter.json_handler.write_json(counter_data)
            counter = counter_data[id_type]
            prefix = config_data["prefix"]
            padding = int(config_data["padding"])

            result = f"{prefix}{counter:0{padding}d}"

            return result

    def add_id_type(
        self,
        id_type: str,
        start_value: int,
        increment_step: int,
        prefix: str,
        padding: int,
    ) -> bool:
        """
        Adds new id type

        Args:
            id_type (str): Name of the ID type (e.g. "order", "user")
            start_value (int): Starting value of the counter (e.g. 1000)
            increment_step (int): Steps to increase after each ID generation (e.g. 1,5)
            prefix (str): Prefix in each ID generated (e.g. USER-, ORD-)
            padding (int): Padding IDs with given length by 0s (e.g. 00001023)

        Returns:
            True (bool): Success

        Raises:
            IDTypeExistsError: if ID type already exists
        """

        with self.lock:

            self.validate_id_type_name(id_type)

            config_data = self.config.json_handler.read_json()
            if id_type in config_data:
                raise IDTypeExistsError(f"ID type '{id_type}' already exists")

            new_id_type = {
                id_type: {
                    "start_value": start_value,
                    "increment_step": increment_step,
                    "prefix": prefix,
                    "padding": padding,
                }
            }

            self.config.add_config(new_id_type)
            self.counter.add_counter(new_id_type)

            return True

    def update_id_type(self, id_type: str, **kwrgs: dict) -> bool:
        """
        Updates ID type with given changes

        Args:
            id_type (str): Name of the ID type (e.g. "order", "user")
            **kwrgs (dict): Keyword arguments (e.g. name = "product", padding = 8)

        Returns:
            True (bool): Success

        Raises:
            IDTypeNotFoundError: if ID type not found
        """

        with self.lock:

            self.validate_id_type_name(id_type)

            config_data = self.config.json_handler.read_json()
            if id_type not in config_data:
                raise IDTypeNotFoundError(f"ID type '{id_type}' not found")

            updated_config = kwrgs
            self.config.update_config(id_type, updated_config)

            return True

    def delete_id_type(self, id_type: str, force: bool = False) -> bool:
        """
        Deletes ID type

        Args:
            id_type (str): Name of the ID type (e.g. "order", "user")
            force (bool): By default False, but can be True to force delete

        Returns:
            True (bool): Success

        Raises:
            IDTypeNotFoundError: if ID type not found
            CounterResetError: if trying to reset the counter
        """

        with self.lock:

            self.validate_id_type_name(id_type)

            config_data = self.config.json_handler.read_json()
            if id_type not in config_data:
                raise IDTypeNotFoundError(f"ID type '{id_type}' not found")

            counter_data = self.counter.json_handler.read_json()
            current_count = counter_data.get(id_type, 0)
            start_value = config_data[id_type]["start_value"]

            if current_count > start_value and not force:
                ids_generated = current_count - start_value
                raise CounterResetError(
                    f"Cannot reset - {ids_generated} IDs generated. Use --force"
                )

            self.config.delete_id_type(id_type)
            self.counter.delete_counter(id_type)

            return True

    def reset_counter(self, id_type: str, force: bool = False) -> bool:
        """
        Resets the counter to the start_value of the ID type

        Args:
            id_type (str): Name of the ID type (e.g. "order", "user")
            force (bool): By default False, but can be True to force reset

        Returns:
            True (bool): Success

        Raises:
            IDTypeNotFoundError: if ID type not found
            CounterResetError: if trying to reset the counter
        """

        with self.lock:

            self.validate_id_type_name(id_type)

            config_data = self.config.json_handler.read_json()
            if id_type not in config_data:
                raise IDTypeNotFoundError(f"ID type '{id_type}' not found")

            counter_data = self.counter.json_handler.read_json()
            current_count = counter_data.get(id_type, 0)
            start_value = config_data[id_type]["start_value"]

            if current_count > start_value and not force:
                ids_generated = current_count - start_value
                raise CounterResetError(
                    f"Cannot reset - {ids_generated} IDs generated. Use --force"
                )

            self.counter.reset_counter(id_type, start_value)

            return True

    def validate_id_type_name(self, id_type: str) -> bool:
        """Validates ID type names, throws Errors if invalid"""

        if validate_not_empty(id_type, field_name="id_type"):
            raise InvalidIDTypeNameError("ID name cannot be empty")

        if not all(c.isalnum() or c == "_" for c in id_type):
            raise InvalidIDTypeNameError(
                "Only alphanumeric and underscore allowed in ID name"
            )

        if len(id_type) < 3 or len(id_type) > 50:
            raise InvalidIDTypeNameError(
                "Length of name should be lesser than 50 and greater or equal to 3"
            )

        if id_type in kwlist:
            raise InvalidIDTypeNameError("Reserved words cannot be used")

        return True

    def generate_password(self, pwd_len: int = 4) -> str:
        """
        Generates random password for given length

        Args:
            pwd_len (int): Length of the password (By default 4)

        Returns:
            password (str): Generated password
        """

        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        digits = string.digits
        specials = "!@#$%^&*_"

        password_chars = [
            random.choice(lower),
            random.choice(upper),
            random.choice(digits),
            random.choice(specials),
        ]

        all_chars = lower + upper + digits + specials
        for i in range(pwd_len - 4):
            password_chars.append(random.choice(all_chars))

        random.shuffle(password_chars)
        password = "".join(password_chars)

        return password

    def list_id_types(self) -> list[dict]:
        """
        List all ID types with their current status.

        Returns:
            list: List of dicts with id_type info
        """

        with self.lock:
            config_data = self.config.json_handler.read_json()
            counter_data = self.counter.json_handler.read_json()

            id_types = []
            for id_type, config in config_data.items():
                id_types.append(
                    {
                        "name": id_type,
                        "prefix": config["prefix"],
                        "counter": counter_data.get(id_type, 0),
                        "start_value": config["start_value"],
                        "increment_step": config["increment_step"],
                        "padding": config["padding"],
                    }
                )

            return id_types


if __name__ == "__main__":
    idg = IDGenerator()

    # print(idg.generate("order"))
    # print(idg.generate("cr"))

    # print(idg.add_id_type("car", 1000, 1, "CAR-", 10))
    # print(idg.update_id_type("car", increment_step=2, padding=12))
    # print(idg.delete_id_type("car"))
    # print(idg.delete_id_type("order"))
    # print(idg.reset_counter("order", force=True))

    # all_ids = idg.list_id_types()
    # for id in all_ids:
    #     print(id)

    # new_id = {
    #     "car": {
    #         "start_value": 1000,
    #         "increment_step": 1,
    #         "prefix": "CAR-",
    #         "padding": 12,
    #     }
    # }
    # idg.add_id_type("car", 1000, 1, "CAR-", 10)
    # all_ids = idg.list_id_types()
    # for id in all_ids:
    #     print(id)

    # print(PROJECT_DIR)
    print(idg.list_id_types())
