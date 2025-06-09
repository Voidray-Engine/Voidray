"""
VoidRay Renderer
Core rendering system for 2D graphics.
"""

import pygame
from typing import Tuple, Optional
from ..math.vector2 import Vector2


class Color:
    """
    Color utility class with common color constants.
    """
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    DARK_GRAY = (64, 64, 64)


class Renderer:
    """
    The main rendering system for VoidRay. Handles all drawing operations.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.
        
        Args:
            screen: The pygame surface to render to
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.camera_offset = Vector2(0, 0)
        self.background_color = Color.BLACK
    
    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """
        Clear the screen with the specified color.
        
        Args:
            color: RGB color tuple, defaults to background_color
        """
        if color is None:
            color = self.background_color
        self.screen.fill(color)
    
    def present(self):
        """
        Present the rendered frame to the screen.
        """
        pygame.display.flip()
    
    def set_camera_offset(self, offset: Vector2):
        """
        Set the camera offset for world-to-screen coordinate conversion.
        
        Args:
            offset: Camera offset as Vector2
        """
        self.camera_offset = offset
    
    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_pos: Position in world space
            
        Returns:
            Position in screen space
        """
        return world_pos - self.camera_offset
    
    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_pos: Position in screen space
            
        Returns:
            Position in world space
        """
        return screen_pos + self.camera_offset
    
    def draw_sprite(self, surface: pygame.Surface, position: Vector2, 
                   rotation: float = 0, scale: Vector2 = None):
        """
        Draw a sprite surface at the specified position.
        
        Args:
            surface: The pygame surface to draw
            position: World position to draw at
            rotation: Rotation in degrees
            scale: Scale factor as Vector2
        """
        if scale is None:
            scale = Vector2(1, 1)
        
        # Apply transformations
        transformed_surface = surface
        
        # Scale
        if scale.x != 1 or scale.y != 1:
            new_width = int(surface.get_width() * scale.x)
            new_height = int(surface.get_height() * scale.y)
            transformed_surface = pygame.transform.scale(transformed_surface, (new_width, new_height))
        
        # Rotate
        if rotation != 0:
            transformed_surface = pygame.transform.rotate(transformed_surface, rotation)
        
        # Convert to screen coordinates
        screen_pos = self.world_to_screen(position)
        
        # Center the sprite on the position
        rect = transformed_surface.get_rect()
        rect.center = (screen_pos.x, screen_pos.y)
        
        self.screen.blit(transformed_surface, rect)
    
    def draw_rect(self, position: Vector2, size: Vector2, 
                  color: Tuple[int, int, int], filled: bool = True):
        """
        Draw a rectangle.
        
        Args:
            position: Top-left corner position
            size: Width and height as Vector2
            color: RGB color tuple
            filled: Whether to fill the rectangle or just draw outline
        """
        screen_pos = self.world_to_screen(position)
        rect = pygame.Rect(screen_pos.x, screen_pos.y, size.x, size.y)
        
        if filled:
            pygame.draw.rect(self.screen, color, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, 1)
    
    def draw_circle(self, center: Vector2, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True):
        """
        Draw a circle.
        
        Args:
            center: Center position
            radius: Circle radius
            color: RGB color tuple
            filled: Whether to fill the circle or just draw outline
        """
        screen_pos = self.world_to_screen(center)
        
        if filled:
            pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius))
        else:
            pygame.draw.circle(self.screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius), 1)
    
    def draw_line(self, start: Vector2, end: Vector2, 
                  color: Tuple[int, int, int], width: int = 1):
        """
        Draw a line between two points.
        
        Args:
            start: Start position
            end: End position
            color: RGB color tuple
            width: Line width in pixels
        """
        screen_start = self.world_to_screen(start)
        screen_end = self.world_to_screen(end)
        
        pygame.draw.line(self.screen, color, 
                        (screen_start.x, screen_start.y), 
                        (screen_end.x, screen_end.y), width)
    
    def draw_text(self, text: str, position: Vector2, 
                  color: Tuple[int, int, int] = Color.WHITE, 
                  font_size: int = 24, font_name: Optional[str] = None):
        """
        Draw text at the specified position.
        
        Args:
            text: Text string to draw
            position: Position to draw at
            color: Text color as RGB tuple
            font_size: Font size in pixels
            font_name: Font name (None for default)
        """
        font = pygame.font.Font(font_name, font_size)
        text_surface = font.render(text, True, color)
        
        screen_pos = self.world_to_screen(position)
        self.screen.blit(text_surface, (screen_pos.x, screen_pos.y))
    
    def get_text_size(self, text: str, font_size: int = 24, 
                     font_name: Optional[str] = None) -> Tuple[int, int]:
        """
        Get the size of rendered text.
        
        Args:
            text: Text string to measure
            font_size: Font size in pixels
            font_name: Font name (None for default)
            
        Returns:
            (width, height) tuple
        """
        font = pygame.font.Font(font_name, font_size)
        return font.size(text)
    
    def set_rendering_mode(self, mode: str):
        """
        Set rendering mode for 2D or 2.5D games.
        
        Args:
            mode: "2D" for traditional 2D, "2.5D" for pseudo-3D
        """
        self.rendering_mode = mode
    
    def set_render_distance(self, distance: float):
        """
        Set render distance for culling optimization.
        
        Args:
            distance: Maximum render distance
        """
        self.render_distance = distance
    
    def set_fog_distance(self, distance: float):
        """
        Set fog distance for atmospheric effects.
        
        Args:
            distance: Fog start distance
        """
        self.fog_distance = distance
    
    def clear_sprite_cache(self):
        """Clear sprite cache to free memory."""
        # Implementation would clear any cached sprites
        pass
