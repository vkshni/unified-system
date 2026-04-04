# Libraries
from datetime import datetime
from pathlib import Path
import sys

# Adding project root to the Python Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Project modules
from shared.id_generator import generate_uuid
from modules.taski.state_machine import StateMachine
from modules.taski.exceptions import (
    FieldEmptyError,
    StateTransitionError,
    CompletedTimeError,
)


# Task
class Task:
    """
    Domain entity representing a single task.

    Owns its own validation logic — an invalid Task object can never
    be constructed. All fields are validated in __init__ via validate_fields(),
    which means any constraint violation is caught at the point of creation
    rather than silently persisted.

    Datetime fields are stored as datetime objects internally and serialized
    to strings only when writing to CSV via to_list().
    """

    def __init__(
        self,
        title: str,
        created_at: str = None,
        completed_at: str = None,
        task_id: str = None,
        note: str = "",
        state: str = "TODO",
    ) -> None:
        """
        Construct a Task, parsing string dates into datetime objects.

        When loading from CSV, all fields are passed as strings.
        When creating a new task, only title (and optionally note) are needed —
        all other fields default to sensible values.

        Args:
            title (str): The task title. Cannot be empty or blank.
            created_at (str | None): Creation timestamp as 'DD-MM-YYYY HH:MM:SS'.
                                     Defaults to now if not provided.
            completed_at (str | None): Completion timestamp as 'DD-MM-YYYY HH:MM:SS'.
                                       Must be None unless state is DONE.
            task_id (str | None): Existing UUID string. Auto-generated if not provided.
            note (str): Optional context or detail for the task. Defaults to "".
            state (str): Task state. Must be a valid state from StateMachine.
                         Defaults to 'TODO'.

        Raises:
            FieldEmptyError: If title is empty or whitespace.
            StateTransitionError: If state is not a recognised valid state.
            CompletedTimeError: If completed_at and state are inconsistent.
        """
        self.task_id = str(task_id) if task_id else generate_uuid()
        self.title = title
        self.created_at = (
            datetime.strptime(created_at, "%d-%m-%Y %H:%M:%S")
            if created_at
            else datetime.now()
        )
        self.completed_at = (
            datetime.strptime(completed_at, "%d-%m-%Y %H:%M:%S")
            if completed_at
            else None
        )
        self.note = note
        self.state = state

        self.validate_fields()

    def to_list(self) -> list:
        """
        Serialize the Task into a flat list for CSV storage.

        Converts datetime objects back to formatted strings. completed_at
        is written as an empty string if None, so CSV rows have consistent
        column counts.

        Returns:
            list: [task_id, title, created_at, completed_at, note, state]
                  All values are strings.
        """
        return [
            self.task_id,
            self.title,
            self.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            (
                self.completed_at.strftime("%d-%m-%Y %H:%M:%S")
                if self.completed_at
                else ""
            ),
            self.note,
            self.state,
        ]

    def to_dict(self) -> dict:

        return {
            "task_id": self.task_id,
            "title": self.title,
            "created_at": self.created_at.strftime("%d-%m-%Y %H:%M:%S"),
            "completed_at": (
                self.completed_at.strftime("%d-%m-%Y %H:%M:%S")
                if self.completed_at
                else ""
            ),
            "note": self.note,
            "state": self.state,
        }

    @classmethod
    def from_list(cls, task_row: list):

        task_id = task_row[0]
        title = task_row[1]
        created_at = task_row[2]
        completed_at = task_row[3]
        note = task_row[4]
        state = task_row[5]
        return cls(title, created_at, completed_at, task_id, note, state)

    @classmethod
    def from_dict(cls, task_dict: dict):
        """
        Construct a Task from a dictionary.

        Alternative constructor for cases where task data arrives as a dict
        rather than positional arguments (e.g. from a JSON source).

        Args:
            task_dict (dict): Must contain keys: task_id, title, created_at,
                              completed_at, note, state.

        Returns:
            Task: A fully constructed and validated Task object.
        """
        return cls(
            task_dict["title"],
            task_dict["created_at"],
            task_dict["completed_at"],
            task_dict["task_id"],
            task_dict["note"],
            task_dict["state"],
        )

    def validate_fields(self):
        """
        Enforce all domain constraints on the task's current field values.

        Called automatically at the end of __init__. Validates three things:
        - Title is not empty or blank
        - State is one of the recognised valid states
        - completed_at and state are consistent with each other

        The completed_at/state check works in both directions:
        a DONE task must have completed_at set, and a non-DONE task
        must not have completed_at set.

        Raises:
            FieldEmptyError: If title is empty or only whitespace.
            StateTransitionError: If state is not a key in StateMachine.transitions.
            CompletedTimeError: If state is DONE but completed_at is missing,
                                or if completed_at is set but state is not DONE.
        """
        if not self.title or self.title.isspace():
            raise FieldEmptyError("Field cannot be empty")

        if self.state not in StateMachine.transitions.keys():
            raise StateTransitionError("Invalid state")

        if not self.completed_at and self.state == "DONE":
            raise CompletedTimeError(
                "Completed time should be created when task 'DONE'"
            )

        if self.state != "DONE" and self.completed_at:
            raise CompletedTimeError(
                "Cannot create Completed time when state is not 'DONE'"
            )
