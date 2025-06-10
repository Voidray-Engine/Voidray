
"""
VoidRay Label Component
Text display UI element.
"""

from ..math.vector2 import Vector2
from .ui_element import UIElement


class Label(UIElement):
    """
    Text display UI element.
    """
    
    def __init__(self, element_id: str, text: str, position: Vector2, font_size: int = 16):
        """
        Initialize label.
        
        Args:
            element_id: Unique identifier
            text: Label text
            position: Label position
            font_size: Font size
        """
        super().__init__(element_id, position, Vector2(0, 0))
        
        self.text = text
        self.font_size = font_size
        self.color = (255, 255, 255)
        
        # Labels don't need background by default
        self.background_color = (0, 0, 0, 0)
        self.border_width = 0
        
        # Labels are not interactive by default
        self.clickable = False
        
        # Text alignment
        self.alignment = "left"  # "left", "center", "right"
        
        # Auto-size based on text
        self._update_size()
    
    def _update_size(self):
        """Update size based on text content."""
        # Rough estimation - in a real implementation you'd measure the actual text
        char_width = self.font_size * 0.6
        char_height = self.font_size
        
        lines = self.text.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0
        
        self.size = Vector2(
            int(max_width * char_width),
            int(len(lines) * char_height)
        )
    
    def set_text(self, text: str):
        """Set the label text."""
        self.text = text
        self._update_size()
    
    def set_color(self, color: tuple):
        """Set the text color."""
        self.color = color
    
    def set_font_size(self, size: int):
        """Set the font size."""
        self.font_size = size
        self._update_size()
    
    def set_alignment(self, alignment: str):
        """Set text alignment ('left', 'center', 'right')."""
        if alignment in ["left", "center", "right"]:
            self.alignment = alignment
    
    def render(self, renderer):
        """Render the label."""
        if not self.visible:
            return
        
        # Render background if needed
        super().render(renderer)
        
        # Split text into lines
        lines = self.text.split('\n')
        line_height = self.font_size * 1.2
        
        for i, line in enumerate(lines):
            line_pos = Vector2(self.position.x, self.position.y + i * line_height)
            
            # Apply alignment
            if self.alignment == "center":
                if hasattr(renderer, 'get_text_size'):
                    text_width, _ = renderer.get_text_size(line, self.font_size)
                    line_pos.x += (self.size.x - text_width) // 2
            elif self.alignment == "right":
                if hasattr(renderer, 'get_text_size'):
                    text_width, _ = renderer.get_text_size(line, self.font_size)
                    line_pos.x += self.size.x - text_width
            
            renderer.draw_text(
                line,
                line_pos,
                self.color,
                font_size=self.font_size
            )
