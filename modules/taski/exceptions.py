"""
Custom exceptions for the taski domain.

Each exception maps to a specific category of failure in the system.
Raising named exceptions instead of generic ValueError allows the CLI
to catch them individually and show the right message for each case.
"""


class TaskNotFoundError(Exception):
    """Raised when a task cannot be found by display_id or task_id."""
    pass


class FilterNotFoundError(Exception):
    """Raised when an unrecognised filter name is passed to a fetch method."""
    pass


class FieldEmptyError(Exception):
    """Raised when a required field (e.g. title) is empty or blank."""
    pass


class StateTransitionError(Exception):
    """
    Raised when a state transition is invalid.

    Covers two cases:
    - The requested target state is not reachable from the current state.
    - An attempt is made to modify a task that is already in DONE state.
    """
    pass


class CompletedTimeError(Exception):
    """
    Raised when completed_at and state are inconsistent.

    Covers two cases:
    - State is DONE but completed_at is not set.
    - completed_at is set but state is not DONE.
    """
    pass