
"""
VoidRay Post-Processing Effects
Screen-space effects like bloom, blur, and color grading.
"""

import pygame
import numpy as np
from typing import List, Optional


class PostProcessingEffect:
    """Base class for post-processing effects."""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.intensity = 1.0
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply the effect to a surface."""
        return surface


class BlurEffect(PostProcessingEffect):
    """Gaussian blur effect."""
    
    def __init__(self, radius: int = 3):
        super().__init__("Blur")
        self.radius = radius
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        if not self.enabled or self.radius <= 0:
            return surface
            
        # Simple box blur implementation
        result = surface.copy()
        
        # Convert to numpy array for faster processing
        try:
            arr = pygame.surfarray.array3d(surface)
            
            # Apply horizontal blur
            for y in range(arr.shape[1]):
                for x in range(self.radius, arr.shape[0] - self.radius):
                    for c in range(3):
                        total = sum(arr[x + dx, y, c] for dx in range(-self.radius, self.radius + 1))
                        arr[x, y, c] = total // (2 * self.radius + 1)
            
            # Apply vertical blur
            for x in range(arr.shape[0]):
                for y in range(self.radius, arr.shape[1] - self.radius):
                    for c in range(3):
                        total = sum(arr[x, y + dy, c] for dy in range(-self.radius, self.radius + 1))
                        arr[x, y, c] = total // (2 * self.radius + 1)
            
            pygame.surfarray.blit_array(result, arr)
            
        except ImportError:
            # Fallback without numpy
            pass
            
        return result


class BloomEffect(PostProcessingEffect):
    """Bloom effect for glowing highlights."""
    
    def __init__(self, threshold: int = 200, intensity: float = 0.5):
        super().__init__("Bloom")
        self.threshold = threshold
        self.bloom_intensity = intensity
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        if not self.enabled:
            return surface
            
        # Extract bright areas
        bright_areas = surface.copy()
        bright_areas.fill((0, 0, 0))
        
        # Simple brightness extraction
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                pixel = surface.get_at((x, y))
                brightness = (pixel[0] + pixel[1] + pixel[2]) / 3
                
                if brightness > self.threshold:
                    bright_areas.set_at((x, y), pixel)
        
        # Blur the bright areas
        blur_effect = BlurEffect(5)
        blurred_bright = blur_effect.apply(bright_areas)
        
        # Blend with original
        result = surface.copy()
        blurred_bright.set_alpha(int(255 * self.bloom_intensity))
        result.blit(blurred_bright, (0, 0), special_flags=pygame.BLEND_ADD)
        
        return result


class ColorGradingEffect(PostProcessingEffect):
    """Color grading effect for mood and atmosphere."""
    
    def __init__(self, tint: tuple = (255, 255, 255), saturation: float = 1.0):
        super().__init__("ColorGrading")
        self.tint = tint
        self.saturation = saturation
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        if not self.enabled:
            return surface
            
        result = surface.copy()
        
        # Apply tint
        if self.tint != (255, 255, 255):
            tint_surface = pygame.Surface(surface.get_size())
            tint_surface.fill(self.tint)
            tint_surface.set_alpha(128)
            result.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        # Apply saturation (simplified)
        if self.saturation != 1.0:
            # Convert to grayscale
            grayscale = pygame.transform.grayscale(surface)
            
            # Blend original with grayscale based on saturation
            alpha = int(255 * (1.0 - self.saturation))
            grayscale.set_alpha(alpha)
            result.blit(grayscale, (0, 0))
        
        return result


class PostProcessingPipeline:
    """Pipeline for applying multiple post-processing effects."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.effects: List[PostProcessingEffect] = []
        self.enabled = True
        self.render_target: Optional[pygame.Surface] = None
        
    def add_effect(self, effect: PostProcessingEffect):
        """Add an effect to the pipeline."""
        self.effects.append(effect)
        
    def remove_effect(self, effect_name: str):
        """Remove an effect by name."""
        self.effects = [e for e in self.effects if e.name != effect_name]
        
    def get_effect(self, effect_name: str) -> Optional[PostProcessingEffect]:
        """Get an effect by name."""
        for effect in self.effects:
            if effect.name == effect_name:
                return effect
        return None
        
    def process(self, surface: pygame.Surface) -> pygame.Surface:
        """Process the surface through all effects."""
        if not self.enabled:
            return surface
            
        result = surface
        
        for effect in self.effects:
            if effect.enabled:
                result = effect.apply(result)
                
        return result
        
    def setup_render_target(self):
        """Set up render target for post-processing."""
        self.render_target = pygame.Surface(self.screen.get_size())
        
    def begin_frame(self):
        """Begin frame rendering to render target."""
        if self.enabled and self.render_target:
            return self.render_target
        return self.screen
        
    def end_frame(self):
        """Apply post-processing and present to screen."""
        if self.enabled and self.render_target:
            processed = self.process(self.render_target)
            self.screen.blit(processed, (0, 0))
        
    def create_default_effects(self):
        """Create some default post-processing effects."""
        # Add subtle bloom for glowing effects
        bloom = BloomEffect(threshold=220, intensity=0.3)
        self.add_effect(bloom)
        
        # Add color grading for atmosphere
        grading = ColorGradingEffect(tint=(255, 250, 240))  # Warm tint
        self.add_effect(grading)
        
    def toggle_effect(self, effect_name: str):
        """Toggle an effect on/off."""
        effect = self.get_effect(effect_name)
        if effect:
            effect.enabled = not effect.enabled
