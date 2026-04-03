from pathlib import Path
import json
import csv
import sys


# Adding project root to the Python Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Use Path for cross-platform compatibility
SHARED_DIR = Path(__file__).parent
DATA_DIR = SHARED_DIR / "data"


class JSONFile:
    def __init__(self, file_path):
        self.path = Path(file_path)  # Convert to Path object

    def read_json(self, default=None):
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def write_json(self, data, indent=4):
        try:
            ensure_directory(self.path)  #
            with open(self.path, "w") as f:
                json.dump(data, f, indent=indent)
            return True
        except Exception as e:  #
            return False


class CSVFile:
    def __init__(self, file_path):
        self.path = Path(file_path)  #  Convert to Path

    def read_csv(self, has_header=True):
        try:
            with open(self.path, "r") as f:
                if has_header:
                    return list(csv.DictReader(f))
                return list(csv.reader(f))
        except FileNotFoundError:
            return []

    def write_csv(self, rows: list[dict], header=None):
        try:
            ensure_directory(self.path)  # ✅ Changed
            with open(self.path, "w", newline="") as f:
                if not header and rows:
                    header = list(rows[0].keys())  # Auto-detect from first row

                writer = csv.DictWriter(f, fieldnames=header)
                writer.writeheader()  # ✅ Changed
                writer.writerows(rows)
            return True
        except Exception as e:  # ✅ Added
            return False

    def append_csv(self, row, header=None):
        try:
            with open(self.path, "a", newline="") as f:
                writer = csv.writer(f)
                if header:
                    writer.writerow(header)
                writer.writerow(row)
            return True
        except Exception as e:  # ✅ Added
            return False


# Utilities
def file_exists(file_path):
    return Path(file_path).exists()


def ensure_directory(file_path):
    """Ensures parent directory exists for a file path"""
    directory = Path(file_path).parent  # ✅ Changed logic
    directory.mkdir(parents=True, exist_ok=True)  # ✅ Changed
    return True
