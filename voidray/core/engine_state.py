
"""
VoidRay Engine State Management
Manages engine lifecycle states and transitions.
"""

from enum import Enum
from typing import Dict, Callable, Optional


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
        self.current_state = EngineState.UNINITIALIZED
        self.previous_state = None
        self.state_callbacks: Dict[EngineState, list] = {state: [] for state in EngineState}
        self.transition_callbacks: Dict[tuple, list] = {}
        
    def transition_to(self, new_state: EngineState):
        """
        Transition to a new engine state.
        
        Args:
            new_state: The state to transition to
        """
        if new_state == self.current_state:
            return
            
        old_state = self.current_state
        self.previous_state = old_state
        self.current_state = new_state
        
        print(f"Engine state: {old_state.value} -> {new_state.value}")
        
        # Call transition callbacks
        transition = (old_state, new_state)
        if transition in self.transition_callbacks:
            for callback in self.transition_callbacks[transition]:
                callback(old_state, new_state)
        
        # Call state enter callbacks
        for callback in self.state_callbacks[new_state]:
            callback()
    
    def add_state_callback(self, state: EngineState, callback: Callable):
        """Add a callback for when entering a specific state."""
        self.state_callbacks[state].append(callback)
    
    def add_transition_callback(self, from_state: EngineState, to_state: EngineState, callback: Callable):
        """Add a callback for a specific state transition."""
        transition = (from_state, to_state)
        if transition not in self.transition_callbacks:
            self.transition_callbacks[transition] = []
        self.transition_callbacks[transition].append(callback)
    
    def is_state(self, state: EngineState) -> bool:
        """Check if engine is in a specific state."""
        return self.current_state == state
    
    def can_transition_to(self, state: EngineState) -> bool:
        """Check if transition to state is valid."""
        valid_transitions = {
            EngineState.UNINITIALIZED: [EngineState.INITIALIZING],
            EngineState.INITIALIZING: [EngineState.RUNNING, EngineState.ERROR],
            EngineState.RUNNING: [EngineState.PAUSED, EngineState.STOPPING],
            EngineState.PAUSED: [EngineState.RUNNING, EngineState.STOPPING],
            EngineState.STOPPING: [EngineState.STOPPED],
            EngineState.STOPPED: [EngineState.INITIALIZING],
            EngineState.ERROR: [EngineState.INITIALIZING, EngineState.STOPPED]
        }
        
        return state in valid_transitions.get(self.current_state, [])
"""
VoidRay Engine State Management
Manages the different states of the game engine.
"""

from enum import Enum
from typing import Optional


class EngineState(Enum):
    """Engine state enumeration."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


class EngineStateManager:
    """
    Manages engine state transitions.
    """
    
    def __init__(self):
        self.current_state = EngineState.UNINITIALIZED
        self.previous_state: Optional[EngineState] = None
    
    def transition_to(self, new_state: EngineState):
        """
        Transition to a new engine state.
        
        Args:
            new_state: The state to transition to
        """
        if self.current_state != new_state:
            print(f"Engine state: {self.current_state.value} -> {new_state.value}")
            self.previous_state = self.current_state
            self.current_state = new_state
    
    def get_current_state(self) -> EngineState:
        """Get the current engine state."""
        return self.current_state
    
    def get_previous_state(self) -> Optional[EngineState]:
        """Get the previous engine state."""
        return self.previous_state
    
    def is_running(self) -> bool:
        """Check if engine is in running state."""
        return self.current_state == EngineState.RUNNING
    
    def is_paused(self) -> bool:
        """Check if engine is paused."""
        return self.current_state == EngineState.PAUSED
