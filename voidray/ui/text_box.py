
"""
VoidRay TextBox Component
Text input UI element.
"""

import pygame
from typing import Optional, Callable
from ..math.vector2 import Vector2
from .ui_element import UIElement


class TextBox(UIElement):
    """
    Text input UI element.
    """
    
    def __init__(self, element_id: str, position: Vector2, size: Vector2, placeholder: str = ""):
        """
        Initialize text box.
        
        Args:
            element_id: Unique identifier
            position: TextBox position
            size: TextBox size
            placeholder: Placeholder text
        """
        super().__init__(element_id, position, size)
        
        self.text = ""
        self.placeholder = placeholder
        self.font_size = 16
        self.text_color = (255, 255, 255)
        self.placeholder_color = (150, 150, 150)
        
        # Text input properties
        self.cursor_position = 0
        self.cursor_visible = True
        self.cursor_blink_timer = 0
        self.cursor_blink_rate = 0.5
        
        # Selection
        self.selection_start = 0
        self.selection_end = 0
        self.has_selection = False
        
        # Input validation
        self.max_length = 100
        self.numeric_only = False
        self.allowed_chars = None  # Set to limit character input
        
        # Callbacks
        self.on_text_changed: Optional[Callable[[str], None]] = None
        self.on_enter_pressed: Optional[Callable[[str], None]] = None
        
        # Visual
        self.background_color = (40, 40, 50)
        self.border_color = (100, 100, 120)
        self.focused_border_color = (150, 150, 200)
        self.border_width = 2
        
        # Text offset for scrolling
        self.text_offset = 0
        self.padding = 5
    
    def on_focus_gained(self):
        """Handle gaining focus."""
        super().on_focus_gained()
        self.border_color = self.focused_border_color
        self.cursor_visible = True
    
    def on_focus_lost(self):
        """Handle losing focus."""
        super().on_focus_lost()
        self.border_color = (100, 100, 120)
        self.cursor_visible = False
        self.has_selection = False
    
    def on_click(self, mouse_pos: Vector2):
        """Handle mouse click to position cursor."""
        super().on_click(mouse_pos)
        
        if self.enabled:
            # Calculate cursor position based on click
            relative_x = mouse_pos.x - self.position.x - self.padding + self.text_offset
            
            # Rough calculation - in real implementation you'd measure actual text
            char_width = self.font_size * 0.6
            clicked_char = max(0, min(len(self.text), int(relative_x / char_width)))
            
            self.cursor_position = clicked_char
            self.has_selection = False
    
    def on_key_down(self, key: int):
        """Handle key press."""
        if not self.enabled:
            return
        
        if key == pygame.K_BACKSPACE:
            if self.has_selection:
                self._delete_selection()
            elif self.cursor_position > 0:
                self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
                self.cursor_position -= 1
                self._on_text_changed()
        
        elif key == pygame.K_DELETE:
            if self.has_selection:
                self._delete_selection()
            elif self.cursor_position < len(self.text):
                self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
                self._on_text_changed()
        
        elif key == pygame.K_LEFT:
            if self.cursor_position > 0:
                self.cursor_position -= 1
                self.has_selection = False
        
        elif key == pygame.K_RIGHT:
            if self.cursor_position < len(self.text):
                self.cursor_position += 1
                self.has_selection = False
        
        elif key == pygame.K_HOME:
            self.cursor_position = 0
            self.has_selection = False
        
        elif key == pygame.K_END:
            self.cursor_position = len(self.text)
            self.has_selection = False
        
        elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
            if self.on_enter_pressed:
                self.on_enter_pressed(self.text)
        
        elif key == pygame.K_a and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Select all
            self.selection_start = 0
            self.selection_end = len(self.text)
            self.has_selection = True
        
        elif key == pygame.K_c and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Copy (would need clipboard implementation)
            pass
        
        elif key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
            # Paste (would need clipboard implementation)
            pass
        
        self._update_text_offset()
    
    def on_text_input(self, text: str):
        """Handle text input."""
        if not self.enabled:
            return
        
        # Filter input
        if self.numeric_only and not text.isdigit():
            return
        
        if self.allowed_chars and text not in self.allowed_chars:
            return
        
        if len(self.text) >= self.max_length:
            return
        
        # Insert text at cursor position
        if self.has_selection:
            self._delete_selection()
        
        self.text = self.text[:self.cursor_position] + text + self.text[self.cursor_position:]
        self.cursor_position += len(text)
        
        self._on_text_changed()
        self._update_text_offset()
    
    def _delete_selection(self):
        """Delete selected text."""
        if self.has_selection:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            
            self.text = self.text[:start] + self.text[end:]
            self.cursor_position = start
            self.has_selection = False
    
    def _on_text_changed(self):
        """Called when text changes."""
        if self.on_text_changed:
            self.on_text_changed(self.text)
    
    def _update_text_offset(self):
        """Update text offset for horizontal scrolling."""
        # Simple scrolling - keep cursor visible
        char_width = self.font_size * 0.6
        cursor_x = self.cursor_position * char_width
        visible_width = self.size.x - 2 * self.padding
        
        if cursor_x - self.text_offset > visible_width:
            self.text_offset = cursor_x - visible_width
        elif cursor_x < self.text_offset:
            self.text_offset = cursor_x
        
        self.text_offset = max(0, self.text_offset)
    
    def update(self, delta_time: float):
        """Update text box."""
        super().update(delta_time)
        
        # Update cursor blink
        if self.focused:
            self.cursor_blink_timer += delta_time
            if self.cursor_blink_timer >= self.cursor_blink_rate:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink_timer = 0
    
    def render(self, renderer):
        """Render the text box."""
        if not self.visible:
            return
        
        # Render background and border
        super().render(renderer)
        
        # Render text
        display_text = self.text if self.text else self.placeholder
        text_color = self.text_color if self.text else self.placeholder_color
        
        text_pos = Vector2(
            self.position.x + self.padding - self.text_offset,
            self.position.y + self.padding
        )
        
        # Clip text to text box bounds
        # Note: In a full implementation, you'd use proper text clipping
        renderer.draw_text(
            display_text,
            text_pos,
            text_color,
            font_size=self.font_size
        )
        
        # Render cursor
        if self.focused and self.cursor_visible and not self.text:
            char_width = self.font_size * 0.6
            cursor_x = self.position.x + self.padding + self.cursor_position * char_width - self.text_offset
            cursor_y = self.position.y + self.padding
            
            if self.position.x + self.padding <= cursor_x <= self.position.x + self.size.x - self.padding:
                renderer.draw_rect(
                    Vector2(cursor_x, cursor_y),
                    Vector2(2, self.font_size),
                    self.text_color,
                    filled=True
                )
    
    def set_text(self, text: str):
        """Set the text content."""
        self.text = text[:self.max_length]
        self.cursor_position = len(self.text)
        self.has_selection = False
        self._update_text_offset()
        self._on_text_changed()
    
    def get_text(self) -> str:
        """Get the current text content."""
        return self.text
    
    def clear(self):
        """Clear the text content."""
        self.set_text("")
