"""
VoidRay Performance Monitor
Advanced performance monitoring and optimization suggestions.
"""

import time
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
import pygame
from typing import Dict, List, Optional, Any
from collections import deque
from ..math.vector2 import Vector2


class PerformanceMetrics:
    """Stores performance metrics over time."""

    def __init__(self, max_samples: int = 300):  # 5 seconds at 60 FPS
        self.max_samples = max_samples
        self.fps_samples = deque(maxlen=max_samples)
        self.frame_time_samples = deque(maxlen=max_samples)
        self.memory_samples = deque(maxlen=max_samples)
        self.draw_calls_samples = deque(maxlen=max_samples)
        self.object_count_samples = deque(maxlen=max_samples)

        # Current frame metrics
        self.current_fps = 0.0
        self.current_frame_time = 0.0
        self.current_memory_mb = 0.0
        self.current_draw_calls = 0
        self.current_object_count = 0

        # Performance warnings
        self.warnings: List[str] = []
        self.last_warning_check = time.time()

    def add_frame_data(self, fps: float, frame_time: float, memory_mb: float, 
                      draw_calls: int, object_count: int):
        """Add frame performance data."""
        self.fps_samples.append(fps)
        self.frame_time_samples.append(frame_time)
        self.memory_samples.append(memory_mb)
        self.draw_calls_samples.append(draw_calls)
        self.object_count_samples.append(object_count)

        self.current_fps = fps
        self.current_frame_time = frame_time
        self.current_memory_mb = memory_mb
        self.current_draw_calls = draw_calls
        self.current_object_count = object_count

    def get_average_fps(self) -> float:
        """Get average FPS over sampling period."""
        return sum(self.fps_samples) / len(self.fps_samples) if self.fps_samples else 0.0

    def get_average_frame_time(self) -> float:
        """Get average frame time in milliseconds."""
        return sum(self.frame_time_samples) / len(self.frame_time_samples) if self.frame_time_samples else 0.0

    def get_memory_trend(self) -> str:
        """Analyze memory usage trend."""
        if len(self.memory_samples) < 10:
            return "stable"

        recent = list(self.memory_samples)[-10:]
        older = list(self.memory_samples)[-20:-10] if len(self.memory_samples) >= 20 else recent

        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)

        if recent_avg > older_avg * 1.1:
            return "increasing"
        elif recent_avg < older_avg * 0.9:
            return "decreasing"
        else:
            return "stable"

    def check_performance_warnings(self, target_fps: float = 60.0):
        """Check for performance issues and generate warnings."""
        current_time = time.time()
        if current_time - self.last_warning_check < 1.0:  # Check once per second
            return

        self.warnings.clear()
        self.last_warning_check = current_time

        # FPS warnings
        avg_fps = self.get_average_fps()
        if avg_fps < target_fps * 0.8:
            self.warnings.append(f"Low FPS: {avg_fps:.1f} (target: {target_fps})")

        # Frame time warnings
        avg_frame_time = self.get_average_frame_time()
        target_frame_time = 1000.0 / target_fps
        if avg_frame_time > target_frame_time * 1.2:
            self.warnings.append(f"High frame time: {avg_frame_time:.1f}ms")

        # Memory warnings
        memory_trend = self.get_memory_trend()
        if memory_trend == "increasing":
            self.warnings.append("Memory usage increasing - possible memory leak")

        if self.current_memory_mb > 500:  # 500MB threshold
            self.warnings.append(f"High memory usage: {self.current_memory_mb:.1f}MB")

        # Draw call warnings
        if self.current_draw_calls > 1000:
            self.warnings.append(f"High draw calls: {self.current_draw_calls}")

        # Object count warnings
        if self.current_object_count > 10000:
            self.warnings.append(f"High object count: {self.current_object_count}")


