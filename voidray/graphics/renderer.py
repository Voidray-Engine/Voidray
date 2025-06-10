
"""
VoidRay Advanced Renderer
Enhanced 2D/2.5D rendering system with advanced features, optimizations, and visual effects.
"""

import pygame
import math
import numpy as np
from typing import Optional, Tuple, List, Dict, Union
from ..math.vector2 import Vector2


class Color:
    """Enhanced color utility class with advanced color operations."""
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
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    BROWN = (165, 42, 42)
    PINK = (255, 192, 203)
    
    @staticmethod
    def lerp(color1: Tuple[int, int, int], color2: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
        """Linear interpolation between two colors."""
        t = max(0, min(1, t))
        return (
            int(color1[0] + (color2[0] - color1[0]) * t),
            int(color1[1] + (color2[1] - color1[1]) * t),
            int(color1[2] + (color2[2] - color1[2]) * t)
        )
    
    @staticmethod
    def darken(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Darken a color by a factor."""
        factor = max(0, min(1, factor))
        return (
            int(color[0] * (1 - factor)),
            int(color[1] * (1 - factor)),
            int(color[2] * (1 - factor))
        )
    
    @staticmethod
    def brighten(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Brighten a color by a factor."""
        factor = max(0, factor)
        return (
            min(255, int(color[0] * (1 + factor))),
            min(255, int(color[1] * (1 + factor))),
            min(255, int(color[2] * (1 + factor)))
        )


class RenderLayer:
    """Represents a rendering layer for depth sorting."""
    
    def __init__(self, name: str, depth: int = 0):
        self.name = name
        self.depth = depth
        self.objects = []
        self.visible = True
        self.alpha = 255
    
    def add_object(self, obj):
        """Add an object to this layer."""
        if obj not in self.objects:
            self.objects.append(obj)
    
    def remove_object(self, obj):
        """Remove an object from this layer."""
        if obj in self.objects:
            self.objects.remove(obj)
    
    def clear(self):
        """Clear all objects from this layer."""
        self.objects.clear()


class PostProcessEffect:
    """Base class for post-processing effects."""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.intensity = 1.0
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply the effect to a surface."""
        return surface


class BloomEffect(PostProcessEffect):
    """Bloom post-processing effect."""
    
    def __init__(self, threshold: float = 0.8, intensity: float = 0.5):
        super().__init__("Bloom")
        self.threshold = threshold
        self.intensity = intensity
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply bloom effect."""
        if not self.enabled:
            return surface
        
        # Simple bloom approximation
        bloom_surface = surface.copy()
        bloom_surface = pygame.transform.smoothscale(bloom_surface, 
                                                   (surface.get_width() // 4, surface.get_height() // 4))
        bloom_surface = pygame.transform.smoothscale(bloom_surface, 
                                                   (surface.get_width(), surface.get_height()))
        
        # Blend with original
        bloom_surface.set_alpha(int(self.intensity * 255))
        result = surface.copy()
        result.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_ADD)
        
        return result


class AdvancedRenderer:
    """
    Advanced 2D/2.5D renderer with enhanced features and optimizations.
    """

    def __init__(self, screen: pygame.Surface):
        """Initialize the advanced renderer."""
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Camera system
        self.camera_offset = Vector2(0, 0)
        self.camera_zoom = 1.0
        self.camera_rotation = 0.0
        self.camera_shake_offset = Vector2(0, 0)
        
        # Rendering settings
        self.background_color = Color.BLACK
        self.rendering_mode = "2D"  # "2D" or "2.5D"
        
        # Layer system
        self.layers: Dict[str, RenderLayer] = {}
        self.default_layer = RenderLayer("default", 0)
        self.layers["default"] = self.default_layer
        
        # 2.5D rendering properties
        self.camera_height = 32.0
        self.camera_pitch = 0.0
        self.field_of_view = 60.0
        self.render_distance = 1000.0
        self.fog_distance = 500.0
        self.fog_color = Color.GRAY
        
        # Lighting system
        self.ambient_light = 0.3
        self.light_sources: List[Dict] = []
        self.enable_lighting = True
        self.enable_shadows = False
        
        # Post-processing
        self.post_effects: List[PostProcessEffect] = []
        self.enable_post_processing = False
        
        # Performance optimizations
        self.enable_frustum_culling = True
        self.enable_occlusion_culling = False
        self.render_stats = {
            'objects_rendered': 0,
            'objects_culled': 0,
            'draw_calls': 0,
            'triangles': 0
        }
        
        # Texture management
        self.texture_cache: Dict[str, pygame.Surface] = {}
        self.max_texture_cache_size = 100
        
        # Render targets
        self.render_targets: Dict[str, pygame.Surface] = {}
        self.active_render_target = None
        
        # Debug features
        self.debug_mode = False
        self.show_wireframe = False
        self.show_bounds = False
        self.show_lights = False
        
        print("Advanced Renderer initialized")

    def set_rendering_mode(self, mode: str):
        """Set rendering mode."""
        if mode in ["2D", "2.5D"]:
            self.rendering_mode = mode
            print(f"Rendering mode set to {mode}")

    def add_layer(self, name: str, depth: int = 0) -> RenderLayer:
        """Add a new rendering layer."""
        layer = RenderLayer(name, depth)
        self.layers[name] = layer
        return layer

    def get_layer(self, name: str) -> Optional[RenderLayer]:
        """Get a rendering layer by name."""
        return self.layers.get(name)

    def set_camera_properties(self, **kwargs):
        """Set camera properties."""
        if 'position' in kwargs:
            self.camera_offset = kwargs['position']
        if 'zoom' in kwargs:
            self.camera_zoom = max(0.1, kwargs['zoom'])
        if 'rotation' in kwargs:
            self.camera_rotation = kwargs['rotation']
        if 'height' in kwargs:
            self.camera_height = kwargs['height']
        if 'pitch' in kwargs:
            self.camera_pitch = max(-45, min(45, kwargs['pitch']))
        if 'fov' in kwargs:
            self.field_of_view = max(30, min(120, kwargs['fov']))

    def add_light_source(self, position: Vector2, intensity: float = 1.0, 
                        color: Tuple[int, int, int] = Color.WHITE, 
                        radius: float = 100.0, light_type: str = "point"):
        """Add a dynamic light source."""
        light = {
            'position': position,
            'intensity': intensity,
            'color': color,
            'radius': radius,
            'type': light_type,
            'enabled': True
        }
        self.light_sources.append(light)
        return light

    def remove_light_source(self, light):
        """Remove a light source."""
        if light in self.light_sources:
            self.light_sources.remove(light)

    def add_post_effect(self, effect: PostProcessEffect):
        """Add a post-processing effect."""
        self.post_effects.append(effect)

    def remove_post_effect(self, effect: PostProcessEffect):
        """Remove a post-processing effect."""
        if effect in self.post_effects:
            self.post_effects.remove(effect)

    def create_render_target(self, name: str, width: int, height: int) -> pygame.Surface:
        """Create a render target."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.render_targets[name] = surface
        return surface

    def set_render_target(self, name: Optional[str]):
        """Set the active render target."""
        if name is None:
            self.active_render_target = None
        else:
            self.active_render_target = self.render_targets.get(name)

    def clear(self, color: Optional[Tuple[int, int, int]] = None):
        """Clear the screen or active render target."""
        if color is None:
            color = self.background_color
        
        target = self.active_render_target or self.screen
        target.fill(color)
        
        # Reset render stats
        self.render_stats = {
            'objects_rendered': 0,
            'objects_culled': 0,
            'draw_calls': 0,
            'triangles': 0
        }

    def present(self):
        """Present the rendered frame."""
        # Apply post-processing effects
        if self.enable_post_processing and self.post_effects:
            final_surface = self.screen.copy()
            for effect in self.post_effects:
                if effect.enabled:
                    final_surface = effect.apply(final_surface)
            self.screen.blit(final_surface, (0, 0))
        
        # Display debug information
        if self.debug_mode:
            self._draw_debug_info()
        
        pygame.display.flip()

    def world_to_screen(self, world_pos: Vector2) -> Vector2:
        """Enhanced world to screen conversion with camera transformations."""
        # Apply camera offset
        relative_pos = world_pos - self.camera_offset
        
        # Apply camera rotation
        if self.camera_rotation != 0:
            cos_rot = math.cos(math.radians(self.camera_rotation))
            sin_rot = math.sin(math.radians(self.camera_rotation))
            
            rotated_x = relative_pos.x * cos_rot - relative_pos.y * sin_rot
            rotated_y = relative_pos.x * sin_rot + relative_pos.y * cos_rot
            
            relative_pos = Vector2(rotated_x, rotated_y)
        
        # Apply zoom
        screen_pos = relative_pos * self.camera_zoom
        
        # Center on screen
        screen_pos += Vector2(self.width / 2, self.height / 2)
        
        # Apply camera shake
        screen_pos += self.camera_shake_offset
        
        return screen_pos

    def screen_to_world(self, screen_pos: Vector2) -> Vector2:
        """Enhanced screen to world conversion."""
        # Remove camera shake
        adjusted_pos = screen_pos - self.camera_shake_offset
        
        # Remove screen centering
        relative_pos = adjusted_pos - Vector2(self.width / 2, self.height / 2)
        
        # Remove zoom
        relative_pos /= self.camera_zoom
        
        # Remove camera rotation
        if self.camera_rotation != 0:
            cos_rot = math.cos(math.radians(-self.camera_rotation))
            sin_rot = math.sin(math.radians(-self.camera_rotation))
            
            rotated_x = relative_pos.x * cos_rot - relative_pos.y * sin_rot
            rotated_y = relative_pos.x * sin_rot + relative_pos.y * cos_rot
            
            relative_pos = Vector2(rotated_x, rotated_y)
        
        # Add camera offset
        world_pos = relative_pos + self.camera_offset
        
        return world_pos

    def is_in_view(self, position: Vector2, radius: float = 0) -> bool:
        """Check if an object is within the camera's view."""
        if not self.enable_frustum_culling:
            return True
        
        screen_pos = self.world_to_screen(position)
        
        # Check if within screen bounds with margin
        margin = radius * self.camera_zoom
        return (-margin <= screen_pos.x <= self.width + margin and
                -margin <= screen_pos.y <= self.height + margin)

    def calculate_lighting(self, position: Vector2, normal: Vector2 = None) -> float:
        """Calculate lighting factor at a position."""
        if not self.enable_lighting:
            return 1.0
        
        light_factor = self.ambient_light
        
        for light in self.light_sources:
            if not light['enabled']:
                continue
            
            distance = (light['position'] - position).magnitude()
            if distance < light['radius']:
                # Distance falloff
                falloff = 1.0 - (distance / light['radius'])
                
                # Normal-based lighting (if normal provided)
                if normal:
                    light_dir = (light['position'] - position).normalized()
                    dot_product = max(0, normal.dot(light_dir))
                    falloff *= dot_product
                
                light_factor += light['intensity'] * falloff
        
        return min(1.0, light_factor)

    def apply_fog(self, color: Tuple[int, int, int], distance: float) -> Tuple[int, int, int]:
        """Apply fog effect to a color based on distance."""
        if distance <= self.fog_distance:
            return color
        
        fog_factor = min(1.0, (distance - self.fog_distance) / (self.render_distance - self.fog_distance))
        return Color.lerp(color, self.fog_color, fog_factor)

    # Enhanced drawing methods
    def draw_sprite_advanced(self, surface: pygame.Surface, position: Vector2, 
                           rotation: float = 0, scale: Vector2 = None,
                           tint: Tuple[int, int, int] = None, alpha: int = 255,
                           layer: str = "default"):
        """Draw a sprite with advanced features."""
        if not self.is_in_view(position, max(surface.get_width(), surface.get_height()) / 2):
            self.render_stats['objects_culled'] += 1
            return
        
        if scale is None:
            scale = Vector2(1, 1)
        
        # Apply transformations
        transformed_surface = surface.copy()
        
        # Apply tint
        if tint:
            tint_surface = pygame.Surface(transformed_surface.get_size(), pygame.SRCALPHA)
            tint_surface.fill(tint + (alpha,))
            transformed_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULTIPLY)
        
        # Apply alpha
        if alpha < 255:
            transformed_surface.set_alpha(alpha)
        
        # Scale
        if scale.x != 1 or scale.y != 1:
            new_width = max(1, int(transformed_surface.get_width() * scale.x))
            new_height = max(1, int(transformed_surface.get_height() * scale.y))
            transformed_surface = pygame.transform.scale(transformed_surface, (new_width, new_height))
        
        # Rotate
        if rotation != 0:
            transformed_surface = pygame.transform.rotate(transformed_surface, rotation)
        
        # Convert to screen coordinates
        screen_pos = self.world_to_screen(position)
        
        # Apply lighting
        if self.enable_lighting:
            light_factor = self.calculate_lighting(position)
            if light_factor < 1.0:
                dark_surface = pygame.Surface(transformed_surface.get_size(), pygame.SRCALPHA)
                dark_surface.fill((0, 0, 0, int((1.0 - light_factor) * 255)))
                transformed_surface.blit(dark_surface, (0, 0), special_flags=pygame.BLEND_MULTIPLY)
        
        # Center and draw
        rect = transformed_surface.get_rect()
        rect.center = (int(screen_pos.x), int(screen_pos.y))
        
        target = self.active_render_target or self.screen
        target.blit(transformed_surface, rect)
        
        self.render_stats['objects_rendered'] += 1
        self.render_stats['draw_calls'] += 1

    def draw_rect_advanced(self, position: Vector2, size: Vector2, 
                          color: Tuple[int, int, int], filled: bool = True,
                          border_width: int = 1, border_color: Tuple[int, int, int] = None,
                          rotation: float = 0, layer: str = "default"):
        """Draw a rectangle with advanced features."""
        if not self.is_in_view(position, max(size.x, size.y) / 2):
            self.render_stats['objects_culled'] += 1
            return
        
        screen_pos = self.world_to_screen(position)
        scaled_size = size * self.camera_zoom
        
        # Apply lighting
        final_color = color
        if self.enable_lighting:
            light_factor = self.calculate_lighting(position)
            final_color = Color.darken(color, 1.0 - light_factor)
        
        target = self.active_render_target or self.screen
        
        if rotation == 0:
            # Simple rectangle
            rect = pygame.Rect(int(screen_pos.x), int(screen_pos.y), int(scaled_size.x), int(scaled_size.y))
            
            if filled:
                pygame.draw.rect(target, final_color, rect)
            
            if border_width > 0 and border_color:
                pygame.draw.rect(target, border_color, rect, border_width)
        else:
            # Rotated rectangle (using polygon)
            self._draw_rotated_rect(target, screen_pos, scaled_size, final_color, rotation, filled, border_width, border_color)
        
        self.render_stats['objects_rendered'] += 1
        self.render_stats['draw_calls'] += 1

    def _draw_rotated_rect(self, target: pygame.Surface, center: Vector2, size: Vector2, 
                          color: Tuple[int, int, int], rotation: float, filled: bool,
                          border_width: int, border_color: Tuple[int, int, int]):
        """Draw a rotated rectangle using polygon."""
        half_width = size.x / 2
        half_height = size.y / 2
        
        # Calculate corners
        corners = [
            Vector2(-half_width, -half_height),
            Vector2(half_width, -half_height),
            Vector2(half_width, half_height),
            Vector2(-half_width, half_height)
        ]
        
        # Rotate corners
        cos_rot = math.cos(math.radians(rotation))
        sin_rot = math.sin(math.radians(rotation))
        
        rotated_corners = []
        for corner in corners:
            rotated_x = corner.x * cos_rot - corner.y * sin_rot
            rotated_y = corner.x * sin_rot + corner.y * cos_rot
            rotated_corners.append((center.x + rotated_x, center.y + rotated_y))
        
        if filled:
            pygame.draw.polygon(target, color, rotated_corners)
        
        if border_width > 0 and border_color:
            pygame.draw.polygon(target, border_color, rotated_corners, border_width)

    def draw_circle_advanced(self, center: Vector2, radius: float, 
                           color: Tuple[int, int, int], filled: bool = True,
                           border_width: int = 1, border_color: Tuple[int, int, int] = None,
                           layer: str = "default"):
        """Draw a circle with advanced features."""
        if not self.is_in_view(center, radius):
            self.render_stats['objects_culled'] += 1
            return
        
        screen_pos = self.world_to_screen(center)
        scaled_radius = int(radius * self.camera_zoom)
        
        if scaled_radius < 1:
            return
        
        # Apply lighting
        final_color = color
        if self.enable_lighting:
            light_factor = self.calculate_lighting(center)
            final_color = Color.darken(color, 1.0 - light_factor)
        
        target = self.active_render_target or self.screen
        
        if filled:
            pygame.draw.circle(target, final_color, (int(screen_pos.x), int(screen_pos.y)), scaled_radius)
        
        if border_width > 0 and border_color:
            pygame.draw.circle(target, border_color, (int(screen_pos.x), int(screen_pos.y)), scaled_radius, border_width)
        
        self.render_stats['objects_rendered'] += 1
        self.render_stats['draw_calls'] += 1

    def draw_line_advanced(self, start: Vector2, end: Vector2, 
                          color: Tuple[int, int, int], width: int = 1,
                          layer: str = "default"):
        """Draw a line with advanced features."""
        screen_start = self.world_to_screen(start)
        screen_end = self.world_to_screen(end)
        
        # Apply lighting (use midpoint)
        final_color = color
        if self.enable_lighting:
            midpoint = (start + end) * 0.5
            light_factor = self.calculate_lighting(midpoint)
            final_color = Color.darken(color, 1.0 - light_factor)
        
        target = self.active_render_target or self.screen
        pygame.draw.line(target, final_color, 
                        (int(screen_start.x), int(screen_start.y)), 
                        (int(screen_end.x), int(screen_end.y)), 
                        max(1, int(width * self.camera_zoom)))
        
        self.render_stats['draw_calls'] += 1

    def draw_text_advanced(self, text: str, position: Vector2, 
                          color: Tuple[int, int, int] = Color.WHITE,
                          font_size: int = 24, font_name: Optional[str] = None,
                          center: bool = False, shadow: bool = False,
                          shadow_offset: Vector2 = Vector2(2, 2),
                          shadow_color: Tuple[int, int, int] = Color.BLACK,
                          layer: str = "default"):
        """Draw text with advanced features."""
        if not self.is_in_view(position, font_size):
            self.render_stats['objects_culled'] += 1
            return
        
        scaled_font_size = max(8, int(font_size * self.camera_zoom))
        
        try:
            font = pygame.font.Font(font_name, scaled_font_size)
            
            # Apply lighting
            final_color = color
            if self.enable_lighting:
                light_factor = self.calculate_lighting(position)
                final_color = Color.darken(color, 1.0 - light_factor)
            
            text_surface = font.render(str(text), True, final_color)
            screen_pos = self.world_to_screen(position)
            
            target = self.active_render_target or self.screen
            
            # Draw shadow
            if shadow:
                shadow_surface = font.render(str(text), True, shadow_color)
                shadow_screen_pos = screen_pos + shadow_offset
                
                if center:
                    shadow_rect = shadow_surface.get_rect(center=(int(shadow_screen_pos.x), int(shadow_screen_pos.y)))
                    target.blit(shadow_surface, shadow_rect)
                else:
                    target.blit(shadow_surface, (int(shadow_screen_pos.x), int(shadow_screen_pos.y)))
            
            # Draw text
            if center:
                text_rect = text_surface.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
                target.blit(text_surface, text_rect)
            else:
                target.blit(text_surface, (int(screen_pos.x), int(screen_pos.y)))
            
            self.render_stats['objects_rendered'] += 1
            self.render_stats['draw_calls'] += 1
            
        except (pygame.error, TypeError, ValueError) as e:
            print(f"Text rendering error: {e}")

    def set_camera_shake(self, intensity: float, duration: float = 0.1):
        """Set camera shake effect."""
        import random
        self.camera_shake_offset = Vector2(
            random.uniform(-intensity, intensity),
            random.uniform(-intensity, intensity)
        )

    def clear_camera_shake(self):
        """Clear camera shake effect."""
        self.camera_shake_offset = Vector2.zero()

    def get_render_stats(self) -> Dict[str, int]:
        """Get rendering statistics."""
        return self.render_stats.copy()

    def optimize_performance(self):
        """Optimize renderer performance."""
        # Clear texture cache if too large
        if len(self.texture_cache) > self.max_texture_cache_size:
            # Remove oldest entries (simple FIFO)
            items_to_remove = len(self.texture_cache) - self.max_texture_cache_size
            keys_to_remove = list(self.texture_cache.keys())[:items_to_remove]
            for key in keys_to_remove:
                del self.texture_cache[key]
        
        # Clean up render targets
        for name, surface in list(self.render_targets.items()):
            if surface.get_locks():  # If surface is locked, it might be in use
                continue
        
        print("Renderer performance optimized")

    def _draw_debug_info(self):
        """Draw debug information on screen."""
        debug_info = [
            f"Render Mode: {self.rendering_mode}",
            f"Objects Rendered: {self.render_stats['objects_rendered']}",
            f"Objects Culled: {self.render_stats['objects_culled']}",
            f"Draw Calls: {self.render_stats['draw_calls']}",
            f"Camera Zoom: {self.camera_zoom:.2f}",
            f"Camera Position: ({self.camera_offset.x:.1f}, {self.camera_offset.y:.1f})",
            f"Light Sources: {len(self.light_sources)}",
            f"Layers: {len(self.layers)}"
        ]
        
        y_offset = 10
        for info in debug_info:
            text_surface = pygame.font.Font(None, 24).render(info, True, Color.WHITE)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25

    def cleanup(self):
        """Clean up renderer resources."""
        self.texture_cache.clear()
        self.render_targets.clear()
        self.layers.clear()
        self.light_sources.clear()
        self.post_effects.clear()
        
        print("Renderer cleaned up")


# Maintain backward compatibility
Renderer = AdvancedRenderer
