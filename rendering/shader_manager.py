"""
VoidRay Shader Manager
Advanced shader system for post-processing and visual effects.
"""

import pygame
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from ..math.vector2 import Vector2


class Shader:
    """Base shader class for visual effects."""

    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.uniforms: Dict[str, Any] = {}
        self.render_targets: List[pygame.Surface] = []

    def set_uniform(self, name: str, value: Any):
        """Set a uniform value."""
        self.uniforms[name] = value

    def get_uniform(self, name: str, default: Any = None) -> Any:
        """Get a uniform value."""
        return self.uniforms.get(name, default)

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply the shader effect to a surface."""
        raise NotImplementedError("Subclasses must implement apply method")


class RetroShader(Shader):
    """Retro pixelation shader for pixel-perfect 2D games."""

    def __init__(self, pixel_size: int = 2):
        super().__init__("retro")
        self.pixel_size = pixel_size

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply retro pixelation effect."""
        if self.pixel_size <= 1:
            return surface

        # Downscale
        original_size = surface.get_size()
        small_size = (original_size[0] // self.pixel_size, 
                     original_size[1] // self.pixel_size)

        if small_size[0] <= 0 or small_size[1] <= 0:
            return surface

        # Scale down and back up for pixelation effect
        small_surface = pygame.transform.scale(surface, small_size)
        result = pygame.transform.scale(small_surface, original_size)

        return result


class ScanlineShader(Shader):
    """CRT-style scanline shader."""

    def __init__(self):
        super().__init__("scanlines")
        self.line_intensity = 0.3
        self.line_spacing = 2

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
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
        self.light_sources = []
        self.ambient_light = 0.2

    def add_light(self, position, radius: float, intensity: float, color: tuple = (255, 255, 255)):
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

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
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


class BlurShader(Shader):
    """Gaussian blur shader effect."""

    def __init__(self, radius: float = 5.0):
        super().__init__("blur")
        self.set_uniform("radius", radius)
        self.set_uniform("sigma", radius / 3.0)

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply blur effect."""
        radius = self.get_uniform("radius", 5.0)
        if radius <= 0:
            return surface

        # Simple box blur approximation
        result = surface.copy()

        # Multiple passes for better quality
        passes = max(1, int(radius / 2))
        for _ in range(passes):
            result = pygame.transform.smoothscale(
                pygame.transform.smoothscale(result, 
                    (surface.get_width() // 2, surface.get_height() // 2)),
                (surface.get_width(), surface.get_height())
            )

        return result


class BloomShader(Shader):
    """Bloom effect shader."""

    def __init__(self, threshold: float = 0.8, intensity: float = 1.5):
        super().__init__("bloom")
        self.set_uniform("threshold", threshold)
        self.set_uniform("intensity", intensity)
        self.blur_shader = BlurShader(10.0)

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply bloom effect."""
        threshold = self.get_uniform("threshold", 0.8)
        intensity = self.get_uniform("intensity", 1.5)

        # Extract bright areas
        bright_surface = self._extract_bright_areas(surface, threshold)

        # Blur the bright areas
        bloom_surface = self.blur_shader.apply(bright_surface, delta_time)

        # Combine with original
        result = surface.copy()
        bloom_surface.set_alpha(int(255 * intensity))
        result.blit(bloom_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        return result

    def _extract_bright_areas(self, surface: pygame.Surface, threshold: float) -> pygame.Surface:
        """Extract areas brighter than threshold."""
        result = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        # Convert threshold to 0-255 range
        threshold_value = int(threshold * 255)

        # Simple bright area extraction using pixel access
        pixels = pygame.surfarray.array3d(surface)
        mask = np.max(pixels, axis=2) > threshold_value

        bright_pixels = pixels.copy()
        bright_pixels[~mask] = [0, 0, 0]

        pygame.surfarray.blit_array(result, bright_pixels)
        return result


class ChromaticAberrationShader(Shader):
    """Chromatic aberration effect."""

    def __init__(self, strength: float = 2.0):
        super().__init__("chromatic_aberration")
        self.set_uniform("strength", strength)

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply chromatic aberration effect."""
        strength = self.get_uniform("strength", 2.0)

        if strength <= 0:
            return surface

        result = pygame.Surface(surface.get_size())

        # Separate RGB channels and offset them
        r_surface = surface.copy()
        g_surface = surface.copy()
        b_surface = surface.copy()

        # Apply color channel filters
        r_array = pygame.surfarray.array3d(r_surface)
        g_array = pygame.surfarray.array3d(g_surface)
        b_array = pygame.surfarray.array3d(b_surface)

        # Zero out other channels
        r_array[:, :, 1] = 0  # Remove green
        r_array[:, :, 2] = 0  # Remove blue

        g_array[:, :, 0] = 0  # Remove red
        g_array[:, :, 2] = 0  # Remove blue

        b_array[:, :, 0] = 0  # Remove red
        b_array[:, :, 1] = 0  # Remove green

        pygame.surfarray.blit_array(r_surface, r_array)
        pygame.surfarray.blit_array(g_surface, g_array)
        pygame.surfarray.blit_array(b_surface, b_array)

        # Offset channels
        offset = int(strength)

        # Red channel offset left
        result.blit(r_surface, (-offset, 0), special_flags=pygame.BLEND_ADD)

        # Green channel no offset
        result.blit(g_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        # Blue channel offset right
        result.blit(b_surface, (offset, 0), special_flags=pygame.BLEND_ADD)

        return result


class VignetteShader(Shader):
    """Vignette darkening effect."""

    def __init__(self, intensity: float = 0.5, radius: float = 0.8):
        super().__init__("vignette")
        self.set_uniform("intensity", intensity)
        self.set_uniform("radius", radius)

    def apply(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply vignette effect."""
        intensity = self.get_uniform("intensity", 0.5)
        radius = self.get_uniform("radius", 0.8)

        if intensity <= 0:
            return surface

        result = surface.copy()
        vignette_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        width, height = surface.get_size()
        center_x, center_y = width // 2, height // 2
        max_distance = max(width, height) // 2

        # Create vignette mask
        for x in range(width):
            for y in range(height):
                # Calculate distance from center
                dx = (x - center_x) / max_distance
                dy = (y - center_y) / max_distance
                distance = (dx * dx + dy * dy) ** 0.5

                # Apply vignette based on distance
                if distance > radius:
                    vignette_factor = min(1.0, (distance - radius) / (1.0 - radius))
                    alpha = int(255 * intensity * vignette_factor)
                    vignette_surface.set_at((x, y), (0, 0, 0, alpha))

        result.blit(vignette_surface, (0, 0))
        return result


class ShaderManager:
    """
    Manages and applies post-processing shaders.
    """

    def __init__(self):
        self.shaders: List[Shader] = []
        self.enabled = True

        # Built-in shaders
        self.built_in_shaders: Dict[str, type] = {
            'blur': BlurShader,
            'bloom': BloomShader,
            'chromatic_aberration': ChromaticAberrationShader,
            'vignette': VignetteShader,
            'retro': RetroShader,
            'scanlines': ScanlineShader,
            'lighting': LightingShader
        }

        # Render targets for multi-pass effects
        self.render_targets: List[pygame.Surface] = []

        # Performance tracking
        self.shader_times: Dict[str, float] = {}

    def add_shader(self, shader: Shader):
        """Add a shader to the pipeline."""
        self.shaders.append(shader)

    def remove_shader(self, shader_name: str):
        """Remove a shader by name."""
        self.shaders = [s for s in self.shaders if s.name != shader_name]

    def get_shader(self, name: str) -> Optional[Shader]:
        """Get a shader by name."""
        for shader in self.shaders:
            if shader.name == name:
                return shader
        return None

    def create_shader(self, shader_type: str, **kwargs) -> Optional[Shader]:
        """Create a built-in shader."""
        if shader_type in self.built_in_shaders:
            return self.built_in_shaders[shader_type](**kwargs)
        return None

    def apply_shaders(self, surface: pygame.Surface, delta_time: float) -> pygame.Surface:
        """Apply all enabled shaders in order."""
        if not self.enabled or not self.shaders:
            return surface

        result = surface

        for shader in self.shaders:
            if shader.enabled:
                import time
                start_time = time.perf_counter()

                result = shader.apply(result, delta_time)

                end_time = time.perf_counter()
                self.shader_times[shader.name] = end_time - start_time

        return result

    def clear_shaders(self):
        """Remove all shaders."""
        self.shaders.clear()

    def enable_shader(self, name: str, enabled: bool = True):
        """Enable or disable a specific shader."""
        shader = self.get_shader(name)
        if shader:
            shader.enabled = enabled

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get shader performance statistics."""
        total_time = sum(self.shader_times.values())
        return {
            'total_time': total_time,
            'shader_count': len(self.shaders),
            'individual_times': self.shader_times.copy()
        }

    def create_render_target(self, width: int, height: int) -> pygame.Surface:
        """Create a render target surface."""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.render_targets.append(surface)
        return surface

    def cleanup_render_targets(self):
        """Clean up unused render targets."""
        self.render_targets.clear()

    def set_retro_mode(self, enabled: bool, pixel_size: int = 2):
        """Enable/disable retro pixel art mode for backward compatibility."""
        if enabled:
            # Remove existing retro shader if present
            self.remove_shader("retro")

            # Create a simple pixelation shader
            retro_shader = RetroShader(pixel_size)
            self.add_shader(retro_shader)
            print(f"Retro mode enabled with pixel size {pixel_size}")
        else:
            self.remove_shader("retro")
            print("Retro mode disabled")

    def set_lighting_mode(self, enabled: bool):
        """Enable/disable dynamic lighting for backward compatibility."""
        if enabled:
            lighting_shader = self.create_shader("lighting")
            if lighting_shader:
                self.add_shader(lighting_shader)
                print("Lighting mode enabled")
        else:
            self.remove_shader("lighting")
            print("Lighting mode disabled")

    def set_crt_mode(self, enabled: bool):
        """Enable/disable CRT scanline effect for backward compatibility."""
        if enabled:
            scanline_shader = ScanlineShader()
            self.add_shader(scanline_shader)
            print("CRT mode enabled")
        else:
            self.remove_shader("scanlines")
            print("CRT mode disabled")


# Utility functions for common shader effects
def create_post_processing_pipeline(blur_radius: float = 0, 
                                  bloom_enabled: bool = False,
                                  chromatic_aberration: float = 0,
                                  vignette_intensity: float = 0) -> ShaderManager:
    """Create a common post-processing pipeline."""
    manager = ShaderManager()

    if blur_radius > 0:
        blur = BlurShader(blur_radius)
        manager.add_shader(blur)

    if bloom_enabled:
        bloom = BloomShader()
        manager.add_shader(bloom)

    if chromatic_aberration > 0:
        aberration = ChromaticAberrationShader(chromatic_aberration)
        manager.add_shader(aberration)

    if vignette_intensity > 0:
        vignette = VignetteShader(vignette_intensity)
        manager.add_shader(vignette)

    return manager