"""
VoidRay Renderer
Handles all rendering operations including sprites, shapes, and text.
"""

import pygame
from typing import List, Optional, Dict, Tuple
from ..math.vector2 import Vector2


class Color:
    """
    Color constants and utilities.
    """
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    BROWN = (139, 69, 19)

    @staticmethod
    def rgb(r: int, g: int, b: int) -> tuple:
        """
        Create a color from RGB values.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)

        Returns:
            Color tuple
        """
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    @staticmethod
    def rgba(r: int, g: int, b: int, a: int) -> tuple:
        """
        Create a color from RGBA values.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            a: Alpha component (0-255)

        Returns:
            Color tuple with alpha
        """
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), max(0, min(255, a)))


class RenderCommand:
    """
    Represents a single render command with z-order and layer information.
    """
    def __init__(self, render_func, z_order: int = 0, layer: str = "default"):
        self.render_func = render_func
        self.z_order = z_order
        self.layer = layer


class Renderer:
    """
    The main renderer that handles drawing operations.
    """

    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.

        Args:
            screen: Pygame surface to render to
        """
        self.screen = screen
        self.camera = None
        self.background_color = Color.BLACK

        # Enhanced rendering system
        self.render_queue: List[RenderCommand] = []
        self.layer_order: List[str] = ["background", "default", "ui"]  # Layers in render order
        self.layer_enabled: Dict[str, bool] = {}

        # Initialize all layers as enabled
        for layer in self.layer_order:
            self.layer_enabled[layer] = True

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
        # Sort render queue by z-order within each layer
        self.render_queue.sort(key=lambda x: x.z_order)

        # Render each layer in order
        for layer in self.layer_order:
            if self.layer_enabled[layer]:
                for command in self.render_queue:
                    if command.layer == layer:
                        command.render_func(self.screen, self.camera)

        self.render_queue.clear()  # Clear queue after rendering

        pygame.display.flip()

    def set_camera(self, camera):
        """
        Set the camera for the renderer.

        Args:
            camera: Camera object
        """
        self.camera = camera

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
        return world_pos  # If no camera, return world position

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

    def queue_render(self, render_func, z_order: int = 0, layer: str = "default"):
        """
        Add a render command to the queue.

        Args:
            render_func: Function that takes screen and camera as arguments and performs rendering.
            z_order: Z-order for depth sorting (lower values are drawn first).
            layer: Layer to draw on.
        """
        command = RenderCommand(render_func, z_order, layer)
        self.render_queue.append(command)

    def draw_sprite(self, surface: pygame.Surface, position: Vector2, 
                   rotation: float = 0, scale: Vector2 = None, 
                   z_order: int = 0, layer: str = "default"):
        """
        Draw a sprite surface at the specified position.

        Args:
            surface: The pygame surface to draw
            position: World position to draw at
            rotation: Rotation in degrees
            scale: Scale factor as Vector2
            z_order: Z-order for depth sorting.
            layer: Layer to draw on.
        """
        def render_sprite(screen, camera):
            actual_scale = scale
            if actual_scale is None:
                actual_scale = Vector2(1, 1)

            # Apply transformations
            transformed_surface = surface

            # Scale
            if actual_scale.x != 1 or actual_scale.y != 1:
                new_width = int(surface.get_width() * actual_scale.x)
                new_height = int(surface.get_height() * actual_scale.y)
                transformed_surface = pygame.transform.scale(transformed_surface, (new_width, new_height))

            # Rotate
            if rotation != 0:
                transformed_surface = pygame.transform.rotate(transformed_surface, rotation)

            # Convert to screen coordinates
            if camera:
                screen_pos = camera.world_to_screen(position)
            else:
                screen_pos = position

            # Center the sprite on the position
            rect = transformed_surface.get_rect()
            rect.center = (screen_pos.x, screen_pos.y)

            screen.blit(transformed_surface, rect)

        self.queue_render(render_sprite, z_order, layer)

    def draw_rect(self, position: Vector2, size: Vector2, 
                  color: Tuple[int, int, int], filled: bool = True, 
                  z_order: int = 0, layer: str = "default"):
        """
        Draw a rectangle.

        Args:
            position: Top-left corner position
            size: Width and height as Vector2
            color: RGB color tuple
            filled: Whether to fill the rectangle or just draw outline
            z_order: Z-order for depth sorting.
            layer: Layer to draw on.
        """
        def render_rect(screen, camera):
            # Convert to screen coordinates
            if camera:
                screen_pos = camera.world_to_screen(position)
            else:
                screen_pos = position

            rect = pygame.Rect(screen_pos.x, screen_pos.y, size.x, size.y)

            if filled:
                pygame.draw.rect(screen, color, rect)
            else:
                pygame.draw.rect(screen, color, rect, 1)
        
        self.queue_render(render_rect, z_order, layer)

    def draw_circle(self, center: Vector2, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True, 
                   z_order: int = 0, layer: str = "default"):
        """
        Draw a circle.

        Args:
            center: Center position
            radius: Circle radius
            color: RGB color tuple
            filled: Whether to fill the circle or just draw outline
            z_order: Z-order for depth sorting.
            layer: Layer to draw on.
        """
        def render_circle(screen, camera):
            # Convert to screen coordinates
            if camera:
                screen_pos = camera.world_to_screen(center)
            else:
                screen_pos = center

            if filled:
                pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius))
            else:
                pygame.draw.circle(screen, color, (int(screen_pos.x), int(screen_pos.y)), int(radius), 1)

        self.queue_render(render_circle, z_order, layer)

    def draw_line(self, start: Vector2, end: Vector2, 
                  color: Tuple[int, int, int], width: int = 1, 
                  z_order: int = 0, layer: str = "default"):
        """
        Draw a line between two points.

        Args:
            start: Start position
            end: End position
            color: RGB color tuple
            width: Line width in pixels
            z_order: Z-order for depth sorting.
            layer: Layer to draw on.
        """
        def render_line(screen, camera):
            if camera:
                screen_start = camera.world_to_screen(start)
                screen_end = camera.world_to_screen(end)
            else:
                screen_start = start
                screen_end = end

            pygame.draw.line(screen, color, 
                            (screen_start.x, screen_start.y), 
                            (screen_end.x, screen_end.y), width)

        self.queue_render(render_line, z_order, layer)

    def draw_text(self, text: str, position: Vector2, 
                  color: Tuple[int, int, int] = Color.WHITE, 
                  font_size: int = 24, font_name: Optional[str] = None, 
                  z_order: int = 0, layer: str = "default"):
        """
        Draw text at the specified position.

        Args:
            text: Text string to draw
            position: Position to draw at
            color: Text color as RGB tuple
            font_size: Font size in pixels
            font_name: Font name (None for default)
            z_order: Z-order for depth sorting.
            layer: Layer to draw on.
        """
        def render_text(screen, camera):
            font = pygame.font.Font(font_name, font_size)
            text_surface = font.render(text, True, color)

            if camera:
                screen_pos = camera.world_to_screen(position)
            else:
                screen_pos = position
            screen.blit(text_surface, (screen_pos.x, screen_pos.y))

        self.queue_render(render_text, z_order, layer)

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