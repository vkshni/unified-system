# Libraries
from pathlib import Path
import sys

# Adding project root to the Python Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.file_handler import CSVFile
from modules.taski.entity import Task
from modules.taski.exceptions import TaskNotFoundError

# Directories for file operations
TASKI_DIR = Path(__file__).parent
DATA_DIR = TASKI_DIR / "data"

TASKS_FILE_PATH = DATA_DIR / "tasks.csv"


# # Low Levels File Handlers
# class CSVFile:
#     """
#     Low-level handler for reading and writing CSV files.

#     Responsible only for raw file I/O. Has no knowledge of tasks,
#     business rules, or data structure — just rows in, rows out.
#     """

#     def __init__(self, file_name: str) -> None:
#         """
#         Initialize CSVFile and create the file if it doesn't exist.

#         Args:
#             file_name (str): Name of the CSV file (e.g. 'tasks.csv').
#                              Created inside the /database directory.
#         """
#         self.file_path = self.create(file_name)

#     def create(self, file_name: str) -> str:
#         """
#         Resolve the file path and create the file if it doesn't exist.

#         Args:
#             file_name (str): Name of the file to create.

#         Returns:
#             Path: Absolute path to the file.
#         """
#         path = BASE_DIR / "database" / file_name
#         if not path.exists():
#             with open(path, "x") as f:
#                 pass
#         return path

#     def read_all(self) -> list[list]:
#         """
#         Read all rows from the CSV file.

#         Returns:
#             list[list]: All rows including the header as lists of strings.
#                         Returns an empty list if the file is empty.
#         """
#         with open(self.file_path, "r") as f:

#             reader = csv.reader(f)
#             rows = [row for row in reader]
#             return rows

#     def write_all(self, rows: list[list]) -> None:
#         """
#         Overwrite the entire CSV file with the given rows.

#         Used for updates and deletes where the full file needs rewriting.

#         Args:
#             rows (list[list]): All rows to write, including the header.
#         """
#         with open(self.file_path, "w", newline="") as f:

#             writer = csv.writer(f)
#             writer.writerows(rows)

#     def append_row(self, row: list) -> None:
#         """
#         Append a single row to the end of the CSV file.

#         Used for creating new tasks without rewriting the whole file.

#         Args:
#             row (list): A single row to append.
#         """
#         with open(self.file_path, "a", newline="") as f:

#             writer = csv.writer(f)
#             writer.writerow(row)


# class JSONFile:
#     """
#     Low-level handler for JSON files.

#     Reserved for future use. Currently only creates the file if it
#     doesn't exist.
#     """

#     def __init__(self, file_name: str) -> None:
#         """
#         Initialize JSONFile and create the file if it doesn't exist.

#         Args:
#             file_name (str): Name of the JSON file to create.
#         """
#         self.file_path = self.create(file_name)

#     def create(self, file_name: str) -> str:
#         """
#         Resolve the file path and create the file if it doesn't exist.

#         Args:
#             file_name (str): Name of the file to create.

#         Returns:
#             Path: Absolute path to the file.
#         """
#         path = BASE_DIR / "database" / file_name
#         if not path.exists():
#             with open(path, "x") as f:
#                 pass
#         return path


