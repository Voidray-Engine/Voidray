
"""
VoidRay Performance Profiler
Comprehensive performance monitoring and profiling for game optimization.
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from dataclasses import dataclass
import os
import json


@dataclass
class ProfileData:
    """Container for profiling data."""
    name: str
    start_time: float
    end_time: float
    duration: float
    memory_before: int
    memory_after: int
    thread_id: int
    frame_number: int


class PerformanceProfiler:
    """
    Advanced performance profiler for game engines.
    """
    
    def __init__(self, max_samples: int = 10000, enable_memory_tracking: bool = True):
        """
        Initialize the profiler.
        
        Args:
            max_samples: Maximum number of samples to keep
            enable_memory_tracking: Whether to track memory usage
        """
        self.max_samples = max_samples
        self.enable_memory_tracking = enable_memory_tracking
        
        # Profiling data
        self.samples: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_samples))
        self.active_profiles: Dict[int, Dict[str, ProfileData]] = defaultdict(dict)
        
        # Performance metrics
        self.frame_times = deque(maxlen=1000)
        self.fps_history = deque(maxlen=1000)
        self.memory_history = deque(maxlen=1000)
        
        # Threading
        self.lock = threading.Lock()
        self.thread_stats: Dict[int, Dict[str, Any]] = defaultdict(lambda: {
            'samples': 0,
            'total_time': 0.0,
            'avg_time': 0.0
        })
        
        # Frame tracking
        self.current_frame = 0
        self.frame_start_time = 0.0
        
        # Hotspot detection
        self.hotspots: Dict[str, float] = {}
        self.hotspot_threshold = 0.016  # 16ms for 60 FPS
        
        # Custom metrics
        self.custom_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Reporting
        self.report_callbacks: List[Callable] = []
        
        # Auto-profiling
        self.auto_profile_functions: Dict[str, Callable] = {}
        
    def start_profile(self, name: str) -> int:
        """
        Start profiling a section of code.
        
        Args:
            name: Name of the profile section
            
        Returns:
            Profile ID for ending the profile
        """
        thread_id = threading.get_ident()
        profile_id = id(self) + thread_id + int(time.time() * 1000000)
        
        memory_before = self._get_memory_usage() if self.enable_memory_tracking else 0
        
        profile_data = ProfileData(
            name=name,
            start_time=time.perf_counter(),
            end_time=0.0,
            duration=0.0,
            memory_before=memory_before,
            memory_after=0,
            thread_id=thread_id,
            frame_number=self.current_frame
        )
        
        with self.lock:
            self.active_profiles[thread_id][profile_id] = profile_data
        
        return profile_id
    
    def end_profile(self, profile_id: int):
        """
        End a profile section.
        
        Args:
            profile_id: ID returned from start_profile
        """
        end_time = time.perf_counter()
        thread_id = threading.get_ident()
        
        with self.lock:
            if thread_id not in self.active_profiles:
                return
            
            if profile_id not in self.active_profiles[thread_id]:
                return
            
            profile_data = self.active_profiles[thread_id][profile_id]
            profile_data.end_time = end_time
            profile_data.duration = end_time - profile_data.start_time
            
            if self.enable_memory_tracking:
                profile_data.memory_after = self._get_memory_usage()
            
            # Store the sample
            self.samples[profile_data.name].append(profile_data)
            
            # Update thread stats
            thread_stats = self.thread_stats[thread_id]
            thread_stats['samples'] += 1
            thread_stats['total_time'] += profile_data.duration
            thread_stats['avg_time'] = thread_stats['total_time'] / thread_stats['samples']
            
            # Check for hotspots
            if profile_data.duration > self.hotspot_threshold:
                self.hotspots[profile_data.name] = max(
                    self.hotspots.get(profile_data.name, 0.0),
                    profile_data.duration
                )
            
            # Clean up
            del self.active_profiles[thread_id][profile_id]
    
    def profile_function(self, func: Callable, name: Optional[str] = None) -> Callable:
        """
        Decorator to automatically profile a function.
        
        Args:
            func: Function to profile
            name: Optional custom name for the profile
            
        Returns:
            Wrapped function
        """
        profile_name = name or f"{func.__module__}.{func.__name__}"
        
        def wrapper(*args, **kwargs):
            profile_id = self.start_profile(profile_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                self.end_profile(profile_id)
        
        return wrapper
    
    def start_frame(self):
        """Mark the start of a new frame."""
        self.frame_start_time = time.perf_counter()
        self.current_frame += 1
    
    def end_frame(self):
        """Mark the end of the current frame."""
        if self.frame_start_time > 0:
            frame_time = time.perf_counter() - self.frame_start_time
            fps = 1.0 / frame_time if frame_time > 0 else 0
            
            self.frame_times.append(frame_time)
            self.fps_history.append(fps)
            
            if self.enable_memory_tracking:
                memory_usage = self._get_memory_usage()
                self.memory_history.append(memory_usage)
    
    def add_custom_metric(self, name: str, value: float):
        """
        Add a custom metric value.
        
        Args:
            name: Metric name
            value: Metric value
        """
        self.custom_metrics[name].append(value)
        
        # Keep only recent samples
        if len(self.custom_metrics[name]) > self.max_samples:
            self.custom_metrics[name] = self.custom_metrics[name][-self.max_samples:]
    
    def get_profile_stats(self, name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific profile.
        
        Args:
            name: Profile name
            
        Returns:
            Statistics dictionary
        """
        if name not in self.samples:
            return {}
        
        samples = list(self.samples[name])
        if not samples:
            return {}
        
        durations = [s.duration for s in samples]
        memory_deltas = [s.memory_after - s.memory_before for s in samples if s.memory_after > 0]
        
        stats = {
            'sample_count': len(samples),
            'total_time': sum(durations),
            'avg_time': sum(durations) / len(durations),
            'min_time': min(durations),
            'max_time': max(durations),
            'last_time': durations[-1] if durations else 0,
        }
        
        if memory_deltas:
            stats.update({
                'avg_memory_delta': sum(memory_deltas) / len(memory_deltas),
                'max_memory_delta': max(memory_deltas),
                'min_memory_delta': min(memory_deltas)
            })
        
        # Calculate percentiles
        sorted_durations = sorted(durations)
        length = len(sorted_durations)
        if length > 0:
            stats['p50'] = sorted_durations[length // 2]
            stats['p90'] = sorted_durations[int(length * 0.9)]
            stats['p95'] = sorted_durations[int(length * 0.95)]
            stats['p99'] = sorted_durations[int(length * 0.99)]
        
        return stats
    
    def get_frame_stats(self) -> Dict[str, Any]:
        """Get frame timing statistics."""
        if not self.frame_times:
            return {}
        
        frame_times = list(self.frame_times)
        fps_values = list(self.fps_history)
        
        return {
            'frame_count': len(frame_times),
            'avg_frame_time': sum(frame_times) / len(frame_times),
            'min_frame_time': min(frame_times),
            'max_frame_time': max(frame_times),
            'avg_fps': sum(fps_values) / len(fps_values) if fps_values else 0,
            'min_fps': min(fps_values) if fps_values else 0,
            'max_fps': max(fps_values) if fps_values else 0,
            'current_fps': fps_values[-1] if fps_values else 0
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        if not self.memory_history:
            return {}
        
        memory_values = list(self.memory_history)
        
        return {
            'current_memory_mb': memory_values[-1] / 1024 / 1024,
            'avg_memory_mb': sum(memory_values) / len(memory_values) / 1024 / 1024,
            'min_memory_mb': min(memory_values) / 1024 / 1024,
            'max_memory_mb': max(memory_values) / 1024 / 1024,
            'memory_samples': len(memory_values)
        }
    
    def get_hotspots(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top performance hotspots.
        
        Args:
            top_n: Number of top hotspots to return
            
        Returns:
            List of hotspot data
        """
        sorted_hotspots = sorted(
            self.hotspots.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        result = []
        for name, max_time in sorted_hotspots[:top_n]:
            stats = self.get_profile_stats(name)
            result.append({
                'name': name,
                'max_time': max_time,
                'avg_time': stats.get('avg_time', 0),
                'sample_count': stats.get('sample_count', 0)
            })
        
        return result
    
    def get_thread_stats(self) -> Dict[int, Dict[str, Any]]:
        """Get statistics for all threads."""
        return dict(self.thread_stats)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        report = {
            'timestamp': time.time(),
            'frame_stats': self.get_frame_stats(),
            'memory_stats': self.get_memory_stats(),
            'thread_stats': self.get_thread_stats(),
            'hotspots': self.get_hotspots(),
            'profile_summaries': {}
        }
        
        # Add summaries for all profiles
        for profile_name in self.samples.keys():
            report['profile_summaries'][profile_name] = self.get_profile_stats(profile_name)
        
        # Add custom metrics
        if self.custom_metrics:
            report['custom_metrics'] = {}
            for metric_name, values in self.custom_metrics.items():
                if values:
                    report['custom_metrics'][metric_name] = {
                        'current': values[-1],
                        'avg': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'sample_count': len(values)
                    }
        
        # Call report callbacks
        for callback in self.report_callbacks:
            try:
                callback(report)
            except Exception as e:
                print(f"Error in report callback: {e}")
        
        return report
    
    def save_report(self, file_path: str):
        """Save a performance report to file."""
        report = self.generate_report()
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Performance report saved to: {file_path}")
        except Exception as e:
            print(f"Failed to save performance report: {e}")
    
    def add_report_callback(self, callback: Callable):
        """Add a callback that will be called when generating reports."""
        self.report_callbacks.append(callback)
    
    def clear_samples(self):
        """Clear all profiling samples."""
        with self.lock:
            self.samples.clear()
            self.active_profiles.clear()
            self.frame_times.clear()
            self.fps_history.clear()
            self.memory_history.clear()
            self.hotspots.clear()
            self.custom_metrics.clear()
            self.thread_stats.clear()
        
        print("Profiler samples cleared")
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Fallback to basic method
            import sys
            return sys.getsizeof(self.samples)


class ProfileContext:
    """Context manager for profiling code blocks."""
    
    def __init__(self, profiler: PerformanceProfiler, name: str):
        self.profiler = profiler
        self.name = name
        self.profile_id = None
    
    def __enter__(self):
        self.profile_id = self.profiler.start_profile(self.name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.profile_id is not None:
            self.profiler.end_profile(self.profile_id)


# Global profiler instance
global_profiler = PerformanceProfiler()


def profile(name: str = None):
    """Decorator for profiling functions."""
    def decorator(func):
        return global_profiler.profile_function(func, name)
    return decorator


def profile_context(name: str) -> ProfileContext:
    """Create a profiling context manager."""
    return ProfileContext(global_profiler, name)
