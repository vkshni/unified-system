from uuid import uuid4
from datetime import datetime
from pathlib import Path
import sys

# Adding project root to the Python Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.file_handler import JSONFile, DATA_DIR

# Counter file setup
COUNTER_FILE_PATH = DATA_DIR / "counter.json"  # ✅ Changed
counter_file = JSONFile(COUNTER_FILE_PATH)

if not counter_file.read_json():
    initial_data = {"global": 0, "tasks": 0, "expenses": 0, "urls": 0, "snippets": 0}
    counter_file.write_json(initial_data)

# Timestamp counter file setup
TIMESTAMP_COUNTER_FILE_PATH = DATA_DIR / "timestamp_counter.json"  # ✅ Changed
COUNTER_DATE_FORMAT = "%d%m%Y"
time_counter_file = JSONFile(TIMESTAMP_COUNTER_FILE_PATH)

if not time_counter_file.read_json():
    initial_data = {
        "last_date": datetime.now().strftime(COUNTER_DATE_FORMAT),
        "last_id": 0,
    }
    time_counter_file.write_json(initial_data)


def generate_uuid() -> str:
    return str(uuid4())


def generate_incremental_id(system_name="global", counter_file=counter_file):
    data = counter_file.read_json(default={})

    if system_name not in data:
        raise ValueError(f"System name '{system_name}' not found in counter file")

    data[system_name] += 1
    counter_file.write_json(data)
    return data[system_name]


def generate_time_stamp_id(counter_file=time_counter_file, prefix=""):
    counter_data = counter_file.read_json()
    current_date = datetime.now()
    counter_date = datetime.strptime(counter_data["last_date"], COUNTER_DATE_FORMAT)

    if current_date.date() > counter_date.date():  # Compare dates only
        counter_data["last_date"] = current_date.strftime(COUNTER_DATE_FORMAT)
        counter_data["last_id"] = 1
        counter_file.write_json(counter_data)
    else:
        counter_data["last_id"] += 1
        counter_file.write_json(counter_data)

    # ✅ Added zero-padding
    date_str = counter_data["last_date"]
    id_str = f"{counter_data['last_id']:05d}"

    if prefix:
        return f"{prefix}_{date_str}_{id_str}"
    return f"{date_str}_{id_str}"


def generate_prefixed_id(prefix, system_name, counter_file=counter_file):  # ✅ Added
    """Generates IDs like TASK_001, EXP_042"""
    counter = generate_incremental_id(system_name, counter_file)
    return f"{prefix}_{counter:05d}"


if __name__ == "__main__":
    print(generate_uuid())
    print(generate_uuid())
    print(generate_uuid())

    print(generate_incremental_id())
    print(generate_incremental_id())
    print(generate_incremental_id())

    print(generate_time_stamp_id())
    print(generate_time_stamp_id())
    print(generate_time_stamp_id())

    print(generate_prefixed_id("TASK", "tasks"))
    print(generate_prefixed_id("TASK", "tasks"))
    print(generate_prefixed_id("TASK", "tasks"))
