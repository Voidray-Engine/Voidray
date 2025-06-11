"""Fixes and improvements to the animation system, addressing potential errors and enhancing functionality."""
"""
VoidRay Animation Tween System
Advanced tweening and interpolation for smooth animations.
"""

import math
from typing import Callable, Any, Union
from ..math.vector2 import Vector2


class EaseType:
    """Easing function types for animations."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class Tween:
    """
    Advanced tweening class for smooth property animations.
    """

    def __init__(self, target: Any, property_name: str, end_value: Any, 
                 duration: float, ease_type: str = EaseType.LINEAR,
                 on_complete: Callable = None, on_update: Callable = None):
        """
        Initialize a tween animation.

        Args:
            target: Object to tween
            property_name: Name of the property to animate
            end_value: Target value for the property
            duration: Animation duration in seconds
            ease_type: Type of easing to use
            on_complete: Callback when animation completes
            on_update: Callback on each frame update
        """
        self.target = target
        self.property_name = property_name
        self.end_value = end_value
        self.duration = max(0.001, duration)  # Prevent division by zero
        self.ease_type = ease_type
        self.on_complete = on_complete
        self.on_update = on_update

        # Get starting value safely
        try:
            self.start_value = getattr(target, property_name)
        except AttributeError:
            print(f"Warning: Property '{property_name}' not found on target object")
            self.start_value = 0

        # Animation state
        self.current_time = 0.0
        self.is_complete = False
        self.is_playing = True

    def update(self, delta_time: float):
        """Update the tween animation."""
        if not self.is_playing or self.is_complete:
            return

        self.current_time += delta_time

        # Calculate progress (0.0 to 1.0)
        progress = min(self.current_time / self.duration, 1.0)

        # Apply easing
        eased_progress = self._apply_easing(progress)

        # Calculate current value
        current_value = self._interpolate(self.start_value, self.end_value, eased_progress)

        # Set the property
        try:
            setattr(self.target, self.property_name, current_value)
        except (AttributeError, TypeError):
            pass  # Silently handle errors

        # Call update callback
        if self.on_update:
            try:
                self.on_update(current_value, progress)
            except Exception:
                pass  # Don't let callback errors break the animation

        # Check if complete
        if progress >= 1.0:
            self.is_complete = True
            self.is_playing = False

            # Call completion callback
            if self.on_complete:
                try:
                    self.on_complete()
                except Exception:
                    pass  # Don't let callback errors break the system

    def _apply_easing(self, t: float) -> float:
        """Apply easing function to progress value."""
        if self.ease_type == EaseType.LINEAR:
            return t
        elif self.ease_type == EaseType.EASE_IN:
            return t * t
        elif self.ease_type == EaseType.EASE_OUT:
            return 1 - (1 - t) * (1 - t)
        elif self.ease_type == EaseType.EASE_IN_OUT:
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        elif self.ease_type == EaseType.BOUNCE:
            return self._bounce_ease(t)
        elif self.ease_type == EaseType.ELASTIC:
            return self._elastic_ease(t)
        return t

    def _bounce_ease(self, t: float) -> float:
        """Bounce easing function."""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375

    def _elastic_ease(self, t: float) -> float:
        """Elastic easing function."""
        if t == 0 or t == 1:
            return t
        return -(2**(-10 * t)) * math.sin((t - 0.1) * (2 * math.pi) / 0.4) + 1

    def _interpolate(self, start: Any, end: Any, t: float) -> Any:
        """Interpolate between start and end values."""
        if isinstance(start, (int, float)) and isinstance(end, (int, float)):
            return start + (end - start) * t
        elif isinstance(start, Vector2) and isinstance(end, Vector2):
            return Vector2(
                start.x + (end.x - start.x) * t,
                start.y + (end.y - start.y) * t
            )
        elif isinstance(start, tuple) and isinstance(end, tuple) and len(start) == len(end):
            return tuple(start[i] + (end[i] - start[i]) * t for i in range(len(start)))
        else:
            # For non-numeric types, switch at halfway point
            return end if t >= 0.5 else start

    def pause(self):
        """Pause the animation."""
        self.is_playing = False

    def resume(self):
        """Resume the animation."""
        if not self.is_complete:
            self.is_playing = True

    def stop(self):
        """Stop the animation."""
        self.is_playing = False
        self.is_complete = True

    def restart(self):
        """Restart the animation from the beginning."""
        self.current_time = 0.0
        self.is_complete = False
        self.is_playing = True

        # Refresh start value
        try:
            self.start_value = getattr(self.target, self.property_name)
        except AttributeError:
            pass