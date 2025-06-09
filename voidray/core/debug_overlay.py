
"""
VoidRay Debug Overlay
Provides real-time debugging information and performance metrics.
"""

import pygame
from ..math.vector2 import Vector2
from ..utils.color import Color


class DebugOverlay:
    """
    Debug overlay for displaying real-time engine information.
    """
    
    def __init__(self, engine):
        """
        Initialize debug overlay.
        
        Args:
            engine: Reference to the main engine
        """
        self.engine = engine
        self.visible = False
        self.font = None
        self.line_height = 20
        self.margin = 10
        
    def toggle(self):
        """Toggle debug overlay visibility."""
        self.visible = not self.visible
        
    def render(self, renderer):
        """
        Render debug information.
        
        Args:
            renderer: The renderer to draw with
        """
        if not self.visible:
            return
            
        # Initialize font if needed
        if self.font is None:
            pygame.font.init()
            self.font = pygame.font.Font(None, 24)
        
        # Gather debug info
        fps = self.engine.get_fps()
        delta_time = self.engine.get_delta_time()
        object_count = self.engine.get_scene_object_count()
        
        # Debug text lines
        debug_lines = [
            f"FPS: {fps:.1f}",
            f"Delta Time: {delta_time:.3f}s",
            f"Objects: {object_count}",
            f"Physics Objects: {len(self.engine.physics_engine.colliders)}",
            f"Rendering Mode: {getattr(self.engine, 'rendering_mode', '2D')}",
            f"Performance Mode: {'ON' if getattr(self.engine, 'performance_mode', False) else 'OFF'}"
        ]
        
        # Render background
        bg_height = len(debug_lines) * self.line_height + self.margin * 2
        bg_rect = pygame.Rect(self.margin, self.margin, 250, bg_height)
        pygame.draw.rect(renderer.screen, (0, 0, 0, 128), bg_rect)
        pygame.draw.rect(renderer.screen, Color.WHITE, bg_rect, 1)
        
        # Render text lines
        y_offset = self.margin + 5
        for line in debug_lines:
            text_surface = self.font.render(line, True, Color.WHITE)
            renderer.screen.blit(text_surface, (self.margin + 5, y_offset))
            y_offset += self.line_height
