
"""
VoidRay UI Manager
Manages UI elements, events, and rendering.
"""

import pygame
from typing import Dict, List, Optional, Callable
from ..math.vector2 import Vector2
from .ui_element import UIElement


class UIManager:
    """
    Manages all UI elements in the game.
    """
    
    def __init__(self):
        """Initialize the UI manager."""
        self.elements: List[UIElement] = []
        self.focused_element: Optional[UIElement] = None
        self.hovered_element: Optional[UIElement] = None
        self.dragging_element: Optional[UIElement] = None
        self.drag_offset = Vector2(0, 0)
        
        # UI state
        self.mouse_position = Vector2(0, 0)
        self.mouse_pressed = False
        self.mouse_just_pressed = False
        self.mouse_just_released = False
        
        # Input handling
        self.key_pressed = {}
        self.text_input = ""
        
        print("UI Manager initialized")
    
    def add_element(self, element: UIElement):
        """Add a UI element to the manager."""
        if element not in self.elements:
            self.elements.append(element)
            element.ui_manager = self
            print(f"Added UI element: {element.__class__.__name__}")
    
    def remove_element(self, element: UIElement):
        """Remove a UI element from the manager."""
        if element in self.elements:
            self.elements.remove(element)
            
            # Clear references if this was the focused/hovered element
            if self.focused_element == element:
                self.focused_element = None
            if self.hovered_element == element:
                self.hovered_element = None
            if self.dragging_element == element:
                self.dragging_element = None
            
            element.ui_manager = None
            print(f"Removed UI element: {element.__class__.__name__}")
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events for UI interaction."""
        # Update mouse state
        if event.type == pygame.MOUSEMOTION:
            self.mouse_position = Vector2(event.pos[0], event.pos[1])
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.mouse_just_pressed = True
                self.mouse_pressed = True
                self.mouse_position = Vector2(event.pos[0], event.pos[1])
                
                # Check which element was clicked
                clicked_element = self.get_element_at_position(self.mouse_position)
                
                if clicked_element:
                    self.set_focus(clicked_element)
                    
                    # Start dragging if element is draggable
                    if clicked_element.draggable:
                        self.dragging_element = clicked_element
                        self.drag_offset = self.mouse_position - clicked_element.position
                    
                    # Trigger click event
                    clicked_element.on_click(self.mouse_position)
                else:
                    self.set_focus(None)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.mouse_just_released = True
                self.mouse_pressed = False
                
                # Stop dragging
                if self.dragging_element:
                    self.dragging_element.on_drag_end(self.mouse_position)
                    self.dragging_element = None
        
        elif event.type == pygame.KEYDOWN:
            self.key_pressed[event.key] = True
            
            # Send key event to focused element
            if self.focused_element:
                self.focused_element.on_key_down(event.key)
        
        elif event.type == pygame.KEYUP:
            if event.key in self.key_pressed:
                del self.key_pressed[event.key]
            
            # Send key event to focused element
            if self.focused_element:
                self.focused_element.on_key_up(event.key)
        
        elif event.type == pygame.TEXTINPUT:
            self.text_input = event.text
            
            # Send text input to focused element
            if self.focused_element:
                self.focused_element.on_text_input(event.text)
    
    def update(self, delta_time: float):
        """Update all UI elements."""
        # Reset per-frame input flags
        self.mouse_just_pressed = False
        self.mouse_just_released = False
        self.text_input = ""
        
        # Update hover state
        hovered = self.get_element_at_position(self.mouse_position)
        if hovered != self.hovered_element:
            if self.hovered_element:
                self.hovered_element.on_mouse_exit()
            if hovered:
                hovered.on_mouse_enter()
            self.hovered_element = hovered
        
        # Handle dragging
        if self.dragging_element:
            new_position = self.mouse_position - self.drag_offset
            self.dragging_element.set_position(new_position)
            self.dragging_element.on_drag(self.mouse_position)
        
        # Update all elements
        for element in self.elements[:]:  # Copy list to allow modification during iteration
            if element.active:
                element.update(delta_time)
    
    def render(self, renderer):
        """Render all UI elements."""
        # Sort elements by z-order
        sorted_elements = sorted(self.elements, key=lambda e: e.z_order)
        
        for element in sorted_elements:
            if element.visible:
                element.render(renderer)
    
    def get_element_at_position(self, position: Vector2) -> Optional[UIElement]:
        """Get the topmost UI element at the given position."""
        # Check in reverse z-order (highest first)
        sorted_elements = sorted(self.elements, key=lambda e: e.z_order, reverse=True)
        
        for element in sorted_elements:
            if element.visible and element.contains_point(position):
                return element
        
        return None
    
    def set_focus(self, element: Optional[UIElement]):
        """Set the focused UI element."""
        if self.focused_element != element:
            if self.focused_element:
                self.focused_element.on_focus_lost()
            
            self.focused_element = element
            
            if self.focused_element:
                self.focused_element.on_focus_gained()
    
    def clear_focus(self):
        """Clear the currently focused element."""
        self.set_focus(None)
    
    def find_element_by_id(self, element_id: str) -> Optional[UIElement]:
        """Find a UI element by its ID."""
        for element in self.elements:
            if element.id == element_id:
                return element
        return None
    
    def find_elements_by_tag(self, tag: str) -> List[UIElement]:
        """Find all UI elements with a specific tag."""
        return [element for element in self.elements if tag in element.tags]
    
    def clear_all(self):
        """Remove all UI elements."""
        self.elements.clear()
        self.focused_element = None
        self.hovered_element = None
        self.dragging_element = None
        print("All UI elements cleared")
    
    def create_simple_menu(self, title: str, buttons: List[tuple]) -> List[UIElement]:
        """
        Create a simple menu with buttons.
        
        Args:
            title: Menu title
            buttons: List of (button_text, callback_function) tuples
            
        Returns:
            List of created UI elements
        """
        from .label import Label
        from .button import Button
        from .panel import Panel
        
        elements = []
        
        # Create background panel
        panel = Panel("menu_panel", Vector2(300, 400), Vector2(250, 300))
        panel.background_color = (50, 50, 70, 200)
        panel.border_color = (100, 100, 120)
        panel.border_width = 2
        elements.append(panel)
        
        # Create title label
        title_label = Label("menu_title", title, Vector2(325, 200))
        title_label.font_size = 32
        title_label.color = (255, 255, 255)
        elements.append(title_label)
        
        # Create buttons
        button_y = 250
        for i, (button_text, callback) in enumerate(buttons):
            button = Button(f"menu_button_{i}", button_text, Vector2(325, button_y))
            button.size = Vector2(200, 40)
            button.on_click_callback = callback
            elements.append(button)
            button_y += 50
        
        # Add all elements to manager
        for element in elements:
            self.add_element(element)
        
        return elements
    
    def show_message_box(self, title: str, message: str, callback: Callable = None) -> List[UIElement]:
        """Show a simple message box."""
        from .label import Label
        from .button import Button
        from .panel import Panel
        
        elements = []
        
        # Background panel
        panel = Panel("message_panel", Vector2(200, 150), Vector2(400, 200))
        panel.background_color = (40, 40, 40, 220)
        panel.border_color = (150, 150, 150)
        panel.border_width = 2
        elements.append(panel)
        
        # Title
        title_label = Label("message_title", title, Vector2(250, 120))
        title_label.font_size = 24
        title_label.color = (255, 255, 255)
        elements.append(title_label)
        
        # Message
        msg_label = Label("message_text", message, Vector2(250, 160))
        msg_label.font_size = 16
        msg_label.color = (200, 200, 200)
        elements.append(msg_label)
        
        # OK button
        def ok_clicked(pos):
            for elem in elements:
                self.remove_element(elem)
            if callback:
                callback()
        
        ok_button = Button("message_ok", "OK", Vector2(250, 220))
        ok_button.size = Vector2(80, 30)
        ok_button.on_click_callback = ok_clicked
        elements.append(ok_button)
        
        # Add elements
        for element in elements:
            self.add_element(element)
        
        return elements
