# Shared file handler


from pathlib import Path
import json
import csv


SHARED_DIR = Path(__file__).parent


# JSON Handler
class JSONFile:

    def __init__(self, file_path):
        self.path = file_path

    def read_json(self, default=None):

        try:
            with open(self.path, "r") as f:
                data = json.load(f)

            return data
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def write_json(self, data, indent=4):

        # checks if directory exists or not
        ensure_directory((SHARED_DIR / "data"))

        with open(self.path, "w") as f:

            json.dump(data, f, indent=indent)
            return True

        return False


class CSVFile:

    def __init__(self, file_path):
        self.path = file_path

    def read_csv(self, has_header=True):

        try:
            with open(self.path, "r") as f:
                if has_header:
                    reader = csv.DictReader(f)
                    rows = [row for row in reader]
                    return rows
                reader = csv.reader(f)
                rows = [row for row in reader]
                return rows

        except FileNotFoundError:
            return []

    def write_csv(self, rows: list[dict], header=None):

        # checks if directory exists or not
        ensure_directory((SHARED_DIR / "data"))

        with open(self.path, "w", newline="") as f:

            writer = csv.DictWriter(f, fieldnames=header)
            if header:
                writer.writerow(header)

            writer.writerows(rows)
            return True

        return False

    def append_csv(self, row, header=None):

        with open(self.path, "a", newline="") as f:

            writer = csv.writer(f)
            if header:
                writer.writerow(header)

            writer.writerow(row)
            return True

        return False


# Utilities


def file_exists(file_path):

    file_path = Path(file_path)
    return file_path.exists()


def ensure_directory(file_path):

    file = Path(file_path)
    parent_dir = file.parent
    if not parent_dir.exists():
        parent_dir.mkdir()
    return True


if __name__ == "__main__":

    COUNTER_FILE = SHARED_DIR / "data" / "counter.json"
    counter = JSONFile(COUNTER_FILE)
    # print(counter.path)
    # print(counter.read_json())
    # data = {"snippets": 20}
    # print(counter.write_json(data))
    CSV_FILE = SHARED_DIR / "data" / "trial.csv"
    trial = CSVFile(CSV_FILE)
    # print(trial.read_csv())
    # header = ["id", "name", "age"]
    # data = [[1, "vijay", 20]]
    # print(trial.write_csv(data, header=header))
    # print(trial.append_csv([2, "Ritu", 30]))
    # print(file_exists(CSV_FILE))

    FILE = SHARED_DIR / "demo" / "john.json"
    print(ensure_directory(FILE))
    print(file_exists(FILE))

    # p = Path(CSV_FILE)
    # print(p, type(p))
