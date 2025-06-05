"""
VoidRay Renderer
Handles all rendering operations including sprites, shapes, and text with 2.5D support.
"""

import pygame
from typing import List, Optional, Dict, Tuple, Callable
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
        """Create a color from RGB values."""
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))

    @staticmethod
    def rgba(r: int, g: int, b: int, a: int) -> tuple:
        """Create a color from RGBA values."""
        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), max(0, min(255, a)))

    def to_tuple(self) -> tuple:
        """Convert color to tuple format."""
        if isinstance(self, tuple):
            return self
        return (0, 0, 0)  # Default fallback


class RenderCommand:
    """Represents a single render command with z-order and layer information."""

    def __init__(self, render_func: Callable, z_order: int = 0, layer: str = "default", depth: float = 0.0):
        self.render_func = render_func
        self.z_order = z_order
        self.layer = layer
        self.depth = depth  # For 2.5D depth sorting


class Renderer:
    """The main renderer that handles drawing operations with 2.5D support."""

    def __init__(self, screen: pygame.Surface):
        """Initialize the renderer."""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.camera = None
        self.background_color = Color.BLACK

        # Enhanced rendering system with 2.5D support
        self.render_queue: List[RenderCommand] = []
        self.layer_order: List[str] = ["background", "floor", "walls", "world", "entities", "effects", "ui"]
        self.layer_enabled: Dict[str, bool] = {}

        # Initialize all layers as enabled
        for layer in self.layer_order:
            self.layer_enabled[layer] = True

        # Advanced 2.5D rendering settings (like id Tech 1 / DOOM)
        self.enable_depth_sorting = True
        self.perspective_enabled = True
        self.depth_scale_factor = 0.8  # How much objects scale based on depth
        self.perspective_strength = 1.0  # How strong the perspective effect is
        self.horizon_line = 0.5  # Where the horizon appears (0.0 = top, 1.0 = bottom)
        self.fov = 60.0  # Field of view in degrees

        # Height mapping (for DOOM-style rendering)
        self.floor_height = 0.0
        self.ceiling_height = 100.0
        self.enable_height_mapping = True

        # Wall rendering (for GTA 1 / DOOM style buildings)
        self.wall_segments = []
        self.enable_wall_rendering = True
        self.wall_scale_factor = 1.0

        # Fog and atmospheric effects
        self.fog_color = Color.LIGHT_GRAY
        self.fog_strength = 0.0  # 0.0 = no fog, 1.0 = full fog
        self.fog_start_distance = 100.0
        self.fog_end_distance = 500.0

        # Lighting system
        self.ambient_light = 0.8
        self.light_sources = []

        # Texture caching
        self.texture_cache = {}
        self.surface_cache = {}  # Cache for transformed surfaces

        # Performance tracking
        self.stats = {
            'draw_calls': 0,
            'objects_rendered': 0,
            'sprites_batched': 0,
            'walls_rendered': 0,
            'perspective_calculations': 0
        }

    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear the screen with the specified color."""
        if color is None:
            color = self.background_color
        self.screen.fill(color)

        # Reset stats
        self.stats = {
            'draw_calls': 0,
            'objects_rendered': 0,
            'sprites_batched': 0,
            'walls_rendered': 0,
            'perspective_calculations': 0
        }

    def present(self):
        """Present the rendered frame to the screen with efficient sorting."""
        # Sort render queue by layer, then by depth (for 2.5D), then by z-order
        def sort_key(command):
            layer_index = self.layer_order.index(command.layer) if command.layer in self.layer_order else 999
            return (layer_index, -command.depth if self.enable_depth_sorting else 0, command.z_order)

        self.render_queue.sort(key=sort_key)

        # Render each command
        for command in self.render_queue:
            if self.layer_enabled.get(command.layer, True):
                command.render_func()
                self.stats['draw_calls'] += 1

                # Render walls after floor layer but before world layer
                if command.layer == "floor" and self.enable_wall_rendering:
                    self.render_walls()

        self.render_queue.clear()
        pygame.display.flip()

    def set_camera(self, camera):
        """Set the camera for the renderer."""
        self.camera = camera

    def world_to_screen(self, world_pos: Vector2, depth: float = 0.0, height: float = 0.0) -> Vector2:
        """Convert world coordinates to screen coordinates with advanced 2.5D support."""
        if self.camera:
            screen_size = Vector2(self.screen_width, self.screen_height)
            screen_pos = self.camera.world_to_screen(world_pos, screen_size, depth, height)
            return screen_pos
        else:
            # Enhanced 2.5D transformation without camera
            screen_pos = world_pos.copy()

            if self.perspective_enabled:
                # Apply perspective projection (DOOM/GTA style)
                distance_from_camera = max(1.0, abs(depth) + 1.0)
                perspective_scale = 1.0 / distance_from_camera * self.perspective_strength

                # Apply height-based vertical offset
                if self.enable_height_mapping:
                    horizon_y = self.screen_height * self.horizon_line
                    vertical_offset = (height - self.floor_height) / distance_from_camera
                    screen_pos.y = horizon_y - vertical_offset

                # Apply perspective to X coordinate
                center_x = self.screen_width / 2
                screen_pos.x = center_x + (screen_pos.x - center_x) * perspective_scale

                self.stats['perspective_calculations'] += 1

            # Apply 2.5D depth scaling
            if self.enable_depth_sorting and depth != 0.0:
                scale = max(0.1, 1.0 + (depth * self.depth_scale_factor))
                center = Vector2(self.screen_width / 2, self.screen_height / 2)
                offset = screen_pos - center
                screen_pos = center + offset * scale

            return screen_pos

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Convert screen coordinates to world coordinates."""
        if self.camera:
            return self.camera.screen_to_world(screen_pos)
        return screen_pos

    def queue_render(self, render_func: Callable, z_order: int = 0, layer: str = "world", depth: float = 0.0):
        """Add a render command to the queue."""
        command = RenderCommand(render_func, z_order, layer, depth)
        self.render_queue.append(command)

    def draw_sprite(self, surface: pygame.Surface, position: Vector2, 
                   rotation: float = 0, scale: Vector2 = None, 
                   z_order: int = 0, layer: str = "entities", depth: float = 0.0,
                   alpha: int = 255):
        """Draw a sprite surface with 2.5D support."""
        if not surface:
            return

        def render_sprite():
            actual_scale = scale if scale else Vector2(1, 1)

            # Apply 2.5D depth scaling
            if self.enable_depth_sorting and depth != 0.0:
                depth_scale = 1.0 + (depth * self.depth_scale_factor)
                actual_scale = Vector2(actual_scale.x * depth_scale, actual_scale.y * depth_scale)

            # Apply transformations
            transformed_surface = surface.copy()

            # Apply alpha
            if alpha < 255:
                transformed_surface.set_alpha(alpha)

            # Scale
            if actual_scale.x != 1 or actual_scale.y != 1:
                new_width = max(1, int(surface.get_width() * actual_scale.x))
                new_height = max(1, int(surface.get_height() * actual_scale.y))
                transformed_surface = pygame.transform.scale(transformed_surface, (new_width, new_height))

            # Rotate
            if rotation != 0:
                transformed_surface = pygame.transform.rotate(transformed_surface, rotation)

            # Convert to screen coordinates
            screen_pos = self.world_to_screen(position, depth)

            # Center the sprite on the position
            rect = transformed_surface.get_rect()
            rect.center = (int(screen_pos.x), int(screen_pos.y))

            # Apply fog effect for 2.5D
            if self.fog_strength > 0 and depth < 0:
                fog_alpha = min(255, int(abs(depth) * self.fog_strength * 255))
                fog_surface = pygame.Surface(transformed_surface.get_size())
                fog_surface.fill(self.fog_color)
                fog_surface.set_alpha(fog_alpha)
                transformed_surface.blit(fog_surface, (0, 0))

            self.screen.blit(transformed_surface, rect)
            self.stats['objects_rendered'] += 1

        self.queue_render(render_sprite, z_order, layer, depth)

    def draw_rect(self, position: Vector2, size: Vector2, 
                  color: Tuple[int, int, int], filled: bool = True, 
                  z_order: int = 0, layer: str = "world", depth: float = 0.0):
        """Draw a rectangle with 2.5D support."""
        def render_rect():
            screen_pos = self.world_to_screen(position, depth)

            # Apply 2.5D depth scaling
            actual_size = size
            if self.enable_depth_sorting and depth != 0.0:
                depth_scale = 1.0 + (depth * self.depth_scale_factor)
                actual_size = Vector2(size.x * depth_scale, size.y * depth_scale)

            rect = pygame.Rect(int(screen_pos.x), int(screen_pos.y), 
                              int(actual_size.x), int(actual_size.y))

            if filled:
                pygame.draw.rect(self.screen, color, rect)
            else:
                pygame.draw.rect(self.screen, color, rect, 1)

        self.queue_render(render_rect, z_order, layer, depth)

    def draw_circle(self, center: Vector2, radius: float, 
                   color: Tuple[int, int, int], filled: bool = True, 
                   z_order: int = 0, layer: str = "world", depth: float = 0.0):
        """Draw a circle with 2.5D support."""
        def render_circle():
            screen_pos = self.world_to_screen(center, depth)

            # Apply 2.5D depth scaling
            actual_radius = radius
            if self.enable_depth_sorting and depth != 0.0:
                depth_scale = 1.0 + (depth * self.depth_scale_factor)
                actual_radius = radius * depth_scale

            if filled:
                pygame.draw.circle(self.screen, color, 
                                 (int(screen_pos.x), int(screen_pos.y)), 
                                 int(actual_radius))
            else:
                pygame.draw.circle(self.screen, color, 
                                 (int(screen_pos.x), int(screen_pos.y)), 
                                 int(actual_radius), 1)

        self.queue_render(render_circle, z_order, layer, depth)

    def draw_line(self, start: Vector2, end: Vector2, 
                  color: Tuple[int, int, int], width: int = 1, 
                  z_order: int = 0, layer: str = "world"):
        """Draw a line between two points."""
        def render_line():
            screen_start = self.world_to_screen(start)
            screen_end = self.world_to_screen(end)

            pygame.draw.line(self.screen, color, 
                            (int(screen_start.x), int(screen_start.y)), 
                            (int(screen_end.x), int(screen_end.y)), width)

        self.queue_render(render_line, z_order, layer)

    def draw_text(self, text: str, position: Vector2, 
                  color: Tuple[int, int, int] = Color.WHITE, 
                  font_size: int = 24, font_name: Optional[str] = None, 
                  z_order: int = 0, layer: str = "ui"):
        """Draw text at the specified position."""
        def render_text():
            font = pygame.font.Font(font_name, font_size)
            text_surface = font.render(text, True, color)
            screen_pos = self.world_to_screen(position)
            self.screen.blit(text_surface, (int(screen_pos.x), int(screen_pos.y)))

        self.queue_render(render_text, z_order, layer)

    def get_text_size(self, text: str, font_size: int = 24, 
                     font_name: Optional[str] = None) -> Tuple[int, int]:
        """Get the size of rendered text."""
        font = pygame.font.Font(font_name, font_size)
        return font.size(text)

    def get_screen_size(self) -> Vector2:
        """Get the screen dimensions."""
        return Vector2(self.screen_width, self.screen_height)

    def set_fog(self, color: Tuple[int, int, int], strength: float):
        """Set fog parameters for 2.5D depth effects."""
        self.fog_color = color
        self.fog_strength = max(0.0, min(1.0, strength))

    def enable_layer(self, layer: str, enabled: bool = True):
        """Enable or disable a rendering layer."""
        self.layer_enabled[layer] = enabled

    def add_wall_segment(self, start: Vector2, end: Vector2, height: float, 
                        color: Tuple[int, int, int], texture: Optional[pygame.Surface] = None):
        """Add a wall segment for 2.5D rendering (DOOM/GTA style)."""
        wall = {
            'start': start,
            'end': end,
            'height': height,
            'color': color,
            'texture': texture,
            'depth': min(start.distance_to(Vector2(self.screen_width/2, self.screen_height/2)),
                        end.distance_to(Vector2(self.screen_width/2, self.screen_height/2)))
        }
        self.wall_segments.append(wall)

    def clear_walls(self):
        """Clear all wall segments."""
        self.wall_segments.clear()

    def render_walls(self):
        """Render all wall segments with proper depth sorting."""
        if not self.enable_wall_rendering:
            return

        # Sort walls by depth (back to front)
        sorted_walls = sorted(self.wall_segments, key=lambda w: w['depth'], reverse=True)

        for wall in sorted_walls:
            self._render_wall_segment(wall)
            self.stats['walls_rendered'] += 1

    def _render_wall_segment(self, wall: dict):
        """Render a single wall segment with perspective."""
        start_screen = self.world_to_screen(wall['start'], wall['depth'], self.floor_height)
        end_screen = self.world_to_screen(wall['end'], wall['depth'], self.floor_height)

        # Calculate wall top positions
        start_top = self.world_to_screen(wall['start'], wall['depth'], wall['height'])
        end_top = self.world_to_screen(wall['end'], wall['depth'], wall['height'])

        # Create wall polygon
        wall_points = [
            (int(start_screen.x), int(start_screen.y)),  # Bottom left
            (int(end_screen.x), int(end_screen.y)),      # Bottom right
            (int(end_top.x), int(end_top.y)),            # Top right
            (int(start_top.x), int(start_top.y))         # Top left
        ]

        # Apply fog based on depth
        color = wall['color']
        if self.fog_strength > 0 and wall['depth'] > self.fog_start_distance:
            fog_factor = min(1.0, (wall['depth'] - self.fog_start_distance) / 
                           (self.fog_end_distance - self.fog_start_distance))
            fog_factor *= self.fog_strength

            # Blend wall color with fog color
            color = (
                int(color[0] * (1 - fog_factor) + self.fog_color[0] * fog_factor),
                int(color[1] * (1 - fog_factor) + self.fog_color[1] * fog_factor),
                int(color[2] * (1 - fog_factor) + self.fog_color[2] * fog_factor)
            )

        # Draw the wall
        if len(wall_points) >= 3:
            pygame.draw.polygon(self.screen, color, wall_points)

            # Optional: draw wall outline
            pygame.draw.polygon(self.screen, (max(0, color[0]-20), max(0, color[1]-20), max(0, color[2]-20)), 
                              wall_points, 1)

    def draw_floor_tile(self, position: Vector2, size: Vector2, 
                       color: Tuple[int, int, int], height: float = 0.0,
                       z_order: int = 0, layer: str = "floor"):
        """Draw a floor tile with perspective and height."""
        def render_floor():
            # Calculate the four corners of the floor tile
            corners = [
                Vector2(position.x - size.x/2, position.y - size.y/2),  # Top-left
                Vector2(position.x + size.x/2, position.y - size.y/2),  # Top-right
                Vector2(position.x + size.x/2, position.y + size.y/2),  # Bottom-right
                Vector2(position.x - size.x/2, position.y + size.y/2)   # Bottom-left
            ]

            # Convert to screen coordinates with height
            screen_corners = []
            for corner in corners:
                depth = corner.distance_to(Vector2(self.screen_width/2, self.screen_height/2))
                screen_corner = self.world_to_screen(corner, depth, height)
                screen_corners.append((int(screen_corner.x), int(screen_corner.y)))

            # Draw the floor tile
            if len(screen_corners) >= 3:
                pygame.draw.polygon(self.screen, color, screen_corners)

        self.queue_render(render_floor, z_order, layer)

    def set_perspective_settings(self, fov: float = 60.0, horizon: float = 0.5, 
                               strength: float = 1.0):
        """Configure perspective rendering settings."""
        self.fov = max(30.0, min(120.0, fov))
        self.horizon_line = max(0.0, min(1.0, horizon))
        self.perspective_strength = max(0.1, min(3.0, strength))

    def set_height_bounds(self, floor: float = 0.0, ceiling: float = 100.0):
        """Set the floor and ceiling heights for the world."""
        self.floor_height = floor
        self.ceiling_height = max(floor + 1.0, ceiling)

    def enable_perspective(self, enabled: bool = True):
        """Enable or disable perspective projection."""
        self.perspective_enabled = enabled

    def enable_walls(self, enabled: bool = True):
        """Enable or disable wall rendering."""
        self.enable_wall_rendering = enabled

    def get_stats(self) -> Dict[str, int]:
        """Get rendering performance statistics."""
        return self.stats.copy()

    def clear_caches(self):
        """Clear all caches to free memory."""
        self.surface_cache.clear()
        print(f"Cleared surface cache")

    def get_cache_info(self):
        """Get information about cache usage."""
        return {
            'texture_cache_size': len(self.texture_cache),
            'surface_cache_size': len(self.surface_cache)
        }
`