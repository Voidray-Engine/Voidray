"""
VoidRay Time Utilities

Provides time management functionality including delta time calculation,
frame rate monitoring, and time-based utilities for games.
"""

import time


class Time:
    """
    Manages time-related functionality for the game engine including
    delta time calculation, frame timing, and time utilities.
    """
    
    def __init__(self):
        """Initialize the time manager."""
        self.delta_time = 0.0
        self.time_scale = 1.0
        self.total_time = 0.0
        self.frame_count = 0
        self.fps = 0.0
        
        # Internal timing
        self._last_frame_time = time.time()
        self._fps_timer = 0.0
        self._fps_frame_count = 0
        self._start_time = time.time()
    
    def update(self, delta_time: float) -> None:
        """
        Update time calculations.
        
        Args:
            delta_time: Raw delta time from the game loop
        """
        self.delta_time = delta_time * self.time_scale
        self.total_time += self.delta_time
        self.frame_count += 1
        
        # Calculate FPS
        self._fps_timer += delta_time
        self._fps_frame_count += 1
        
        # Update FPS every second
        if self._fps_timer >= 1.0:
            self.fps = self._fps_frame_count / self._fps_timer
            self._fps_timer = 0.0
            self._fps_frame_count = 0
    
    def get_delta_time(self) -> float:
        """
        Get the scaled delta time for this frame.
        
        Returns:
            Delta time in seconds
        """
        return self.delta_time
    
    def get_unscaled_delta_time(self) -> float:
        """
        Get the unscaled delta time for this frame.
        
        Returns:
            Unscaled delta time in seconds
        """
        return self.delta_time / self.time_scale if self.time_scale != 0 else 0
    
    def get_total_time(self) -> float:
        """
        Get the total scaled time since the game started.
        
        Returns:
            Total time in seconds
        """
        return self.total_time
    
    def get_real_time(self) -> float:
        """
        Get the real time since the game started (unaffected by time scale).
        
        Returns:
            Real time in seconds
        """
        return time.time() - self._start_time
    
    def get_frame_count(self) -> int:
        """
        Get the total number of frames rendered.
        
        Returns:
            Frame count
        """
        return self.frame_count
    
    def get_fps(self) -> float:
        """
        Get the current frames per second.
        
        Returns:
            FPS value
        """
        return self.fps
    
    def set_time_scale(self, scale: float) -> None:
        """
        Set the time scale for the game (affects delta time).
        
        Args:
            scale: Time scale multiplier (1.0 = normal, 0.5 = half speed, 2.0 = double speed)
        """
        self.time_scale = max(0, scale)
    
    def get_time_scale(self) -> float:
        """
        Get the current time scale.
        
        Returns:
            Time scale value
        """
        return self.time_scale
    
    def pause(self) -> None:
        """Pause time by setting time scale to 0."""
        self.set_time_scale(0.0)
    
    def resume(self) -> None:
        """Resume time by setting time scale to 1.0."""
        self.set_time_scale(1.0)
    
    def is_paused(self) -> bool:
        """
        Check if time is paused.
        
        Returns:
            True if time scale is 0, False otherwise
        """
        return self.time_scale == 0.0
    
    @staticmethod
    def get_time() -> float:
        """
        Get the current system time.
        
        Returns:
            Current time in seconds since epoch
        """
        return time.time()
    
    @staticmethod
    def sleep(seconds: float) -> None:
        """
        Sleep for a specified duration.
        
        Args:
            seconds: Duration to sleep in seconds
        """
        time.sleep(seconds)
    
    def __str__(self) -> str:
        return f"Time(delta={self.delta_time:.4f}s, total={self.total_time:.2f}s, fps={self.fps:.1f})"
    
    def __repr__(self) -> str:
        return (f"Time(delta_time={self.delta_time}, total_time={self.total_time}, "
                f"frame_count={self.frame_count}, fps={self.fps})")
