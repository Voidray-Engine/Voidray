
"""
VoidRay Performance Profiler
Real-time performance monitoring and optimization suggestions.
"""

import time
from typing import Dict, List, Callable
from collections import defaultdict, deque

class PerformanceProfiler:
    """
    Profiles game performance and provides optimization suggestions.
    """
    
    def __init__(self, history_size: int = 60):
        """
        Initialize profiler.
        
        Args:
            history_size: Number of frames to keep in history
        """
        self.history_size = history_size
        self.frame_times: deque = deque(maxlen=history_size)
        self.update_times: deque = deque(maxlen=history_size)
        self.render_times: deque = deque(maxlen=history_size)
        self.physics_times: deque = deque(maxlen=history_size)
        
        self.function_timings: Dict[str, deque] = defaultdict(lambda: deque(maxlen=history_size))
        self.memory_usage: deque = deque(maxlen=history_size)
        
        self.current_frame_start = 0
        self.bottlenecks: List[str] = []
        
    def start_frame(self):
        """Start timing a frame."""
        self.current_frame_start = time.perf_counter()
    
    def end_frame(self):
        """End frame timing."""
        frame_time = time.perf_counter() - self.current_frame_start
        self.frame_times.append(frame_time)
        
        # Detect bottlenecks
        self._detect_bottlenecks()
    
    def time_function(self, name: str):
        """Decorator to time function execution."""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                
                self.function_timings[name].append(end_time - start_time)
                return result
            return wrapper
        return decorator
    
    def record_update_time(self, time_taken: float):
        """Record update cycle time."""
        self.update_times.append(time_taken)
    
    def record_render_time(self, time_taken: float):
        """Record render cycle time."""
        self.render_times.append(time_taken)
    
    def record_physics_time(self, time_taken: float):
        """Record physics update time."""
        self.physics_times.append(time_taken)
    
    def _detect_bottlenecks(self):
        """Detect performance bottlenecks."""
        self.bottlenecks.clear()
        
        if len(self.frame_times) < 10:
            return
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        target_frame_time = 1.0 / 60.0  # 60 FPS target
        
        if avg_frame_time > target_frame_time * 1.2:
            # Analyze where time is spent
            if self.update_times:
                avg_update = sum(self.update_times) / len(self.update_times)
                if avg_update > target_frame_time * 0.4:
                    self.bottlenecks.append("Update cycle taking too long")
            
            if self.render_times:
                avg_render = sum(self.render_times) / len(self.render_times)
                if avg_render > target_frame_time * 0.4:
                    self.bottlenecks.append("Render cycle taking too long")
            
            if self.physics_times:
                avg_physics = sum(self.physics_times) / len(self.physics_times)
                if avg_physics > target_frame_time * 0.2:
                    self.bottlenecks.append("Physics simulation taking too long")
    
    def get_performance_report(self) -> Dict:
        """Get comprehensive performance report."""
        if not self.frame_times:
            return {"status": "No data available"}
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        report = {
            "fps": {
                "current": avg_fps,
                "target": 60.0,
                "frame_time_ms": avg_frame_time * 1000
            },
            "bottlenecks": self.bottlenecks.copy(),
            "timings": {}
        }
        
        if self.update_times:
            report["timings"]["update_ms"] = (sum(self.update_times) / len(self.update_times)) * 1000
        
        if self.render_times:
            report["timings"]["render_ms"] = (sum(self.render_times) / len(self.render_times)) * 1000
        
        if self.physics_times:
            report["timings"]["physics_ms"] = (sum(self.physics_times) / len(self.physics_times)) * 1000
        
        return report
    
    def get_optimization_suggestions(self) -> List[str]:
        """Get optimization suggestions based on profiling data."""
        suggestions = []
        
        if "Update cycle taking too long" in self.bottlenecks:
            suggestions.append("Consider reducing the number of active game objects")
            suggestions.append("Optimize update logic in game objects")
            suggestions.append("Use object pooling for frequently created/destroyed objects")
        
        if "Render cycle taking too long" in self.bottlenecks:
            suggestions.append("Reduce the number of sprites being rendered")
            suggestions.append("Use sprite batching for similar objects")
            suggestions.append("Consider using culling to skip off-screen objects")
        
        if "Physics simulation taking too long" in self.bottlenecks:
            suggestions.append("Reduce the number of physics objects")
            suggestions.append("Increase spatial grid size for collision detection")
            suggestions.append("Use static colliders where possible")
        
        return suggestions
