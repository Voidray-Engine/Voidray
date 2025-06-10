
from typing import Callable, Optional
import pygame
from ..math.vector2 import Vector2
from ..utils.color import Color
from enum import Enum


class TransitionType(Enum):
    """Types of scene transitions."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class SceneTransition:
    """
    Handles smooth transitions between scenes.
    """

    def __init__(self, transition_type: TransitionType, duration: float = 1.0):
        """
        Initialize scene transition.

        Args:
            transition_type: Type of transition effect
            duration: Duration in seconds
        """
        self.type = transition_type
        self.duration = duration
        self.progress = 0.0
        self.active = False
        self.on_complete: Optional[Callable] = None

    def start(self, on_complete: Callable = None):
        """Start the transition."""
        self.active = True
        self.progress = 0.0
        self.on_complete = on_complete

    def update(self, delta_time: float) -> bool:
        """
        Update the transition.

        Args:
            delta_time: Time elapsed since last frame

        Returns:
            True if transition is complete
        """
        if not self.active:
            return True

        self.progress += delta_time / self.duration
        
        if self.progress >= 1.0:
            self.progress = 1.0
            self.active = False
            
            if self.on_complete:
                self.on_complete()
            
            return True
        
        return False

    def render(self, screen: pygame.Surface, renderer):
        """Render the transition effect."""
        if not self.active:
            return

        screen_rect = screen.get_rect()
        
        if self.type == TransitionType.FADE:
            # Create fade overlay
            fade_surface = pygame.Surface(screen.get_size())
            fade_surface.set_alpha(int(255 * self.progress))
            fade_surface.fill((0, 0, 0))
            screen.blit(fade_surface, (0, 0))
            
        elif self.type == TransitionType.SLIDE_LEFT:
            # Slide effect (would need scene buffers in full implementation)
            slide_x = int(screen_rect.width * self.progress)
            overlay = pygame.Surface((slide_x, screen_rect.height))
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (screen_rect.width - slide_x, 0))
            
        elif self.type == TransitionType.ZOOM_IN:
            # Simple zoom effect with black borders
            border_size = int(min(screen_rect.width, screen_rect.height) * (1.0 - self.progress) * 0.5)
            if border_size > 0:
                # Top and bottom borders
                pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_rect.width, border_size))
                pygame.draw.rect(screen, (0, 0, 0), (0, screen_rect.height - border_size, screen_rect.width, border_size))
                # Left and right borders
                pygame.draw.rect(screen, (0, 0, 0), (0, 0, border_size, screen_rect.height))
                pygame.draw.rect(screen, (0, 0, 0), (screen_rect.width - border_size, 0, border_size, screen_rect.height))

    def is_active(self) -> bool:
        """Check if transition is currently active."""
        return self.active

    def get_progress(self) -> float:
        """Get current transition progress (0.0 to 1.0)."""
        return self.progress
