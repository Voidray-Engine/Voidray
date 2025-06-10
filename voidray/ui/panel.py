
"""
VoidRay Panel Component
Container UI element for grouping other elements.
"""

from ..math.vector2 import Vector2
from .ui_element import UIElement


class Panel(UIElement):
    """
    Container UI element for grouping other elements.
    """
    
    def __init__(self, element_id: str, position: Vector2, size: Vector2):
        """
        Initialize panel.
        
        Args:
            element_id: Unique identifier
            position: Panel position
            size: Panel size
        """
        super().__init__(element_id, position, size)
        
        # Default panel appearance
        self.background_color = (60, 60, 80, 180)
        self.border_color = (120, 120, 140)
        self.border_width = 2
        
        # Panel-specific properties
        self.padding = 10
        self.auto_size = False
        
        # Child elements (optional - for layout management)
        self.children = []
    
    def add_child(self, child: UIElement):
        """Add a child element to this panel."""
        if child not in self.children:
            self.children.append(child)
            
            # Position child relative to panel
            if hasattr(child, 'relative_position'):
                child.position = self.position + child.relative_position
    
    def remove_child(self, child: UIElement):
        """Remove a child element from this panel."""
        if child in self.children:
            self.children.remove(child)
    
    def layout_vertical(self, spacing: int = 5):
        """Layout children vertically with spacing."""
        current_y = self.position.y + self.padding
        
        for child in self.children:
            child.position.x = self.position.x + self.padding
            child.position.y = current_y
            current_y += child.size.y + spacing
    
    def layout_horizontal(self, spacing: int = 5):
        """Layout children horizontally with spacing."""
        current_x = self.position.x + self.padding
        
        for child in self.children:
            child.position.x = current_x
            child.position.y = self.position.y + self.padding
            current_x += child.size.x + spacing
    
    def auto_resize_to_content(self):
        """Auto-resize panel to fit its children."""
        if not self.children:
            return
        
        min_x = min(child.position.x for child in self.children)
        min_y = min(child.position.y for child in self.children)
        max_x = max(child.position.x + child.size.x for child in self.children)
        max_y = max(child.position.y + child.size.y for child in self.children)
        
        # Update panel size and position
        self.position = Vector2(min_x - self.padding, min_y - self.padding)
        self.size = Vector2(
            max_x - min_x + 2 * self.padding,
            max_y - min_y + 2 * self.padding
        )
    
    def update(self, delta_time: float):
        """Update panel and its children."""
        super().update(delta_time)
        
        # Update children if managing them
        for child in self.children:
            if hasattr(child, 'update'):
                child.update(delta_time)
    
    def render(self, renderer):
        """Render the panel."""
        if not self.visible:
            return
        
        # Render panel background and border
        super().render(renderer)
        
        # Note: Children are rendered by the UI manager separately
        # This allows for proper z-ordering across all UI elements
