# Storage layer

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# from directories
from shared.file_handler import JSONFile


# Files and directories
IDGEN_DIR = Path(__file__).parent
CONFIG_FILE_PATH = IDGEN_DIR / "data" / "config.json"
COUNTER_FILE_PATH = IDGEN_DIR / "data" / "counter.json"


# class JSONFile:

#     def __init__(self, file_name: str) -> None:
#         """JSONFile Constructor"""

#         self.file_path = self.create_file(BASE_DIR, file_name)

#     def create_file(self, BASE_DIR: str, file_name: str) -> str:
#         """Creates file if file doesn't exists"""

#         path = BASE_DIR / file_name
#         if not path.exists():
#             with open(path, "x") as f:
#                 pass
#         return path

#     def read_all(self) -> dict:

#         with open(self.file_path, "r") as f:

#             data = json.load(f)
#             return data

#     def write_all(self, data):

#         with open(self.file_path, "w") as f:

#             json.dump(data, f, indent=4)
#             return True

# Counter


class CounterFile:

    def __init__(self):
        self.json_handler = JSONFile(COUNTER_FILE_PATH)
        self.config = ConfigFile()
        self.initialize_file()

    def initialize_file(self):

        try:
            if self.json_handler.read_json():
                return True
            else:
                self.json_handler.write_json(self.__initial_data())

        except BaseException:
            self.json_handler.write_all(self.__initial_data())
            return True

    def __initial_data(self):

        start_values = self.config.get_start_values()

        data = {
            "order": start_values["order"],
            "user": start_values["user"],
            "invoice": start_values["invoice"],
        }
        return data

    def add_counter(self, new_id_type: dict):

        data = self.json_handler.read_json(default={})
        for id_type, config in new_id_type.items():
            data[id_type] = config["start_value"]

        self.json_handler.write_json(data)

        return True

    def delete_counter(self, id_type):

        data = self.json_handler.read_json(default={})
        if not data.get(id_type):
            return False
        del data[id_type]

        self.json_handler.write_json(data)
        return True

    def reset_counter(self, id_type, start_value):

        data = self.json_handler.read_json()

        if not data.get(id_type):
            return False

        data[id_type] = start_value
        self.json_handler.write_json(data)
        return True


# Configuration


class ConfigFile:

    def __init__(self):
        self.json_handler = JSONFile(CONFIG_FILE_PATH)
        self.initialize_file()

    def initialize_file(self):

        try:
            if self.json_handler.read_json():
                return True
            else:
                self.json_handler.write_json(self.__initial_data())

        except BaseException:
            self.json_handler.write_json(self.__initial_data())
            return True

    def get_start_values(self):

        data = self.json_handler.read_json()

        start_values = dict()
        for id_type, config in data.items():
            start_values[id_type] = config["start_value"]
        return start_values

    def get_id_type_info(self, id_type):

        data = self.json_handler.read_json()
        config = data.get(id_type, None)
        return config

    def get_increment_step(self, id_type):

        data = self.json_handler.read_json()
        step = data[id_type].get("increment_step", 0)
        return step

    def get_prefix(self, id_type):

        data = self.json_handler.read_json()
        prefix = data[id_type].get("prefix", "")
        return prefix

    def __initial_data(self):

        data = {
            "order": {
                "start_value": 1000,
                "increment_step": 1,
                "prefix": "ORD-",
                "padding": 10,
            },
            "user": {
                "start_value": 1000,
                "increment_step": 1,
                "prefix": "USER-",
                "padding": 10,
            },
            "invoice": {
                "start_value": 1000,
                "increment_step": 1,
                "prefix": "INV-",
                "padding": 10,
            },
        }
        return data

    def add_config(self, new_id_type: dict):

        data = self.json_handler.read_json(default={})
        for id_type, config in new_id_type.items():
            data[id_type] = config

        self.json_handler.write_json(data)
        return True

    def update_config(self, id_type, updated_config: dict):

        data = self.json_handler.read_json()
        if not data.get(id_type):
            return False
        old_config = data[id_type]
        for key, value in updated_config.items():
            if key in old_config:
                old_config[key] = value

        data[id_type] = old_config
        self.json_handler.write_json(data)
        return True

    def delete_id_type(self, id_type):

        data = self.json_handler.read_json()
        if not data.get(id_type):
            return False
        del data[id_type]

        self.json_handler.write_json(data)

        return True


if __name__ == "__main__":
    test_config = ConfigFile()
    counter = CounterFile()

    new_id = {
        "car": {
            "start_value": 1000,
            "increment_step": 1,
            "prefix": "CAR-",
            "padding": 10,
        }
    }
    # print(counter.add_counter(new_id))
    # print(counter.reset_counter("car", 1000))
    # print(counter.delete_counter("car"))

    # print(test_config.get_start_values())
    # print(test_config.get_id_type_info("order"))
    # print(test_config.get_increment_step("order"))
    # print(test_config.get_prefix("order"))
    # print(test_config.add_config(new_id))
    # print(test_config.update_config("car", {"start_value": 2000, "padding": 12}))
    # print(test_config.delete_id_type("car"))
