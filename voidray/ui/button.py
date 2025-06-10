
"""
VoidRay Button Component
Interactive button UI element.
"""

import pygame
from typing import Callable, Optional
from ..math.vector2 import Vector2
from .ui_element import UIElement


class Button(UIElement):
    """
    Interactive button UI element.
    """
    
    def __init__(self, element_id: str, text: str, position: Vector2, size: Vector2 = None):
        """
        Initialize button.
        
        Args:
            element_id: Unique identifier
            text: Button text
            position: Button position
            size: Button size (auto-sized if None)
        """
        # Auto-size if not provided
        if size is None:
            text_width = len(text) * 12 + 20  # Rough estimate
            size = Vector2(max(80, text_width), 30)
        
        super().__init__(element_id, position, size)
        
        self.text = text
        self.font_size = 16
        self.text_color = (255, 255, 255)
        self.text_color_hovered = (255, 255, 200)
        self.text_color_pressed = (200, 200, 200)
        
        # Button states
        self.pressed = False
        
        # Colors for different states
        self.normal_color = (80, 80, 100)
        self.hovered_color = (100, 100, 120)
        self.pressed_color = (60, 60, 80)
        self.disabled_color = (50, 50, 50)
        
        self.background_color = self.normal_color
        self.border_color = (150, 150, 150)
        self.border_width = 2
    
    def on_click(self, mouse_pos: Vector2):
        """Handle button click."""
        if not self.enabled:
            return
        
        self.pressed = True
        super().on_click(mouse_pos)
        print(f"Button clicked: {self.text}")
    
    def on_mouse_enter(self):
        """Handle mouse enter."""
        super().on_mouse_enter()
        if self.enabled:
            self.background_color = self.hovered_color
    
    def on_mouse_exit(self):
        """Handle mouse exit."""
        super().on_mouse_exit()
        self.pressed = False
        if self.enabled:
            self.background_color = self.normal_color
        else:
            self.background_color = self.disabled_color
    
    def update(self, delta_time: float):
        """Update button state."""
        super().update(delta_time)
        
        # Reset pressed state
        if self.pressed:
            self.pressed = False
            if self.hovered:
                self.background_color = self.hovered_color
            else:
                self.background_color = self.normal_color
        
        # Update colors based on state
        if not self.enabled:
            self.background_color = self.disabled_color
    
    def render(self, renderer):
        """Render the button."""
        if not self.visible:
            return
        
        # Render base element (background and border)
        super().render(renderer)
        
        # Determine text color
        if not self.enabled:
            text_color = (100, 100, 100)
        elif self.pressed:
            text_color = self.text_color_pressed
        elif self.hovered:
            text_color = self.text_color_hovered
        else:
            text_color = self.text_color
        
        # Render text centered
        text_pos = Vector2(
            self.position.x + self.size.x // 2,
            self.position.y + self.size.y // 2
        )
        
        # Get text size for centering
        if hasattr(renderer, 'get_text_size'):
            text_width, text_height = renderer.get_text_size(self.text, self.font_size)
            text_pos.x -= text_width // 2
            text_pos.y -= text_height // 2
        
        renderer.draw_text(
            self.text,
            text_pos,
            text_color,
            font_size=self.font_size
        )
    
    def set_text(self, text: str):
        """Set the button text."""
        self.text = text
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        self.enabled = enabled
        if not enabled:
            self.background_color = self.disabled_color
            if self.ui_manager and self.focused:
                self.ui_manager.clear_focus()
        else:
            self.background_color = self.normal_color
