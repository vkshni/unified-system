class StateMachine:
    """
    Defines and enforces valid state transitions for tasks.

    Acts as the single source of truth for what states exist and which
    transitions between them are allowed. No business logic lives here —
    just the transition map and a yes/no query method.

    Valid state flow:
        TODO → IN_PROGRESS → DONE
        TODO → CANCELLED
        IN_PROGRESS → CANCELLED

    Terminal states (DONE, CANCELLED) have no outgoing transitions.
    No reverse transitions are allowed under any circumstance.
    """

    transitions = {
        "TODO": ["IN_PROGRESS", "CANCELLED"],
        "IN_PROGRESS": ["DONE", "CANCELLED"],
        "DONE": [],
        "CANCELLED": [],
    }

    def __init__(self) -> None:
        """StateMachine Constructor"""
        pass

    def can_transition(self, from_state: str, to_state: str) -> bool:
        """
        Check whether a transition between two states is permitted.

        Does not perform the transition — only answers yes or no.
        The caller (TaskManager) is responsible for acting on the result.

        Args:
            from_state (str): The task's current state.
            to_state (str): The target state to transition to.

        Returns:
            bool: True if the transition is allowed, False otherwise.
        """
        final_states = self.transitions.get(from_state, [])
        return to_state in final_states