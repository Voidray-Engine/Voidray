"""
VoidRay Renderer

The main rendering system that handles drawing sprites, shapes, and other
visual elements to the screen.
"""

import pygame
from typing import Optional, Tuple
from ..math.vector2 import Vector2
from ..utils.color import Color
from .camera import Camera


class Renderer:
    """
    The main renderer responsible for drawing all visual elements to the screen.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.
        
        Args:
            screen: The pygame surface to render to
        """
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.camera: Optional[Camera] = None
        self.clear_color = Color.BLACK
    
    def set_camera(self, camera: Camera) -> None:
        """
        Set the active camera for rendering.
        
        Args:
            camera: The camera to use for rendering
        """
        self.camera = camera
    
    def set_clear_color(self, color: Color) -> None:
        """
        Set the background clear color.
        
        Args:
            color: The color to use for clearing the screen
        """
        self.clear_color = color
    
    def clear(self) -> None:
        """Clear the screen with the current clear color."""
        self.screen.fill(self.clear_color.to_tuple())
    
    def present(self) -> None:
        """Present the rendered frame to the screen."""
        pygame.display.flip()
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in world space
            
        Returns:
            Position in screen space
        """
        if self.camera:
            return self.camera.world_to_screen(world_pos)
        return world_pos
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen space
            
        Returns:
            Position in world space
        """
        if self.camera:
            return self.camera.screen_to_world(screen_pos)
        return screen_pos
    
    def draw_sprite(self, surface: pygame.Surface, position: Vector2, 
                   rotation: float = 0, scale: Vector2 = Vector2(1, 1)) -> None:
        """
        Draw a sprite to the screen.
        
        Args:
            surface: The pygame surface to draw
            position: World position to draw at
            rotation: Rotation in degrees
            scale: Scale factor
        """
        if not surface:
            return
        
        # Transform position to screen space
        screen_pos = self.world_to_screen(position)
        
        # Apply transformations
        if rotation != 0 or scale != Vector2(1, 1):
            # Scale the surface
            if scale != Vector2(1, 1):
                new_width = int(surface.get_width() * scale.x)
                new_height = int(surface.get_height() * scale.y)
                surface = pygame.transform.scale(surface, (new_width, new_height))
            
            # Rotate the surface
            if rotation != 0:
                surface = pygame.transform.rotate(surface, -rotation)  # Negative for correct direction
        
        # Calculate position to center the sprite
        rect = surface.get_rect()
        rect.center = (int(screen_pos.x), int(screen_pos.y))
        
        self.screen.blit(surface, rect)
    
    def draw_rect(self, position: Vector2, size: Vector2, color: Color, 
                  filled: bool = True, width: int = 1) -> None:
        """
        Draw a rectangle.
        
        Args:
            position: Top-left corner position in world space
            size: Width and height of the rectangle
            color: Color to draw with
            filled: Whether to fill the rectangle
            width: Line width for unfilled rectangles
        """
        screen_pos = self.world_to_screen(position)
        rect = pygame.Rect(int(screen_pos.x), int(screen_pos.y), 
                          int(size.x), int(size.y))
        
        if filled:
            pygame.draw.rect(self.screen, color.to_tuple(), rect)
        else:
            pygame.draw.rect(self.screen, color.to_tuple(), rect, width)
    
    def draw_circle(self, center: Vector2, radius: float, color: Color, 
                   filled: bool = True, width: int = 1) -> None:
        """
        Draw a circle.
        
        Args:
            center: Center position in world space
            radius: Radius of the circle
            color: Color to draw with
            filled: Whether to fill the circle
            width: Line width for unfilled circles
        """
        screen_pos = self.world_to_screen(center)
        
        if filled:
            pygame.draw.circle(self.screen, color.to_tuple(), 
                             (int(screen_pos.x), int(screen_pos.y)), int(radius))
        else:
            pygame.draw.circle(self.screen, color.to_tuple(), 
                             (int(screen_pos.x), int(screen_pos.y)), int(radius), width)
    
    def draw_line(self, start: Vector2, end: Vector2, color: Color, width: int = 1) -> None:
        """
        Draw a line.
        
        Args:
            start: Start position in world space
            end: End position in world space
            color: Color to draw with
            width: Line width
        """
        screen_start = self.world_to_screen(start)
        screen_end = self.world_to_screen(end)
        
        pygame.draw.line(self.screen, color.to_tuple(),
                        (int(screen_start.x), int(screen_start.y)),
                        (int(screen_end.x), int(screen_end.y)), width)
    
    def draw_text(self, text: str, position: Vector2, color: Color, 
                  font_size: int = 24, font_name: str = None) -> None:
        """
        Draw text to the screen.
        
        Args:
            text: The text to draw
            position: Position in world space
            color: Text color
            font_size: Font size
            font_name: Font name (None for default)
        """
        screen_pos = self.world_to_screen(position)
        font = pygame.font.Font(font_name, font_size)
        text_surface = font.render(text, True, color.to_tuple())
        self.screen.blit(text_surface, (int(screen_pos.x), int(screen_pos.y)))
    
    def get_screen_size(self) -> Vector2:
        """Get the screen dimensions."""
        return Vector2(self.screen_width, self.screen_height)
