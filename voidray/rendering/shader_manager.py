
"""
VoidRay Shader Manager
Manages shaders and post-processing effects for enhanced 2.5D rendering.
"""

import pygame
import numpy as np
from typing import Dict, List, Optional, Callable
from ..math.vector2 import Vector2


class Shader:
    """Base shader class for rendering effects."""
    
    def __init__(self, name: str):
        self.name = name
        self.uniforms: Dict[str, any] = {}
        
    def set_uniform(self, name: str, value):
        """Set shader uniform value."""
        self.uniforms[name] = value
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply shader effect to surface."""
        return surface


class RetroShader(Shader):
    """Retro/pixel-perfect shader for 2D games."""
    
    def __init__(self):
        super().__init__("retro")
        self.pixel_size = 2
        self.color_depth = 16
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply retro pixelation effect."""
        # Downscale
        small_size = (surface.get_width() // self.pixel_size, 
                     surface.get_height() // self.pixel_size)
        small_surface = pygame.transform.scale(surface, small_size)
        
        # Upscale with nearest neighbor
        result = pygame.transform.scale(small_surface, surface.get_size())
        
        # Reduce color depth
        if self.color_depth < 256:
            pixels = pygame.surfarray.array3d(result)
            factor = 256 // self.color_depth
            pixels = (pixels // factor) * factor
            pygame.surfarray.blit_array(result, pixels)
        
        return result


class ScanlineShader(Shader):
    """CRT-style scanline shader."""
    
    def __init__(self):
        super().__init__("scanlines")
        self.line_intensity = 0.3
        self.line_spacing = 2
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply scanline effect."""
        result = surface.copy()
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        height = surface.get_height()
        for y in range(0, height, self.line_spacing):
            alpha = int(255 * self.line_intensity)
            pygame.draw.line(overlay, (0, 0, 0, alpha), 
                           (0, y), (surface.get_width(), y))
        
        result.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)
        return result


class LightingShader(Shader):
    """Dynamic lighting shader for 2.5D environments."""
    
    def __init__(self):
        super().__init__("lighting")
        self.light_sources: List[Dict] = []
        self.ambient_light = 0.2
        
    def add_light(self, position: Vector2, radius: float, intensity: float, color: tuple = (255, 255, 255)):
        """Add a light source."""
        self.light_sources.append({
            'position': position,
            'radius': radius,
            'intensity': intensity,
            'color': color
        })
    
    def clear_lights(self):
        """Clear all light sources."""
        self.light_sources.clear()
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply dynamic lighting."""
        result = surface.copy()
        
        # Create lighting overlay
        lighting = pygame.Surface(surface.get_size())
        lighting.fill((int(255 * self.ambient_light),) * 3)
        
        # Add light sources
        for light in self.light_sources:
            pos = light['position']
            radius = light['radius']
            intensity = light['intensity']
            color = light['color']
            
            # Create radial gradient
            light_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            for r in range(int(radius)):
                alpha = int(255 * intensity * (1 - r / radius))
                light_color = (*color, alpha)
                pygame.draw.circle(light_surface, light_color, 
                                 (int(radius), int(radius)), int(radius - r))
            
            # Blend with lighting
            lighting.blit(light_surface, 
                         (pos.x - radius, pos.y - radius), 
                         special_flags=pygame.BLEND_ADD)
        
        # Apply lighting to surface
        result.blit(lighting, (0, 0), special_flags=pygame.BLEND_MULT)
        return result


class ShaderManager:
    """Manages shader pipeline for advanced rendering."""
    
    def __init__(self):
        self.shaders: Dict[str, Shader] = {}
        self.active_shaders: List[str] = []
        self.post_process_enabled = True
        
        # Register built-in shaders
        self.register_shader(RetroShader())
        self.register_shader(ScanlineShader())
        self.register_shader(LightingShader())
    
    def register_shader(self, shader: Shader):
        """Register a shader."""
        self.shaders[shader.name] = shader
    
    def enable_shader(self, name: str):
        """Enable a shader in the pipeline."""
        if name in self.shaders and name not in self.active_shaders:
            self.active_shaders.append(name)
    
    def disable_shader(self, name: str):
        """Disable a shader in the pipeline."""
        if name in self.active_shaders:
            self.active_shaders.remove(name)
    
    def get_shader(self, name: str) -> Optional[Shader]:
        """Get shader by name."""
        return self.shaders.get(name)
    
    def process(self, surface: pygame.Surface) -> pygame.Surface:
        """Process surface through shader pipeline."""
        if not self.post_process_enabled:
            return surface
        
        result = surface
        for shader_name in self.active_shaders:
            if shader_name in self.shaders:
                result = self.shaders[shader_name].apply(result)
        
        return result
    
    def set_lighting_mode(self, enabled: bool):
        """Enable/disable dynamic lighting."""
        if enabled:
            self.enable_shader("lighting")
        else:
            self.disable_shader("lighting")
    
    def set_retro_mode(self, enabled: bool, pixel_size: int = 2):
        """Enable/disable retro pixel art mode."""
        if enabled:
            retro_shader = self.get_shader("retro")
            if retro_shader:
                retro_shader.pixel_size = pixel_size
            self.enable_shader("retro")
        else:
            self.disable_shader("retro")
    
    def set_crt_mode(self, enabled: bool):
        """Enable/disable CRT scanline effect."""
        if enabled:
            self.enable_shader("scanlines")
        else:
            self.disable_shader("scanlines")
