"""
VoidRay Component System

Base component class for implementing the component-based architecture
that allows for modular and reusable game object functionality.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game_object import GameObject


class Component:
    """
    Base class for all components that can be attached to game objects.
    Components provide specific functionality and behavior to game objects.
    """
    
    def __init__(self):
        """Initialize the component."""
        self.enabled = True
        self.game_object: 'GameObject' = None
    
    def on_attach(self) -> None:
        """
        Called when this component is attached to a game object.
        Override in subclasses for initialization logic.
        """
        pass
    
    def on_detach(self) -> None:
        """
        Called when this component is detached from a game object.
        Override in subclasses for cleanup logic.
        """
        pass
    
    def update(self, delta_time: float) -> None:
        """
        Update the component logic.
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable this component.
        
        Args:
            enabled: Whether the component should be enabled
        """
        self.enabled = enabled
    
    @property
    def transform(self):
        """Get the transform of the attached game object."""
        return self.game_object.transform if self.game_object else None
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(enabled={self.enabled})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(enabled={self.enabled}, game_object={self.game_object.name if self.game_object else None})"
