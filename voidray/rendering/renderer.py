
"""
VoidRay Renderer

The main rendering system that handles drawing sprites, shapes, and other
visual elements to the screen with 2.5D support for DOOM-style games.
"""

import pygame
import math
from typing import Optional, Tuple, List, Dict
from ..math.vector2 import Vector2
from ..utils.color import Color
from .camera import Camera


class Renderer:
    """
    The main renderer responsible for drawing all visual elements to the screen
    with support for both 2D and 2.5D rendering modes.
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
        
        # 2.5D rendering support
        self.rendering_mode = "2D"  # "2D" or "2.5D"
        self.zbuffer = [float('inf')] * (self.screen_width * self.screen_height)
        self.wall_height = 64
        self.player_height = 32
        self.fog_distance = 800
        
        # Performance optimizations
        self.render_distance = 1000
        self.cull_frustum = True
        self.dirty_rects = []
        self.sprite_cache = {}
        self.last_frame_objects = set()
        
        # Render layers for depth sorting
        self.render_layers = {
            'background': [],
            'world': [],
            'entities': [],
            'effects': [],
            'ui': []
        }
    
    def set_rendering_mode(self, mode: str) -> None:
        """
        Set the rendering mode.
        
        Args:
            mode: "2D" for traditional 2D, "2.5D" for raycasting/pseudo-3D
        """
        if mode in ["2D", "2.5D"]:
            self.rendering_mode = mode
            if mode == "2.5D":
                self._init_2_5d_rendering()
    
    def _init_2_5d_rendering(self) -> None:
        """Initialize 2.5D rendering systems."""
        # Reset z-buffer
        self.zbuffer = [float('inf')] * (self.screen_width * self.screen_height)
        
        # Pre-calculate trigonometric values for performance
        self.sin_table = [math.sin(math.radians(i)) for i in range(360)]
        self.cos_table = [math.cos(math.radians(i)) for i in range(360)]
    
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
        if self.rendering_mode == "2.5D":
            # Clear with gradient for sky effect
            self._draw_sky_gradient()
            # Reset z-buffer
            self.zbuffer = [float('inf')] * (self.screen_width * self.screen_height)
        else:
            self.screen.fill(self.clear_color.to_tuple())
        
        # Clear render layers
        for layer in self.render_layers.values():
            layer.clear()
    
    def _draw_sky_gradient(self) -> None:
        """Draw a gradient sky for 2.5D mode."""
        for y in range(self.screen_height // 2):
            intensity = int(255 * (1.0 - y / (self.screen_height // 2)))
            color = (intensity // 4, intensity // 3, intensity)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))
        
        # Draw floor
        floor_color = (64, 64, 64)
        pygame.draw.rect(self.screen, floor_color, 
                        (0, self.screen_height // 2, self.screen_width, self.screen_height // 2))
    
    def present(self) -> None:
        """Present the rendered frame to the screen."""
        if self.rendering_mode == "2.5D":
            self._render_2_5d_layers()
        else:
            self._render_2d_layers()
        
        pygame.display.flip()
        self.dirty_rects.clear()
    
    def _render_2d_layers(self) -> None:
        """Render all 2D layers in order."""
        for layer_name in ['background', 'world', 'entities', 'effects', 'ui']:
            for render_item in self.render_layers[layer_name]:
                render_item()
    
    def _render_2_5d_layers(self) -> None:
        """Render all 2.5D layers with depth sorting."""
        # Sort entities by distance for proper depth rendering
        if self.camera:
            camera_pos = self.camera.transform.position if self.camera.transform else Vector2.zero()
            
            # Sort world and entity layers by distance
            combined_items = []
            for item in self.render_layers['world'] + self.render_layers['entities']:
                if hasattr(item, 'position'):
                    distance = (item.position - camera_pos).magnitude()
                    combined_items.append((distance, item))
                else:
                    combined_items.append((0, item))
            
            # Sort by distance (far to near)
            combined_items.sort(key=lambda x: x[0], reverse=True)
            
            # Render background
            for render_item in self.render_layers['background']:
                render_item()
            
            # Render sorted world/entities
            for _, render_item in combined_items:
                if callable(render_item):
                    render_item()
            
            # Render effects and UI
            for render_item in self.render_layers['effects']:
                render_item()
            for render_item in self.render_layers['ui']:
                render_item()
    
    def add_to_render_layer(self, layer: str, render_func) -> None:
        """
        Add a render function to a specific layer.
        
        Args:
            layer: Layer name ('background', 'world', 'entities', 'effects', 'ui')
            render_func: Function to call for rendering
        """
        if layer in self.render_layers:
            self.render_layers[layer].append(render_func)
    
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
                   rotation: float = 0, scale: Vector2 = Vector2(1, 1),
                   layer: str = 'entities', height: float = 0) -> None:
        """
        Draw a sprite to the screen with 2.5D support.
        
        Args:
            surface: The pygame surface to draw
            position: World position to draw at
            rotation: Rotation in degrees
            scale: Scale factor
            layer: Render layer
            height: Height above ground for 2.5D rendering
        """
        if not surface:
            return
        
        if self.rendering_mode == "2.5D":
            self._draw_sprite_2_5d(surface, position, rotation, scale, layer, height)
        else:
            self._draw_sprite_2d(surface, position, rotation, scale, layer)
    
    def _draw_sprite_2d(self, surface: pygame.Surface, position: Vector2, 
                       rotation: float, scale: Vector2, layer: str) -> None:
        """Draw sprite in 2D mode."""
        def render():
            # Transform position to screen space
            screen_pos = self.world_to_screen(position)
            
            # Check if sprite is visible
            if not self._is_sprite_visible(screen_pos, surface):
                return
            
            # Use cached transformed surface if available
            cache_key = (id(surface), rotation, scale.x, scale.y)
            if cache_key in self.sprite_cache:
                transformed_surface = self.sprite_cache[cache_key]
            else:
                transformed_surface = self._transform_surface(surface, rotation, scale)
                self.sprite_cache[cache_key] = transformed_surface
            
            # Calculate position to center the sprite
            rect = transformed_surface.get_rect()
            rect.center = (int(screen_pos.x), int(screen_pos.y))
            
            self.screen.blit(transformed_surface, rect)
            self.dirty_rects.append(rect)
        
        self.add_to_render_layer(layer, render)
    
    def _draw_sprite_2_5d(self, surface: pygame.Surface, position: Vector2, 
                         rotation: float, scale: Vector2, layer: str, height: float) -> None:
        """Draw sprite in 2.5D mode with depth and perspective."""
        if not self.camera or not self.camera.transform:
            return
        
        def render():
            camera_pos = self.camera.transform.position
            camera_angle = self.camera.transform.rotation
            
            # Calculate relative position and distance
            rel_pos = position - camera_pos
            distance = rel_pos.magnitude()
            
            # Skip if too far
            if distance > self.render_distance:
                return
            
            # Calculate angle to sprite
            angle_to_sprite = math.degrees(math.atan2(rel_pos.y, rel_pos.x))
            relative_angle = angle_to_sprite - camera_angle
            
            # Normalize angle
            while relative_angle > 180:
                relative_angle -= 360
            while relative_angle < -180:
                relative_angle += 360
            
            # Check if sprite is in view frustum
            if abs(relative_angle) > 60:  # 120-degree FOV
                return
            
            # Calculate screen x position
            screen_x = int(self.screen_width / 2 + (relative_angle / 60) * (self.screen_width / 2))
            
            if screen_x < 0 or screen_x >= self.screen_width:
                return
            
            # Calculate perspective scaling
            perspective_scale = 1.0 / max(distance / 100, 0.1)
            sprite_scale = perspective_scale * scale.x
            
            # Calculate screen y position with height
            screen_y = int(self.screen_height / 2 - height * perspective_scale)
            
            # Scale sprite based on distance
            scaled_width = max(1, int(surface.get_width() * sprite_scale))
            scaled_height = max(1, int(surface.get_height() * sprite_scale))
            
            if scaled_width < 1 or scaled_height < 1:
                return
            
            # Transform surface
            scaled_surface = pygame.transform.scale(surface, (scaled_width, scaled_height))
            if rotation != 0:
                scaled_surface = pygame.transform.rotate(scaled_surface, -rotation)
            
            # Apply fog/distance fading
            if distance > self.fog_distance / 2:
                fog_factor = min(1.0, (distance - self.fog_distance / 2) / (self.fog_distance / 2))
                fog_surface = scaled_surface.copy()
                fog_surface.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
                fog_surface.set_alpha(int(255 * (1 - fog_factor)))
                scaled_surface = fog_surface
            
            # Draw sprite
            rect = scaled_surface.get_rect()
            rect.center = (screen_x, screen_y)
            
            # Z-buffer check (simple implementation)
            if self._depth_test(rect, distance):
                self.screen.blit(scaled_surface, rect)
        
        self.add_to_render_layer(layer, render)
    
    def _transform_surface(self, surface: pygame.Surface, rotation: float, scale: Vector2) -> pygame.Surface:
        """Transform surface with rotation and scaling."""
        transformed = surface
        
        # Apply scale
        if scale != Vector2(1, 1):
            new_width = max(1, int(surface.get_width() * scale.x))
            new_height = max(1, int(surface.get_height() * scale.y))
            transformed = pygame.transform.scale(transformed, (new_width, new_height))
        
        # Apply rotation
        if rotation != 0:
            transformed = pygame.transform.rotate(transformed, -rotation)
        
        return transformed
    
    def _is_sprite_visible(self, screen_pos: Vector2, surface: pygame.Surface) -> bool:
        """Check if sprite is visible on screen."""
        half_width = surface.get_width() // 2
        half_height = surface.get_height() // 2
        
        return (screen_pos.x + half_width >= 0 and
                screen_pos.x - half_width < self.screen_width and
                screen_pos.y + half_height >= 0 and
                screen_pos.y - half_height < self.screen_height)
    
    def _depth_test(self, rect: pygame.Rect, distance: float) -> bool:
        """Simple depth test for 2.5D rendering."""
        # Simplified depth test - in a full implementation you'd check per-pixel
        center_x = rect.centerx
        center_y = rect.centery
        
        if 0 <= center_x < self.screen_width and 0 <= center_y < self.screen_height:
            buffer_index = center_y * self.screen_width + center_x
            if distance < self.zbuffer[buffer_index]:
                self.zbuffer[buffer_index] = distance
                return True
        
        return False
    
    def draw_wall_segment(self, start_pos: Vector2, end_pos: Vector2, height: float,
                         color, texture: pygame.Surface = None) -> None:
        """
        Draw a wall segment in 2.5D mode (for DOOM-style games).
        
        Args:
            start_pos: Wall start position
            end_pos: Wall end position
            height: Wall height
            color: Wall color (Color object or RGB tuple)
            texture: Optional wall texture
        """
        if self.rendering_mode != "2.5D" or not self.camera or not self.camera.transform:
            return
        
        def render():
            self._render_wall_segment(start_pos, end_pos, height, color, texture)
        
        self.add_to_render_layer('world', render)
    
    def _render_wall_segment(self, start_pos: Vector2, end_pos: Vector2, height: float,
                           color, texture: pygame.Surface = None) -> None:
        """Render a wall segment using raycasting principles."""
        camera_pos = self.camera.transform.position
        camera_angle = self.camera.transform.rotation
        
        # Handle both Color objects and tuples
        if hasattr(color, 'to_tuple'):
            base_color = color
        else:
            # Convert tuple to Color-like object for shading calculations
            from ..utils.color import Color
            base_color = Color(color[0], color[1], color[2])
        
        # Cast rays from camera through each screen column
        for x in range(self.screen_width):
            # Calculate ray angle
            ray_angle = camera_angle + (x - self.screen_width / 2) * (60 / self.screen_width)
            
            # Cast ray and find intersection with wall
            hit_distance = self._cast_ray_to_wall(camera_pos, ray_angle, start_pos, end_pos)
            
            if hit_distance is not None and hit_distance > 0:
                # Calculate wall height on screen
                wall_screen_height = int((height / hit_distance) * 200)
                
                # Calculate wall top and bottom
                wall_top = max(0, self.screen_height // 2 - wall_screen_height // 2)
                wall_bottom = min(self.screen_height, self.screen_height // 2 + wall_screen_height // 2)
                
                # Apply distance-based shading
                shade_factor = max(0.1, 1.0 - hit_distance / self.fog_distance)
                shaded_color = (
                    int(base_color.r * shade_factor),
                    int(base_color.g * shade_factor),
                    int(base_color.b * shade_factor)
                )
                
                # Draw wall column
                if wall_bottom > wall_top:
                    pygame.draw.line(self.screen, shaded_color, (x, wall_top), (x, wall_bottom))
    
    def _cast_ray_to_wall(self, start: Vector2, angle: float, wall_start: Vector2, wall_end: Vector2) -> Optional[float]:
        """Cast a ray and find intersection with wall segment."""
        # Ray direction
        angle_rad = math.radians(angle)
        ray_dir = Vector2(math.cos(angle_rad), math.sin(angle_rad))
        
        # Wall direction
        wall_dir = wall_end - wall_start
        wall_length = wall_dir.magnitude()
        
        if wall_length == 0:
            return None
        
        wall_dir = wall_dir.normalized()
        
        # Line-line intersection
        denominator = ray_dir.x * wall_dir.y - ray_dir.y * wall_dir.x
        
        if abs(denominator) < 1e-6:  # Parallel lines
            return None
        
        t1 = ((wall_start.x - start.x) * wall_dir.y - (wall_start.y - start.y) * wall_dir.x) / denominator
        t2 = ((wall_start.x - start.x) * ray_dir.y - (wall_start.y - start.y) * ray_dir.x) / denominator
        
        if t1 > 0 and 0 <= t2 <= wall_length:
            return t1
        
        return None
    
    def draw_rect(self, position: Vector2, size: Vector2, color, 
                  filled: bool = True, width: int = 1, layer: str = 'world') -> None:
        """
        Draw a rectangle.
        
        Args:
            position: Top-left corner position in world space
            size: Width and height of the rectangle
            color: Color to draw with (Color object or RGB tuple)
            filled: Whether to fill the rectangle
            width: Line width for unfilled rectangles
            layer: Render layer
        """
        def render():
            screen_pos = self.world_to_screen(position)
            rect = pygame.Rect(int(screen_pos.x), int(screen_pos.y), 
                              int(size.x), int(size.y))
            
            # Handle both Color objects and tuples
            if hasattr(color, 'to_tuple'):
                draw_color = color.to_tuple()
            else:
                draw_color = color
            
            if filled:
                pygame.draw.rect(self.screen, draw_color, rect)
            else:
                pygame.draw.rect(self.screen, draw_color, rect, width)
        
        self.add_to_render_layer(layer, render)
    
    def draw_circle(self, center: Vector2, radius: float, color, 
                   filled: bool = True, width: int = 1, layer: str = 'world') -> None:
        """
        Draw a circle.
        
        Args:
            center: Center position in world space
            radius: Radius of the circle
            color: Color to draw with (Color object or RGB tuple)
            filled: Whether to fill the circle
            width: Line width for unfilled circles
            layer: Render layer
        """
        def render():
            screen_pos = self.world_to_screen(center)
            
            # Handle both Color objects and tuples
            if hasattr(color, 'to_tuple'):
                draw_color = color.to_tuple()
            else:
                draw_color = color
            
            if filled:
                pygame.draw.circle(self.screen, draw_color, 
                                 (int(screen_pos.x), int(screen_pos.y)), int(radius))
            else:
                pygame.draw.circle(self.screen, draw_color, 
                                 (int(screen_pos.x), int(screen_pos.y)), int(radius), width)
        
        self.add_to_render_layer(layer, render)
    
    def draw_line(self, start: Vector2, end: Vector2, color, width: int = 1,
                  layer: str = 'world') -> None:
        """
        Draw a line.
        
        Args:
            start: Start position in world space
            end: End position in world space
            color: Color to draw with (Color object or RGB tuple)
            width: Line width
            layer: Render layer
        """
        def render():
            screen_start = self.world_to_screen(start)
            screen_end = self.world_to_screen(end)
            
            # Handle both Color objects and tuples
            if hasattr(color, 'to_tuple'):
                draw_color = color.to_tuple()
            else:
                draw_color = color
            
            pygame.draw.line(self.screen, draw_color,
                            (int(screen_start.x), int(screen_start.y)),
                            (int(screen_end.x), int(screen_end.y)), width)
        
        self.add_to_render_layer(layer, render)
    
    def draw_text(self, text: str, position: Vector2, color, 
                  font_size: int = 24, font_name: str = None, layer: str = 'ui') -> None:
        """
        Draw text to the screen.
        
        Args:
            text: The text to draw
            position: Position in world space
            color: Text color (Color object or RGB tuple)
            font_size: Font size
            font_name: Font name (None for default)
            layer: Render layer
        """
        def render():
            screen_pos = self.world_to_screen(position)
            font = pygame.font.Font(font_name, font_size)
            
            # Handle both Color objects and tuples
            if hasattr(color, 'to_tuple'):
                draw_color = color.to_tuple()
            else:
                draw_color = color
            
            text_surface = font.render(text, True, draw_color)
            self.screen.blit(text_surface, (int(screen_pos.x), int(screen_pos.y)))
        
        self.add_to_render_layer(layer, render)
    
    def get_screen_size(self) -> Vector2:
        """Get the screen dimensions."""
        return Vector2(self.screen_width, self.screen_height)
    
    def clear_sprite_cache(self) -> None:
        """Clear the sprite transformation cache."""
        self.sprite_cache.clear()
    
    def set_render_distance(self, distance: float) -> None:
        """Set the maximum render distance for optimization."""
        self.render_distance = distance
    
    def set_fog_distance(self, distance: float) -> None:
        """Set the fog distance for 2.5D rendering."""
        self.fog_distance = distance
