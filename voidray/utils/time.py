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
"""
VoidRay Time Utilities
Time and timing related utilities for the engine.
"""

import time
from typing import Optional


class Timer:
    """Simple timer utility for tracking elapsed time."""
    
    def __init__(self):
        self.start_time = 0.0
        self.pause_time = 0.0
        self.paused = False
        
    def start(self):
        """Start the timer."""
        self.start_time = time.time()
        self.paused = False
        
    def pause(self):
        """Pause the timer."""
        if not self.paused:
            self.pause_time = time.time()
            self.paused = True
            
    def resume(self):
        """Resume the timer."""
        if self.paused:
            self.start_time += time.time() - self.pause_time
            self.paused = False
            
    def reset(self):
        """Reset the timer."""
        self.start_time = time.time()
        self.paused = False
        
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.paused:
            return self.pause_time - self.start_time
        return time.time() - self.start_time
    
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return self.elapsed() * 1000.0


class FrameTimer:
    """Frame timing utility for performance monitoring."""
    
    def __init__(self, sample_size: int = 60):
        self.sample_size = sample_size
        self.frame_times = []
        self.last_frame_time = time.time()
        
    def tick(self) -> float:
        """Update frame timing and return delta time."""
        current_time = time.time()
        delta_time = current_time - self.last_frame_time
        
        self.frame_times.append(delta_time)
        if len(self.frame_times) > self.sample_size:
            self.frame_times.pop(0)
            
        self.last_frame_time = current_time
        return delta_time
    
    def get_avg_fps(self) -> float:
        """Get average FPS over the sample period."""
        if not self.frame_times:
            return 0.0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def get_min_fps(self) -> float:
        """Get minimum FPS over the sample period."""
        if not self.frame_times:
            return 0.0
        max_frame_time = max(self.frame_times)
        return 1.0 / max_frame_time if max_frame_time > 0 else 0.0
