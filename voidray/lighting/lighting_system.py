
"""
VoidRay Lighting System
Dynamic lighting and shadow effects for enhanced 2.5D rendering.
"""

import pygame
import math
from typing import List, Tuple
from ..math.vector2 import Vector2
from ..utils.color import Color


class Light:
    """Individual light source."""
    
    def __init__(self, position: Vector2, color: Tuple[int, int, int] = (255, 255, 255), 
                 intensity: float = 1.0, radius: float = 200.0):
        self.position = position
        self.color = color
        self.intensity = intensity
        self.radius = radius
        self.enabled = True
        self.flicker = False
        self.flicker_speed = 5.0
        self.flicker_amount = 0.2
        self._flicker_timer = 0.0
        
    def update(self, delta_time: float):
        """Update light properties."""
        if self.flicker:
            self._flicker_timer += delta_time * self.flicker_speed
            flicker_factor = 1.0 + math.sin(self._flicker_timer) * self.flicker_amount
            self.current_intensity = self.intensity * flicker_factor
        else:
            self.current_intensity = self.intensity
    
    def get_light_at_position(self, position: Vector2) -> Tuple[float, Tuple[int, int, int]]:
        """Get light influence at a specific position."""
        if not self.enabled:
            return 0.0, (0, 0, 0)
            
        distance = (position - self.position).magnitude()
        
        if distance >= self.radius:
            return 0.0, (0, 0, 0)
        
        # Calculate falloff
        falloff = 1.0 - (distance / self.radius)
        falloff = falloff * falloff  # Quadratic falloff
        
        light_strength = falloff * self.current_intensity
        
        # Apply color
        light_color = (
            int(self.color[0] * light_strength),
            int(self.color[1] * light_strength),
            int(self.color[2] * light_strength)
        )
        
        return light_strength, light_color


class AmbientLight:
    """Global ambient lighting."""
    
    def __init__(self, color: Tuple[int, int, int] = (50, 50, 70), intensity: float = 0.3):
        self.color = color
        self.intensity = intensity
        self.enabled = True
    
    def get_ambient_color(self) -> Tuple[int, int, int]:
        """Get the ambient color."""
        if not self.enabled:
            return (0, 0, 0)
            
        return (
            int(self.color[0] * self.intensity),
            int(self.color[1] * self.intensity),
            int(self.color[2] * self.intensity)
        )


class LightingSystem:
    """System for managing dynamic lighting."""
    
    def __init__(self):
        self.lights: List[Light] = []
        self.ambient_light = AmbientLight()
        self.enabled = True
        self.shadow_quality = "medium"  # low, medium, high
        self.light_map: pygame.Surface = None
        self.light_map_size = (800, 600)
        
    def add_light(self, light: Light):
        """Add a light to the system."""
        self.lights.append(light)
        
    def remove_light(self, light: Light):
        """Remove a light from the system."""
        if light in self.lights:
            self.lights.remove(light)
            
    def create_point_light(self, position: Vector2, color: Tuple[int, int, int] = (255, 255, 255),
                          intensity: float = 1.0, radius: float = 200.0) -> Light:
        """Create and add a point light."""
        light = Light(position, color, intensity, radius)
        self.add_light(light)
        return light
        
    def update(self, delta_time: float):
        """Update all lights."""
        if not self.enabled:
            return
            
        for light in self.lights:
            light.update(delta_time)
            
    def calculate_lighting_at_position(self, position: Vector2) -> Tuple[int, int, int]:
        """Calculate combined lighting at a position."""
        if not self.enabled:
            return (255, 255, 255)
            
        # Start with ambient light
        total_r, total_g, total_b = self.ambient_light.get_ambient_color()
        
        # Add contribution from each light
        for light in self.lights:
            strength, light_color = light.get_light_at_position(position)
            if strength > 0:
                total_r += light_color[0]
                total_g += light_color[1]
                total_b += light_color[2]
        
        # Clamp values
        total_r = min(255, max(0, total_r))
        total_g = min(255, max(0, total_g))
        total_b = min(255, max(0, total_b))
        
        return (total_r, total_g, total_b)
        
    def generate_light_map(self, width: int, height: int, tile_size: int = 16):
        """Generate a light map for efficient lighting."""
        if not self.enabled:
            return
            
        self.light_map_size = (width, height)
        self.light_map = pygame.Surface((width // tile_size, height // tile_size))
        
        # Calculate lighting for each tile
        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                world_pos = Vector2(x + tile_size // 2, y + tile_size // 2)
                light_color = self.calculate_lighting_at_position(world_pos)
                
                tile_x = x // tile_size
                tile_y = y // tile_size
                
                if tile_x < self.light_map.get_width() and tile_y < self.light_map.get_height():
                    self.light_map.set_at((tile_x, tile_y), light_color)
                    
    def apply_lighting_to_surface(self, surface: pygame.Surface, position: Vector2) -> pygame.Surface:
        """Apply lighting to a surface."""
        if not self.enabled:
            return surface
            
        # Calculate lighting at the surface position
        light_color = self.calculate_lighting_at_position(position)
        
        # Create a tinted version of the surface
        tinted_surface = surface.copy()
        
        # Simple color multiplication
        overlay = pygame.Surface(surface.get_size())
        overlay.fill(light_color)
        tinted_surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted_surface
        
    def render_light_map(self, renderer, camera_offset: Vector2 = Vector2.zero()):
        """Render the light map as an overlay."""
        if not self.enabled or not self.light_map:
            return
            
        # Scale up the light map and render it
        scaled_light_map = pygame.transform.scale(self.light_map, self.light_map_size)
        
        # Apply camera offset
        render_pos = (-camera_offset.x, -camera_offset.y)
        
        # Blend the light map onto the screen
        renderer.screen.blit(scaled_light_map, render_pos, special_flags=pygame.BLEND_MULT)
        
    def set_shadow_quality(self, quality: str):
        """Set shadow rendering quality."""
        if quality in ["low", "medium", "high"]:
            self.shadow_quality = quality
            
    def clear_lights(self):
        """Remove all lights."""
        self.lights.clear()
        
    def get_light_count(self) -> int:
        """Get the number of active lights."""
        return len([light for light in self.lights if light.enabled])
