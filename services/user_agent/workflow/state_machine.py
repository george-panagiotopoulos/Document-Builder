"""
Workflow state machine.

Manages state transitions for the document generation workflow.
"""

from enum import Enum


class WorkflowState(str, Enum):
    """Workflow states as defined in the design specification."""

    INITIALIZED = "initialized"
    SUBMITTED = "submitted"
    CONTENT_NORMALIZED = "content_normalized"
    LAYOUT_QUEUED = "layout_queued"
    LAYOUT_PROCESSING = "layout_processing"
    LAYOUT_COMPLETE = "layout_complete"
    RENDERING_QUEUED = "rendering_queued"
    RENDERING_PROCESSING = "rendering_processing"
    RENDERING_COMPLETE = "rendering_complete"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStateMachine:
    """State machine for workflow orchestration."""

    def __init__(self) -> None:
        """Initialize state machine."""
        self.current_state = WorkflowState.INITIALIZED
        self.state_history: list[WorkflowState] = [WorkflowState.INITIALIZED]

    def transition(self, new_state: WorkflowState) -> None:
        """
        Transition to a new state.

        Args:
            new_state: Target state
        """
        self.current_state = new_state
        self.state_history.append(new_state)

    def get_state(self) -> WorkflowState:
        """Get current state."""
        return self.current_state

    def get_history(self) -> list[WorkflowState]:
        """Get state transition history."""
        return self.state_history.copy()