class PerformanceMonitor:
    """Advanced performance monitoring system."""

    def __init__(self, engine):
        self.engine = engine
        self.enabled = True
        self.show_overlay = False

        # Initialize metrics
        self.metrics = PerformanceMetrics()

        # Performance metrics
        self.fps_history = []
        self.memory_history = []
        self.frame_time_history = []
        self.cpu_usage_history = []
        self.draw_calls_history = []
        self.physics_time_history = []
        self.render_time_history = []
        self.max_history_size = 100

        # Detailed timing
        self.last_update_time = 0
        self.update_interval = 1.0  # Update every second
        self.frame_start_time = 0
        self.physics_start_time = 0
        self.render_start_time = 0

        # Performance warnings
        self.fps_warning_threshold = 30
        self.memory_warning_threshold = 512  # MB
        self.warnings = []
        self.max_warnings = 10
        self.auto_optimize = False

        # Profiling categories
        self.profile_timers: Dict[str, float] = {}
        self.profile_start_times: Dict[str, float] = {}

        # Optimization suggestions
        self.optimization_suggestions: List[str] = []

        # Display settings
        self.show_overlay = False
        self.overlay_position = Vector2(10, 10)
        self.overlay_font_size = 16

    def start_profile(self, category: str):
        """Start profiling a category."""
        if not self.enabled:
            return
        self.profile_start_times[category] = time.perf_counter()

    def end_profile(self, category: str):
        """End profiling a category."""
        if not self.enabled or category not in self.profile_start_times:
            return

        elapsed = time.perf_counter() - self.profile_start_times[category]
        self.profile_timers[category] = elapsed
        del self.profile_start_times[category]

    def update(self, delta_time: float):
        """Update performance monitoring."""
        if not self.enabled:
            return

        # Collect frame data
        fps = self.engine.get_fps()
        frame_time = delta_time * 1000  # Convert to milliseconds
        memory_mb = self._get_memory_usage()
        draw_calls = self._get_draw_calls()
        object_count = self._get_object_count()

        self.metrics.add_frame_data(fps, frame_time, memory_mb, draw_calls, object_count)
        self.metrics.check_performance_warnings(self.engine.target_fps)

        # Generate optimization suggestions
        self._generate_optimization_suggestions()

        # Auto-optimize if enabled
        if self.auto_optimize:
            self._apply_auto_optimizations()

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                return process.memory_info().rss / 1024 / 1024
            except:
                return 0.0
        else:
            return 0.0

    def _get_draw_calls(self) -> int:
        """Estimate draw calls (simplified)."""
        if hasattr(self.engine, 'renderer'):
            return getattr(self.engine.renderer, '_draw_calls', 0)
        return 0

    def _get_object_count(self) -> int:
        """Get total object count."""
        if hasattr(self.engine, 'current_scene') and self.engine.current_scene:
            return len(self.engine.current_scene.objects)
        return 0

    def _generate_optimization_suggestions(self):
        """Generate optimization suggestions based on metrics."""
        self.optimization_suggestions.clear()

        if self.metrics.current_fps < self.engine.target_fps * 0.8:
            self.optimization_suggestions.append("Consider reducing render distance")
            self.optimization_suggestions.append("Enable performance mode")

        if self.metrics.get_memory_trend() == "increasing":
            self.optimization_suggestions.append("Check for memory leaks")
            self.optimization_suggestions.append("Clear unused assets")

        if self.metrics.current_draw_calls > 500:
            self.optimization_suggestions.append("Use sprite batching")
            self.optimization_suggestions.append("Combine textures into atlases")

        if self.metrics.current_object_count > 5000:
            self.optimization_suggestions.append("Implement object pooling")
            self.optimization_suggestions.append("Use spatial culling")

    def _apply_auto_optimizations(self):
        """Apply automatic optimizations."""
        if self.metrics.current_fps < self.engine.target_fps * 0.7:
            # Reduce render distance
            if hasattr(self.engine, 'renderer'):
                if hasattr(self.engine.renderer, 'render_distance'):
                    self.engine.renderer.render_distance *= 0.95

            # Clear asset caches
            if hasattr(self.engine, 'asset_loader'):
                self.engine.asset_loader.clear_cache()

    def render_overlay(self, renderer):
        """Render performance overlay."""
        if not self.show_overlay:
            return

        y_offset = self.overlay_position.y
        line_height = self.overlay_font_size + 2

        # Basic metrics
        fps_text = f"FPS: {self.metrics.current_fps:.1f}"
        frame_time_text = f"Frame: {self.metrics.current_frame_time:.2f}ms"
        memory_text = f"Memory: {self.metrics.current_memory_mb:.1f}MB"
        objects_text = f"Objects: {self.metrics.current_object_count}"

        # Render text
        texts = [fps_text, frame_time_text, memory_text, objects_text]

        for i, text in enumerate(texts):
            color = (255, 255, 255)
            if i == 0 and self.metrics.current_fps < self.engine.target_fps * 0.8:
                color = (255, 128, 128)  # Red for low FPS

            renderer.draw_text(text, 
                             Vector2(self.overlay_position.x, y_offset), 
                             color, self.overlay_font_size)
            y_offset += line_height

        # Render warnings
        if self.metrics.warnings:
            y_offset += line_height
            for warning in self.metrics.warnings:
                renderer.draw_text(f"⚠ {warning}", 
                                 Vector2(self.overlay_position.x, y_offset), 
                                 (255, 255, 128), self.overlay_font_size)
                y_offset += line_height

    def toggle_overlay(self):
        """Toggle performance overlay visibility."""
        self.show_overlay = not self.show_overlay

    def get_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'current_metrics': {
                'fps': self.metrics.current_fps,
                'frame_time_ms': self.metrics.current_frame_time,
                'memory_mb': self.metrics.current_memory_mb,
                'draw_calls': self.metrics.current_draw_calls,
                'object_count': self.metrics.current_object_count
            },
            'averages': {
                'fps': self.metrics.get_average_fps(),
                'frame_time_ms': self.metrics.get_average_frame_time()
            },
            'memory_trend': self.metrics.get_memory_trend(),
            'warnings': self.metrics.warnings.copy(),
            'optimizations': self.optimization_suggestions.copy(),
            'profile_timers': self.profile_timers.copy()
        }
    def get_current_metrics(self) -> dict:
        """Get current performance metrics."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
        except ImportError:
            memory_mb = 0
            cpu_percent = 0

        # Get renderer stats
        draw_calls = 0
        if hasattr(self.engine, 'renderer') and hasattr(self.engine.renderer, 'draw_calls_this_frame'):
            draw_calls = self.engine.renderer.draw_calls_this_frame

        # Physics stats
        physics_objects = 0
        if hasattr(self.engine, 'physics_engine') and hasattr(self.engine.physics_engine, 'colliders'):
            physics_objects = len(self.engine.physics_engine.colliders)

        return {
            'fps': self.engine.get_fps(),
            'memory_mb': memory_mb,
            'cpu_percent': cpu_percent,
            'frame_time_ms': self.engine.get_delta_time() * 1000,
            'object_count': self.engine.get_scene_object_count() if hasattr(self.engine, 'get_scene_object_count') else 0,
            'draw_calls': draw_calls,
            'physics_objects': physics_objects,
            'physics_time_ms': getattr(self, 'last_physics_time', 0),
            'render_time_ms': getattr(self, 'last_render_time', 0)
        }

    def start_frame_timing(self):
        """Start timing the current frame."""
        self.frame_start_time = time.time()

    def start_physics_timing(self):
        """Start timing physics update."""
        self.physics_start_time = time.time()

    def end_physics_timing(self):
        """End physics timing and record duration."""
        if self.physics_start_time > 0:
            self.last_physics_time = (time.time() - self.physics_start_time) * 1000
            self.physics_time_history.append(self.last_physics_time)
            if len(self.physics_time_history) > self.max_history_size:
                self.physics_time_history.pop(0)

    def start_render_timing(self):
        """Start timing render phase."""
        self.render_start_time = time.time()

    def end_render_timing(self):
        """End render timing and record duration."""
        if self.render_start_time > 0:
            self.last_render_time = (time.time() - self.render_start_time) * 1000
            self.render_time_history.append(self.last_render_time)
            if len(self.render_time_history) > self.max_history_size:
                self.render_time_history.pop(0)

    def check_performance_warnings(self, metrics: dict):
        """Check for performance issues and add warnings."""
        current_time = time.time()

        # FPS warning
        if metrics['fps'] < self.fps_warning_threshold:
            self.add_warning(f"Low FPS: {metrics['fps']:.1f}", current_time)

        # Memory warning
        if metrics['memory_mb'] > self.memory_warning_threshold:
            self.add_warning(f"High memory usage: {metrics['memory_mb']:.1f}MB", current_time)

        # Frame time warning
        if metrics['frame_time_ms'] > 33.3:  # 30 FPS threshold
            self.add_warning(f"Long frame time: {metrics['frame_time_ms']:.1f}ms", current_time)

    def add_warning(self, message: str, timestamp: float):
        """Add a performance warning."""
        self.warnings.append({
            'message': message,
            'timestamp': timestamp
        })

        # Remove old warnings
        if len(self.warnings) > self.max_warnings:
            self.warnings.pop(0)

    def get_performance_summary(self) -> dict:
        """Get a summary of performance over time."""
        if not self.fps_history:
            return {}

        return {
            'avg_fps': sum(self.fps_history) / len(self.fps_history),
            'min_fps': min(self.fps_history),
            'max_fps': max(self.fps_history),
            'avg_memory_mb': sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0,
            'avg_frame_time_ms': sum(self.frame_time_history) / len(self.frame_time_history) if self.frame_time_history else 0,
            'avg_physics_time_ms': sum(self.physics_time_history) / len(self.physics_time_history) if self.physics_time_history else 0,
            'avg_render_time_ms': sum(self.render_time_history) / len(self.render_time_history) if self.render_time_history else 0,
            'warning_count': len(self.warnings)
        }