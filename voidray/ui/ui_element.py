
"""
VoidRay UI Element Base Class
Base class for all UI elements.
"""

import pygame
from typing import Optional, Set, Callable, Any
from ..math.vector2 import Vector2


class UIElement:
    """
    Base class for all UI elements.
    """
    
    def __init__(self, element_id: str, position: Vector2 = None, size: Vector2 = None):
        """
        Initialize UI element.
        
        Args:
            element_id: Unique identifier for this element
            position: Position in screen coordinates
            size: Size of the element
        """
        self.id = element_id
        self.position = position or Vector2(0, 0)
        self.size = size or Vector2(100, 30)
        
        # State
        self.visible = True
        self.active = True
        self.enabled = True
        self.focused = False
        self.hovered = False
        
        # Interaction
        self.draggable = False
        self.clickable = True
        
        # Visual properties
        self.background_color = (100, 100, 100, 200)
        self.border_color = (150, 150, 150)
        self.border_width = 1
        self.z_order = 0
        
        # Tags for grouping
        self.tags: Set[str] = set()
        
        # Parent UI manager
        self.ui_manager = None
        
        # Event callbacks
        self.on_click_callback: Optional[Callable] = None
        self.on_hover_callback: Optional[Callable] = None
        self.on_focus_callback: Optional[Callable] = None
    
    def set_position(self, position: Vector2):
        """Set the position of this element."""
        self.position = position
    
    def set_size(self, size: Vector2):
        """Set the size of this element."""
        self.size = size
    
    def get_rect(self) -> pygame.Rect:
        """Get the rectangle bounds of this element."""
        return pygame.Rect(self.position.x, self.position.y, self.size.x, self.size.y)
    
    def contains_point(self, point: Vector2) -> bool:
        """Check if a point is inside this element."""
        return (self.position.x <= point.x <= self.position.x + self.size.x and
                self.position.y <= point.y <= self.position.y + self.size.y)
    
    def add_tag(self, tag: str):
        """Add a tag to this element."""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str):
        """Remove a tag from this element."""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if this element has a specific tag."""
        return tag in self.tags
    
    # Event handlers (override in subclasses)
    def on_click(self, mouse_pos: Vector2):
        """Called when the element is clicked."""
        if self.on_click_callback:
            self.on_click_callback(mouse_pos)
    
    def on_mouse_enter(self):
        """Called when mouse enters the element."""
        self.hovered = True
        if self.on_hover_callback:
            self.on_hover_callback(True)
    
    def on_mouse_exit(self):
        """Called when mouse leaves the element."""
        self.hovered = False
        if self.on_hover_callback:
            self.on_hover_callback(False)
    
    def on_focus_gained(self):
        """Called when the element gains focus."""
        self.focused = True
        if self.on_focus_callback:
            self.on_focus_callback(True)
    
    def on_focus_lost(self):
        """Called when the element loses focus."""
        self.focused = False
        if self.on_focus_callback:
            self.on_focus_callback(False)
    
    def on_key_down(self, key: int):
        """Called when a key is pressed while this element has focus."""
        pass
    
    def on_key_up(self, key: int):
        """Called when a key is released while this element has focus."""
        pass
    
    def on_text_input(self, text: str):
        """Called when text is input while this element has focus."""
        pass
    
    def on_drag(self, mouse_pos: Vector2):
        """Called while the element is being dragged."""
        pass
    
    def on_drag_end(self, mouse_pos: Vector2):
        """Called when dragging ends."""
        pass
    
    # Update and render (override in subclasses)
    def update(self, delta_time: float):
        """Update the element (called every frame)."""
        pass
    
    def render(self, renderer):
        """Render the element."""
        if not self.visible:
            return
        
        # Draw background
        if self.background_color[3] > 0:  # Has alpha
            rect = self.get_rect()
            if hasattr(renderer, 'draw_rect_alpha'):
                renderer.draw_rect_alpha(
                    Vector2(rect.x, rect.y),
                    Vector2(rect.width, rect.height),
                    self.background_color
                )
            else:
                # Fallback to regular rect
                renderer.draw_rect(
                    Vector2(rect.x, rect.y),
                    Vector2(rect.width, rect.height),
                    self.background_color[:3],
                    filled=True
                )
        
        # Draw border
        if self.border_width > 0:
            rect = self.get_rect()
            renderer.draw_rect(
                Vector2(rect.x, rect.y),
                Vector2(rect.width, rect.height),
                self.border_color,
                filled=False
            )
    
    def show(self):
        """Show the element."""
        self.visible = True
    
    def hide(self):
        """Hide the element."""
        self.visible = False
    
    def enable(self):
        """Enable the element."""
        self.enabled = True
    
    def disable(self):
        """Disable the element."""
        self.enabled = False
        if self.focused and self.ui_manager:
            self.ui_manager.clear_focus()
    
    def destroy(self):
        """Destroy the element and remove it from the UI manager."""
        if self.ui_manager:
            self.ui_manager.remove_element(self)
