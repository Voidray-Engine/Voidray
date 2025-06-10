
"""
VoidRay Message System
Handles structured messaging for multiplayer games.
"""

import time
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Message:
    """Base message structure."""
    type: str
    data: Dict[str, Any]
    sender_id: Optional[str] = None
    timestamp: float = None
    priority: MessagePriority = MessagePriority.NORMAL
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class MessageSystem:
    """
    Advanced message system for handling game communications.
    Supports message queuing, filtering, and priority handling.
    """
    
    def __init__(self):
        self.message_queue: List[Message] = []
        self.handlers: Dict[str, List[Callable]] = {}
        self.filters: List[Callable] = []
        self.max_queue_size = 1000
        
    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type."""
        if message_type not in self.handlers:
            self.handlers[message_type] = []
        self.handlers[message_type].append(handler)
    
    def unregister_handler(self, message_type: str, handler: Callable):
        """Unregister a handler for a specific message type."""
        if message_type in self.handlers:
            try:
                self.handlers[message_type].remove(handler)
                if not self.handlers[message_type]:
                    del self.handlers[message_type]
            except ValueError:
                pass
    
    def add_filter(self, filter_func: Callable):
        """Add a message filter function."""
        self.filters.append(filter_func)
    
    def send_message(self, message_type: str, data: Dict[str, Any], 
                    sender_id: str = None, priority: MessagePriority = MessagePriority.NORMAL):
        """Send a message through the system."""
        message = Message(message_type, data, sender_id, priority=priority)
        
        # Apply filters
        for filter_func in self.filters:
            if not filter_func(message):
                return False
        
        # Add to queue with priority sorting
        self.message_queue.append(message)
        self.message_queue.sort(key=lambda x: x.priority.value, reverse=True)
        
        # Maintain queue size limit
        if len(self.message_queue) > self.max_queue_size:
            self.message_queue.pop()
        
        return True
    
    def process_messages(self):
        """Process all queued messages."""
        processed_count = 0
        
        while self.message_queue:
            message = self.message_queue.pop(0)
            
            if message.type in self.handlers:
                for handler in self.handlers[message.type]:
                    try:
                        handler(message)
                    except Exception as e:
                        print(f"Error processing message {message.type}: {e}")
            
            processed_count += 1
        
        return processed_count
    
    def get_queued_message_count(self) -> int:
        """Get the number of queued messages."""
        return len(self.message_queue)
    
    def clear_queue(self):
        """Clear all queued messages."""
        self.message_queue.clear()
    
    def get_handlers_for_type(self, message_type: str) -> List[Callable]:
        """Get all handlers for a specific message type."""
        return self.handlers.get(message_type, [])
    
    def broadcast_message(self, message_type: str, data: Dict[str, Any], 
                         priority: MessagePriority = MessagePriority.NORMAL):
        """Broadcast a message to all handlers immediately."""
        message = Message(message_type, data, priority=priority)
        
        # Apply filters
        for filter_func in self.filters:
            if not filter_func(message):
                return False
        
        # Process immediately
        if message_type in self.handlers:
            for handler in self.handlers[message_type]:
                try:
                    handler(message)
                except Exception as e:
                    print(f"Error broadcasting message {message_type}: {e}")
        
        return True
