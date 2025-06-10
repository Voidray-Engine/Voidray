
from typing import Dict, List, Callable, Any
from enum import Enum


class EventType(Enum):
    """Built-in event types."""
    PLAYER_DIED = "player_died"
    SCORE_CHANGED = "score_changed"
    LEVEL_COMPLETED = "level_completed"
    ITEM_COLLECTED = "item_collected"
    ENEMY_DEFEATED = "enemy_defeated"
    GAME_PAUSED = "game_paused"
    GAME_RESUMED = "game_resumed"


class GameEvent:
    """Represents a game event with data."""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        """
        Initialize game event.
        
        Args:
            event_type: Type of event
            data: Optional event data
        """
        self.type = event_type
        self.data = data or {}
        self.timestamp = None
        
        # Set timestamp if available
        try:
            import time
            self.timestamp = time.time()
        except:
            pass


class EventSystem:
    """
    Global event system for game-wide communication.
    """
    
    def __init__(self):
        """Initialize the event system."""
        self.listeners: Dict[str, List[Callable]] = {}
        self.event_queue: List[GameEvent] = []
        self.enabled = True
    
    def subscribe(self, event_type: str, callback: Callable[[GameEvent], None]):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(callback)
        print(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: Type of event
            callback: Callback function to remove
        """
        if event_type in self.listeners:
            if callback in self.listeners[event_type]:
                self.listeners[event_type].remove(callback)
    
    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """
        Emit an event.
        
        Args:
            event_type: Type of event
            data: Optional event data
        """
        if not self.enabled:
            return
            
        event = GameEvent(event_type, data)
        self.event_queue.append(event)
    
    def process_events(self):
        """Process all queued events."""
        if not self.enabled:
            return
            
        for event in self.event_queue:
            self._dispatch_event(event)
        
        self.event_queue.clear()
    
    def _dispatch_event(self, event: GameEvent):
        """Dispatch an event to all listeners."""
        if event.type in self.listeners:
            for callback in self.listeners[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback for {event.type}: {e}")
    
    def get_listener_count(self, event_type: str = None) -> int:
        """Get number of listeners for an event type or total."""
        if event_type:
            return len(self.listeners.get(event_type, []))
        else:
            return sum(len(listeners) for listeners in self.listeners.values())
    
    def clear_listeners(self, event_type: str = None):
        """Clear listeners for a specific event type or all."""
        if event_type:
            if event_type in self.listeners:
                self.listeners[event_type].clear()
        else:
            self.listeners.clear()
    
    def enable(self):
        """Enable the event system."""
        self.enabled = True
        
    def disable(self):
        """Disable the event system."""
        self.enabled = False


# Global event system instance
event_system = EventSystem()