# TaskDB
class TaskDB:
    """
    Persistence layer for task data.

    Handles all reading and writing of Task objects to CSV storage.
    Knows the structure of the CSV (column order, header) but enforces
    no business rules — that responsibility belongs to TaskManager.
    """

    def __init__(self, TASK_FILE=TASKS_FILE_PATH) -> None:
        """
        Initialize TaskDB and ensure the CSV file has a header row.
        """
        self.csv_handler = CSVFile(TASK_FILE)
        self.initialize()

    def __initial_data(self) -> list:
        """
        Return the CSV header row.

        Returns:
            list: Column names in the order they appear in the CSV.
        """
        header = ["task_id", "title", "created_at", "completed_at", "note", "state"]
        return header

    def initialize(self) -> None:
        """
        Write the header row if the CSV file is empty.

        Called once on startup to ensure the file is ready to use.
        """
        rows = self.csv_handler.read_csv()
        if not rows:
            row = self.__initial_data()
            self.csv_handler.append_csv(row)

    def get_all_tasks(self, skip_header: bool = True) -> list[Task]:
        """
        Read all rows from CSV and deserialize them into Task objects.

        Args:
            skip_header (bool): Whether to skip the first row (header).
                                Defaults to True.

        Returns:
            list[Task]: All tasks in the order they appear in the CSV.
                        Returns an empty list if no tasks exist.
        """
        rows = self.csv_handler.read_csv()
        if skip_header:
            rows = rows[1:]

        tasks = [Task.from_dict(r) for r in rows]
        return tasks

    def fetch_task(self, filter: str, value: str) -> list[Task]:
        """
        Return all tasks matching the given filter and value.

        Supports filtering by title (exact match) or by date fields
        (created_on, completed_on) using DD-MM-YYYY format.

        Args:
            filter (str): The field to filter by.
                          One of: 'TITLE', 'CREATED_ON', 'COMPLETED_ON'.
            value (str): The value to match against.

        Returns:
            list[Task]: All matching Task objects. Empty list if none match.

        Raises:
            TaskNotFoundError: If the database has no tasks at all.
        """
        tasks = self.get_all_tasks()

        if not tasks:
            raise TaskNotFoundError("No tasks found")

        filtered = []
        for task in tasks:
            if filter.upper() == "TITLE" and task.title.lower() == value.lower():
                filtered.append(task)
            elif (
                filter == "CREATED_ON"
                and str(task.created_at.strftime("%d-%m-%Y")) == value
            ):
                filtered.append(task)
            elif (
                filter == "COMPLETED_ON"
                and task.completed_at
                and str(task.completed_at.strftime("%d-%m-%Y")) == value
            ):
                filtered.append(task)

        return filtered

    def create_task(self, task: Task) -> None:
        """
        Persist a new Task object to the CSV file.

        Serializes the task via to_list() and appends it as a new row.

        Args:
            task (Task): The Task object to save.
        """
        row = task.to_list()
        self.csv_handler.append_csv(row)
        return True

    def update_task(self, task: Task) -> bool:
        """
        Find an existing task by task_id and overwrite it with new data.

        Reads the full CSV, replaces the matching row, and rewrites
        the entire file. Raises if the task_id is not found.

        Args:
            task (Task): The Task object with updated fields.
                         Matched against existing rows by task_id.

        Returns:
            bool: True if the update was successful.

        Raises:
            TaskNotFoundError: If no row with the given task_id exists.
        """
        rows = self.csv_handler.read_csv()
        header = rows[0]
        new_tasks = rows[1:]

        updated = False

        for i, t in enumerate(new_tasks):
            if t["task_id"] == task.task_id:
                new_tasks[i] = task.to_dict()
                updated = True
                break

        if not updated:
            raise TaskNotFoundError("Task Not found")

        self.csv_handler.write_csv([header] + new_tasks)
        return True

    def delete_task(self, task_id: str) -> None:
        """
        Remove a task from the CSV by its task_id.

        Filters out the matching row and rewrites the file.
        Raises if no matching task_id is found.

        Args:
            task_id (str): The UUID of the task to delete.

        Raises:
            TaskNotFoundError: If no row with the given task_id exists.
        """
        rows = self.csv_handler.read_csv()

        filtered = [row for row in rows if row["task_id"] != task_id]

        if len(rows) == len(filtered):
            raise TaskNotFoundError("Task Not found")

        self.csv_handler.write_csv(filtered)
        return True


if __name__ == "__main__":

    t = TaskDB()

    all_tasks = t.get_all_tasks()
    for t in all_tasks:
        print(t)
