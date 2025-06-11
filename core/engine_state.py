"""
VoidRay Engine State Management
Manages engine lifecycle states and transitions.
"""

from enum import Enum
from typing import Dict, Callable, Optional, List


class EngineState(Enum):
    """Engine states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class EngineStateManager:
    """
    Manages engine state transitions and callbacks.
    """

    def __init__(self):
        """Initialize the state manager."""
        self.current_state = EngineState.UNINITIALIZED
        self.previous_state = None
        self.state_callbacks: Dict[EngineState, List[Callable]] = {
            state: [] for state in EngineState
        }
        self.transition_callbacks: List[Callable[[EngineState, EngineState], None]] = []

    def transition_to(self, new_state: EngineState) -> bool:
        """
        Transition to a new state.

        Args:
            new_state: The state to transition to

        Returns:
            True if transition was successful, False otherwise
        """
        if not self._is_valid_transition(self.current_state, new_state):
            print(f"Invalid state transition: {self.current_state} -> {new_state}")
            return False

        old_state = self.current_state
        self.previous_state = old_state
        self.current_state = new_state

        # Call transition callbacks
        for callback in self.transition_callbacks:
            try:
                callback(old_state, new_state)
            except Exception as e:
                print(f"Error in state transition callback: {e}")

        # Call state-specific callbacks
        for callback in self.state_callbacks[new_state]:
            try:
                callback()
            except Exception as e:
                print(f"Error in state callback: {e}")

        return True

    def _is_valid_transition(self, from_state: EngineState, to_state: EngineState) -> bool:
        """Check if a state transition is valid."""
        # Define valid transitions
        valid_transitions = {
            EngineState.UNINITIALIZED: [EngineState.INITIALIZING, EngineState.ERROR],
            EngineState.INITIALIZING: [EngineState.RUNNING, EngineState.ERROR],
            EngineState.RUNNING: [EngineState.PAUSED, EngineState.STOPPING, EngineState.ERROR],
            EngineState.PAUSED: [EngineState.RUNNING, EngineState.STOPPING, EngineState.ERROR],
            EngineState.STOPPING: [EngineState.STOPPED, EngineState.ERROR],
            EngineState.STOPPED: [EngineState.INITIALIZING],
            EngineState.ERROR: [EngineState.STOPPED, EngineState.INITIALIZING]
        }

        return to_state in valid_transitions.get(from_state, [])

    def add_state_callback(self, state: EngineState, callback: Callable):
        """Add a callback for when entering a specific state."""
        self.state_callbacks[state].append(callback)

    def add_transition_callback(self, callback: Callable[[EngineState, EngineState], None]):
        """Add a callback for any state transition."""
        self.transition_callbacks.append(callback)

    def get_current_state(self) -> EngineState:
        """Get the current engine state."""
        return self.current_state

    def is_running(self) -> bool:
        """Check if the engine is in a running state."""
        return self.current_state == EngineState.RUNNING

    def is_paused(self) -> bool:
        """Check if the engine is paused."""
        return self.current_state == EngineState.PAUSED

    def is_stopped(self) -> bool:
        """Check if the engine is stopped."""
        return self.current_state == EngineState.STOPPED